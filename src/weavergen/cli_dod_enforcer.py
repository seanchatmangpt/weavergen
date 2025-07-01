"""
CLI Definition of Done Enforcer

Automatically validates that every CLI command execution meets the
Definition of Done criteria, especially BPMN attribution.
"""

import functools
import inspect
import sys
import asyncio
from pathlib import Path
from typing import Any, Callable, Optional
import typer
import json
from datetime import datetime

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from .dod_validator import DefinitionOfDoneValidator, DoDValidationResult

console = Console()

# Global span exporter for CLI validation
CLI_MEMORY_EXPORTER = InMemorySpanExporter()
CLI_PROVIDER = TracerProvider()
CLI_PROVIDER.add_span_processor(BatchSpanProcessor(CLI_MEMORY_EXPORTER))

# Store original provider to restore later
ORIGINAL_PROVIDER = trace.get_tracer_provider()


class CLIDoDEnforcer:
    """Enforces Definition of Done on CLI commands"""
    
    def __init__(self, 
                 require_bpmn: bool = True,
                 min_trust_score: float = 0.8,
                 fail_on_lies: bool = True):
        self.require_bpmn = require_bpmn
        self.min_trust_score = min_trust_score
        self.fail_on_lies = fail_on_lies
        self.validator = DefinitionOfDoneValidator()
    
    def capture_cli_context(self, func: Callable) -> dict:
        """Capture context about the CLI command"""
        module = inspect.getmodule(func)
        return {
            "cli.command": func.__name__,
            "cli.module": module.__name__ if module else "unknown",
            "cli.file": inspect.getfile(func),
            "cli.timestamp": datetime.now().isoformat(),
            "cli.args": sys.argv[1:]  # CLI arguments
        }
    
    def export_spans(self) -> list:
        """Export captured spans"""
        CLI_PROVIDER.force_flush()
        raw_spans = CLI_MEMORY_EXPORTER.get_finished_spans()
        
        spans = []
        for span in raw_spans:
            span_dict = {
                "name": span.name,
                "trace_id": f"0x{span.context.trace_id:032x}",
                "span_id": f"0x{span.context.span_id:016x}",
                "parent_id": f"0x{span.parent.span_id:016x}" if span.parent else None,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "duration_ns": span.end_time - span.start_time if span.end_time else 0,
                "attributes": dict(span.attributes or {}),
                "status": {
                    "status_code": span.status.status_code.name if span.status else "UNSET",
                    "description": span.status.description if span.status else None
                }
            }
            spans.append(span_dict)
        
        return spans
    
    def validate_command_execution(self, 
                                   command_name: str,
                                   spans: list,
                                   context: dict) -> tuple[bool, DoDValidationResult]:
        """Validate that command execution meets DoD"""
        # Run validation
        result = self.validator.validate_spans(spans)
        
        # Check specific requirements
        passed = True
        reasons = []
        
        # Check trust score
        if result.trust_score < self.min_trust_score:
            passed = False
            reasons.append(f"Trust score {result.trust_score:.1%} < required {self.min_trust_score:.1%}")
        
        # Check for lies
        if self.fail_on_lies and result.lies_detected:
            passed = False
            reasons.append(f"Detected {len(result.lies_detected)} lies in execution")
        
        # Check BPMN attribution if required
        if self.require_bpmn:
            bpmn_spans = [
                s for s in spans 
                if s.get("attributes", {}).get("bpmn.workflow.file")
            ]
            if not bpmn_spans:
                passed = False
                reasons.append("No BPMN attribution found in any spans")
        
        # Show validation summary
        if not passed:
            console.print(Panel(
                f"[bold red]❌ COMMAND FAILED VALIDATION[/bold red]\n\n"
                f"Command: [yellow]{command_name}[/yellow]\n"
                f"Trust Score: [red]{result.trust_score:.1%}[/red]\n"
                f"Reasons:\n" + "\n".join(f"  • {r}" for r in reasons),
                title="Definition of Done Violation",
                border_style="red"
            ))
            
            # Show what's missing
            if self.require_bpmn and not bpmn_spans:
                console.print("\n[yellow]Missing BPMN attributes:[/yellow]")
                console.print("  • bpmn.workflow.file")
                console.print("  • bpmn.workflow.id")
                console.print("  • bpmn.task.id")
                console.print("  • bpmn.task.type")
        
        return passed, result
    
    def save_validation_report(self, 
                               command_name: str,
                               result: DoDValidationResult,
                               spans: list,
                               context: dict):
        """Save validation report for audit"""
        report = {
            "command": command_name,
            "context": context,
            "validation": {
                "trust_score": result.trust_score,
                "is_done": result.is_done,
                "total_spans": result.total_spans,
                "level1_pass": result.level1_pass,
                "level2_pass": result.level2_pass,
                "level3_pass": result.level3_pass,
                "lies_detected": result.lies_detected,
                "violations": [
                    {
                        "level": v.level,
                        "rule": v.rule,
                        "description": v.description,
                        "severity": v.severity
                    }
                    for v in result.violations
                ]
            },
            "spans": spans
        }
        
        # Save to .weavergen/validation/
        validation_dir = Path(".weavergen/validation")
        validation_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = validation_dir / f"{command_name}_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        console.print(f"\n[dim]Validation report saved: {report_file}[/dim]")


def enforce_dod(
    require_bpmn: bool = True,
    min_trust_score: float = 0.8,
    fail_on_lies: bool = True,
    save_report: bool = True
):
    """
    Decorator that enforces Definition of Done on CLI commands
    
    Usage:
        @enforce_dod(require_bpmn=True)
        def my_command():
            # Command implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create enforcer
            enforcer = CLIDoDEnforcer(
                require_bpmn=require_bpmn,
                min_trust_score=min_trust_score,
                fail_on_lies=fail_on_lies
            )
            
            # Clear any previous spans
            CLI_MEMORY_EXPORTER.clear()
            
            # Set our provider to capture spans
            trace.set_tracer_provider(CLI_PROVIDER)
            
            # Capture context
            context = enforcer.capture_cli_context(func)
            command_name = func.__name__
            
            # Create root span for the command
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(f"cli.command.{command_name}") as span:
                # Add CLI context
                for key, value in context.items():
                    span.set_attribute(key, str(value))
                
                # Add code attribution
                span.set_attribute("code.filepath", context["cli.file"])
                span.set_attribute("code.function", command_name)
                
                try:
                    # Execute the actual command
                    result = func(*args, **kwargs)
                    span.set_attribute("execution.success", True)
                    
                except Exception as e:
                    span.set_attribute("execution.success", False)
                    span.set_attribute("execution.error", str(e))
                    span.record_exception(e)
                    raise
                
                finally:
                    # Restore original provider
                    trace.set_tracer_provider(ORIGINAL_PROVIDER)
                    
                    # Export and validate spans
                    spans = enforcer.export_spans()
                    
                    # Validate
                    passed, validation_result = enforcer.validate_command_execution(
                        command_name, spans, context
                    )
                    
                    # Save report if requested
                    if save_report:
                        enforcer.save_validation_report(
                            command_name, validation_result, spans, context
                        )
                    
                    # Fail command if validation failed
                    if not passed:
                        console.print(f"\n[red]Command '{command_name}' failed DoD validation[/red]")
                        raise typer.Exit(1)
                
                return result
        
        return wrapper
    return decorator


def cli_span(name: str, bpmn_file: Optional[str] = None, bpmn_task: Optional[str] = None):
    """
    Enhanced span decorator for CLI functions that includes BPMN attribution
    
    Usage:
        @cli_span("generate.python", bpmn_file="workflows/generate.bpmn", bpmn_task="Task_Generate")
        def generate_python_code():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_as_current_span(name) as span:
                # Add code attribution
                file_path = inspect.getfile(func)
                _, line_num = inspect.getsourcelines(func)
                
                span.set_attribute("code.filepath", file_path)
                span.set_attribute("code.lineno", line_num)
                span.set_attribute("code.function", func.__name__)
                span.set_attribute("code.module", func.__module__)
                
                # Add BPMN attribution if provided
                if bpmn_file:
                    span.set_attribute("bpmn.workflow.file", bpmn_file)
                    span.set_attribute("bpmn.workflow.id", Path(bpmn_file).stem)
                    
                    if bpmn_task:
                        span.set_attribute("bpmn.task.id", bpmn_task)
                        span.set_attribute("bpmn.task.type", "serviceTask")
                
                # Add execution context
                span.set_attribute("execution.timestamp", datetime.now().isoformat())
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("execution.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("execution.success", False)
                    span.set_attribute("execution.error", str(e))
                    span.record_exception(e)
                    raise
        
        # Handle async functions
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                tracer = trace.get_tracer(__name__)
                
                with tracer.start_as_current_span(name) as span:
                    # Same attribution as sync version
                    file_path = inspect.getfile(func)
                    _, line_num = inspect.getsourcelines(func)
                    
                    span.set_attribute("code.filepath", file_path)
                    span.set_attribute("code.lineno", line_num)
                    span.set_attribute("code.function", func.__name__)
                    span.set_attribute("code.module", func.__module__)
                    
                    if bpmn_file:
                        span.set_attribute("bpmn.workflow.file", bpmn_file)
                        span.set_attribute("bpmn.workflow.id", Path(bpmn_file).stem)
                        
                        if bpmn_task:
                            span.set_attribute("bpmn.task.id", bpmn_task)
                            span.set_attribute("bpmn.task.type", "serviceTask")
                    
                    span.set_attribute("execution.timestamp", datetime.now().isoformat())
                    
                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("execution.success", True)
                        return result
                    except Exception as e:
                        span.set_attribute("execution.success", False)
                        span.set_attribute("execution.error", str(e))
                        span.record_exception(e)
                        raise
            
            return async_wrapper
        
        return wrapper
    return decorator


# Example enhanced CLI command
@enforce_dod(require_bpmn=True, min_trust_score=0.8)
@cli_span("example.validated_command", 
          bpmn_file="workflows/example.bpmn", 
          bpmn_task="Task_Example")
def example_validated_command():
    """Example command with full DoD enforcement"""
    console.print("[green]Executing validated command...[/green]")
    
    # This will automatically be validated for:
    # - BPMN attribution
    # - File path validity
    # - Trust score > 80%
    # - No lies detected
    
    return "Success"