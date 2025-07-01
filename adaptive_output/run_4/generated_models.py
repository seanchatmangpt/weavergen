# Generated Pydantic Models

# Model: MockPydanticModels
# Generated: 2025-07-01T07:53:35.003000

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AgentInteraction(BaseModel):
    """Generated agent interaction model"""
    agent_id: str = Field(..., description="Unique agent identifier")
    role: str = Field(..., description="Agent role (coordinator, analyst, facilitator)")
    message_content: str = Field(..., description="Message content")
    structured_output: bool = Field(default=True, description="Whether output is structured")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class ValidationResult(BaseModel):
    """Generated validation result model"""
    component_id: str = Field(..., description="Component being validated")
    validation_passed: bool = Field(..., description="Whether validation passed")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score")
    issues: List[str] = Field(default_factory=list, description="Validation issues")


