#!/usr/bin/env python3
"""
Demo script showing how Weaver would generate the tool-based CLI structure
from semantic conventions.

This simulates the Weaver generation process without requiring the actual
Weaver binary.
"""

import yaml
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List, Any

def load_semantic_conventions(file_path: Path) -> Dict[str, Any]:
    """Load semantic conventions from YAML file."""
    with open(file_path) as f:
        return yaml.safe_load(f)

def setup_jinja_env() -> Environment:
    """Setup Jinja2 environment with filters."""
    env = Environment(
        loader=FileSystemLoader("templates/cli"),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Add custom filters
    def selectattr_equalto(seq, attr, value):
        """Select items where attribute equals value."""
        return [item for item in seq if any(
            a.get("id") == attr and a.get("value") == value 
            for a in item.get("attributes", [])
        )]
    
    def attr_value(item, attr_id):
        """Get attribute value by ID."""
        for attr in item.get("attributes", []):
            if attr.get("id") == attr_id:
                return attr.get("value")
        return None
    
    env.filters["selectattr_equalto"] = selectattr_equalto
    env.filters["attr_value"] = attr_value
    
    return env

def generate_main_cli(groups: List[Dict], output_dir: Path):
    """Generate main CLI application."""
    env = setup_jinja_env()
    template = env.get_template("tool_cli_main.j2")
    
    # Filter for application group
    app_groups = [g for g in groups if g.get("type") == "application"]
    command_groups = [g for g in groups if g.get("type") == "command_group"]
    
    content = template.render(groups=groups)
    
    output_file = output_dir / "cli_generated.py"
    output_file.write_text(content)
    print(f"✅ Generated main CLI: {output_file}")

def generate_tool_commands(groups: List[Dict], output_dir: Path):
    """Generate tool command groups."""
    env = setup_jinja_env()
    template = env.get_template("tool_command_group.j2")
    
    # Create tools directory
    tools_dir = output_dir / "tools"
    tools_dir.mkdir(exist_ok=True)
    
    # Generate each tool command group
    command_groups = [g for g in groups if g.get("type") == "command_group"]
    
    for tool_group in command_groups:
        # Get tool name
        tool_name = None
        for attr in tool_group.get("attributes", []):
            if attr.get("id") == "tool.name":
                tool_name = attr.get("value")
                break
        
        if not tool_name:
            continue
            
        # Render template
        content = template.render(
            groups=groups,
            tool_group=tool_group
        )
        
        # Write to file
        output_file = tools_dir / f"{tool_name}.py"
        output_file.write_text(content)
        print(f"✅ Generated tool: {output_file}")

def generate_cli_metrics(groups: List[Dict], output_dir: Path):
    """Generate CLI metrics instrumentation."""
    metrics = [g for g in groups if g.get("type") == "metric"]
    
    if not metrics:
        return
    
    # Simple metrics template
    content = '''"""CLI Metrics instrumentation generated from semantic conventions"""

from opentelemetry import metrics

meter = metrics.get_meter("weavergen.cli")

'''
    
    for metric in metrics:
        metric_id = metric.get("id", "").replace(".", "_")
        brief = metric.get("brief", "")
        unit = metric.get("unit", "1")
        instrument = metric.get("instrument", "counter")
        
        content += f'''{metric_id} = meter.create_{instrument}(
    name="{metric_id}",
    description="{brief}",
    unit="{unit}"
)

'''
    
    output_file = output_dir / "cli_metrics.py"
    output_file.write_text(content)
    print(f"✅ Generated metrics: {output_file}")

def main():
    """Main generation function."""
    print("🌟 WeaverGen CLI Generation Demo")
    print("=" * 50)
    
    # Load semantic conventions
    semantic_file = Path("semantic_conventions/weavergen_tool_cli.yaml")
    if not semantic_file.exists():
        print(f"❌ Semantic conventions file not found: {semantic_file}")
        return
    
    data = load_semantic_conventions(semantic_file)
    groups = data.get("groups", [])
    
    print(f"📋 Loaded {len(groups)} semantic convention groups")
    
    # Create output directory
    output_dir = Path("generated_cli")
    output_dir.mkdir(exist_ok=True)
    
    # Generate CLI components
    try:
        generate_main_cli(groups, output_dir)
        generate_tool_commands(groups, output_dir)
        generate_cli_metrics(groups, output_dir)
        
        print("\n🎉 CLI generation completed successfully!")
        print(f"📁 Output directory: {output_dir.absolute()}")
        
        # Show structure
        print("\n📂 Generated structure:")
        for file in sorted(output_dir.rglob("*.py")):
            print(f"   {file.relative_to(output_dir)}")
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        raise

if __name__ == "__main__":
    main()