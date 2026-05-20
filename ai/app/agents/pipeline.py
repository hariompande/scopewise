from dataclasses import dataclass
from typing import Type

from app.agents.schemas import ClassifyOutput, GenerateScopeOutput, RisksOutput
from pydantic import BaseModel

@dataclass(frozen=True)
class StepDefinition:
    template_name: str
    output_schema: Type[BaseModel]
    next_step: str | None

PIPELINE_STEPS: dict[str, StepDefinition] = {
    "classify": StepDefinition(
        template_name="classify.j2",
        output_schema=ClassifyOutput,
        next_step="analyze_risks"
    ),
    "analyze_risks": StepDefinition(
        template_name="risks.j2",
        output_schema=RisksOutput,
        next_step="generate_scope"
    ),
    "generate_scope": StepDefinition(
        template_name="generate_scope.j2",
        output_schema=GenerateScopeOutput,
        next_step=None
    ),
}

STEP_ORDER: list[str] = ["classify", "analyze_risks", "generate_scope"]

