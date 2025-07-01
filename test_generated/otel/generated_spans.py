"""
Generated OpenTelemetry span utilities from semantic conventions
"""

import json
from typing import Dict, Any, Optional, List
from opentelemetry import trace
from datetime import datetime

class GeneratedSpanUtils:
    """Generated utilities for working with OTel spans"""
    
    @staticmethod
    def add_structured_attributes(span, data: Dict[str, Any], prefix: str = ""):
        """Add structured data as span attributes"""
        for key, value in data.items():
            attr_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, (str, int, float, bool)):
                span.set_attribute(attr_key, value)
            elif isinstance(value, (dict, list)):
                span.set_attribute(attr_key, json.dumps(value))
            else:
                span.set_attribute(attr_key, str(value))
    
    @staticmethod
    def create_conversation_span(tracer, conversation_id: str, topic: str):
        """Create a span for conversation tracking"""
        span = tracer.start_span("generated.conversation")
        span.set_attribute("conversation.id", conversation_id)
        span.set_attribute("conversation.topic", topic)
        span.set_attribute("conversation.generated", True)
        span.set_attribute("conversation.timestamp", datetime.now().isoformat())
        return span
    
    @staticmethod
    def create_agent_span(tracer, agent_id: str, role: str, operation: str):
        """Create a span for agent operations"""
        span = tracer.start_span(f"generated.agent.{operation}")
        span.set_attribute("agent.id", agent_id)
        span.set_attribute("agent.role", role)
        span.set_attribute("agent.operation", operation)
        span.set_attribute("agent.generated", True)
        return span
    
    @staticmethod
    def create_decision_span(tracer, decision_id: str, decision_type: str):
        """Create a span for decision tracking"""
        span = tracer.start_span("generated.decision")
        span.set_attribute("decision.id", decision_id)
        span.set_attribute("decision.type", decision_type)
        span.set_attribute("decision.generated", True)
        span.set_attribute("decision.timestamp", datetime.now().isoformat())
        return span
