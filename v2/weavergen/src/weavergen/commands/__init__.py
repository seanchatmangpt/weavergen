"""WeaverGen v2 CLI commands."""

from .forge import forge_app
from .generate import generate_app
from .validate import validate_app
from .agents import agents_app
from .bpmn import bpmn_app
from .debug import debug_app
from .templates import templates_app
from .semantic import semantic_app
from .mining import mining_app

__all__ = [
    "forge_app",
    "generate_app",
    "validate_app",
    "agents_app",
    "bpmn_app",
    "debug_app",
    "templates_app",
    "semantic_app",
    "mining_app",
]