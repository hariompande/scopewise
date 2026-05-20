from pydantic import BaseModel

from app.database.models import ComplexityLevel


class ClassifyOutput(BaseModel):
    complexity: ComplexityLevel
    reasoning: str


class RisksOutput(BaseModel):
    risks: list[str]
    mitigations: dict[str, str]


class GenerateScopeOutput(BaseModel):
    deliverables: list[str]
    tech_stack: dict[str, str]
    timeline_breakdown: list[dict[str, str]]
    risks: list[str]
    out_of_scope: list[str]