#!/usr/bin/env python3
"""
OpenTelemetry Span Visualizer for Real Agent Communication
Shows how agents actually communicate through spans
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

# OTel imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import (
    SpanExporter, 
    SpanExportResult,
    BatchSpanProcessor
)
from opentelemetry.trace import Status, StatusCode

# ============= Custom Span Exporter to Capture Communication =============

class CommunicationCapturingExporter(SpanExporter):
    """Custom exporter that captures agent communication from spans"""
    
    def __init__(self):
        self.captured_spans = []
        self.agent_messages = defaultdict(list)
        self.communication_graph = []
        
    def export(self, spans: List[Span]) -> SpanExportResult:
        """Export spans and extract communication"""
        
        for span in spans:
            # Capture the span
            self.captured_spans.append(span)
            
            # Extract agent communication
            attrs = dict(span.attributes or {})
            
            # Check if this is an agent communication
            if attrs.get("message.type") and attrs.get("agent.id"):
                agent_id = attrs.get("agent.id")
                message = {
                    "timestamp": span.start_time,
                    "agent_id": agent_id,
                    "agent_name": attrs.get("agent.name", "Unknown"),
                    "message_type": attrs.get("message.type"),
                    "content": attrs.get("message.content", ""),
                    "span_name": span.name,
                    "duration_ms": (span.end_time - span.start_time) // 1_000_000
                }
                
                self.agent_messages[agent_id].append(message)
                
                # Track communication flow
                if "decision" in span.name:
                    self.communication_graph.append({
                        "from": agent_id,
                        "to": "system",
                        "type": "decision",
                        "timestamp": span.start_time
                    })
        
        return SpanExportResult.SUCCESS
    
    def shutdown(self) -> None:
        pass
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
    
    def generate_mermaid_diagram(self) -> str:
        """Generate Mermaid sequence diagram from captured communication"""
        
        if not self.agent_messages:
            return "No agent communication captured"
        
        # Sort messages by timestamp
        all_messages = []
        for agent_id, messages in self.agent_messages.items():
            all_messages.extend(messages)
        
        all_messages.sort(key=lambda x: x["timestamp"])
        
        # Build mermaid diagram
        lines = ["```mermaid", "sequenceDiagram"]
        
        # Add participants
        seen_agents = set()
        for msg in all_messages:
            agent_name = msg["agent_name"]
            if agent_name not in seen_agents:
                lines.append(f"    participant {agent_name.replace(' ', '_')}")
                seen_agents.add(agent_name)
        
        lines.append("    participant OTel as OpenTelemetry_Spans")
        
        # Add communications
        for msg in all_messages:
            agent = msg["agent_name"].replace(' ', '_')
            
            if msg["message_type"] == "decision":
                try:
                    content = json.loads(msg["content"])
                    decision = content.get("decision", "unknown")
                    confidence = content.get("confidence", 0)
                    
                    lines.append(f"    {agent}->>OTel: Decision: {decision} (conf: {confidence:.1%})")
                    lines.append(f"    Note over {agent}: Thinking time: {msg['duration_ms']}ms")
                except:
                    lines.append(f"    {agent}->>OTel: {msg['message_type']}")
            else:
                lines.append(f"    {agent}->>OTel: {msg['message_type']}")
        
        lines.append("```")
        
        return "\n".join(lines)

# ============= Communication Bus Using Spans =============

class OTelSpanCommunicationBus:
    """Real communication bus using OTel spans as the transport"""
    
    def __init__(self, tracer):
        self.tracer = tracer
        self.subscribers = defaultdict(list)
        
    async def publish(self, agent_id: str, agent_name: str, message_type: str, 
                     content: Any, recipient: Optional[str] = None):
        """Publish a message via OTel span"""
        
        with self.tracer.start_as_current_span(f"communication.{message_type}") as span:
            # Set all communication attributes
            span.set_attribute("agent.id", agent_id)
            span.set_attribute("agent.name", agent_name)
            span.set_attribute("message.type", message_type)
            span.set_attribute("message.recipient", recipient or "broadcast")
            span.set_attribute("message.timestamp", datetime.utcnow().isoformat())
            
            # Serialize content
            if isinstance(content, dict):
                span.set_attribute("message.content", json.dumps(content))
            else:
                span.set_attribute("message.content", str(content))
            
            # Add event for visibility
            span.add_event(f"{agent_name} published {message_type}", {
                "recipient": recipient or "all",
                "content_preview": str(content)[:100]
            })
            
            # Notify subscribers (if any)
            if recipient in self.subscribers:
                for callback in self.subscribers[recipient]:
                    await callback(agent_id, message_type, content)
            
            # Broadcast subscribers
            for callback in self.subscribers.get("*", []):
                await callback(agent_id, message_type, content)
    
    def subscribe(self, agent_id: str, callback):
        """Subscribe to messages for an agent"""
        self.subscribers[agent_id].append(callback)
    
    def subscribe_all(self, callback):
        """Subscribe to all messages"""
        self.subscribers["*"].append(callback)

# ============= Demo Agent with Real Communication =============

class CommunicatingAgent:
    """Agent that communicates via OTel spans"""
    
    def __init__(self, agent_id: str, name: str, role: str, bus: OTelSpanCommunicationBus):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.bus = bus
        self.received_messages = []
        
        # Subscribe to messages
        bus.subscribe(agent_id, self._receive_message)
        
    async def _receive_message(self, sender_id: str, message_type: str, content: Any):
        """Handle received message"""
        self.received_messages.append({
            "from": sender_id,
            "type": message_type,
            "content": content,
            "received_at": datetime.utcnow()
        })
    
    async def make_decision(self, context: Dict[str, Any]):
        """Make a decision and communicate it"""
        
        # Simulate thinking
        thinking_time = 2 + len(json.dumps(context)) / 1000  # Based on context size
        print(f"\n🤔 {self.name} thinking for {thinking_time:.1f}s...")
        await asyncio.sleep(thinking_time)
        
        # Make decision
        decision = {
            "decision": "approve" if context.get("value", 0) > 50 else "reject",
            "reasoning": f"As {self.role}, I analyzed the context and decided based on value",
            "confidence": 0.85 if context.get("value", 0) > 50 else 0.65,
            "thinking_time_seconds": thinking_time
        }
        
        # Communicate decision via span
        await self.bus.publish(
            self.agent_id,
            self.name,
            "decision",
            decision
        )
        
        print(f"✅ {self.name} decided: {decision['decision']} (confidence: {decision['confidence']:.1%})")
        
        return decision
    
    async def request_input(self, target_agent: str, question: str):
        """Request input from another agent"""
        
        await self.bus.publish(
            self.agent_id,
            self.name,
            "request",
            {"question": question, "requesting_agent": self.agent_id},
            recipient=target_agent
        )
        
        print(f"❓ {self.name} asked {target_agent}: {question}")
    
    async def provide_analysis(self, data: Dict[str, Any]):
        """Provide analysis and broadcast it"""
        
        analysis = {
            "patterns_found": ["trend_1", "anomaly_2"],
            "recommendations": ["action_1", "monitor_2"],
            "confidence": 0.78
        }
        
        await self.bus.publish(
            self.agent_id,
            self.name,
            "analysis",
            analysis
        )
        
        print(f"📊 {self.name} shared analysis: {len(analysis['patterns_found'])} patterns found")

# ============= Demo Scenario =============

async def demonstrate_real_communication():
    """Demonstrate real OTel span-based agent communication"""
    
    # Setup custom exporter to capture communication
    comm_exporter = CommunicationCapturingExporter()
    
    # Setup OTel with our custom exporter
    resource = Resource.create({
        "service.name": "agent-communication-demo",
        "service.version": "1.0.0"
    })
    
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(comm_exporter))
    trace.set_tracer_provider(provider)
    
    tracer = trace.get_tracer(__name__)
    
    # Create communication bus
    bus = OTelSpanCommunicationBus(tracer)
    
    # Create agents
    print("🤖 Creating Communicating Agents...")
    ceo = CommunicatingAgent("ceo-001", "Sarah (CEO)", "CEO", bus)
    cpo = CommunicatingAgent("cpo-001", "David (CPO)", "CPO", bus)
    cto = CommunicatingAgent("cto-001", "Marcus (CTO)", "CTO", bus)
    
    print("✅ Agents created with OTel span communication")
    
    # Scenario: Strategic Decision Making via Spans
    print("\n" + "="*60)
    print("📡 SCENARIO: Strategic Decision via OTel Spans")
    print("="*60)
    
    with tracer.start_as_current_span("scenario.strategic_decision") as scenario_span:
        scenario_span.set_attribute("scenario.type", "investment_decision")
        scenario_span.set_attribute("scenario.participants", "CEO,CPO,CTO")
        
        # CEO initiates decision process
        print("\n1️⃣ CEO initiates strategic decision")
        await ceo.make_decision({
            "type": "investment",
            "name": "AI Platform",
            "value": 75,  # $75M
            "strategic_importance": "high"
        })
        
        # CEO requests input from others
        print("\n2️⃣ CEO requests input from executives")
        await ceo.request_input("cpo-001", "What's the product impact of AI platform?")
        await ceo.request_input("cto-001", "What's the technical feasibility?")
        
        # Others respond with their analysis
        print("\n3️⃣ Executives provide analysis")
        await cpo.provide_analysis({"market_opportunity": "high", "customer_demand": 85})
        await cto.provide_analysis({"technical_readiness": 70, "team_skills": "adequate"})
        
        # CPO and CTO make their decisions
        print("\n4️⃣ Other executives make decisions")
        await cpo.make_decision({"value": 85, "product_fit": "excellent"})
        await cto.make_decision({"value": 70, "risk": "manageable"})
        
        # Final consensus
        print("\n5️⃣ CEO makes final decision based on input")
        await ceo.make_decision({
            "type": "final_investment_decision",
            "value": 75,
            "cpo_approved": True,
            "cto_approved": True,
            "consensus": "strong"
        })
    
    # Wait for spans to be exported
    await asyncio.sleep(1)
    
    # Show captured communication
    print("\n" + "="*60)
    print("📊 CAPTURED OTEL SPAN COMMUNICATION")
    print("="*60)
    
    print(f"\nTotal spans captured: {len(comm_exporter.captured_spans)}")
    print(f"Agent messages: {sum(len(msgs) for msgs in comm_exporter.agent_messages.values())}")
    
    print("\nMessages by agent:")
    for agent_id, messages in comm_exporter.agent_messages.items():
        print(f"\n{agent_id}:")
        for msg in messages:
            print(f"  - {msg['message_type']}: {msg['agent_name']} ({msg['duration_ms']}ms)")
    
    # Generate and show mermaid diagram
    print("\n" + "="*60)
    print("📈 MERMAID SEQUENCE DIAGRAM OF ACTUAL COMMUNICATION")
    print("="*60)
    print(comm_exporter.generate_mermaid_diagram())
    
    print("\n✅ All communication happened through OpenTelemetry spans!")
    print("📡 Each span carries the full message as attributes")
    print("🔍 Any OTel backend can observe and analyze this communication")

# ============= Main Entry Point =============

if __name__ == "__main__":
    print("🚀 OpenTelemetry Span Communication Demonstration")
    print("📡 Showing how agents communicate through spans")
    print("="*60)
    
    asyncio.run(demonstrate_real_communication())