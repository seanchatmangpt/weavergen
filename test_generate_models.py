#!/usr/bin/env python3
"""Test script for generating Pydantic models from semantic conventions."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weavergen.generate_models import generate_pydantic_models, validate_generated_models

if __name__ == "__main__":
    # Test with minimal.yaml
    semantic_file = Path("semantic-conventions/groups/minimal.yaml")
    output_dir = Path("generated")
    
    print(f"🚀 Testing model generation from {semantic_file}")
    
    if semantic_file.exists():
        result = generate_pydantic_models(semantic_file, output_dir)
        
        if result.success:
            print("✅ Generation successful!")
            # Validate the generated models
            model_file = output_dir / "pydantic" / "models.py"
            if model_file.exists():
                print(f"📄 Generated file: {model_file}")
                validate_generated_models(model_file)
        else:
            print(f"❌ Generation failed: {result.error}")
    else:
        print(f"❌ File not found: {semantic_file}")