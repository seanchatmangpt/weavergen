"""
Span Validator for BPMN-driven systems

Captures, analyzes, and validates OpenTelemetry spans from 
BPMN workflow executions.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()
tracer = trace.get_tracer(__name__)


@dataclass
class SpanValidationResult:
    """Result of span validation"""
    total_spans: int = 0
    valid_spans: int = 0
    semantic_compliance: float = 0.0
    coverage_score: float = 0.0
    hierarchy_valid: bool = False
    performance_score: float = 0.0
    health_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class SpanCaptureSystem:
    """Captures spans from BPMN executions"""
    
    def __init__(self):
        self.memory_exporter = InMemorySpanExporter()
        self.provider = TracerProvider()
        
        # Add exporters
        self.provider.add_span_processor(
            BatchSpanProcessor(self.memory_exporter)
        )
        
        # Set as global provider
        trace.set_tracer_provider(self.provider)
        
        self.captured_spans = []
    
    def get_captured_spans(self) -> List[Dict[str, Any]]:
        """Get all captured spans as dictionaries"""
        spans = self.memory_exporter.get_finished_spans()
        
        span_dicts = []
        for span in spans:
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
                "events": [
                    {
                        "name": event.name,
                        "timestamp": event.timestamp,
                        "attributes": dict(event.attributes or {})
                    }
                    for event in span.events
                ],
                "resource": dict(span.resource.attributes) if span.resource else {}
            }
            span_dicts.append(span_dict)
        
        return span_dicts
    
    def save_spans(self, filepath: Path):
        """Save captured spans to file"""
        spans = self.get_captured_spans()
        with open(filepath, 'w') as f:
            json.dump(spans, f, indent=2, default=str)
        return len(spans)
    
    def clear_spans(self):
        """Clear captured spans"""
        self.memory_exporter.clear()


class SpanValidator:
    """Validates spans according to semantic conventions"""
    
    def __init__(self):
        self.required_attributes = {
            "bpmn": ["bpmn.task.type", "bpmn.task.class"],
            "weaver": ["weaver.command", "weaver.path"],
            "generation": ["generation.target", "generation.language"],
            "validation": ["validation.method", "validation.score"]
        }
    
    def validate_spans(self, spans: List[Dict[str, Any]]) -> SpanValidationResult:
        """Validate a collection of spans"""
        result = SpanValidationResult()
        result.total_spans = len(spans)
        
        if not spans:
            result.issues.append("No spans captured")
            return result
        
        # Check each validation aspect
        result.semantic_compliance = self._check_semantic_compliance(spans)
        result.coverage_score = self._check_coverage(spans)
        result.hierarchy_valid = self._check_hierarchy(spans)
        result.performance_score = self._check_performance(spans)
        
        # Calculate valid spans
        for span in spans:
            if self._is_span_valid(span):
                result.valid_spans += 1
        
        # Calculate health score
        result.health_score = (
            result.semantic_compliance * 0.3 +
            result.coverage_score * 0.3 +
            (1.0 if result.hierarchy_valid else 0.0) * 0.2 +
            result.performance_score * 0.2
        )
        
        # Generate recommendations
        if result.semantic_compliance < 0.8:
            result.recommendations.append("Improve semantic attribute compliance")
        if result.coverage_score < 0.8:
            result.recommendations.append("Increase span coverage for all components")
        if not result.hierarchy_valid:
            result.recommendations.append("Fix span parent-child relationships")
        if result.performance_score < 0.8:
            result.recommendations.append("Optimize long-running operations")
        
        return result
    
    def _is_span_valid(self, span: Dict[str, Any]) -> bool:
        """Check if a single span is valid"""
        # Must have name
        if not span.get("name"):
            return False
        
        # Must have attributes
        if not span.get("attributes"):
            return False
        
        # Must have valid times
        if span.get("duration_ns", 0) < 0:
            return False
        
        return True
    
    def _check_semantic_compliance(self, spans: List[Dict[str, Any]]) -> float:
        """Check compliance with semantic conventions"""
        compliant_count = 0
        
        for span in spans:
            attrs = span.get("attributes", {})
            span_type = None
            
            # Determine span type from name
            if "bpmn" in span["name"]:
                span_type = "bpmn"
            elif "weaver" in span["name"]:
                span_type = "weaver"
            elif "generation" in span["name"]:
                span_type = "generation"
            elif "validation" in span["name"]:
                span_type = "validation"
            
            if span_type and span_type in self.required_attributes:
                # Check if required attributes are present
                required = self.required_attributes[span_type]
                if any(attr in attrs for attr in required):
                    compliant_count += 1
        
        return compliant_count / len(spans) if spans else 0.0
    
    def _check_coverage(self, spans: List[Dict[str, Any]]) -> float:
        """Check span coverage across components"""
        components = set()
        expected_components = {
            "bpmn", "weaver", "python", "validation", "generation"
        }
        
        for span in spans:
            name = span["name"]
            for component in expected_components:
                if component in name:
                    components.add(component)
        
        return len(components) / len(expected_components)
    
    def _check_hierarchy(self, spans: List[Dict[str, Any]]) -> bool:
        """Check if span hierarchy is valid"""
        span_map = {span["span_id"]: span for span in spans}
        
        for span in spans:
            parent_id = span.get("parent_id")
            if parent_id and parent_id != "0x0000000000000000":
                if parent_id not in span_map:
                    return False
        
        return True
    
    def _check_performance(self, spans: List[Dict[str, Any]]) -> float:
        """Check span performance metrics"""
        if not spans:
            return 0.0
        
        # Check for reasonable durations (not too long)
        long_spans = 0
        for span in spans:
            duration_ms = span.get("duration_ns", 0) / 1_000_000
            if duration_ms > 5000:  # More than 5 seconds
                long_spans += 1
        
        return 1.0 - (long_spans / len(spans))


class SpanReportGenerator:
    """Generates reports from span validation"""
    
    def generate_table_report(self, result: SpanValidationResult) -> Table:
        """Generate a table report"""
        table = Table(title="Span Validation Report", show_header=True)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="green", width=15)
        table.add_column("Status", style="yellow", width=10)
        
        # Add metrics
        table.add_row("Total Spans", str(result.total_spans), "✅" if result.total_spans > 0 else "❌")
        table.add_row("Valid Spans", str(result.valid_spans), "✅" if result.valid_spans == result.total_spans else "⚠️")
        table.add_row("Semantic Compliance", f"{result.semantic_compliance:.1%}", "✅" if result.semantic_compliance >= 0.8 else "❌")
        table.add_row("Coverage Score", f"{result.coverage_score:.1%}", "✅" if result.coverage_score >= 0.8 else "❌")
        table.add_row("Hierarchy Valid", str(result.hierarchy_valid), "✅" if result.hierarchy_valid else "❌")
        table.add_row("Performance Score", f"{result.performance_score:.1%}", "✅" if result.performance_score >= 0.8 else "❌")
        table.add_row("Health Score", f"{result.health_score:.1%}", "✅" if result.health_score >= 0.8 else "⚠️")
        
        return table
    
    def generate_tree_report(self, spans: List[Dict[str, Any]]) -> Tree:
        """Generate a tree view of span hierarchy"""
        tree = Tree("Span Hierarchy")
        
        # Build parent-child map
        children_map = defaultdict(list)
        root_spans = []
        
        for span in spans:
            parent_id = span.get("parent_id")
            if not parent_id or parent_id == "0x0000000000000000":
                root_spans.append(span)
            else:
                children_map[parent_id].append(span)
        
        # Build tree recursively
        def add_span_to_tree(parent_node, span):
            span_info = f"{span['name']} ({span.get('duration_ns', 0) / 1_000_000:.1f}ms)"
            node = parent_node.add(span_info)
            
            # Add children
            for child in children_map.get(span["span_id"], []):
                add_span_to_tree(node, child)
        
        # Add root spans
        for root_span in root_spans:
            add_span_to_tree(tree, root_span)
        
        return tree
    
    def generate_mermaid_trace(self, spans: List[Dict[str, Any]]) -> str:
        """Generate Mermaid sequence diagram from spans"""
        if not spans:
            return "graph LR\n    A[No spans captured]"
        
        # Sort spans by start time
        sorted_spans = sorted(spans, key=lambda s: s.get("start_time", 0))
        
        mermaid = """sequenceDiagram
    participant U as User
    participant B as BPMN Engine
    participant W as Weaver
    participant G as Generated Code
    
"""
        
        for span in sorted_spans:
            name = span["name"]
            duration_ms = span.get("duration_ns", 0) / 1_000_000
            
            if "bpmn" in name:
                mermaid += f"    U->>B: {name}\n"
                mermaid += f"    Note over B: {duration_ms:.1f}ms\n"
            elif "weaver" in name:
                mermaid += f"    B->>W: {name}\n"
                mermaid += f"    Note over W: {duration_ms:.1f}ms\n"
            elif "generation" in name or "python" in name:
                mermaid += f"    W->>G: {name}\n"
                mermaid += f"    Note over G: {duration_ms:.1f}ms\n"
            
            # Add attributes as notes
            attrs = span.get("attributes", {})
            if attrs:
                key_attrs = list(attrs.items())[:3]  # Show first 3 attributes
                for key, value in key_attrs:
                    mermaid += f"    Note right of B: {key}={value}\n"
        
        return mermaid


# CLI functions
async def capture_and_validate_spans():
    """Capture spans from a BPMN execution and validate them"""
    # Create capture system
    capture = SpanCaptureSystem()
    
    # Create some test spans
    with tracer.start_as_current_span("bpmn.execute.test") as span:
        span.set_attribute("bpmn.task.type", "service")
        span.set_attribute("bpmn.task.class", "TestTask")
        
        with tracer.start_as_current_span("weaver.initialize") as child:
            child.set_attribute("weaver.path", "/usr/local/bin/weaver")
            child.set_attribute("weaver.version", "0.1.0")
            
        with tracer.start_as_current_span("generation.python") as child:
            child.set_attribute("generation.target", "metrics")
            child.set_attribute("generation.language", "python")
    
    # Get captured spans
    spans = capture.get_captured_spans()
    
    # Validate spans
    validator = SpanValidator()
    result = validator.validate_spans(spans)
    
    # Generate reports
    reporter = SpanReportGenerator()
    
    # Show table report
    table = reporter.generate_table_report(result)
    console.print(table)
    
    # Show tree report
    tree = reporter.generate_tree_report(spans)
    console.print(tree)
    
    # Show mermaid
    mermaid = reporter.generate_mermaid_trace(spans)
    console.print("\n[bold cyan]Mermaid Trace:[/bold cyan]")
    console.print(mermaid)
    
    # Save spans
    span_file = Path("captured_spans.json")
    count = capture.save_spans(span_file)
    console.print(f"\n[green]✅ Saved {count} spans to {span_file}[/green]")
    
    return result


if __name__ == "__main__":
    asyncio.run(capture_and_validate_spans())