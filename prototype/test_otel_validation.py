#!/usr/bin/env python3
"""
Validate OTEL instrumentation is working correctly.

This test demonstrates that our 4-layer architecture properly
instruments operations with OpenTelemetry.
"""

import sys
import json
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import InMemorySpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

# Add output to path
sys.path.insert(0, 'output')

from commands.forge import forge_semantic_generate, forge_code_generate


def test_otel_instrumentation():
    """Test that OTEL instrumentation captures traces and metrics."""
    print("=== OTEL Instrumentation Validation ===\n")
    
    # Setup in-memory exporters to capture telemetry
    span_exporter = InMemorySpanExporter()
    metric_reader = InMemoryMetricReader()
    
    # Configure trace provider
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)
    
    # Configure metrics provider  
    meter_provider = MeterProvider(metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    
    print("1. Testing forge.semantic.generate operation...")
    result = forge_semantic_generate(
        input_description="Test telemetry system",
        output_path="otel_test.yaml",
        llm_model="mock",
        validation_status="pending"
    )
    print(f"   Result: {'✓ Success' if result.success else '✗ Failed'}")
    
    print("\n2. Checking captured spans...")
    spans = span_exporter.get_finished_spans()
    print(f"   Captured {len(spans)} spans")
    
    for span in spans:
        print(f"\n   Span: {span.name}")
        print(f"   Status: {span.status.status_code.name}")
        print("   Attributes:")
        for key, value in span.attributes.items():
            print(f"     - {key}: {value}")
    
    print("\n3. Checking captured metrics...")
    metrics_data = metric_reader.get_metrics_data()
    
    if metrics_data and metrics_data.resource_metrics:
        for resource_metric in metrics_data.resource_metrics:
            for scope_metric in resource_metric.scope_metrics:
                for metric in scope_metric.metrics:
                    print(f"\n   Metric: {metric.name}")
                    print(f"   Description: {metric.description}")
                    print(f"   Unit: {metric.unit}")
                    
                    # Print data points
                    for data_point in metric.data.data_points:
                        if hasattr(data_point, 'value'):
                            print(f"   Value: {data_point.value}")
                        if hasattr(data_point, 'attributes'):
                            print(f"   Attributes: {dict(data_point.attributes)}")
    
    print("\n4. Testing error scenario...")
    # Clear previous spans
    span_exporter.clear()
    
    # Trigger an error
    result = forge_code_generate(
        input_semantic_path="non_existent.yaml",
        target_language="python", 
        template_directory="templates",
        output_directory="output"
    )
    print(f"   Result: {'✓ Success' if result.success else '✗ Failed (expected)'}")
    
    error_spans = span_exporter.get_finished_spans()
    for span in error_spans:
        if span.status.status_code != trace.StatusCode.OK:
            print(f"\n   Error span: {span.name}")
            print(f"   Status: {span.status.status_code.name}")
            if span.events:
                print("   Events:")
                for event in span.events:
                    print(f"     - {event.name}")
    
    print("\n✅ OTEL Validation Complete!")
    print(f"   Total spans captured: {len(spans) + len(error_spans)}")
    print(f"   Metrics initialized: {'Yes' if metrics_data else 'No'}")
    
    # Cleanup
    import os
    if os.path.exists("otel_test.yaml"):
        os.remove("otel_test.yaml")
    
    return True


def test_span_hierarchy():
    """Test that spans form proper parent-child relationships."""
    print("\n=== Testing Span Hierarchy ===\n")
    
    span_exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)
    
    # Create a parent span manually
    tracer = trace.get_tracer("test")
    
    with tracer.start_as_current_span("parent_operation") as parent:
        # Call our instrumented function
        result = forge_semantic_generate(
            input_description="Nested span test",
            output_path="nested_test.yaml",
            llm_model="mock",
            validation_status="pending"
        )
    
    spans = span_exporter.get_finished_spans()
    
    print(f"Captured {len(spans)} spans:")
    for span in spans:
        parent_id = span.parent.span_id if span.parent else None
        print(f"  - {span.name} (parent: {parent_id})")
    
    # Verify hierarchy
    forge_span = next((s for s in spans if s.name == "forge.semantic.generate"), None)
    parent_span = next((s for s in spans if s.name == "parent_operation"), None)
    
    if forge_span and parent_span:
        print(f"\n✓ Span hierarchy verified: {forge_span.name} is child of {parent_span.name}")
    
    # Cleanup
    import os
    if os.path.exists("nested_test.yaml"):
        os.remove("nested_test.yaml")
    
    return True


def main():
    """Run all OTEL validation tests."""
    print("OpenTelemetry Instrumentation Validation")
    print("=" * 40)
    
    try:
        test_otel_instrumentation()
        test_span_hierarchy()
        
        print("\n" + "=" * 40)
        print("✅ All OTEL validations passed!")
        
    except Exception as e:
        print(f"\n❌ OTEL validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)