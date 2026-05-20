"""
Pipeline execution and streaming endpoints.

ROUTE MAP
=========

  POST /pipeline/run
  ──────────────────
  Blocking execution backed by the same streaming Runnable as /run-stream.
  Consumes the SSE event stream internally and returns the final
  ScopeDocument as JSON once the ``result`` event arrives.

    Client ──POST──► run_pipeline()
                          │
                          ├─ create ScopeRequest + PipelineRun (DB)
                          ├─ consume agent_service.stream_pipeline()
                          │       classify → analyze_risks → generate_scope
                          └─ return PipelineRunResponse (JSON) from result event


  POST /pipeline/run-stream
  ─────────────────────────
  Async streaming execution via LangChain ``astream_events``.  Returns an
  SSE stream so the client can render tokens and phase transitions in real
  time.  The final ``result`` event carries the same document payload as
  POST /run.

    Client ──POST──► run_pipeline_stream()
                          │
                          ├─ create ScopeRequest + PipelineRun (DB)
                          └─ StreamingResponse(event_generator)
                                    │
                                    │  agent_service.stream_pipeline()
                                    │
                                    ├── data: {"type":"phase_start", ...}
                                    ├── data: {"type":"llm_token",   ...}  (×N)
                                    ├── data: {"type":"phase_complete",...}
                                    ├──  ... (repeated for each of 3 steps)
                                    ├── data: {"type":"result",      ...}
                                    └── data: {"type":"error",       ...}  (on failure)


  GET /pipeline/stream/{request_id}
  ──────────────────────────────────
  Status-polling SSE stream.  Useful when the client did not connect to
  /run-stream from the start (e.g. page reload mid-run).  Polls the DB
  every 0.5 s and emits an event on each status transition.

    Client ──GET──► stream_pipeline_status(request_id)
                          │
                          └─ StreamingResponse(event_generator)
                                    │
                                    ├── data: {"status":"classifying",      ...}
                                    ├── data: {"status":"analyzing_risks",  ...}
                                    ├── data: {"status":"generating_scope", ...}
                                    └── data: {"status":"completed",        ...}
                                              (stream closes on completed / failed)
"""

import asyncio
import json
import logging
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from app.agents import ParsingError, PromptValidationError, TransientLLMError
from app.database import SessionLocal
from app.database.models import (
    PipelineRun,
    PipelineStatus,
    ScopeRequest,
)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class PipelineRunRequest(BaseModel):
    """Request body for both /run and /run-stream endpoints."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_input": "A small inventory web app with auth and CSV export."
            }
        }
    )

    user_input: str = Field(
        min_length=1,
        description=(
            "Required. Non-empty description of what to scope. "
            "Omitting this field or sending '' returns HTTP 422."
        ),
    )


class PipelineRunResponse(BaseModel):
    """Response body for POST /run — mirrors the ScopeDocument DB model."""

    model_config = ConfigDict(
        # Accept both datetime objects and ISO-format strings so this model
        # works whether it's constructed from a DB row or a stream_pipeline
        # result event (which serialises created_at via .isoformat()).
        populate_by_name=True,
    )

    # Identity
    id: str
    request_id: str
    pipeline_run_id: str

    # Complexity (from classify step)
    complexity: str
    complexity_reason: str

    # Cost / timeline estimates (populated post-processing, may be None)
    estimated_cost_min: int | None = None
    estimated_cost_max: int | None = None
    estimated_weeks_min: int | None = None
    estimated_weeks_max: int | None = None

    # Scope content (from generate_scope step)
    deliverables: list[str]
    tech_stack: dict[str, str]
    timeline_breakdown: list[dict[str, str]]
    risks: list[str]
    mitigations: dict[str, str]
    out_of_scope: list[str]

    created_at: datetime


class SSEEvent(BaseModel):
    """Payload for GET /stream/{request_id} status-polling events."""

    status: str               # PipelineStatus value (e.g. "classifying")
    current_node: str | None  # Active step name, or None when idle
    error_message: str | None = None


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/pipeline", tags=["pipeline"])
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. POST /run  —  blocking, backed by the streaming Runnable
# ---------------------------------------------------------------------------

@router.post("/run", response_model=PipelineRunResponse)
async def run_pipeline(request: Request, payload: PipelineRunRequest) -> PipelineRunResponse:
    """Execute the scope analysis pipeline and return the completed ScopeDocument.

    Internally consumes ``AgentService.stream_pipeline()`` (the same Runnable
    chain used by ``/run-stream``) and waits for the ``result`` event before
    returning.  This keeps a single execution path while still presenting a
    simple blocking JSON API to callers that don't need token streaming.

    Args:
        request: FastAPI ``Request`` used to access ``app.state.agent_service``.
        payload: Request body containing ``user_input``.

    Returns:
        ``PipelineRunResponse`` with the full scope document.

    Raises:
        HTTPException 502: If the LLM service is unavailable (``TransientLLMError``).
        HTTPException 422: If an LLM response cannot be parsed (``ParsingError``).
    """
    db_session = SessionLocal()
    try:
        logger.info(
            "Pipeline run started (user_input length=%s)", len(payload.user_input)
        )

        # --- Persist the incoming request ---
        scope_request = ScopeRequest(user_input=payload.user_input)
        db_session.add(scope_request)
        db_session.flush()

        pipeline_run = PipelineRun(
            scope_request_id=scope_request.id,
            langgraph_thread_id=str(uuid.uuid4()),
            status=PipelineStatus.pending,
        )
        db_session.add(pipeline_run)
        db_session.commit()

        agent_service = request.app.state.agent_service
        logger.info(
            "Running LLM pipeline request_id=%s pipeline_run_id=%s",
            scope_request.id,
            pipeline_run.id,
        )

        # Consume the stream internally; only the final ``result`` event matters.
        document: dict | None = None
        async for event in agent_service.stream_pipeline(scope_request, db_session):
            if event.get("type") == "result":
                document = event["document"]
                break

        if document is None:
            raise RuntimeError("Pipeline completed without emitting a result event")

        logger.info(
            "Pipeline run finished request_id=%s", scope_request.id
        )

        return PipelineRunResponse(**document)

    except TransientLLMError as exc:
        raise HTTPException(
            status_code=502, detail=f"LLM service unavailable: {exc}"
        ) from None
    except ParsingError as exc:
        raise HTTPException(
            status_code=422, detail=f"Invalid LLM response: {exc}"
        ) from None
    finally:
        db_session.close()


# ---------------------------------------------------------------------------
# 2. POST /run-stream  —  async, token-by-token SSE
# ---------------------------------------------------------------------------

@router.post(
    "/run-stream",
    response_class=StreamingResponse,
    summary="Run pipeline with LangChain streaming (SSE)",
    responses={
        200: {
            "description": (
                "Server-Sent Events (text/event-stream). Each `data:` line is JSON "
                "with a `type` field. Swagger UI often buffers or does not render "
                "live streams; use curl, httpx, or browser EventSource instead."
            ),
            "content": {
                "text/event-stream": {
                    "schema": {"type": "string"},
                }
            },
        }
    },
)
async def run_pipeline_stream(
    request: Request, payload: PipelineRunRequest
) -> StreamingResponse:
    """Run the scope pipeline and stream progress as Server-Sent Events.

    Creates the same DB rows as ``POST /run``, then delegates to
    ``AgentService.stream_pipeline()`` which wraps the LangChain Runnable
    with ``astream_events``.  Each yielded event dict is serialised to a
    ``data: <json>\\n\\n`` SSE frame.

    Common ``type`` values in the stream:
    - ``phase_start``    – a pipeline step is beginning
    - ``llm_token``      – an incremental token from the LLM
    - ``phase_complete`` – a pipeline step finished
    - ``tool_start``     – a tool call is starting (future use)
    - ``tool_end``       – a tool call returned (future use)
    - ``result``         – final document payload (same fields as POST /run)
    - ``error``          – an error occurred; stream ends after this frame
    """
    db_session = SessionLocal()
    logger.info(
        "Pipeline run-stream started (user_input length=%s)", len(payload.user_input)
    )

    # --- Persist the incoming request (same as /run) ---
    scope_request = ScopeRequest(user_input=payload.user_input)
    db_session.add(scope_request)
    db_session.flush()

    pipeline_run = PipelineRun(
        scope_request_id=scope_request.id,
        langgraph_thread_id=str(uuid.uuid4()),
        status=PipelineStatus.pending,
    )
    db_session.add(pipeline_run)
    db_session.commit()

    agent_service = request.app.state.agent_service

    async def event_generator() -> AsyncGenerator[str]:
        """Consume agent events and format them as SSE frames.

        Each event dict from ``stream_pipeline`` is serialised with
        ``json.dumps(default=str)`` — the ``default=str`` fallback handles
        datetime objects and other non-JSON-native types gracefully.
        """
        try:
            async for ev in agent_service.stream_pipeline(scope_request, db_session):
                yield f"data: {json.dumps(ev, default=str)}\n\n"

        except ParsingError as exc:
            # LLM response failed schema validation — emit error frame and close.
            yield f"data: {json.dumps({'type': 'error', 'message': f'Invalid LLM response: {exc}'})}\n\n"
        except TransientLLMError as exc:
            # LLM provider unavailable — emit error frame and close.
            yield f"data: {json.dumps({'type': 'error', 'message': f'LLM service unavailable: {exc}'})}\n\n"
        except PromptValidationError as exc:
            # Misconfiguration (e.g. warmup not called) — emit error frame and close.
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
        except Exception as exc:
            # Catch-all for unexpected errors — emit error frame and close.
            logger.exception("Unexpected error in pipeline stream")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Internal error: {exc}'})}\n\n"
        finally:
            # Always close the DB session, even if the client disconnects early.
            db_session.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # Tells nginx not to buffer the response — critical for SSE to work
            # behind a reverse proxy.
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# 3. GET /stream/{request_id}  —  status-polling SSE
# ---------------------------------------------------------------------------

@router.get("/stream/{request_id}")
async def stream_pipeline_status(request_id: str) -> StreamingResponse:
    """Stream ``PipelineRun`` status transitions as Server-Sent Events.

    Polls the DB every 0.5 s and emits an ``SSEEvent`` whenever the
    ``PipelineRun.status`` changes.  The stream closes automatically once
    the run reaches a terminal state (``completed`` or ``failed``).

    This endpoint is useful when the client was not connected to
    ``/run-stream`` from the start (e.g. after a page reload mid-run).

    Args:
        request_id: The ``ScopeRequest.id`` to watch.

    Returns:
        ``StreamingResponse`` (text/event-stream) of ``SSEEvent`` JSON frames.

    Raises:
        HTTPException 404: If no ``ScopeRequest`` with ``request_id`` exists.
        (404 is emitted as an SSE error frame rather than an HTTP error, since
        the response has already started as a stream.)
    """

    async def event_generator() -> AsyncGenerator[str]:
        """Poll the DB and emit an event on each status change."""
        db_session = SessionLocal()
        try:
            # --- Validate that the request exists ---
            scope_request = (
                db_session.query(ScopeRequest).filter_by(id=request_id).first()
            )
            if not scope_request:
                yield f"data: {json.dumps({'error': 'Request not found'})}\n\n"
                return

            # --- Locate the associated PipelineRun ---
            pipeline_run = (
                db_session.query(PipelineRun)
                .filter_by(scope_request_id=request_id)
                .first()
            )
            if not pipeline_run:
                yield f"data: {json.dumps({'error': 'Pipeline run not found'})}\n\n"
                return

            last_status = None

            while True:
                # Re-read the row from the DB to pick up status changes made
                # by the worker running the pipeline in another session.
                db_session.refresh(pipeline_run)

                # Only emit an event when the status actually changes, to avoid
                # flooding the client with identical frames.
                if pipeline_run.status != last_status:
                    event = SSEEvent(
                        status=pipeline_run.status.value,
                        current_node=pipeline_run.current_node,
                        error_message=pipeline_run.error_message,
                    )
                    yield f"data: {event.model_dump_json()}\n\n"
                    last_status = pipeline_run.status

                # Stop polling once the run reaches a terminal state.
                if pipeline_run.status in (
                    PipelineStatus.completed,
                    PipelineStatus.failed,
                ):
                    break

                await asyncio.sleep(0.5)  # poll interval

        finally:
            db_session.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering for SSE
        },
    )
