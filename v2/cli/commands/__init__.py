"""
WeaverGen v2 CLI Commands
Modular command structure for enhanced maintainability
"""

from .regeneration import app as regeneration_app
from .generate import app as generate_app
from .validate import app as validate_app
from .agents import app as agents_app
from .bpmn import app as bpmn_app
from .debug import app as debug_app
from .templates import app as templates_app
from .semantic import app as semantic_app
from .mining import app as mining_app

__all__ = [
    "regeneration_app",
    "generate_app",
    "validate_app",
    "agents_app",
    "bpmn_app",
    "debug_app",
    "templates_app",
    "semantic_app",
    "mining_app",
]