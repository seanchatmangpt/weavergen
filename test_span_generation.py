"""Test script to generate spans for validation"""

import asyncio
from pathlib import Path
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
import json
import time

# Setup tracing
memory_exporter = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(memory_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


async def simulate_bpmn_weaver_execution():
    """Simulate a BPMN Weaver Forge execution with realistic spans"""
    
    # Main BPMN orchestration span
    with tracer.start_as_current_span("bpmn.execute.WeaverForgeOrchestration") as main_span:
        main_span.set_attribute("bpmn.workflow.name", "WeaverForgeOrchestration")
        main_span.set_attribute("bpmn.workflow.type", "weaver_forge")
        
        # Initialize Weaver
        with tracer.start_as_current_span("weaver.initialize") as span:
            span.set_attribute("weaver.path", "/usr/local/bin/weaver")
            span.set_attribute("weaver.version", "0.1.0")
            span.set_attribute("weaver.initialized", True)
            time.sleep(0.1)  # Simulate work
        
        # Load registry
        with tracer.start_as_current_span("weaver.load_registry") as span:
            span.set_attribute("registry.source", "semantic_conventions/weavergen_system.yaml")
            span.set_attribute("registry.files", 1)
            span.set_attribute("registry.groups", 5)
            time.sleep(0.05)
        
        # Validate registry
        with tracer.start_as_current_span("weaver.validate_registry") as span:
            span.set_attribute("weaver.command", "registry check")
            span.set_attribute("registry.valid", True)
            span.set_attribute("registry.check.returncode", 0)
            time.sleep(0.05)
        
        # Python generation subprocess
        with tracer.start_as_current_span("bpmn.execute.PythonForgeGeneration") as python_span:
            python_span.set_attribute("bpmn.subprocess", True)
            python_span.set_attribute("generation.language", "python")
            
            # Select templates
            with tracer.start_as_current_span("python.select_templates") as span:
                span.set_attribute("templates.count", 5)
                span.set_attribute("templates.type", "python")
                time.sleep(0.02)
            
            # Parallel generation of components
            tasks = []
            
            # Generate metrics
            with tracer.start_as_current_span("python.generate_metrics") as span:
                span.set_attribute("generation.target", "metrics")
                span.set_attribute("generation.language", "python")
                span.set_attribute("generation.success", True)
                span.set_attribute("generation.files", 3)
                time.sleep(0.1)
            
            # Generate attributes
            with tracer.start_as_current_span("python.generate_attributes") as span:
                span.set_attribute("generation.target", "attributes")
                span.set_attribute("generation.language", "python")
                span.set_attribute("generation.success", True)
                span.set_attribute("generation.files", 2)
                time.sleep(0.08)
            
            # Generate resources
            with tracer.start_as_current_span("python.generate_resources") as span:
                span.set_attribute("generation.target", "resources")
                span.set_attribute("generation.language", "python")
                span.set_attribute("generation.success", True)
                span.set_attribute("generation.files", 1)
                time.sleep(0.06)
            
            # Generate spans
            with tracer.start_as_current_span("python.generate_spans") as span:
                span.set_attribute("generation.target", "spans")
                span.set_attribute("generation.language", "python")
                span.set_attribute("generation.success", True)
                span.set_attribute("generation.files", 2)
                time.sleep(0.07)
        
        # Capture spans
        with tracer.start_as_current_span("weaver.capture_spans") as span:
            span.set_attribute("spans.captured", 12)
            span.set_attribute("spans.file", "generation_spans.json")
            time.sleep(0.03)
        
        # Validate generated code
        with tracer.start_as_current_span("weaver.validate_code") as span:
            span.set_attribute("validation.files", 8)
            span.set_attribute("validation.score", 0.95)
            span.set_attribute("validation.passed", True)
            time.sleep(0.05)
        
        # Generate report
        with tracer.start_as_current_span("weaver.span_report") as span:
            span.set_attribute("report.generated", True)
            span.set_attribute("report.components", 4)
            time.sleep(0.02)
    
    # Also create a validation workflow span tree
    with tracer.start_as_current_span("bpmn.execute.SpanValidationWorkflow") as val_span:
        val_span.set_attribute("bpmn.workflow.name", "SpanValidationWorkflow")
        
        with tracer.start_as_current_span("validation.collect_spans") as span:
            span.set_attribute("validation.method", "span")
            span.set_attribute("spans.collected", 15)
            time.sleep(0.02)
        
        with tracer.start_as_current_span("validation.analyze_hierarchy") as span:
            span.set_attribute("hierarchy.valid", True)
            span.set_attribute("hierarchy.depth", 3)
            time.sleep(0.03)
        
        # Parallel validation checks
        with tracer.start_as_current_span("validation.semantic_compliance") as span:
            span.set_attribute("validation.method", "semantic")
            span.set_attribute("compliance.score", 0.92)
            time.sleep(0.04)
        
        with tracer.start_as_current_span("validation.span_coverage") as span:
            span.set_attribute("validation.method", "coverage")
            span.set_attribute("coverage.score", 0.88)
            time.sleep(0.03)
        
        with tracer.start_as_current_span("validation.span_performance") as span:
            span.set_attribute("validation.method", "performance")
            span.set_attribute("performance.score", 0.95)
            time.sleep(0.02)
        
        with tracer.start_as_current_span("validation.health_score") as span:
            span.set_attribute("validation.score", 0.91)
            span.set_attribute("health.score", 0.91)
            span.set_attribute("validation.passed", True)
            time.sleep(0.01)


def export_spans():
    """Export captured spans to file"""
    # Force export of all spans
    provider.force_flush()
    spans = memory_exporter.get_finished_spans()
    
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
            "events": [],
            "resource": {}
        }
        span_dicts.append(span_dict)
    
    # Save to file
    output_dir = Path("bpmn_validation")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "test_spans.json", 'w') as f:
        json.dump(span_dicts, f, indent=2, default=str)
    
    print(f"Exported {len(span_dicts)} spans to {output_dir}/test_spans.json")
    return len(span_dicts)


async def main():
    """Generate test spans"""
    print("Generating test spans...")
    await simulate_bpmn_weaver_execution()
    count = export_spans()
    print(f"Generated {count} spans successfully!")


if __name__ == "__main__":
    asyncio.run(main())