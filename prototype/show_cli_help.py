#!/usr/bin/env python3
"""Script to display WeaverGen CLI help."""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.weavergen.cli import app

# Show main help
print("=== WeaverGen CLI Help ===\n")
app(["--help"], standalone_mode=False)

print("\n=== Command: generate ===")
app(["generate", "--help"], standalone_mode=False)

print("\n=== Command: validate ===")
app(["validate", "--help"], standalone_mode=False)

print("\n=== Command: templates ===")
app(["templates", "--help"], standalone_mode=False)

print("\n=== Command: config ===")
app(["config", "--help"], standalone_mode=False)