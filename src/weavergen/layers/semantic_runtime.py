#!/usr/bin/env python3
"""
WeaverGen Runtime Layer Extension  
Semantic convention processing runtime
"""

import asyncio
from pathlib import Path
from typing import Dict, Any
from .semantic_parser import SemanticConventionParser
from .template_engine import WeaverGenTemplateEngine

class SemanticConventionRuntime:
    """Runtime engine for semantic convention processing"""
    
    def __init__(self):
        self.parser = SemanticConventionParser()
        self.template_engine = WeaverGenTemplateEngine()
    
    async def process_convention(self, convention_file: Path, output_dir: Path) -> Dict[str, Any]:
        """Process semantic convention and generate code"""
        
        # Parse convention
        convention = self.parser.parse_convention_file(convention_file)
        
        # Validate convention
        issues = self.parser.validate_convention(convention)
        if issues:
            return {"success": False, "errors": issues}
        
        # Generate code
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # Generate Pydantic models
        models_code = self.template_engine.generate_pydantic_models(convention.__dict__)
        models_file = output_dir / f"{convention.name}_models.py"
        with open(models_file, 'w') as f:
            f.write(models_code)
        generated_files.append(str(models_file))
        
        # Generate validators
        validators_code = self.template_engine.generate_validators(convention.__dict__)
        validators_file = output_dir / f"{convention.name}_validators.py"
        with open(validators_file, 'w') as f:
            f.write(validators_code)
        generated_files.append(str(validators_file))
        
        return {
            "success": True,
            "generated_files": generated_files,
            "convention": convention.name
        }
