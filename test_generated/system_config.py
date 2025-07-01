"""
Generated system configuration from semantic conventions
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class GeneratedSystemConfig:
    """Configuration for the generated system"""
    llm_model: str = "qwen3:latest"
    otel_service_name: str = "generated_weaver_system"
    default_conversation_duration: int = 10
    max_agents: int = 10
    enable_structured_output: bool = True
    enable_otel_tracing: bool = True
    output_directory: str = "generated_outputs"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "llm_model": self.llm_model,
            "otel_service_name": self.otel_service_name,
            "default_conversation_duration": self.default_conversation_duration,
            "max_agents": self.max_agents,
            "enable_structured_output": self.enable_structured_output,
            "enable_otel_tracing": self.enable_otel_tracing,
            "output_directory": self.output_directory
        }

# Default configuration
default_config = GeneratedSystemConfig()
