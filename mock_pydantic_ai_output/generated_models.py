# Generated Pydantic Models

from pydantic import BaseModel
from typing import List

# Model: AgentInteraction
# Generated: 2025-07-01T04:01:05.008593
class AgentInteraction(BaseModel):
    agent_role: str
    message_content: str
    structured: bool = True

# Model: ValidationResult
# Generated: 2025-07-01T04:01:05.008614
class ValidationResult(BaseModel):
    valid: bool
    score: float
    issues: List[str] = []

