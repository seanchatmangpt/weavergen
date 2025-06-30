#!/usr/bin/env python3
"""Quickstart script for WeaverGen Ollama examples.

Run this to get started immediately:
    python quickstart.py
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return success status."""
    print(f"→ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"✗ Failed: {result.stderr}")
        return False
    return True


def main():
    """Quick setup and demo."""
    print("🚀 WeaverGen Ollama Examples - Quick Start")
    print("=" * 50)
    
    # 1. Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return 1
    
    # 2. Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-e", ".[examples]", "--quiet"]):
        print("❌ Failed to install dependencies")
        return 1
    
    # 3. Check Ollama
    print("\n🔍 Checking Ollama...")
    os.environ["PYTHONPATH"] = str(Path(__file__).parent / "src")
    
    result = subprocess.run(
        [sys.executable, "-m", "weavergen.examples.check_setup"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(result.stdout)
        print("\n❌ Please fix the issues above and try again")
        return 1
    
    # 4. Run a simple example
    print("\n✨ Running SQL generation example...")
    print("-" * 50)
    
    # Create inline example
    example_code = '''
import asyncio
from weavergen.examples.ollama_utils import get_ollama_model
from weavergen.examples.sql_gen_ollama_simple import SqlQuery
from pydantic_ai import Agent

async def demo():
    model = get_ollama_model()
    agent = Agent(
        model=model,
        result_type=SqlQuery,
        system_prompt="Generate PostgreSQL queries with explanations."
    )
    
    result = await agent.run("Show me the top 10 users by activity")
    output = result.output
    
    print(f"\\n📝 Generated SQL:\\n{output.query}")
    print(f"\\n💡 Explanation:\\n{output.explanation}")

asyncio.run(demo())
'''
    
    result = subprocess.run(
        [sys.executable, "-c", example_code],
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parent / "src")}
    )
    
    if result.returncode == 0:
        print("\n✅ Success! Everything is working.")
        print("\n📚 Next steps:")
        print("1. Try the examples:")
        print("   python -m weavergen.examples.structured_output_ollama")
        print("   python -m weavergen.examples.sql_gen_ollama_simple")
        print("\n2. Read the docs:")
        print("   src/weavergen/examples/README.md")
        print("\n3. Run tests:")
        print("   pytest tests/test_ollama_integration.py -v")
    else:
        print("\n❌ Example failed. Check your Ollama setup.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())