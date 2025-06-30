#!/usr/bin/env python3
"""
Generate semantic conventions from natural language using LLMs
This is the initial implementation before Forge generates itself
"""

import typer
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from typing import List, Dict, Any, Optional
import yaml
import subprocess
import asyncio
from pathlib import Path
from enum import Enum

app = typer.Typer(help="Generate OpenTelemetry semantic conventions using LLMs")

# Pydantic models for semantic conventions
class AttributeType(str, Enum):
    STRING = "string"
    INT = "int"
    DOUBLE = "double"
    BOOLEAN = "boolean"
    STRING_ARRAY = "string[]"
    INT_ARRAY = "int[]"
    DOUBLE_ARRAY = "double[]"
    BOOLEAN_ARRAY = "boolean[]"

class RequirementLevel(str, Enum):
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPT_IN = "opt_in"

class Stability(str, Enum):
    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"

class GroupType(str, Enum):
    SPAN = "span"
    METRIC = "metric"
    ATTRIBUTE_GROUP = "attribute_group"
    RESOURCE = "resource"
    EVENT = "event"

class SpanKind(str, Enum):
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"

class Attribute(BaseModel):
    id: str = Field(..., description="Attribute identifier using dot notation")
    type: AttributeType = Field(..., description="Attribute data type")
    requirement_level: RequirementLevel = Field(default=RequirementLevel.RECOMMENDED)
    brief: str = Field(..., description="Brief description of the attribute")
    examples: Optional[List[Any]] = Field(default=None, description="Example values")
    note: Optional[str] = Field(default=None, description="Additional notes")

class Group(BaseModel):
    id: str = Field(..., description="Group identifier")
    type: GroupType = Field(..., description="Type of semantic convention group")
    brief: str = Field(..., description="Brief description")
    stability: Stability = Field(default=Stability.EXPERIMENTAL)
    note: Optional[str] = None
    prefix: Optional[str] = None
    extends: Optional[str] = None
    span_kind: Optional[SpanKind] = None
    attributes: Optional[List[Attribute]] = None

class SemanticConvention(BaseModel):
    groups: List[Group]

class SemanticGenerator:
    """Generate semantic conventions using LLMs"""
    
    def __init__(self, model: str = "llama3.2", temperature: float = 0.1):
        self.model = model
        self.temperature = temperature
        self.system_prompt = """You are an OpenTelemetry semantic convention expert.
        
Generate semantic conventions following these rules:
1. Use proper group types: span, metric, attribute_group, resource, event
2. For operations, create both an attribute_group and a span that extends it
3. Use dot notation for IDs (e.g., 'service.operation.detail')
4. Include stability markers (experimental, stable, deprecated)
5. Use only valid attribute types: string, int, double, boolean, and their array versions
6. Follow OpenTelemetry naming conventions

Structure example:
- First group: attribute_group with shared attributes
- Second group: span that extends the attribute_group
- Include proper span_kind for spans (internal, server, client, producer, consumer)
"""
        
    async def generate(self, description: str) -> SemanticConvention:
        """Generate semantic convention from description"""
        try:
            model = OllamaModel(self.model)
            agent = Agent(
                model,
                result_type=SemanticConvention,
                system_prompt=self.system_prompt
            )
            
            prompt = f"""Generate OpenTelemetry semantic convention for: {description}

Remember to:
- Create attribute_group for shared attributes
- Create span/metric groups that extend the attribute_group
- Use proper requirement levels (required, recommended, opt_in)
- Include meaningful examples for attributes
- Add documentation in brief and note fields"""
            
            result = await agent.run(prompt)
            return result.data
            
        except Exception as e:
            typer.echo(f"❌ LLM generation failed: {e}", err=True)
            # Return minimal valid structure
            return SemanticConvention(groups=[
                Group(
                    id="generated.operation",
                    type=GroupType.SPAN,
                    brief=description,
                    stability=Stability.EXPERIMENTAL
                )
            ])
    
    def to_yaml(self, convention: SemanticConvention) -> str:
        """Convert semantic convention to YAML"""
        # Convert Pydantic model to dict and clean up
        data = convention.model_dump(exclude_none=True, mode="json")
        
        # Ensure examples are properly formatted
        for group in data.get("groups", []):
            if "attributes" in group:
                for attr in group["attributes"]:
                    # Ensure examples match the type
                    if "examples" in attr and attr["examples"]:
                        attr_type = attr.get("type", "string")
                        if attr_type in ["int", "double", "boolean"]:
                            # Keep examples as-is for primitive types
                            pass
                        elif attr_type.endswith("[]"):
                            # Ensure array types have array examples
                            if not isinstance(attr["examples"][0], list):
                                attr["examples"] = [attr["examples"]]
        
        return yaml.dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True)
    
    def validate(self, yaml_file: str) -> tuple[bool, Optional[str]]:
        """Validate semantic convention with Weaver"""
        try:
            result = subprocess.run(
                ["weaver", "registry", "check", "-r", yaml_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr or result.stdout
                
        except FileNotFoundError:
            return False, "Weaver CLI not found. Please install Weaver."
        except Exception as e:
            return False, str(e)

@app.command()
def generate(
    description: str = typer.Argument(..., help="Natural language description of what to generate"),
    output: str = typer.Option("semantic.yaml", "--output", "-o", help="Output file path"),
    model: str = typer.Option("llama3.2", "--model", "-m", help="LLM model to use"),
    temperature: float = typer.Option(0.1, "--temperature", "-t", help="LLM temperature (0.0-1.0)"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate with Weaver"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Generate OpenTelemetry semantic convention from natural language description"""
    
    typer.echo(f"🤖 Generating semantic convention for: {description}")
    
    # Initialize generator
    generator = SemanticGenerator(model=model, temperature=temperature)
    
    # Generate semantic convention
    if verbose:
        typer.echo(f"   Using model: {model} (temperature: {temperature})")
    
    convention = asyncio.run(generator.generate(description))
    
    # Convert to YAML
    yaml_content = generator.to_yaml(convention)
    
    # Write to file
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml_content)
    
    typer.echo(f"✅ Generated: {output}")
    
    if verbose:
        typer.echo(f"\n📄 Content preview:")
        lines = yaml_content.split('\n')[:20]
        for line in lines:
            typer.echo(f"   {line}")
        if len(yaml_content.split('\n')) > 20:
            typer.echo("   ...")
    
    # Validate if requested
    if validate:
        typer.echo(f"\n🔍 Validating with Weaver...")
        is_valid, error = generator.validate(str(output_path))
        
        if is_valid:
            typer.echo("✅ Validation passed!")
        else:
            typer.echo(f"❌ Validation failed: {error}", err=True)
            raise typer.Exit(1)
    
    typer.echo(f"\n✨ Success! Semantic convention saved to: {output}")

@app.command()
def validate(
    file: str = typer.Argument(..., help="Semantic convention YAML file to validate")
):
    """Validate a semantic convention file with Weaver"""
    
    typer.echo(f"🔍 Validating: {file}")
    
    generator = SemanticGenerator()
    is_valid, error = generator.validate(file)
    
    if is_valid:
        typer.echo("✅ Validation passed!")
    else:
        typer.echo(f"❌ Validation failed:\n{error}", err=True)
        raise typer.Exit(1)

@app.command()
def example():
    """Show example semantic conventions"""
    
    examples = {
        "HTTP Server": "HTTP server request handling with method, path, status code, and duration",
        "Database": "Database query operations with statement, rows affected, and connection pool metrics",
        "Message Queue": "Message queue producer and consumer with topic, partition, and offset tracking",
        "Cache": "Cache operations with hit/miss rates, eviction metrics, and key patterns",
        "AI/LLM": "LLM inference with model, tokens, latency, and prompt characteristics"
    }
    
    typer.echo("📚 Example semantic convention descriptions:\n")
    
    for name, desc in examples.items():
        typer.echo(f"  {name}:")
    typer.echo(f"    {desc}")
        typer.echo()
    
    typer.echo("💡 Usage example:")
    typer.echo('  python generate_semantic.py "HTTP server request handling" -o http_server.yaml')

if __name__ == "__main__":
    app()