"""Database models and schemas for the ScopeWise application.

This module contains Pydantic models used for data validation and serialization
throughout the application, including project creation and management schemas.
"""

# Standard library imports
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Optional
import uuid

# Third-party imports
from pydantic import BaseModel, StringConstraints, field_validator
from sqlmodel import SQLModel, Column, Field, JSON, Relationship

StrippedName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=120),
]


# --- Enums ---

class ComplexityLevel(str, Enum):
    simple = "simple"
    mid_tier = "mid_tier"
    complex = "complex"
    enterprise = "enterprise"


class PipelineStatus(str, Enum):
    pending = "pending"
    classifying = "classifying"
    paused = "paused"          # HITL breakpoint
    analyzing_risks = "analyzing_risks"
    generating_scope = "generating_scope"
    completed = "completed"
    failed = "failed"


class ProjectInterestForm(SQLModel, table=True):
    __tablename__ = "project_interest_forms"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )

    project_name: StrippedName = Field(index=True)
    project_type: str = Field(default='')  # e.g. "web app", "mobile app", "e-commerce platform"
    industry: str = Field(default='')  # e.g. "healthcare", "finance", "education"
    description: str = Field(default='')  # brief overview of the project and its goals

    budget_range: str = Field(default='')  # e.g. "$10k-$50k", "$50k-$200k", "$200k+"
    launch_date: str = Field(default='')  # e.g. "Q4 2024", "December 2024", "6 months from now"
    deadline_flexibility: str = Field(default='')  # e.g. "fixed", "some flexibility", "completely flexible"

    core_features: list[str] = Field(sa_column=Column(JSON), default=[])  # e.g. ["user authentication", "payment processing", "real-time chat"]
    third_party_integrations: str = Field(default='')  # e.g. "Stripe for payments, Firebase for notifications"
    user_roles: list[str] = Field(sa_column=Column(JSON), default=[])  # e.g. ["end users", "admin users", "content creators"]
    concurrent_users: str = Field(default='')  # e.g. "100-1000", "1000+"

    existing_codebase: str = Field(default='')
    existing_tech_stack: str = Field(default='')
    preferred_tech_stack: str = Field(default='')
    hosting_preference: str = Field(default='')
    design_or_development: str = Field(default='')

    top_priority: str = Field(default='')
    known_constraints: str = Field(default='')
    compliance_requirements: list[str] = Field(sa_column=Column(JSON), default=[])



# --- Scope Document (final structured output) ---

class ScopeDocument(SQLModel, table=True):
    __tablename__ = "scope_documents"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    request_id: str = Field(foreign_key="scope_requests.id", index=True)
    pipeline_run_id: str = Field(foreign_key="pipeline_runs.id")

    complexity: ComplexityLevel
    complexity_reason: str

    estimated_cost_min: Optional[int] = None
    estimated_cost_max: Optional[int] = None
    
    estimated_weeks_min: Optional[int] = None
    estimated_weeks_max: Optional[int] = None

    deliverables: list[str] = Field(sa_column=Column(JSON))
    tech_stack: dict[str, str] = Field(sa_column=Column(JSON))

    timeline_breakdown: list[dict[str, str]] = Field(sa_column=Column(JSON))

    risks: list[str] = Field(sa_column=Column(JSON))
    out_of_scope: list[str] = Field(sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    pipeline_run: Optional["PipelineRun"] = Relationship(back_populates="scope_document")


# --- Scope Request (initial user submission) ---

class ScopeRequest(SQLModel, table=True):
    __tablename__ = "scope_requests"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    project_interest_form_id: Optional[str] = Field(foreign_key="project_interest_forms.id", index=True)
    
    user_input: str = Field()  # Raw user input/description
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relationships
    pipeline_run: Optional["PipelineRun"] = Relationship(back_populates="scope_request")


# --- Pipeline Run (one per scope request) ---

class PipelineRun(SQLModel, table=True):
    __tablename__ = "pipeline_runs"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    scope_request_id: str = Field(foreign_key="scope_requests.id", index=True)
    langgraph_thread_id: str = Field(index=True)  # used to resume HITL

    status: PipelineStatus = Field(default=PipelineStatus.pending)
    current_node: Optional[str] = None            # "classify", "risks", "scope"
    error_message: Optional[str] = None

    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # relationships
    scope_request: Optional[ScopeRequest] = Relationship(back_populates="pipeline_run")
    node_outputs: list["NodeOutput"] = Relationship(back_populates="pipeline_run")
    scope_document: Optional["ScopeDocument"] = Relationship(back_populates="pipeline_run")


# --- Node Output (result of each LangGraph node) ---

class NodeOutput(SQLModel, table=True):
    __tablename__ = "node_outputs"

    id: int = Field(default=None, primary_key=True)
    pipeline_run_id: str = Field(foreign_key="pipeline_runs.id", index=True)
    request_id: str = Field(foreign_key="scope_requests.id", index=True)

    node_name: str                                # "classify", "risks", "scope"
    output: dict[str, Any] = Field(sa_column=Column(JSON)) # raw node output
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    pipeline_run: Optional[PipelineRun] = Relationship(back_populates="node_outputs")