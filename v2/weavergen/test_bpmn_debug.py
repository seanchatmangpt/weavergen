"""Debug BPMN loading."""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from weavergen.engine.simple_engine import SimpleBpmnEngine
from weavergen.engine.service_task import WeaverGenServiceEnvironment
from weavergen.engine.forge_service_tasks import register_forge_tasks

# Initialize environment
environment = WeaverGenServiceEnvironment()
register_forge_tasks(environment)

# Initialize engine
engine = SimpleBpmnEngine(environment)

# Try to load BPMN
workflow_dir = Path("src/workflows/bpmn/forge")
print(f"Looking for BPMN files in: {workflow_dir}")
print(f"Directory exists: {workflow_dir.exists()}")

if workflow_dir.exists():
    for bpmn_file in workflow_dir.glob("*.bpmn"):
        print(f"\nFound BPMN file: {bpmn_file}")
        try:
            # Load the file
            engine.parser.add_bpmn_file(str(bpmn_file))
            print(f"  ✓ File loaded successfully")
            
            # Get process IDs
            process_ids = engine.parser.get_process_ids()
            print(f"  Process IDs found: {process_ids}")
            
            # Register each process
            for process_id in process_ids:
                spec = engine.parser.get_spec(process_id)
                engine.specs[process_id] = spec
                print(f"  ✓ Registered process: {process_id}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")

print(f"\nRegistered specs: {list(engine.specs.keys())}")

# Try to start workflow
if 'ForgeInitProcess' in engine.specs:
    print("\n✓ ForgeInitProcess is registered and ready!")
else:
    print("\n✗ ForgeInitProcess not found in registered specs")