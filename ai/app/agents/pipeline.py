from dataclasses import dataclass
from typing import Type

from app.agents.schemas import (
    ClassifyOutput,
    FirmHistoryOutput,
    GenerateScopeOutput,
    MarketResearchOutput,
    ResourceAvailabilityOutput,
    RisksOutput,
)
from pydantic import BaseModel

@dataclass(frozen=True)
class StepDefinition:
    template_name: str
    output_schema: Type[BaseModel]
    next_step: str | None

# Extended pipeline with research phase before classification
# Research steps run tools (RAG, DB queries, web search) to enrich context
PIPELINE_STEPS: dict[str, StepDefinition] = {
    # --- Research Phase ---
    "search_firm_history": StepDefinition(
        template_name="search_firm_history.j2",
        output_schema=FirmHistoryOutput,
        next_step="check_resources"
    ),
    "check_resources": StepDefinition(
        template_name="check_resources.j2",
        output_schema=ResourceAvailabilityOutput,
        next_step="market_research"
    ),
    "market_research": StepDefinition(
        template_name="market_research.j2",
        output_schema=MarketResearchOutput,
        next_step="classify"
    ),
    # --- Original Pipeline Steps ---
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

# Step order matches actual execution: research phase runs first to inform LLM steps
STEP_ORDER: list[str] = [
    "search_firm_history",
    "check_resources",
    "market_research",
    "classify",
    "analyze_risks",
    "generate_scope",
]

