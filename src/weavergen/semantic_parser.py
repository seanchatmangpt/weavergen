"""
Direct Semantic Convention Parser - Bypass Weaver Dependency

This module provides direct YAML parsing of OpenTelemetry semantic conventions,
eliminating the need for the Weaver binary during development.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass
import re


class Attribute(BaseModel):
    """Represents a semantic convention attribute."""
    name: str
    type: str
    brief: str
    examples: Optional[List[Any]] = None
    required: Optional[bool] = False
    deprecated: Optional[bool] = False
    note: Optional[str] = None
    
    @property
    def python_name(self) -> str:
        """Convert attribute name to Python-safe identifier."""
        return self.name.replace('.', '_').replace('-', '_')
    
    @property
    def python_type(self) -> str:
        """Map semantic type to Python type."""
        type_mapping = {
            'string': 'str',
            'int': 'int',
            'double': 'float',
            'boolean': 'bool',
            'string[]': 'List[str]',
            'int[]': 'List[int]',
        }
        return type_mapping.get(self.type, 'Any')


class SemanticConvention(BaseModel):
    """Represents a complete semantic convention."""
    id: str
    type: str  # span, metric, event, resource
    brief: str
    prefix: Optional[str] = None
    extends: Optional[str] = None
    attributes: List[Attribute] = Field(default_factory=list)
    constraints: Optional[Dict[str, Any]] = None
    
    @property
    def class_name(self) -> str:
        """Generate Python class name from convention ID."""
        parts = self.id.split('.')
        return ''.join(word.capitalize() for word in parts) + 'Convention'


class SemanticConventionParser:
    """Parser for OpenTelemetry semantic convention YAML files."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path("semantic-conventions/model/registry")
        self.conventions: Dict[str, SemanticConvention] = {}
    
    def parse_file(self, yaml_path: Path) -> List[SemanticConvention]:
        """Parse a single YAML file containing semantic conventions."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        conventions = []
        for group in data.get('groups', []):
            convention = self._parse_group(group)
            if convention:
                conventions.append(convention)
                self.conventions[convention.id] = convention
        
        return conventions
    
    def parse_directory(self, directory: Path) -> List[SemanticConvention]:
        """Parse all YAML files in a directory."""
        all_conventions = []
        for yaml_file in directory.glob("**/*.yaml"):
            try:
                conventions = self.parse_file(yaml_file)
                all_conventions.extend(conventions)
            except Exception as e:
                print(f"Error parsing {yaml_file}: {e}")
        
        return all_conventions
    
    def _parse_group(self, group: Dict[str, Any]) -> Optional[SemanticConvention]:
        """Parse a single group into a SemanticConvention."""
        if 'id' not in group:
            return None
        
        attributes = []
        for attr_data in group.get('attributes', []):
            # Handle attribute references
            if isinstance(attr_data, str):
                # This is a reference to another attribute
                attr = self._resolve_attribute_ref(attr_data)
                if attr:
                    attributes.append(attr)
            else:
                # Direct attribute definition
                attr = self._parse_attribute(attr_data)
                if attr:
                    attributes.append(attr)
        
        return SemanticConvention(
            id=group['id'],
            type=group.get('type', 'span'),
            brief=group.get('brief', ''),
            prefix=group.get('prefix'),
            extends=group.get('extends'),
            attributes=attributes,
            constraints=group.get('constraints')
        )
    
    def _parse_attribute(self, attr_data: Dict[str, Any]) -> Optional[Attribute]:
        """Parse attribute data into an Attribute model."""
        if 'id' not in attr_data:
            return None
        
        return Attribute(
            name=attr_data['id'],
            type=attr_data.get('type', 'string'),
            brief=attr_data.get('brief', ''),
            examples=attr_data.get('examples'),
            required=attr_data.get('requirement_level') == 'required',
            deprecated=attr_data.get('deprecated'),
            note=attr_data.get('note')
        )
    
    def _resolve_attribute_ref(self, ref: str) -> Optional[Attribute]:
        """Resolve an attribute reference to actual attribute data."""
        # Simple implementation - would need enhancement for full resolution
        # This is where we'd look up the referenced attribute
        return None
    
    def generate_pydantic_models(self, conventions: List[SemanticConvention]) -> str:
        """Generate Pydantic model code from conventions."""
        code_lines = [
            '"""Generated Pydantic models for OpenTelemetry semantic conventions."""',
            '',
            'from typing import Optional, List, Any',
            'from pydantic import BaseModel, Field',
            '',
            ''
        ]
        
        for convention in conventions:
            # Generate class
            code_lines.append(f'class {convention.class_name}(BaseModel):')
            code_lines.append(f'    """{convention.brief}"""')
            
            # Generate fields
            for attr in convention.attributes:
                field_line = f'    {attr.python_name}: '
                if not attr.required:
                    field_line += f'Optional[{attr.python_type}]'
                    default = ' = None'
                else:
                    field_line += attr.python_type
                    default = ''
                
                # Add Field with description
                field_line += f' = Field({default}, description="{attr.brief}")'
                code_lines.append(field_line)
            
            code_lines.append('')
            code_lines.append('')
        
        return '\n'.join(code_lines)


# Example usage and testing
if __name__ == "__main__":
    parser = SemanticConventionParser()
    
    # Test with a simple convention
    test_convention = SemanticConvention(
        id="http.request",
        type="span",
        brief="HTTP request attributes",
        attributes=[
            Attribute(
                name="http.method",
                type="string",
                brief="HTTP request method",
                required=True
            ),
            Attribute(
                name="http.status_code",
                type="int",
                brief="HTTP response status code",
                required=False
            )
        ]
    )
    
    # Generate code
    code = parser.generate_pydantic_models([test_convention])
    print(code)