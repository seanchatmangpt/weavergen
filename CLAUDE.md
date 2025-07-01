# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WeaverGen is a Python wrapper around OpenTelemetry Weaver Forge that transforms YAML semantic convention definitions into production-ready code across multiple languages. It's optimized for Claude Code workflows with custom commands and agent integration.

## Common Development Commands

### Setup and Installation
```bash
# Install package in development mode with all dependencies
pip install -e ".[dev]"

# Quick development setup (install + pre-commit hooks + directories)
make dev

# Install OTel Weaver binary (required dependency)
cargo install otellib-weaver-cli
```

### BPMN Workflow Execution (with SpiffWorkflow)
```bash
# ALL CLI commands execute BPMN workflows (NO direct function calls)
uv run weavergen generate test_semantic.yaml  # -> triggers generation.bpmn workflow
uv run weavergen validate test_semantic.yaml # -> triggers validation.bpmn workflow
uv run weavergen templates --list           # -> triggers template_list.bpmn workflow

# Execute BPMN workflows directly with SpiffWorkflow engine
uv run python -m weavergen.bpmn_first_engine --workflow weavergen_orchestration.bpmn

# Run full generation pipeline with BPMN orchestration
uv run run_cli.py full-pipeline test_semantic.yaml --agents 3

# Debug and analyze captured spans from BPMN execution
uv run run_cli.py debug spans --format table
uv run run_cli.py debug spans --format mermaid

# Health check generated components via BPMN workflow
uv run run_cli.py debug health --deep

# Trace live BPMN workflow operations
uv run run_cli.py debug trace workflow
```

### Code Quality
```bash
# Format code
make format
# OR
ruff format src/

# Lint and type check
make lint
# OR
ruff check src/
mypy src/weavergen/
```

### Building and Distribution
```bash
# Clean build artifacts
make clean

# Build distribution packages
make build
# OR
python -m build
```

## Architecture Overview

WeaverGen follows a BPMN-first modular architecture:

1. **BPMN Workflow Engine** (`src/weavergen/bpmn_first_engine.py`)
   - SpiffWorkflow-based BPMN execution engine
   - Visual workflow orchestration with .bpmn files
   - OpenTelemetry span tracking for all workflow steps
   - Service task registry for semantic operations

2. **CLI Layer** (`src/weavergen/cli.py`)
   - Typer-based CLI with Rich formatting
   - Commands trigger BPMN workflows: `generate`, `validate`, `templates`, `config`
   - Entry point: `weavergen` command (workflow orchestrator)
   - NO direct function calls - ALL commands execute .bpmn workflows

3. **Core Logic** (`src/weavergen/core.py`)
   - `WeaverGen` class orchestrates the Weaver binary
   - Handles subprocess execution and error management
   - Manages configuration and template resolution

4. **Data Models** (`src/weavergen/models.py`)
   - Pydantic models for configuration and results
   - `GenerationConfig`, `ValidationResult`, `FileInfo` etc.

5. **BPMN Workflows** (`src/weavergen/workflows/bpmn/`)
   - Visual BPMN workflow definitions (.bpmn files)
   - Agent generation, validation, and orchestration workflows
   - Multi-instance loops and parallel gateways

## Key Workflows

### BPMN-Driven Code Generation Flow
1. Load semantic convention YAML via BPMN service task
2. Execute BPMN validation workflow with SpiffWorkflow engine  
3. Parallel BPMN gateways orchestrate multi-language generation
4. Service tasks call OTel Weaver binary with appropriate templates
5. BPMN validation workflows verify generated code with spans
6. Visual BPMN diagrams provide execution trace and debugging

### BPMN Workflow Patterns
- **Sequential Orchestration**: Linear service task chains for deterministic flows
- **Parallel Gateways**: Concurrent generation for multiple languages/agents
- **Exclusive Gateways**: Conditional routing based on validation results
- **Multi-Instance Tasks**: Dynamic agent role generation loops
- **Call Activities**: Subprocess workflows for complex operations

## Important Patterns

### Error Handling
- Custom exceptions: `WeaverGenError`, `WeaverNotFoundError`
- Rich console output for user-friendly errors
- Verbose mode for debugging

### Configuration Management
- Searches for Weaver binary in PATH
- Falls back to Cargo installation directory
- Configurable via CLI or API

### BPMN + Span Validation Strategy
- **BPMN Workflow Validation**: Visual processes with SpiffWorkflow execution
- **Span-Based Validation**: Superior to unit tests for distributed systems  
- **OTel Spans**: Capture runtime reality, real AI behavior, cross-system interactions
- **BPMN Service Tasks**: All semantic operations instrumented with spans
- **Enhanced Instrumentation**: 80/20 validation coverage with critical decorators
- **Debug Commands**: Comprehensive system health and component inspection
- **Span-Referenced Reporting**: All summaries MUST cite specific spans with trace IDs

## Claude Code Custom Commands

The project includes custom commands in `claude-code-context/commands/`:
- `/weavergen:multi-generate` - Generate for multiple languages
- `/weavergen:validate` - Validate semantic conventions
- `/weavergen:optimize` - Optimize generation performance
- `/weavergen:bootstrap` - Bootstrap new projects

## Development Notes

- The project uses Hatch as build backend
- Requires Python 3.11+
- **SpiffWorkflow**: Standard BPMN execution engine (installed via uv)
- **BPMN Files**: Visual workflow definitions in `src/weavergen/workflows/bpmn/`
- OTel Weaver binary is a Rust tool installed via Cargo
- Templates use Jinja2 with JQ expressions
- Performance target: 26x optimization over manual generation

## AI Development Guidelines

- **BPMN-First Development**:
  - ALWAYS use existing SpiffWorkflow library with `uv`
  - DO NOT create custom workflow engines
  - DO NOT run Python directly - use BPMN service tasks
  - ALL workflows must be visual .bpmn files
  - **ALL CLI COMMANDS MUST BE REFACTORED TO EXECUTE WORKFLOWS INSTEAD OF FUNCTIONS DIRECTLY**
  
- **CLI Architecture Requirements**:
  - CLI commands MUST trigger BPMN workflows, not Python functions
  - Each CLI operation MUST have a corresponding .bpmn workflow file
  - Direct function calls in CLI are FORBIDDEN - use SpiffWorkflow orchestration
  - CLI becomes a thin wrapper that launches BPMN workflows with context
  
- **Testing Philosophy**:
  - DO NOT WRITE OR RUN UNIT TESTS
  - USE BPMN WORKFLOWS WITH SPAN VALIDATION
  - USE SPANS WITH CHAINS OF RUNNING COMMANDS
  - Validation should be done through OTel spans and observability traces

- **Reporting and Documentation Requirements**:
  - **ALL SUMMARIES MUST SPECIFICALLY REFERENCE THE SPANS THAT PROVIDED THE INFORMATION**
  - NO summary or report without explicit span references and trace IDs
  - Include span attributes, timestamps, and execution context in all reports
  - Reference specific span names, task IDs, and workflow execution traces
  - Format: "Based on span `bpmn.service.load_semantics` (trace_id: abc123) at 2024-01-01T10:00:00Z..."