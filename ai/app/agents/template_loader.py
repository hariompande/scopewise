from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from app.agents import PromptValidationError
from app.agents.pipeline import PIPELINE_STEPS

# Character-based limit (not token-based); 1 token ≈ 4 chars for English text.
MAX_PROMPT_CHARS = 32_000


class TemplateLoader:
    """Loads and renders Jinja2 prompt templates for pipeline steps.

    Instances are cheap but the internal cache is per-instance.
    Use as a singleton (e.g. via DI) to get cache reuse across requests.
    """

    def __init__(self, *, reload: bool = False) -> None:
        """
        Args:
            reload: If True, Jinja2 reloads templates from disk on every render.
                    Useful in development; leave False in production.
        """
        templates_dir = Path(__file__).parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            auto_reload=reload,
        )
        self._cache: dict[str, Template] = {}
        self._reload = reload

    def render(self, step_name: str, context: dict[str, Any]) -> str:
        """Render the template for *step_name* with the given *context*.

        Template variables are the top-level keys of *context* only
        (i.e. use ``{{ my_key }}``, not ``{{ context.my_key }}``).

        Raises:
            PromptValidationError: Unknown step, missing template, or output too large.
        """
        step = PIPELINE_STEPS.get(step_name)
        if step is None:
            raise PromptValidationError(f"Unknown step: {step_name!r}")

        template = self._load_template(step.template_name)
        rendered = template.render(**context)

        if len(rendered) > MAX_PROMPT_CHARS:
            raise PromptValidationError(
                f"Rendered prompt too large for step {step_name!r}: "
                f"{len(rendered):,} chars (max {MAX_PROMPT_CHARS:,})"
            )

        return rendered

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_template(self, template_name: str) -> Template:
        if not self._reload and template_name in self._cache:
            return self._cache[template_name]

        try:
            template = self._env.get_template(template_name)
        except TemplateNotFound as exc:
            raise PromptValidationError(f"Template not found: {template_name!r}") from exc

        self._cache[template_name] = template
        return template