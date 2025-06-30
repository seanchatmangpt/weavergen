#!/usr/bin/env python3
"""Simple launcher for WeaverGen Ollama examples (no installation required)."""

import subprocess
import sys
import os
from pathlib import Path


def main():
    """Launch examples without installation."""
    print("🚀 WeaverGen Ollama Examples")
    print("=" * 40)
    
    # Set up path
    src_path = Path(__file__).parent / "src"
    os.environ["PYTHONPATH"] = str(src_path)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return 1
    
    print("\n✨ Running interactive menu...")
    
    # Run the examples module
    result = subprocess.run([
        sys.executable, "-m", "weavergen.examples"
    ], env=os.environ)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())