# Weaver Forge Makefile
.PHONY: help install bootstrap clean test generate example all

# Default target
help:
	@echo "Weaver Forge - Self-Referential Code Generator"
	@echo ""
	@echo "Available targets:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make bootstrap  - Bootstrap Forge from its semantic conventions"
	@echo "  make test       - Run tests"
	@echo "  make example    - Run example usage"
	@echo "  make clean      - Clean generated files"
	@echo "  make all        - Install, bootstrap, and run examples"
	@echo ""
	@echo "Quick start:"
	@echo "  make all"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Bootstrap Weaver Forge
bootstrap: weaver_forge.yaml
	@echo "🚀 Bootstrapping Weaver Forge..."
	python bootstrap_forge.py
	@echo "✅ Bootstrap complete"

# Generate the initial semantic convention if it doesn't exist
weaver_forge.yaml:
	@echo "🤖 Generating Weaver Forge semantic conventions..."
	python generate_semantic.py \
		"semantic convention generation from natural language with LLM integration and validation" \
		-o weaver_forge.yaml
	@echo "✅ Semantic convention generated"

# Run tests
test:
	@echo "🧪 Running tests..."
	@if [ -d "generated/forge" ]; then \
		python -m pytest tests/ -v; \
	else \
		echo "❌ Please run 'make bootstrap' first"; \
		exit 1; \
	fi

# Run examples
example:
	@echo "📚 Running examples..."
	@if [ -d "generated/forge" ]; then \
		python example_usage.py; \
	else \
		echo "❌ Please run 'make bootstrap' first"; \
		exit 1; \
	fi

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf generated/
	rm -rf examples/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	@echo "✅ Clean complete"

# Full setup and demo
all: install bootstrap example
	@echo ""
	@echo "🎉 Weaver Forge is ready!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit operations in generated/forge/operations/forge.py"
	@echo "2. Use the generated Forge to create new semantic conventions"
	@echo "3. Let Forge improve itself with forge_self_improve()"
	@echo ""
	@echo "Example:"
	@echo "  from generated.forge import forge_semantic_generate"
	@echo "  forge_semantic_generate('your description', 'output.yaml', 'llama3.2')"

# Development targets
.PHONY: format lint type-check

format:
	@echo "🎨 Formatting code..."
	black *.py generated/ templates/

lint:
	@echo "🔍 Linting code..."
	pylint *.py

type-check:
	@echo "📝 Type checking..."
	mypy *.py --ignore-missing-imports