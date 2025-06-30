#!/bin/bash
# Test script for Forge Prototype

echo "🧪 Forge Prototype Test Suite"
echo "============================="
echo ""

# Change to prototype directory
cd "$(dirname "$0")"

# Test 1: Basic generation
echo "Test 1: Generate simple semantic convention"
echo "-------------------------------------------"
python3 forge_mvp.py "hello world operation" --skip-validation
echo ""

# Test 2: Check generated files
echo "Test 2: Check generated files"
echo "-----------------------------"
ls -la *.yaml
ls -la generated/
echo ""

# Test 3: Show metrics
echo "Test 3: Show metrics"
echo "-------------------"
python3 forge_mvp.py --metrics
echo ""

# Test 4: Self-generation (THE BIG ONE)
echo "Test 4: Self-generation (Semantic Quine)"
echo "---------------------------------------"
python3 forge_mvp.py --self-test

echo ""
echo "🏁 Test suite complete!"
