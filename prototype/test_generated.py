#!/usr/bin/env python3
"""Test the generated Weaver Forge code"""

import sys
sys.path.insert(0, 'output')

from commands.forge import (
    forge_semantic_generate, 
    forge_code_generate, 
    forge_self_improve,
    ForgeResult
)

def test_semantic_generation():
    """Test semantic convention generation"""
    print("\n1. Testing forge_semantic_generate...")
    
    result = forge_semantic_generate(
        input_description="Create a user authentication system with login, logout, and session tracking",
        output_path="test_output/auth_semantic.yaml",
        llm_model="llama3.2",
        validation_status="pending",
        llm_temperature=0.1
    )
    
    print(f"   Success: {result.success}")
    if result.errors:
        print(f"   Errors: {result.errors}")
    if result.data:
        print(f"   Data: {result.data}")
    
    return result

def test_code_generation():
    """Test code generation from semantic conventions"""
    print("\n2. Testing forge_code_generate...")
    
    result = forge_code_generate(
        input_semantic_path="test_registry2/groups/weaver-forge.yaml",
        target_language="python", 
        template_directory="templates/registry/python",
        output_directory="test_output/generated_code"
    )
    
    print(f"   Success: {result.success}")
    if result.errors:
        print(f"   Errors: {result.errors}")
    if result.data:
        print(f"   Data: {result.data}")
    
    return result

def test_self_improvement():
    """Test self-referential improvement"""
    print("\n3. Testing forge_self_improve...")
    
    result = forge_self_improve(
        current_version="1.0.0",
        improvements=["Add better error handling", "Optimize template generation"],
        target_version="1.1.0",
        reference_depth=0
    )
    
    print(f"   Success: {result.success}")
    if result.errors:
        print(f"   Errors: {result.errors}")
    if result.data:
        print(f"   Data: {result.data}")
    
    return result

if __name__ == "__main__":
    print("Testing generated Weaver Forge operations...")
    
    # Test each operation
    semantic_result = test_semantic_generation()
    code_result = test_code_generation()
    improve_result = test_self_improvement()
    
    print("\n=== Summary ===")
    print(f"Semantic Generation: {'✓' if semantic_result.success else '✗'}")
    print(f"Code Generation: {'✓' if code_result.success else '✗'}")
    print(f"Self Improvement: {'✓' if improve_result.success else '✗'}")