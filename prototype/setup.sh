#!/bin/bash
# Weaver Forge Prototype Setup Script
# This script sets up the prototype environment and runs initial tests

set -e  # Exit on any error

echo "🔨 Weaver Forge Prototype Setup"
echo "==============================="
echo ""

# Check if we're in the right directory
if [ ! -f "forge_mvp.py" ]; then
    echo "❌ Error: Please run this script from the prototype directory"
    echo "   cd /path/to/weavergen/prototype"
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Error: Python 3 is required but not found"
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists, removing..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate and install dependencies
echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Make test script executable
echo ""
echo "🔧 Setting up test scripts..."
chmod +x test_prototype.sh
echo "✅ Test scripts ready"

# Run initial test
echo ""
echo "🧪 Running initial test..."
python forge_mvp.py "test operation" --skip-validation

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate the environment: source venv/bin/activate"
echo "   2. Run the full test suite: ./test_prototype.sh"
echo "   3. Try self-generation: python forge_mvp.py --self-test"
echo "   4. Generate your own: python forge_mvp.py 'your operation description'"
echo ""
echo "📚 Documentation: README.md"
echo "🎯 The prototype proves the semantic quine concept!" 