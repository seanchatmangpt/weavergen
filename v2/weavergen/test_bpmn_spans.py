"""Test BPMN forge execution with comprehensive span validation."""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from typer.testing import CliRunner
import commands
from commands.forge import forge_app
import shutil
import time
from collections import defaultdict

# Custom span collector
captured_spans = []

def capture_span(span_data):
    """Capture span data for analysis."""
    captured_spans.append(span_data)

# Monkey patch console exporter to capture spans
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
original_export = ConsoleSpanExporter.export

def capturing_export(self, spans):
    for span in spans:
        capture_span({
            'name': span.name,
            'status': span.status.status_code.name,
            'attributes': dict(span.attributes) if span.attributes else {},
            'duration_ms': (span.end_time - span.start_time) / 1_000_000 if span.end_time else 0,
            'parent': span.parent.span_id if span.parent else None,
            'events': [e.name for e in span.events] if span.events else []
        })
    return original_export(self, spans)

ConsoleSpanExporter.export = capturing_export

# Run test
runner = CliRunner()

# Clean up
test_dir = Path("test_bpmn_spans")
if test_dir.exists():
    shutil.rmtree(test_dir)

print("=" * 80)
print("TESTING BPMN FORGE INIT WITH SPAN VALIDATION")
print("=" * 80)

# Clear captured spans
captured_spans.clear()

# Test the init command
result = runner.invoke(forge_app, ["init", "BPMNTest", "--output-dir", "test_bpmn_spans"])

print(f"\nCommand exit code: {result.exit_code}")
print("\nCommand output:")
print("-" * 40)
print(result.output)
print("-" * 40)

# Give spans time to export
time.sleep(0.5)

# Analyze captured spans
print("\n" + "=" * 80)
print("SPAN ANALYSIS")
print("=" * 80)

# Group spans by type
span_types = defaultdict(list)
for span in captured_spans:
    span_type = span['name'].split('.')[0]
    span_types[span_type].append(span)

print("\nSpan Summary:")
for span_type, spans in sorted(span_types.items()):
    print(f"  {span_type}: {len(spans)} spans")

# Find BPMN-specific spans
bpmn_spans = [s for s in captured_spans if 'bpmn' in s['name'].lower() or 'workflow' in str(s.get('attributes', {})).lower()]
forge_spans = [s for s in captured_spans if 'forge' in s['name'].lower()]
service_spans = [s for s in captured_spans if 'forge.service' in s['name']]

print(f"\nBPMN-related spans: {len(bpmn_spans)}")
print(f"Forge command spans: {len(forge_spans)}")
print(f"Service task spans: {len(service_spans)}")

if service_spans:
    print("\nService Tasks Executed:")
    for span in service_spans:
        status = "✓" if span['status'] == "OK" else "✗"
        duration = f"{span['duration_ms']:.2f}ms" if span['duration_ms'] > 0 else "N/A"
        print(f"  {status} {span['name']} [{duration}]")

# Validate workflow completion
completion_span = next((s for s in captured_spans if s.get('attributes', {}).get('workflow.completed')), None)
if completion_span:
    print("\n✓ BPMN workflow completed successfully!")
else:
    print("\n✗ No workflow completion detected")

# Check for errors
error_spans = [s for s in captured_spans if s['status'] not in ['OK', 'UNSET']]
if error_spans:
    print(f"\n⚠️  Found {len(error_spans)} error spans:")
    for span in error_spans:
        print(f"  - {span['name']}: {span['status']}")

# Check created files
if test_dir.exists():
    print("\nCreated files:")
    for file in test_dir.rglob("*.yaml"):
        print(f"  ✓ {file}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)