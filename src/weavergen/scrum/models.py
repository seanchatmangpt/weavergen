"""Enterprise Scrum Data Models.

Comprehensive data models for enterprise-scale Scrum implementation
with full SAS capabilities including multi-tenancy, compliance, and analytics.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import HttpUrl
from typing import Annotated


# ============================================================================
# Core Enums and Types
# ============================================================================

class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class StoryPointScale(str, Enum):
    FIBONACCI = "fibonacci"  # 1, 2, 3, 5, 8, 13, 21
    POWER_OF_TWO = "power_of_two"  # 1, 2, 4, 8, 16, 32
    T_SHIRT = "t_shirt"  # XS, S, M, L, XL, XXL
    LINEAR = "linear"  # 1, 2, 3, 4, 5, 6, 7, 8, 9, 10


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    TESTING = "testing"
    DONE = "done"
    BLOCKED = "blocked"


class SprintStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UserStoryStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    IN_SPRINT = "in_sprint"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    DONE = "done"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class MeetingType(str, Enum):
    SPRINT_PLANNING = "sprint_planning"
    DAILY_STANDUP = "daily_standup"
    SPRINT_REVIEW = "sprint_review"
    RETROSPECTIVE = "retrospective"
    BACKLOG_REFINEMENT = "backlog_refinement"


class UserRole(str, Enum):
    PRODUCT_OWNER = "product_owner"
    SCRUM_MASTER = "scrum_master"
    DEVELOPER = "developer"
    QA_ENGINEER = "qa_engineer"
    STAKEHOLDER = "stakeholder"
    ADMIN = "admin"


class ComplianceLevel(str, Enum):
    SOX = "sox"
    GDPR = "gdpr"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"


# ============================================================================
# Base Models
# ============================================================================

class BaseEntity(BaseModel):
    """Base entity with common fields for all models."""
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID = Field(description="Multi-tenant isolation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: UUID = Field(description="User who created this entity")
    updated_by: Optional[UUID] = None
    version: int = Field(default=1, description="Optimistic locking version")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class AuditableEntity(BaseEntity):
    """Entity with full audit trail."""
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_tags: Set[ComplianceLevel] = Field(default_factory=set)
    
    def add_audit_entry(self, action: str, user_id: UUID, details: Dict[str, Any] = None):
        """Add an audit trail entry."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": str(user_id),
            "details": details or {}
        }
        self.audit_trail.append(entry)


# ============================================================================
# Organization and Tenant Models
# ============================================================================

class Organization(AuditableEntity):
    """Multi-tenant organization."""
    name: str = Field(min_length=1, max_length=100)
    domain: str = Field(description="Organization domain for SSO")
    subscription_tier: str = Field(default="enterprise")
    max_users: int = Field(default=1000)
    max_projects: int = Field(default=100)
    features: Set[str] = Field(default_factory=set)
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if not v or "." not in v:
            raise ValueError("Valid domain required")
        return v.lower()


class User(AuditableEntity):
    """Enterprise user with role-based access."""
    email: str
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    roles: Set[UserRole] = Field(default_factory=set)
    is_active: bool = True
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    # SSO Integration
    sso_provider: Optional[str] = None
    sso_user_id: Optional[str] = None
    
    # Enterprise Features
    department: Optional[str] = None
    cost_center: Optional[str] = None
    manager_id: Optional[UUID] = None
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


# ============================================================================
# Project and Team Models
# ============================================================================

class Team(AuditableEntity):
    """Scrum team with enterprise features."""
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(max_length=500)
    members: Set[UUID] = Field(default_factory=set)
    scrum_master_id: Optional[UUID] = None
    product_owner_id: Optional[UUID] = None
    
    # Team Metrics
    velocity_history: List[float] = Field(default_factory=list)
    capacity_per_sprint: float = Field(default=0.0)
    story_point_scale: StoryPointScale = StoryPointScale.FIBONACCI
    
    # Enterprise Features
    cost_center: Optional[str] = None
    budget_allocated: Optional[Decimal] = None
    geographical_location: Optional[str] = None
    
    @field_validator("members")
    @classmethod
    def validate_members(cls, v: Set[UUID]) -> Set[UUID]:
        if len(v) > 12:  # Scrum team size recommendation
            raise ValueError("Team size should not exceed 12 members")
        return v


class Project(AuditableEntity):
    """Enterprise project with portfolio management."""
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=1000)
    key: str = Field(min_length=2, max_length=10, description="Project key (e.g., PROJ)")
    team_ids: Set[UUID] = Field(default_factory=set)
    
    # Project Timeline
    start_date: date
    target_end_date: date
    actual_end_date: Optional[date] = None
    
    # Business Value
    business_value: int = Field(ge=1, le=100, description="Business priority 1-100")
    roi_target: Optional[Decimal] = None
    budget: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    
    # Status and Health
    health_score: float = Field(ge=0, le=100, default=75)
    risk_level: Priority = Priority.MEDIUM
    
    # Stakeholders
    sponsor_id: Optional[UUID] = None
    stakeholder_ids: Set[UUID] = Field(default_factory=set)
    
    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not v.isupper() or not v.isalpha():
            raise ValueError("Project key must be uppercase letters only")
        return v


# ============================================================================
# Product Backlog Models
# ============================================================================

class Epic(AuditableEntity):
    """Large feature or initiative spanning multiple sprints."""
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=2000)
    project_id: UUID
    
    # Epic Planning
    business_value: int = Field(ge=1, le=100)
    effort_estimate: Optional[int] = Field(ge=1, description="Story points")
    target_release: Optional[str] = None
    
    # Progress Tracking
    total_story_points: int = Field(default=0)
    completed_story_points: int = Field(default=0)
    
    @property
    def completion_percentage(self) -> float:
        if self.total_story_points == 0:
            return 0.0
        return (self.completed_story_points / self.total_story_points) * 100


class UserStory(AuditableEntity):
    """User story with comprehensive tracking."""
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=2000)
    acceptance_criteria: List[str] = Field(default_factory=list)
    
    # Hierarchy
    project_id: UUID
    epic_id: Optional[UUID] = None
    parent_story_id: Optional[UUID] = None
    
    # Planning and Estimation
    story_points: Optional[int] = Field(ge=0, le=100)
    business_value: int = Field(ge=1, le=100, default=50)
    priority: Priority = Priority.MEDIUM
    
    # Status and Assignment
    status: UserStoryStatus = UserStoryStatus.DRAFT
    assignee_id: Optional[UUID] = None
    sprint_id: Optional[UUID] = None
    
    # Quality and Testing
    definition_of_done: List[str] = Field(default_factory=list)
    test_cases: List[str] = Field(default_factory=list)
    
    # Dependencies and Blocking
    depends_on: Set[UUID] = Field(default_factory=set)
    blocks: Set[UUID] = Field(default_factory=set)
    
    # Tags and Labels
    labels: Set[str] = Field(default_factory=set)
    components: Set[str] = Field(default_factory=set)


class Task(AuditableEntity):
    """Individual task within a user story."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(max_length=1000)
    user_story_id: UUID
    
    # Assignment and Status
    assignee_id: Optional[UUID] = None
    status: TaskStatus = TaskStatus.TODO
    
    # Time Tracking
    estimated_hours: Optional[float] = Field(ge=0)
    actual_hours: Optional[float] = Field(ge=0)
    remaining_hours: Optional[float] = Field(ge=0)
    
    # Task Details
    type: str = Field(default="development")  # development, testing, documentation, etc.
    priority: Priority = Priority.MEDIUM
    
    # Dependencies
    depends_on: Set[UUID] = Field(default_factory=set)
    
    @field_validator("actual_hours", "remaining_hours")
    @classmethod
    def validate_hours(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Hours cannot be negative")
        return v


# ============================================================================
# Sprint Models
# ============================================================================

class Sprint(AuditableEntity):
    """Sprint with comprehensive tracking and analytics."""
    name: str = Field(min_length=1, max_length=100)
    goal: str = Field(max_length=500, description="Sprint goal")
    project_id: UUID
    team_id: UUID
    
    # Sprint Timeline
    start_date: date
    end_date: date
    
    # Sprint Planning
    planned_capacity: float = Field(ge=0, description="Team capacity in story points")
    committed_story_points: int = Field(default=0)
    completed_story_points: int = Field(default=0)
    
    # Status
    status: SprintStatus = SprintStatus.PLANNING
    
    # Sprint Content
    user_story_ids: Set[UUID] = Field(default_factory=set)
    
    # Sprint Metrics (populated during/after sprint)
    velocity: Optional[float] = None
    burndown_data: List[Dict[str, Any]] = Field(default_factory=list)
    
    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1
    
    @property
    def completion_percentage(self) -> float:
        if self.committed_story_points == 0:
            return 0.0
        return (self.completed_story_points / self.committed_story_points) * 100
    
    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        if self.duration_days > 30:
            raise ValueError("Sprint duration should not exceed 30 days")
        return self


# ============================================================================
# Meeting and Event Models
# ============================================================================

class Meeting(AuditableEntity):
    """Scrum ceremony with automated insights."""
    title: str = Field(min_length=1, max_length=200)
    type: MeetingType
    project_id: UUID
    sprint_id: Optional[UUID] = None
    
    # Meeting Details
    scheduled_at: datetime
    duration_minutes: int = Field(ge=15, le=480)
    location: Optional[str] = None
    meeting_url: Optional[HttpUrl] = None
    
    # Participants
    organizer_id: UUID
    required_attendees: Set[UUID] = Field(default_factory=set)
    optional_attendees: Set[UUID] = Field(default_factory=set)
    actual_attendees: Set[UUID] = Field(default_factory=set)
    
    # Meeting Content
    agenda: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    action_items: List[Dict[str, Any]] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    
    # Meeting Analytics
    effectiveness_score: Optional[float] = Field(ge=0, le=10)
    attendance_rate: Optional[float] = Field(ge=0, le=100)


class Impediment(AuditableEntity):
    """Impediment tracking with resolution workflow."""
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=1000)
    
    # Context
    project_id: UUID
    sprint_id: Optional[UUID] = None
    reported_by: UUID
    assigned_to: Optional[UUID] = None
    
    # Impediment Details
    severity: Priority = Priority.MEDIUM
    category: str = Field(description="e.g., technical, process, external")
    
    # Resolution Tracking
    status: str = Field(default="open")  # open, in_progress, resolved, closed
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    # Impact Assessment
    affected_stories: Set[UUID] = Field(default_factory=set)
    estimated_delay_days: Optional[int] = Field(ge=0)


# ============================================================================
# Analytics and Reporting Models
# ============================================================================

class TeamMetrics(BaseModel):
    """Team performance metrics for analytics."""
    team_id: UUID
    sprint_id: UUID
    calculation_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Velocity Metrics
    planned_velocity: float
    actual_velocity: float
    velocity_variance: float
    
    # Quality Metrics
    defect_rate: float = Field(ge=0, le=100)
    test_coverage: float = Field(ge=0, le=100)
    code_review_coverage: float = Field(ge=0, le=100)
    
    # Delivery Metrics
    cycle_time_days: float
    lead_time_days: float
    throughput: int
    
    # Team Health
    team_satisfaction: Optional[float] = Field(ge=1, le=10)
    burnout_risk: float = Field(ge=0, le=100)
    collaboration_score: float = Field(ge=0, le=100)


class ProjectHealthMetrics(BaseModel):
    """Project-level health and progress metrics."""
    project_id: UUID
    calculation_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Progress Metrics
    scope_completion: float = Field(ge=0, le=100)
    schedule_health: float = Field(ge=0, le=100)
    budget_health: float = Field(ge=0, le=100)
    
    # Quality Metrics
    overall_quality_score: float = Field(ge=0, le=100)
    technical_debt_ratio: float = Field(ge=0, le=100)
    
    # Risk Assessment
    risk_score: float = Field(ge=0, le=100)
    critical_issues_count: int = Field(ge=0)
    blocked_stories_count: int = Field(ge=0)
    
    # Predictive Analytics
    estimated_completion_date: date
    success_probability: float = Field(ge=0, le=100)
    recommended_actions: List[str] = Field(default_factory=list)


class BusinessValueMetrics(BaseModel):
    """Business value and ROI tracking."""
    project_id: UUID
    calculation_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Financial Metrics
    planned_investment: Decimal
    actual_investment: Decimal
    realized_value: Decimal
    projected_roi: float
    
    # Value Delivery
    features_delivered: int
    user_adoption_rate: float = Field(ge=0, le=100)
    customer_satisfaction: float = Field(ge=1, le=10)
    
    # Business Impact
    revenue_impact: Optional[Decimal] = None
    cost_savings: Optional[Decimal] = None
    market_share_impact: Optional[float] = None


# ============================================================================
# Integration and API Models
# ============================================================================

class Integration(AuditableEntity):
    """External system integration configuration."""
    name: str = Field(min_length=1, max_length=100)
    type: str  # jira, github, slack, teams, etc.
    endpoint: HttpUrl
    
    # Authentication
    auth_type: str  # oauth, api_key, basic, etc.
    credentials: Dict[str, str] = Field(default_factory=dict)  # Encrypted in storage
    
    # Configuration
    mapping_config: Dict[str, Any] = Field(default_factory=dict)
    sync_frequency: str = Field(default="hourly")
    is_active: bool = True
    
    # Status
    last_sync: Optional[datetime] = None
    sync_status: str = Field(default="pending")
    error_count: int = Field(default=0)


class Webhook(AuditableEntity):
    """Webhook configuration for real-time integrations."""
    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    events: Set[str] = Field(default_factory=set)
    
    # Security
    secret: Optional[str] = None
    is_active: bool = True
    
    # Delivery Tracking
    last_delivery: Optional[datetime] = None
    success_rate: float = Field(ge=0, le=100, default=100.0)
    failure_count: int = Field(default=0)


# ============================================================================
# AI/ML Enhancement Models
# ============================================================================

class AIInsight(BaseModel):
    """AI-generated insights and recommendations."""
    id: UUID = Field(default_factory=uuid4)
    type: str  # prediction, recommendation, anomaly, risk_alert
    entity_type: str  # project, sprint, team, user_story
    entity_id: UUID
    
    # Insight Content
    title: str
    description: str
    confidence_score: float = Field(ge=0, le=1)
    impact_level: Priority = Priority.MEDIUM
    
    # AI Model Information
    model_name: str
    model_version: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Action Items
    recommended_actions: List[str] = Field(default_factory=list)
    estimated_impact: Optional[str] = None
    
    # User Feedback
    user_feedback: Optional[str] = None
    feedback_rating: Optional[int] = Field(ge=1, le=5)


class PredictiveModel(BaseModel):
    """ML model metadata for predictions."""
    name: str
    version: str
    type: str  # velocity_prediction, risk_assessment, etc.
    
    # Model Performance
    accuracy: float = Field(ge=0, le=1)
    last_trained: datetime
    training_data_size: int
    
    # Model Configuration
    parameters: Dict[str, Any] = Field(default_factory=dict)
    features: List[str] = Field(default_factory=list)
    
    # Usage Tracking
    prediction_count: int = Field(default=0)
    last_used: Optional[datetime] = None