"""
Generated conversation models from semantic conventions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ConversationTurn(BaseModel):
    """A single turn in a conversation"""
    turn_id: str = Field(..., description="Unique turn identifier")
    participant_id: str = Field(..., description="Participant who made this turn")
    content: str = Field(..., description="Turn content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    structured_data: Optional[Dict[str, Any]] = Field(None)
    span_id: str = Field(..., description="Associated OTel span ID")

class ConversationState(BaseModel):
    """State of an ongoing conversation"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    current_round: int = Field(0, description="Current conversation round")
    active_participants: List[str] = Field(default_factory=list)
    turns: List[ConversationTurn] = Field(default_factory=list)
    decisions_made: List[Dict[str, Any]] = Field(default_factory=list)
    consensus_level: float = Field(0.0, ge=0.0, le=1.0)
