from pydantic import BaseModel, Field

from app.database.models import ComplexityLevel


# --- Research Phase Output Schemas ---

class SimilarProject(BaseModel):
    """A similar project from firm history."""
    project_name: str
    client_name: str
    industry: str
    project_type: str
    description: str
    tech_stack: list[str]
    team_size: int
    duration_weeks: int
    outcome: str
    relevance_score: float = Field(description="Similarity score 0-1")
    key_learnings: str = Field(description="Key lessons from this project applicable to current request")


class FirmHistoryOutput(BaseModel):
    """Output from searching firm project history."""
    similar_projects: list[SimilarProject]
    total_matches: int
    relevant_experience_summary: str = Field(
        description="Summary of firm's relevant experience for this project type"
    )
    recommended_approach: str = Field(
        description="Recommended approach based on past similar projects"
    )


class AvailableExpert(BaseModel):
    """An available expert for the project."""
    name: str
    role: str
    level: str
    skills: list[str]
    current_utilization: float
    availability_status: str  # "available", "partial", "busy"


class ReallocatableResource(BaseModel):
    """A resource that could be reallocated from a lower priority project."""
    name: str
    role: str
    level: str
    skills: list[str]
    current_project: str
    current_priority: str
    allocation_percentage: float
    potential_availability_date: str | None = None


class ResourceAvailabilityOutput(BaseModel):
    """Output from checking resource availability."""
    experts_available: list[AvailableExpert]
    experts_available_count: int
    reallocatable_resources: list[ReallocatableResource]
    reallocatable_count: int
    skill_coverage_analysis: dict[str, int] = Field(
        description="Map of required skills to number of available experts"
    )
    resource_recommendation: str = Field(
        description="Recommendation on resource allocation for this project"
    )
    potential_team_composition: str = Field(
        description="Suggested team composition based on available resources"
    )


class MarketProjectExample(BaseModel):
    """An example of a similar project found in market research."""
    project_name: str
    company: str
    industry: str
    description: str
    tech_stack: list[str]
    timeline: str
    budget_range: str | None = None
    outcome: str
    source_url: str | None = None


class MarketResearchOutput(BaseModel):
    """Output from web search market research."""
    similar_projects_in_market: list[MarketProjectExample]
    market_trends: str = Field(description="Current trends for this project type")
    typical_budget_range: str = Field(description="Typical budget range in the market")
    typical_timeline: str = Field(description="Typical timeline for such projects")
    competitive_landscape: str = Field(description="Overview of competitive landscape")
    technology_recommendations: list[str] = Field(
        description="Recommended technologies based on market research"
    )


# --- Original Pipeline Output Schemas ---

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