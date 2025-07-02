"""Test BPMN forge via CLI with span capture."""

import subprocess
import json
import time
from pathlib import Path
import shutil

# Clean up
test_dir = Path("test_bpmn_cli")
if test_dir.exists():
    shutil.rmtree(test_dir)

print("=" * 80)
print("TESTING BPMN FORGE INIT VIA CLI")
print("=" * 80)

# Run the command
result = subprocess.run(
    ["uv", "run", "weavergen", "forge", "init", "BPMNTest", "--output-dir", "test_bpmn_cli"],
    capture_output=True,
    text=True
)

print(f"\nExit code: {result.returncode}")
print("\nSTDOUT:")
print("-" * 40)
print(result.stdout)
print("-" * 40)

if result.stderr:
    print("\nSTDERR:")
    print("-" * 40)
    print(result.stderr)
    print("-" * 40)

# Check if BPMN was mentioned
if "BPMN" in result.stdout or "workflow" in result.stdout.lower():
    print("\n✓ BPMN workflow execution detected")
else:
    print("\n✗ No BPMN workflow execution detected")

# Check for crash vs success
if result.returncode == 0:
    print("✓ Command succeeded")
    
    # Check created files
    if test_dir.exists():
        print("\nCreated files:")
        for file in test_dir.rglob("*.yaml"):
            print(f"  ✓ {file}")
            
        # Validate with weaver
        print("\nValidating created registry...")
        validate_result = subprocess.run(
            ["weaver", "registry", "check", "-r", str(test_dir)],
            capture_output=True,
            text=True
        )
        
        if validate_result.returncode == 0:
            print("✓ Registry validation passed!")
        else:
            print("✗ Registry validation failed")
            
else:
    print(f"✗ Command failed with exit code {result.returncode}")
    
    # Check if it's the expected BPMN crash
    if "FATAL" in result.stdout and "BPMN" in result.stdout:
        print("✓ Failed as expected: BPMN-first enforcement")
    else:
        print("✗ Unexpected failure")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)