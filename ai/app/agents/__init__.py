"""Agent pipeline package."""


class TransientLLMError(Exception):
	"""Raised when an LLM call fails transiently and may succeed on retry."""


class PromptValidationError(Exception):
	"""Raised when a prompt template or prompt input is invalid."""


class ParsingError(Exception):
	"""Raised when an LLM response cannot be parsed into the expected schema."""


__all__ = [
	"TransientLLMError",
	"PromptValidationError",
	"ParsingError",
]
