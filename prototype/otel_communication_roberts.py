#!/usr/bin/env python3
"""
Roberts Rules implementation where agents communicate entirely through OpenTelemetry.
Each message is a span, votes are attributes, and the trace forms the meeting record.
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# OpenTelemetry imports
from opentelemetry import trace, context
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode, Link
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

# Import Roberts Rules
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'output'))

from roberts_integrated_operations import install_integrated_operations
install_integrated_operations()

from output.roberts.commands.forge import (
    roberts_meeting_start,
    roberts_motion_make,
    roberts_motion_second,
    roberts_vote_record,
    roberts_recognition_request
)

class MessageType(Enum):
    """Types of messages agents can send via OTel"""
    STATEMENT = "statement"
    MOTION = "motion"
    SECOND = "second"
    VOTE = "vote"
    POINT_OF_ORDER = "point_of_order"
    REQUEST_RECOGNITION = "request_recognition"
    GRANT_RECOGNITION = "grant_recognition"
    REPORT = "report"

@dataclass
class OTelMessage:
    """Message sent through OpenTelemetry span"""
    sender: str
    recipient: str  # "all" for broadcast
    message_type: MessageType
    content: str
    metadata: Dict[str, Any]

class OTelCommunicationBus:
    """Communication bus using OpenTelemetry as the transport layer"""
    
    def __init__(self):
        self.spans_by_agent: Dict[str, List[Span]] = {}
        self.active_motions: Dict[str, Dict[str, Any]] = {}
        self.meeting_context = None
        self.message_queue: List[OTelMessage] = []
        
    def register_agent(self, agent_name: str):
        """Register an agent to the communication bus"""
        self.spans_by_agent[agent_name] = []
    
    def get_messages_for_agent(self, agent_name: str, since_span_id: Optional[str] = None) -> List[OTelMessage]:
        """Retrieve messages for an agent from OTel spans"""
        messages = []
        
        # Check all spans for messages to this agent
        for sender, spans in self.spans_by_agent.items():
            for span in spans:
                if hasattr(span, '_attributes'):
                    attrs = span._attributes
                    
                    # Check if message is for this agent or broadcast
                    recipient = attrs.get('message.recipient', '')
                    if recipient == agent_name or recipient == 'all':
                        msg = OTelMessage(
                            sender=attrs.get('agent.name', sender),
                            recipient=recipient,
                            message_type=MessageType(attrs.get('message.type', 'statement')),
                            content=attrs.get('message.content', ''),
                            metadata={
                                'span_id': f"{span.context.span_id:016x}",
                                'trace_id': f"{span.context.trace_id:032x}",
                                'timestamp': span.start_time
                            }
                        )
                        messages.append(msg)
        
        return messages

class OTelAgent:
    """Agent that communicates entirely through OpenTelemetry"""
    
    def __init__(self, name: str, role: str, bus: OTelCommunicationBus):
        self.name = name
        self.role = role
        self.bus = bus
        self.tracer = trace.get_tracer(f"agent.{name}")
        self.current_span = None
        self.bus.register_agent(name)
        
    async def send_message(self, recipient: str, message_type: MessageType, content: str, **metadata):
        """Send a message through OpenTelemetry span"""
        with self.tracer.start_as_current_span(f"{self.name}.{message_type.value}") as span:
            # Set all message data as span attributes
            span.set_attribute("agent.name", self.name)
            span.set_attribute("agent.role", self.role)
            span.set_attribute("message.recipient", recipient)
            span.set_attribute("message.type", message_type.value)
            span.set_attribute("message.content", content)
            span.set_attribute("message.timestamp", time.time())
            
            # Add any additional metadata
            for key, value in metadata.items():
                span.set_attribute(f"message.metadata.{key}", str(value))
            
            # Store span for message retrieval
            self.bus.spans_by_agent[self.name].append(span)
            
            # If this is a motion, track it
            if message_type == MessageType.MOTION:
                motion_id = metadata.get('motion_id', f"motion_{time.time()}")
                self.bus.active_motions[motion_id] = {
                    'proposer': self.name,
                    'text': content,
                    'seconded': False,
                    'seconds': [],
                    'votes': {}
                }
                span.set_attribute("motion.id", motion_id)
            
            # Link to parent meeting span if exists
            if self.bus.meeting_context:
                span.add_link(self.bus.meeting_context)
            
            return span
    
    async def receive_messages(self) -> List[OTelMessage]:
        """Receive messages from OTel spans"""
        return self.bus.get_messages_for_agent(self.name)
    
    async def vote(self, motion_id: str, vote: str):
        """Cast a vote through OTel"""
        await self.send_message(
            "all",
            MessageType.VOTE,
            f"Vote: {vote}",
            motion_id=motion_id,
            vote=vote
        )
        
        # Record vote in bus
        if motion_id in self.bus.active_motions:
            self.bus.active_motions[motion_id]['votes'][self.name] = vote

class ChairAgent(OTelAgent):
    """Chairperson agent with special parliamentary powers"""
    
    def __init__(self, name: str, bus: OTelCommunicationBus):
        super().__init__(name, "chair", bus)
        self.recognition_queue = []
        
    async def call_to_order(self):
        """Start the meeting"""
        with self.tracer.start_as_current_span("meeting.call_to_order") as span:
            self.bus.meeting_context = span.context
            
            # Use Roberts Rules operation
            result = roberts_meeting_start(
                roberts_meeting_id=f"otel-meeting-{int(time.time())}",
                roberts_meeting_type="development",
                roberts_meeting_quorum=3,
                roberts_meeting_members_present=5,
                roberts_meeting_chair=self.name,
                roberts_meeting_secretary="OTel Recorder"
            )
            
            span.set_attribute("meeting.started", result.success)
            
            await self.send_message(
                "all",
                MessageType.STATEMENT,
                "I call this meeting to order. We have quorum with 5 members present."
            )
    
    async def recognize_speaker(self, agent_name: str):
        """Grant recognition to speak"""
        await self.send_message(
            agent_name,
            MessageType.GRANT_RECOGNITION,
            f"The chair recognizes {agent_name}",
            recognized=True
        )
    
    async def call_for_vote(self, motion_id: str):
        """Call for a vote on a motion"""
        motion = self.bus.active_motions.get(motion_id)
        if motion:
            await self.send_message(
                "all",
                MessageType.STATEMENT,
                f"We will now vote on the motion: {motion['text']}. All in favor say Aye.",
                motion_id=motion_id,
                voting_open=True
            )

async def run_otel_roberts_meeting():
    """Run a complete Roberts Rules meeting using OTel as communication"""
    
    # Setup OTel with in-memory export
    resource = Resource.create({
        "service.name": "roberts-rules-otel-communication",
        "meeting.type": "feature_planning"
    })
    
    provider = TracerProvider(resource=resource)
    
    # Console export for visualization
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(console_exporter))
    
    trace.set_tracer_provider(provider)
    
    # Create communication bus
    bus = OTelCommunicationBus()
    
    # Create agents
    chair = ChairAgent("Sarah Chen", bus)
    agents = [
        OTelAgent("Mike Johnson", "backend_dev", bus),
        OTelAgent("Emily Davis", "qa_engineer", bus),
        OTelAgent("Alex Kumar", "devops", bus),
        OTelAgent("Lisa Wong", "frontend_dev", bus)
    ]
    
    # Start meeting
    await chair.call_to_order()
    await asyncio.sleep(0.1)
    
    # Team reports via OTel
    for agent in agents:
        await agent.send_message(
            "all",
            MessageType.REPORT,
            f"{agent.name} reporting: System analysis complete, ready for feature discussion",
            report_type="status"
        )
        await asyncio.sleep(0.05)
    
    # Main motion through OTel
    mike = agents[0]
    await mike.send_message(
        "all",
        MessageType.MOTION,
        "I move that we implement OTel-based agent communication for distributed Roberts Rules",
        motion_id="motion_otel_comm",
        motion_type="main"
    )
    
    # Second the motion
    emily = agents[1]
    await emily.send_message(
        "all",
        MessageType.SECOND,
        "I second the motion",
        motion_id="motion_otel_comm"
    )
    
    # Discussion
    alex = agents[2]
    await alex.send_message(
        "all",
        MessageType.STATEMENT,
        "This will enable distributed parliamentary procedures across microservices",
        discussion=True
    )
    
    # Call for vote
    await chair.call_for_vote("motion_otel_comm")
    
    # Agents vote through OTel
    for agent in agents:
        await agent.vote("motion_otel_comm", "aye")
        await asyncio.sleep(0.05)
    
    # Chair votes
    await chair.vote("motion_otel_comm", "aye")
    
    # Announce results
    motion = bus.active_motions["motion_otel_comm"]
    ayes = sum(1 for v in motion['votes'].values() if v == 'aye')
    
    await chair.send_message(
        "all",
        MessageType.STATEMENT,
        f"The ayes have it {ayes}-0. The motion passes unanimously.",
        motion_id="motion_otel_comm",
        result="passed"
    )
    
    # Adjourn
    lisa = agents[3]
    await lisa.send_message(
        "all",
        MessageType.MOTION,
        "I move to adjourn",
        motion_id="motion_adjourn",
        motion_type="privileged"
    )
    
    await alex.send_message(
        "all",
        MessageType.SECOND,
        "Second",
        motion_id="motion_adjourn"
    )
    
    await chair.send_message(
        "all",
        MessageType.STATEMENT,
        "Meeting adjourned. All communication successfully conducted through OpenTelemetry.",
        meeting_end=True
    )
    
    return bus

def generate_otel_communication_mermaid(bus: OTelCommunicationBus):
    """Generate Mermaid diagram of OTel-based communication"""
    
    # Communication flow through OTel spans
    otel_flow = """```mermaid
sequenceDiagram
    participant OTel as OpenTelemetry Bus
    participant Sarah as Sarah Chen<br/>(Chair)
    participant Mike as Mike Johnson
    participant Emily as Emily Davis
    participant Alex as Alex Kumar
    participant Lisa as Lisa Wong

    Note over OTel: All Communication via Spans & Attributes
    
    Sarah->>OTel: span: meeting.call_to_order<br/>attr: message.content="Call to order"
    OTel-->>All: Broadcast: Meeting Started
    
    Mike->>OTel: span: Mike.report<br/>attr: message.type="report"
    Emily->>OTel: span: Emily.report<br/>attr: message.type="report"
    Alex->>OTel: span: Alex.report<br/>attr: message.type="report"
    Lisa->>OTel: span: Lisa.report<br/>attr: message.type="report"
    
    Note over OTel: Motion Phase
    Mike->>OTel: span: Mike.motion<br/>attr: motion.id="motion_otel_comm"<br/>attr: message.content="Implement OTel communication"
    OTel-->>All: New Motion Available
    
    Emily->>OTel: span: Emily.second<br/>attr: motion.id="motion_otel_comm"
    OTel-->>All: Motion Seconded
    
    Alex->>OTel: span: Alex.statement<br/>attr: message.content="Enables distributed parliament"
    
    Note over OTel: Voting Phase
    Sarah->>OTel: span: Sarah.statement<br/>attr: voting_open=true
    
    Mike->>OTel: span: Mike.vote<br/>attr: vote="aye"
    Emily->>OTel: span: Emily.vote<br/>attr: vote="aye"
    Alex->>OTel: span: Alex.vote<br/>attr: vote="aye"
    Lisa->>OTel: span: Lisa.vote<br/>attr: vote="aye"
    Sarah->>OTel: span: Sarah.vote<br/>attr: vote="aye"
    
    Sarah->>OTel: span: Sarah.statement<br/>attr: result="passed"<br/>attr: message.content="Motion passes 5-0"
    
    Lisa->>OTel: span: Lisa.motion<br/>attr: motion.id="motion_adjourn"
    Alex->>OTel: span: Alex.second<br/>attr: motion.id="motion_adjourn"
    Sarah->>OTel: span: Sarah.statement<br/>attr: meeting_end=true
```"""

    # OTel span hierarchy
    span_hierarchy = """```mermaid
graph TD
    subgraph "OpenTelemetry Trace Structure"
        Meeting[meeting.call_to_order<br/>trace_id: abc123]
        
        Meeting --> Reports[Agent Reports]
        Reports --> R1[Mike.report<br/>span_id: 001]
        Reports --> R2[Emily.report<br/>span_id: 002]
        Reports --> R3[Alex.report<br/>span_id: 003]
        Reports --> R4[Lisa.report<br/>span_id: 004]
        
        Meeting --> Motion[Motion Phase]
        Motion --> M1[Mike.motion<br/>motion.id: motion_otel_comm]
        Motion --> M2[Emily.second<br/>links_to: M1]
        Motion --> M3[Alex.statement<br/>discussion: true]
        
        Meeting --> Voting[Voting Phase]
        Voting --> V1[Mike.vote<br/>vote: aye]
        Voting --> V2[Emily.vote<br/>vote: aye]
        Voting --> V3[Alex.vote<br/>vote: aye]
        Voting --> V4[Lisa.vote<br/>vote: aye]
        Voting --> V5[Sarah.vote<br/>vote: aye]
        
        Meeting --> Adjourn[Adjournment]
        Adjourn --> A1[Lisa.motion<br/>motion_type: privileged]
        Adjourn --> A2[Alex.second]
        Adjourn --> A3[Sarah.statement<br/>meeting_end: true]
    end
    
    style Meeting fill:#4CAF50
    style M1 fill:#90EE90
    style Voting fill:#87CEEB
```"""

    # Message attributes schema
    attribute_schema = """```mermaid
graph LR
    subgraph "OTel Message Attributes Schema"
        Core[Core Attributes]
        Core --> C1[agent.name: string]
        Core --> C2[agent.role: string]
        Core --> C3[message.recipient: string]
        Core --> C4[message.type: enum]
        Core --> C5[message.content: string]
        Core --> C6[message.timestamp: float]
        
        Motion[Motion Attributes]
        Motion --> M1[motion.id: string]
        Motion --> M2[motion.type: string]
        Motion --> M3[motion.text: string]
        
        Vote[Vote Attributes]
        Vote --> V1[vote: string]
        Vote --> V2[motion.id: string]
        
        Meeting[Meeting Attributes]
        Meeting --> ME1[meeting.started: bool]
        Meeting --> ME2[voting_open: bool]
        Meeting --> ME3[meeting_end: bool]
        Meeting --> ME4[result: string]
    end
```"""

    # Communication patterns
    patterns = """```mermaid
graph TB
    subgraph "OTel Communication Patterns"
        Broadcast["Broadcast Message<br/>recipient: 'all'"]
        Direct["Direct Message<br/>recipient: agent_name"]
        Motion["Motion Submission<br/>type: MOTION + motion.id"]
        Vote["Vote Casting<br/>type: VOTE + vote value"]
        
        Broadcast --> B1[Meeting announcements]
        Broadcast --> B2[Motion proposals]
        Broadcast --> B3[Vote results]
        
        Direct --> D1[Recognition grants]
        Direct --> D2[Point of order]
        
        Motion --> M1[Creates span with motion.id]
        Motion --> M2[Links seconding spans]
        Motion --> M3[Tracks in active_motions]
        
        Vote --> V1[Span per vote]
        Vote --> V2[Aggregated by motion.id]
        Vote --> V3[Results calculated]
    end
    
    style Broadcast fill:#90EE90
    style Motion fill:#FFE4B5
    style Vote fill:#87CEEB
```"""

    print(otel_flow)
    print()
    print(span_hierarchy)
    print()
    print(attribute_schema)
    print()
    print(patterns)

async def main():
    """Run the OTel-based Roberts Rules meeting"""
    
    print("🚀 Roberts Rules Meeting via OpenTelemetry Communication")
    print("=" * 60)
    print("All agent communication happens through OTel spans and attributes")
    print("=" * 60)
    
    # Run the meeting
    bus = await run_otel_roberts_meeting()
    
    # Generate visualizations
    print("\n📊 OTel Communication Patterns:")
    print("=" * 60)
    generate_otel_communication_mermaid(bus)
    
    # Summary of messages sent
    total_spans = sum(len(spans) for spans in bus.spans_by_agent.values())
    print(f"\n✅ Meeting Complete!")
    print(f"   Total OTel spans created: {total_spans}")
    print(f"   Active motions tracked: {len(bus.active_motions)}")
    print(f"   All communication through OpenTelemetry!")

if __name__ == "__main__":
    asyncio.run(main())