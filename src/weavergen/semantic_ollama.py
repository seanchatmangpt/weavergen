"""Semantic convention generation using Pydantic AI with Ollama."""

from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path
import yaml

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from .models import ValidationResult


class AttributeType(str, Enum):
    """Valid attribute types in semantic conventions."""
    STRING = "string"
    INT = "int"
    DOUBLE = "double"
    BOOLEAN = "boolean"
    STRING_ARRAY = "string[]"
    INT_ARRAY = "int[]"
    DOUBLE_ARRAY = "double[]"
    BOOLEAN_ARRAY = "boolean[]"


class RequirementLevel(str, Enum):
    """Requirement levels for attributes."""
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPT_IN = "opt_in"


class Stability(str, Enum):
    """Stability levels for semantic conventions."""
    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


class GroupType(str, Enum):
    """Types of semantic convention groups."""
    SPAN = "span"
    METRIC = "metric"
    ATTRIBUTE_GROUP = "attribute_group"
    RESOURCE = "resource"
    EVENT = "event"


class SpanKind(str, Enum):
    """OpenTelemetry span kinds."""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class Attribute(BaseModel):
    """Semantic convention attribute definition."""
    
    id: str = Field(..., description="Attribute identifier using dot notation")
    type: AttributeType = Field(..., description="Attribute data type")
    requirement_level: RequirementLevel = Field(default=RequirementLevel.RECOMMENDED)
    brief: str = Field(..., description="Brief description of the attribute")
    examples: Optional[List[Any]] = Field(default=None, description="Example values")
    note: Optional[str] = Field(default=None, description="Additional notes")


class Group(BaseModel):
    """Semantic convention group definition."""
    
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
    """Complete semantic convention definition."""
    
    groups: List[Group]


class SemanticGenerator:
    """Generate semantic conventions using Pydantic AI with Ollama."""
    
    def __init__(
        self,
        model: str = "llama3.2",
        temperature: float = 0.1,
        base_url: str = "http://localhost:11434/v1",
    ):
        """Initialize semantic generator with Ollama model.
        
        Args:
            model: Ollama model name (e.g., "llama3.2", "qwen2.5-coder:7b")
            temperature: Model temperature for generation
            base_url: Ollama server URL
        """
        self.model_name = model
        self.temperature = temperature
        self.base_url = base_url
        
        # Create Ollama model using OpenAI-compatible API
        ollama_model = OpenAIModel(
            model_name=model,
            provider=OpenAIProvider(base_url=base_url),
        )
        
        # Create agent with structured output
        self.agent = Agent(
            model=ollama_model,
            output_type=SemanticConvention,
            instructions=self._get_system_prompt(),
            model_settings={"temperature": temperature},
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for semantic generation."""
        return """You are an OpenTelemetry semantic convention expert.

Generate semantic conventions following these rules:
1. Use proper group types: span, metric, attribute_group, resource, event
2. For operations, create both an attribute_group and a span that extends it
3. Use dot notation for IDs (e.g., 'service.operation.detail')
4. Include stability markers (experimental, stable, deprecated)
5. Use only valid attribute types: string, int, double, boolean, and their array versions
6. Follow OpenTelemetry naming conventions
7. Include proper span_kind for spans (internal, server, client, producer, consumer)

Structure example:
- First group: attribute_group with shared attributes
- Second group: span that extends the attribute_group

Generate comprehensive, well-structured semantic conventions that follow OpenTelemetry standards."""
    
    async def generate(self, description: str) -> SemanticConvention:
        """Generate semantic convention from natural language description.
        
        Args:
            description: Natural language description of desired conventions
            
        Returns:
            Generated semantic convention
        """
        prompt = f"""Generate OpenTelemetry semantic conventions for: {description}

Create a complete semantic convention with:
1. Attribute group for shared attributes
2. Span group(s) for operations
3. Relevant metrics if applicable
4. Proper attribute types and requirement levels
5. Clear, descriptive briefs
6. Example values where helpful"""
        
        result = await self.agent.run(prompt)
        return result.data
    
    def save_to_yaml(self, convention: SemanticConvention, output_path: Path) -> None:
        """Save semantic convention to YAML file.
        
        Args:
            convention: Semantic convention to save
            output_path: Path to output YAML file
        """
        # Convert to dict format expected by Weaver
        yaml_data = {
            "groups": [
                {
                    "id": group.id,
                    "type": group.type.value,
                    "brief": group.brief,
                    "stability": group.stability.value,
                    **({"note": group.note} if group.note else {}),
                    **({"prefix": group.prefix} if group.prefix else {}),
                    **({"extends": group.extends} if group.extends else {}),
                    **({"span_kind": group.span_kind.value} if group.span_kind else {}),
                    **({"attributes": [
                        {
                            "id": attr.id,
                            "type": attr.type.value,
                            "requirement_level": attr.requirement_level.value,
                            "brief": attr.brief,
                            **({"examples": attr.examples} if attr.examples else {}),
                            **({"note": attr.note} if attr.note else {}),
                        }
                        for attr in group.attributes
                    ]} if group.attributes else {}),
                }
                for group in convention.groups
            ]
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
    
    def validate_semantic(self, yaml_path: Path) -> ValidationResult:
        """Validate a semantic convention YAML file.
        
        Args:
            yaml_path: Path to YAML file to validate
            
        Returns:
            Validation result
        """
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            
            errors = []
            warnings = []
            
            # Basic structure validation
            if not isinstance(data, dict) or 'groups' not in data:
                errors.append("YAML must contain 'groups' key")
                return ValidationResult(
                    valid=False,
                    errors=errors,
                    warnings=warnings,
                    checked_files=[str(yaml_path)]
                )
            
            # Validate each group
            for i, group in enumerate(data.get('groups', [])):
                if not isinstance(group, dict):
                    errors.append(f"Group {i} must be a dictionary")
                    continue
                
                # Required fields
                if 'id' not in group:
                    errors.append(f"Group {i} missing required 'id' field")
                if 'type' not in group:
                    errors.append(f"Group {i} missing required 'type' field")
                elif group['type'] not in [t.value for t in GroupType]:
                    errors.append(f"Group {i} has invalid type: {group['type']}")
                
                # Validate attributes
                for j, attr in enumerate(group.get('attributes', [])):
                    if not isinstance(attr, dict):
                        errors.append(f"Group {i} attribute {j} must be a dictionary")
                        continue
                    
                    if 'id' not in attr:
                        errors.append(f"Group {i} attribute {j} missing 'id'")
                    if 'type' not in attr:
                        errors.append(f"Group {i} attribute {j} missing 'type'")
                    elif attr['type'] not in [t.value for t in AttributeType]:
                        errors.append(f"Group {i} attribute {j} has invalid type: {attr['type']}")
            
            return ValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                checked_files=[str(yaml_path)]
            )
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Failed to validate: {str(e)}"],
                warnings=[],
                checked_files=[str(yaml_path)]
            )