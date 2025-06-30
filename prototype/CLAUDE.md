# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the WeaverGen prototype directory, demonstrating a "semantic quine" - a self-referential code generation system that can regenerate itself from its own semantic conventions. It wraps OpenTelemetry Weaver with a 4-layer architecture and full observability.

## Common Development Commands

### Running the Semantic Quine Demo
```bash
# See the semantic quine in action
python semantic_quine_demo.py

# Validate with OpenTelemetry traces
python test_otel_runtime_validation.py

# Run integration tests
python run_integration_tests.py
```

### Generating Code from Semantics
```bash
# Bootstrap Forge from its own semantics
make bootstrap

# Generate CLI from semantic conventions
python generate_weaver_cli.py

# Use the generated CLI
python generated_cli/weaver_cli_generated.py --help
```

### Testing and Validation
```bash
# Run 80/20 validation (core features)
python validate_80_20.py

# Test Weaver wrapper functionality
python test_weaver_forge.py

# Run full integration tests
python test_integration_full_workflow.py
```

## Architecture Overview

### 4-Layer Architecture

1. **Commands Layer** (`output/commands/forge.py`)
   - Auto-generated from semantic conventions
   - Provides OpenTelemetry instrumentation
   - DO NOT EDIT - regenerated from semantics

2. **Operations Layer** (`output/operations/forge.py`)
   - Business logic implementation
   - AI-EDITABLE - can be modified while maintaining contracts
   - Contains the core algorithms

3. **Runtime Layer** (`output/runtime/forge.py`)
   - Handles all side effects
   - Wraps external tools (Weaver CLI)
   - Stable interface - rarely changes

4. **Contracts Layer** (`output/contracts/forge.py`)
   - Runtime validation with icontract
   - Ensures data integrity
   - Generated from semantic constraints

### Key Semantic Conventions

- **`weaver-forge.yaml`** - Defines Forge's own operations
- **`weaver-cli-semantics.yaml`** - Defines CLI commands
- **`test_registry2/`** - Example semantic conventions for testing

### Template System

Templates in `templates/registry/python/`:
- Use Jinja2 with JQ expressions
- Generate the 4-layer architecture
- Support multiple target languages

## The Semantic Quine Concept

The system can regenerate itself:
1. `weaver-forge.yaml` defines the system's semantics
2. Weaver generates implementation from those semantics
3. Generated code can call Weaver to regenerate itself
4. The regeneration matches the original (quine property)

## Important Notes

- **Typing**: Avoid `typing.Any` in generated code - use specific types
- **Template Types**: `template[string]` maps to `Dict[str, str]` in Python
- **Weaver Path**: Templates are in `templates/registry/`, targets like `code/python`
- **Registry Structure**: Single YAML files need temporary registry structure
- **OTel Validation**: All operations must have proper telemetry attributes