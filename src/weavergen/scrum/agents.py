"""Enterprise Scrum Agents with Multi-Tenant Support.

This module implements the core AI agents for enterprise Scrum management
with full multi-tenancy, security, and scalability features.
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Set
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.models.openai import OpenAIModel

from .models import (
    UserStory, Task, Sprint, TeamMetrics, ProjectHealthMetrics,
    Priority, TaskStatus, UserStoryStatus, SprintStatus,
    AIInsight, Team, Project, User, Meeting, Impediment
)
from ..examples.ollama_utils import get_ollama_model


# ============================================================================
# Agent Context and Dependencies
# ============================================================================

class AgentContext(BaseModel):
    """Context passed to all agents for multi-tenant operations."""
    tenant_id: UUID
    user_id: UUID
    user_roles: Set[str]
    organization_features: Set[str]
    session_id: Optional[str] = None
    
    # Caching and Performance
    cache_ttl: int = 300  # 5 minutes default
    enable_ml_predictions: bool = True
    
    # Security Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def has_permission(self, required_role: str) -> bool:
        """Check if user has required role."""
        return required_role in self.user_roles or "admin" in self.user_roles
    
    def has_feature(self, feature: str) -> bool:
        """Check if organization has feature enabled."""
        return feature in self.organization_features


class DataRepository:
    """Mock repository for data access (would be replaced with actual DB)."""
    
    async def get_team(self, tenant_id: UUID, team_id: UUID) -> Optional[Team]:
        """Get team by ID with tenant isolation."""
        # Implementation would query database with tenant_id filter
        pass
    
    async def get_sprint(self, tenant_id: UUID, sprint_id: UUID) -> Optional[Sprint]:
        """Get sprint by ID with tenant isolation."""
        pass
    
    async def get_user_stories(self, tenant_id: UUID, sprint_id: UUID) -> List[UserStory]:
        """Get user stories for a sprint."""
        pass
    
    async def save_user_story(self, story: UserStory) -> UserStory:
        """Save user story to database."""
        pass
    
    async def get_team_velocity_history(self, tenant_id: UUID, team_id: UUID) -> List[float]:
        """Get historical velocity data for team."""
        pass


# ============================================================================
# Core Agent Base Class
# ============================================================================

class ScrumAgentBase:
    """Base class for all Scrum agents with enterprise features."""
    
    def __init__(self, model_name: str = "qwen3:latest"):
        """Initialize base agent."""
        self.model = get_ollama_model(model_name)
        self.repository = DataRepository()
        
    async def audit_action(self, context: AgentContext, action: str, details: Dict[str, Any]):
        """Record audit trail for compliance."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": str(context.tenant_id),
            "user_id": str(context.user_id),
            "action": action,
            "details": details,
            "ip_address": context.ip_address,
            "user_agent": context.user_agent
        }
        # In real implementation, this would go to audit log storage
        print(f"AUDIT: {audit_entry}")
    
    def check_permissions(self, context: AgentContext, required_roles: List[str]):
        """Check if user has required permissions."""
        if not any(context.has_permission(role) for role in required_roles):
            raise PermissionError(f"User requires one of: {required_roles}")


# ============================================================================
# Scrum Master Agent
# ============================================================================

class SprintPlanningResult(BaseModel):
    """Result of sprint planning analysis."""
    recommended_capacity: float
    story_recommendations: List[Dict[str, Any]]
    velocity_prediction: float
    risk_assessment: str
    planning_notes: List[str]


class ScrumMasterAgent(ScrumAgentBase):
    """AI Scrum Master for sprint management and team facilitation."""
    
    def __init__(self):
        super().__init__()
        
        # Sprint Planning Agent
        self.planning_agent = Agent(
            model=self.model,
            result_type=SprintPlanningResult,
            system_prompt="""You are an expert Scrum Master AI assistant.
            
            Analyze team data and provide sprint planning recommendations based on:
            - Historical velocity and capacity
            - Team member availability
            - Story complexity and dependencies
            - Risk factors and impediments
            
            Provide data-driven insights for optimal sprint planning.""",
            deps_type=AgentContext
        )
        
        # Daily Standup Agent
        self.standup_agent = Agent(
            model=self.model,
            result_type=List[AIInsight],
            system_prompt="""Analyze daily standup data and identify:
            - Potential blockers and impediments
            - Team collaboration issues
            - Progress anomalies
            - Recommendations for improvement
            
            Focus on actionable insights for the Scrum Master.""",
            deps_type=AgentContext
        )
        
        # Retrospective Agent
        self.retrospective_agent = Agent(
            model=self.model,
            result_type=Dict[str, List[str]],
            system_prompt="""Facilitate retrospective analysis by categorizing feedback into:
            - What went well
            - What could be improved
            - Action items for next sprint
            - Process improvement suggestions
            
            Provide structured output for retrospective meetings.""",
            deps_type=AgentContext
        )
    
    async def plan_sprint(
        self,
        context: AgentContext,
        team_id: UUID,
        sprint_duration_days: int,
        available_stories: List[UserStory]
    ) -> SprintPlanningResult:
        """Generate sprint planning recommendations."""
        
        self.check_permissions(context, ["scrum_master", "product_owner"])
        
        # Gather team data
        team = await self.repository.get_team(context.tenant_id, team_id)
        velocity_history = await self.repository.get_team_velocity_history(context.tenant_id, team_id)
        
        # Prepare context for AI agent
        planning_context = f"""
        Team: {team.name if team else 'Unknown'}
        Sprint Duration: {sprint_duration_days} days
        Team Capacity: {team.capacity_per_sprint if team else 0} story points
        Historical Velocity: {velocity_history[-5:] if velocity_history else []}
        Available Stories: {len(available_stories)}
        Story Details: {[{'title': s.title, 'points': s.story_points, 'priority': s.priority} for s in available_stories[:10]]}
        """
        
        result = await self.planning_agent.run(planning_context, deps=context)
        
        # Audit the planning action
        await self.audit_action(context, "sprint_planning", {
            "team_id": str(team_id),
            "sprint_duration": sprint_duration_days,
            "stories_analyzed": len(available_stories)
        })
        
        return result.output
    
    async def analyze_daily_standup(
        self,
        context: AgentContext,
        team_id: UUID,
        standup_updates: List[Dict[str, Any]]
    ) -> List[AIInsight]:
        """Analyze daily standup for issues and recommendations."""
        
        self.check_permissions(context, ["scrum_master"])
        
        # Format standup data for analysis
        standup_context = f"""
        Team ID: {team_id}
        Date: {datetime.utcnow().date()}
        Updates: {standup_updates}
        """
        
        result = await self.standup_agent.run(standup_context, deps=context)
        
        await self.audit_action(context, "standup_analysis", {
            "team_id": str(team_id),
            "updates_count": len(standup_updates)
        })
        
        return result.output
    
    async def facilitate_retrospective(
        self,
        context: AgentContext,
        sprint_id: UUID,
        team_feedback: List[str]
    ) -> Dict[str, List[str]]:
        """Process retrospective feedback and generate action items."""
        
        self.check_permissions(context, ["scrum_master"])
        
        sprint = await self.repository.get_sprint(context.tenant_id, sprint_id)
        
        retro_context = f"""
        Sprint: {sprint.name if sprint else 'Unknown'}
        Team Feedback: {team_feedback}
        Sprint Metrics: Planned: {sprint.committed_story_points if sprint else 0}, 
                       Completed: {sprint.completed_story_points if sprint else 0}
        """
        
        result = await self.retrospective_agent.run(retro_context, deps=context)
        
        await self.audit_action(context, "retrospective_facilitation", {
            "sprint_id": str(sprint_id),
            "feedback_items": len(team_feedback)
        })
        
        return result.output


# ============================================================================
# Product Owner Agent
# ============================================================================

class BacklogPrioritization(BaseModel):
    """Result of backlog prioritization analysis."""
    prioritized_stories: List[Dict[str, Any]]
    business_value_analysis: Dict[str, Any]
    recommendations: List[str]
    risk_factors: List[str]


class ProductOwnerAgent(ScrumAgentBase):
    """AI Product Owner for backlog management and prioritization."""
    
    def __init__(self):
        super().__init__()
        
        # Backlog Prioritization Agent
        self.prioritization_agent = Agent(
            model=self.model,
            result_type=BacklogPrioritization,
            system_prompt="""You are an expert Product Owner AI assistant.
            
            Analyze user stories and prioritize them based on:
            - Business value and customer impact
            - Technical dependencies and complexity
            - Market timing and competitive advantage
            - Resource constraints and team capacity
            
            Provide clear prioritization rationale and business value analysis.""",
            deps_type=AgentContext
        )
        
        # User Story Generation Agent
        self.story_generation_agent = Agent(
            model=self.model,
            result_type=UserStory,
            system_prompt="""Generate well-formed user stories with:
            - Clear user persona and need
            - Specific acceptance criteria
            - Appropriate story point estimation
            - Business value justification
            
            Follow industry best practices for user story creation.""",
            deps_type=AgentContext
        )
        
        # Release Planning Agent
        self.release_planning_agent = Agent(
            model=self.model,
            result_type=Dict[str, Any],
            system_prompt="""Create release plans by analyzing:
            - Feature dependencies and sequencing
            - Team velocity and capacity
            - Market windows and deadlines
            - Risk mitigation strategies
            
            Provide realistic timelines and milestone recommendations.""",
            deps_type=AgentContext
        )
    
    async def prioritize_backlog(
        self,
        context: AgentContext,
        project_id: UUID,
        stories: List[UserStory],
        business_objectives: List[str]
    ) -> BacklogPrioritization:
        """Analyze and prioritize product backlog."""
        
        self.check_permissions(context, ["product_owner", "stakeholder"])
        
        # Prepare stories for analysis
        story_data = [
            {
                "id": str(s.id),
                "title": s.title,
                "business_value": s.business_value,
                "story_points": s.story_points,
                "priority": s.priority,
                "dependencies": [str(dep) for dep in s.depends_on]
            }
            for s in stories
        ]
        
        prioritization_context = f"""
        Project ID: {project_id}
        Business Objectives: {business_objectives}
        Stories to Prioritize: {story_data}
        Total Stories: {len(stories)}
        """
        
        result = await self.prioritization_agent.run(prioritization_context, deps=context)
        
        await self.audit_action(context, "backlog_prioritization", {
            "project_id": str(project_id),
            "stories_analyzed": len(stories)
        })
        
        return result.output
    
    async def generate_user_story(
        self,
        context: AgentContext,
        feature_description: str,
        user_persona: str,
        business_context: str
    ) -> UserStory:
        """Generate a user story from feature requirements."""
        
        self.check_permissions(context, ["product_owner"])
        
        story_context = f"""
        Feature Description: {feature_description}
        User Persona: {user_persona}
        Business Context: {business_context}
        Tenant ID: {context.tenant_id}
        Created By: {context.user_id}
        """
        
        result = await self.story_generation_agent.run(story_context, deps=context)
        
        # Set tenant and audit fields
        story = result.output
        story.tenant_id = context.tenant_id
        story.created_by = context.user_id
        
        await self.audit_action(context, "user_story_generation", {
            "story_title": story.title,
            "feature_description": feature_description
        })
        
        return story
    
    async def plan_release(
        self,
        context: AgentContext,
        project_id: UUID,
        target_date: date,
        must_have_features: List[str],
        nice_to_have_features: List[str]
    ) -> Dict[str, Any]:
        """Generate release plan with timeline and milestones."""
        
        self.check_permissions(context, ["product_owner", "project_manager"])
        
        release_context = f"""
        Project ID: {project_id}
        Target Release Date: {target_date}
        Must-Have Features: {must_have_features}
        Nice-to-Have Features: {nice_to_have_features}
        Current Date: {date.today()}
        """
        
        result = await self.release_planning_agent.run(release_context, deps=context)
        
        await self.audit_action(context, "release_planning", {
            "project_id": str(project_id),
            "target_date": target_date.isoformat(),
            "feature_count": len(must_have_features) + len(nice_to_have_features)
        })
        
        return result.output


# ============================================================================
# Developer Agent
# ============================================================================

class TechnicalAnalysis(BaseModel):
    """Technical analysis and recommendations."""
    complexity_assessment: str
    effort_estimation: Dict[str, Any]
    technical_risks: List[str]
    architecture_recommendations: List[str]
    testing_strategy: List[str]


class DeveloperAgent(ScrumAgentBase):
    """AI Developer agent for technical analysis and estimation."""
    
    def __init__(self):
        super().__init__()
        
        # Technical Analysis Agent
        self.technical_agent = Agent(
            model=self.model,
            result_type=TechnicalAnalysis,
            system_prompt="""You are an expert software developer AI assistant.
            
            Analyze user stories and provide technical insights:
            - Code complexity and effort estimation
            - Technical risks and dependencies
            - Architecture and design recommendations
            - Testing strategy and quality considerations
            
            Focus on practical, actionable technical guidance.""",
            deps_type=AgentContext
        )
        
        # Code Review Agent
        self.code_review_agent = Agent(
            model=self.model,
            result_type=List[Dict[str, Any]],
            system_prompt="""Provide code review feedback focusing on:
            - Code quality and best practices
            - Security vulnerabilities
            - Performance optimization opportunities
            - Maintainability improvements
            
            Give specific, actionable recommendations.""",
            deps_type=AgentContext
        )
    
    async def analyze_technical_requirements(
        self,
        context: AgentContext,
        user_story: UserStory,
        existing_codebase_info: str
    ) -> TechnicalAnalysis:
        """Analyze technical requirements and complexity."""
        
        self.check_permissions(context, ["developer", "tech_lead"])
        
        analysis_context = f"""
        User Story: {user_story.title}
        Description: {user_story.description}
        Acceptance Criteria: {user_story.acceptance_criteria}
        Existing Codebase: {existing_codebase_info}
        Current Story Points: {user_story.story_points}
        """
        
        result = await self.technical_agent.run(analysis_context, deps=context)
        
        await self.audit_action(context, "technical_analysis", {
            "story_id": str(user_story.id),
            "story_title": user_story.title
        })
        
        return result.output
    
    async def estimate_effort(
        self,
        context: AgentContext,
        task_description: str,
        complexity_factors: List[str]
    ) -> Dict[str, Any]:
        """Estimate development effort for tasks."""
        
        self.check_permissions(context, ["developer"])
        
        estimation_context = f"""
        Task: {task_description}
        Complexity Factors: {complexity_factors}
        Team Experience Level: Senior  # Could be dynamic
        """
        
        # Use technical agent for effort estimation
        result = await self.technical_agent.run(estimation_context, deps=context)
        
        await self.audit_action(context, "effort_estimation", {
            "task_description": task_description,
            "complexity_factors": complexity_factors
        })
        
        return {
            "estimated_hours": result.output.effort_estimation,
            "confidence_level": "medium",
            "assumptions": ["Team has required skills", "No major blockers"]
        }


# ============================================================================
# QA Agent
# ============================================================================

class QualityAnalysis(BaseModel):
    """Quality analysis and testing recommendations."""
    test_coverage_assessment: float
    quality_risks: List[str]
    test_strategy: List[str]
    automation_opportunities: List[str]
    quality_gates: List[str]


class QAAgent(ScrumAgentBase):
    """AI QA agent for quality assurance and testing strategy."""
    
    def __init__(self):
        super().__init__()
        
        # Quality Analysis Agent
        self.quality_agent = Agent(
            model=self.model,
            result_type=QualityAnalysis,
            system_prompt="""You are an expert QA engineer AI assistant.
            
            Analyze quality requirements and provide:
            - Test strategy and coverage recommendations
            - Quality risk assessment
            - Test automation opportunities
            - Quality gates and acceptance criteria
            
            Focus on comprehensive quality assurance practices.""",
            deps_type=AgentContext
        )
        
        # Test Case Generation Agent
        self.test_case_agent = Agent(
            model=self.model,
            result_type=List[Dict[str, str]],
            system_prompt="""Generate comprehensive test cases including:
            - Positive and negative test scenarios
            - Edge cases and boundary conditions
            - Integration test requirements
            - Performance and security considerations
            
            Provide detailed test steps and expected results.""",
            deps_type=AgentContext
        )
    
    async def analyze_quality_requirements(
        self,
        context: AgentContext,
        user_story: UserStory,
        quality_standards: Dict[str, Any]
    ) -> QualityAnalysis:
        """Analyze quality requirements for a user story."""
        
        self.check_permissions(context, ["qa_engineer", "test_lead"])
        
        quality_context = f"""
        User Story: {user_story.title}
        Acceptance Criteria: {user_story.acceptance_criteria}
        Definition of Done: {user_story.definition_of_done}
        Quality Standards: {quality_standards}
        Test Cases: {user_story.test_cases}
        """
        
        result = await self.quality_agent.run(quality_context, deps=context)
        
        await self.audit_action(context, "quality_analysis", {
            "story_id": str(user_story.id),
            "quality_standards": list(quality_standards.keys())
        })
        
        return result.output
    
    async def generate_test_cases(
        self,
        context: AgentContext,
        user_story: UserStory,
        test_type: str = "functional"
    ) -> List[Dict[str, str]]:
        """Generate test cases for a user story."""
        
        self.check_permissions(context, ["qa_engineer"])
        
        test_context = f"""
        User Story: {user_story.title}
        Description: {user_story.description}
        Acceptance Criteria: {user_story.acceptance_criteria}
        Test Type: {test_type}
        """
        
        result = await self.test_case_agent.run(test_context, deps=context)
        
        await self.audit_action(context, "test_case_generation", {
            "story_id": str(user_story.id),
            "test_type": test_type,
            "test_cases_generated": len(result.output)
        })
        
        return result.output


# ============================================================================
# Executive Agent
# ============================================================================

class ExecutiveInsights(BaseModel):
    """Executive-level insights and recommendations."""
    portfolio_health: Dict[str, Any]
    strategic_recommendations: List[str]
    roi_analysis: Dict[str, float]
    risk_assessment: Dict[str, Any]
    resource_optimization: List[str]


class ExecutiveAgent(ScrumAgentBase):
    """AI Executive agent for strategic insights and portfolio management."""
    
    def __init__(self):
        super().__init__()
        
        # Executive Dashboard Agent
        self.executive_agent = Agent(
            model=self.model,
            result_type=ExecutiveInsights,
            system_prompt="""You are an executive AI assistant providing strategic insights.
            
            Analyze portfolio data and provide:
            - High-level portfolio health assessment
            - Strategic recommendations for decision making
            - ROI and business value analysis
            - Risk assessment and mitigation strategies
            - Resource optimization opportunities
            
            Focus on business outcomes and strategic value.""",
            deps_type=AgentContext
        )
    
    async def generate_portfolio_insights(
        self,
        context: AgentContext,
        projects: List[Project],
        team_metrics: List[TeamMetrics],
        financial_data: Dict[str, Any]
    ) -> ExecutiveInsights:
        """Generate executive-level portfolio insights."""
        
        self.check_permissions(context, ["executive", "portfolio_manager"])
        
        portfolio_context = f"""
        Projects Count: {len(projects)}
        Active Teams: {len(team_metrics)}
        Portfolio Health: {[p.health_score for p in projects]}
        Budget Utilization: {financial_data.get('budget_utilization', 'N/A')}
        ROI Targets: {[p.roi_target for p in projects if p.roi_target]}
        """
        
        result = await self.executive_agent.run(portfolio_context, deps=context)
        
        await self.audit_action(context, "portfolio_analysis", {
            "projects_analyzed": len(projects),
            "teams_analyzed": len(team_metrics)
        })
        
        return result.output


# ============================================================================
# Agent Orchestrator
# ============================================================================

class ScrumAgentOrchestrator:
    """Orchestrates multiple Scrum agents for complex workflows."""
    
    def __init__(self):
        """Initialize all agents."""
        self.scrum_master = ScrumMasterAgent()
        self.product_owner = ProductOwnerAgent()
        self.developer = DeveloperAgent()
        self.qa_agent = QAAgent()
        self.executive = ExecutiveAgent()
    
    async def comprehensive_sprint_analysis(
        self,
        context: AgentContext,
        sprint_id: UUID
    ) -> Dict[str, Any]:
        """Run comprehensive analysis using multiple agents."""
        
        # Gather sprint data
        sprint = await self.scrum_master.repository.get_sprint(context.tenant_id, sprint_id)
        if not sprint:
            raise ValueError(f"Sprint {sprint_id} not found")
        
        # Run parallel analysis with different agents
        tasks = [
            self.scrum_master.analyze_daily_standup(context, sprint.team_id, []),
            self.developer.analyze_technical_requirements(context, UserStory(), ""),
            self.qa_agent.analyze_quality_requirements(context, UserStory(), {})
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "sprint_id": str(sprint_id),
            "scrum_master_insights": results[0] if not isinstance(results[0], Exception) else None,
            "technical_analysis": results[1] if not isinstance(results[1], Exception) else None,
            "quality_analysis": results[2] if not isinstance(results[2], Exception) else None,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }