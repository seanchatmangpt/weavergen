# Weaver Forge Prototype

A Python implementation of OpenTelemetry Weaver Forge demonstrating the semantic quine concept - a self-referential code generation system that can generate the semantic conventions that define itself.

## Overview

This prototype implements a 4-layer architecture that wraps the OpenTelemetry Weaver CLI with full observability:

1. **Commands Layer** - Thin wrappers with automatic OpenTelemetry instrumentation
2. **Operations Layer** - Business logic (AI-editable)
3. **Runtime Layer** - Side effects and Weaver CLI integration
4. **Contracts Layer** - Runtime validation using icontract

## Key Features

- **Semantic Quine**: Demonstrates self-referential code generation
- **Full OpenTelemetry Instrumentation**: Every operation is traced and measured
- **Weaver CLI Integration**: Wraps `weaver registry` commands
- **4-Layer Architecture**: Clean separation of concerns
- **Enhanced CLI**: Extended Typer-based CLI with multi-language support

## Quick Start

### Prerequisites

- Python 3.11+
- OpenTelemetry Weaver CLI (`cargo install weaver`)
- Basic understanding of semantic conventions

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd weavergen/prototype

# Install dependencies (if using pip)
pip install opentelemetry-api opentelemetry-sdk typer rich pydantic PyYAML

# Or use the existing virtual environment
source /Users/sac/dev/uvmgr/.venv/bin/activate
```

### Basic Usage

1. **Validate the system works** (80/20 validation):
```bash
python validate_80_20.py
```

2. **See the semantic quine in action**:
```bash
python semantic_quine_demo.py
```

3. **Use the enhanced CLI**:
```bash
# Show available commands
python enhanced_cli.py --help

# Generate code from semantic conventions
python enhanced_cli.py generate test_registry2 python

# Multi-language generation
python enhanced_cli.py multi generate test_registry2 --language python --language go --language rust

# Check registry validity
python enhanced_cli.py check test_registry2
```

## Architecture

### Semantic Conventions → Templates → Code → Semantic Conventions

The semantic quine demonstrates how:
1. `weaver-forge.yaml` defines semantic conventions for code generation
2. Templates (`*.j2`) use these conventions to generate code
3. Generated code can create new semantic conventions
4. Creating a self-referential loop

### 4-Layer Architecture

```
┌─────────────────────────────────────────────┐
│           Commands Layer                     │
│  (OTEL Instrumentation - commands/forge.py)  │
├─────────────────────────────────────────────┤
│          Operations Layer                    │
│    (Business Logic - operations/forge.py)    │
├─────────────────────────────────────────────┤
│           Runtime Layer                      │
│    (Weaver CLI Calls - runtime/forge.py)     │
├─────────────────────────────────────────────┤
│          Contracts Layer                     │
│    (Validation - contracts/forge.py)         │
└─────────────────────────────────────────────┘
```

## File Structure

```
prototype/
├── weaver-forge.yaml          # Semantic conventions defining Forge operations
├── templates/                 # Jinja2 templates for code generation
│   └── registry/
│       └── python/
│           ├── commands.j2    # Commands layer template
│           ├── operations.j2  # Operations layer template
│           ├── runtime.j2     # Runtime layer template
│           ├── contracts.j2   # Contracts layer template
│           └── weaver.yaml    # Template configuration
├── output/                    # Generated code (via Weaver)
│   ├── commands/
│   ├── operations/
│   ├── runtime/
│   └── contracts/
├── test_registry2/            # Test semantic convention registry
├── enhanced_cli.py            # Enhanced Typer CLI
├── validate_80_20.py          # 80/20 validation script
├── test_otel_validation.py    # OTEL instrumentation tests
└── semantic_quine_demo.py     # Semantic quine demonstration

```

## Validation

The system includes comprehensive validation:

### 80/20 Validation (`validate_80_20.py`)

Tests the core functionality that provides 80% of the value:
- ✓ Semantic convention generation
- ✓ Code generation from conventions
- ✓ Self-improvement capability
- ✓ 4-layer architecture integration
- ✓ Semantic quine concept
- ✓ Weaver CLI integration

Run with continuous loop:
```bash
python validate_80_20.py --loop
```

### OTEL Validation (`test_otel_validation.py`)

Validates OpenTelemetry instrumentation:
- Span creation and attributes
- Metrics collection
- Error handling and tracing
- Parent-child span relationships

### Test Results

```
============================================================
VALIDATION SUMMARY
============================================================
semantic_generate....................... ✓ PASS
code_generate........................... ✓ PASS
self_improve............................ ✓ PASS
layers.................................. ✓ PASS
semantic_quine.......................... ✓ PASS
weaver_cli.............................. ✓ PASS

Total: 6/6 passed (100%)
```

## Operations

The system implements three core operations defined in `weaver-forge.yaml`:

### 1. forge.semantic.generate
Generate semantic conventions from natural language descriptions.

```python
result = forge_semantic_generate(
    input_description="A telemetry system",
    output_path="telemetry.yaml",
    llm_model="mock",
    validation_status="pending"
)
```

### 2. forge.code.generate
Generate code from semantic conventions using Weaver templates.

```python
result = forge_code_generate(
    input_semantic_path="registry/",
    target_language="python",
    template_directory="templates",
    output_directory="generated"
)
```

### 3. forge.self.improve
Self-referential improvement of Weaver Forge itself.

```python
result = forge_self_improve(
    current_version="1.0.0",
    improvements=["Add metrics support"],
    target_version="1.1.0"
)
```

## Enhanced CLI Commands

### Main Commands
- `generate` - Generate code from semantic conventions
- `check` - Validate semantic convention registry
- `templates` - List available templates
- `version` - Show version information

### Registry Sub-commands
- `registry resolve` - Resolve and merge semantic conventions
- `registry stats` - Show statistics about registry
- `registry generate` - Full registry generation command

### Multi-language Operations
- `multi generate` - Generate code for multiple languages at once

### Session Management
- `session start` - Start a new Claude Code session
- `session list` - List all sessions

## Testing

Run the test suite:
```bash
# Run pytest tests (if pytest is available)
python -m pytest test_weaver_forge.py -v

# Or run validation directly
python validate_80_20.py

# Test OTEL instrumentation
python test_otel_validation.py
```

## Key Concepts

### Semantic Quine
A program that generates the semantic conventions that define itself, creating a self-referential loop. This demonstrates how semantic conventions can bootstrap themselves.

### Why This Matters
1. **Self-documenting systems** - Code that can describe itself
2. **Evolution** - Systems that can improve their own definitions
3. **Consistency** - Generated code always matches its semantic conventions
4. **Observability** - Full tracing of the generation process

## Performance

The system demonstrates:
- Instant semantic convention generation (mock mode)
- Parallel multi-language generation
- Continuous validation at 100+ iterations/minute
- Full OTEL instrumentation with minimal overhead

## What This Proves

1. **Semantic-driven development is viable** - Code can be generated from semantic definitions
2. **Self-reference works** - A system can generate its own definition and regenerate itself
3. **Observability is integral** - Not an afterthought but built into the generation process
4. **Weaver CLI integration** - Successfully wraps and extends Weaver functionality

## The Key Insight

> "A system that can generate valid, observable code from semantic definitions,
> and can generate itself, proves that semantic-driven development is viable."

This prototype demonstrates that telemetry and application code can be unified
from the same semantic source - they're only separate due to human cognitive
limitations, not architectural necessity.

## Future Enhancements

1. **Real LLM Integration** - Replace mock with actual LLM for semantic generation
2. **Template Generation** - Programmatically create Jinja2 templates
3. **More Languages** - Add support for Java, C++, JavaScript
4. **Registry Management** - Full CRUD operations on registries
5. **Cloud Integration** - Deploy as a service with API

## Contributing

This is a prototype demonstrating the semantic quine concept. Feel free to:
- Experiment with different semantic conventions
- Add new templates for other languages
- Enhance the CLI with more features
- Improve the validation suite

## License

This prototype is part of the WeaverGen project and follows the same license terms.