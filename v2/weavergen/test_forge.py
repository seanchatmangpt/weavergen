"""Test script for forge commands with span capture."""

import subprocess
import sys
from pathlib import Path
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# Set up OpenTelemetry
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "weavergen-forge-test",
    ResourceAttributes.SERVICE_VERSION: "1.0.0",
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

def run_command(cmd: str) -> tuple[int, str, str]:
    """Run a CLI command and capture output."""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print('='*60)
    
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


def main():
    """Test forge commands with span tracking."""
    
    with tracer.start_as_current_span("forge_test_suite") as span:
        
        # Test 1: List templates
        with tracer.start_as_current_span("test_templates_command"):
            code, out, err = run_command("uv run weavergen forge templates")
            span.set_attribute("command", "templates")
            span.set_attribute("exit_code", code)
        
        # Test 2: Validate semantic file
        with tracer.start_as_current_span("test_validate_command"):
            code, out, err = run_command("uv run weavergen forge validate test_semantic.yaml")
            span.set_attribute("command", "validate")
            span.set_attribute("exit_code", code)
            span.set_attribute("semantic_file", "test_semantic.yaml")
        
        # Test 3: Generate code (will likely fail without weaver binary)
        with tracer.start_as_current_span("test_generate_command"):
            code, out, err = run_command(
                "uv run weavergen forge generate test_semantic.yaml "
                "--output-dir generated_test --language python"
            )
            span.set_attribute("command", "generate")
            span.set_attribute("exit_code", code)
            span.set_attribute("language", "python")
        
        # Test 4: Full pipeline
        with tracer.start_as_current_span("test_full_pipeline_command"):
            code, out, err = run_command(
                "uv run weavergen forge full-pipeline test_semantic.yaml "
                "--agents 3 --output-dir pipeline_test"
            )
            span.set_attribute("command", "full_pipeline")
            span.set_attribute("exit_code", code)
            span.set_attribute("agents", 3)


if __name__ == "__main__":
    main()
    print("\n" + "="*60)
    print("Test completed - spans exported above")
    print("="*60)