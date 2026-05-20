"""
LangChain Runnable pipeline and helpers for streaming via ``astream_events``.

PIPELINE FLOW
=============

  User input (dict)
        │
        ▼
  ┌─────────────┐
  │   classify  │  ← renders classify.j2, calls LLM, parses ClassifyOutput
  └──────┬──────┘
         │  state now includes "classify" key
         ▼
  ┌──────────────┐
  │ analyze_risks│  ← renders risks.j2 (uses classify result), parses RisksOutput
  └──────┬───────┘
         │  state now includes "analyze_risks" key
         ▼
  ┌───────────────┐
  │ generate_scope│  ← renders generate_scope.j2, parses GenerateScopeOutput
  └──────┬────────┘
         │
         ▼
  Final state dict  ←  streamed token-by-token via astream_events

Each step:
  1. Renders its Jinja2 template with the current state.
  2. Calls the LLM asynchronously.
  3. Normalises the raw content to a plain string.
  4. Validates the string against the step's Pydantic output schema.
  5. Merges the parsed result back into state before passing it downstream.
"""

from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableLambda
from pydantic import BaseModel, ValidationError

from app.agents import ParsingError
from app.agents.pipeline import PIPELINE_STEPS
from app.agents.template_loader import TemplateLoader

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# The run_name assigned to the root chain.
# ``astream_events`` emits an "on_chain_end" event with this name when the
# entire pipeline finishes, which callers use to detect completion.
STREAM_ROOT_RUN_NAME = "scope_pipeline"


# ---------------------------------------------------------------------------
# 1. Content normalisation
#    LLM responses can arrive as a plain string or as a list of content
#    blocks (e.g. from Anthropic's multi-block format).  Everything is
#    flattened to a single string before JSON parsing.
# ---------------------------------------------------------------------------

def normalize_llm_content(content: Any) -> str:
    """Normalise a chat model ``content`` value to a single plain string.

    Handles three cases:
    - ``str``  → returned as-is.
    - ``list`` → text blocks are extracted and concatenated.
    - anything else → coerced with ``str()``.
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                # Prefer the explicit "text" type block; fall back to any
                # dict that happens to carry a "text" key.
                if block.get("type") == "text" and "text" in block:
                    parts.append(str(block["text"]))
                elif "text" in block:
                    parts.append(str(block["text"]))
            else:
                parts.append(str(block))
        return "".join(parts)

    # Fallback for unexpected types (e.g. AIMessageChunk in edge cases).
    return str(content)


# ---------------------------------------------------------------------------
# 2. Response parsing
#    Each pipeline step declares its expected Pydantic schema in
#    PIPELINE_STEPS.  This helper validates the raw LLM string against that
#    schema and raises a typed ParsingError on failure so callers can handle
#    it uniformly.
# ---------------------------------------------------------------------------

def parse_step_content(step_name: str, raw_content: str | None) -> BaseModel:
    """Parse a raw LLM response string into the Pydantic model for *step_name*.

    Args:
        step_name:   Key into ``PIPELINE_STEPS`` (e.g. ``"classify"``).
        raw_content: JSON string returned by the LLM.

    Returns:
        A validated Pydantic model instance for the step.

    Raises:
        ParsingError: If the content is empty or fails schema validation.
    """
    if raw_content is None or raw_content.strip() == "":
        raise ParsingError(f"Empty response for {step_name}")

    step = PIPELINE_STEPS[step_name]
    try:
        return step.output_schema.model_validate_json(raw_content)
    except ValidationError as exc:
        raise ParsingError(
            f"Failed to parse response for {step_name}: {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# 3. Single-step execution
#    Combines template rendering → LLM call → normalisation → parsing into
#    one async function.  The result is merged into the shared state dict so
#    downstream steps can reference it via their Jinja2 templates.
# ---------------------------------------------------------------------------

async def _run_single_step(
    llm: BaseChatModel,
    loader: TemplateLoader,
    step_name: str,
    state: dict[str, Any],
) -> dict[str, Any]:
    """Execute one pipeline step and return the updated state.

    Steps:
        1. Render the Jinja2 template for *step_name* using the current state.
        2. Send the rendered prompt to the LLM.
        3. Normalise and parse the response.
        4. Return a new state dict with the parsed result stored under *step_name*.

    Args:
        llm:       The chat model to invoke.
        loader:    Template loader used to render the step's prompt.
        step_name: Key identifying the step in ``PIPELINE_STEPS``.
        state:     Accumulated pipeline state from previous steps.

    Returns:
        A new state dict that includes all previous keys plus the parsed
        output of this step under ``state[step_name]``.
    """
    # Render the prompt template with whatever the pipeline has accumulated so far.
    prompt = loader.render(step_name, state)

    # Call the LLM and normalise its response to a plain string.
    response = await llm.ainvoke(prompt)
    raw_str = normalize_llm_content(response.content)

    # Validate the string against the step's declared Pydantic schema.
    parsed = parse_step_content(step_name, raw_str)

    # Merge the parsed result into state; downstream steps can read it.
    return {**state, step_name: parsed}


# ---------------------------------------------------------------------------
# 4. Pipeline assembly
#    Chains the three steps into a single LangChain Runnable using the pipe
#    operator (|).  Each step is wrapped in a RunnableLambda so LangChain can
#    track it individually in astream_events (run_name + tags).
# ---------------------------------------------------------------------------

def build_scope_pipeline_runnable(
    llm: BaseChatModel, loader: TemplateLoader
) -> Runnable:
    """Build the sequential classify → analyze_risks → generate_scope chain.

    The returned Runnable is designed to be consumed via ``astream_events``,
    which emits per-token streaming events as well as step-level lifecycle
    events (start / end) that callers can use to track progress.

    Args:
        llm:    Chat model to use for all three steps.
        loader: Template loader that renders each step's Jinja2 prompt.

    Returns:
        A LangChain ``Runnable`` that accepts an initial state dict and
        returns the fully populated state dict after all three steps.
    """

    # Each inner function closes over ``llm`` and ``loader`` and delegates
    # to ``_run_single_step`` with the appropriate step name.

    async def classify(state: dict[str, Any]) -> dict[str, Any]:
        """Step 1 – classify the incoming request."""
        return await _run_single_step(llm, loader, "classify", state)

    async def risks(state: dict[str, Any]) -> dict[str, Any]:
        """Step 2 – identify risks based on the classification."""
        return await _run_single_step(llm, loader, "analyze_risks", state)

    async def scope(state: dict[str, Any]) -> dict[str, Any]:
        """Step 3 – generate the final scope document."""
        return await _run_single_step(llm, loader, "generate_scope", state)

    # Chain the three steps with LangChain's pipe operator.
    # run_name lets astream_events identify each step; tags group them under
    # the "scope_pipeline" namespace for filtering.
    return (
        RunnableLambda(classify).with_config(
            run_name="classify", tags=["scope_pipeline"]
        )
        | RunnableLambda(risks).with_config(
            run_name="analyze_risks", tags=["scope_pipeline"]
        )
        | RunnableLambda(scope).with_config(
            run_name="generate_scope", tags=["scope_pipeline"]
        )
    ).with_config(run_name=STREAM_ROOT_RUN_NAME, tags=["scope_pipeline"])


# ---------------------------------------------------------------------------
# 5. Streaming helpers
#    When the pipeline is consumed via ``astream_events``, the caller receives
#    a stream of event dicts.  This helper extracts the incremental token text
#    from ``on_chat_model_stream`` events so callers don't need to know the
#    internal event structure.
# ---------------------------------------------------------------------------

def extract_token_from_stream_event(event: Any) -> str:
    """Extract the delta token text from an ``on_chat_model_stream`` event.

    Returns an empty string for any event that carries no text (e.g.
    lifecycle events like ``on_chain_start``), so callers can safely
    concatenate the return value without extra guards.

    Args:
        event: A raw event dict emitted by ``astream_events``.

    Returns:
        The incremental token string, or ``""`` if none is present.
    """
    chunk = event.get("data", {}).get("chunk")
    if chunk is None:
        return ""

    content = getattr(chunk, "content", None)
    return normalize_llm_content(content) if content is not None else ""
