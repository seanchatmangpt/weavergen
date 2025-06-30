"""Enterprise Analytics and Reporting Engine.

This module provides comprehensive analytics, KPI tracking, and reporting
capabilities for enterprise Scrum management with real-time dashboards,
predictive analytics, and business intelligence features.
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass

import numpy as np
from pydantic import BaseModel, Field

from .models import (
    Sprint, UserStory, Task, Team, Project, TeamMetrics,
    ProjectHealthMetrics, BusinessValueMetrics, User,
    SprintStatus, TaskStatus, UserStoryStatus, Priority
)
from .agents import AgentContext, ExecutiveAgent


# ============================================================================
# Analytics Models and Enums
# ============================================================================

class MetricType(str, Enum):
    """Types of metrics."""
    VELOCITY = "velocity"
    BURNDOWN = "burndown"
    CYCLE_TIME = "cycle_time"
    LEAD_TIME = "lead_time"
    THROUGHPUT = "throughput"
    QUALITY = "quality"
    PREDICTABILITY = "predictability"
    TEAM_HEALTH = "team_health"
    BUSINESS_VALUE = "business_value"
    ROI = "roi"
    RISK = "risk"


class TimeFrame(str, Enum):
    """Time frame for analytics."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    SPRINT = "sprint"
    RELEASE = "release"


class DashboardType(str, Enum):
    """Types of dashboards."""
    TEAM = "team"
    PROJECT = "project"
    PORTFOLIO = "portfolio"
    EXECUTIVE = "executive"
    QUALITY = "quality"
    DELIVERY = "delivery"
    BUSINESS_VALUE = "business_value"


class MetricDataPoint(BaseModel):
    """Single metric data point."""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    quality_score: float = Field(default=1.0, ge=0, le=1)  # Data quality indicator


class TimeSeries(BaseModel):
    """Time series data for metrics."""
    metric_type: MetricType
    entity_id: UUID
    entity_type: str  # team, project, organization
    timeframe: TimeFrame
    data_points: List[MetricDataPoint]
    
    @property
    def latest_value(self) -> Optional[float]:
        """Get the latest metric value."""
        if not self.data_points:
            return None
        return max(self.data_points, key=lambda dp: dp.timestamp).value
    
    @property
    def trend(self) -> str:
        """Calculate trend direction."""
        if len(self.data_points) < 2:
            return "insufficient_data"
        
        recent = self.data_points[-5:]  # Last 5 points
        if len(recent) < 2:
            return "stable"
        
        slope = (recent[-1].value - recent[0].value) / len(recent)
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"


class KPITarget(BaseModel):
    """KPI target definition."""
    metric_type: MetricType
    target_value: float
    threshold_warning: float
    threshold_critical: float
    direction: str = "higher_better"  # higher_better, lower_better
    
    def evaluate_status(self, current_value: float) -> str:
        """Evaluate current value against targets."""
        if self.direction == "higher_better":
            if current_value >= self.target_value:
                return "excellent"
            elif current_value >= self.threshold_warning:
                return "good"
            elif current_value >= self.threshold_critical:
                return "warning"
            else:
                return "critical"
        else:  # lower_better
            if current_value <= self.target_value:
                return "excellent"
            elif current_value <= self.threshold_warning:
                return "good"
            elif current_value <= self.threshold_critical:
                return "warning"
            else:
                return "critical"


class DashboardWidget(BaseModel):
    """Dashboard widget configuration."""
    id: UUID
    title: str
    widget_type: str  # chart, kpi, table, gauge, etc.
    metric_type: MetricType
    entity_ids: List[UUID]
    timeframe: TimeFrame
    configuration: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, int] = Field(default_factory=dict)  # x, y, width, height


class Dashboard(BaseModel):
    """Dashboard configuration."""
    id: UUID
    name: str
    dashboard_type: DashboardType
    tenant_id: UUID
    owner_id: UUID
    is_public: bool = False
    widgets: List[DashboardWidget]
    layout: Dict[str, Any] = Field(default_factory=dict)
    refresh_interval: int = 300  # seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Predictive Analytics Models
# ============================================================================

class Prediction(BaseModel):
    """Prediction result."""
    entity_id: UUID
    entity_type: str
    prediction_type: str
    predicted_value: float
    confidence_interval: Tuple[float, float]
    confidence_score: float = Field(ge=0, le=1)
    prediction_date: datetime = Field(default_factory=datetime.utcnow)
    target_date: datetime
    model_used: str
    features_used: List[str]
    assumptions: List[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    """Risk assessment result."""
    entity_id: UUID
    entity_type: str
    risk_type: str
    risk_level: Priority
    probability: float = Field(ge=0, le=1)
    impact_score: float = Field(ge=0, le=100)
    risk_factors: List[str]
    mitigation_strategies: List[str]
    assessment_date: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Analytics Engine
# ============================================================================

class AnalyticsEngine:
    """Enterprise analytics and reporting engine."""
    
    def __init__(self):
        """Initialize the analytics engine."""
        self.metric_cache: Dict[str, TimeSeries] = {}
        self.kpi_targets: Dict[UUID, List[KPITarget]] = {}
        self.dashboards: Dict[UUID, Dashboard] = {}
        self.executive_agent = ExecutiveAgent()
        
        # Predictive models (in real implementation, these would be ML models)
        self.prediction_models = {
            "velocity": self._velocity_prediction_model,
            "completion_date": self._completion_date_model,
            "quality_risk": self._quality_risk_model,
            "budget_overrun": self._budget_overrun_model
        }
    
    # ========================================================================
    # Metric Collection and Calculation
    # ========================================================================
    
    async def calculate_team_velocity(self, tenant_id: UUID, team_id: UUID, sprint_count: int = 5) -> TimeSeries:
        """Calculate team velocity over recent sprints."""
        # In real implementation, this would query the database
        # For demo, we'll simulate the data
        
        data_points = []
        base_date = datetime.utcnow() - timedelta(weeks=sprint_count * 2)
        
        for i in range(sprint_count):
            # Simulate velocity data with some variance
            velocity = 25 + np.random.normal(0, 5)  # Base 25 with variance
            data_points.append(MetricDataPoint(
                timestamp=base_date + timedelta(weeks=i * 2),
                value=max(0, velocity),
                metadata={"sprint_number": i + 1}
            ))
        
        return TimeSeries(
            metric_type=MetricType.VELOCITY,
            entity_id=team_id,
            entity_type="team",
            timeframe=TimeFrame.SPRINT,
            data_points=data_points
        )
    
    async def calculate_cycle_time(self, tenant_id: UUID, team_id: UUID, days: int = 30) -> TimeSeries:
        """Calculate average cycle time for completed stories."""
        data_points = []
        base_date = datetime.utcnow() - timedelta(days=days)
        
        # Simulate daily cycle time data
        for i in range(days):
            cycle_time = 3.5 + np.random.normal(0, 1.2)  # Average 3.5 days
            data_points.append(MetricDataPoint(
                timestamp=base_date + timedelta(days=i),
                value=max(0.5, cycle_time),
                metadata={"stories_completed": np.random.randint(1, 4)}
            ))
        
        return TimeSeries(
            metric_type=MetricType.CYCLE_TIME,
            entity_id=team_id,
            entity_type="team",
            timeframe=TimeFrame.DAILY,
            data_points=data_points
        )
    
    async def calculate_quality_metrics(self, tenant_id: UUID, project_id: UUID) -> Dict[str, float]:
        """Calculate quality metrics for a project."""
        # Simulate quality metrics
        return {
            "defect_rate": 2.5,  # defects per 100 story points
            "test_coverage": 87.5,  # percentage
            "code_review_coverage": 95.0,  # percentage
            "technical_debt_ratio": 15.2,  # percentage
            "security_score": 92.0  # security assessment score
        }
    
    async def calculate_business_value_metrics(self, tenant_id: UUID, project_id: UUID) -> BusinessValueMetrics:
        """Calculate business value metrics."""
        # Simulate business value calculation
        return BusinessValueMetrics(
            project_id=project_id,
            planned_investment=Decimal("500000"),
            actual_investment=Decimal("475000"),
            realized_value=Decimal("750000"),
            projected_roi=58.0,
            features_delivered=25,
            user_adoption_rate=73.5,
            customer_satisfaction=8.2,
            revenue_impact=Decimal("200000"),
            cost_savings=Decimal("150000")
        )
    
    async def calculate_team_health_score(self, tenant_id: UUID, team_id: UUID) -> float:
        """Calculate team health score based on multiple factors."""
        # In real implementation, this would consider:
        # - Sprint goal achievement rate
        # - Velocity consistency
        # - Team satisfaction surveys
        # - Impediment resolution time
        # - Collaboration metrics
        
        factors = {
            "goal_achievement": 0.85,  # 85% sprint goal achievement
            "velocity_consistency": 0.90,  # Low velocity variance
            "satisfaction": 0.78,  # Team satisfaction score
            "collaboration": 0.88,  # Collaboration metrics
            "impediment_resolution": 0.75  # How quickly impediments are resolved
        }
        
        # Weighted average
        weights = {
            "goal_achievement": 0.25,
            "velocity_consistency": 0.20,
            "satisfaction": 0.25,
            "collaboration": 0.15,
            "impediment_resolution": 0.15
        }
        
        health_score = sum(factors[key] * weights[key] for key in factors) * 100
        return round(health_score, 1)
    
    # ========================================================================
    # Dashboard and Reporting
    # ========================================================================
    
    async def create_team_dashboard(self, tenant_id: UUID, team_id: UUID, user_id: UUID) -> Dashboard:
        """Create a comprehensive team dashboard."""
        widgets = [
            DashboardWidget(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                title="Team Velocity",
                widget_type="line_chart",
                metric_type=MetricType.VELOCITY,
                entity_ids=[team_id],
                timeframe=TimeFrame.SPRINT,
                position={"x": 0, "y": 0, "width": 6, "height": 4}
            ),
            DashboardWidget(
                id=UUID("22222222-2222-2222-2222-222222222222"),
                title="Cycle Time",
                widget_type="line_chart",
                metric_type=MetricType.CYCLE_TIME,
                entity_ids=[team_id],
                timeframe=TimeFrame.DAILY,
                position={"x": 6, "y": 0, "width": 6, "height": 4}
            ),
            DashboardWidget(
                id=UUID("33333333-3333-3333-3333-333333333333"),
                title="Team Health Score",
                widget_type="gauge",
                metric_type=MetricType.TEAM_HEALTH,
                entity_ids=[team_id],
                timeframe=TimeFrame.WEEKLY,
                position={"x": 0, "y": 4, "width": 4, "height": 3}
            ),
            DashboardWidget(
                id=UUID("44444444-4444-4444-4444-444444444444"),
                title="Sprint Burndown",
                widget_type="burndown_chart",
                metric_type=MetricType.BURNDOWN,
                entity_ids=[team_id],
                timeframe=TimeFrame.SPRINT,
                position={"x": 4, "y": 4, "width": 8, "height": 3}
            )
        ]
        
        return Dashboard(
            id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            name=f"Team Dashboard - {team_id}",
            dashboard_type=DashboardType.TEAM,
            tenant_id=tenant_id,
            owner_id=user_id,
            widgets=widgets
        )
    
    async def create_executive_dashboard(self, tenant_id: UUID, user_id: UUID) -> Dashboard:
        """Create an executive-level dashboard."""
        widgets = [
            DashboardWidget(
                id=UUID("55555555-5555-5555-5555-555555555555"),
                title="Portfolio Health",
                widget_type="health_matrix",
                metric_type=MetricType.BUSINESS_VALUE,
                entity_ids=[],  # All projects
                timeframe=TimeFrame.MONTHLY,
                position={"x": 0, "y": 0, "width": 12, "height": 6}
            ),
            DashboardWidget(
                id=UUID("66666666-6666-6666-6666-666666666666"),
                title="ROI Analysis",
                widget_type="bar_chart",
                metric_type=MetricType.ROI,
                entity_ids=[],  # All projects
                timeframe=TimeFrame.QUARTERLY,
                position={"x": 0, "y": 6, "width": 6, "height": 4}
            ),
            DashboardWidget(
                id=UUID("77777777-7777-7777-7777-777777777777"),
                title="Risk Assessment",
                widget_type="risk_matrix",
                metric_type=MetricType.RISK,
                entity_ids=[],  # All projects
                timeframe=TimeFrame.MONTHLY,
                position={"x": 6, "y": 6, "width": 6, "height": 4}
            )
        ]
        
        return Dashboard(
            id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            name="Executive Portfolio Dashboard",
            dashboard_type=DashboardType.EXECUTIVE,
            tenant_id=tenant_id,
            owner_id=user_id,
            widgets=widgets
        )
    
    async def generate_sprint_report(self, tenant_id: UUID, sprint_id: UUID) -> Dict[str, Any]:
        """Generate comprehensive sprint report."""
        # In real implementation, this would gather actual data
        
        report = {
            "sprint_id": str(sprint_id),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "planned_story_points": 42,
                "completed_story_points": 38,
                "completion_rate": 90.5,
                "sprint_goal_achieved": True
            },
            "velocity": {
                "current_sprint": 38,
                "average_velocity": 35.2,
                "variance": 8.5
            },
            "quality": {
                "defects_found": 3,
                "test_coverage": 89.5,
                "code_review_coverage": 95.0
            },
            "team_performance": {
                "impediments_count": 2,
                "impediment_resolution_time": 1.5,  # days
                "collaboration_score": 8.5
            },
            "recommendations": [
                "Consider breaking down larger stories for better predictability",
                "Increase test coverage for critical components",
                "Address recurring impediments in next retrospective"
            ]
        }
        
        return report
    
    # ========================================================================
    # Predictive Analytics
    # ========================================================================
    
    async def predict_sprint_completion(self, tenant_id: UUID, sprint_id: UUID) -> Prediction:
        """Predict sprint completion probability."""
        # Simple prediction model (in real implementation, use ML)
        current_progress = 0.65  # 65% complete
        days_remaining = 8
        historical_velocity = 35.2
        current_velocity_trend = 1.05  # 5% above average
        
        completion_probability = min(0.95, current_progress + (current_velocity_trend * 0.3))
        
        return Prediction(
            entity_id=sprint_id,
            entity_type="sprint",
            prediction_type="completion_probability",
            predicted_value=completion_probability,
            confidence_interval=(completion_probability - 0.1, completion_probability + 0.05),
            confidence_score=0.85,
            target_date=datetime.utcnow() + timedelta(days=days_remaining),
            model_used="velocity_trend_model",
            features_used=["historical_velocity", "current_progress", "team_capacity"],
            assumptions=["No major impediments", "Team availability remains stable"]
        )
    
    async def predict_project_completion_date(self, tenant_id: UUID, project_id: UUID) -> Prediction:
        """Predict project completion date."""
        # Simulation of project completion prediction
        remaining_story_points = 450
        team_velocity = 35.2
        sprints_remaining = remaining_story_points / team_velocity
        weeks_remaining = sprints_remaining * 2  # 2-week sprints
        
        completion_date = datetime.utcnow() + timedelta(weeks=weeks_remaining)
        
        return Prediction(
            entity_id=project_id,
            entity_type="project",
            prediction_type="completion_date",
            predicted_value=completion_date.timestamp(),
            confidence_interval=(
                (completion_date - timedelta(weeks=2)).timestamp(),
                (completion_date + timedelta(weeks=4)).timestamp()
            ),
            confidence_score=0.78,
            target_date=completion_date,
            model_used="velocity_projection_model",
            features_used=["team_velocity", "remaining_scope", "historical_variance"],
            assumptions=["Scope remains stable", "Team composition unchanged"]
        )
    
    async def assess_project_risks(self, tenant_id: UUID, project_id: UUID) -> List[RiskAssessment]:
        """Assess project risks using various factors."""
        risks = []
        
        # Schedule Risk
        schedule_risk = RiskAssessment(
            entity_id=project_id,
            entity_type="project",
            risk_type="schedule_delay",
            risk_level=Priority.MEDIUM,
            probability=0.35,
            impact_score=75.0,
            risk_factors=[
                "Velocity variance higher than 15%",
                "Dependencies on external teams",
                "Historical delivery delays"
            ],
            mitigation_strategies=[
                "Buffer time for critical path items",
                "Early engagement with dependent teams",
                "Regular scope review sessions"
            ]
        )
        risks.append(schedule_risk)
        
        # Quality Risk
        quality_risk = RiskAssessment(
            entity_id=project_id,
            entity_type="project",
            risk_type="quality_issues",
            risk_level=Priority.LOW,
            probability=0.20,
            impact_score=60.0,
            risk_factors=[
                "Test coverage below 85%",
                "Technical debt accumulation"
            ],
            mitigation_strategies=[
                "Implement stricter quality gates",
                "Allocate time for technical debt reduction",
                "Increase code review coverage"
            ]
        )
        risks.append(quality_risk)
        
        # Budget Risk
        budget_risk = RiskAssessment(
            entity_id=project_id,
            entity_type="project",
            risk_type="budget_overrun",
            risk_level=Priority.HIGH,
            probability=0.45,
            impact_score=85.0,
            risk_factors=[
                "Scope creep detected",
                "Resource costs increasing",
                "Extended timeline impacts"
            ],
            mitigation_strategies=[
                "Implement strict change control",
                "Regular budget reviews",
                "Stakeholder communication on trade-offs"
            ]
        )
        risks.append(budget_risk)
        
        return risks
    
    # ========================================================================
    # AI-Powered Insights
    # ========================================================================
    
    async def generate_ai_insights(self, context: AgentContext, entity_type: str, entity_id: UUID) -> List[str]:
        """Generate AI-powered insights using the executive agent."""
        if entity_type == "project":
            # Use executive agent for high-level insights
            insights_result = await self.executive_agent.generate_portfolio_insights(
                context, [], [], {}
            )
            return insights_result.strategic_recommendations
        
        # For other entity types, provide analytical insights
        insights = [
            "Team velocity has been consistent over the last 5 sprints, indicating good predictability",
            "Cycle time shows an upward trend - consider investigating potential bottlenecks",
            "Quality metrics are within acceptable ranges but test coverage could be improved",
            "Team health score suggests high satisfaction but watch for signs of burnout"
        ]
        
        return insights
    
    # ========================================================================
    # Utility Methods for Prediction Models
    # ========================================================================
    
    def _velocity_prediction_model(self, data: Dict[str, Any]) -> float:
        """Simple velocity prediction model."""
        historical_velocity = data.get("historical_velocity", [])
        if not historical_velocity:
            return 25.0  # Default
        
        # Simple moving average with trend
        recent_velocity = np.mean(historical_velocity[-3:])
        overall_velocity = np.mean(historical_velocity)
        trend_factor = recent_velocity / overall_velocity if overall_velocity > 0 else 1.0
        
        return recent_velocity * trend_factor
    
    def _completion_date_model(self, data: Dict[str, Any]) -> datetime:
        """Project completion date prediction model."""
        remaining_work = data.get("remaining_work", 100)
        team_velocity = data.get("team_velocity", 25)
        
        sprints_needed = remaining_work / team_velocity
        weeks_needed = sprints_needed * 2  # Assuming 2-week sprints
        
        return datetime.utcnow() + timedelta(weeks=weeks_needed)
    
    def _quality_risk_model(self, data: Dict[str, Any]) -> float:
        """Quality risk assessment model."""
        test_coverage = data.get("test_coverage", 85)
        defect_rate = data.get("defect_rate", 2.5)
        code_review_coverage = data.get("code_review_coverage", 90)
        
        # Simple risk score calculation
        risk_score = 0.0
        if test_coverage < 80:
            risk_score += 0.3
        if defect_rate > 5:
            risk_score += 0.4
        if code_review_coverage < 85:
            risk_score += 0.2
        
        return min(1.0, risk_score)
    
    def _budget_overrun_model(self, data: Dict[str, Any]) -> float:
        """Budget overrun risk assessment model."""
        budget_utilization = data.get("budget_utilization", 0.75)
        scope_change_rate = data.get("scope_change_rate", 0.1)
        schedule_variance = data.get("schedule_variance", 0.05)
        
        # Risk increases with high utilization, scope changes, and schedule variance
        risk_score = (budget_utilization * 0.4 + 
                     scope_change_rate * 0.4 + 
                     schedule_variance * 0.2)
        
        return min(1.0, risk_score)


# ============================================================================
# Report Generator
# ============================================================================

class ReportGenerator:
    """Generate various reports for different stakeholders."""
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        """Initialize with analytics engine."""
        self.analytics = analytics_engine
    
    async def generate_team_performance_report(
        self, 
        tenant_id: UUID, 
        team_id: UUID, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Generate comprehensive team performance report."""
        
        # Gather metrics
        velocity_data = await self.analytics.calculate_team_velocity(tenant_id, team_id)
        cycle_time_data = await self.analytics.calculate_cycle_time(tenant_id, team_id)
        health_score = await self.analytics.calculate_team_health_score(tenant_id, team_id)
        
        report = {
            "report_type": "team_performance",
            "team_id": str(team_id),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": {
                "velocity": {
                    "current": velocity_data.latest_value,
                    "average": np.mean([dp.value for dp in velocity_data.data_points]),
                    "trend": velocity_data.trend
                },
                "cycle_time": {
                    "current": cycle_time_data.latest_value,
                    "average": np.mean([dp.value for dp in cycle_time_data.data_points]),
                    "trend": cycle_time_data.trend
                },
                "health_score": health_score
            },
            "insights": [
                "Team is maintaining consistent velocity",
                "Cycle time has improved by 15% over the reporting period",
                "Team health score indicates high engagement"
            ],
            "recommendations": [
                "Continue current practices for velocity consistency",
                "Focus on further reducing cycle time through process optimization",
                "Monitor team workload to maintain health score"
            ]
        }
        
        return report
    
    async def generate_executive_summary(
        self, 
        tenant_id: UUID, 
        user_id: UUID
    ) -> Dict[str, Any]:
        """Generate executive summary report."""
        
        # This would aggregate data across all projects and teams
        summary = {
            "report_type": "executive_summary",
            "generated_at": datetime.utcnow().isoformat(),
            "generated_for": str(user_id),
            "portfolio_overview": {
                "total_projects": 12,
                "active_projects": 8,
                "total_teams": 15,
                "total_budget": "$2,400,000",
                "budget_utilized": "67%"
            },
            "key_metrics": {
                "overall_health_score": 82.5,
                "average_velocity": 28.3,
                "on_time_delivery": "78%",
                "quality_score": 87.2,
                "customer_satisfaction": 8.4
            },
            "strategic_insights": [
                "Portfolio health is strong with 82.5% overall score",
                "Delivery predictability has improved by 12% this quarter",
                "Quality metrics exceed industry benchmarks",
                "Customer satisfaction remains high across all projects"
            ],
            "risk_alerts": [
                "3 projects at risk of schedule delays",
                "Budget variance increasing in 2 projects",
                "Resource constraints in mobile development team"
            ],
            "recommended_actions": [
                "Reallocate resources to projects at risk",
                "Review scope of projects with budget variance",
                "Consider hiring additional mobile developers"
            ]
        }
        
        return summary