"""Test forge commands and capture all spans."""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from commands.forge import _init_direct, _validate_semantics
import shutil
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# Set up comprehensive OpenTelemetry
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "forge-test",
    ResourceAttributes.SERVICE_VERSION: "2.0.0",
})

provider = TracerProvider(resource=resource)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Clean up
test_dir = Path("test_forge_output")
if test_dir.exists():
    shutil.rmtree(test_dir)

print("=" * 80)
print("TESTING FORGE COMMANDS WITH SPAN CAPTURE")
print("=" * 80)

# Test 1: Init command (direct implementation)
print("\n1. Testing forge init (direct implementation)...")
with tracer.start_as_current_span("test.forge.init_direct") as span:
    span.set_attribute("test.command", "init")
    span.set_attribute("test.registry_name", "TestRegistry")
    
    try:
        _init_direct("TestRegistry", test_dir, with_examples=True)
        span.set_attribute("test.result", "success")
        print("✓ Init completed successfully")
    except Exception as e:
        span.record_exception(e)
        span.set_attribute("test.result", "failed")
        print(f"✗ Init failed: {e}")

# Check created files
if test_dir.exists():
    print("\nCreated files:")
    for file in test_dir.rglob("*.yaml"):
        print(f"  • {file}")

# Test 2: Validate command
print("\n2. Testing forge validate...")
with tracer.start_as_current_span("test.forge.validate") as span:
    span.set_attribute("test.command", "validate")
    span.set_attribute("test.registry_path", str(test_dir))
    
    try:
        result = _validate_semantics(test_dir)
        span.set_attribute("test.valid", result.valid)
        span.set_attribute("test.errors", len(result.errors))
        span.set_attribute("test.warnings", len(result.warnings))
        
        if result.valid:
            print("✓ Validation passed")
        else:
            print(f"✗ Validation failed with {len(result.errors)} errors")
            for error in result.errors:
                print(f"    - {error}")
    except Exception as e:
        span.record_exception(e)
        print(f"✗ Validation error: {e}")

print("\n" + "=" * 80)
print("SPAN CAPTURE COMPLETE - See spans above")
print("=" * 80)