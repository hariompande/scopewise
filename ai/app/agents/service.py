"""
Agent service — orchestrates the scope analysis pipeline end-to-end.

SERVICE FLOW
============

  ScopeRequest (user_input)
        │
        ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  AgentService                                               │
  │                                                             │
  │  warmup()  ──►  create LLM  +  pre-load all templates       │
  │                                                             │
  │  stream_pipeline()  ← single execution path for all callers │
  │        │                                                     │
  │        ▼                                                     │
  │  Resolve / create PipelineRun row                           │
  │        │                                                     │
  │  ┌─────▼──────┐                                             │
  │  │  classify  │  status → classifying  / persist NodeOutput │
  │  └─────┬──────┘                                             │
  │  ┌─────▼────────────┐                                       │
  │  │  analyze_risks   │  status → analyzing_risks             │
  │  └─────┬────────────┘                                       │
  │  ┌─────▼──────────────┐                                     │
  │  │  generate_scope    │  status → generating_scope          │
  │  └─────┬──────────────┘                                     │
  │  ┌─────▼──────────┐                                         │
  │  │  ScopeDocument │  status → completed (or failed)         │
  │  └────────────────┘                                         │
  └─────────────────────────────────────────────────────────────┘

Yields SSE event dicts:
  phase_start  →  llm_token (per token)  →  phase_complete
  →  result  (or error on exception)

POST /run consumes stream_pipeline() internally and returns only the
final ``result`` event payload — no separate sync code path exists.

Database writes per run:
  PipelineRun  (1)  ─── status updated before each step
  NodeOutput   (3)  ─── one per step, written after step completes
  ScopeDocument(1)  ─── written after all steps succeed
"""

import logging
import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from sqlalchemy.orm import Session

from app.agents import PromptValidationError
from app.agents.llm_factory import create_llm
from app.agents.pipeline import PIPELINE_STEPS, STEP_ORDER
from app.agents.runner import (
    STREAM_ROOT_RUN_NAME,
    build_scope_pipeline_runnable,
    extract_token_from_stream_event,
)
from app.agents.template_loader import TemplateLoader
from app.config import Settings
from app.database.models import (
    NodeOutput,
    PipelineRun,
    PipelineStatus,
    ScopeDocument,
    ScopeRequest,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Maps each step name to the PipelineStatus value that should be set on the
# PipelineRun row *before* that step's LLM call begins.  This lets the API
# layer report live progress to the client.
STEP_STATUS_MAP: dict[str, PipelineStatus] = {
    "classify": PipelineStatus.classifying,
    "analyze_risks": PipelineStatus.analyzing_risks,
    "generate_scope": PipelineStatus.generating_scope,
}

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# AgentService
# ---------------------------------------------------------------------------

class AgentService:
    """Orchestrates the three-step LLM pipeline and persists all results.

    Lifecycle
    ---------
    1. Instantiate with ``Settings``.
    2. Call ``warmup()`` once at startup to initialise the LLM and validate
       templates (no API calls are made during warmup).
    3. Call ``run_pipeline()`` (sync) or ``stream_pipeline()`` (async/SSE)
       per request.
    """

    # ------------------------------------------------------------------
    # 1. Initialisation
    # ------------------------------------------------------------------

    def __init__(self, settings: Settings) -> None:
        """Store settings and create the template loader.

        The LLM is *not* created here; call ``warmup()`` before processing
        any requests.

        Args:
            settings: Application settings containing LLM provider/model config.
        """
        self.settings = settings
        self.template_loader = TemplateLoader()
        self._llm: BaseChatModel | None = None  # populated by warmup()

    def warmup(self) -> None:
        """Initialise the LLM and pre-validate all Jinja2 templates.

        Intended to be called once at application startup (e.g. in a
        ``lifespan`` handler).  Raises early if any template is missing or
        malformed, so misconfiguration is caught before the first request.

        Raises:
            PromptValidationError: If any step template cannot be loaded.
        """
        self._llm = create_llm(self.settings)

        # Attempt to load every template to surface missing/broken files at
        # startup rather than mid-request.
        for step_name in STEP_ORDER:
            step = PIPELINE_STEPS[step_name]
            try:
                self.template_loader._load_template(step.template_name)
            except Exception as exc:
                raise PromptValidationError(
                    f"Failed to load template for {step_name}: {exc}"
                ) from exc

    # ------------------------------------------------------------------
    # 2. Streaming pipeline  (async, yields SSE-ready event dicts)
    # ------------------------------------------------------------------

    async def stream_pipeline(
        self,
        scope_request: ScopeRequest,
        db_session: Session,
    ) -> AsyncIterator[dict[str, Any]]:
        """Run the pipeline via ``astream_events`` and yield SSE event dicts.

        Yields JSON-serialisable dicts discriminated by a ``type`` field.
        The caller is responsible for serialising these to SSE frames.

        Event sequence per request
        --------------------------
        phase_start        – emitted before each step begins
        llm_token          – emitted for every streamed token within a step
        tool_start         – emitted if the LLM invokes a tool (future use)
        tool_end           – emitted when a tool call returns (future use)
        phase_complete     – emitted after each step's chain_end event
        result             – emitted once with the full ScopeDocument payload
        (error is raised, not yielded — the caller's SSE handler catches it)

        DB writes mirror ``run_pipeline``:
          PipelineRun status updated before each step.
          NodeOutput persisted after each step's chain_end.
          ScopeDocument persisted after the root chain_end.

        Args:
            scope_request: The incoming request; ``user_input`` seeds the pipeline.
            db_session:    Active SQLAlchemy session for all DB writes.

        Yields:
            Event dicts (see sequence above).

        Raises:
            PromptValidationError: If ``warmup()`` was not called first.
        """
        if self._llm is None:
            raise PromptValidationError("LLM not initialized; call warmup() first")

        # Resolve or create the PipelineRun (same logic as run_pipeline).
        pipeline_run = self._resolve_pipeline_run(scope_request, db_session)

        # Build the LangChain Runnable and seed the initial state.
        initial: dict[str, Any] = {"user_input": scope_request.user_input}
        runnable = build_scope_pipeline_runnable(self._llm, self.template_loader)

        # Set status to the first step before we start streaming.
        stream_phase = STEP_ORDER[0]  # "classify"
        pipeline_run.status = STEP_STATUS_MAP[stream_phase]
        pipeline_run.current_node = stream_phase
        db_session.add(pipeline_run)
        db_session.commit()

        # Signal to the client that the first phase is starting.
        yield {
            "type": "phase_start",
            "phase": stream_phase,
            "request_id": scope_request.id,
            "pipeline_run_id": pipeline_run.id,
        }

        try:
            async for event in runnable.astream_events(initial, version="v2"):
                et = event.get("event")    # e.g. "on_chat_model_stream"
                name = event.get("name")   # e.g. "classify", STREAM_ROOT_RUN_NAME

                # --- Incremental token from the LLM ---
                # Forward each token to the client so the UI can render
                # the response as it arrives.
                if et == "on_chat_model_stream":
                    token = extract_token_from_stream_event(event)
                    if token:
                        yield {
                            "type": "llm_token",
                            "phase": stream_phase,
                            "token": token,
                        }

                # --- Tool lifecycle events (reserved for future tool use) ---
                if et == "on_tool_start":
                    data = event.get("data") or {}
                    yield {
                        "type": "tool_start",
                        "tool": name,
                        "input": data.get("input"),
                    }

                if et == "on_tool_end":
                    data = event.get("data") or {}
                    yield {
                        "type": "tool_end",
                        "tool": name,
                        "output": data.get("output"),
                    }

                # --- Individual step completed ---
                # ``on_chain_end`` fires for every Runnable in the chain.
                # We only care about the three named pipeline steps here.
                if et == "on_chain_end" and name in STEP_STATUS_MAP:
                    out = (event.get("data") or {}).get("output")
                    # Guard: output must be a dict containing the step's key.
                    if not isinstance(out, dict) or name not in out:
                        continue

                    # Persist the step output for auditing / replay.
                    step_output = out[name]
                    node_output = NodeOutput(
                        pipeline_run_id=pipeline_run.id,
                        request_id=scope_request.id,
                        node_name=name,
                        output=step_output.model_dump(),
                    )
                    db_session.add(node_output)
                    db_session.commit()

                    # Emit the phase result so the frontend can display it progressively
                    if step_output:
                        yield {
                            "type": "phase_result",
                            "phase": name,
                            "output": step_output.model_dump(),
                        }

                    yield {"type": "phase_complete", "phase": name}

                    # Advance to the next step if one exists.
                    next_i = STEP_ORDER.index(name) + 1
                    if next_i < len(STEP_ORDER):
                        stream_phase = STEP_ORDER[next_i]
                        pipeline_run.status = STEP_STATUS_MAP[stream_phase]
                        pipeline_run.current_node = stream_phase
                        db_session.add(pipeline_run)
                        db_session.commit()
                        yield {
                            "type": "phase_start",
                            "phase": stream_phase,
                            "request_id": scope_request.id,
                            "pipeline_run_id": pipeline_run.id,
                        }

                # --- Entire pipeline completed ---
                # The root chain emits its own ``on_chain_end`` with the full
                # final state dict.  We use this to build and persist the
                # ScopeDocument and emit the ``result`` event.
                if et == "on_chain_end" and name == STREAM_ROOT_RUN_NAME:
                    final_state = (event.get("data") or {}).get("output")
                    if not isinstance(final_state, dict):
                        continue

                    gen = final_state.get("generate_scope")  # GenerateScopeOutput | None
                    cls_out = final_state.get("classify")    # ClassifyOutput | None
                    risks_out = final_state.get("analyze_risks")  # RisksOutput | None

                    if not gen or not cls_out:
                        raise RuntimeError("Pipeline completed but missing required outputs")

                    scope_doc = ScopeDocument(
                        request_id=scope_request.id,
                        pipeline_run_id=pipeline_run.id,
                        # From classify step
                        complexity=cls_out.complexity,
                        complexity_reason=cls_out.reasoning,
                        # From generate_scope step
                        deliverables=gen.deliverables,
                        tech_stack=gen.tech_stack,
                        timeline_breakdown=gen.timeline_breakdown,
                        risks=gen.risks,
                        out_of_scope=gen.out_of_scope,
                    )
                    db_session.add(scope_doc)

                    # Mark the run as done.
                    pipeline_run.status = PipelineStatus.completed
                    pipeline_run.completed_at = datetime.utcnow()
                    pipeline_run.current_node = None  # no active step
                    db_session.add(pipeline_run)
                    db_session.commit()

                    # Emit the full document payload so the client can render
                    # the final result without a separate API call.
                    yield {
                        "type": "result",
                        "document": {
                            "id": scope_doc.id,
                            "request_id": scope_doc.request_id,
                            "pipeline_run_id": scope_doc.pipeline_run_id,
                            "complexity": scope_doc.complexity.value,
                            "complexity_reason": scope_doc.complexity_reason,
                            "estimated_cost_min": scope_doc.estimated_cost_min,
                            "estimated_cost_max": scope_doc.estimated_cost_max,
                            "estimated_weeks_min": scope_doc.estimated_weeks_min,
                            "estimated_weeks_max": scope_doc.estimated_weeks_max,
                            "deliverables": scope_doc.deliverables,
                            "tech_stack": scope_doc.tech_stack,
                            "timeline_breakdown": scope_doc.timeline_breakdown,
                            "risks": scope_doc.risks,
                            "mitigations": risks_out.mitigations if risks_out else {},
                            "out_of_scope": scope_doc.out_of_scope,
                            "created_at": scope_doc.created_at.isoformat(),
                        },
                    }

        except Exception as exc:
            # Record the failure and re-raise; the SSE handler in the route
            # layer is responsible for closing the stream gracefully.
            pipeline_run.status = PipelineStatus.failed
            pipeline_run.error_message = str(exc)
            pipeline_run.completed_at = datetime.utcnow()
            db_session.add(pipeline_run)
            db_session.commit()
            raise

    # ------------------------------------------------------------------
    # 3. Internal helpers
    # ------------------------------------------------------------------

    def _resolve_pipeline_run(
        self, scope_request: ScopeRequest, db_session: Session
    ) -> PipelineRun:
        """Reuse an existing PipelineRun for *scope_request*, or create one.

        The API layer typically creates the row before calling the service.
        This method handles the case where the service is called directly
        (e.g. in tests) without a pre-existing row.

        Args:
            scope_request: The incoming request whose id is the FK.
            db_session:    Active SQLAlchemy session.

        Returns:
            A ``PipelineRun`` that is already added to *db_session*.
        """
        pipeline_run = (
            db_session.query(PipelineRun)
            .filter_by(scope_request_id=scope_request.id)
            .first()
        )
        if pipeline_run is None:
            pipeline_run = PipelineRun(
                scope_request_id=scope_request.id,
                langgraph_thread_id=str(uuid.uuid4()),
            )
            db_session.add(pipeline_run)
            db_session.flush()
        return pipeline_run
