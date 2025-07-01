"""
Generated Pydantic models from semantic conventions
Generated at: 2025-06-30T16:08:14.654447
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import hashlib

# Generated enums and models from semantic conventions

class GeneratedMessage(BaseModel):
    """Generated message model for agent communication"""
    message_id: str = Field(..., description="Unique message identifier")
    sender_id: str = Field(..., description="Agent ID of sender")
    recipient_id: str = Field(..., description="Agent ID of recipient or 'all'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trace_id: str = Field(..., description="OpenTelemetry trace ID")
    span_id: str = Field(..., description="OpenTelemetry span ID")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured data payload")

class ConversationConfig(BaseModel):
    """Configuration for generated conversations"""
    topic: str = Field(..., description="Conversation topic")
    participant_count: int = Field(..., ge=2, le=10, description="Number of participants")
    mode: str = Field(..., description="Conversation mode")
    duration_minutes: int = Field(..., ge=1, le=120, description="Duration in minutes")
    output_format: str = Field("otel", description="Output format")
    structured_output: bool = Field(True, description="Use structured outputs")
    otel_tracing: bool = Field(True, description="Enable OTel tracing")

class ConversationResult(BaseModel):
    """Result of a generated conversation"""
    success: bool = Field(..., description="Conversation success status")
    message_count: int = Field(0, description="Number of messages exchanged")
    spans_created: int = Field(0, description="Number of OTel spans created")
    decisions_count: int = Field(0, description="Number of decisions made")
    structured_outputs_count: int = Field(0, description="Number of structured outputs")
    actual_duration: float = Field(0.0, description="Actual duration in minutes")
    active_agents: int = Field(0, description="Number of active agents")
    avg_message_quality: float = Field(0.0, description="Average message quality score")
    consensus_level: float = Field(0.0, description="Consensus level achieved")
    telemetry_coverage: float = Field(0.0, description="Telemetry coverage percentage")
    otel_output_path: Optional[str] = Field(None, description="Path to OTel output")
    json_output_path: Optional[str] = Field(None, description="Path to JSON output")
    transcript_path: Optional[str] = Field(None, description="Path to transcript")
    error: Optional[str] = Field(None, description="Error message if failed")

class CommunicationResult(BaseModel):
    """Result of agent communication"""
    success: bool = Field(..., description="Communication success status")
    interactions: int = Field(0, description="Number of interactions")
    spans_created: int = Field(0, description="Number of spans created")
    error: Optional[str] = Field(None, description="Error message if failed")

# Additional models based on semantic groups

class Test_Agent(BaseModel):
    """
    Test AI agent for complete forge testing
    
    Generated from semantic convention: test.agent
    Type: span
    """
    id: str = Field(..., description="Unique identifier")
    type: str = Field(default="span", description="Entity type")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Add attributes from semantic convention
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_role: str = Field(..., description="Agent role in the system")
    agent_status: str = Field(..., description="Current agent status")


class Test_Conversation(BaseModel):
    """
    Test conversation for agent communication
    
    Generated from semantic convention: test.conversation
    Type: span
    """
    id: str = Field(..., description="Unique identifier")
    type: str = Field(default="span", description="Entity type")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Add attributes from semantic convention
    conversation_id: str = Field(..., description="Unique conversation identifier")
    conversation_topic: str = Field(..., description="Conversation topic")
    conversation_participants: int = Field(..., description="Number of participants")
    conversation_mode: str = Field(..., description="Conversation mode")


class Test_Decision(BaseModel):
    """
    Test decision making process
    
    Generated from semantic convention: test.decision
    Type: span
    """
    id: str = Field(..., description="Unique identifier")
    type: str = Field(default="span", description="Entity type")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Add attributes from semantic convention
    decision_id: str = Field(..., description="Unique decision identifier")
    decision_type: str = Field(..., description="Type of decision")
    decision_confidence: float = Field(..., description="Confidence level in the decision")
    decision_reasoning: str = Field(..., description="Reasoning behind the decision")

