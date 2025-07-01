"""
Generated System Integration from semantic conventions
Generated at: 2025-06-30T16:08:14.656299
"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

# Import all generated components
from .models.generated_models import ConversationConfig, ConversationResult
from .agents.generated_agent_system import GeneratedAgentSystem
from .conversations.generated_conversation_system import GeneratedConversationOrchestrator
from .otel.generated_instrumentation import generated_instrumentation

def run_generated_system(mode: str = "conversation", topic: str = "System Discussion", agents: int = 3) -> Dict[str, Any]:
    """Run the complete generated system"""
    
    try:
        if mode == "conversation":
            config = ConversationConfig(
                topic=topic,
                participant_count=agents,
                mode="structured",
                duration_minutes=5,
                output_format="otel",
                structured_output=True,
                otel_tracing=True
            )
            
            orchestrator = GeneratedConversationOrchestrator(config)
            result = asyncio.run(orchestrator.run_conversation())
            
            return {
                "success": result.success,
                "mode": mode,
                "messages": result.message_count,
                "spans": result.spans_created,
                "decisions": result.decisions_count,
                "error": result.error
            }
        
        elif mode == "communication":
            from .agents.generated_agent_system import run_generated_communication
            result = asyncio.run(run_generated_communication(agents, "otel"))
            
            return {
                "success": result.success,
                "mode": mode,
                "interactions": result.interactions,
                "spans": result.spans_created,
                "error": result.error
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown mode: {mode}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
