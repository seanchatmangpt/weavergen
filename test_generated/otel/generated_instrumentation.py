"""
Generated OpenTelemetry instrumentation from semantic conventions
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from typing import Dict, Any, Optional

class GeneratedInstrumentation:
    """Generated OTel instrumentation from semantic conventions"""
    
    def __init__(self, service_name: str = "generated_weaver_system"):
        self.service_name = service_name
        self._setup_tracing()
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        resource = Resource.create({"service.name": self.service_name})
        provider = TracerProvider(resource=resource)
        
        # Console exporter for development
        console_processor = SimpleSpanProcessor(
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter
            ConsoleSpanExporter()
        )
        provider.add_span_processor(console_processor)
        
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(self.service_name)
    
    def create_span(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """Create a new span with generated attributes"""
        span = self.tracer.start_span(operation_name)
        
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        
        return span
    
    def instrument_function(self, func_name: str):
        """Decorator to instrument functions"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                with self.create_span(f"generated.{func_name}") as span:
                    span.set_attribute("function.name", func_name)
                    span.set_attribute("function.args", str(len(args)))
                    span.set_attribute("function.kwargs", str(len(kwargs)))
                    
                    try:
                        result = func(*args, **kwargs)
                        span.set_attribute("function.success", True)
                        return result
                    except Exception as e:
                        span.set_attribute("function.success", False)
                        span.set_attribute("error.message", str(e))
                        raise
            return wrapper
        return decorator

# Global instrumentation instance
generated_instrumentation = GeneratedInstrumentation()
