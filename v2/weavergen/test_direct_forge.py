"""Test forge init directly."""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from typer.testing import CliRunner
from commands.forge import forge_app

runner = CliRunner()

# Clean up
test_dir = Path("test_bpmn_direct")
if test_dir.exists():
    import shutil
    shutil.rmtree(test_dir)

# Test the init command
print("Testing BPMN-first forge init...")
result = runner.invoke(forge_app, ["init", "TestApp", "--output-dir", "test_bpmn_direct"])

print(f"\nExit code: {result.exit_code}")
print(f"Output:\n{result.output}")

# Check if BPMN workflow was executed
if "BPMN workflow" in result.output:
    print("\n✓ BPMN workflow execution detected!")
else:
    print("\n✗ No BPMN workflow execution detected")

# Check created files
if result.exit_code == 0 and test_dir.exists():
    print("\nCreated files:")
    for file in test_dir.rglob("*"):
        if file.is_file():
            print(f"  ✓ {file}")