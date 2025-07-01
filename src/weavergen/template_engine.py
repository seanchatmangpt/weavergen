#!/usr/bin/env python3
"""
WeaverGen Template Engine
Generates code from semantic conventions using Jinja2 templates
"""

from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Dict, Any, List
import uuid
from datetime import datetime

class WeaverGenTemplateEngine:
    """80/20 template engine for code generation"""
    
    def __init__(self, template_dir: Path = None):
        self.template_dir = template_dir or Path("templates")
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Create default templates if they don't exist
        self._ensure_default_templates()
    
    def generate_pydantic_models(self, convention: Dict[str, Any]) -> str:
        """Generate Pydantic models from convention"""
        
        template = self.env.get_template('pydantic_models.j2')
        
        context = {
            'convention': convention,
            'timestamp': datetime.now().isoformat(),
            'generator': 'WeaverGen Template Engine'
        }
        
        return template.render(**context)
    
    def generate_validators(self, convention: Dict[str, Any]) -> str:
        """Generate validation logic from convention"""
        
        template = self.env.get_template('validators.j2')
        
        context = {
            'convention': convention,
            'timestamp': datetime.now().isoformat()
        }
        
        return template.render(**context)
    
    def generate_cli_commands(self, convention: Dict[str, Any]) -> str:
        """Generate CLI commands for convention"""
        
        template = self.env.get_template('cli_commands.j2')
        
        context = {
            'convention': convention,
            'timestamp': datetime.now().isoformat()
        }
        
        return template.render(**context)
    
    def _ensure_default_templates(self):
        """Create default templates if they don't exist"""
        
        templates = {
            'pydantic_models.j2': self._get_pydantic_template(),
            'validators.j2': self._get_validator_template(),
            'cli_commands.j2': self._get_cli_template()
        }
        
        for template_name, template_content in templates.items():
            template_file = self.template_dir / template_name
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    f.write(template_content)
    
    def _get_pydantic_template(self) -> str:
        return """# Generated Pydantic Models
# Convention: {{ convention.name }}
# Generated: {{ timestamp }}

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

{% for group in convention.groups %}
class {{ group.id | title | replace('.', '') }}Model(BaseModel):
    """{{ group.brief }}"""
    
{% for attr in group.attributes %}
    {{ attr.id.split('.')[-1] }}: {% if attr.requirement_level == 'required' %}{{ attr.type }}{% else %}Optional[{{ attr.type }}]{% endif %} = Field(
        {% if attr.requirement_level != 'required' %}default=None, {% endif %}
        description="{{ attr.brief }}"
    )
{% endfor %}
    
{% endfor %}
"""
    
    def _get_validator_template(self) -> str:
        return """# Generated Validators
# Convention: {{ convention.name }}
# Generated: {{ timestamp }}

from typing import Dict, Any, List

class {{ convention.name | title | replace('.', '') }}Validator:
    """Validator for {{ convention.name }} convention"""
    
    def validate_span(self, span: Dict[str, Any]) -> List[str]:
        """Validate span against convention"""
        issues = []
        
        attributes = span.get('attributes', {})
        
{% for group in convention.groups %}
{% for attr in group.attributes %}
{% if attr.requirement_level == 'required' %}
        if '{{ attr.id }}' not in attributes:
            issues.append("Missing required attribute: {{ attr.id }}")
{% endif %}
{% endfor %}
{% endfor %}
        
        return issues
"""
    
    def _get_cli_template(self) -> str:
        return """# Generated CLI Commands
# Convention: {{ convention.name }}
# Generated: {{ timestamp }}

import typer
from typing import Optional

app = typer.Typer()

@app.command()
def generate_{{ convention.name.replace('.', '_') }}(
    output_dir: Optional[str] = typer.Option("generated", help="Output directory")
):
    """Generate code for {{ convention.name }} convention"""
    typer.echo(f"Generating {{ convention.name }} code to {output_dir}")
    # Implementation here

if __name__ == "__main__":
    app()
"""
