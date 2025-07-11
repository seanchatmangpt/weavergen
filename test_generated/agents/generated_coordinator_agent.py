"""
Generated Coordinator Agent from semantic conventions
"""

from typing import Dict, Any, Optional
from opentelemetry import trace

tracer = trace.get_tracer("generated_coordinator_agent")

class GeneratedCoordinatorAgent:
    """Generated coordinator agent with semantic-driven behavior"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.role = "coordinator"
        self.tracer = tracer
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message with coordinator-specific logic"""
        with self.tracer.start_span(f"coordinator_process_message") as span:
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("agent.role", self.role)
            span.set_attribute("message.content", message)
            
            # Coordinator-specific processing
            result = {
                "agent_id": self.agent_id,
                "role": self.role,
                "response": f"{role.title()} response to: {message}",
                "context_processed": len(context),
                "structured_output": True
            }
            
            span.set_attribute("result.structured", True)
            
            return result
