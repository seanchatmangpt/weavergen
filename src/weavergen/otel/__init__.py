"""OpenTelemetry utilities for WeaverGen.

Enhanced instrumentation, span utilities, and communication framework.
"""

from .instrumentation import setup_instrumentation, get_tracer
from .spans import span_manager, create_operation_span
from .communication import OTelCommunicationBus, OTelMessage

__all__ = [
    "setup_instrumentation",
    "get_tracer", 
    "span_manager",
    "create_operation_span",
    "OTelCommunicationBus",
    "OTelMessage",
]