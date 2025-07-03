#!/bin/bash
set -e

# This script builds the weavergen executable using PyInstaller.

# Clean up previous builds
rm -rf dist build

# Create the executable
pyinstaller --name weavergen --onefile --console src/weavergen/cli.py

# Create checksum and signature
shasum -a 256 dist/weavergen > dist/weavergen.sha256
# gpg --detach-sign --armor dist/weavergen # Uncomment to enable GPG signing
