[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTE3IDE2VjdsLTYgNU0yIDlWOGwxLTFoMWw0IDMgOC04aDFsNCAyIDEgMXYxNGwtMSAxLTQgMmgtMWwtOC04LTQgM0gzbC0xLTF2LTFsMy0zIi8+PC9zdmc+)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/seanchatmangpt/wvrgen) [![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://github.com/codespaces/new/seanchatmangpt/wvrgen)

# WeaverGen v2: BPMN-Driven Semantic Code Generation

**OpenTelemetry-powered semantic code generation toolkit with BPMN workflow orchestration, AI agents, and process mining capabilities.**

## 🚀 Overview

WeaverGen v2 is a comprehensive toolkit that combines OpenTelemetry's Weaver Forge with SpiffWorkflow BPMN engine to provide visual workflow-driven semantic code generation. This represents a paradigm shift from manual coding to semantic-driven generation with built-in observability, AI agent orchestration, and process mining capabilities.

## ✨ Key Features

### 🔧 **Core Capabilities**
- **BPMN Workflow Engine**: Visual workflow orchestration using SpiffWorkflow
- **Semantic Code Generation**: Transform YAML semantic conventions into production code
- **Multi-Language Support**: Generate code for Python, JavaScript, Go, Rust, and more
- **OpenTelemetry Integration**: Built-in observability with semantic spans and metrics
- **AI Agent Orchestration**: Multi-agent communication and validation systems
- **Process Mining**: XES conversion, discovery, and analysis capabilities

### 🛠️ **Tool-Based CLI Architecture**
WeaverGen v2 organizes functionality into **7 core tools** that match user mental models:

```bash
weavergen <tool> <action> [options]
```

1. **`workflow`** - BPMN workflow operations
2. **`forge`** - Weaver Forge lifecycle commands  
3. **`semantic`** - AI-powered semantic generation
4. **`agents`** - AI agent operations
5. **`mining`** - Process mining and XES conversion
6. **`xes`** - Advanced XES operations
7. **`templates`** - Template management
8. **`validate`** - Validation commands
9. **`generate`** - Code generation commands
10. **`debug`** - Debugging and diagnostics
11. **`bpmn`** - BPMN workflow execution

### 🎯 **Advanced Features**
- **Service Task Integration**: Custom service tasks for Weaver Forge operations
- **File-Based Persistence**: Simple workflow and specification storage
- **Span-Based Validation**: Runtime validation through OpenTelemetry spans
- **Template System**: Jinja2-based code generation templates
- **Multi-Agent Communication**: AI agent consensus building and validation
- **Process Discovery**: Algorithm-driven process model discovery
- **Conformance Checking**: Process model conformance validation

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Initialize a semantic convention registry
uv run weavergen forge init my-registry --template enterprise

# Add a BPMN workflow
uv run weavergen workflow add --process SemanticGeneration --bpmn bpmn/semantic_generation.bpmn

# List available workflows
uv run weavergen workflow list

# Run a workflow with initial data
uv run weavergen workflow run SemanticGeneration --data '{"semantic_file": "conventions.yaml", "target_language": "python"}'

# Generate code from semantic conventions
uv run weavergen forge generate semantic.yaml --language python

# Convert OpenTelemetry spans to XES for process mining
uv run weavergen xes convert spans.json --output process.xes

# Discover process models from event logs
uv run weavergen xes discover process.xes --algorithm alpha --output-format bpmn

# Deploy AI agents for validation
uv run weavergen agents validate semantic.yaml --agents 5 --deep

# Debug with span visualization
uv run weavergen debug spans --format table --live
```

## 📋 CLI Commands Overview

### Workflow Management
```bash
weavergen workflow add <process> --bpmn <files>     # Add workflow specification
weavergen workflow list                             # List specifications
weavergen workflow run <spec-id> --data <json>      # Execute workflow
weavergen workflow show <spec-id> --format tree     # Show workflow structure
weavergen workflow validate <bpmn-file> --strict    # Validate BPMN
weavergen workflow delete <spec-id>                 # Delete specification
```

### Weaver Forge Operations
```bash
weavergen forge init <name> --template enterprise   # Initialize registry
weavergen forge generate <semantic.yaml> --language python
weavergen forge validate <registry> --strict        # Validate conventions
weavergen forge templates --language go             # List templates
weavergen forge pipeline <semantic.yaml> --agents 5 # Full pipeline
```

### AI-Powered Semantic Generation
```bash
weavergen semantic generate "API service with user management" --model gpt-4
weavergen semantic enhance existing.yaml --suggestions 5 --auto-apply
weavergen semantic analyze semantic.yaml --checks completeness,consistency
weavergen semantic merge file1.yaml file2.yaml --strategy smart
```

### AI Agent Operations
```bash
weavergen agents communicate semantic.yaml --agents 3 --rounds 5
weavergen agents validate semantic.yaml --agents 5 --deep
weavergen agents analyze codebase/ --focus performance --agents 3
weavergen agents orchestrate workflow.bpmn --agents 5 --async
weavergen agents forge-to-agents semantic.yaml --count 5
```

### Process Mining & XES
```bash
weavergen xes convert spans.json --output process.xes --filter-noise
weavergen xes discover process.xes --algorithm alpha --output-format bpmn
weavergen xes analyze process.xes --metrics performance,bottlenecks --visualize
weavergen xes conformance process.xes model.bpmn --method token-replay
weavergen xes visualize process.xes --viz-type process-map --interactive
weavergen xes predict model.pkl "Task_A,Task_B" --top-k 3
```

### Debugging & Diagnostics
```bash
weavergen debug spans --format table --live         # Live span monitoring
weavergen debug health --components all --deep      # System health check
weavergen debug inspect workflow --verbose          # Deep inspection
weavergen debug trace generation --detailed         # Execution tracing
weavergen debug performance --threshold 1.0         # Performance analysis
```

## 🏗️ Architecture

```
weavergen/
├── cli.py                    # Main CLI interface with tool-based structure
├── cli_workflow.py           # Workflow subcommand with span support
├── cli_debug.py              # Debug subcommand with span visualization
├── engine/
│   ├── simple_engine.py      # BPMN workflow engine
│   ├── service_task.py       # WeaverGen service operations
│   ├── forge_service_tasks.py # Forge-specific service tasks
│   └── xes_service_tasks.py  # XES-specific service tasks
├── commands/                 # Tool-based command implementations
│   ├── forge.py              # Weaver Forge lifecycle
│   ├── semantic.py           # AI-powered semantic generation
│   ├── agents.py             # AI agent operations
│   ├── xes.py                # XES and process mining
│   ├── mining.py             # Process mining operations
│   ├── templates.py          # Template management
│   ├── validate.py           # Validation commands
│   ├── generate.py           # Code generation
│   ├── debug.py              # Debugging and diagnostics
│   └── bpmn.py               # BPMN workflow execution
├── bpmn/                     # BPMN workflow definitions
│   ├── semantic_generation.bpmn
│   └── simple_workflow.bpmn
├── templates/                # Jinja2 code generation templates
├── semantic_conventions/     # Semantic convention definitions
└── enhanced_instrumentation.py # OpenTelemetry integration
```

## 🔄 Service Tasks

The following service tasks are available for BPMN workflows:

- `validate_semantic_convention`: Validate YAML semantic conventions
- `generate_semantic_code`: Generate code from semantic conventions
- `execute_weaver_forge`: Run Weaver Forge transformations
- `convert_spans_to_xes`: Convert OpenTelemetry spans to XES format
- `discover_process_model`: Discover process models from event logs
- `analyze_process_performance`: Analyze process performance metrics

## 🎯 Paradigm Shift: Why Traditional "Best Practices" Are Anti-Patterns Here

WeaverGen represents a fundamental shift from manual coding to semantic-driven generation. This changes everything about how we think about software development.

### Anti-Patterns in the WeaverGen Paradigm

#### 1. **Manual Code Reviews** → Anti-Pattern
- **Traditional**: Peer review of code changes for quality
- **WeaverGen**: Code is generated, not written. Review happens at semantic convention level only.

#### 2. **Unit Testing Generated Code** → Anti-Pattern
- **Traditional**: 100% test coverage is gold standard
- **WeaverGen**: Testing generated code means you don't trust your generator. Test the generator once, validate with spans.

#### 3. **Dependency Injection / IoC Containers** → Anti-Pattern
- **Traditional**: Loose coupling through DI
- **WeaverGen**: Single binary with everything included. Dependencies resolved at generation time.

#### 4. **Microservices Architecture** → Anti-Pattern
- **Traditional**: Small, independent services
- **WeaverGen**: Generate monolithic binaries from semantic conventions. Distribution at binary level.

#### 5. **Package Management (pip, npm, maven)** → Anti-Pattern
- **Traditional**: Careful dependency version management
- **WeaverGen**: 125MB binary includes everything. Package managers are complexity vectors.

#### 6. **Environment-Specific Configuration** → Anti-Pattern
- **Traditional**: .env files, config maps, environment variables
- **WeaverGen**: Configuration generated into binary. Environment differences are semantic variations.

#### 7. **API Versioning Strategies** → Anti-Pattern
- **Traditional**: v1, v2 endpoints, deprecation cycles
- **WeaverGen**: Semantic conventions version everything. Generate new binary for new version.

#### 8. **Manual Documentation** → Anti-Pattern
- **Traditional**: Keep docs in sync with code
- **WeaverGen**: Documentation generated from semantic conventions. Manual docs are lies waiting to happen.

#### 9. **Feature Flags / Progressive Rollout** → Anti-Pattern
- **Traditional**: Gradual feature enablement
- **WeaverGen**: Generate different binaries for different features. Feature flags are runtime complexity.

#### 10. **Database Migrations** → Anti-Pattern
- **Traditional**: Careful schema evolution scripts
- **WeaverGen**: Generate new binary with new schema. Data migration is a separate semantic operation.

#### 11. **CI/CD Pipelines** → Anti-Pattern
- **Traditional**: Complex build/test/deploy pipelines
- **WeaverGen**: One command generates deployable binary. CI/CD is just running the generator.

#### 12. **Error Handling Code** → Anti-Pattern
- **Traditional**: Comprehensive try/catch blocks
- **WeaverGen**: Happy path only in semantic conventions. Error handling generated from patterns.

#### 13. **Abstract Base Classes / Interfaces** → Anti-Pattern
- **Traditional**: Design patterns for extensibility
- **WeaverGen**: Generate concrete implementations. Abstraction at semantic level only.

#### 14. **ORMs and Database Abstraction** → Anti-Pattern
- **Traditional**: Database-agnostic code
- **WeaverGen**: Generate database-specific code. Switching databases means regenerating.

#### 15. **Logging Statements in Code** → Anti-Pattern
- **Traditional**: Strategic log placement
- **WeaverGen**: OpenTelemetry spans generated automatically. Manual logging is redundant.

#### 16. **Configuration as Code (Terraform, etc.)** → Anti-Pattern
- **Traditional**: Infrastructure defined in code
- **WeaverGen**: Infrastructure generated from semantic conventions. IaC is another manual step.

#### 17. **Design Patterns (Factory, Strategy, etc.)** → Anti-Pattern
- **Traditional**: Reusable solutions to common problems
- **WeaverGen**: Patterns encoded in generator. Patterns in generated code = generator failure.

#### 18. **Code Comments** → Anti-Pattern
- **Traditional**: Explain complex logic
- **WeaverGen**: Generated code needs no explanation. Comments belong in semantic conventions.

#### 19. **Pull Request Workflow** → Anti-Pattern
- **Traditional**: Review, discuss, merge
- **WeaverGen**: Semantic changes trigger regeneration. No merge conflicts in generated code.

#### 20. **Modular Architecture** → Anti-Pattern
- **Traditional**: Separation of concerns through modules
- **WeaverGen**: Single binary with everything. Modularity is a semantic concern.

#### 21. **API Mocking for Tests** → Anti-Pattern
- **Traditional**: Mock external dependencies
- **WeaverGen**: Generate test scenarios from semantic conventions. Mocking implies uncertainty.

#### 22. **Developer Environments** → Anti-Pattern
- **Traditional**: Local dev, staging, production
- **WeaverGen**: Single binary runs anywhere. Environment differences are semantic variations.

### The Meta Anti-Pattern

**"Best Practices" Themselves** → The ultimate anti-pattern is following "best practices" instead of generating from semantic conventions. Best practices assume human-written code, which is the root anti-pattern.

### The Only Practice That Matters

In the WeaverGen paradigm:
1. **Define semantically** - Everything starts with semantic conventions
2. **Generate completely** - No manual code, ever
3. **Deploy atomically** - Single binary deployment
4. **Validate through spans** - Runtime reality via OpenTelemetry

Everything else is unnecessary complexity from the manual coding era.

## 📦 Installation

To install this package, run:

```sh
pip install weavergen
```

## 🎮 Usage

To view the CLI help information, run:

```sh
weavergen --help
```

For specific tool help:

```sh
weavergen workflow --help
weavergen forge --help
weavergen xes --help
weavergen agents --help
```

## 🔧 Development

<details>
<summary>Prerequisites</summary>

1. [Generate an SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) and [add the SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
1. Configure SSH to automatically load your SSH keys:

    ```sh
    cat << EOF >> ~/.ssh/config
    
    Host *
      AddKeysToAgent yes
      IgnoreUnknown UseKeychain
      UseKeychain yes
      ForwardAgent yes
    EOF
    ```

1. [Install Docker Desktop](https://www.docker.com/get-started).
1. [Install VS Code](https://code.visualstudio.com/) and [VS Code's Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). Alternatively, install [PyCharm](https://www.jetbrains.com/pycharm/download/).
1. _Optional:_ install a [Nerd Font](https://www.nerdfonts.com/font-downloads) such as [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode) and [configure VS Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) or [PyCharm](https://github.com/tonsky/FiraCode/wiki/Intellij-products-instructions) to use it.

</details>

<details open>
<summary>Development environments</summary>

The following development environments are supported:

1. ⭐️ _GitHub Codespaces_: click on [Open in GitHub Codespaces](https://github.com/codespaces/new/seanchatmangpt/wvrgen) to start developing in your browser.
1. ⭐️ _VS Code Dev Container (with container volume)_: click on [Open in Dev Containers](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/seanchatmangpt/wvrgen) to clone this repository in a container volume and create a Dev Container with VS Code.
1. ⭐️ _uv_: clone this repository and run the following from root of the repository:

    ```sh
    # Create and install a virtual environment
    uv sync --python 3.12 --all-extras

    # Activate the virtual environment
    source .venv/bin/activate

    # Install the pre-commit hooks
    pre-commit install --install-hooks
    ```

1. _VS Code Dev Container_: clone this repository, open it with VS Code, and run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Dev Containers: Reopen in Container_.
1. _PyCharm Dev Container_: clone this repository, open it with PyCharm, [create a Dev Container with Mount Sources](https://www.jetbrains.com/help/pycharm/start-dev-container-inside-ide.html), and [configure an existing Python interpreter](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#widget) at `/opt/venv/bin/python`.

</details>

<details open>
<summary>Developing</summary>

- This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
- Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project.
- Run `uv add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `uv.lock`. Add `--dev` to install a development dependency.
- Run `uv sync --upgrade` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`. Add `--only-dev` to upgrade the development dependencies only.
- Run `cz bump` to bump the app's version, update the `CHANGELOG.md`, and create a git tag. Then push the changes and the git tag with `git push origin main --tags`.

</details>

## 📊 Current Status

### ✅ **Implemented Features**
- **BPMN Workflow Engine**: Full SpiffWorkflow integration with custom service tasks
- **Tool-Based CLI**: 11 core tools with comprehensive command structure
- **OpenTelemetry Integration**: Span-based instrumentation and debugging
- **Semantic Generation**: AI-powered semantic convention generation
- **Process Mining**: XES conversion, discovery, and analysis
- **AI Agent Framework**: Multi-agent communication and validation
- **Template System**: Jinja2-based code generation templates
- **Validation Framework**: Multi-level validation capabilities
- **Debug & Diagnostics**: Comprehensive debugging tools

### 🚧 **In Development**
- **Weaver Binary Integration**: Direct Weaver Forge binary execution
- **Advanced Process Discovery**: Machine learning-based process discovery
- **Real-time Agent Communication**: Live multi-agent consensus building
- **Enhanced Visualization**: Interactive process and span visualizations

### 📈 **Roadmap**
- **Enterprise Templates**: Pre-built semantic convention templates
- **Cloud Integration**: AWS, GCP, Azure semantic conventions
- **Performance Optimization**: Advanced caching and optimization
- **Community Templates**: Template sharing and marketplace

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
