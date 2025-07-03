"""Enhanced instrumentation for WeaverGen with Weaver spans."""

from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Import generated semantic convention attributes
from .semconv import (
    COMPONENT_TYPE,
    COMPONENT_TYPE__GENERATOR,
    COMPONENT_TYPE__VALIDATOR,
    COMPONENT_TYPE__WORKFLOW,
    ENGINE,
)

# Initialize tracer with WeaverGen resource


def semantic_span(component: str, operation: str) -> Callable:
    """Decorator to add semantic attributes to the current span."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = trace.get_current_span()
            if span and span.is_recording():
                span.set_attribute("component", component)
                span.set_attribute("operation", operation)

                if component == "bpmn_engine":
                    span.set_attribute(COMPONENT_TYPE, COMPONENT_TYPE__WORKFLOW)
                elif component == "generator":
                    span.set_attribute(COMPONENT_TYPE, COMPONENT_TYPE__GENERATOR)
                elif component == "validator":
                    span.set_attribute(COMPONENT_TYPE, COMPONENT_TYPE__VALIDATOR)
                else:
                    span.set_attribute(COMPONENT_TYPE, component)

                if args and hasattr(args[0], "__class__"):
                    span.set_attribute("instance.type", args[0].__class__.__name__)
            
            return func(*args, **kwargs)

        return wrapper

    return decorator


def workflow_span(workflow_id: str, spec_name: str) -> Callable:
    """Decorator to add workflow attributes to the current span."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = trace.get_current_span()
            if span and span.is_recording():
                span.set_attribute("workflow.id", workflow_id)
                span.set_attribute("workflow.spec", spec_name)
                span.set_attribute(COMPONENT_TYPE, COMPONENT_TYPE__WORKFLOW)
                span.set_attribute(ENGINE, "spiffworkflow")
            
            return func(*args, **kwargs)

        return wrapper

    return decorator


def task_span(task_name: str, task_type: str) -> Callable:
    """Decorator to add task attributes to the current span."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = trace.get_current_span()
            if span and span.is_recording():
                span.set_attribute("task.name", task_name)
                span.set_attribute("task.type", task_type)
                span.set_attribute("weaver.type", "task_span")
            
            return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def service_task_span(operation_name: str, operation_params: dict[str, Any]):
    """Context manager to add service task attributes to the current span."""
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("service.operation", operation_name)
        span.set_attribute("weaver.type", "service_task_span")

        for key, value in operation_params.items():
            if isinstance(value, (str, int, float, bool)):
                span.set_attribute(f"param.{key}", value)
    try:
        yield span
    except Exception:
        raise


@contextmanager
def cli_command_span(command: str, args: dict[str, Any]):
    """Context manager to add CLI command attributes to the current span."""
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("cli.command", command)
        span.set_attribute("weaver.type", "cli_span")

        for key, value in args.items():
            if value is not None and isinstance(value, (str, int, float, bool)):
                span.set_attribute(f"arg.{key}", value)
    try:
        yield span
    except Exception:
        raise


def get_current_span():
    """Get the current active span."""
    return trace.get_current_span()


def add_span_event(name: str, attributes: dict[str, Any] | None = None):
    """Add an event to the current span."""
    span = get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes or {})