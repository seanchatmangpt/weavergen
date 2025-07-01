"""
UltraThink Validator: Trust Nothing, Validate Everything

This module implements the principle that ALL summaries are lies
until validated against actual OpenTelemetry spans that include
the exact file that executed each operation.
"""

import inspect
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Setup tracing with file attribution
memory_exporter = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(memory_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


@dataclass
class Claim:
    """A claim made in a summary that must be validated"""
    claim_text: str
    claim_type: str  # "execution", "performance", "success", "count"
    expected_value: Any
    source_file: str
    line_number: int
    validated: bool = False
    actual_value: Any = None
    evidence_spans: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Report showing which claims are lies vs truth"""
    total_claims: int = 0
    validated_claims: int = 0
    lies: List[Claim] = field(default_factory=list)
    truths: List[Claim] = field(default_factory=list)
    unverifiable: List[Claim] = field(default_factory=list)
    trust_score: float = 0.0


def capture_file_context() -> Tuple[str, int]:
    """Capture the file and line number of the caller"""
    frame = inspect.currentframe()
    if frame and frame.f_back and frame.f_back.f_back:
        caller_frame = frame.f_back.f_back
        filename = caller_frame.f_code.co_filename
        line_number = caller_frame.f_lineno
        return filename, line_number
    return "unknown", 0


def ultra_span(name: str):
    """Decorator that captures file context in every span"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            file_path, line_num = capture_file_context()
            
            with tracer.start_as_current_span(name) as span:
                # CRITICAL: Add file attribution to EVERY span
                span.set_attribute("code.filepath", file_path)
                span.set_attribute("code.lineno", line_num)
                span.set_attribute("code.function", func.__name__)
                span.set_attribute("code.module", func.__module__)
                
                # Add timestamp for exact execution time
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
        
        # Sync version
        def sync_wrapper(*args, **kwargs):
            file_path, line_num = capture_file_context()
            
            with tracer.start_as_current_span(name) as span:
                span.set_attribute("code.filepath", file_path)
                span.set_attribute("code.lineno", line_num)
                span.set_attribute("code.function", func.__name__)
                span.set_attribute("code.module", func.__module__)
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
        
        return wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


class UltraThinkValidator:
    """Validates ALL claims against actual telemetry"""
    
    def __init__(self):
        self.claims: List[Claim] = []
        self.spans: List[Dict[str, Any]] = []
    
    def register_claim(self, claim_text: str, claim_type: str, expected_value: Any):
        """Register a claim that must be validated"""
        file_path, line_num = capture_file_context()
        claim = Claim(
            claim_text=claim_text,
            claim_type=claim_type,
            expected_value=expected_value,
            source_file=file_path,
            line_number=line_num
        )
        self.claims.append(claim)
        return claim
    
    def load_spans(self):
        """Load all captured spans"""
        provider.force_flush()
        raw_spans = memory_exporter.get_finished_spans()
        
        self.spans = []
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
                },
                "events": [],
                "resource": {}
            }
            self.spans.append(span_dict)
    
    def validate_claims(self) -> ValidationReport:
        """Validate all claims against actual spans"""
        report = ValidationReport(total_claims=len(self.claims))
        
        for claim in self.claims:
            validated = False
            
            if claim.claim_type == "execution":
                # Validate that something actually executed
                matching_spans = [
                    s for s in self.spans 
                    if claim.expected_value in s["name"]
                ]
                if matching_spans:
                    claim.validated = True
                    claim.actual_value = len(matching_spans)
                    claim.evidence_spans = matching_spans
                    validated = True
            
            elif claim.claim_type == "success":
                # Validate success claims
                matching_spans = [
                    s for s in self.spans
                    if s["attributes"].get("execution.success") == claim.expected_value
                ]
                if matching_spans:
                    claim.validated = True
                    claim.actual_value = True
                    claim.evidence_spans = matching_spans
                    validated = True
            
            elif claim.claim_type == "performance":
                # Validate performance claims
                for span in self.spans:
                    duration_ms = span["duration_ns"] / 1_000_000
                    if duration_ms <= claim.expected_value:
                        claim.validated = True
                        claim.actual_value = duration_ms
                        claim.evidence_spans.append(span)
                        validated = True
            
            elif claim.claim_type == "count":
                # Validate count claims
                actual_count = len(self.spans)
                claim.actual_value = actual_count
                if actual_count == claim.expected_value:
                    claim.validated = True
                    claim.evidence_spans = self.spans
                    validated = True
            
            elif claim.claim_type == "file_execution":
                # Validate that specific file executed
                matching_spans = [
                    s for s in self.spans
                    if claim.expected_value in s["attributes"].get("code.filepath", "")
                ]
                if matching_spans:
                    claim.validated = True
                    claim.actual_value = len(matching_spans)
                    claim.evidence_spans = matching_spans
                    validated = True
            
            # Categorize claim
            if validated and claim.validated:
                report.truths.append(claim)
                report.validated_claims += 1
            elif not validated and claim.actual_value is not None:
                report.lies.append(claim)
            else:
                report.unverifiable.append(claim)
        
        # Calculate trust score
        if report.total_claims > 0:
            report.trust_score = report.validated_claims / report.total_claims
        
        return report
    
    def generate_truth_table(self, report: ValidationReport) -> Table:
        """Generate a table showing lies vs truths"""
        table = Table(title="UltraThink Validation: Lies vs Truth", show_header=True)
        table.add_column("Claim", style="cyan", width=40)
        table.add_column("Type", style="yellow", width=15)
        table.add_column("Expected", style="green", width=15)
        table.add_column("Actual", style="magenta", width=15)
        table.add_column("Status", style="bold", width=10)
        table.add_column("Evidence", style="blue", width=20)
        
        # Show lies first (most important)
        for lie in report.lies:
            evidence = f"{len(lie.evidence_spans)} spans" if lie.evidence_spans else "NO SPANS"
            table.add_row(
                lie.claim_text,
                lie.claim_type,
                str(lie.expected_value),
                str(lie.actual_value),
                "[red]LIE[/red]",
                evidence
            )
        
        # Then truths
        for truth in report.truths:
            evidence = f"{len(truth.evidence_spans)} spans"
            table.add_row(
                truth.claim_text,
                truth.claim_type,
                str(truth.expected_value),
                str(truth.actual_value),
                "[green]TRUTH[/green]",
                evidence
            )
        
        # Finally unverifiable
        for unv in report.unverifiable:
            table.add_row(
                unv.claim_text,
                unv.claim_type,
                str(unv.expected_value),
                "N/A",
                "[yellow]UNVERIFIABLE[/yellow]",
                "NO EVIDENCE"
            )
        
        return table
    
    def show_file_attribution(self) -> Table:
        """Show which files actually executed based on spans"""
        table = Table(title="File Execution Attribution", show_header=True)
        table.add_column("File", style="cyan", width=50)
        table.add_column("Function", style="yellow", width=20)
        table.add_column("Line", style="green", width=10)
        table.add_column("Spans", style="magenta", width=10)
        table.add_column("Success Rate", style="bold", width=15)
        
        # Group spans by file
        file_stats: Dict[str, Dict[str, Any]] = {}
        
        for span in self.spans:
            attrs = span["attributes"]
            filepath = attrs.get("code.filepath", "unknown")
            
            if filepath not in file_stats:
                file_stats[filepath] = {
                    "functions": set(),
                    "lines": set(),
                    "total_spans": 0,
                    "successful_spans": 0
                }
            
            stats = file_stats[filepath]
            stats["functions"].add(attrs.get("code.function", "unknown"))
            stats["lines"].add(attrs.get("code.lineno", 0))
            stats["total_spans"] += 1
            
            if attrs.get("execution.success", False):
                stats["successful_spans"] += 1
        
        # Show stats
        for filepath, stats in sorted(file_stats.items()):
            success_rate = stats["successful_spans"] / stats["total_spans"] if stats["total_spans"] > 0 else 0
            
            table.add_row(
                Path(filepath).name if filepath != "unknown" else "unknown",
                ", ".join(sorted(stats["functions"]))[:20] + "...",
                ", ".join(str(l) for l in sorted(stats["lines"]))[:10] + "...",
                str(stats["total_spans"]),
                f"{success_rate:.1%}"
            )
        
        return table


# Example usage functions with claims
@ultra_span("example.function.one")
def example_function_one():
    """Example function that generates spans"""
    validator = UltraThinkValidator()
    validator.register_claim("Function one executes", "execution", "example.function.one")
    validator.register_claim("Function one succeeds", "success", True)
    
    # Do some work
    import time
    time.sleep(0.01)
    
    return "done"


@ultra_span("example.function.two")
async def example_function_two():
    """Example async function that generates spans"""
    validator = UltraThinkValidator()
    validator.register_claim("Function two executes", "execution", "example.function.two")
    validator.register_claim("Function two is fast", "performance", 50)  # < 50ms
    
    # Do some work
    await asyncio.sleep(0.02)
    
    return "done"


async def demonstrate_ultrathink_validation():
    """Demonstrate the UltraThink validation principle"""
    console.clear()
    
    intro = Panel(
        "[bold red]🧠 ULTRATHINK VALIDATION PRINCIPLE[/bold red]\n\n"
        "[yellow]ALL SUMMARIES ARE LIES UNTIL PROVEN BY TELEMETRY[/yellow]\n\n"
        "This system validates EVERY claim against actual OpenTelemetry spans\n"
        "that include the exact file and line number that executed.\n\n"
        "[cyan]Trust nothing. Validate everything.[/cyan]",
        style="red"
    )
    console.print(intro)
    console.print()
    
    # Create validator
    validator = UltraThinkValidator()
    
    # Register some claims (some true, some lies)
    console.print("[yellow]Registering claims to validate...[/yellow]")
    validator.register_claim("20 spans were generated", "count", 20)
    validator.register_claim("All operations succeeded", "success", True)
    validator.register_claim("BPMN workflow executed", "execution", "bpmn")
    validator.register_claim("Weaver Forge ran", "execution", "weaver")
    validator.register_claim("Everything was super fast", "performance", 10)  # < 10ms
    validator.register_claim("This file executed", "file_execution", "ultrathink_validator.py")
    
    # Execute some functions
    console.print("[cyan]Executing functions...[/cyan]")
    example_function_one()
    await example_function_two()
    
    # Load and validate
    console.print("[green]Loading spans and validating claims...[/green]\n")
    validator.load_spans()
    report = validator.validate_claims()
    
    # Show results
    truth_table = validator.generate_truth_table(report)
    console.print(truth_table)
    console.print()
    
    # Show file attribution
    file_table = validator.show_file_attribution()
    console.print(file_table)
    console.print()
    
    # Summary
    summary = Panel(
        f"[bold]VALIDATION SUMMARY[/bold]\n\n"
        f"Total Claims: {report.total_claims}\n"
        f"Validated Truths: [green]{len(report.truths)}[/green]\n"
        f"Exposed Lies: [red]{len(report.lies)}[/red]\n"
        f"Unverifiable: [yellow]{len(report.unverifiable)}[/yellow]\n\n"
        f"TRUST SCORE: [{'green' if report.trust_score >= 0.8 else 'red'}]{report.trust_score:.1%}[/]\n\n"
        f"[dim]Remember: Without telemetry, it's just fiction.[/dim]",
        title="UltraThink Results",
        border_style="cyan"
    )
    console.print(summary)
    
    # Save evidence
    evidence_file = Path("ultrathink_evidence.json")
    with open(evidence_file, 'w') as f:
        evidence = {
            "claims": [
                {
                    "claim": c.claim_text,
                    "type": c.claim_type,
                    "expected": c.expected_value,
                    "actual": c.actual_value,
                    "validated": c.validated,
                    "source_file": c.source_file,
                    "line_number": c.line_number,
                    "evidence_span_count": len(c.evidence_spans)
                }
                for c in report.lies + report.truths + report.unverifiable
            ],
            "spans": validator.spans,
            "trust_score": report.trust_score
        }
        json.dump(evidence, f, indent=2, default=str)
    
    console.print(f"\n[cyan]Evidence saved to: {evidence_file}[/cyan]")


if __name__ == "__main__":
    asyncio.run(demonstrate_ultrathink_validation())