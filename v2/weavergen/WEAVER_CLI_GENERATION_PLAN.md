# Using Weaver to Generate WeaverGen CLI from Semantic Conventions

## Overview

Transform the `semantic_conventions/weavergen_cli.yaml` into a fully functional Typer CLI using OTel Weaver Forge.

## Semantic Convention Structure Analysis

The YAML defines:
1. **CLI Application** (`cli.weavergen`) - Root app configuration
2. **Commands** (`cli.command.*`) - Individual command definitions
3. **Command Groups** (`cli.group.*`) - Subcommand groups (bpmn, agents, mining)
4. **Metrics** (`cli.metrics.*`) - CLI usage metrics
5. **Attributes** (`cli.attribute.*`) - CLI-specific attributes

## Weaver Templates Required

### 1. **cli_main.j2** - Main CLI Application
```jinja2
"""{{ app.brief | comment_block }}"""
{%- set app = groups | select("id", "cli.weavergen") | first %}

import typer
from rich.console import Console
from pathlib import Path
from typing import Optional, List

app = typer.Typer(
    name="{{ app.attributes | select_attr("cli.app.name") | first.value }}",
    help="{{ app.attributes | select_attr("cli.app.help") | first.value }}",
    rich_markup_mode={{ app.attributes | select_attr("cli.app.rich_markup") | first.value }},
    no_args_is_help={{ app.attributes | select_attr("cli.app.no_args_is_help") | first.value }}
)

console = Console()

{%- for group in groups | select("type", "command_group") %}
# Import {{ group.brief }}
from .commands.{{ group.attributes | select_attr("cli.group.name") | first.value }} import {{ group.attributes | select_attr("cli.group.name") | first.value }}_app
app.add_typer({{ group.attributes | select_attr("cli.group.name") | first.value }}_app, name="{{ group.attributes | select_attr("cli.group.name") | first.value }}", help="{{ group.attributes | select_attr("cli.group.help") | first.value }}")
{%- endfor %}

{%- for command in groups | select("type", "command") | reject("prefix", "cli.") %}
{{ command | render_command }}
{%- endfor %}

if __name__ == "__main__":
    app()
```

### 2. **cli_command.j2** - Command Template
```jinja2
{%- macro render_command(command) -%}
{{ command.attributes | select_attr("cli.command.decorator.dod") | first.value }}
{{ command.attributes | select_attr("cli.command.decorator.span") | first.value }}
@app.command()
def {{ command.attributes | select_attr("cli.command.name") | first.value }}(
{%- for arg in command.attributes | select_attr("cli.command.arguments") | first.value %}
    {{ arg.name }}: {{ arg.type }} = typer.Argument(..., help="{{ arg.help }}"),
{%- endfor %}
{%- for opt in command.attributes | select_attr("cli.command.options") | first.value %}
    {{ opt.name }}: {{ opt.type }} = typer.Option({{ opt.default }}, "--{{ opt.name | kebab }}"{% if opt.short %}, "{{ opt.short }}"{% endif %}, help="{{ opt.help }}"),
{%- endfor %}
) -> None:
    """{{ command.attributes | select_attr("cli.command.help") | first.value }}"""
    # Implementation generated from semantic conventions
    with console.status("[bold green]{{ command.brief }}..."):
        # TODO: Implement {{ command.id }}
        pass
{%- endmacro -%}
```

### 3. **cli_group.j2** - Command Group Template
```jinja2
{%- set group = groups | select("id", group_id) | first -%}
"""{{ group.brief }}"""

import typer
from rich.console import Console
from pathlib import Path
from typing import Optional, List

{{ group.attributes | select_attr("cli.group.name") | first.value }}_app = typer.Typer(
    help="{{ group.attributes | select_attr("cli.group.help") | first.value }}"
)

console = Console()

{%- for command_name in group.attributes | select_attr("cli.group.commands") | first.value %}
{%- set command = groups | select("id", "cli.command." + group.attributes | select_attr("cli.group.name") | first.value + "." + command_name) | first %}
{{ command | render_command }}
{%- endfor %}
```

### 4. **cli_metrics.j2** - Metrics Collection
```jinja2
"""CLI Metrics instrumentation generated from semantic conventions"""

from opentelemetry import metrics
from opentelemetry.metrics import Counter, Histogram

meter = metrics.get_meter("weavergen.cli")

{%- for metric in groups | select("type", "metric") %}
{{ metric.id | snake_case }} = meter.create_{{ metric.instrument }}(
    name="{{ metric.id }}",
    description="{{ metric.brief }}",
    unit="{{ metric.unit }}"
)
{%- endfor %}
```

## Weaver Configuration File

### weaver.yaml
```yaml
schema_url: https://weavergen.dev/schemas/1.0.0
templates:
  - pattern: cli_main.j2
    filter: 'groups | select("type", "application")'
    output: src/weavergen/cli.py
    
  - pattern: cli_group.j2
    filter: 'groups | select("type", "command_group")'
    output: 'src/weavergen/commands/{{ group.attributes | select_attr("cli.group.name") | first.value }}.py'
    
  - pattern: cli_metrics.j2
    filter: 'groups | select("type", "metric")'
    output: src/weavergen/cli_metrics.py

params:
  cli:
    decorators_enabled: true
    spans_enabled: true
    dod_enforcement: true
```

## Generation Process

### Step 1: Validate Semantic Conventions
```bash
weaver registry check -r semantic_conventions/weavergen_cli.yaml
```

### Step 2: Generate CLI Structure
```bash
weaver registry generate \
  -r semantic_conventions/weavergen_cli.yaml \
  -t cli_templates \
  --output generated_cli
```

### Step 3: Post-Processing Script
```python
# post_process.py
import ast
import black
from pathlib import Path

def enhance_generated_cli(output_dir: Path):
    """Add implementation logic to generated CLI skeleton"""
    
    # Read implementation mappings
    implementations = {
        "generate": "implementation/generate_impl.py",
        "forge_to_agents": "implementation/forge_to_agents_impl.py",
        # ... etc
    }
    
    # Inject implementations into generated commands
    for file in output_dir.rglob("*.py"):
        tree = ast.parse(file.read_text())
        # Transform AST to inject implementations
        # Write back formatted code
        file.write_text(black.format_str(ast.unparse(tree), mode=black.Mode()))
```

## Benefits of Weaver-Generated CLI

1. **Single Source of Truth**: Semantic conventions define the entire CLI structure
2. **Type Safety**: Generated from strongly-typed semantic definitions
3. **Consistency**: All commands follow the same patterns
4. **Metrics Built-in**: Automatic instrumentation from semantic conventions
5. **Documentation**: Help text and descriptions from semantic conventions
6. **Evolution**: Add new commands by updating YAML and regenerating

## Example: Generated Command

From semantic convention:
```yaml
- id: cli.command.generate
  type: command
  brief: "Generate code from semantic conventions"
  attributes:
    - id: cli.command.name
      value: "generate"
    - id: cli.command.help
      value: "🚀 Generate code from semantic conventions using OTel Weaver Forge"
```

Generates:
```python
@enforce_dod(require_bpmn=False, min_trust_score=0.7)
@cli_span("cli.generate", bpmn_file="workflows/bpmn/code_generation.bpmn", bpmn_task="Task_Generate")
@app.command()
def generate(
    registry_url: str = typer.Argument(..., help="URL or path to semantic convention registry"),
    output_dir: Path = typer.Option(Path("./generated"), "--output", "-o", help="Output directory for generated code"),
    language: str = typer.Option("python", "--language", "-l", help="Target language for code generation"),
    template_dir: Optional[Path] = typer.Option(None, "--templates", "-t", help="Custom template directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
    single_binary: bool = typer.Option(True, "--single-binary", help="Optimize for single binary deployment"),
) -> None:
    """🚀 Generate code from semantic conventions using OTel Weaver Forge"""
    with console.status("[bold green]Generate code from semantic conventions..."):
        # Implementation injected during post-processing
        from .implementation import generate_impl
        generate_impl(registry_url, output_dir, language, template_dir, force, single_binary)
```

## Integration with Tool-Based Structure

The Weaver-generated CLI can be organized into the tool-based semantic structure:

```bash
weavergen workflow <action>  # From cli.group.bpmn + cli.group.spiff
weavergen weaver <action>    # Core weaver operations
weavergen forge <action>     # From cli.group.forge
weavergen otel <action>      # From cli.group.otel (spans, metrics)
weavergen mermaid <action>   # Visualization commands
```

## Next Steps

1. **Create Weaver Templates**: Build the Jinja2 templates for CLI generation
2. **Define Complete Semantics**: Expand weavergen_cli.yaml with all commands
3. **Build Post-Processor**: Create tool to inject implementations
4. **Generate and Test**: Generate CLI and validate against current implementation
5. **Iterate**: Refine templates based on generation results