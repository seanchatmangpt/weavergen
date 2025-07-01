"""Models generated from semantic conventions"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Auto-generated from semantic conventions
class ComponentType(BaseModel):
    agent: str = "agent"
    workflow: str = "workflow"
    generator: str = "generator"
    validator: str = "validator"

class TelemetrySpan(BaseModel):
    component_type: str
    generation_source: str
    generation_target: str
    timestamp: datetime
    attributes: dict

class SystemHealth(BaseModel):
    overall_health: float
    component_health: dict
    validation_passed: bool
    quine_compliant: Optional[bool] = None
