#!/usr/bin/env python3
"""Simple test that the generated code structure is correct"""

import sys
sys.path.insert(0, 'output')

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from commands.forge import forge_semantic_generate, forge_code_generate, forge_self_improve, ForgeResult
        print("✓ Commands module imported successfully")
    except Exception as e:
        print(f"✗ Commands import failed: {e}")
        return False
        
    try:
        from operations.forge import forge_semantic_generate_execute, forge_code_generate_execute, forge_self_improve_execute
        print("✓ Operations module imported successfully")
    except Exception as e:
        print(f"✗ Operations import failed: {e}")
        return False
        
    try:
        from contracts.forge import ForgeSemanticGenerateContracts, ForgeCodeGenerateContracts, ForgeSelfImproveContracts
        print("✓ Contracts module imported successfully")
    except Exception as e:
        print(f"✗ Contracts import failed: {e}")
        return False
        
    try:
        from runtime.forge import write_semantic_file, read_semantic_file, validate_file_exists
        print("✓ Runtime module imported successfully")
    except Exception as e:
        print(f"✗ Runtime import failed: {e}")
        return False
        
    return True

def test_code_generation_operation():
    """Test the code generation operation (doesn't need LLM)"""
    print("\nTesting code generation operation...")
    
    from commands.forge import forge_code_generate
    
    # This should fail gracefully since the file doesn't exist
    result = forge_code_generate(
        input_semantic_path="nonexistent.yaml",
        target_language="python",
        template_directory="templates",
        output_directory="test_output"
    )
    
    print(f"Result success: {result.success}")
    print(f"Expected error: {result.errors}")
    
    # Should have failed with file not found
    return not result.success and result.errors

def test_function_signatures():
    """Test that function signatures match expectations"""
    print("\nTesting function signatures...")
    
    from commands.forge import forge_semantic_generate
    import inspect
    
    sig = inspect.signature(forge_semantic_generate)
    params = list(sig.parameters.keys())
    
    expected = ['input_description', 'output_path', 'llm_model', 'validation_status', 'llm_temperature', 'validation_errors']
    
    print(f"Parameters: {params}")
    print(f"Expected: {expected}")
    
    # Check required params come first
    required_count = 0
    for param in sig.parameters.values():
        if param.default == inspect.Parameter.empty:
            required_count += 1
        else:
            break  # First optional param means all required are done
            
    print(f"Required parameters: {required_count}")
    
    return params == expected

if __name__ == "__main__":
    print("=== Weaver Forge Generated Code Test ===\n")
    
    tests = [
        ("Imports", test_imports),
        ("Code Generation", test_code_generation_operation),
        ("Function Signatures", test_function_signatures)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n=== Summary ===")
    for name, passed in results:
        print(f"{name}: {'✓' if passed else '✗'}")
    
    all_passed = all(passed for _, passed in results)
    print(f"\nAll tests {'passed' if all_passed else 'failed'}!")
    
    sys.exit(0 if all_passed else 1)