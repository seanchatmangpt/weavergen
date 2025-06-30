#!/usr/bin/env python3
"""
Semantic Quine Demonstration

This demonstrates the self-referential nature of Weaver Forge:
1. Templates generate code from semantic conventions
2. That code can generate new semantic conventions
3. Those conventions can regenerate templates and code
4. Creating a self-referential loop!
"""

import sys
sys.path.insert(0, 'output')

from commands.forge import forge_semantic_generate, forge_code_generate, forge_self_improve
from pathlib import Path
import yaml

def demonstrate_semantic_quine():
    print("=== Weaver Forge Semantic Quine Demonstration ===\n")
    
    print("The Semantic Quine Concept:")
    print("- A quine is a program that produces its own source code")
    print("- A semantic quine generates the semantic conventions that define itself")
    print("- Weaver Forge implements this through a 4-layer architecture\n")
    
    print("Architecture:")
    print("1. Commands Layer: Thin wrappers with OpenTelemetry instrumentation")
    print("2. Operations Layer: Business logic (AI-editable)")
    print("3. Runtime Layer: Side effects (Weaver CLI calls)")
    print("4. Contracts Layer: Validation rules\n")
    
    print("=== Step 1: Generate Semantic Conventions ===")
    print("Creating semantic conventions from natural language...")
    
    result = forge_semantic_generate(
        input_description="A system for generating code from semantic conventions",
        output_path="quine_semantics.yaml",
        llm_model="none",
        validation_status="pending"
    )
    
    if result.success:
        print("✓ Created semantic convention")
        with open("quine_semantics.yaml") as f:
            print(f"  Contents:\n{f.read()}")
    
    print("\n=== Step 2: Code Generation (Using Our Registry) ===")
    print("The generated code can create semantic conventions...")
    
    # Show that we're using Weaver to generate code
    result = forge_code_generate(
        input_semantic_path="test_registry2",
        target_language="python",
        template_directory="templates",
        output_directory="quine_output"
    )
    
    print(f"✓ Code generation capability: {result.success}")
    
    print("\n=== Step 3: Self-Improvement ===")
    print("The system can improve itself...")
    
    # Create base version if needed
    if not Path("weaver_forge_v2.0.0.yaml").exists() and Path("weaver-forge.yaml").exists():
        import shutil
        shutil.copy2("weaver-forge.yaml", "weaver_forge_v2.0.0.yaml")
    
    result = forge_self_improve(
        current_version="2.0.0",
        improvements=["Add distributed tracing", "Optimize template generation"],
        target_version="2.1.0"
    )
    
    if result.success:
        print(f"✓ Created improved version: {result.data.get('improved_semantic_path')}")
        print(f"  Reference depth: {result.data.get('reference_depth')}")
    
    print("\n=== The Quine Loop ===")
    print("1. weaver-forge.yaml defines the semantic conventions")
    print("2. Templates (*.j2) use these conventions to generate code")
    print("3. Generated code (output/) can create new semantic conventions")
    print("4. Those conventions can regenerate the templates")
    print("5. Creating a self-referential system!\n")
    
    print("Key Innovation:")
    print("- No LLMs needed - just Weaver CLI wrappers")
    print("- Full OpenTelemetry instrumentation built-in")
    print("- Each operation is traced and measured")
    print("- The system can analyze its own telemetry to improve")
    
    print("\n=== Practical Applications ===")
    print("1. Auto-generate SDKs from semantic conventions")
    print("2. Keep documentation in sync with code")
    print("3. Evolve telemetry schemas based on usage patterns")
    print("4. Generate test cases from conventions")
    print("5. Create language-specific implementations automatically")

if __name__ == "__main__":
    demonstrate_semantic_quine()
    
    # Clean up demo files
    import os
    for f in ["quine_semantics.yaml", "weaver_forge_v2.0.0.yaml", "weaver_forge_v2.1.0.yaml"]:
        if os.path.exists(f):
            os.remove(f)