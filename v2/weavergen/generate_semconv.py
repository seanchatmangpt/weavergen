#!/usr/bin/env python
"""Generate semantic convention constants from weavergen_system.yaml"""

import yaml
from pathlib import Path

def generate_semconv():
    # Read the semantic convention file
    with open("../../semantic_conventions/weavergen_system.yaml") as f:
        data = yaml.safe_load(f)
    
    # Create output directory
    output_dir = Path("src/weavergen/semconv")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate attributes file
    attributes_py = output_dir / "attributes.py"
    with open(attributes_py, "w") as f:
        f.write('"""Generated semantic convention attributes for WeaverGen."""\n\n')
        
        # Generate attribute constants
        for group in data.get("groups", []):
            prefix = group.get("prefix", "")
            f.write(f"\n# {group.get('brief', '')}\n")
            
            for attr in group.get("attributes", []):
                attr_id = attr.get("id", "")
                const_name = attr_id.upper().replace(".", "_")
                full_name = f"{prefix}.{attr_id}" if prefix else attr_id
                
                f.write(f'{const_name} = "{full_name}"\n')
                
                # Generate enum values if present
                if "type" in attr and isinstance(attr["type"], dict):
                    members = attr["type"].get("members", [])
                    if members:
                        f.write(f"\n# Values for {full_name}\n")
                        for member in members:
                            member_const = f"{const_name}__{member['id'].upper()}"
                            f.write(f'{member_const} = "{member["value"]}"\n')
                        f.write("\n")
    
    print(f"✓ Generated {attributes_py}")
    
    # Generate __init__.py
    init_py = output_dir / "__init__.py"
    with open(init_py, "w") as f:
        f.write('"""WeaverGen semantic conventions."""\n\n')
        f.write('from .attributes import *\n')
    
    print(f"✓ Generated {init_py}")

if __name__ == "__main__":
    generate_semconv()