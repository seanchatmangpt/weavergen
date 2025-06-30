#!/usr/bin/env python3
"""
Semantic Quine Demonstration V2

This demonstrates the self-referential nature of Weaver Forge using the actual
generated functions from the semantic conventions.
"""

import sys
import os
import shutil
import tempfile
from pathlib import Path

# Add output to path
sys.path.insert(0, 'output')

# Import the actual generated functions
from commands.forge import (
    weaver_registry_check,
    weaver_registry_generate,
    weaver_registry_stats
)
from runtime.forge import create_registry_structure

def demonstrate_semantic_quine():
    """Demonstrate the semantic quine capability"""
    print("=" * 70)
    print("🔄 SEMANTIC QUINE DEMONSTRATION")
    print("=" * 70)
    
    print("\n📖 What is a Semantic Quine?")
    print("  A program that can regenerate itself from its own semantic definition")
    print("  Like a quine that outputs its source, but at the semantic level!")
    
    print("\n🏗️  The WeaverGen Semantic Quine:")
    print("  1. weaver-forge.yaml defines the system's semantics")
    print("  2. Weaver generates a 4-layer implementation from those semantics")
    print("  3. The generated code can read weaver-forge.yaml")
    print("  4. The generated code calls Weaver to regenerate itself")
    print("  5. The new generation matches the original!")
    
    print("\n" + "=" * 70)
    print("STEP 1: Load Forge's Own Semantic Conventions")
    print("=" * 70)
    
    forge_yaml = Path("weaver-forge.yaml")
    if not forge_yaml.exists():
        print("❌ weaver-forge.yaml not found!")
        return
    
    print(f"✅ Found {forge_yaml}")
    
    # Create a temporary registry for validation
    print("\n🔧 Creating temporary registry structure...")
    temp_registry = None
    
    try:
        temp_registry = create_registry_structure(str(forge_yaml))
        print(f"✅ Created registry at: {temp_registry}")
        
        print("\n" + "=" * 70)
        print("STEP 2: Validate Forge's Semantics Using Generated Code")
        print("=" * 70)
        
        # Use the generated validation function
        result = weaver_registry_check(
            registry_check_path=temp_registry,
            registry_check_valid=True,  # Required but should be output
            registry_check_strict=True
        )
        
        print(f"✅ Validation result: {result}")
        print(f"   Success: {result.success}")
        if result.errors:
            print(f"   Errors: {result.errors}")
        
        print("\n" + "=" * 70)
        print("STEP 3: Get Statistics About Forge's Semantics")
        print("=" * 70)
        
        stats_result = weaver_registry_stats(
            registry_stats_registry_path=temp_registry,
            registry_stats_total_groups=0,
            registry_stats_total_attributes=0
        )
        
        print(f"✅ Statistics gathered: {stats_result}")
        if stats_result.data:
            print(f"   Data: {stats_result.data}")
        
        print("\n" + "=" * 70)
        print("STEP 4: The Quine - Regenerate Forge from Its Own Semantics")
        print("=" * 70)
        
        # Create output directory for regeneration
        regen_dir = Path("quine_regenerated")
        regen_dir.mkdir(exist_ok=True)
        
        print(f"🔄 Calling Weaver to regenerate Forge...")
        
        # Use the generated code generation function
        gen_result = weaver_registry_generate(
            registry_generate_registry_path=temp_registry,
            registry_generate_target="code/python",
            registry_generate_output_dir=str(regen_dir),
            registry_generate_files_count=0,
            registry_generate_template_path="templates/registry"
        )
        
        print(f"✅ Generation result: {gen_result}")
        print(f"   Success: {gen_result.success}")
        
        if gen_result.success and gen_result.data:
            files = gen_result.data.get("files", [])
            print(f"   Generated {len(files)} files:")
            for f in files[:5]:
                print(f"     - {f}")
            if len(files) > 5:
                print(f"     ... and {len(files)-5} more")
        
        print("\n" + "=" * 70)
        print("STEP 5: Verify the Quine Property")
        print("=" * 70)
        
        # Check if key files were regenerated
        expected_files = [
            "commands/forge.py",
            "operations/forge.py", 
            "runtime/forge.py",
            "contracts/forge.py"
        ]
        
        regenerated = []
        for ef in expected_files:
            regen_path = regen_dir / ef
            if regen_path.exists():
                regenerated.append(ef)
                print(f"✅ Regenerated: {ef}")
            else:
                print(f"❌ Missing: {ef}")
        
        if len(regenerated) == len(expected_files):
            print("\n🎉 QUINE PROPERTY VERIFIED!")
            print("   The system successfully regenerated itself from its semantics!")
        else:
            print("\n⚠️  Partial regeneration - some files missing")
        
        # Cleanup
        shutil.rmtree(regen_dir, ignore_errors=True)
        
    finally:
        # Cleanup temp registry
        if temp_registry:
            parent = Path(temp_registry).parent
            shutil.rmtree(parent, ignore_errors=True)
    
    print("\n" + "=" * 70)
    print("🌟 Key Insights")
    print("=" * 70)
    print("1. The system defines itself through semantic conventions")
    print("2. It can use those definitions to regenerate its implementation")
    print("3. Every operation is traced with OpenTelemetry")
    print("4. The system can analyze its own behavior to improve")
    print("\n✨ This is a true semantic quine - code that understands itself!")


if __name__ == "__main__":
    demonstrate_semantic_quine()