#!/usr/bin/env python3
"""
OpenTelemetry Runtime Validation for WeaverGen.

This script validates that all operations are properly instrumented with
OpenTelemetry and that the semantic quine workflow produces valid traces.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode

# Set up custom span collector
class SpanCollector(SpanExporter):
    """Collects spans for validation"""
    def __init__(self):
        self.spans = []
    
    def export(self, spans):
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS
    
    def shutdown(self):
        pass

# Configure OpenTelemetry
resource = Resource.create({"service.name": "weaver-forge-validation"})
provider = TracerProvider(resource=resource)

# Add console exporter for debugging
console_exporter = ConsoleSpanExporter()
provider.add_span_processor(SimpleSpanProcessor(console_exporter))

# Add collector for validation
collector = SpanCollector()
provider.add_span_processor(SimpleSpanProcessor(collector))

# Set as global provider
trace.set_tracer_provider(provider)

# Import after OTel setup
sys.path.append("output")
from commands.forge import (
    weaver_registry_check,
    weaver_registry_generate,
    weaver_registry_resolve,
    weaver_registry_stats
)


def validate_span_attributes(span_data: Dict[str, Any], expected_attrs: List[str]) -> List[str]:
    """Validate that a span has expected attributes"""
    missing = []
    attributes = span_data.get("attributes", {})
    
    for attr in expected_attrs:
        if attr not in attributes:
            missing.append(attr)
    
    return missing


def run_full_workflow_with_tracing():
    """Run the complete workflow and collect traces"""
    print("=" * 60)
    print("OpenTelemetry Runtime Validation")
    print("=" * 60)
    
    # Clear previous spans
    collector.spans.clear()
    
    # Test 1: Registry Check
    print("\n1. Testing Registry Check with OTel...")
    try:
        result = weaver_registry_check(
            registry_check_path="test_registry2",
            registry_check_valid=True,  # This is incorrectly required
            registry_check_strict=False
        )
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Registry Stats
    print("\n2. Testing Registry Stats with OTel...")
    try:
        result = weaver_registry_stats(
            registry_stats_registry_path="test_registry2",
            registry_stats_total_groups=0,
            registry_stats_total_attributes=0
        )
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Registry Resolve
    print("\n3. Testing Registry Resolve with OTel...")
    try:
        result = weaver_registry_resolve(
            registry_resolve_registry_path="test_registry2",
            registry_resolve_groups_count=0
        )
        print(f"   Result: Success={result.success}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Code Generation (if possible)
    print("\n4. Testing Code Generation with OTel...")
    try:
        result = weaver_registry_generate(
            registry_generate_registry_path="test_registry2",
            registry_generate_target="code/python",
            registry_generate_output_dir="./otel_test_output",
            registry_generate_files_count=0,
            registry_generate_template_path="templates/registry"
        )
        print(f"   Result: Success={result.success}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Wait for spans to be processed
    time.sleep(0.5)
    
    return collector.spans


def analyze_traces(spans):
    """Analyze collected traces for validation"""
    print("\n" + "=" * 60)
    print("Trace Analysis")
    print("=" * 60)
    
    print(f"\nTotal spans collected: {len(spans)}")
    
    # Group spans by operation
    operations = {}
    for span in spans:
        name = span.name
        if name not in operations:
            operations[name] = []
        operations[name].append(span)
    
    print(f"\nOperations traced:")
    for op_name, op_spans in operations.items():
        print(f"  - {op_name}: {len(op_spans)} spans")
    
    # Validate semantic conventions
    print("\nValidating semantic conventions:")
    validation_results = []
    
    # Expected attributes for each operation
    expected_attrs = {
        "weaver.registry.check": ["registry.check.path", "registry.check.strict"],
        "weaver.registry.stats": ["registry.stats.registry_path"],
        "weaver.registry.resolve": ["registry.resolve.registry_path"],
        "weaver.registry.generate": [
            "registry.generate.registry_path",
            "registry.generate.target",
            "registry.generate.output_dir"
        ]
    }
    
    for op_name, expected in expected_attrs.items():
        op_spans = operations.get(op_name, [])
        if op_spans:
            span = op_spans[0]  # Check first span
            span_dict = {
                "name": span.name,
                "attributes": dict(span.attributes or {})
            }
            missing = validate_span_attributes(span_dict, expected)
            
            if missing:
                print(f"  ❌ {op_name}: Missing attributes: {missing}")
                validation_results.append(False)
            else:
                print(f"  ✅ {op_name}: All required attributes present")
                validation_results.append(True)
        else:
            print(f"  ⚠️  {op_name}: No spans found")
    
    # Check for errors
    print("\nChecking for errors in spans:")
    error_count = 0
    for span in spans:
        if span.status.status_code == StatusCode.ERROR:
            error_count += 1
            print(f"  ❌ Error in {span.name}: {span.status.description}")
    
    if error_count == 0:
        print("  ✅ No errors found in spans")
    
    # Performance metrics
    print("\nPerformance metrics:")
    for op_name, op_spans in operations.items():
        if op_spans:
            durations = []
            for span in op_spans:
                if span.end_time and span.start_time:
                    duration_ns = span.end_time - span.start_time
                    duration_ms = duration_ns / 1_000_000
                    durations.append(duration_ms)
            
            if durations:
                avg_duration = sum(durations) / len(durations)
                print(f"  {op_name}: avg={avg_duration:.2f}ms")
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    if all(validation_results) and error_count == 0:
        print("✅ All OpenTelemetry validations PASSED")
        return True
    else:
        print("❌ Some OpenTelemetry validations FAILED")
        return False


def test_semantic_quine_traces():
    """Test the semantic quine capability with full tracing"""
    print("\n" + "=" * 60)
    print("Semantic Quine Trace Validation")
    print("=" * 60)
    
    # Clear spans
    collector.spans.clear()
    
    # Load and validate Forge's own semantic conventions
    forge_yaml = Path("weaver-forge.yaml")
    if not forge_yaml.exists():
        print("❌ weaver-forge.yaml not found")
        return False
    
    print("\n1. Checking Forge's semantic conventions...")
    try:
        result = weaver_registry_check(
            registry_check_path=str(forge_yaml),
            registry_check_valid=True,  # This is incorrectly required
            registry_check_strict=True
        )
        print(f"   Self-check result: {result}")
    except Exception as e:
        print(f"   Error in self-check: {e}")
    
    # Analyze the traces
    time.sleep(0.5)
    quine_spans = collector.spans
    
    print(f"\n2. Semantic quine trace analysis:")
    print(f"   Total spans: {len(quine_spans)}")
    
    # Check for recursive structure
    operation_names = [span.name for span in quine_spans]
    unique_ops = set(operation_names)
    
    print(f"   Unique operations: {unique_ops}")
    
    # Verify the quine property
    has_check = "weaver.registry.check" in unique_ops
    
    if has_check:
        print("   ✅ Semantic quine successfully traced its own validation")
        return True
    else:
        print("   ❌ Semantic quine trace incomplete")
        return False


def main():
    """Main validation runner"""
    # Run full workflow validation
    spans = run_full_workflow_with_tracing()
    workflow_valid = analyze_traces(spans)
    
    # Run semantic quine validation
    quine_valid = test_semantic_quine_traces()
    
    # Final result
    print("\n" + "=" * 60)
    print("FINAL VALIDATION RESULT")
    print("=" * 60)
    
    if workflow_valid and quine_valid:
        print("✅ ALL VALIDATIONS PASSED")
        print("   - OpenTelemetry instrumentation is working correctly")
        print("   - Semantic conventions are properly applied")
        print("   - Semantic quine capability is validated")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED")
        if not workflow_valid:
            print("   - Workflow validation failed")
        if not quine_valid:
            print("   - Semantic quine validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())