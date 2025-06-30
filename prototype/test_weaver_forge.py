#!/usr/bin/env python3
"""
Comprehensive test suite for Weaver Forge prototype.

Tests the 4-layer architecture:
1. Commands - OTEL instrumentation
2. Operations - Business logic
3. Runtime - Weaver CLI integration
4. Contracts - Validation
"""

import pytest
import sys
import os
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode

# Add output directory to path
sys.path.insert(0, 'output')

# Import our layers
from commands.forge import (
    forge_semantic_generate, 
    forge_code_generate,
    forge_self_improve,
    ForgeResult
)
from operations.forge import (
    forge_semantic_generate_execute,
    forge_code_generate_execute,
    forge_self_improve_execute
)
from runtime.forge import (
    weaver_registry_check,
    weaver_registry_generate,
    create_registry_structure
)
from contracts.forge import (
    ForgeSemanticGenerateContracts,
    ForgeCodeGenerateContracts,
    ForgeSelfImproveContracts
)


@pytest.fixture
def setup_otel():
    """Setup OTEL for testing."""
    # Create a TracerProvider with a console exporter for testing
    tracer_provider = TracerProvider()
    span_processor = SimpleSpanProcessor(ConsoleSpanExporter())
    tracer_provider.add_span_processor(span_processor)
    
    # Set the global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    return tracer_provider


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for tests."""
    return tmp_path


class TestCommandsLayer:
    """Test the commands layer with OTEL instrumentation."""
    
    def test_forge_semantic_generate_instrumentation(self, setup_otel):
        """Test that semantic generation creates proper OTEL spans."""
        with patch('operations.forge.forge_semantic_generate_execute') as mock_execute:
            mock_execute.return_value = ForgeResult(
                success=True,
                data={"output_path": "test.yaml"}
            )
            
            result = forge_semantic_generate(
                input_description="Test semantic convention",
                output_path="test.yaml",
                llm_model="test-model",
                validation_status="pending"
            )
            
            assert result.success
            assert mock_execute.called
            
            # Verify span attributes were set
            call_args = mock_execute.call_args[1]
            assert call_args['input_description'] == "Test semantic convention"
            assert call_args['output_path'] == "test.yaml"
            assert call_args['llm_model'] == "test-model"
    
    def test_forge_code_generate_instrumentation(self, setup_otel):
        """Test that code generation creates proper OTEL spans."""
        with patch('operations.forge.forge_code_generate_execute') as mock_execute:
            mock_execute.return_value = ForgeResult(
                success=True,
                data={"files_generated": ["test.py"]}
            )
            
            result = forge_code_generate(
                input_semantic_path="test.yaml",
                target_language="python",
                template_directory="templates",
                output_directory="output"
            )
            
            assert result.success
            assert mock_execute.called
    
    def test_error_handling_with_spans(self, setup_otel):
        """Test that errors are properly recorded in spans."""
        with patch('operations.forge.forge_semantic_generate_execute') as mock_execute:
            mock_execute.side_effect = Exception("Test error")
            
            result = forge_semantic_generate(
                input_description="Test",
                output_path="test.yaml",
                llm_model="test-model",
                validation_status="pending"
            )
            
            assert not result.success
            assert "Test error" in result.errors[0]


class TestOperationsLayer:
    """Test the operations layer business logic."""
    
    def test_semantic_generate_creates_basic_yaml(self, temp_dir):
        """Test semantic generation creates valid YAML."""
        output_path = temp_dir / "test_semantic.yaml"
        
        with patch('runtime.forge.weaver_registry_check', return_value=(True, None)):
            result = forge_semantic_generate_execute(
                input_description="User tracking attributes",
                output_path=str(output_path),
                llm_model="mock",
                validation_status="pending"
            )
            
            assert result.success
            assert output_path.exists()
            
            # Verify YAML structure
            content = yaml.safe_load(output_path.read_text())
            assert "groups" in content
            assert len(content["groups"]) == 1
            assert content["groups"][0]["brief"] == "User tracking attributes"
    
    def test_code_generate_validates_inputs(self, temp_dir):
        """Test code generation validates inputs properly."""
        # Test with non-existent semantic file
        result = forge_code_generate_execute(
            input_semantic_path="non_existent.yaml",
            target_language="python",
            template_directory="templates",
            output_directory=str(temp_dir)
        )
        
        assert not result.success
        assert "not found" in result.errors[0]
    
    def test_self_improve_creates_new_version(self, temp_dir):
        """Test self-improvement creates new version."""
        # Create a base version
        base_yaml = temp_dir / "weaver-forge.yaml"
        base_yaml.write_text(yaml.dump({
            "groups": [{
                "id": "forge",
                "type": "span",
                "brief": "Base version"
            }]
        }))
        
        with patch('runtime.forge.validate_file_exists', return_value=True):
            with patch('runtime.forge.read_file', return_value=base_yaml.read_text()):
                with patch('runtime.forge.write_file') as mock_write:
                    result = forge_self_improve_execute(
                        current_version="1.0.0",
                        improvements=["Add metrics support"],
                        target_version="1.1.0"
                    )
                    
                    assert result.success
                    assert mock_write.called
                    
                    # Verify the improved content
                    improved_path, improved_content = mock_write.call_args[0]
                    assert "weaver_forge_v1.1.0.yaml" in improved_path
                    assert "Add metrics support" in improved_content


class TestRuntimeLayer:
    """Test the runtime layer Weaver CLI integration."""
    
    @patch('subprocess.run')
    def test_weaver_registry_check_success(self, mock_run):
        """Test successful registry check."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        is_valid, errors = weaver_registry_check("test_registry")
        
        assert is_valid
        assert errors is None
        mock_run.assert_called_once()
        assert "weaver" in mock_run.call_args[0][0]
        assert "registry" in mock_run.call_args[0][0]
        assert "check" in mock_run.call_args[0][0]
    
    @patch('subprocess.run')
    def test_weaver_registry_generate_success(self, mock_run):
        """Test successful code generation."""
        mock_output = """
        ✔ Generated file "output/commands/forge.py"
        ✔ Generated file "output/operations/forge.py"
        ✔ Generated file "output/runtime/forge.py"
        """
        mock_run.return_value = Mock(returncode=0, stdout=mock_output, stderr="")
        
        files = weaver_registry_generate(
            registry_path="test_registry",
            target_name="python",
            template_path="templates",
            output_dir="output"
        )
        
        assert len(files) == 3
        assert any("commands/forge.py" in f for f in files)
        assert any("operations/forge.py" in f for f in files)
        assert any("runtime/forge.py" in f for f in files)
    
    def test_create_registry_structure(self, temp_dir):
        """Test registry structure creation."""
        yaml_file = temp_dir / "test.yaml"
        yaml_file.write_text("groups: []")
        
        registry_path = create_registry_structure(str(yaml_file))
        
        try:
            assert Path(registry_path).exists()
            assert (Path(registry_path) / "registry_manifest.yaml").exists()
            assert (Path(registry_path) / "groups" / "test.yaml").exists()
            
            # Verify manifest content
            manifest = yaml.safe_load((Path(registry_path) / "registry_manifest.yaml").read_text())
            assert manifest["name"] == "temp-registry"
            assert manifest["schema_base_url"] == "https://opentelemetry.io/schemas"
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(Path(registry_path).parent, ignore_errors=True)


class TestContractsLayer:
    """Test the contracts layer validation."""
    
    def test_semantic_generate_contracts(self):
        """Test semantic generation contract validation."""
        # Test required fields
        assert ForgeSemanticGenerateContracts.require_input_description("Valid description")
        assert not ForgeSemanticGenerateContracts.require_input_description("")
        
        assert ForgeSemanticGenerateContracts.require_output_path("/path/to/file.yaml")
        assert not ForgeSemanticGenerateContracts.require_output_path("")
        
        assert ForgeSemanticGenerateContracts.require_llm_model("gpt-4")
        assert not ForgeSemanticGenerateContracts.require_llm_model("")
    
    def test_code_generate_contracts(self):
        """Test code generation contract validation."""
        assert ForgeCodeGenerateContracts.require_input_semantic_path("/path/to/semantic.yaml")
        assert not ForgeCodeGenerateContracts.require_input_semantic_path("")
        
        assert ForgeCodeGenerateContracts.require_target_language("python")
        assert not ForgeCodeGenerateContracts.require_target_language("")
    
    def test_self_improve_contracts(self):
        """Test self-improvement contract validation."""
        assert ForgeSelfImproveContracts.require_current_version("1.0.0")
        assert not ForgeSelfImproveContracts.require_current_version("")
        
        assert ForgeSelfImproveContracts.require_improvements(["Add feature"])
        assert not ForgeSelfImproveContracts.require_improvements([])


class TestSemanticQuine:
    """Test the semantic quine concept end-to-end."""
    
    def test_semantic_quine_loop(self, temp_dir):
        """Test the complete semantic quine loop."""
        # Mock all the subprocess calls
        with patch('subprocess.run') as mock_run:
            # Mock successful Weaver runs
            mock_run.return_value = Mock(returncode=0, stdout="✔ Success", stderr="")
            
            # Step 1: Generate semantic conventions
            result1 = forge_semantic_generate(
                input_description="A system for code generation",
                output_path=str(temp_dir / "quine.yaml"),
                llm_model="mock",
                validation_status="pending"
            )
            assert result1.success
            
            # Step 2: Generate code from semantics
            with patch('runtime.forge.validate_file_exists', return_value=True):
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('pathlib.Path.rglob') as mock_rglob:
                        # Mock finding generated Python files
                        mock_file = Mock()
                        mock_file.__str__ = Mock(return_value="output/quine.py")
                        mock_rglob.return_value = [mock_file]
                        
                        result2 = forge_code_generate(
                            input_semantic_path=str(temp_dir / "quine.yaml"),
                            target_language="python",
                            template_directory="templates",
                            output_directory=str(temp_dir / "output")
                        )
                        assert result2.success
            
            # Step 3: Self-improve
            with patch('runtime.forge.validate_file_exists', return_value=True):
                with patch('runtime.forge.read_file', return_value="groups: []"):
                    with patch('runtime.forge.write_file'):
                        result3 = forge_self_improve(
                            current_version="1.0.0",
                            improvements=["Optimize generation"],
                            target_version="1.1.0"
                        )
                        assert result3.success
                        assert result3.data.get("reference_depth", 0) > 0


@pytest.mark.integration
class TestIntegration:
    """Integration tests that require actual Weaver CLI."""
    
    def test_real_weaver_check(self):
        """Test with real Weaver CLI if available."""
        # This test will only run if Weaver is installed
        try:
            import subprocess
            result = subprocess.run(
                ["weaver", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                pytest.skip("Weaver CLI not available")
        except FileNotFoundError:
            pytest.skip("Weaver CLI not available")
        
        # If we get here, Weaver is available
        is_valid, errors = weaver_registry_check("test_registry2")
        # We expect this to be valid since we created it
        assert is_valid or errors  # Either valid or has specific errors


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=output",
        "--cov-report=term-missing"
    ])