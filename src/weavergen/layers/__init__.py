"""
WeaverGen 4-Layer Architecture

This module implements the four-layer architectural pattern for WeaverGen:

1. Commands Layer    - CLI interfaces and user-facing commands
2. Operations Layer  - Business logic and orchestration
3. Runtime Layer     - Execution engine and process management
4. Contracts Layer   - Data models, interfaces, and type definitions

Each layer has clear responsibilities and dependencies flow downward only:
Commands -> Operations -> Runtime -> Contracts
"""

from .commands import *
from .operations import *
from .runtime import *
from .contracts import *

__all__ = [
    # Commands Layer
    "GenerateCommand",
    "ValidateCommand",
    "InitCommand",
    "TemplateCommand",
    "SemanticCommand",
    
    # Operations Layer
    "GenerationOperation",
    "ValidationOperation",
    "TemplateOperation",
    "SemanticOperation",
    
    # Runtime Layer
    "WeaverRuntime",
    "TemplateEngine",
    "ValidationEngine",
    "ExecutionContext",
    
    # Contracts Layer
    "GenerationRequest",
    "GenerationResult",
    "ValidationRequest",
    "ValidationResult",
    "TemplateManifest",
    "SemanticConvention",
]