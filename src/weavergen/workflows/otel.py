"""
OpenTelemetry integration for SpiffWorkflow execution.

Provides comprehensive observability for workflow execution,
agent coordination, and performance monitoring.
"""

import time
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from dataclasses import dataclass

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.trace.status import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    # Mock OpenTelemetry classes for demonstration
    class MockSpan:
        def __init__(self, name):
            self.name = name
            self.attributes = {}
            self.status = None
            
        def set_attributes(self, attrs):
            self.attributes.update(attrs)
            
        def set_attribute(self, key, value):
            self.attributes[key] = value
            
        def set_status(self, status):
            self.status = status
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            pass
    
    class MockTracer:
        def start_span(self, name, context=None):
            return MockSpan(name)
    
    class MockStatus:
        def __init__(self, code, message=""):
            self.code = code
            self.message = message
    
    class MockStatusCode:
        OK = "OK"
        ERROR = "ERROR"
    
    trace = type('MockTrace', (), {'set_span_in_context': lambda x: None, 'get_tracer': lambda x: MockTracer()})()
    Status = MockStatus
    StatusCode = MockStatusCode()
    SERVICE_NAME = "service.name"
    OTEL_AVAILABLE = False


@dataclass
class WorkflowSpanMetrics:
    """Metrics collected from workflow span execution."""
    
    workflow_id: str
    workflow_name: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    total_execution_time_ms: float
    agent_tasks: int
    agent_tokens_used: int
    span_count: int
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.successful_tasks / self.total_tasks) * 100
    
    @property
    def average_task_time_ms(self) -> float:
        """Calculate average task execution time."""
        if self.total_tasks == 0:
            return 0.0
        return self.total_execution_time_ms / self.total_tasks


class WorkflowSpanManager:
    """
    Manager for OpenTelemetry spans in SpiffWorkflow execution.
    
    Provides comprehensive observability for workflow orchestration,
    agent coordination, and performance monitoring.
    """
    
    def __init__(self, service_name: str = "weavergen-workflow"):
        """Initialize span manager."""
        self.service_name = service_name
        self.tracer = self._setup_tracer()
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_metrics: Dict[str, WorkflowSpanMetrics] = {}
    
    def _setup_tracer(self):
        """Set up OpenTelemetry tracer with exporters."""
        
        if not OTEL_AVAILABLE:
            print("📊 OpenTelemetry not available - using mock tracer for demonstration")
            return MockTracer()
        
        # Create resource
        resource = Resource(attributes={
            SERVICE_NAME: self.service_name,
            "service.version": "1.0.0",
            "workflow.engine": "SpiffWorkflow",
            "agent.framework": "PydanticAI",
            "observability.type": "distributed_tracing"
        })
        
        # Set up tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer_provider = trace.get_tracer_provider()
        
        # Add span exporters
        # Console for immediate feedback
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(console_processor)
        
        # OTLP for production monitoring (optional)
        try:
            otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
            otlp_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(otlp_processor)
        except Exception:
            pass  # OTLP collector not available
        
        # Jaeger for visualization (optional)
        try:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
            jaeger_processor = BatchSpanProcessor(jaeger_exporter)
            tracer_provider.add_span_processor(jaeger_processor)
        except Exception:
            pass  # Jaeger not available
        
        return trace.get_tracer(__name__)
    
    @contextmanager
    def workflow_span(
        self, 
        workflow_id: str,
        workflow_name: str,
        semantic_convention_id: str,
        target_languages: List[str]
    ):
        """Create a root span for workflow execution."""
        
        span_name = f"workflow.{workflow_name}.execute"
        
        with self.tracer.start_span(span_name) as span:
            # Set workflow attributes
            span.set_attributes({
                "workflow.id": workflow_id,
                "workflow.name": workflow_name,
                "workflow.engine": "SpiffWorkflow",
                "workflow.semantic_convention": semantic_convention_id,
                "workflow.target_languages": ",".join(target_languages),
                "workflow.start_time": time.time()
            })
            
            # Initialize workflow tracking
            self.active_workflows[workflow_id] = {
                "span": span,
                "start_time": time.time(),
                "tasks_executed": 0,
                "tasks_successful": 0,
                "tasks_failed": 0,
                "agent_tasks": 0,
                "total_tokens": 0,
                "span_count": 1
            }
            
            try:
                yield span
                
                # Mark as successful
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("workflow.status", "completed")
                
            except Exception as e:
                # Mark as failed
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("workflow.status", "failed")
                span.set_attribute("workflow.error", str(e))
                raise
            
            finally:
                # Finalize workflow metrics
                self._finalize_workflow_metrics(workflow_id, workflow_name)
    
    @contextmanager
    def task_span(
        self,
        workflow_id: str,
        task_name: str,
        task_type: str = "service_task"
    ):
        """Create a span for workflow task execution."""
        
        span_name = f"workflow.task.{task_name}"
        
        with self.tracer.start_span(span_name) as span:
            # Set task attributes
            span.set_attributes({
                "workflow.id": workflow_id,
                "workflow.task.name": task_name,
                "workflow.task.type": task_type,
                "workflow.task.start_time": time.time()
            })
            
            # Update workflow tracking
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["tasks_executed"] += 1
                self.active_workflows[workflow_id]["span_count"] += 1
            
            start_time = time.time()
            
            try:
                yield span
                
                # Mark as successful
                execution_time = (time.time() - start_time) * 1000
                span.set_status(Status(StatusCode.OK))
                span.set_attributes({
                    "workflow.task.status": "success",
                    "workflow.task.execution_time_ms": execution_time
                })
                
                # Update success tracking
                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id]["tasks_successful"] += 1
                
            except Exception as e:
                # Mark as failed
                execution_time = (time.time() - start_time) * 1000
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attributes({
                    "workflow.task.status": "failed",
                    "workflow.task.execution_time_ms": execution_time,
                    "workflow.task.error": str(e)
                })
                
                # Update failure tracking
                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id]["tasks_failed"] += 1
                
                raise
    
    @contextmanager 
    def agent_span(
        self,
        workflow_id: str,
        agent_name: str,
        task_name: str,
        tokens_used: int = 0
    ):
        """Create a span for AI agent execution within workflow."""
        
        span_name = f"workflow.agent.{agent_name}.{task_name}"
        
        with self.tracer.start_span(span_name) as span:
            # Set agent attributes
            span.set_attributes({
                "workflow.id": workflow_id,
                "agent.name": agent_name,
                "agent.task": task_name,
                "agent.framework": "PydanticAI",
                "agent.model": "qwen3:latest",
                "agent.start_time": time.time()
            })
            
            # Update agent tracking
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["agent_tasks"] += 1
                self.active_workflows[workflow_id]["span_count"] += 1
            
            start_time = time.time()
            
            try:
                yield span
                
                # Mark as successful
                execution_time = (time.time() - start_time) * 1000
                span.set_status(Status(StatusCode.OK))
                span.set_attributes({
                    "agent.status": "success",
                    "agent.execution_time_ms": execution_time,
                    "agent.tokens_used": tokens_used
                })
                
                # Update token tracking
                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id]["total_tokens"] += tokens_used
                
            except Exception as e:
                # Mark as failed
                execution_time = (time.time() - start_time) * 1000
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attributes({
                    "agent.status": "failed",
                    "agent.execution_time_ms": execution_time,
                    "agent.error": str(e)
                })
                
                raise
    
    @contextmanager
    def validation_span(
        self,
        workflow_id: str,
        validation_type: str,
        target: str
    ):
        """Create a span for validation activities."""
        
        span_name = f"workflow.validation.{validation_type}"
        
        with self.tracer.start_span(span_name) as span:
            # Set validation attributes
            span.set_attributes({
                "workflow.id": workflow_id,
                "validation.type": validation_type,
                "validation.target": target,
                "validation.start_time": time.time()
            })
            
            # Update span tracking
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["span_count"] += 1
            
            start_time = time.time()
            
            try:
                yield span
                
                # Mark as successful
                execution_time = (time.time() - start_time) * 1000
                span.set_status(Status(StatusCode.OK))
                span.set_attributes({
                    "validation.status": "passed",
                    "validation.execution_time_ms": execution_time
                })
                
            except Exception as e:
                # Mark as failed
                execution_time = (time.time() - start_time) * 1000
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attributes({
                    "validation.status": "failed",
                    "validation.execution_time_ms": execution_time,
                    "validation.error": str(e)
                })
                
                raise
    
    def _finalize_workflow_metrics(self, workflow_id: str, workflow_name: str):
        """Finalize and store workflow metrics."""
        
        if workflow_id not in self.active_workflows:
            return
        
        workflow_data = self.active_workflows[workflow_id]
        total_execution_time = (time.time() - workflow_data["start_time"]) * 1000
        
        metrics = WorkflowSpanMetrics(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            total_tasks=workflow_data["tasks_executed"],
            successful_tasks=workflow_data["tasks_successful"],
            failed_tasks=workflow_data["tasks_failed"],
            total_execution_time_ms=total_execution_time,
            agent_tasks=workflow_data["agent_tasks"],
            agent_tokens_used=workflow_data["total_tokens"],
            span_count=workflow_data["span_count"]
        )
        
        self.workflow_metrics[workflow_id] = metrics
        
        # Update final span attributes
        if "span" in workflow_data:
            workflow_data["span"].set_attributes({
                "workflow.total_execution_time_ms": total_execution_time,
                "workflow.total_tasks": metrics.total_tasks,
                "workflow.successful_tasks": metrics.successful_tasks,
                "workflow.failed_tasks": metrics.failed_tasks,
                "workflow.success_rate": metrics.success_rate,
                "workflow.agent_tasks": metrics.agent_tasks,
                "workflow.total_tokens": metrics.agent_tokens_used,
                "workflow.spans_created": metrics.span_count
            })
        
        # Clean up active tracking
        del self.active_workflows[workflow_id]
    
    def get_workflow_metrics(self, workflow_id: str) -> Optional[WorkflowSpanMetrics]:
        """Get metrics for a completed workflow."""
        return self.workflow_metrics.get(workflow_id)
    
    def get_all_workflow_metrics(self) -> List[WorkflowSpanMetrics]:
        """Get metrics for all completed workflows."""
        return list(self.workflow_metrics.values())
    
    def get_active_workflows(self) -> List[str]:
        """Get list of currently active workflow IDs."""
        return list(self.active_workflows.keys())
    
    def clear_metrics(self):
        """Clear stored workflow metrics."""
        self.workflow_metrics.clear()


# Global span manager instance
_span_manager = None

def get_span_manager() -> WorkflowSpanManager:
    """Get the global span manager instance."""
    global _span_manager
    if _span_manager is None:
        _span_manager = WorkflowSpanManager()
    return _span_manager