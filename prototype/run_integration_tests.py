#!/usr/bin/env python3
"""Run integration tests directly"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add output to path
sys.path.append("output")

# Import test class
from test_integration_full_workflow import TestFullWorkflowIntegration

def run_tests():
    """Run integration tests manually"""
    test_instance = TestFullWorkflowIntegration()
    
    # Create temp workspace
    temp_dir = tempfile.mkdtemp(prefix="weaver_test_")
    
    try:
        print("=" * 60)
        print("Running Integration Tests")
        print("=" * 60)
        
        # Test 1: Semantic generation
        print("\n1. Testing semantic generation from natural language...")
        try:
            test_instance.test_semantic_generation_from_natural_language(temp_dir)
            print("✅ PASSED: Semantic generation")
        except Exception as e:
            print(f"❌ FAILED: Semantic generation - {e}")
        
        # Test 2: CLI generation
        print("\n2. Testing CLI generation workflow...")
        try:
            test_instance.test_cli_generation_workflow(temp_dir)
            print("✅ PASSED: CLI generation")
        except Exception as e:
            print(f"❌ FAILED: CLI generation - {e}")
        
        # Test 3: Registry validation
        print("\n3. Testing registry validation...")
        try:
            # Create sample semantic convention directly
            sample_conv = {
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
            test_instance.test_registry_validation(temp_dir, sample_conv)
            print("✅ PASSED: Registry validation")
        except Exception as e:
            print(f"❌ FAILED: Registry validation - {e}")
        
        # Test 4: Code generation
        print("\n4. Testing code generation from registry...")
        try:
            sample_conv = {
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
            test_instance.test_code_generation_from_registry(temp_dir, sample_conv)
            print("✅ PASSED: Code generation")
        except Exception as e:
            print(f"❌ FAILED: Code generation - {e}")
        
        # Test 5: Semantic quine
        print("\n5. Testing semantic quine capability...")
        try:
            test_instance.test_semantic_quine_capability(temp_dir)
            print("✅ PASSED: Semantic quine")
        except Exception as e:
            print(f"❌ FAILED: Semantic quine - {e}")
        
        # Test 6: End-to-end workflow
        print("\n6. Testing end-to-end workflow...")
        try:
            test_instance.test_end_to_end_workflow(temp_dir)
            print("✅ PASSED: End-to-end workflow")
        except Exception as e:
            print(f"❌ FAILED: End-to-end workflow - {e}")
        
        print("\n" + "=" * 60)
        print("Integration tests completed")
        print("=" * 60)
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    run_tests()