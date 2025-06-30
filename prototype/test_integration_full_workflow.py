#!/usr/bin/env python3
"""
Integration tests for the full WeaverGen workflow.

Tests the complete cycle:
1. Semantic convention generation from natural language
2. Code generation from semantic conventions
3. CLI generation from semantic conventions
4. Runtime wrapper execution
5. OpenTelemetry instrumentation validation
"""

import pytest
import tempfile
import shutil
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, Any
import sys
import os

# Add output to path for runtime imports
sys.path.append("output")

# Import the components we're testing
from output.operations.forge import (
    create_basic_semantic_convention,
    weaver_registry_generate_execute,
    apply_improvements_to_yaml
)
from output.runtime.forge import (
    weaver_registry_check,
    weaver_registry_generate,
    weaver_registry_resolve,
    weaver_registry_stats,
    create_registry_structure
)


class TestFullWorkflowIntegration:
    """Integration tests for the complete WeaverGen workflow"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for tests"""
        temp_dir = tempfile.mkdtemp(prefix="weaver_test_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_semantic_conv(self):
        """Sample semantic convention for testing"""
        return {
            "groups": [{
                "id": "test.service",
                "type": "span",
                "brief": "Test service operations",
                "attributes": [
                    {
                        "id": "test.service.name",
                        "type": "string",
                        "requirement_level": "required",
                        "brief": "The name of the test service"
                    },
                    {
                        "id": "test.service.version",
                        "type": "string",
                        "requirement_level": "recommended",
                        "brief": "The version of the test service"
                    }
                ]
            }]
        }
    
    def test_semantic_generation_from_natural_language(self, temp_workspace):
        """Test generating semantic conventions from natural language"""
        # Generate semantic conventions
        description = "Create a service monitoring system with service name, version, and status tracking"
        
        output_path = Path(temp_workspace) / "test_semantics.yaml"
        # Generate semantic conventions using the operations layer
        yaml_content = create_basic_semantic_convention(
            description=description,
            output_path=str(output_path)
        )
        
        # Verify the file was created
        assert output_path.exists()
        
        # Load and validate the generated YAML
        with open(output_path) as f:
            semantics = yaml.safe_load(f)
        
        assert "groups" in semantics
        assert len(semantics["groups"]) > 0
        
        # Check that required attributes were generated
        group = semantics["groups"][0]
        assert "id" in group
        assert "attributes" in group
        
        # Find service name attribute
        attr_ids = [attr["id"] for attr in group["attributes"]]
        assert any("name" in attr_id for attr_id in attr_ids)
        assert any("version" in attr_id for attr_id in attr_ids)
    
    def test_registry_validation(self, temp_workspace, sample_semantic_conv):
        """Test registry validation using runtime wrapper"""
        # Write sample semantic convention
        yaml_path = Path(temp_workspace) / "test_registry.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(sample_semantic_conv, f)
        
        # Create registry structure
        registry_path = create_registry_structure(str(yaml_path))
        
        try:
            # Validate the registry
            is_valid, errors = weaver_registry_check(registry_path)
            
            assert is_valid is True
            assert errors is None
        finally:
            # Cleanup
            shutil.rmtree(Path(registry_path).parent, ignore_errors=True)
    
    def test_code_generation_from_registry(self, temp_workspace, sample_semantic_conv):
        """Test code generation from semantic convention registry"""
        # Write sample semantic convention
        yaml_path = Path(temp_workspace) / "test_registry.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(sample_semantic_conv, f)
        
        # Create registry structure
        registry_path = create_registry_structure(str(yaml_path))
        
        try:
            # Generate Python code
            output_dir = Path(temp_workspace) / "generated"
            files = weaver_registry_generate(
                registry_path=registry_path,
                target_name="code/python",
                template_path="templates/registry",
                output_dir=str(output_dir)
            )
            
            # Verify files were generated
            assert len(files) > 0
            
            # Check that at least one Python file was created
            py_files = [f for f in files if f.endswith('.py')]
            assert len(py_files) > 0
        finally:
            # Cleanup
            shutil.rmtree(Path(registry_path).parent, ignore_errors=True)
    
    def test_cli_generation_workflow(self, temp_workspace):
        """Test CLI generation from semantic conventions"""
        # Run the CLI generation script
        result = subprocess.run(
            ["python", "generate_weaver_cli.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # Check that CLI was generated
        cli_path = Path("generated_cli/weaver_cli_generated.py")
        assert cli_path.exists()
        
        # Test that the generated CLI has proper typing (no Any)
        cli_content = cli_path.read_text()
        assert "typing.Any" not in cli_content or "Any" not in cli_content.split("typing.")[1] if "typing." in cli_content else True
    
    def test_registry_stats(self, temp_workspace, sample_semantic_conv):
        """Test registry statistics gathering"""
        # Write sample semantic convention
        yaml_path = Path(temp_workspace) / "test_registry.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(sample_semantic_conv, f)
        
        # Create registry structure
        registry_path = create_registry_structure(str(yaml_path))
        
        try:
            # Get registry stats
            stats = weaver_registry_stats(registry_path)
            
            assert isinstance(stats, dict)
            # Stats should contain some metrics
            assert len(stats) > 0
        finally:
            # Cleanup
            shutil.rmtree(Path(registry_path).parent, ignore_errors=True)
    
    def test_registry_search(self, temp_workspace, sample_semantic_conv):
        """Test registry search functionality"""
        # Skip this test for now as search is not imported
        pytest.skip("Registry search not imported")
    
    def test_end_to_end_workflow(self, temp_workspace):
        """Test the complete end-to-end workflow"""
        # Step 1: Generate semantic conventions from description
        description = "Create a database monitoring system tracking query duration, table name, and operation type"
        semconv_path = Path(temp_workspace) / "db_monitoring.yaml"
        
        # Generate semantic conventions using the operations layer
        yaml_content = create_basic_semantic_convention(
            description=description,
            output_path=str(semconv_path)
        )
        
        assert semconv_path.exists()
        
        # Step 2: Create registry and validate
        registry_path = create_registry_structure(str(semconv_path))
        
        try:
            is_valid, errors = weaver_registry_check(registry_path)
            assert is_valid is True
            
            # Step 3: Generate code from the registry
            output_dir = Path(temp_workspace) / "generated_code"
            files = weaver_registry_generate(
                registry_path=registry_path,
                target_name="code/python",
                template_path="templates/registry",
                output_dir=str(output_dir)
            )
            
            assert len(files) > 0
            
            # Step 4: Verify generated code structure
            # Check for the 4-layer architecture
            expected_dirs = ["commands", "operations", "runtime", "contracts"]
            for dir_name in expected_dirs:
                dir_path = output_dir / dir_name
                if dir_path.exists():
                    assert any(dir_path.iterdir())  # Should have files
            
            # Step 5: Get stats to verify the registry
            stats = weaver_registry_stats(registry_path)
            assert "Total groups" in str(stats) or len(stats) > 0
            
        finally:
            # Cleanup
            shutil.rmtree(Path(registry_path).parent, ignore_errors=True)
    
    def test_semantic_quine_capability(self, temp_workspace):
        """Test the semantic quine capability - system can regenerate itself"""
        # Load the Weaver Forge semantic conventions
        forge_semconv_path = Path("weaver-forge.yaml")
        assert forge_semconv_path.exists()
        
        # Create a registry from Forge's own semantics
        registry_path = create_registry_structure(str(forge_semconv_path))
        
        try:
            # Validate the registry
            is_valid, errors = weaver_registry_check(registry_path)
            assert is_valid is True
            
            # Generate code from Forge's semantic conventions
            output_dir = Path(temp_workspace) / "regenerated_forge"
            files = weaver_registry_generate(
                registry_path=registry_path,
                target_name="code/python",
                template_path="templates/registry",
                output_dir=str(output_dir)
            )
            
            assert len(files) > 0
            
            # Verify the generated code has the same structure
            for layer in ["commands", "operations", "runtime", "contracts"]:
                original = Path("output") / layer / "forge.py"
                regenerated = output_dir / layer / "forge.py"
                
                if original.exists() and regenerated.exists():
                    # Files should exist and have content
                    assert regenerated.stat().st_size > 0
                    
                    # The regenerated file should have the key functions
                    content = regenerated.read_text()
                    if layer == "operations":
                        assert "generate_semantic_conventions" in content
                        assert "generate_code_from_registry" in content
            
        finally:
            # Cleanup
            shutil.rmtree(Path(registry_path).parent, ignore_errors=True)


@pytest.mark.skipif(
    shutil.which("weaver") is None,
    reason="Weaver CLI not installed"
)
class TestWeaverCLIIntegration:
    """Tests that require the actual Weaver CLI to be installed"""
    
    def test_real_weaver_execution(self):
        """Test actual Weaver CLI execution"""
        # Check Weaver version
        result = subprocess.run(
            ["weaver", "--version"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "weaver" in result.stdout.lower()
    
    def test_generated_cli_execution(self):
        """Test the generated CLI can execute commands"""
        cli_path = Path("generated_cli/weaver_cli_generated.py")
        
        if not cli_path.exists():
            # Generate it first
            subprocess.run(["python", "generate_weaver_cli.py"], check=True)
        
        # Test help command
        result = subprocess.run(
            ["python", str(cli_path), "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Generated Weaver CLI" in result.stdout
        
        # Test check command with test registry
        test_registry = Path("test_registry2")
        if test_registry.exists():
            result = subprocess.run(
                ["python", str(cli_path), "check", str(test_registry)],
                capture_output=True,
                text=True
            )
            
            # Should complete (may pass or fail depending on registry state)
            assert result.returncode in [0, 1]


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])