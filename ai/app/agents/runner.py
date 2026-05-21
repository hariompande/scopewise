"""
LangChain Runnable pipeline and helpers for streaming via ``astream_events``.

PIPELINE FLOW (with Research Phase)
====================================

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
         │  state now includes scope output
         ▼
  ┌───────────────────┐
  │ search_firm_history│  ← RAG search over past projects
  └────────┬──────────┘
           │  state now includes firm history context
           ▼
  ┌───────────────────┐
  │  check_resources   │  ← Query DB for available experts
  └────────┬──────────┘
           │  state now includes resource availability
           ▼
  ┌───────────────────┐
  │  market_research   │  ← Web search for market data
  └────────┬──────────┘
           │
           ▼
 Final state dict  ←  streamed token-by-token via astream_events

Each step:
  1. Renders its Jinja2 template with the current state (or runs tools for research steps).
  2. Calls the LLM asynchronously (or tools for research steps).
  3. Normalises the raw content to a plain string.
  4. Validates the string against the step's declared Pydantic output schema.
  5. Merges the parsed result back into state before passing it downstream.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableLambda
from pydantic import BaseModel, ValidationError

from app.agents import ParsingError
from app.agents.pipeline import PIPELINE_STEPS
from app.agents.template_loader import TemplateLoader

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.config import Settings

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
# 3b. Tool-based step execution (for research phase)
#    Research steps use tools (RAG, DB queries, web search) rather than
#    LLM calls. These emit tool_start/tool_end events for streaming.
# ---------------------------------------------------------------------------

RESEARCH_STEPS = {"search_firm_history", "check_resources", "market_research"}


async def _run_research_step(
    settings: Settings,
    db_session: Session,
    step_name: str,
    state: dict[str, Any],
) -> dict[str, Any]:
    """Execute a research step using tools and return the updated state.
    
    Research steps query external data sources (vector DB, SQL DB, web)
    rather than calling an LLM directly.
    
    Args:
        settings: Application settings for tool configuration.
        db_session: SQLAlchemy session for database queries.
        step_name: Key identifying the research step.
        state: Accumulated pipeline state from previous steps.
        
    Returns:
        A new state dict with the research result stored under *step_name*.
    """
    from app.agents.tools import (
        FirmHistorySearchTool,
        MarketResearchTool,
        ResourceAvailabilityChecker,
    )
    
    user_input = state.get("user_input", "")
    
    if step_name == "search_firm_history":
        tool = FirmHistorySearchTool(settings, db_session)
        # Extract project type and industry from user input (simplified)
        result = await tool.search(
            project_description=user_input,
            project_type=state.get("project_type", "software project"),
            industry=state.get("industry", "")
        )
        
    elif step_name == "check_resources":
        # Infer required skills from user input and previous research
        required_skills = _extract_skills_from_context(state)
        
        checker = ResourceAvailabilityChecker(db_session)
        result = checker.check_availability(
            required_skills=required_skills,
            min_expert_level="mid"
        )
        
    elif step_name == "market_research":
        tool = MarketResearchTool(settings)
        result = await tool.research(
            project_type=state.get("project_type", "software project"),
            industry=state.get("industry", ""),
            budget_range=state.get("budget", "")
        )
    else:
        raise ValueError(f"Unknown research step: {step_name}")
    
    return {**state, step_name: result}


def _extract_skills_from_context(state: dict[str, Any]) -> list[str]:
    """Extract likely required skills from accumulated state.
    
    Uses firm history results and user input to infer skills needed.
    """
    skills: set[str] = set()
    
    # Extract from firm history if available
    firm_history = state.get("search_firm_history")
    if firm_history:
        for project in getattr(firm_history, "similar_projects", []):
            skills.update(getattr(project, "tech_stack", []))
    
    # Extract from user input (common tech keywords)
    user_input = state.get("user_input", "").lower()
    tech_keywords = [
        "react", "vue", "angular", "node.js", "nodejs", "python", "django",
        "flask", "fastapi", "java", "spring", "go", "golang", "rust",
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "machine learning", "ai", "llm", "data engineering", "etl",
        "mobile", "ios", "android", "flutter", "react native",
        "api", "graphql", "rest", "microservices", "serverless"
    ]
    
    for keyword in tech_keywords:
        if keyword in user_input:
            skills.add(keyword)
    
    return list(skills)[:10]  # Limit to top 10 skills


# ---------------------------------------------------------------------------
# 4. Pipeline assembly
#    Chains the three steps into a single LangChain Runnable using the pipe
#    operator (|).  Each step is wrapped in a RunnableLambda so LangChain can
#    track it individually in astream_events (run_name + tags).
# ---------------------------------------------------------------------------

def build_scope_pipeline_runnable(
    llm: BaseChatModel,
    loader: TemplateLoader,
    settings: Settings | None = None,
    db_session: Session | None = None
) -> Runnable:
    """Build the full pipeline with research phase → classify → risks → scope.

    The pipeline now includes a research phase before classification:
    1. search_firm_history - RAG over past projects
    2. check_resources - Query DB for available experts
    3. market_research - Web search for market data
    4. classify - Classify complexity (LLM-based)
    5. analyze_risks - Identify risks (LLM-based)
    6. generate_scope - Generate final scope (LLM-based)

    The returned Runnable is designed to be consumed via ``astream_events``,
    which emits per-token streaming events as well as step-level lifecycle
    events (start / end) that callers can use to track progress.

    Args:
        llm:        Chat model to use for LLM-based steps.
        loader:     Template loader that renders each step's Jinja2 prompt.
        settings:   Application settings (required for research steps).
        db_session: SQLAlchemy session (required for research steps).

    Returns:
        A LangChain ``Runnable`` that accepts an initial state dict and
        returns the fully populated state dict after all steps.
    """

    async def search_firm_history(state: dict[str, Any]) -> dict[str, Any]:
        """Research Step 1 – search firm project history via RAG."""
        if settings and db_session:
            return await _run_research_step(settings, db_session, "search_firm_history", state)
        # Fallback: skip research if deps not provided
        return {**state, "search_firm_history": None}

    async def check_resources(state: dict[str, Any]) -> dict[str, Any]:
        """Research Step 2 – check resource availability in DB."""
        if settings and db_session:
            return await _run_research_step(settings, db_session, "check_resources", state)
        return {**state, "check_resources": None}

    async def market_research(state: dict[str, Any]) -> dict[str, Any]:
        """Research Step 3 – web search for market data."""
        if settings and db_session:
            return await _run_research_step(settings, db_session, "market_research", state)
        return {**state, "market_research": None}

    async def classify(state: dict[str, Any]) -> dict[str, Any]:
        """Step 4 – classify the incoming request using LLM."""
        return await _run_single_step(llm, loader, "classify", state)

    async def risks(state: dict[str, Any]) -> dict[str, Any]:
        """Step 5 – identify risks based on the classification."""
        return await _run_single_step(llm, loader, "analyze_risks", state)

    async def scope(state: dict[str, Any]) -> dict[str, Any]:
        """Step 6 – generate the final scope document."""
        return await _run_single_step(llm, loader, "generate_scope", state)

    # Chain all steps with LangChain's pipe operator.
    # Research steps run first so their results are available to LLM steps.
    return (
        RunnableLambda(search_firm_history).with_config(
            run_name="search_firm_history", tags=["scope_pipeline", "research"]
        )
        | RunnableLambda(check_resources).with_config(
            run_name="check_resources", tags=["scope_pipeline", "research"]
        )
        | RunnableLambda(market_research).with_config(
            run_name="market_research", tags=["scope_pipeline", "research"]
        )
        | RunnableLambda(classify).with_config(
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
