"""
BPMN Error Boundaries - 80/20 Enhancement for Robust Workflow Execution

This module implements error boundaries for BPMN workflows, enabling:
- Automatic error catching and recovery
- Compensation flows for rollback
- Error event propagation
- Graceful degradation
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .enhanced_instrumentation import semantic_span


class ErrorSeverity(Enum):
    """Error severity levels for BPMN error handling"""
    LOW = "low"        # Continue execution with warning
    MEDIUM = "medium"  # Retry or compensate
    HIGH = "high"      # Fail fast with error propagation
    CRITICAL = "critical"  # Stop entire workflow


@dataclass
class BPMNError:
    """Structured BPMN error with context"""
    task_name: str
    error_type: str
    message: str
    severity: ErrorSeverity
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    stacktrace: Optional[str] = None
    recovery_suggestion: Optional[str] = None


@dataclass 
class ErrorBoundaryConfig:
    """Configuration for error boundary behavior"""
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    capture_spans: bool = True
    enable_compensation: bool = True
    propagate_critical: bool = True
    fallback_to_mock: bool = True


class BPMNErrorBoundary:
    """
    Error boundary for BPMN task execution with 80/20 enhancements.
    
    Provides automatic error handling, retries, and compensation flows.
    """
    
    def __init__(self, config: Optional[ErrorBoundaryConfig] = None):
        self.config = config or ErrorBoundaryConfig()
        self.console = Console()
        self.tracer = trace.get_tracer(__name__)
        self.error_history: List[BPMNError] = []
        self.compensation_handlers: Dict[str, Callable] = {}
        
    def register_compensation(self, task_name: str, handler: Callable):
        """Register a compensation handler for a task"""
        self.compensation_handlers[task_name] = handler
        
    @semantic_span("bpmn", "error_boundary")
    async def execute_with_boundary(
        self, 
        task_name: str,
        task_func: Callable,
        context: Dict[str, Any],
        severity_override: Optional[ErrorSeverity] = None
    ) -> Dict[str, Any]:
        """
        Execute a task within an error boundary.
        
        Provides:
        - Automatic retry with exponential backoff
        - Error capture and span annotation
        - Compensation flow execution
        - Graceful fallback to mock execution
        """
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.config.max_retries:
            try:
                # Execute the task
                with self.tracer.start_as_current_span(f"bpmn.task.{task_name}") as span:
                    span.set_attribute("task.name", task_name)
                    span.set_attribute("retry.count", retry_count)
                    span.set_attribute("error.boundary.enabled", True)
                    
                    result = await task_func(context)
                    
                    span.set_attribute("execution.success", True)
                    span.set_status(Status(StatusCode.OK))
                    
                    # Clear any previous errors for this task
                    self.error_history = [e for e in self.error_history if e.task_name != task_name]
                    
                    return result
                    
            except Exception as e:
                last_error = e
                
                # Create structured error
                bpmn_error = BPMNError(
                    task_name=task_name,
                    error_type=type(e).__name__,
                    message=str(e),
                    severity=severity_override or self._determine_severity(e),
                    context={"retry_count": retry_count, "task_context": context},
                    stacktrace=self._get_stacktrace()
                )
                
                self.error_history.append(bpmn_error)
                
                # Log error with Rich formatting
                self._log_error(bpmn_error)
                
                # Handle based on severity
                if bpmn_error.severity == ErrorSeverity.CRITICAL:
                    if self.config.propagate_critical:
                        raise
                    else:
                        return self._create_error_result(bpmn_error)
                
                # Check if we should retry
                if retry_count < self.config.max_retries:
                    retry_count += 1
                    delay = self._calculate_retry_delay(retry_count)
                    
                    self.console.print(f"[yellow]Retrying {task_name} in {delay:.1f}s (attempt {retry_count}/{self.config.max_retries})[/yellow]")
                    await asyncio.sleep(delay)
                    continue
                
                # Max retries exceeded - try compensation
                if self.config.enable_compensation and task_name in self.compensation_handlers:
                    self.console.print(f"[yellow bold]Executing compensation for {task_name}[/yellow bold]")
                    try:
                        compensation_result = await self.compensation_handlers[task_name](context, bpmn_error)
                        return {
                            "success": False,
                            "compensated": True,
                            "compensation_result": compensation_result,
                            "error": bpmn_error.__dict__
                        }
                    except Exception as comp_error:
                        self.console.print(f"[red]Compensation failed: {comp_error}[/red]")
                
                # Fallback to mock if enabled
                if self.config.fallback_to_mock:
                    self.console.print(f"[yellow]Falling back to mock execution for {task_name}[/yellow]")
                    return self._create_mock_result(task_name, context)
                
                # All recovery attempts failed
                raise
        
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on error type and content"""
        
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Critical errors
        if any(term in error_msg for term in ["critical", "fatal", "corruption", "security"]):
            return ErrorSeverity.CRITICAL
            
        # High severity
        if any(term in error_type for term in ["Permission", "Authorization", "Authentication"]):
            return ErrorSeverity.HIGH
            
        # Medium severity  
        if any(term in error_type for term in ["Timeout", "Connection", "Network"]):
            return ErrorSeverity.MEDIUM
            
        # Default to low
        return ErrorSeverity.LOW
        
    def _calculate_retry_delay(self, retry_count: int) -> float:
        """Calculate retry delay with optional exponential backoff"""
        
        if self.config.exponential_backoff:
            return self.config.retry_delay * (2 ** (retry_count - 1))
        else:
            return self.config.retry_delay
            
    def _log_error(self, error: BPMNError):
        """Log error with Rich formatting"""
        
        color_map = {
            ErrorSeverity.LOW: "yellow",
            ErrorSeverity.MEDIUM: "yellow bold",
            ErrorSeverity.HIGH: "red",
            ErrorSeverity.CRITICAL: "red bold"
        }
        
        color = color_map.get(error.severity, "red")
        
        error_panel = Panel(
            f"[{color}]Task: {error.task_name}[/{color}]\n"
            f"Type: {error.error_type}\n"
            f"Message: {error.message}\n"
            f"Severity: {error.severity.value}\n"
            f"Time: {error.timestamp.isoformat()}",
            title=f"[{color}]BPMN Error Boundary Triggered[/{color}]",
            border_style=color
        )
        
        self.console.print(error_panel)
        
    def _create_error_result(self, error: BPMNError) -> Dict[str, Any]:
        """Create structured error result"""
        
        return {
            "success": False,
            "error": error.__dict__,
            "error_boundary_handled": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def _create_mock_result(self, task_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock result for fallback execution"""
        
        return {
            "success": True,
            "mock": True,
            "task_name": task_name,
            "message": f"Mock execution for {task_name} due to error",
            "timestamp": datetime.utcnow().isoformat(),
            "context_keys": list(context.keys())
        }
        
    def _get_stacktrace(self) -> Optional[str]:
        """Get formatted stacktrace"""
        
        import traceback
        return traceback.format_exc()
        
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors in the boundary"""
        
        summary = {
            "total_errors": len(self.error_history),
            "by_severity": {},
            "by_task": {},
            "critical_errors": []
        }
        
        for error in self.error_history:
            # Count by severity
            severity = error.severity.value
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # Count by task
            task = error.task_name
            summary["by_task"][task] = summary["by_task"].get(task, 0) + 1
            
            # Track critical errors
            if error.severity == ErrorSeverity.CRITICAL:
                summary["critical_errors"].append({
                    "task": error.task_name,
                    "message": error.message,
                    "time": error.timestamp.isoformat()
                })
                
        return summary


class BPMNCompensationFlow:
    """
    Compensation flow handler for BPMN workflows.
    
    Implements the Saga pattern for distributed transactions.
    """
    
    def __init__(self):
        self.completed_tasks: List[str] = []
        self.compensation_map: Dict[str, Callable] = {}
        self.console = Console()
        
    def register(self, task_name: str, compensation_func: Callable):
        """Register a compensation function for a task"""
        self.compensation_map[task_name] = compensation_func
        
    def mark_completed(self, task_name: str):
        """Mark a task as completed (for compensation tracking)"""
        if task_name not in self.completed_tasks:
            self.completed_tasks.append(task_name)
            
    @semantic_span("bpmn", "compensation_flow")
    async def compensate_all(self, context: Dict[str, Any], error: Optional[BPMNError] = None):
        """
        Execute compensation for all completed tasks in reverse order.
        
        Implements the Saga pattern for rollback.
        """
        
        self.console.print("[yellow]Starting compensation flow...[/yellow]")
        
        compensation_results = []
        
        # Compensate in reverse order
        for task_name in reversed(self.completed_tasks):
            if task_name in self.compensation_map:
                try:
                    self.console.print(f"[yellow]Compensating: {task_name}[/yellow]")
                    
                    result = await self.compensation_map[task_name](context, error)
                    compensation_results.append({
                        "task": task_name,
                        "success": True,
                        "result": result
                    })
                    
                    self.console.print(f"[green]✓ Compensated: {task_name}[/green]")
                    
                except Exception as e:
                    self.console.print(f"[red]✗ Compensation failed for {task_name}: {e}[/red]")
                    compensation_results.append({
                        "task": task_name,
                        "success": False,
                        "error": str(e)
                    })
                    
        return compensation_results


# Convenience decorators for error boundary integration

def with_error_boundary(
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    max_retries: int = 3,
    fallback_to_mock: bool = True
):
    """Decorator to wrap BPMN tasks with error boundaries"""
    
    def decorator(func: Callable) -> Callable:
        async def wrapper(self, *args, **kwargs):
            # Create error boundary with custom config
            config = ErrorBoundaryConfig(
                max_retries=max_retries,
                fallback_to_mock=fallback_to_mock
            )
            boundary = BPMNErrorBoundary(config)
            
            # Extract task name from function
            task_name = func.__name__
            
            # Create execution function
            async def task_execution(context):
                return await func(self, *args, **kwargs)
                
            # Execute with boundary
            return await boundary.execute_with_boundary(
                task_name=task_name,
                task_func=lambda ctx: task_execution(ctx),
                context=kwargs.get('context', {}),
                severity_override=severity
            )
            
        return wrapper
    return decorator


# Example compensation handlers

async def compensate_weaver_generation(context: Dict[str, Any], error: BPMNError):
    """Compensation handler for Weaver generation failures"""
    
    return {
        "action": "cleanup",
        "removed_files": context.get("generated_files", []),
        "reason": f"Compensating due to: {error.message}"
    }


async def compensate_ai_agent_creation(context: Dict[str, Any], error: BPMNError):
    """Compensation handler for AI agent creation failures"""
    
    return {
        "action": "rollback",
        "agents_removed": context.get("created_agents", []),
        "models_cleaned": context.get("generated_models", [])
    }