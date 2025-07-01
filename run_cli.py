#!/usr/bin/env python3
"""
Run weavergen CLI with uv for fast dependency resolution.

Usage:
    uv run run_cli.py --help
    uv run run_cli.py debug spans
    uv run run_cli.py debug health --deep
    uv run run_cli.py agents communicate --agents 2
"""

import sys
from pathlib import Path

# Add src to path so we can import weavergen
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weavergen.cli import app

if __name__ == "__main__":
    app()