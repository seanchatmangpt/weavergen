#!/usr/bin/env python3
"""
WeaverGen Semantic Convention Parser
Parses OpenTelemetry semantic conventions from YAML/JSON
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class ParsedConvention:
    """Parsed semantic convention"""
    name: str
    type: str = "span"
    brief: str = ""
    stability: str = "stable"
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    groups: List[Dict[str, Any]] = field(default_factory=list)

class SemanticConventionParser:
    """80/20 parser for semantic conventions"""
    
    def parse_convention_file(self, file_path: Path) -> ParsedConvention:
        """Parse convention from YAML/JSON file"""
        
        if not file_path.exists():
            raise FileNotFoundError(f"Convention file not found: {file_path}")
        
        with open(file_path) as f:
            if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        # Extract convention metadata
        convention = ParsedConvention(
            name=file_path.stem,
            type=data.get('type', 'span'),
            brief=data.get('brief', ''),
            stability=data.get('stability', 'stable')
        )
        
        # Parse groups (main structure)
        if 'groups' in data:
            convention.groups = data['groups']
            # Extract all attributes from groups
            for group in convention.groups:
                if 'attributes' in group:
                    convention.attributes.extend(group['attributes'])
        
        # Direct attributes (fallback)
        if 'attributes' in data:
            convention.attributes.extend(data['attributes'])
        
        return convention
    
    def validate_convention(self, convention: ParsedConvention) -> List[str]:
        """Validate parsed convention"""
        issues = []
        
        if not convention.name:
            issues.append("Convention name is required")
        
        if not convention.attributes:
            issues.append("Convention must have attributes")
        
        # Validate attributes
        for attr in convention.attributes:
            if 'id' not in attr:
                issues.append(f"Attribute missing 'id': {attr}")
            if 'type' not in attr:
                issues.append(f"Attribute missing 'type': {attr.get('id', 'unknown')}")
        
        return issues
