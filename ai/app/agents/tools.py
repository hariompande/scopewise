"""Agent tools for research phase.

This module provides tools for:
- Searching firm project history (RAG)
- Checking resource availability
- Market research via web search
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from langchain_community.tools.tavily_search import TavilySearchResults

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from app.agents.schemas import (
    AvailableExpert,
    FirmHistoryOutput,
    MarketProjectExample,
    MarketResearchOutput,
    ReallocatableResource,
    ResourceAvailabilityOutput,
    SimilarProject,
)
from app.config import Settings
from app.database.models import Employee, ProjectAssignment, ProjectDocument


def create_web_search_tool(settings: Settings) -> TavilySearchResults | None:
    """Create a web search tool for market research.
    
    Returns None if Tavily API key is not configured.
    """
    if not settings.tavily_api_key:
        return None
    
    return TavilySearchResults(
        max_results=10,
        search_depth="advanced",
        tavily_api_key=settings.tavily_api_key.get_secret_value()
    )


class ResourceAvailabilityChecker:
    """Tool for checking resource availability in the firm."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def check_availability(
        self,
        required_skills: list[str],
        min_expert_level: str = "mid"
    ) -> ResourceAvailabilityOutput:
        """Check resource availability for given skills.
        
        Args:
            required_skills: List of required skills (e.g., ["React", "Node.js", "AWS"])
            min_expert_level: Minimum level for experts (junior, mid, senior, lead)
            
        Returns:
            ResourceAvailabilityOutput with available experts and reallocatable resources
        """
        # Map level to numeric for comparison
        level_order = {"junior": 1, "mid": 2, "senior": 3, "lead": 4}
        min_level_num = level_order.get(min_expert_level, 2)
        
        # Find available experts with matching skills
        all_employees = self.db_session.query(Employee).all()
        
        experts_available: list[AvailableExpert] = []
        for emp in all_employees:
            # Check if employee has any of the required skills
            has_matching_skill = any(
                skill.lower() in [s.lower() for s in emp.skills]
                for skill in required_skills
            )
            
            if has_matching_skill:
                emp_level_num = level_order.get(emp.level, 1)
                if emp_level_num >= min_level_num and emp.available:
                    experts_available.append(AvailableExpert(
                        name=emp.name,
                        role=emp.role,
                        level=emp.level,
                        skills=emp.skills,
                        current_utilization=emp.utilization_rate,
                        availability_status="available" if emp.utilization_rate < 0.5 else "partial"
                    ))
        
        # Find reallocatable resources (employees on low priority projects)
        reallocatable: list[ReallocatableResource] = []
        
        low_priority_assignments = (
            self.db_session.query(ProjectAssignment, Employee, ProjectDocument)
            .join(Employee, ProjectAssignment.employee_id == Employee.id)
            .join(ProjectDocument, ProjectAssignment.project_id == ProjectDocument.id)
            .filter(ProjectAssignment.priority.in_(["low", "medium"]))
            .all()
        )
        
        for assignment, emp, project in low_priority_assignments:
            has_matching_skill = any(
                skill.lower() in [s.lower() for s in emp.skills]
                for skill in required_skills
            )
            
            if has_matching_skill:
                reallocatable.append(ReallocatableResource(
                    name=emp.name,
                    role=emp.role,
                    level=emp.level,
                    skills=emp.skills,
                    current_project=project.project_name,
                    current_priority=assignment.priority,
                    allocation_percentage=assignment.allocation_percentage,
                    potential_availability_date=None  # Could calculate based on project end date
                ))
        
        # Build skill coverage analysis
        skill_coverage: dict[str, int] = {}
        for skill in required_skills:
            count = sum(
                1 for expert in experts_available
                if skill.lower() in [s.lower() for s in expert.skills]
            )
            skill_coverage[skill] = count
        
        # Generate recommendation
        if experts_available_count := len(experts_available) >= len(required_skills):
            recommendation = (
                f"Sufficient resources available. {experts_available_count} experts "
                f"match the required skills. Recommended to proceed with internal team."
            )
        elif experts_available_count > 0:
            recommendation = (
                f"Partial coverage available. {experts_available_count} experts found "
                f"for {len(required_skills)} skill areas. Consider augmenting team "
                f"or reallocating {len(reallocatable)} potentially available resources."
            )
        else:
            recommendation = (
                "No immediate internal resources available. Consider hiring or "
                "partnering for this project."
            )
        
        # Suggest team composition
        team_suggestion = self._suggest_team_composition(
            experts_available, reallocatable, required_skills
        )
        
        return ResourceAvailabilityOutput(
            experts_available=experts_available,
            experts_available_count=len(experts_available),
            reallocatable_resources=reallocatable,
            reallocatable_count=len(reallocatable),
            skill_coverage_analysis=skill_coverage,
            resource_recommendation=recommendation,
            potential_team_composition=team_suggestion
        )
    
    def _suggest_team_composition(
        self,
        experts: list[AvailableExpert],
        reallocatable: list[ReallocatableResource],
        required_skills: list[str]
    ) -> str:
        """Generate a suggested team composition based on available resources."""
        by_level: dict[str, list[str]] = {"lead": [], "senior": [], "mid": [], "junior": []}
        
        for expert in experts:
            by_level.setdefault(expert.level, []).append(expert.name)
        
        for resource in reallocatable:
            by_level.setdefault(resource.level, []).append(resource.name)
        
        parts = []
        if by_level["lead"] or by_level["senior"]:
            parts.append(
                f"Technical Lead: {', '.join(by_level['lead'] or by_level['senior'][:1])}"
            )
        if by_level["senior"] or by_level["mid"]:
            senior_count = len(by_level["senior"])
            parts.append(f"Senior Developers: {max(1, senior_count // 2)}-{senior_count}")
        if by_level["mid"] or by_level["junior"]:
            mid_count = len(by_level["mid"])
            parts.append(f"Mid-level Developers: {max(1, mid_count // 2)}-{mid_count}")
        
        return "Suggested team: " + "; ".join(parts) if parts else "Unable to suggest team composition due to limited resources"


class FirmHistorySearchTool:
    """Tool for searching firm project history using RAG."""
    
    def __init__(
        self,
        settings: Settings,
        db_session: Session
    ):
        self.settings = settings
        self.db_session = db_session
        self._retriever = None
    
    def _get_retriever(self):
        """Lazy-load the retriever."""
        if self._retriever is None:
            from app.agents.retrievers import FirmHistoryRetriever
            self._retriever = FirmHistoryRetriever(self.settings)
        return self._retriever
    
    async def search(
        self,
        project_description: str,
        project_type: str,
        industry: str = ""
    ) -> FirmHistoryOutput:
        """Search for similar projects in firm history.
        
        Args:
            project_description: Description of the project to find matches for
            project_type: Type of project (web app, mobile, etc.)
            industry: Industry sector (optional)
            
        Returns:
            FirmHistoryOutput with similar projects and recommendations
        """
        retriever = self._get_retriever()
        
        # Construct search query
        search_query = f"{project_type} project: {project_description}"
        if industry:
            search_query += f" in {industry} industry"
        
        # Search vector store
        # Note: scores via OpenRouter embeddings use a different scale than direct OpenAI
        results = await retriever.search(
            query=search_query,
            db_session=self.db_session,
            k=5,
            min_similarity=0.1
        )
        
        # Convert to schema format
        similar_projects: list[SimilarProject] = []
        for result in results:
            proj = result.project
            similar_projects.append(SimilarProject(
                project_name=proj.project_name,
                client_name=proj.client_name,
                industry=proj.industry,
                project_type=proj.project_type,
                description=proj.description,
                tech_stack=proj.tech_stack,
                team_size=proj.team_size,
                duration_weeks=proj.duration_weeks,
                outcome=proj.outcome,
                relevance_score=result.similarity_score,
                key_learnings=proj.challenges[0] if proj.challenges else ""
            ))
        
        # Generate summary
        if similar_projects:
            experience_summary = (
                f"Firm has completed {len(similar_projects)} similar projects. "
                f"Typical team size: {sum(p.team_size for p in similar_projects) // len(similar_projects)}-"
                f"{max(p.team_size for p in similar_projects)} people. "
                f"Typical duration: {min(p.duration_weeks for p in similar_projects)}-"
                f"{max(p.duration_weeks for p in similar_projects)} weeks."
            )
            
            # Collect tech stack patterns
            tech_stacks = [tech for p in similar_projects for tech in p.tech_stack]
            common_tech = list(set([t for t in tech_stacks if tech_stacks.count(t) > 1]))
            
            recommended_approach = (
                f"Based on similar projects, recommend using established tech stack: "
                f"{', '.join(common_tech[:5]) if common_tech else 'standard technologies'}. "
                f"Reference learnings from: {similar_projects[0].project_name}."
            )
        else:
            experience_summary = "No directly similar projects found in firm history."
            recommended_approach = (
                "This appears to be a new project type for the firm. Recommend "
                "conservative estimation and consider external expertise."
            )
        
        return FirmHistoryOutput(
            similar_projects=similar_projects,
            total_matches=len(similar_projects),
            relevant_experience_summary=experience_summary,
            recommended_approach=recommended_approach
        )


class MarketResearchTool:
    """Tool for conducting market research via web search."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._search_tool = create_web_search_tool(settings)
    
    async def research(
        self,
        project_type: str,
        industry: str = "",
        budget_range: str = ""
    ) -> MarketResearchOutput:
        """Conduct market research for a project type.
        
        Args:
            project_type: Type of project to research
            industry: Industry sector (optional)
            budget_range: Budget range hint (optional)
            
        Returns:
            MarketResearchOutput with market insights
        """
        if not self._search_tool:
            # Return placeholder if web search not configured
            return MarketResearchOutput(
                similar_projects_in_market=[],
                market_trends="Market research not available - web search not configured",
                typical_budget_range="Unable to determine",
                typical_timeline="Unable to determine",
                competitive_landscape="Unable to determine",
                technology_recommendations=[]
            )
        
        # Build search queries
        queries = [
            f"{project_type} development cost budget estimate {industry}" if industry else f"{project_type} development cost budget estimate",
            f"{project_type} project timeline duration weeks months",
            f"{project_type} technology stack best practices {industry}" if industry else f"{project_type} technology stack best practices",
            f"{project_type} market trends 2024 2025",
        ]
        
        all_results: list[MarketProjectExample] = []
        raw_snippets: list[str] = []
        
        for query in queries:
            try:
                search_results = await self._search_tool.ainvoke(query)
                # Tavily returns a list of dicts with keys: url, content, title, score
                if isinstance(search_results, list):
                    for item in search_results:
                        if isinstance(item, dict):
                            content = item.get("content", "")
                            title = item.get("title", "")
                            if content:
                                raw_snippets.append(f"[{title}] {content[:300]}")
                            # Build market examples from case study results
                            if "case study" in query or "success" in query:
                                all_results.append(MarketProjectExample(
                                    project_name=title[:80] if title else "Market example",
                                    description=content[:200] if content else "",
                                    tech_stack=[],
                                    outcome=""
                                ))
                elif isinstance(search_results, str):
                    raw_snippets.append(search_results[:500])
            except Exception:
                continue
        
        # Synthesise findings from actual search results
        combined = " ".join(raw_snippets)
        
        # Extract budget signals
        budget_matches = re.findall(r'\$[\d,]+[kKmM]?(?:\s*[-–]\s*\$[\d,]+[kKmM]?)?', combined)
        if budget_matches:
            typical_budget = ", ".join(dict.fromkeys(budget_matches[:3]))
        elif budget_range:
            typical_budget = budget_range
        else:
            typical_budget = "Unable to determine from search results"
        
        # Extract timeline signals
        timeline_matches = re.findall(r'\d+[\s-]+(?:to[\s-]+\d+\s+)?(?:weeks?|months?)', combined, re.IGNORECASE)
        if timeline_matches:
            typical_timeline = ", ".join(dict.fromkeys(m.strip() for m in timeline_matches[:3]))
        else:
            typical_timeline = "Unable to determine from search results"
        
        # Build trends summary from actual snippets
        if raw_snippets:
            trends = f"Based on current market data for {project_type}: " + " | ".join(raw_snippets[:3])[:600]
        else:
            trends = f"No market data retrieved for {project_type}."
        
        landscape = (
            f"Competitive market for {project_type} solutions"
            + (f" in the {industry} industry" if industry else "")
            + ". See search findings above for current competitive context."
        )
        
        # Extract tech recommendations from snippets
        tech_keywords = [
            "React", "Vue", "Angular", "Next.js", "TypeScript",
            "Node.js", "Python", "FastAPI", "Django", "Go",
            "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes",
            "GraphQL", "REST", "microservices", "serverless",
        ]
        found_tech = [t for t in tech_keywords if t.lower() in combined.lower()]
        tech_recommendations = found_tech[:6] if found_tech else []
        
        return MarketResearchOutput(
            similar_projects_in_market=all_results[:5],
            market_trends=trends,
            typical_budget_range=typical_budget,
            typical_timeline=typical_timeline,
            competitive_landscape=landscape,
            technology_recommendations=tech_recommendations
        )
