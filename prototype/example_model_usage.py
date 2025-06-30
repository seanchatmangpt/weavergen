#!/usr/bin/env python3
"""
Example usage of the complete Pydantic models
Shows how to use them for Roberts Rules + OTel communication
"""

from complete_pydantic_models import *
from datetime import datetime

# Create agents
agents = [
    Agent(
        id="agent-sarah-chen-001",
        name="Sarah Chen",
        role="chair",
        expertise=["architecture", "leadership"]
    ),
    Agent(
        id="agent-mike-johnson-002",
        name="Mike Johnson",
        role="backend_dev",
        expertise=["operations", "runtime"]
    )
]

# Create OTel-based meeting
meeting = EnhancedMeeting(
    meeting_id="meeting-2024-12-refactor",
    meeting_type=MeetingType.DEVELOPMENT,
    trace_context={"trace_id": "abc123", "span_id": "def456"},
    chair_agent_id=agents[0].id,
    secretary_agent_id="agent-secretary",
    members_present=[a.id for a in agents],
    quorum=2
)

# Send message through OTel
message = OTelMessage(
    message_id="msg-001",
    sender=agents[1].id,
    recipient="all",
    message_type=MessageType.MOTION,
    content="I move that we refactor using the complete Pydantic models",
    trace_id=meeting.trace_context["trace_id"],
    span_id="span-001"
)

# Track motion with OTel
motion = OTelMotion(
    id="motion-refactor",
    trace_id=message.trace_id,
    proposer_span_id=message.span_id,
    text=message.content,
    motion_type="main"
)

# File analysis by agent
analysis = FileAnalysis(
    agent_id=agents[0].id,
    file_path="weaver-forge-complete.yaml",
    file_hash="abc12345",
    insights=[
        "Comprehensive semantic conventions",
        "10 distinct model groups",
        "Full OTel integration"
    ],
    patterns_found={"attributes": 89, "groups": 10}
)

# Layer validation
validation = LayerValidation(
    layer=ArchitectureLayer.COMMANDS,
    start_time=datetime.utcnow(),
    duration_ms=15.3,
    files_checked=12,
    success=True
)

# Complete session
session = OTelCommunicationSession(
    session_id="session-001",
    meeting=meeting,
    agents=agents
)
session.add_message(message)

print(f"Meeting has quorum: {meeting.has_quorum}")
print(f"Motion tracked: {motion.id}")
print(f"Analysis insights: {len(analysis.insights)}")
print(f"Layer valid: {validation.is_valid}")
print(f"Session spans: {session.total_spans}")
