"""WeaverGen: Python wrapper for OTel Weaver Forge with Claude Code optimization.

A high-performance Python interface to OpenTelemetry Weaver Forge for automated
semantic convention code generation, optimized for Claude Code workflows.
"""

__version__ = "0.1.0"
__author__ = "Sean Chatman"
__email__ = "sean@seanchatman.com"

from .core import WeaverGen
from .cli import app as cli_app

__all__ = ["WeaverGen", "cli_app", "__version__"]
