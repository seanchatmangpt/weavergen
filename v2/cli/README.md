# WeaverGen v2 CLI Structure

## Overview

The WeaverGen v2 CLI has been restructured with a modular command architecture for better maintainability and extensibility. Each command group is implemented as a separate module in the `commands/` directory.

## Command Structure

```
v2/cli/
├── main.py                 # Main CLI entry point
├── commands/              # Command modules
│   ├── __init__.py
│   ├── regeneration.py    # DMEDI regeneration commands
│   ├── generate.py        # Code generation commands
│   ├── validate.py        # Validation commands
│   ├── agents.py          # AI agent operations
│   ├── bpmn.py           # BPMN workflow execution
│   ├── debug.py          # Debugging and diagnostics
│   ├── templates.py      # Template management
│   ├── semantic.py       # AI-powered semantic generation
│   └── mining.py         # Process mining and XES conversion
├── output_formats/       # Output formatting utilities
└── completion/          # Shell completion scripts
```

## Command Groups

### 1. Regeneration (`weavergen regeneration`)
DMEDI-based system regeneration commands:
- `define` - Create regeneration charter
- `measure` - Assess system entropy
- `explore` - Generate regeneration options
- `execute` - Execute DMEDI cycle
- `auto` - Automatic intelligent regeneration
- `status` - Check regeneration status

### 2. Generate (`weavergen generate`)
Code generation commands:
- `code` - Generate from semantic conventions
- `models` - Generate data models
- `forge` - Use Forge templates
- `smart` - AI-optimized generation

### 3. Validate (`weavergen validate`)
Validation commands:
- `semantic` - Validate semantic conventions
- `code` - Validate generated code
- `multi` - Run multiple validators
- `compliance` - Check standards compliance

### 4. Agents (`weavergen agents`)
AI agent operations:
- `communicate` - Agent communication simulation
- `validate` - Multi-agent validation
- `analyze` - Multi-agent code analysis
- `orchestrate` - Complex workflow orchestration
- `forge-to-agents` - Convert Forge to agent system

### 5. BPMN (`weavergen bpmn`)
BPMN workflow execution:
- `execute` - Execute BPMN workflow
- `orchestrate` - Orchestrate multiple workflows
- `list` - List available workflows
- `validate` - Validate BPMN definitions
- `monitor` - Monitor workflow execution
- `debug` - Debug workflow execution

### 6. Debug (`weavergen debug`)
Debugging and diagnostics:
- `spans` - Analyze OpenTelemetry spans
- `health` - System health check
- `inspect` - Deep component inspection
- `trace` - Trace operations
- `performance` - Performance profiling

### 7. Templates (`weavergen templates`)
Template management:
- `list` - List available templates
- `generate` - Generate from template
- `create` - Create new template
- `validate` - Validate template
- `install` - Install external templates

### 8. Semantic (`weavergen semantic`)
AI-powered semantic generation:
- `generate` - Generate semantic conventions
- `enhance` - Enhance existing conventions
- `analyze` - Analyze convention quality
- `merge` - Merge multiple conventions

### 9. Mining (`weavergen mining`)
Process mining and analysis:
- `convert` - Convert logs to XES format
- `discover` - Discover process models
- `analyze` - Analyze process logs
- `conformance` - Check conformance
- `visualize` - Create visualizations
- `predict` - ML-based predictions

## Usage Examples

```bash
# DMEDI regeneration
weavergen regeneration define my-system --component api --component db
weavergen regeneration execute my-system --strategy auto

# Code generation
weavergen generate code semantic_conventions.yaml --language python
weavergen generate models schema.yaml --language python typescript

# Multi-agent validation
weavergen agents validate semantic.yaml --agents 5 --deep
weavergen agents orchestrate generate --agents 3 --strategy balanced

# BPMN workflow execution
weavergen bpmn execute CodeGeneration --trace
weavergen bpmn monitor --live --metrics

# Debugging
weavergen debug spans --format mermaid --errors-only
weavergen debug health --components all --deep

# Process mining
weavergen mining convert logs.csv --format xes
weavergen mining discover process.xes --algorithm inductive
```

## Global Options

All commands support these global options:
- `--config, -c` - Configuration file path
- `--verbose` - Enable verbose output
- `--quiet, -q` - Suppress output
- `--version, -v` - Show version
- `--help, -h` - Show help

## Architecture Benefits

1. **Modularity**: Each command group is self-contained
2. **Maintainability**: Easy to add/modify commands
3. **Type Safety**: Full typing with Typer
4. **Rich Output**: Beautiful CLI with Rich library
5. **Async Support**: All commands use async/await
6. **Consistent Interface**: Uniform command structure

## Adding New Commands

To add a new command group:

1. Create a new module in `commands/`
2. Define the Typer app and commands
3. Import in `commands/__init__.py`
4. Add to `main.py`

Example structure:
```python
import typer
from rich.console import Console

app = typer.Typer(name="mycommand", help="Description")
console = Console()

@app.command("action")
def my_action(ctx: typer.Context, ...):
    """Action description"""
    # Implementation
```

## Future Enhancements

Commands still to be ported:
- `meetings` - Parliamentary meeting simulations
- `benchmark` - Performance benchmarking
- `demo` - System demonstrations
- `conversation` - Conversation systems
- `spiff` - SpiffWorkflow operations

## Dependencies

- `typer` - CLI framework
- `rich` - Terminal formatting
- `asyncio` - Async support
- Custom v2 engine integration