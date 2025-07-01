#!/usr/bin/env python3
"""
WeaverGen Contracts Layer Extension
Semantic convention support for the contracts layer
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SemanticConventionContract(BaseModel):
    """Contract for semantic convention processing"""
    
    name: str = Field(..., description="Convention name")
    type: str = Field(default="span", description="Convention type")
    brief: str = Field(default="", description="Brief description")
    stability: str = Field(default="stable", description="Stability level")
    attributes: List[Dict[str, Any]] = Field(default_factory=list)
    groups: List[Dict[str, Any]] = Field(default_factory=list)

class GenerationContract(BaseModel):
    """Contract for code generation requests"""
    
    convention: SemanticConventionContract
    output_dir: str = Field(default="generated")
    target_language: str = Field(default="python")
    template_type: str = Field(default="pydantic")
    validation_enabled: bool = Field(default=True)

class GenerationResultContract(BaseModel):
    """Contract for generation results"""
    
    success: bool
    generated_files: List[str] = Field(default_factory=list)
    validation_results: List[str] = Field(default_factory=list)
    duration_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
