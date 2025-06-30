"""Validate that all imports work correctly."""

import sys
sys.path.insert(0, 'src')

print("Testing imports...")

try:
    from weavergen.models import (
        GenerationConfig, GenerationResult, ValidationResult,
        FileInfo, TemplateInfo, WeaverConfig
    )
    print("✓ Models imported successfully")
except Exception as e:
    print(f"✗ Models import failed: {e}")

try:
    from weavergen.semantic import (
        SemanticGenerator, SemanticConvention,
        Group, Attribute, AttributeType
    )
    print("✓ Semantic module imported successfully")
except Exception as e:
    print(f"✗ Semantic import failed: {e}")

try:
    from weavergen.core import WeaverGen
    print("✓ Core module imported successfully")
except Exception as e:
    print(f"✗ Core import failed: {e}")

try:
    from weavergen.cli_v1 import app
    print("✓ CLI v1 imported successfully")
except Exception as e:
    print(f"✗ CLI v1 import failed: {e}")

print("\nTesting basic functionality...")

# Test semantic models
try:
    attr = Attribute(
        id="test.attr",
        type=AttributeType.STRING,
        brief="Test attribute"
    )
    print(f"✓ Created attribute: {attr.id}")
except Exception as e:
    print(f"✗ Attribute creation failed: {e}")

try:
    group = Group(
        id="test.group",
        type="span",
        brief="Test group"
    )
    print(f"✓ Created group: {group.id}")
except Exception as e:
    print(f"✗ Group creation failed: {e}")

print("\nValidation complete!")