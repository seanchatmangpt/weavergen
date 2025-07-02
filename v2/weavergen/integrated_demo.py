#!/usr/bin/env python
"""Integrated demo showing workflow subcommand functionality."""

from src.weavergen.cli_workflow import get_engine
import json

def main():
    print("🚀 WeaverGen v2 Workflow Subcommand - Integrated Demo")
    print("=" * 60)
    
    # Get the engine instance
    engine = get_engine()
    
    # 1. Add workflows
    print("\n1️⃣  Adding workflows...")
    try:
        engine.add_spec("SimpleWorkflow", ["bpmn/simple_workflow.bpmn"])
        print("   ✓ Added SimpleWorkflow")
        
        engine.add_spec("SemanticGeneration", ["bpmn/semantic_generation.bpmn"])
        print("   ✓ Added SemanticGeneration")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 2. List specifications
    print("\n2️⃣  Available specifications:")
    for spec_id, name, _ in engine.list_specs():
        print(f"   • {spec_id} ({name})")
    
    # 3. Show workflow details
    print("\n3️⃣  SimpleWorkflow structure:")
    spec = engine.specs.get("SimpleWorkflow")
    if spec:
        for task_name, task_spec in spec.task_specs.items():
            print(f"   • {task_name}: {task_spec.__class__.__name__}")
    
    # 4. Run workflows
    print("\n4️⃣  Running SimpleWorkflow...")
    instance1 = engine.start_workflow("SimpleWorkflow")
    instance1.run_until_user_input_required()
    print(f"   Status: {'Completed' if instance1.workflow.is_completed() else 'Active'}")
    
    print("\n5️⃣  Running SemanticGeneration with data...")
    instance2 = engine.start_workflow("SemanticGeneration")
    instance2.workflow.data.update({
        "semantic_file": "conventions.yaml",
        "target_language": "python"
    })
    
    try:
        instance2.run_until_user_input_required()
        print(f"   Status: {'Completed' if instance2.workflow.is_completed() else 'Active'}")
    except Exception as e:
        print(f"   Note: {e}")
    
    # 5. Show instances
    print("\n6️⃣  Workflow instances:")
    for wf_id, name, _, active, _, _ in engine.list_workflows(include_completed=True):
        status = "Active" if active else "Completed"
        print(f"   • {wf_id}: {name} ({status})")
    
    # 6. Export example
    print("\n7️⃣  Export example (SemanticGeneration):")
    export_data = {
        "id": "SemanticGeneration",
        "name": "SemanticGeneration",
        "tasks": {
            name: task.__class__.__name__ 
            for name, task in engine.specs["SemanticGeneration"].task_specs.items()
        }
    }
    print(json.dumps(export_data, indent=2)[:200] + "...")
    
    print("\n✨ Integrated demo complete!")
    print("\n💡 Try these commands:")
    print("   uv run weavergen workflow --help")
    print("   uv run weavergen workflow list")
    print("   uv run weavergen workflow show SimpleWorkflow")
    print("   uv run weavergen workflow validate bpmn/simple_workflow.bpmn")

if __name__ == "__main__":
    main()