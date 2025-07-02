"""Test BPMN-first forge commands with comprehensive span capture."""

import subprocess
import sys
import json
from pathlib import Path
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from typing import Sequence
import time

# Custom span collector
class SpanCollector(SpanExporter):
    """Collect all spans for analysis."""
    def __init__(self):
        self.spans = []
    
    def export(self, spans: Sequence) -> SpanExportResult:
        for span in spans:
            self.spans.append({
                'name': span.name,
                'trace_id': f"0x{span.context.trace_id:032x}",
                'span_id': f"0x{span.context.span_id:016x}",
                'parent_id': f"0x{span.parent.span_id:016x}" if span.parent else None,
                'start_time': span.start_time,
                'end_time': span.end_time,
                'duration_ms': (span.end_time - span.start_time) / 1_000_000 if span.end_time else 0,
                'status': span.status.status_code.name,
                'attributes': dict(span.attributes) if span.attributes else {},
                'events': [{'name': e.name, 'attributes': dict(e.attributes) if e.attributes else {}} for e in span.events] if span.events else []
            })
        return SpanExportResult.SUCCESS

# Set up OpenTelemetry with custom collector
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "weavergen-bpmn-test",
    ResourceAttributes.SERVICE_VERSION: "2.0.0",
})

provider = TracerProvider(resource=resource)
collector = SpanCollector()
provider.add_span_processor(SimpleSpanProcessor(collector))
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

def run_command(cmd: str) -> tuple[int, str, str]:
    """Run a CLI command and capture output."""
    print(f"\n{'='*80}")
    print(f"Running: {cmd}")
    print('='*80)
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode, result.stdout, result.stderr


def print_span_hierarchy(spans):
    """Print spans in a hierarchical tree structure."""
    print("\n" + "="*80)
    print("SPAN HIERARCHY")
    print("="*80)
    
    # Build parent-child relationships
    root_spans = []
    child_map = {}
    
    for span in spans:
        if span['parent_id'] is None:
            root_spans.append(span)
        else:
            if span['parent_id'] not in child_map:
                child_map[span['parent_id']] = []
            child_map[span['parent_id']].append(span)
    
    def print_span_tree(span, indent=0):
        prefix = "  " * indent + "└─" if indent > 0 else ""
        duration = f"{span['duration_ms']:.2f}ms" if span['duration_ms'] > 0 else "N/A"
        status = "✓" if span['status'] == "OK" else "✗"
        
        print(f"{prefix}{status} {span['name']} [{duration}]")
        
        # Print key attributes
        if span['attributes']:
            for key, value in span['attributes'].items():
                if key in ['registry_name', 'workflow', 'bpmn.task.name', 'cli.command']:
                    print(f"{'  ' * (indent + 1)}  {key}: {value}")
        
        # Print child spans
        if span['span_id'] in child_map:
            for child in sorted(child_map[span['span_id']], key=lambda x: x['start_time']):
                print_span_tree(child, indent + 1)
    
    # Print all root spans
    for root in sorted(root_spans, key=lambda x: x['start_time']):
        print_span_tree(root)


def main():
    """Test BPMN forge commands with span tracking."""
    
    # Clean up any existing test registry
    test_dir = Path("test_bpmn_registry")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    # Test 1: BPMN-orchestrated init command
    print("\n" + "="*80)
    print("TEST: BPMN-FIRST FORGE INIT")
    print("="*80)
    
    code, out, err = run_command(
        "uv run weavergen forge init TestApp --output-dir test_bpmn_registry"
    )
    
    # Give spans time to export
    time.sleep(0.5)
    
    # Analyze collected spans
    print_span_hierarchy(collector.spans)
    
    # Check if files were created
    if test_dir.exists():
        print("\n" + "="*80)
        print("CREATED FILES")
        print("="*80)
        for file in test_dir.rglob("*.yaml"):
            print(f"  ✓ {file}")
    
    # Test 2: Validate the created registry
    if code == 0:
        print("\n" + "="*80)
        print("TEST: VALIDATE CREATED REGISTRY")
        print("="*80)
        
        # Clear previous spans
        collector.spans.clear()
        
        code2, out2, err2 = run_command(
            f"uv run weavergen forge validate test_bpmn_registry"
        )
        
        time.sleep(0.5)
        print_span_hierarchy(collector.spans)
    
    # Summary of BPMN execution
    print("\n" + "="*80)
    print("BPMN EXECUTION SUMMARY")
    print("="*80)
    
    # Count span types
    span_types = {}
    for span in collector.spans:
        span_type = span['name'].split('.')[0]
        span_types[span_type] = span_types.get(span_type, 0) + 1
    
    print("Span Categories:")
    for span_type, count in sorted(span_types.items()):
        print(f"  {span_type}: {count} spans")
    
    # Find BPMN-specific spans
    bpmn_spans = [s for s in collector.spans if 'bpmn' in s['name'].lower() or 'workflow' in str(s['attributes']).lower()]
    print(f"\nBPMN-related spans: {len(bpmn_spans)}")
    
    # Find service task spans
    service_spans = [s for s in collector.spans if 'forge.service' in s['name']]
    print(f"Service task spans: {len(service_spans)}")
    
    if service_spans:
        print("\nService Tasks Executed:")
        for span in service_spans:
            print(f"  • {span['name']} [{span['duration_ms']:.2f}ms]")


if __name__ == "__main__":
    main()