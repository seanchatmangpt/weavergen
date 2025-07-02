"""Enhanced instrumentation for WeaverGen with Weaver spans."""

from functools import wraps
from typing import Any, Callable, Dict, Optional
import time
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, Span
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

# Import generated semantic convention attributes
from .semconv import (
    COMPONENT_TYPE, COMPONENT_TYPE__WORKFLOW, COMPONENT_TYPE__AGENT,
    COMPONENT_TYPE__GENERATOR, COMPONENT_TYPE__VALIDATOR,
    ENGINE, STEPS_TOTAL, STEPS_COMPLETED,
    FILES_GENERATED, LANGUAGE,
    METHOD, METHOD__SPAN
)

# Initialize tracer with WeaverGen resource
resource = Resource.create({
    "service.name": "weavergen",
    "service.version": "2.0.0",
    "service.namespace": "semantic-generation"
})

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Add console exporter for debugging
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

tracer = trace.get_tracer("weavergen", "2.0.0")


def semantic_span(component: str, operation: str) -> Callable:
    """Decorator to create semantic spans for operations."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with tracer.start_as_current_span(f"{component}.{operation}") as span:
                span.set_attribute("component", component)
                span.set_attribute("operation", operation)
                
                # Use generated constant based on component type
                if component == "bpmn_engine":
                    span.set_attribute(COMPONENT_TYPE, COMPONENT_TYPE__WORKFLOW)
                elif component == "generator":
                    span.set_attribute(COMPONENT_TYPE, COMPONENT_TYPE__GENERATOR)
                elif component == "validator":
                    span.set_attribute(COMPONENT_TYPE, COMPONENT_TYPE__VALIDATOR)
                else:
                    span.set_attribute(COMPONENT_TYPE, component)
                
                # Add function arguments as attributes
                if args and hasattr(args[0], '__class__'):
                    span.set_attribute("instance.type", args[0].__class__.__name__)
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    span.set_attribute("duration_ms", (time.time() - start_time) * 1000)
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        return wrapper
    return decorator


def workflow_span(workflow_id: str, spec_name: str) -> Callable:
    """Decorator for workflow execution spans."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with tracer.start_as_current_span(f"workflow.{spec_name}") as span:
                span.set_attribute("workflow.id", workflow_id)
                span.set_attribute("workflow.spec", spec_name)
                span.set_attribute(COMPONENT_TYPE, COMPONENT_TYPE__WORKFLOW)
                span.set_attribute(ENGINE, "spiffworkflow")
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator


def task_span(task_name: str, task_type: str) -> Callable:
    """Decorator for BPMN task execution spans."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with tracer.start_as_current_span(f"task.{task_name}") as span:
                span.set_attribute("task.name", task_name)
                span.set_attribute("task.type", task_type)
                span.set_attribute("weaver.type", "task_span")
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator


@contextmanager
def service_task_span(operation_name: str, operation_params: Dict[str, Any]):
    """Context manager for service task spans."""
    with tracer.start_as_current_span(f"service.{operation_name}") as span:
        span.set_attribute("service.operation", operation_name)
        span.set_attribute("weaver.type", "service_task_span")
        
        # Add operation parameters as attributes
        for key, value in operation_params.items():
            if isinstance(value, (str, int, float, bool)):
                span.set_attribute(f"param.{key}", value)
        
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


@contextmanager
def cli_command_span(command: str, args: Dict[str, Any]):
    """Context manager for CLI command spans."""
    with tracer.start_as_current_span(f"cli.{command}") as span:
        span.set_attribute("cli.command", command)
        span.set_attribute("weaver.type", "cli_span")
        
        # Add command arguments
        for key, value in args.items():
            if value is not None and isinstance(value, (str, int, float, bool)):
                span.set_attribute(f"arg.{key}", value)
        
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


def get_current_span() -> Optional[Span]:
    """Get the current active span."""
    return trace.get_current_span()


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Add an event to the current span."""
    span = get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes or {})