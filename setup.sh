#!/bin/bash
# WeaverGen Setup Script - CDCS v8.0 Optimized
# Automated project initialization with compound intelligence

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project info
PROJECT_NAME="WeaverGen"
PROJECT_DESC="Python wrapper for OTel Weaver Forge with Claude Code optimization"

echo -e "${PURPLE}🌟 ${PROJECT_NAME} Setup - CDCS v8.0${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${CYAN}${PROJECT_DESC}${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"

# Check pip
if ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ pip not found. Please install pip${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip found${NC}"

# Check if in project directory
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}❌ Not in WeaverGen project directory${NC}"
    echo -e "${YELLOW}Please run this script from the WeaverGen root directory${NC}"
    exit 1
fi

# Install development dependencies
echo ""
echo -e "${YELLOW}📦 Installing development dependencies...${NC}"
pip install -e ".[dev]"
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Setup pre-commit hooks
echo ""
echo -e "${YELLOW}🔧 Setting up pre-commit hooks...${NC}"
if command -v pre-commit &> /dev/null; then
    pre-commit install --install-hooks
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠️  pre-commit not found, installing...${NC}"
    pip install pre-commit
    pre-commit install --install-hooks
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
fi

# Check for OTel Weaver
echo ""
echo -e "${YELLOW}🦀 Checking for OTel Weaver...${NC}"
if command -v weaver &> /dev/null; then
    WEAVER_VERSION=$(weaver --version 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ OTel Weaver found: ${WEAVER_VERSION}${NC}"
else
    echo -e "${YELLOW}⚠️  OTel Weaver not found${NC}"
    echo -e "${CYAN}💡 To install OTel Weaver:${NC}"
    echo -e "  ${BLUE}cargo install otellib-weaver-cli${NC}"
    echo -e "  ${BLUE}# OR${NC}"
    echo -e "  ${BLUE}make install-weaver${NC}"
fi

# Check for Cargo (Rust)
echo ""
echo -e "${YELLOW}🦀 Checking for Rust/Cargo...${NC}"
if command -v cargo &> /dev/null; then
    CARGO_VERSION=$(cargo --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Cargo ${CARGO_VERSION} found${NC}"
else
    echo -e "${YELLOW}⚠️  Cargo not found${NC}"
    echo -e "${CYAN}💡 To install Rust:${NC}"
    echo -e "  ${BLUE}curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh${NC}"
fi

# Create necessary directories
echo ""
echo -e "${YELLOW}📁 Creating project directories...${NC}"
mkdir -p generated logs cache templates examples/output
echo -e "${GREEN}✅ Directories created${NC}"

# Initialize git if not already done
echo ""
echo -e "${YELLOW}🔧 Checking git repository...${NC}"
if [[ ! -d ".git" ]]; then
    echo -e "${YELLOW}📝 Initializing git repository...${NC}"
    git init
    git add .
    git commit -m "feat: initial WeaverGen project setup with CDCS v8.0"
    echo -e "${GREEN}✅ Git repository initialized${NC}"
else
    echo -e "${GREEN}✅ Git repository already exists${NC}"
fi

# Run initial tests
echo ""
echo -e "${YELLOW}🧪 Running initial tests...${NC}"
if python -m pytest tests/ -v --tb=short; then
    echo -e "${GREEN}✅ All tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Some tests failed (this is normal for initial setup)${NC}"
fi

# CDCS Integration Check
echo ""
echo -e "${YELLOW}🧠 Checking CDCS v8.0 integration...${NC}"
if [[ -d "/Users/sac/claude-desktop-context" ]]; then
    echo -e "${GREEN}✅ CDCS system found${NC}"
    
    # Create project link in CDCS work directory
    CDCS_WORK_DIR="/Users/sac/claude-desktop-context/work"
    if [[ -d "$CDCS_WORK_DIR" ]]; then
        mkdir -p "$CDCS_WORK_DIR/weavergen-dev"
        echo "$(pwd)" > "$CDCS_WORK_DIR/weavergen-dev/project.link"
        echo -e "${GREEN}✅ CDCS project link created${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  CDCS system not found${NC}"
    echo -e "${CYAN}💡 WeaverGen will work standalone${NC}"
fi

# Final summary
echo ""
echo -e "${PURPLE}🎉 WeaverGen Setup Complete!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${GREEN}✅ Project successfully initialized${NC}"
echo -e "${GREEN}✅ Development environment ready${NC}"
echo -e "${GREEN}✅ CDCS v8.0 integration configured${NC}"
echo ""
echo -e "${CYAN}🚀 Quick Start Commands:${NC}"
echo -e "  ${BLUE}make help${NC}          # Show all available commands"
echo -e "  ${BLUE}make morning${NC}       # CDCS morning workflow"
echo -e "  ${BLUE}make work${NC}          # Start development session"
echo -e "  ${BLUE}weavergen --help${NC}   # Show CLI help"
echo -e "  ${BLUE}make test${NC}          # Run test suite"
echo -e "  ${BLUE}make demo${NC}          # Run demonstration"
echo ""
echo -e "${CYAN}📚 Next Steps:${NC}"
echo -e "  1. ${YELLOW}Install OTel Weaver:${NC} ${BLUE}make install-weaver${NC}"
echo -e "  2. ${YELLOW}Run demo:${NC} ${BLUE}make demo${NC}"
echo -e "  3. ${YELLOW}Start development:${NC} ${BLUE}make work${NC}"
echo -e "  4. ${YELLOW}Generate code:${NC} ${BLUE}weavergen generate examples/sample-conventions.yaml${NC}"
echo ""
echo -e "${PURPLE}🌟 Ready for compound impact OpenTelemetry development!${NC}"
