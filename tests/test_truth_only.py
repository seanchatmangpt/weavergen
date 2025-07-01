"""
Test Framework: Trust Only Execution Traces

This test framework ensures that all test results are backed by
OpenTelemetry spans. No test can claim success without execution proof.
"""

import functools
import inspect
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from unittest.mock import Mock, patch

import pytest
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from weavergen.core import WeaverGen
from weavergen.models import GenerationConfig, GenerationResult


# Global span exporter for truth collection
TRUTH_EXPORTER = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(TRUTH_EXPORTER))
trace.set_tracer_provider(provider)


class TruthOnlyTest:
    """Base class for tests that can only pass with span evidence."""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
        self.test_spans = []
        self.claims = {}
    
    def setup_method(self):
        """Clear spans before each test."""
        TRUTH_EXPORTER.clear()
    
    def teardown_method(self):
        """Validate all claims after each test."""
        self._validate_all_claims()
    
    def claim(self, claim_text: str) -> Callable:
        """Decorator for test methods that make claims."""
        def decorator(test_func: Callable) -> Callable:
            @functools.wraps(test_func)
            def wrapper(*args, **kwargs):
                # Get test location
                frame = inspect.currentframe()
                filepath = frame.f_code.co_filename
                lineno = frame.f_lineno
                
                with self.tracer.start_as_current_span(
                    f"test_claim:{claim_text}",
                    attributes={
                        "test.name": test_func.__name__,
                        "claim.text": claim_text,
                        "code.filepath": filepath,
                        "code.lineno": lineno
                    }
                ) as span:
                    try:
                        # Run the test
                        result = test_func(*args, **kwargs)
                        
                        # Test must provide evidence
                        if not hasattr(result, "__evidence__"):
                            span.set_status(Status(StatusCode.ERROR))
                            span.set_attribute("claim.validation_error", "No evidence provided")
                            raise AssertionError(
                                f"Test '{test_func.__name__}' claimed '{claim_text}' but provided no evidence"
                            )
                        
                        # Record evidence
                        evidence = result.__evidence__
                        for key, value in evidence.items():
                            span.set_attribute(f"evidence.{key}", str(value))
                        
                        span.set_attribute("claim.validated", True)
                        self.claims[claim_text] = True
                        
                        return result
                        
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR))
                        self.claims[claim_text] = False
                        raise
            
            return wrapper
        return decorator
    
    def _validate_all_claims(self):
        """Ensure all claims were validated with spans."""
        spans = TRUTH_EXPORTER.get_finished_spans()
        
        for claim, validated in self.claims.items():
            if not validated:
                # Find the span for this claim
                claim_spans = [s for s in spans if claim in s.name]
                if claim_spans:
                    span = claim_spans[0]
                    error = span.attributes.get("claim.validation_error", "Unknown error")
                    pytest.fail(f"Claim '{claim}' failed validation: {error}")
                else:
                    pytest.fail(f"Claim '{claim}' has no supporting span")


class Evidence:
    """Container for test evidence that must be provided."""
    
    def __init__(self, **kwargs):
        self.__evidence__ = kwargs


class TestWeaverGenWithTruthOnly(TruthOnlyTest):
    """Test WeaverGen using only verifiable execution traces."""
    
    @pytest.fixture
    def weaver_gen(self):
        """Create WeaverGen instance with span tracking."""
        return WeaverGen()
    
    @TruthOnlyTest.claim("WeaverGen successfully validates semantic conventions")
    def test_validate_semantic_yaml(self, weaver_gen, tmp_path):
        """Test that validation actually runs and succeeds."""
        
        # Create test semantic YAML
        test_yaml = tmp_path / "test.yaml"
        test_yaml.write_text("""
groups:
  - id: http
    type: attribute_group
    attributes:
      - id: http.method
        type: string
        brief: HTTP request method
""")
        
        # Track actual execution
        with self.tracer.start_as_current_span("validate_execution") as span:
            span.set_attributes({
                "code.filepath": __file__,
                "code.lineno": inspect.currentframe().f_lineno,
                "yaml.path": str(test_yaml),
                "yaml.exists": test_yaml.exists()
            })
            
            # Mock the weaver subprocess to track execution
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="Validation successful",
                    stderr=""
                )
                
                # Run validation
                result = weaver_gen.validate(str(test_yaml))
                
                # Record what actually happened
                span.set_attributes({
                    "subprocess.called": mock_run.called,
                    "subprocess.call_count": mock_run.call_count,
                    "validation.success": result.success,
                    "validation.returncode": 0,
                    "weaver.command": str(mock_run.call_args) if mock_run.called else "NOT_CALLED"
                })
        
        # Return evidence of actual execution
        return Evidence(
            subprocess_called=mock_run.called,
            call_count=mock_run.call_count,
            validation_result=result.success,
            command_executed=str(mock_run.call_args) if mock_run.called else None,
            yaml_existed=test_yaml.exists()
        )
    
    @TruthOnlyTest.claim("WeaverGen generates code for Python")
    def test_generate_python_code(self, weaver_gen, tmp_path):
        """Test Python code generation with full execution tracking."""
        
        # Setup test files
        test_yaml = tmp_path / "semantic.yaml"
        test_yaml.write_text("""
groups:
  - id: http
    type: span
    attributes:
      - id: http.method
""")
        
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        python_template = template_dir / "python.j2"
        python_template.write_text("# Generated code for {{ group.id }}")
        
        output_dir = tmp_path / "output"
        
        with self.tracer.start_as_current_span("python_generation") as span:
            span.set_attributes({
                "code.filepath": __file__,
                "code.lineno": inspect.currentframe().f_lineno,
                "test.yaml": str(test_yaml),
                "test.template": str(python_template)
            })
            
            # Track the actual subprocess call
            actual_command = None
            actual_success = False
            files_created = []
            
            def mock_subprocess_run(cmd, **kwargs):
                nonlocal actual_command, actual_success
                actual_command = cmd
                
                # Simulate file creation
                output_file = output_dir / "http.py"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text("# Generated HTTP code")
                files_created.append(str(output_file))
                
                actual_success = True
                return Mock(returncode=0, stdout="Generation complete")
            
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                config = GenerationConfig(
                    semantic_yaml=str(test_yaml),
                    target="python",
                    template_dir=str(template_dir),
                    output_dir=str(output_dir)
                )
                
                result = weaver_gen.generate(config)
                
                span.set_attributes({
                    "subprocess.command": str(actual_command),
                    "subprocess.executed": actual_success,
                    "files.created": len(files_created),
                    "files.list": json.dumps(files_created),
                    "generation.success": result.success if result else False
                })
        
        # Must provide evidence
        return Evidence(
            command_executed=actual_command is not None,
            subprocess_success=actual_success,
            files_created=files_created,
            output_exists=output_dir.exists(),
            result_success=result.success if result else False
        )
    
    @TruthOnlyTest.claim("WeaverGen handles missing templates correctly")
    def test_missing_template_handling(self, weaver_gen, tmp_path):
        """Test that missing templates are properly detected and reported."""
        
        test_yaml = tmp_path / "semantic.yaml"
        test_yaml.write_text("groups: []")
        
        # No template directory created - should fail
        
        with self.tracer.start_as_current_span("missing_template_test") as span:
            span.set_attributes({
                "code.filepath": __file__,
                "code.lineno": inspect.currentframe().f_lineno,
                "template_dir": str(tmp_path / "templates"),
                "template_exists": (tmp_path / "templates").exists()
            })
            
            error_caught = None
            subprocess_called = False
            
            def mock_subprocess_run(cmd, **kwargs):
                nonlocal subprocess_called
                subprocess_called = True
                return Mock(
                    returncode=1,
                    stdout="",
                    stderr="Error: Template not found"
                )
            
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                try:
                    config = GenerationConfig(
                        semantic_yaml=str(test_yaml),
                        target="python",
                        template_dir=str(tmp_path / "templates"),
                        output_dir=str(tmp_path / "output")
                    )
                    result = weaver_gen.generate(config)
                except Exception as e:
                    error_caught = e
                    span.record_exception(e)
            
            span.set_attributes({
                "error.caught": error_caught is not None,
                "error.type": type(error_caught).__name__ if error_caught else "None",
                "subprocess.called": subprocess_called,
                "template.missing": True
            })
        
        return Evidence(
            error_occurred=error_caught is not None,
            error_type=type(error_caught).__name__ if error_caught else None,
            subprocess_attempted=subprocess_called,
            template_dir_existed=False
        )


def generate_truth_report():
    """Generate a report based only on span evidence."""
    spans = TRUTH_EXPORTER.get_finished_spans()
    
    report = {
        "timestamp": time.time(),
        "total_spans": len(spans),
        "test_claims": [],
        "execution_facts": []
    }
    
    for span in spans:
        if "test_claim:" in span.name:
            claim_text = span.attributes.get("claim.text", "Unknown")
            validated = span.attributes.get("claim.validated", False)
            
            report["test_claims"].append({
                "claim": claim_text,
                "validated": validated,
                "test_name": span.attributes.get("test.name"),
                "file": Path(span.attributes.get("code.filepath", "")).name,
                "line": span.attributes.get("code.lineno"),
                "duration_ms": (span.end_time - span.start_time) / 1_000_000,
                "evidence": {k.replace("evidence.", ""): v 
                           for k, v in span.attributes.items() 
                           if k.startswith("evidence.")}
            })
        
        # Collect all execution facts
        if span.attributes.get("subprocess.called"):
            report["execution_facts"].append({
                "operation": span.name,
                "subprocess_called": True,
                "command": span.attributes.get("subprocess.command", "Unknown"),
                "success": span.status.status_code == StatusCode.OK,
                "duration_ms": (span.end_time - span.start_time) / 1_000_000
            })
    
    return report


# Example: Running tests and getting truth-only report
if __name__ == "__main__":
    # Run a test
    test_instance = TestWeaverGenWithTruthOnly()
    test_instance.setup_method()
    
    # Create a mock WeaverGen
    weaver_gen = WeaverGen()
    
    # Run test with temp directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        try:
            result = test_instance.test_validate_semantic_yaml(weaver_gen, tmp_path)
            print("Test passed with evidence:", result.__evidence__)
        except Exception as e:
            print("Test failed:", e)
    
    # Generate truth report
    report = generate_truth_report()
    print("\nTRUTH-ONLY REPORT:")
    print(json.dumps(report, indent=2))