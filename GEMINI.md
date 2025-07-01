# GEMINI.md

This file provides guidance to Gemini Code when working with code in this repository.

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

### CLI-First Workflow Execution (v1.0.0)
```bash
# CORE PRINCIPLE: Use CLI only - no individual Python files
# ALL operations via uv run weavergen commands

# Primary generation workflow
uv run weavergen generate semantic_conventions/weavergen_system.yaml

# Validation with span-based testing
uv run weavergen validate semantic_conventions/weavergen_system.yaml

# BPMN workflow execution (SpiffWorkflow engine)
uv run weavergen bpmn execute WeaverGenOrchestration --trace
uv run weavergen bpmn orchestrate --test

# Multi-agent system operations
uv run weavergen agents communicate --agents 3
uv run weavergen agents validate --deep

# Span-based debugging (NO unit tests)
uv run weavergen debug spans --format mermaid
uv run weavergen debug health --components all
uv run weavergen debug trace communication

# Template operations
uv run weavergen templates list
uv run weavergen templates generate --language python

# Full pipeline execution
uv run weavergen full-pipeline semantic_conventions/weavergen_system.yaml --agents 3
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



## Development Notes

- The project uses Hatch as build backend
- Requires Python 3.11+
- **SpiffWorkflow**: Standard BPMN execution engine (installed via uv)
- **BPMN Files**: Visual workflow definitions in `src/weavergen/workflows/bpmn/`
- OTel Weaver binary is a Rust tool installed via Cargo
- Templates use Jinja2 with JQ expressions
- Performance target: 26x optimization over manual generation

## v1.0.0 Development Guidelines

- **CLI-First Philosophy (v1)**:
  - **NO individual Python scripts** - use CLI commands only
  - ALL operations via `uv run weavergen` commands
  - Use SpiffWorkflow BPMN engine through CLI
  - NO direct Python execution - everything through CLI interface
  - CLI commands automatically execute BPMN workflows with SpiffWorkflow
  
- **v1 Architecture Requirements**:
  - CLI is the ONLY interface - no direct file execution
  - Each CLI command triggers SpiffWorkflow BPMN execution
  - All workflows are visual .bpmn files in `src/weavergen/workflows/bpmn/`
  - Service tasks handle actual work within BPMN workflows
  - Context flows through BPMN data objects, not Python variables
  
- **v1 Testing Philosophy**:
  - NO unit tests - use span-based validation only
  - ALL validation via OTel spans captured from CLI execution
  - Test by running CLI commands and analyzing generated spans
  - Use `uv run weavergen debug spans` for validation
  - Spans are the source of truth for system behavior
  
- **v1 Usage Patterns**:
  - Development: `uv run weavergen generate <semantic_file>`
  - Testing: `uv run weavergen debug spans --format mermaid`
  - Deployment: `uv run weavergen bpmn orchestrate --production`
  - Debugging: `uv run weavergen debug health --deep`
  
- **v1 Reporting Requirements**:
  - ALL reports must reference specific CLI commands executed
  - Include span trace IDs from CLI execution
  - Reference BPMN workflow names and task completion
  - Format: "Based on `uv run weavergen bpmn execute` (trace_id: abc123) at 2025-01-01T10:00:00Z..."
  - NO Python file creation for demonstrations - use CLI only

- **Exception for Debugging/Historical Analysis**: For the purpose of debugging, understanding historical development, or specific isolated testing, direct execution of Python files within the `prototype/` directory using `uv run` is permitted. This is an exception to the general CLI-first philosophy and should be used with caution, as these scripts may not adhere to current architectural patterns or have side effects.