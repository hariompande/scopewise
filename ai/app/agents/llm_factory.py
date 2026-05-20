from __future__ import annotations

from typing import Any, cast

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openrouter import ChatOpenRouter
from tenacity import (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.agents import TransientLLMError
from app.config import Settings

RETRYABLE_STATUS_CODES = {429, 500, 502, 503}

_RETRY_WAIT = wait_exponential(multiplier=1, min=1, max=10)


def _extract_status_code(error: BaseException) -> int | None:
    """Walk common exception shapes to find an HTTP status code."""
    # Different SDKs surface the HTTP status in different places.
    # Check the common shapes we expect before giving up.
    for candidate in (
        getattr(error, "status_code", None),
        getattr(getattr(error, "response", None), "status_code", None),
        (getattr(error, "body", None) or {}).get("status_code"),
    ):
        if isinstance(candidate, int):
            return candidate
    return None


def _is_retryable(error: BaseException) -> bool:
    # Only retry transient HTTP failures that are typically safe to try again.
    return _extract_status_code(error) in RETRYABLE_STATUS_CODES


def _unwrap_retry_error(exc: RetryError, label: str) -> TransientLLMError:
    """Extract the root cause from a RetryError and wrap it."""
    # Preserve the original failure as the cause so callers still see the
    # low-level error after retries are exhausted.
    last = exc.last_attempt.exception()  # None only if attempt returned normally
    cause = last if last is not None else exc
    raise TransientLLMError(f"LLM {label} failed after retry exhaustion") from cause


class RetryingChatModel(BaseChatModel):
    """Thin BaseChatModel subclass that adds retry logic around ChatOpenRouter."""

    # Declared so Pydantic / LangChain field machinery doesn't interfere.
    _llm: ChatOpenRouter
    _sync_retrying: Retrying
    _async_retrying: AsyncRetrying

    def __init__(self, llm: ChatOpenRouter, max_retries: int, **kwargs: Any) -> None:
        # BaseChatModel is a Pydantic v2 model; we must run its __init__ so fields
        # like `callbacks` exist (invoke/generate read them on `self`).
        super().__init__(**kwargs)
        object.__setattr__(self, "_llm", llm)
        object.__setattr__(self, "_sync_retrying", self._build_sync(max_retries))
        object.__setattr__(self, "_async_retrying", self._build_async(max_retries))

    # ------------------------------------------------------------------
    # BaseChatModel abstract interface
    # ------------------------------------------------------------------

    @property
    def _llm_type(self) -> str:
        return self._llm._llm_type

    def _generate(self, *args: Any, **kwargs: Any) -> Any:
        # Apply the retry policy to the underlying LangChain generation call.
        try:
            return self._sync_retrying(self._llm._generate, *args, **kwargs)
        except RetryError as exc:
            raise _unwrap_retry_error(exc, "invoke") from None

    async def _agenerate(self, *args: Any, **kwargs: Any) -> Any:
        # Mirror the sync path for async generation.
        try:
            return await self._async_retrying(self._llm._agenerate, *args, **kwargs)
        except RetryError as exc:
            raise _unwrap_retry_error(exc, "ainvoke") from None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_sync(max_retries: int) -> Retrying:
        # Tenacity retries only the transient statuses above, with exponential backoff.
        return Retrying(
            stop=stop_after_attempt(max_retries),
            wait=_RETRY_WAIT,
            retry=retry_if_exception(_is_retryable),
            reraise=False,
        )

    @staticmethod
    def _build_async(max_retries: int) -> AsyncRetrying:
        # Keep the async policy aligned with the sync policy.
        return AsyncRetrying(
            stop=stop_after_attempt(max_retries),
            wait=_RETRY_WAIT,
            retry=retry_if_exception(_is_retryable),
            reraise=False,
        )


def create_llm(settings: Settings) -> BaseChatModel:
    # ChatOpenRouter's `timeout` is milliseconds (maps to SDK `timeout_ms`).
    timeout_ms = max(1, settings.openrouter_timeout) * 1000
    llm = ChatOpenRouter(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        base_url=settings.openrouter_base_url,
        temperature=settings.openrouter_temperature,
        timeout=timeout_ms,
        # Avoid stacking long OpenRouter SDK retries on top of RetryingChatModel.
        max_retries=0,
    )
    return RetryingChatModel(llm=llm, max_retries=settings.openrouter_max_retries)