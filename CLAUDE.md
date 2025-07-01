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

### Span-Based Validation (Superior to Unit Tests)
```bash
# Generate and validate system via OTel spans
uv run run_cli.py full-pipeline test_semantic.yaml --agents 3

# Debug and analyze captured spans
uv run run_cli.py debug spans --format table
uv run run_cli.py debug spans --format mermaid

# Health check generated components
uv run run_cli.py debug health --deep

# Trace live operations
uv run run_cli.py debug trace communication
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

WeaverGen follows a modular architecture:

1. **CLI Layer** (`src/weavergen/cli.py`)
   - Typer-based CLI with Rich formatting
   - Commands: `generate`, `validate`, `templates`, `config`
   - Entry point: `weavergen` command

2. **Core Logic** (`src/weavergen/core.py`)
   - `WeaverGen` class orchestrates the Weaver binary
   - Handles subprocess execution and error management
   - Manages configuration and template resolution

3. **Data Models** (`src/weavergen/models.py`)
   - Pydantic models for configuration and results
   - `GenerationConfig`, `ValidationResult`, `FileInfo` etc.

4. **Claude Code Integration** (`claude-code-context/`)
   - Custom commands for multi-language generation
   - Session management for continuity
   - Agent workflow automation

## Key Workflows

### Code Generation Flow
1. User provides semantic convention YAML (URL or local path)
2. WeaverGen validates the registry
3. Calls OTel Weaver binary with appropriate templates
4. Processes generated files and returns results
5. Optionally validates generated code

### Multi-Language Generation
The system can generate code for multiple languages in parallel:
- Python, Rust, Go, Java, JavaScript
- Each language uses specific templates
- Results are aggregated and validated

## Important Patterns

### Error Handling
- Custom exceptions: `WeaverGenError`, `WeaverNotFoundError`
- Rich console output for user-friendly errors
- Verbose mode for debugging

### Configuration Management
- Searches for Weaver binary in PATH
- Falls back to Cargo installation directory
- Configurable via CLI or API

### Testing Strategy
- Unit tests mock the Weaver binary
- Integration tests require actual Weaver installation
- Coverage target: 80%

## Claude Code Custom Commands

The project includes custom commands in `claude-code-context/commands/`:
- `/weavergen:multi-generate` - Generate for multiple languages
- `/weavergen:validate` - Validate semantic conventions
- `/weavergen:optimize` - Optimize generation performance
- `/weavergen:bootstrap` - Bootstrap new projects

## Development Notes

- The project uses Hatch as build backend
- Requires Python 3.11+
- OTel Weaver binary is a Rust tool installed via Cargo
- Templates use Jinja2 with JQ expressions
- Performance target: 26x optimization over manual generation