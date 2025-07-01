# Weaver Command Reference for WeaverGen v2

**Version:** Weaver 0.15.3  
**Purpose:** Complete command reference to inform WeaverGen v2 design  
**Date:** 2025-01-01

---

## Overview

This document contains the complete help text for every Weaver command to guide the design of WeaverGen v2. The unified BPMN architecture should provide intuitive access to all these capabilities while preserving the full power of the underlying Weaver toolchain.

---

## Main Command Structure

```
weaver [OPTIONS] <COMMAND>
```

### Global Options
- `--debug...` - Turn debugging information on (can be repeated for more verbosity)
- `--quiet` - Turn the quiet mode on (minimal output)
- `--future` - Enable most recent validation rules for semconv registry (recommended for new registries)
- `-h, --help` - Print help
- `-V, --version` - Print version

### Top-Level Commands
1. **registry** - Manage Semantic Convention Registry
2. **diagnostic** - Manage Diagnostic Messages  
3. **completion** - Generate shell completions
4. **help** - Print help messages

---

## 1. Registry Commands

The `registry` subcommand is the primary interface for semantic convention operations.

### 1.1 Registry Check

**Command:** `weaver registry check [OPTIONS]`

**Purpose:** Validates a semantic convention registry through multiple validation steps:
- Loading semantic convention specifications from local directory or git repository
- Parsing the loaded specifications
- Resolving references and extends clauses
- Checking compliance with Rego policies

**Key Options:**
```
-r, --registry <REGISTRY>
    Local folder, Git repo URL, or Git archive URL of the semantic convention registry
    Default: https://github.com/open-telemetry/semantic-conventions.git[model]

-s, --follow-symlinks
    Follow symlinks when loading the registry (default: false)

--include-unreferenced
    Include signals/attributes from dependency registries even if not explicitly referenced

--baseline-registry <BASELINE_REGISTRY>
    Baseline semantic convention registry for comparison

-p, --policy <POLICIES>
    Policy files or directories to check against (.rego files)

--skip-policies
    Skip the policy checks

--display-policy-coverage
    Display policy coverage report for debugging

--diagnostic-format <DIAGNOSTIC_FORMAT>
    Format for diagnostic messages: ansi, json, gh_workflow_command (default: ansi)

--diagnostic-template <DIAGNOSTIC_TEMPLATE>
    Path to diagnostic templates directory (default: diagnostic_templates)

--diagnostic-stdout
    Send output to stdout instead of stderr
```

**Exit Code:** 0 if validation successful

---

### 1.2 Registry Generate

**Command:** `weaver registry generate [OPTIONS] <TARGET> [OUTPUT]`

**Purpose:** Generates artifacts from a semantic convention registry. Validates Rego policies before artifact generation.

**Arguments:**
- `<TARGET>` - Target to generate artifacts for
- `[OUTPUT]` - Output directory (default: "output")

**Key Options:**
```
-t, --templates <TEMPLATES>
    Path to templates directory (default: templates)

-c, --config <CONFIG>
    List of weaver.yaml configuration files (last one overrides conflicts)

-D, --param <PARAM>
    Parameters key=value from command line (YAML values)

--params <PARAMS>
    Parameters from YAML file

-r, --registry <REGISTRY>
    Registry source (same as check command)

-s, --follow-symlinks
    Follow symlinks when loading registry

--include-unreferenced
    Include unreferenced dependency registry items

-p, --policy <POLICIES>
    Policy files for validation

--skip-policies
    Skip policy checks

--display-policy-coverage
    Show policy coverage report

--diagnostic-format <DIAGNOSTIC_FORMAT>
    Diagnostic message format (default: ansi)
```

**Exit Code:** 0 if generation successful

---

### 1.3 Registry Resolve

**Command:** `weaver registry resolve [OPTIONS]`

**Purpose:** Resolves a semantic convention registry. Validates Rego policies before resolution.

**Key Options:**
```
-r, --registry <REGISTRY>
    Registry source

--lineage
    Include lineage information in resolved schema (not yet implemented)

-o, --output <OUTPUT>
    Output file for resolved schema (stdout if not specified)

-f, --format <FORMAT>
    Output format: yaml (default), json

-p, --policy <POLICIES>
    Policy files for validation

--skip-policies / --display-policy-coverage
    Policy-related options (same as other commands)
```

**Exit Code:** 0 if resolution successful

---

### 1.4 Registry Search

**Command:** `weaver registry search [OPTIONS] [SEARCH_STRING]`

**Purpose:** Searches a registry (Experimental and subject to change)

**Arguments:**
- `[SEARCH_STRING]` - Optional search string. If specified, returns matching values. Otherwise runs interactive terminal UI.

**Key Options:**
```
-r, --registry <REGISTRY>
    Registry source

--lineage
    Include lineage information (not yet implemented)

Standard diagnostic and registry options apply
```

---

### 1.5 Registry Stats

**Command:** `weaver registry stats [OPTIONS]`

**Purpose:** Calculate general statistics on a semantic convention registry

**Key Options:**
```
-r, --registry <REGISTRY>
    Registry source

Standard registry loading and diagnostic options apply
```

---

### 1.6 Registry Update Markdown

**Command:** `weaver registry update-markdown [OPTIONS] --target <TARGET> <MARKDOWN_DIR>`

**Purpose:** Update markdown files containing markers that indicate templates for updating specified sections

**Arguments:**
- `<MARKDOWN_DIR>` - Path to directory with markdown files

**Required Options:**
```
--target <TARGET>
    Target to generate snippets with
    Looks for template: {templates}/{target}/snippet.md.j2
```

**Key Options:**
```
-t, --templates <TEMPLATES>
    Templates directory (default: templates)

--dry-run
    Run in dry-run mode without making changes

--attribute-registry-base-url <URL>
    Base URL for attribute registry links

-D, --param <PARAM> / --params <PARAMS>
    Template parameters
```

---

### 1.7 Registry JSON Schema

**Command:** `weaver registry json-schema [OPTIONS]`

**Purpose:** Generate JSON Schema of resolved registry documents for template generator and policy engine

**Key Options:**
```
-j, --json-schema <JSON_SCHEMA>
    Type of JSON schema to generate (default: resolved-registry)
    Options: resolved-registry, semconv-group

-o, --output <OUTPUT>
    Output file (stdout if not specified)
```

**Use Cases:** Generate documentation or code for interacting with resolved registry format

---

### 1.8 Registry Diff

**Command:** `weaver registry diff [OPTIONS] --baseline-registry <BASELINE_REGISTRY>`

**Purpose:** Generate diff between two versions of a semantic convention registry

**Required Options:**
```
--baseline-registry <BASELINE_REGISTRY>
    Baseline semantic convention registry for comparison
```

**Key Options:**
```
-r, --registry <REGISTRY>
    Current registry (default: OpenTelemetry semantic-conventions)

--diff-format <DIFF_FORMAT>
    Diff rendering format: ansi (default), json, markdown

--diff-template <DIFF_TEMPLATE>
    Path to diff templates directory (default: diff_templates)

-o, --output <OUTPUT>
    Output directory (stdout if not specified)
```

---

### 1.9 Registry Emit

**Command:** `weaver registry emit [OPTIONS]`

**Purpose:** Emits semantic convention registry as example signals to OTLP receiver using standard OpenTelemetry SDK

**Key Options:**
```
--stdout
    Write telemetry to standard output

--endpoint <ENDPOINT>
    OTLP receiver endpoint (default: http://localhost:4317)
    Can be overridden by OTEL_EXPORTER_OTLP_ENDPOINT env var

Standard registry loading and policy options apply
```

**Default:** OTLP gRPC on localhost:4317

---

### 1.10 Registry Live Check

**Command:** `weaver registry live-check [OPTIONS]`

**Purpose:** Perform live check on sample telemetry by comparing to semantic convention registry. Includes flexible input ingestion, configurable assessment, and template-based output.

**Key Options:**
```
--input-source <INPUT_SOURCE>
    Input telemetry source: {file path} | stdin | otlp (default: otlp)

--input-format <INPUT_FORMAT>
    Input telemetry format: text | json (default: json)
    Not required for OTLP

--format <FORMAT>
    Report format: ansi (default), json

--templates <TEMPLATES>
    Templates directory (default: live_check_templates)

--no-stream
    Disable streaming output mode

-o, --output <OUTPUT>
    Output directory (stdout if not specified)

--otlp-grpc-address <ADDRESS>
    gRPC OTLP listener address (default: 0.0.0.0)

--otlp-grpc-port <PORT>
    gRPC OTLP listener port (default: 4317)

--admin-port <PORT>
    HTTP admin port for endpoints like /stop (default: 4320)

--inactivity-timeout <SECONDS>
    Max inactivity time before stopping listener (default: 10)

--advice-policies <ADVICE_POLICIES>
    Advice policies directory (overrides defaults)

--advice-preprocessor <ADVICE_PREPROCESSOR>
    Advice preprocessor (jq script for preprocessing registry data)
```

---

## 2. Diagnostic Commands

### 2.1 Diagnostic Init

**Command:** `weaver diagnostic init [OPTIONS] [TARGET]`

**Purpose:** Initializes a `diagnostic_templates` directory to define or override diagnostic output formats

**Arguments:**
- `[TARGET]` - Optional target for diagnostic templates. If empty, extracts all default templates

**Key Options:**
```
-t, --diagnostic-templates-dir <DIR>
    Path for diagnostic templates directory (default: diagnostic_templates)

--diagnostic-format <FORMAT>
    Diagnostic message format: ansi (default), json, gh_workflow_command
```

---

## 3. Completion Commands

### 3.1 Generate Completions

**Command:** `weaver completion [OPTIONS] <SHELL>`

**Purpose:** Generate shell completions

**Arguments:**
- `<SHELL>` - Target shell: bash, elvish, fish, powershell, zsh

---

## WeaverGen v2 Design Implications

### Command Mapping Strategy

Based on this comprehensive command reference, WeaverGen v2 should provide:

#### 1. **Core Workflow Commands**
```bash
# Map to weaver registry check
weavergen validate <registry> [options]

# Map to weaver registry generate  
weavergen generate <target> <registry> [options]

# Map to weaver registry resolve
weavergen resolve <registry> [options]
```

#### 2. **Discovery & Analysis Commands**
```bash
# Map to weaver registry search
weavergen search <registry> [query]

# Map to weaver registry stats
weavergen stats <registry>

# Map to weaver registry diff
weavergen diff <baseline> <current>
```

#### 3. **Documentation Commands** 
```bash
# Map to weaver registry update-markdown
weavergen docs update <target> <markdown-dir>

# Map to weaver registry json-schema
weavergen schema <type> [output]
```

#### 4. **Testing & Validation Commands**
```bash
# Map to weaver registry emit
weavergen emit <registry> [endpoint]

# Map to weaver registry live-check
weavergen live-check <registry> [options]
```

#### 5. **Utility Commands**
```bash
# Map to weaver diagnostic init
weavergen init-diagnostics [target]

# Map to weaver completion
weavergen completion <shell>
```

### Unified Interface Benefits

1. **Simplified Parameter Management**: Reduce complex option combinations through intelligent defaults
2. **Registry Auto-Detection**: Automatically detect local vs remote registries
3. **Template Discovery**: Auto-discover available templates and targets
4. **Policy Integration**: Seamless policy validation with clear feedback
5. **Output Format Consistency**: Unified output formatting across all commands
6. **Configuration Management**: Centralized configuration with sensible defaults
7. **Progress Feedback**: Visual progress indicators for long-running operations

### Advanced Features for v2

1. **Interactive Mode**: Terminal UI for registry exploration and command building
2. **Pipeline Support**: Chain commands together for complex workflows
3. **Watch Mode**: Monitor registries for changes and auto-regenerate
4. **Template Management**: Built-in template discovery, validation, and sharing
5. **Policy Library**: Curated policy sets for different use cases
6. **Diff Visualization**: Enhanced diff output with rich formatting
7. **Live Testing**: Integrated testing against running OTLP endpoints

---

## Implementation Priority Matrix

### High Priority (Core Functionality)
1. `registry check` → `weavergen validate`
2. `registry generate` → `weavergen generate`  
3. `registry resolve` → `weavergen resolve`
4. `registry search` → `weavergen search`

### Medium Priority (Developer Tools)
5. `registry stats` → `weavergen stats`
6. `registry diff` → `weavergen diff`
7. `registry update-markdown` → `weavergen docs`
8. `registry json-schema` → `weavergen schema`

### Lower Priority (Advanced Features)
9. `registry emit` → `weavergen emit`
10. `registry live-check` → `weavergen test`
11. `diagnostic init` → `weavergen init-diagnostics`
12. `completion` → `weavergen completion`

This comprehensive reference ensures WeaverGen v2 will provide intuitive access to the full power of the Weaver toolchain while maintaining the unified BPMN architecture and 80/20 ease-of-use principles.