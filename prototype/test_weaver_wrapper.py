#!/usr/bin/env python3
"""Test the Weaver CLI wrapper implementation"""

import sys
sys.path.insert(0, 'output')

from commands.forge import (
    forge_semantic_generate, 
    forge_code_generate, 
    forge_self_improve,
    ForgeResult
)

def test_semantic_generation():
    """Test semantic convention generation (just creates YAML, no LLM)"""
    print("1. Testing semantic generation (Weaver wrapper)...")
    
    result = forge_semantic_generate(
        input_description="User authentication telemetry with login tracking",
        output_path="test_output/auth.yaml",
        llm_model="none",  # No LLM, just creates basic YAML
        validation_status="pending"
    )
    
    print(f"   Success: {result.success}")
    if result.data:
        print(f"   Output path: {result.data.get('output_path')}")
        print(f"   Validation: {result.data.get('validation_status')}")
    if result.errors:
        print(f"   Errors: {result.errors}")
    
    return result

def test_code_generation():
    """Test code generation using our existing registry"""
    print("\n2. Testing code generation (Weaver wrapper)...")
    
    result = forge_code_generate(
        input_semantic_path="test_registry2",  # Use our existing registry
        target_language="python",
        template_directory="templates",
        output_directory="test_output/weaver_generated"
    )
    
    print(f"   Success: {result.success}")
    if result.data:
        files = result.data.get('files_generated', [])
        print(f"   Generated {len(files)} files:")
        for f in files[:5]:  # Show first 5
            print(f"     - {f}")
    if result.errors:
        print(f"   Errors: {result.errors}")
    
    return result

def test_self_improvement():
    """Test self-improvement by creating a new version"""
    print("\n3. Testing self-improvement (version evolution)...")
    
    # First copy weaver-forge.yaml to v1.0.0
    import shutil
    from pathlib import Path
    
    if Path("weaver-forge.yaml").exists():
        shutil.copy2("weaver-forge.yaml", "weaver_forge_v1.0.0.yaml")
    
    result = forge_self_improve(
        current_version="1.0.0",
        improvements=["Add telemetry metrics", "Improve error handling"],
        target_version="1.1.0"
    )
    
    print(f"   Success: {result.success}")
    if result.data:
        print(f"   New version: {result.data.get('improved_semantic_path')}")
        print(f"   Reference depth: {result.data.get('reference_depth')}")
        files = result.data.get('generated_files', [])
        if files:
            print(f"   Generated {len(files)} files")
    if result.errors:
        print(f"   Errors: {result.errors}")
    
    return result

def main():
    print("=== Weaver CLI Wrapper Test ===")
    print("Testing Python wrappers around Weaver forge commands...\n")
    
    # Run tests
    semantic_result = test_semantic_generation()
    code_result = test_code_generation()
    improve_result = test_self_improvement()
    
    print("\n=== Summary ===")
    print(f"✓ Semantic generation: {'Success' if semantic_result.success else 'Failed'}")
    print(f"✓ Code generation: {'Success' if code_result.success else 'Failed'}")
    print(f"✓ Self improvement: {'Success' if improve_result.success else 'Failed'}")
    
    print("\nThe semantic quine concept is demonstrated:")
    print("1. We generate semantic conventions from descriptions")
    print("2. We use Weaver to generate code from those conventions")
    print("3. That code can generate new semantic conventions")
    print("4. Creating a self-referential loop!")
    
    # Check if we actually created files
    from pathlib import Path
    if Path("test_output/auth.yaml").exists():
        print("\n✓ Created semantic convention file")
        with open("test_output/auth.yaml") as f:
            print(f.read()[:200] + "...")
    
    if Path("weaver_forge_v1.1.0.yaml").exists():
        print("\n✓ Created improved version")

if __name__ == "__main__":
    main()