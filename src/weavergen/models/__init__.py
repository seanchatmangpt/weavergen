"""Enhanced data models for WeaverGen.

Generated from semantic conventions using Weaver Forge.
"""

# Import from parent models.py (avoid circular import)
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from models import *
except ImportError:
    # Fallback - import explicitly
    from models import GenerationConfig, FileInfo, GenerationResult, ValidationResult, TemplateInfo, ConfigData

# Import from generated models (created by Weaver Forge)
try:
    from .generated import *
except ImportError:
    pass  # Generated models may not exist yet

__all__ = [
    "GenerationConfig",
    "FileInfo", 
    "GenerationResult",
    "ValidationResult",
    "TemplateInfo",
    "ConfigData",
    # All exports from generated models
]