#!/usr/bin/env python3
"""
Pydantic models generated from Robert's Rules of Order semantic conventions.
These models provide type-safe data structures for parliamentary procedures.
"""

from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict

# Enums for constrained values from semantic conventions

class MeetingType(str, Enum):
    """Types of meetings according to Robert's Rules"""
    BOARD = "board"
    COMMITTEE = "committee"
    GENERAL = "general"
    SPECIAL = "special"

class MotionType(str, Enum):
    """Types of motions with their precedence order"""
    MAIN = "main"  # Lowest precedence
    SUBSIDIARY = "subsidiary"  # Can be applied to main motions
    PRIVILEGED = "privileged"  # Highest precedence
    INCIDENTAL = "incidental"  # Arise incidentally

class MotionStatus(str, Enum):
    """Lifecycle states of a motion"""
    PENDING = "pending"
    SECONDED = "seconded"
    DEBATING = "debating"
    VOTING = "voting"
    PASSED = "passed"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"
    TABLED = "tabled"

class VoteThreshold(str, Enum):
    """Required vote thresholds for different motion types"""
    MAJORITY = "majority"  # More than half
    TWO_THIRDS = "two_thirds"  # 2/3 majority
    UNANIMOUS = "unanimous"  # All in favor

class VoteMethod(str, Enum):
    """Methods of conducting votes"""
    VOICE = "voice"  # Aye/Nay
    SHOW_OF_HANDS = "show_of_hands"
    ROLL_CALL = "roll_call"  # Each member's vote recorded
    BALLOT = "ballot"  # Secret ballot
    UNANIMOUS_CONSENT = "unanimous_consent"

class VoteResult(str, Enum):
    """Possible outcomes of a vote"""
    PASSED = "passed"
    FAILED = "failed"
    TIED = "tied"

class RecognitionPurpose(str, Enum):
    """Reasons for seeking recognition to speak"""
    SPEAK_FOR = "speak_for"
    SPEAK_AGAINST = "speak_against"
    ASK_QUESTION = "ask_question"
    MAKE_MOTION = "make_motion"
    POINT_OF_ORDER = "point_of_order"
    POINT_OF_INFORMATION = "point_of_information"

# Pydantic Models

class Meeting(BaseModel):
    """Represents a meeting following Robert's Rules"""
    model_config = ConfigDict(validate_assignment=True)
    
    id: str = Field(..., description="Unique identifier for the meeting")
    type: MeetingType = Field(..., description="Type of meeting being conducted")
    quorum: int = Field(..., gt=0, description="Number of members required for quorum")
    members_present: int = Field(..., ge=0, description="Current number of members present")
    chair: str = Field(..., description="Name or ID of the meeting chair")
    secretary: str = Field(..., description="Name or ID of the meeting secretary")
    agenda_items: Optional[List[str]] = Field(default=None, description="List of agenda items")
    minutes_path: Optional[str] = Field(default=None, description="Path where minutes will be saved")
    start_time: datetime = Field(default_factory=datetime.now, description="Meeting start time")
    end_time: Optional[datetime] = Field(default=None, description="Meeting end time")
    motions: List[str] = Field(default_factory=list, description="IDs of motions made during meeting")
    
    @validator('members_present')
    def validate_quorum(cls, v, values):
        """Ensure we track whether quorum is met"""
        if 'quorum' in values and v < values['quorum']:
            # Note: We don't raise an error, just track the state
            # The meeting can proceed without quorum for informational purposes
            pass
        return v
    
    @property
    def has_quorum(self) -> bool:
        """Check if the meeting has quorum"""
        return self.members_present >= self.quorum
    
    @property
    def is_active(self) -> bool:
        """Check if the meeting is currently active"""
        return self.end_time is None

class Motion(BaseModel):
    """Represents a motion in Robert's Rules"""
    model_config = ConfigDict(validate_assignment=True)
    
    id: str = Field(..., description="Unique identifier for the motion")
    type: MotionType = Field(..., description="Type of motion according to Robert's Rules")
    text: str = Field(..., min_length=1, description="The full text of the motion")
    mover: str = Field(..., description="Member who made the motion")
    seconder: Optional[str] = Field(default=None, description="Member who seconded the motion")
    requires_second: bool = Field(..., description="Whether this motion requires a second")
    debatable: bool = Field(..., description="Whether this motion is debatable")
    vote_required: VoteThreshold = Field(..., description="Vote threshold required to pass")
    status: MotionStatus = Field(default=MotionStatus.PENDING, description="Current status")
    created_at: datetime = Field(default_factory=datetime.now)
    debate_history: List[Dict[str, Any]] = Field(default_factory=list, description="Record of debate")
    amendments: List[str] = Field(default_factory=list, description="IDs of amendments to this motion")
    parent_motion: Optional[str] = Field(default=None, description="ID of motion this amends")
    
    @validator('status')
    def validate_status_transition(cls, v, values):
        """Ensure valid status transitions"""
        # If motion requires second and has no seconder, it can't progress past pending
        if values.get('requires_second') and not values.get('seconder') and v not in [MotionStatus.PENDING, MotionStatus.WITHDRAWN]:
            raise ValueError("Motion requiring second cannot progress without seconder")
        return v
    
    @property
    def can_be_debated(self) -> bool:
        """Check if motion can currently be debated"""
        return self.debatable and self.status == MotionStatus.SECONDED
    
    @property
    def is_amendment(self) -> bool:
        """Check if this is an amendment to another motion"""
        return self.parent_motion is not None
    
    def get_precedence_level(self) -> int:
        """Get precedence level for ordering (higher number = higher precedence)"""
        precedence = {
            MotionType.MAIN: 1,
            MotionType.SUBSIDIARY: 2,
            MotionType.INCIDENTAL: 3,
            MotionType.PRIVILEGED: 4
        }
        return precedence.get(self.type, 0)

class Vote(BaseModel):
    """Represents a vote on a motion"""
    model_config = ConfigDict(validate_assignment=True)
    
    motion_id: str = Field(..., description="ID of the motion being voted on")
    method: VoteMethod = Field(..., description="Method of voting")
    yes_count: int = Field(..., ge=0, description="Number of yes votes")
    no_count: int = Field(..., ge=0, description="Number of no votes")
    abstain_count: int = Field(default=0, ge=0, description="Number of abstentions")
    result: Optional[VoteResult] = Field(default=None, description="Result of the vote")
    timestamp: datetime = Field(default_factory=datetime.now)
    roll_call: Optional[Dict[str, Literal["yes", "no", "abstain"]]] = Field(
        default=None, description="Individual votes for roll call"
    )
    
    @validator('result', always=True)
    def calculate_result(cls, v, values):
        """Calculate vote result based on counts"""
        if v is not None:
            return v
        
        yes = values.get('yes_count', 0)
        no = values.get('no_count', 0)
        
        if yes > no:
            return VoteResult.PASSED
        elif no > yes:
            return VoteResult.FAILED
        else:
            return VoteResult.TIED
    
    @property
    def total_votes(self) -> int:
        """Total number of votes cast (excluding abstentions)"""
        return self.yes_count + self.no_count
    
    @property
    def participation_count(self) -> int:
        """Total participation including abstentions"""
        return self.yes_count + self.no_count + self.abstain_count
    
    def meets_threshold(self, threshold: VoteThreshold) -> bool:
        """Check if vote meets required threshold"""
        if self.total_votes == 0:
            return False
        
        if threshold == VoteThreshold.MAJORITY:
            return self.yes_count > self.no_count
        elif threshold == VoteThreshold.TWO_THIRDS:
            return self.yes_count >= (self.total_votes * 2 / 3)
        elif threshold == VoteThreshold.UNANIMOUS:
            return self.yes_count == self.total_votes and self.no_count == 0
        
        return False

class PointOfOrder(BaseModel):
    """Represents a point of order raised during proceedings"""
    model_config = ConfigDict(validate_assignment=True)
    
    member: str = Field(..., description="Member raising the point of order")
    issue: str = Field(..., description="Description of the procedural issue")
    ruling: Optional[str] = Field(default=None, description="Chair's ruling on the point")
    appealed: bool = Field(default=False, description="Whether the ruling was appealed")
    appeal_motion_id: Optional[str] = Field(default=None, description="ID of appeal motion if appealed")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('appeal_motion_id')
    def validate_appeal(cls, v, values):
        """Ensure appeal motion ID is only set when appealed"""
        if v and not values.get('appealed'):
            raise ValueError("Cannot have appeal motion ID without appeal")
        return v

class RecognitionRequest(BaseModel):
    """Represents a request for recognition to speak"""
    model_config = ConfigDict(validate_assignment=True)
    
    member: str = Field(..., description="Member seeking recognition")
    purpose: RecognitionPurpose = Field(..., description="Purpose of seeking recognition")
    granted: bool = Field(..., description="Whether recognition was granted")
    queue_position: Optional[int] = Field(default=None, ge=1, description="Position in speaking queue")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('queue_position')
    def validate_queue_position(cls, v, values):
        """Ensure queue position is only set when not immediately granted"""
        if v is not None and values.get('granted'):
            raise ValueError("Cannot have queue position when immediately granted")
        return v

class SpeakingQueue(BaseModel):
    """Manages the queue of members waiting to speak"""
    model_config = ConfigDict(validate_assignment=True)
    
    queue: List[RecognitionRequest] = Field(default_factory=list)
    current_speaker: Optional[str] = Field(default=None)
    
    def add_to_queue(self, request: RecognitionRequest) -> int:
        """Add a recognition request to queue and return position"""
        self.queue.append(request)
        position = len(self.queue)
        request.queue_position = position
        return position
    
    def next_speaker(self) -> Optional[RecognitionRequest]:
        """Get next speaker from queue"""
        if self.queue:
            next_request = self.queue.pop(0)
            self.current_speaker = next_request.member
            # Update queue positions
            for i, req in enumerate(self.queue):
                req.queue_position = i + 1
            return next_request
        return None

class ParliamentaryState(BaseModel):
    """Complete state of parliamentary proceedings"""
    model_config = ConfigDict(validate_assignment=True)
    
    current_meeting: Optional[Meeting] = Field(default=None)
    meetings: Dict[str, Meeting] = Field(default_factory=dict)
    motions: Dict[str, Motion] = Field(default_factory=dict)
    votes: List[Vote] = Field(default_factory=list)
    points_of_order: List[PointOfOrder] = Field(default_factory=list)
    speaking_queue: SpeakingQueue = Field(default_factory=SpeakingQueue)
    
    def get_active_motions(self) -> List[Motion]:
        """Get all motions currently under consideration"""
        active_statuses = {MotionStatus.PENDING, MotionStatus.SECONDED, 
                          MotionStatus.DEBATING, MotionStatus.VOTING}
        return [m for m in self.motions.values() if m.status in active_statuses]
    
    def get_motion_hierarchy(self) -> List[Motion]:
        """Get active motions ordered by precedence"""
        active = self.get_active_motions()
        return sorted(active, key=lambda m: m.get_precedence_level(), reverse=True)
    
    def can_make_motion(self, motion_type: MotionType) -> bool:
        """Check if a motion of given type can be made now"""
        hierarchy = self.get_motion_hierarchy()
        if not hierarchy:
            return True
        
        # Get precedence of highest active motion
        highest_precedence = hierarchy[0].get_precedence_level()
        
        # New motion must have equal or higher precedence
        new_precedence = Motion(
            id="temp", type=motion_type, text="", mover="",
            requires_second=True, debatable=True, 
            vote_required=VoteThreshold.MAJORITY
        ).get_precedence_level()
        
        return new_precedence >= highest_precedence

# Validation models for operations

class MeetingStartRequest(BaseModel):
    """Request to start a meeting"""
    meeting_id: str
    meeting_type: MeetingType
    quorum: int = Field(..., gt=0)
    members_present: int = Field(..., ge=0)
    chair: str
    secretary: str
    agenda_items: Optional[List[str]] = None
    minutes_path: Optional[str] = None

class MotionMakeRequest(BaseModel):
    """Request to make a motion"""
    motion_id: str
    motion_type: MotionType
    motion_text: str = Field(..., min_length=1)
    mover: str
    requires_second: bool
    debatable: bool
    vote_required: VoteThreshold

class VoteRecordRequest(BaseModel):
    """Request to record a vote"""
    motion_id: str
    vote_method: VoteMethod
    yes_count: int = Field(..., ge=0)
    no_count: int = Field(..., ge=0)
    abstain_count: int = Field(default=0, ge=0)

# Example factory functions for common scenarios

def create_main_motion(text: str, mover: str, motion_id: Optional[str] = None) -> Motion:
    """Create a standard main motion"""
    return Motion(
        id=motion_id or f"motion-{datetime.now().timestamp()}",
        type=MotionType.MAIN,
        text=text,
        mover=mover,
        requires_second=True,
        debatable=True,
        vote_required=VoteThreshold.MAJORITY
    )

def create_motion_to_adjourn(mover: str, motion_id: Optional[str] = None) -> Motion:
    """Create a privileged motion to adjourn"""
    return Motion(
        id=motion_id or f"adjourn-{datetime.now().timestamp()}",
        type=MotionType.PRIVILEGED,
        text="I move to adjourn",
        mover=mover,
        requires_second=True,
        debatable=False,  # Motion to adjourn is not debatable
        vote_required=VoteThreshold.MAJORITY
    )

def create_motion_to_table(mover: str, motion_id: Optional[str] = None) -> Motion:
    """Create a subsidiary motion to table"""
    return Motion(
        id=motion_id or f"table-{datetime.now().timestamp()}",
        type=MotionType.SUBSIDIARY,
        text="I move to table the motion",
        mover=mover,
        requires_second=True,
        debatable=False,  # Motion to table is not debatable
        vote_required=VoteThreshold.MAJORITY
    )