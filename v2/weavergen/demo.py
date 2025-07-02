#!/usr/bin/env python
"""Demo script for WeaverGen v2 BPMN functionality."""

import json
from pathlib import Path

from src.weavergen.engine.simple_engine import SimpleBpmnEngine
from src.weavergen.engine.service_task import WeaverGenServiceEnvironment

def main():
    # Initialize engine
    script_env = WeaverGenServiceEnvironment()
    engine = SimpleBpmnEngine(script_env)
    
    print("=== WeaverGen v2 BPMN Demo ===\n")
    
    # Add workflows
    print("1. Adding workflows...")
    simple_id = engine.add_spec("SimpleWorkflow", ["bpmn/simple_workflow.bpmn"])
    print(f"   ✓ Added SimpleWorkflow: {simple_id}")
    
    semantic_id = engine.add_spec("SemanticGeneration", ["bpmn/semantic_generation.bpmn"])
    print(f"   ✓ Added SemanticGeneration: {semantic_id}")
    
    # List specifications
    print("\n2. Available specifications:")
    for spec_id, name, filename in engine.list_specs():
        print(f"   - {spec_id}: {name}")
    
    # Run simple workflow
    print("\n3. Running SimpleWorkflow...")
    instance = engine.start_workflow("SimpleWorkflow")
    instance.run_until_user_input_required()
    
    if instance.workflow.is_completed():
        print("   ✓ Workflow completed successfully")
    else:
        print("   ⚠ Workflow requires user input")
    
    print(f"   Data: {json.dumps(instance.data, indent=2)}")
    
    # Run semantic generation workflow with data
    print("\n4. Running SemanticGeneration workflow...")
    instance2 = engine.start_workflow("SemanticGeneration")
    instance2.workflow.data.update({
        "semantic_file": "conventions.yaml",
        "target_language": "python"
    })
    
    try:
        instance2.run_until_user_input_required()
        print("   ✓ Workflow executed")
    except Exception as e:
        print(f"   ⚠ Workflow error: {e}")
    
    print(f"   Data: {json.dumps(instance2.data, indent=2)}")
    
    # List workflow instances
    print("\n5. Workflow instances:")
    for wf_id, name, filename, active, started, updated in engine.list_workflows():
        status = "Active" if active else "Completed"
        print(f"   - {wf_id}: {name} ({status})")
    
    print("\n✨ Demo complete!")

if __name__ == "__main__":
    main()