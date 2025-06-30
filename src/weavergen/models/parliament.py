"""Parliamentary procedure models for Roberts Rules implementation."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum, IntEnum
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class MotionType(str, Enum):
    """Types of motions in parliamentary procedure."""
    # Main motions
    MAIN = "main"
    
    # Subsidiary motions (modify or dispose of main motion)
    AMEND = "amend"
    REFER_TO_COMMITTEE = "refer_to_committee"
    POSTPONE_INDEFINITELY = "postpone_indefinitely"
    POSTPONE_TO_TIME = "postpone_to_time"
    TABLE = "table"
    PREVIOUS_QUESTION = "previous_question"
    
    # Privileged motions (urgent matters)
    ADJOURN = "adjourn"
    RECESS = "recess"
    QUESTION_OF_PRIVILEGE = "question_of_privilege"
    
    # Incidental motions (procedure questions)
    POINT_OF_ORDER = "point_of_order"
    APPEAL = "appeal"
    SUSPEND_RULES = "suspend_rules"
    WITHDRAW_MOTION = "withdraw_motion"


class MotionPrecedence(IntEnum):
    """Precedence levels for motions (higher number = higher precedence)."""
    MAIN = 1
    AMEND = 2
    REFER_TO_COMMITTEE = 3
    POSTPONE_INDEFINITELY = 4
    POSTPONE_TO_TIME = 5
    TABLE = 6
    PREVIOUS_QUESTION = 7
    QUESTION_OF_PRIVILEGE = 8
    RECESS = 9
    ADJOURN = 10


class VoteType(str, Enum):
    """Types of votes."""
    VOICE = "voice"
    DIVISION = "division"
    BALLOT = "ballot"
    ROLL_CALL = "roll_call"


class VoteThreshold(str, Enum):
    """Vote thresholds required for motions."""
    MAJORITY = "majority"           # >50%
    TWO_THIRDS = "two_thirds"       # >=66.7%
    UNANIMOUS = "unanimous"         # 100%
    CHAIR_DECISION = "chair_decision"  # Chair decides


class VoteResult(str, Enum):
    """Results of votes."""
    PASSED = "passed"
    FAILED = "failed"
    TIE = "tie"
    WITHDRAWN = "withdrawn"


class MeetingStatus(str, Enum):
    """Status of meetings."""
    NOT_STARTED = "not_started"
    IN_SESSION = "in_session"
    IN_RECESS = "in_recess"
    ADJOURNED = "adjourned"


class MeetingParticipant(BaseModel):
    """Participant in a parliamentary meeting."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    role: str = "member"  # member, chair, secretary, etc.
    present: bool = True
    can_vote: bool = True
    recognition_queue_position: Optional[int] = None
    
    class Config:
        extra = "allow"


class Motion(BaseModel):
    """A parliamentary motion."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MotionType
    proposer_id: str
    seconder_id: Optional[str] = None
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Motion state
    is_seconded: bool = False
    is_open_for_debate: bool = False
    is_voted_on: bool = False
    
    # Voting requirements
    vote_threshold: VoteThreshold = VoteThreshold.MAJORITY
    vote_type: VoteType = VoteType.VOICE
    
    # Results
    vote_result: Optional[VoteResult] = None
    yes_votes: int = 0
    no_votes: int = 0
    abstentions: int = 0
    
    # Metadata
    debate_speakers: List[str] = Field(default_factory=list)
    amendments: List["Motion"] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def precedence(self) -> int:
        """Get motion precedence level."""
        precedence_map = {
            MotionType.MAIN: MotionPrecedence.MAIN,
            MotionType.AMEND: MotionPrecedence.AMEND,
            MotionType.REFER_TO_COMMITTEE: MotionPrecedence.REFER_TO_COMMITTEE,
            MotionType.POSTPONE_INDEFINITELY: MotionPrecedence.POSTPONE_INDEFINITELY,
            MotionType.POSTPONE_TO_TIME: MotionPrecedence.POSTPONE_TO_TIME,
            MotionType.TABLE: MotionPrecedence.TABLE,
            MotionType.PREVIOUS_QUESTION: MotionPrecedence.PREVIOUS_QUESTION,
            MotionType.QUESTION_OF_PRIVILEGE: MotionPrecedence.QUESTION_OF_PRIVILEGE,
            MotionType.RECESS: MotionPrecedence.RECESS,
            MotionType.ADJOURN: MotionPrecedence.ADJOURN,
        }
        return precedence_map.get(self.type, MotionPrecedence.MAIN)
    
    @property
    def requires_second(self) -> bool:
        """Check if motion requires a second."""
        no_second_required = {
            MotionType.POINT_OF_ORDER,
            MotionType.QUESTION_OF_PRIVILEGE,
            MotionType.WITHDRAW_MOTION,
        }
        return self.type not in no_second_required
    
    @property
    def is_debatable(self) -> bool:
        """Check if motion is debatable."""
        non_debatable = {
            MotionType.TABLE,
            MotionType.PREVIOUS_QUESTION,
            MotionType.ADJOURN,
            MotionType.RECESS,
            MotionType.POINT_OF_ORDER,
        }
        return self.type not in non_debatable
    
    @property
    def is_amendable(self) -> bool:
        """Check if motion is amendable."""
        non_amendable = {
            MotionType.TABLE,
            MotionType.PREVIOUS_QUESTION,
            MotionType.ADJOURN,
            MotionType.RECESS,
            MotionType.POINT_OF_ORDER,
            MotionType.APPEAL,
            MotionType.WITHDRAW_MOTION,
        }
        return self.type not in non_amendable
    
    def calculate_vote_result(self, total_voting_members: int) -> VoteResult:
        """Calculate vote result based on threshold."""
        total_votes = self.yes_votes + self.no_votes
        
        if total_votes == 0:
            return VoteResult.FAILED
        
        if self.vote_threshold == VoteThreshold.UNANIMOUS:
            if self.no_votes == 0 and self.yes_votes > 0:
                return VoteResult.PASSED
            return VoteResult.FAILED
        
        elif self.vote_threshold == VoteThreshold.TWO_THIRDS:
            required_yes = int(total_votes * (2/3)) + (1 if total_votes * (2/3) % 1 > 0 else 0)
            if self.yes_votes >= required_yes:
                return VoteResult.PASSED
            return VoteResult.FAILED
        
        elif self.vote_threshold == VoteThreshold.MAJORITY:
            if self.yes_votes > self.no_votes:
                return VoteResult.PASSED
            elif self.yes_votes == self.no_votes:
                return VoteResult.TIE
            return VoteResult.FAILED
        
        return VoteResult.FAILED


class Vote(BaseModel):
    """Individual vote on a motion."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    motion_id: str
    voter_id: str
    vote: str  # "yes", "no", "abstain"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('vote')
    def validate_vote(cls, v):
        valid_votes = {"yes", "no", "abstain"}
        if v.lower() not in valid_votes:
            raise ValueError(f"Vote must be one of {valid_votes}")
        return v.lower()


class PointOfOrder(BaseModel):
    """Point of order raised during proceedings."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    raiser_id: str
    issue: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    chair_ruling: Optional[str] = None
    is_appealed: bool = False
    appeal_result: Optional[VoteResult] = None


class RecognitionRequest(BaseModel):
    """Request to be recognized to speak."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    requester_id: str
    purpose: str  # "speak", "motion", "point_of_order", etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    granted: bool = False
    queue_position: Optional[int] = None


class Meeting(BaseModel):
    """Parliamentary meeting."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    chair_id: str
    secretary_id: Optional[str] = None
    
    # Meeting state
    status: MeetingStatus = MeetingStatus.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Participants
    participants: List[MeetingParticipant] = Field(default_factory=list)
    quorum_required: int = 1
    
    # Parliamentary state
    current_motion: Optional[Motion] = None
    motion_stack: List[Motion] = Field(default_factory=list)
    completed_motions: List[Motion] = Field(default_factory=list)
    
    # Recognition and speaking
    floor_holder: Optional[str] = None
    recognition_queue: List[RecognitionRequest] = Field(default_factory=list)
    
    # Records
    points_of_order: List[PointOfOrder] = Field(default_factory=list)
    votes: List[Vote] = Field(default_factory=list)
    
    # Metadata
    agenda: List[str] = Field(default_factory=list)
    minutes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def has_quorum(self) -> bool:
        """Check if meeting has quorum."""
        present_count = sum(1 for p in self.participants if p.present)
        return present_count >= self.quorum_required
    
    @property
    def voting_members_count(self) -> int:
        """Count of members eligible to vote."""
        return sum(1 for p in self.participants if p.present and p.can_vote)
    
    def add_participant(self, participant: MeetingParticipant) -> None:
        """Add participant to meeting."""
        self.participants.append(participant)
    
    def get_participant(self, participant_id: str) -> Optional[MeetingParticipant]:
        """Get participant by ID."""
        return next((p for p in self.participants if p.id == participant_id), None)
    
    def is_motion_in_order(self, motion: Motion) -> bool:
        """Check if a motion is in order given current state."""
        if not self.has_quorum:
            return False
        
        if self.status != MeetingStatus.IN_SESSION:
            return False
        
        # Check motion precedence
        if self.current_motion and motion.precedence <= self.current_motion.precedence:
            # Lower precedence motions cannot interrupt higher precedence ones
            return False
        
        return True


class ParliamentaryState(BaseModel):
    """Complete state of parliamentary proceedings."""
    
    meeting: Meeting
    current_speaker: Optional[str] = None
    debate_time_remaining: Optional[int] = None  # seconds
    
    # State flags
    is_in_debate: bool = False
    is_in_voting: bool = False
    is_awaiting_second: bool = False
    
    # Statistics
    total_motions: int = 0
    total_votes: int = 0
    session_duration: Optional[int] = None  # seconds
    
    def update_statistics(self) -> None:
        """Update session statistics."""
        self.total_motions = len(self.meeting.completed_motions) + len(self.meeting.motion_stack)
        if self.meeting.current_motion:
            self.total_motions += 1
        
        self.total_votes = len(self.meeting.votes)
        
        if self.meeting.start_time:
            if self.meeting.end_time:
                duration = self.meeting.end_time - self.meeting.start_time
            else:
                duration = datetime.utcnow() - self.meeting.start_time
            self.session_duration = int(duration.total_seconds())


# Enable forward references for Motion amendments
Motion.model_rebuild()