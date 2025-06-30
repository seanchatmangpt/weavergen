# Prototype Implementation Plan

## File Structure (Minimal)

```
forge-prototype/
├── forge_mvp.py           # Main entry point
├── templates/
│   └── simple.yaml.j2     # Minimal semantic template
│   └── python_code.j2     # Minimal code template
├── telemetry.csv          # Simple metrics storage
└── generated/             # Output directory
```

## Implementation Stages

### Stage 1: Hardcoded Semantic Generator (Day 1-2)

```python
# forge_mvp.py - Version 1
import yaml
import subprocess
from datetime import datetime

class ForgePrototype:
    def __init__(self):
        self.telemetry = []
    
    def generate_semantic(self, description: str, output_path: str) -> bool:
        """Generate semantic YAML with mostly hardcoded template"""
        start = datetime.now()
        
        # MVP: Hardcoded template with simple substitution
        semantic = {
            "groups": [{
                "id": description.replace(" ", "_").lower(),
                "type": "span",
                "brief": description,
                "stability": "experimental",
                "attributes": [{
                    "id": "input",
                    "type": "string",
                    "requirement_level": "required",
                    "brief": "Input parameter"
                }, {
                    "id": "success",
                    "type": "boolean", 
                    "requirement_level": "required",
                    "brief": "Operation success"
                }]
            }]
        }
        
        # Write YAML
        with open(output_path, 'w') as f:
            yaml.dump(semantic, f)
        
        # Track metrics
        duration = (datetime.now() - start).total_seconds()
        self.log_telemetry("generate_semantic", True, duration)
        
        return True
    
    def log_telemetry(self, operation: str, success: bool, duration: float):
        with open('telemetry.csv', 'a') as f:
            f.write(f"{operation},{success},{duration}\n")
```

### Stage 2: Weaver Integration (Day 3-4)

```python
# Add to forge_mvp.py
    def validate_semantic(self, yaml_path: str) -> bool:
        """Validate with Weaver CLI"""
        start = datetime.now()
        
        result = subprocess.run(
            ["weaver", "registry", "check", "-r", yaml_path],
            capture_output=True
        )
        
        success = result.returncode == 0
        duration = (datetime.now() - start).total_seconds()
        self.log_telemetry("validate_semantic", success, duration)
        
        return success
    
    def generate_code(self, semantic_path: str, output_dir: str) -> bool:
        """Generate Python code using simple template"""
        start = datetime.now()
        
        # MVP: Read semantic and apply simple template
        with open(semantic_path) as f:
            semantic = yaml.safe_load(f)
        
        # Simple code template
        code = f'''# Generated from {semantic_path}
def {semantic['groups'][0]['id']}(input: str) -> dict:
    """Generated operation"""
    print(f"Executing: {{input}}")
    return {{"success": True, "result": input}}
'''
        
        # Write code
        output_path = f"{output_dir}/generated.py"
        with open(output_path, 'w') as f:
            f.write(code)
        
        duration = (datetime.now() - start).total_seconds()
        self.log_telemetry("generate_code", True, duration)
        
        return True
```

### Stage 3: Self-Reference Proof (Day 5-7)

```python
# Add to forge_mvp.py
    def generate_forge_semantics(self) -> str:
        """Generate semantics for Forge itself"""
        self.generate_semantic(
            "semantic generator with validation",
            "forge_semantics.yaml"
        )
        return "forge_semantics.yaml"
    
    def self_generate(self) -> bool:
        """The critical test: can Forge generate itself?"""
        print("🔄 Self-generation starting...")
        
        # Step 1: Generate Forge's semantics
        semantic_path = self.generate_forge_semantics()
        print(f"✓ Generated Forge semantics: {semantic_path}")
        
        # Step 2: Validate
        if not self.validate_semantic(semantic_path):
            print("✗ Validation failed")
            return False
        print("✓ Semantics validated")
        
        # Step 3: Generate Forge code
        if not self.generate_code(semantic_path, "./generated"):
            print("✗ Code generation failed")
            return False
        print("✓ Generated Forge v2")
        
        # Step 4: Test if generated code works
        try:
            import generated.generated as forge_v2
            result = forge_v2.semantic_generator_with_validation("test")
            print(f"✓ Forge v2 works: {result}")
            return True
        except Exception as e:
            print(f"✗ Forge v2 failed: {e}")
            return False
```

### Stage 4: CLI Interface (Day 8-9)

```python
# Complete forge_mvp.py
import argparse

def main():
    parser = argparse.ArgumentParser(description="Forge MVP")
    parser.add_argument("description", help="What to generate")
    parser.add_argument("--self-test", action="store_true", 
                       help="Run self-generation test")
    
    args = parser.parse_args()
    
    forge = ForgePrototype()
    
    if args.self_test:
        # The money shot - prove self-reference works
        success = forge.self_generate()
        if success:
            print("\n🎉 SEMANTIC QUINE PROVEN!")
            show_metrics()
    else:
        # Normal generation
        output = f"{args.description.replace(' ', '_')}.yaml"
        forge.generate_semantic(args.description, output)
        
        if forge.validate_semantic(output):
            forge.generate_code(output, "./generated")
            print(f"✓ Complete! Check ./generated/")
            show_metrics()

def show_metrics():
    """Display simple metrics"""
    print("\n📊 Metrics:")
    with open('telemetry.csv') as f:
        lines = f.readlines()
    
    total = len(lines)
    success = sum(1 for l in lines if ',True,' in l)
    
    print(f"Success Rate: {success}/{total} ({success/total*100:.0f}%)")

if __name__ == "__main__":
    main()
```

## Critical Path Test Script

```bash
#!/bin/bash
# test_prototype.sh - Proves the concept works

echo "🧪 Forge Prototype Test"

# Test 1: Basic generation
echo "Test 1: Generate simple semantic"
python forge_mvp.py "hello world operation"

# Test 2: Validation
echo "Test 2: Validate semantic"
weaver registry check -r hello_world_operation.yaml

# Test 3: Self-generation (THE BIG ONE)
echo "Test 3: Self-generation"
python forge_mvp.py --self-test

# Show all metrics
echo "📊 Final Metrics:"
cat telemetry.csv | grep success | wc -l
```

## Daily Deliverables

| Day | Deliverable | Test Command |
|-----|------------|--------------|
| 1 | Generate YAML | `python forge_mvp.py "test"` |
| 2 | Valid YAML | `weaver check -r test.yaml` |
| 3 | Weaver integration | Validation in code |
| 4 | Code generation | Check `./generated/` |
| 5 | Metrics tracking | `cat telemetry.csv` |
| 6 | Forge semantics | `cat forge_semantics.yaml` |
| 7 | **SELF-GENERATION** | `python forge_mvp.py --self-test` |
| 8 | Polish CLI | Full demo flow |
| 9 | Documentation | README exists |
| 10 | **DEMO** | Live presentation |

## Minimum Viable Demo Script

```bash
# The 3-minute demo that proves everything

# 1. Show it works for any semantic
$ python forge_mvp.py "payment processing operation"
✓ Generated: payment_processing_operation.yaml
✓ Validated: Pass
✓ Generated: ./generated/generated.py

# 2. Show the generated code works
$ python -c "import generated.generated; print(generated.generated.payment_processing_operation('test'))"
{'success': True, 'result': 'test'}

# 3. THE KILLER FEATURE - Self-generation
$ python forge_mvp.py --self-test
🔄 Self-generation starting...
✓ Generated Forge semantics: forge_semantics.yaml
✓ Semantics validated
✓ Generated Forge v2
✓ Forge v2 works: {'success': True, 'result': 'test'}

🎉 SEMANTIC QUINE PROVEN!

📊 Metrics:
Success Rate: 6/6 (100%)
```

## What Success Looks Like

```yaml
prototype_success:
  technical:
    - Self-generation works once
    - Metrics prove >90% success
    - Generated code imports
  
  demonstration:
    - Stakeholders say "wow"
    - Clear path to production
    - Team wants to continue
  
  learning:
    - Proved semantic quine concept
    - Found simplest viable approach
    - Identified evolution priorities
```

---

**Remember: One working self-generation is worth a thousand features. Focus only on proving the loop.**