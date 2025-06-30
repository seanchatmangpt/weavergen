"""
Complete Pydantic models for Roberts Rules + OpenTelemetry Communication System
Generated from weaver-forge-complete.yaml semantic conventions
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import hashlib

# Enums from semantic conventions

class AgentStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"

class MessageType(str, Enum):
    STATEMENT = "statement"
    MOTION = "motion"
    SECOND = "second"
    VOTE = "vote"
    POINT_OF_ORDER = "point_of_order"
    RECOGNITION_REQUEST = "recognition_request"
    GRANT_RECOGNITION = "grant_recognition"
    REPORT = "report"

class MeetingType(str, Enum):
    BOARD = "board"
    COMMITTEE = "committee"
    DEVELOPMENT = "development"
    SCRUM_OF_SCRUMS = "scrum_of_scrums"

class CommunicationMode(str, Enum):
    OTEL_SPANS = "otel_spans"
    DIRECT = "direct"
    HYBRID = "hybrid"

class ArchitectureLayer(str, Enum):
    COMMANDS = "commands"
    OPERATIONS = "operations"
    RUNTIME = "runtime"
    CONTRACTS = "contracts"

# Core Models

class Agent(BaseModel):
    """AI agent participating in distributed systems"""
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Human-readable name")
    role: str = Field(..., description="Role or position")
    expertise: List[str] = Field(default_factory=list, description="Areas of expertise")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    
    class Config:
        use_enum_values = True

class OTelMessage(BaseModel):
    """Message sent through OpenTelemetry spans"""
    message_id: str = Field(..., description="Unique message identifier")
    sender: str = Field(..., description="Agent ID of sender")
    recipient: str = Field(..., description="Agent ID or 'all' for broadcast")
    message_type: MessageType
    content: str = Field(..., description="Message content")
    trace_id: str = Field(..., description="OTel trace ID")
    span_id: str = Field(..., description="OTel span ID")
    parent_span_id: Optional[str] = Field(None, description="Parent span for hierarchy")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('recipient')
    def validate_recipient(cls, v):
        if v != 'all' and not v.startswith('agent-'):
            raise ValueError('Recipient must be "all" or valid agent ID')
        return v

class EnhancedMeeting(BaseModel):
    """Roberts Rules meeting with OTel integration"""
    meeting_id: str = Field(..., description="Unique meeting identifier")
    meeting_type: MeetingType
    trace_context: Dict[str, str] = Field(..., description="OTel trace context")
    communication_mode: CommunicationMode = Field(default=CommunicationMode.OTEL_SPANS)
    chair_agent_id: str
    secretary_agent_id: str
    members_present: List[str] = Field(..., description="Agent IDs present")
    quorum: int
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    
    @property
    def has_quorum(self) -> bool:
        return len(self.members_present) >= self.quorum

class OTelMotion(BaseModel):
    """Parliamentary motion with OpenTelemetry tracking"""
    id: str = Field(..., description="Unique motion identifier")
    trace_id: str = Field(..., description="OTel trace when motion was made")
    proposer_span_id: str = Field(..., description="Span ID of proposer's message")
    seconder_span_ids: List[str] = Field(default_factory=list)
    vote_span_ids: Dict[str, str] = Field(default_factory=dict, description="agent_id -> vote span")
    discussion_span_ids: List[str] = Field(default_factory=list)
    text: str = Field(..., description="Motion text")
    motion_type: str = Field(..., description="Type of motion")
    status: str = Field(default="pending")
    result: Optional[str] = None
    
    def add_vote(self, agent_id: str, span_id: str):
        self.vote_span_ids[agent_id] = span_id
    
    def calculate_votes(self) -> Dict[str, int]:
        # In real implementation, would query spans for vote values
        return {"aye": 0, "nay": 0, "abstain": 0}

class FileAnalysis(BaseModel):
    """Agent's analysis of a project file"""
    agent_id: str
    file_path: str
    file_hash: str = Field(..., description="MD5 hash of file contents")
    insights: List[str] = Field(..., description="Discovered insights")
    patterns_found: Dict[str, int] = Field(default_factory=dict)
    analysis_time: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_file(cls, agent_id: str, file_path: str, content: str) -> 'FileAnalysis':
        return cls(
            agent_id=agent_id,
            file_path=file_path,
            file_hash=hashlib.md5(content.encode()).hexdigest()[:8],
            insights=[]
        )

class LayerValidation(BaseModel):
    """Concurrent validation result for a layer"""
    layer: ArchitectureLayer
    start_time: datetime
    duration_ms: float
    files_checked: int
    issues_found: int = 0
    success: bool
    details: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        return self.success and self.issues_found == 0

class DevTeamMeeting(BaseModel):
    """Development team meeting with code analysis"""
    meeting_id: str
    feature_proposed: str
    agents: List[Agent]
    files_analyzed: int = 0
    file_analyses: List[FileAnalysis] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    action_items: Dict[str, str] = Field(default_factory=dict)
    otel_spans_created: int = 0
    transcript: List[OTelMessage] = Field(default_factory=list)
    
    def assign_action(self, agent_id: str, action: str):
        self.action_items[agent_id] = action

class ScrumTeam(BaseModel):
    """Scrum team in Scrum of Scrums"""
    team_name: str
    scrum_master: str = Field(..., description="Agent ID of scrum master")
    sprint_number: int
    completion_percent: float = Field(ge=0, le=100)
    story_points_complete: int
    story_points_total: int
    impediments: List[str] = Field(default_factory=list)
    dependencies: Dict[str, str] = Field(default_factory=dict)
    
    @property
    def status(self) -> str:
        if self.completion_percent < 40:
            return "blocked"
        elif self.completion_percent < 70:
            return "at_risk"
        return "on_track"

class QuineValidation(BaseModel):
    """Semantic quine validation results"""
    semantic_file: str
    generated_files: List[str]
    can_regenerate: bool
    regeneration_hash: Optional[str] = None
    layers_validated: int
    validation_time: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def is_valid_quine(self) -> bool:
        return self.can_regenerate and self.layers_validated == 4

class OllamaBenchmark(BaseModel):
    """LLM performance benchmark results"""
    model: str
    gpu_enabled: bool
    gpu_layers: Optional[int] = None
    tokens_generated: int
    tokens_per_second: float
    response_time_ms: float
    metal_active: Optional[bool] = None
    test_prompts: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def performance_rating(self) -> str:
        if self.tokens_per_second > 100:
            return "excellent"
        elif self.tokens_per_second > 50:
            return "good"
        elif self.tokens_per_second > 20:
            return "acceptable"
        return "poor"

# Composite Models

class OTelCommunicationSession(BaseModel):
    """Complete OTel-based communication session"""
    session_id: str
    meeting: EnhancedMeeting
    agents: List[Agent]
    messages: List[OTelMessage] = Field(default_factory=list)
    motions: List[OTelMotion] = Field(default_factory=list)
    total_spans: int = 0
    
    def add_message(self, message: OTelMessage):
        self.messages.append(message)
        self.total_spans += 1
        
        # Track motions
        if message.message_type == MessageType.MOTION:
            motion = OTelMotion(
                id=f"motion_{len(self.motions)}",
                trace_id=message.trace_id,
                proposer_span_id=message.span_id,
                text=message.content,
                motion_type="main"  # Would be extracted from metadata
            )
            self.motions.append(motion)

class CompleteSystemValidation(BaseModel):
    """Full system validation including all components"""
    validation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    layer_validations: List[LayerValidation]
    quine_validation: QuineValidation
    dev_meeting: DevTeamMeeting
    benchmarks: List[OllamaBenchmark] = Field(default_factory=list)
    total_duration_seconds: float
    
    @property
    def all_valid(self) -> bool:
        return (
            all(lv.is_valid for lv in self.layer_validations) and
            self.quine_validation.is_valid_quine
        )
    
    def summary(self) -> Dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "all_valid": self.all_valid,
            "layers_checked": len(self.layer_validations),
            "quine_valid": self.quine_validation.is_valid_quine,
            "decisions_made": len(self.dev_meeting.decisions),
            "duration_seconds": self.total_duration_seconds
        }
