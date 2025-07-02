"""Test the init command directly."""

import sys
sys.path.insert(0, 'src')

from commands.forge import init
from pathlib import Path
from typer.testing import CliRunner
from commands.forge import forge_app

runner = CliRunner()

# Test the init command
result = runner.invoke(forge_app, ["init", "MyApp", "--output-dir", "test_registry"])

print("Exit code:", result.exit_code)
print("Output:", result.output)

# Check created files
if result.exit_code == 0:
    registry_dir = Path("test_registry")
    print("\nCreated files:")
    for file in registry_dir.rglob("*"):
        if file.is_file():
            print(f"  {file}")