"""Enhanced OpenTelemetry instrumentation for WeaverGen."""

import logging
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION

logger = logging.getLogger(__name__)

_tracer_provider: Optional[TracerProvider] = None
_tracer: Optional[trace.Tracer] = None

def setup_instrumentation(
    service_name: str = "weavergen",
    service_version: str = "0.1.0",
    console_export: bool = False,
    resource_attributes: Optional[dict] = None
) -> TracerProvider:
    """Setup OpenTelemetry instrumentation for WeaverGen.
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        console_export: Whether to export traces to console
        resource_attributes: Additional resource attributes
        
    Returns:
        TracerProvider: The configured tracer provider
    """
    global _tracer_provider, _tracer
    
    if _tracer_provider is not None:
        logger.debug("Instrumentation already setup")
        return _tracer_provider
    
    # Create resource attributes
    resource_attrs = {
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        "telemetry.sdk.name": "opentelemetry",
        "telemetry.sdk.language": "python",
        "weavergen.component": "core",
    }
    
    if resource_attributes:
        resource_attrs.update(resource_attributes)
    
    # Create resource
    resource = Resource.create(resource_attrs)
    
    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)
    
    # Add console exporter if requested
    if console_export:
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        _tracer_provider.add_span_processor(console_processor)
    
    # Set global tracer provider
    trace.set_tracer_provider(_tracer_provider)
    
    # Create tracer
    _tracer = trace.get_tracer(__name__)
    
    logger.info(f"OpenTelemetry instrumentation setup for {service_name} v{service_version}")
    
    return _tracer_provider

def get_tracer(name: Optional[str] = None) -> trace.Tracer:
    """Get the configured tracer.
    
    Args:
        name: Optional tracer name
        
    Returns:
        trace.Tracer: The tracer instance
    """
    global _tracer
    
    if _tracer is None:
        # Auto-setup with defaults if not already done
        setup_instrumentation()
    
    if name:
        return trace.get_tracer(name)
    
    return _tracer

def shutdown_instrumentation():
    """Shutdown instrumentation and cleanup resources."""
    global _tracer_provider, _tracer
    
    if _tracer_provider:
        _tracer_provider.shutdown()
        _tracer_provider = None
        _tracer = None
        logger.info("OpenTelemetry instrumentation shutdown")