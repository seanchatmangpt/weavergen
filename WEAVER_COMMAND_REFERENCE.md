# 📚 WEAVER COMMAND REFERENCE DOCUMENTATION

**Version:** OpenTelemetry Weaver (otellib-weaver-cli)  
**Purpose:** Define WeaverGen v2 Architecture  
**Generated:** 2025-07-01  

This document contains the complete help text for every Weaver command to inform the design of WeaverGen v2, a Python wrapper that will provide enhanced functionality around the Weaver toolchain.

---

## 🔧 MAIN COMMAND

### `weaver`

```
Manage semantic convention registry and telemetry schema workflows (OpenTelemetry Project)

Usage: weaver [OPTIONS] <COMMAND>

Commands:
  registry    Manage Semantic Convention Registry
  diagnostic  Manage Diagnostic Messages
  completion  Generate shell completions
  help        Print this message or the help of the given subcommand(s)

Options:
      --debug...  Turn debugging information on
      --quiet     Turn the quiet mode on (i.e., minimal output)
      --future    Enable the most recent validation rules for the semconv registry. It is recommended to enable this flag when checking a new registry. Note: `semantic_conventions` main branch should always enable this flag
  -h, --help      Print help
  -V, --version   Print version
```

**WeaverGen v2 Implications:**
- Core orchestrator should support debug levels and quiet mode
- Future flag suggests version compatibility strategy needed
- CLI should maintain same help/version patterns

---

## 📊 REGISTRY COMMANDS

### `weaver registry`

```
Manage Semantic Convention Registry

Usage: weaver registry [OPTIONS] <COMMAND>

Commands:
  check            Validates a semantic convention registry.
  generate         Generates artifacts from a semantic convention registry.
  resolve          Resolves a semantic convention registry.
  search           Searches a registry (Note: Experimental and subject to change)
  stats            Calculate a set of general statistics on a semantic convention registry
  update-markdown  Update markdown files that contain markers indicating the templates used to update the specified sections
  json-schema      Generate the JSON Schema of the resolved registry documents consumed by the template generator and the policy engine.
  diff             Generate a diff between two versions of a semantic convention registry.
  emit             Emits a semantic convention registry as example signals to your OTLP receiver.
  live-check       Perform a live check on sample telemetry by comparing it to a semantic convention registry.
  help             Print this message or the help of the given subcommand(s)
```

**WeaverGen v2 Implications:**
- Registry management is core functionality
- Need Python wrappers for all 10 registry operations
- Experimental features should be clearly marked
- Live telemetry capabilities indicate real-time processing needs

---

### `weaver registry check`

```
Validates a semantic convention registry.

The validation process for a semantic convention registry involves several steps:
- Loading the semantic convention specifications from a local directory or a git repository.
- Parsing the loaded semantic convention specifications.
- Resolving references and extends clauses within the specifications.
- Checking compliance with specified Rego policies, if provided.

Note: The `-d` and `--registry-git-sub-dir` options are only used when the registry is a Git URL otherwise these options are ignored.

The process exits with a code of 0 if the registry validation is successful.

Usage: weaver registry check [OPTIONS]

Options:
      --debug...
  -r, --registry <REGISTRY>
          Local folder, Git repo URL, or Git archive URL of the semantic convention registry. For Git URLs, a sub-folder can be specified using the `[sub-folder]` syntax after the URL
          [default: https://github.com/open-telemetry/semantic-conventions.git[model]]
      --quiet
  -s, --follow-symlinks
          Boolean flag to specify whether to follow symlinks when loading the registry. Default is false
      --future
      --include-unreferenced
          Boolean flag to include signals and attributes defined in dependency registries, even if they are not explicitly referenced in the current (custom) registry
      --baseline-registry <BASELINE_REGISTRY>
          Parameters to specify the baseline semantic convention registry
  -p, --policy <POLICIES>
          Optional list of policy files or directories to check against the files of the semantic convention registry.  If a directory is provided all `.rego` files in the directory will be loaded
      --skip-policies
          Skip the policy checks
      --display-policy-coverage
          Display the policy coverage report (useful for debugging)
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          Format used to render the diagnostic messages. Predefined formats are: ansi, json, gh_workflow_command
          [default: ansi]
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          Path to the directory where the diagnostic templates are located
          [default: diagnostic_templates]
      --diagnostic-stdout
          Send the output to stdout instead of stderr
  -h, --help
```

**WeaverGen v2 Implications:**
- Multi-source registry support (local, Git, Git archive)
- Git subfolder syntax parsing needed
- Rego policy engine integration required
- Multiple diagnostic output formats (ANSI, JSON, GitHub Workflow)
- Symlink handling consideration
- Baseline comparison capabilities

---

### `weaver registry generate`

```
Generates artifacts from a semantic convention registry.

Rego policies present in the registry or specified using -p or --policy will be automatically validated by the policy engine before the artifact generation phase.

Note: The `-d` and `--registry-git-sub-dir` options are only used when the registry is a Git URL otherwise these options are ignored.

The process exits with a code of 0 if the generation is successful.

Usage: weaver registry generate [OPTIONS] <TARGET> [OUTPUT]

Arguments:
  <TARGET>
          Target to generate the artifacts for
  [OUTPUT]
          Path to the directory where the generated artifacts will be saved. Default is the `output` directory
          [default: output]

Options:
      --debug...
  -t, --templates <TEMPLATES>
          Path to the directory where the templates are located. Default is the `templates` directory
          [default: templates]
  -c, --config <CONFIG>
          List of `weaver.yaml` configuration files to use. When there is a conflict, the last one will override the previous ones for the keys that are defined in both
      --quiet
  -D, --param <PARAM>
          Parameters key=value, defined in the command line, to pass to the templates. The value must be a valid YAML value
      --params <PARAMS>
          Parameters, defined in a YAML file, to pass to the templates
  -r, --registry <REGISTRY>
          [default: https://github.com/open-telemetry/semantic-conventions.git[model]]
  -s, --follow-symlinks
      --include-unreferenced
  -p, --policy <POLICIES>
      --skip-policies
      --display-policy-coverage
      --future
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          [default: ansi]
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          [default: diagnostic_templates]
      --diagnostic-stdout
  -h, --help
```

**WeaverGen v2 Implications:**
- Target-based generation system
- Template directory management
- Configuration file cascading (weaver.yaml)
- Command-line and file-based parameter passing
- YAML parameter validation required
- Policy validation before generation

---

### `weaver registry resolve`

```
Resolves a semantic convention registry.

Rego policies present in the registry or specified using -p or --policy will be automatically validated by the policy engine before the artifact generation phase.

Note: The `-d` and `--registry-git-sub-dir` options are only used when the registry is a Git URL otherwise these options are ignored.

The process exits with a code of 0 if the resolution is successful.

Usage: weaver registry resolve [OPTIONS]

Options:
      --debug...
  -r, --registry <REGISTRY>
          [default: https://github.com/open-telemetry/semantic-conventions.git[model]]
      --quiet
  -s, --follow-symlinks
      --future
      --include-unreferenced
      --lineage
          Flag to indicate if lineage information should be included in the resolved schema (not yet implemented)
  -o, --output <OUTPUT>
          Output file to write the resolved schema to If not specified, the resolved schema is printed to stdout
  -f, --format <FORMAT>
          Output format for the resolved schema If not specified, the resolved schema is printed in YAML format Supported formats: yaml, json Default format: yaml Example: `--format json`
          [default: yaml]
          Possible values:
          - yaml: YAML format
          - json: JSON format
  -p, --policy <POLICIES>
      --skip-policies
      --display-policy-coverage
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          [default: ansi]
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          [default: diagnostic_templates]
      --diagnostic-stdout
  -h, --help
```

**WeaverGen v2 Implications:**
- Schema resolution with lineage tracking (future feature)
- Dual output format support (YAML/JSON)
- File or stdout output options
- Resolved schema can be consumed by other tools

---

### `weaver registry search`

```
Searches a registry (Note: Experimental and subject to change)

Usage: weaver registry search [OPTIONS] [SEARCH_STRING]

Arguments:
  [SEARCH_STRING]  An (optional) search string to use.  If specified, will return matching values on the command line. Otherwise, runs an interactive terminal UI

Options:
      --debug...
  -r, --registry <REGISTRY>
          [default: https://github.com/open-telemetry/semantic-conventions.git[model]]
      --quiet
  -s, --follow-symlinks
      --future
      --include-unreferenced
      --lineage
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          [default: ansi]
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          [default: diagnostic_templates]
      --diagnostic-stdout
  -h, --help
```

**WeaverGen v2 Implications:**
- Interactive TUI capability when no search string provided
- Command-line search when string provided
- Experimental status indicates potential API changes

---

### `weaver registry stats`

```
Calculate a set of general statistics on a semantic convention registry

Usage: weaver registry stats [OPTIONS]

Options: [Similar to other registry commands]
```

**WeaverGen v2 Implications:**
- Analytics and metrics functionality
- Registry health monitoring capabilities

---

### `weaver registry update-markdown`

```
Update markdown files that contain markers indicating the templates used to update the specified sections

Usage: weaver registry update-markdown [OPTIONS] --target <TARGET> <MARKDOWN_DIR>

Arguments:
  <MARKDOWN_DIR>  Path to the directory where the markdown files are located

Options:
      --debug...
  -r, --registry <REGISTRY>
          [default: https://github.com/open-telemetry/semantic-conventions.git[model]]
      --quiet
  -s, --follow-symlinks
      --future
      --include-unreferenced
      --dry-run
          Whether or not to run updates in dry-run mode
      --attribute-registry-base-url <ATTRIBUTE_REGISTRY_BASE_URL>
          Optional path to the attribute registry. If provided, all attributes will be linked here
  -D, --param <PARAM>
  -t, --templates <TEMPLATES>
          [default: templates]
      --target <TARGET>
          If provided, the target to generate snippets with. Note: `registry update-markdown` will look for a specific jinja template: {templates}/{target}/snippet.md.j2
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          [default: ansi]
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          [default: diagnostic_templates]
      --diagnostic-stdout
  -h, --help
```

**WeaverGen v2 Implications:**
- Documentation automation with markers
- Dry-run capability for safety
- Template-driven markdown updates
- Specific template naming convention: `{templates}/{target}/snippet.md.j2`

---

### `weaver registry json-schema`

```
Generate the JSON Schema of the resolved registry documents consumed by the template generator and the policy engine.

The produced JSON Schema can be used to generate documentation of the resolved registry format or to generate code in your language of choice if you need to interact with the resolved registry format for any reason.

Usage: weaver registry json-schema [OPTIONS]

Options:
      --debug...
  -j, --json-schema <JSON_SCHEMA>
          The type of JSON schema to generate
          [default: resolved-registry]
          Possible values:
          - resolved-registry: The JSON schema of a resolved registry
          - semconv-group:     The JSON schema of a semantic convention group
  -o, --output <OUTPUT>
          Output file to write the JSON schema to If not specified, the JSON schema is printed to stdout
      --quiet
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          [default: ansi]
      --future
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          [default: diagnostic_templates]
      --diagnostic-stdout
  -h, --help
```

**WeaverGen v2 Implications:**
- Schema generation for tooling integration
- Two schema types: resolved-registry and semconv-group
- Enables code generation in multiple languages
- Self-describing format capabilities

---

### `weaver registry diff`

```
Generate a diff between two versions of a semantic convention registry.

This diff can then be rendered in multiple formats:
- a console-friendly format (default: ansi),
- a structured document in JSON format,
- ...

Usage: weaver registry diff [OPTIONS] --baseline-registry <BASELINE_REGISTRY>

Options:
      --debug...
  -r, --registry <REGISTRY>
          [default: https://github.com/open-telemetry/semantic-conventions.git[model]]
      --quiet
  -s, --follow-symlinks
      --future
      --include-unreferenced
      --baseline-registry <BASELINE_REGISTRY>
          Parameters to specify the baseline semantic convention registry
      --diff-format <DIFF_FORMAT>
          Format used to render the schema changes. Predefined formats are: ansi, json, and markdown
          [default: ansi]
      --diff-template <DIFF_TEMPLATE>
          Path to the directory where the schema changes templates are located
          [default: diff_templates]
  -o, --output <OUTPUT>
          Path to the directory where the generated artifacts will be saved. If not specified, the diff report is printed to stdout
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          [default: ansi]
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          [default: diagnostic_templates]
      --diagnostic-stdout
  -h, --help
```

**WeaverGen v2 Implications:**
- Version comparison capabilities
- Multiple diff formats (ANSI, JSON, Markdown)
- Template-driven diff rendering
- Change tracking and migration support

---

### `weaver registry emit`

```
Emits a semantic convention registry as example signals to your OTLP receiver.

This uses the standard OpenTelemetry SDK, defaulting to OTLP gRPC on localhost:4317.

Usage: weaver registry emit [OPTIONS]

Options:
      --debug...
  -r, --registry <REGISTRY>
          [default: https://github.com/open-telemetry/semantic-conventions.git[model]]
      --quiet
  -s, --follow-symlinks
      --future
      --include-unreferenced
  -p, --policy <POLICIES>
      --skip-policies
      --display-policy-coverage
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          [default: ansi]
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          [default: diagnostic_templates]
      --diagnostic-stdout
      --stdout
          Write the telemetry to standard output
      --endpoint <ENDPOINT>
          Endpoint for the OTLP receiver. OTEL_EXPORTER_OTLP_ENDPOINT env var will override this
          [default: http://localhost:4317]
  -h, --help
```

**WeaverGen v2 Implications:**
- Live telemetry generation from conventions
- OTLP integration required
- Environment variable override support
- Example signal generation for testing

---

### `weaver registry live-check`

```
Perform a live check on sample telemetry by comparing it to a semantic convention registry.

Includes: Flexible input ingestion, configurable assessment, and template-based output.

Usage: weaver registry live-check [OPTIONS]

Options:
      --debug...
  -r, --registry <REGISTRY>
          [default: https://github.com/open-telemetry/semantic-conventions.git[model]]
      --quiet
  -s, --follow-symlinks
      --future
      --include-unreferenced
  -p, --policy <POLICIES>
      --skip-policies
      --display-policy-coverage
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          [default: ansi]
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          [default: diagnostic_templates]
      --diagnostic-stdout
      --input-source <INPUT_SOURCE>
          Where to read the input telemetry from. {file path} | stdin | otlp
          [default: otlp]
      --input-format <INPUT_FORMAT>
          The format of the input telemetry. (Not required for OTLP). text | json
          [default: json]
      --format <FORMAT>
          Format used to render the report. Predefined formats are: ansi, json
          [default: ansi]
      --templates <TEMPLATES>
          Path to the directory where the templates are located
          [default: live_check_templates]
      --no-stream
          Disable stream mode. Use this flag to disable streaming output.
      -o, --output <OUTPUT>
          Path to the directory where the generated artifacts will be saved. If not specified, the report is printed to stdout
      --otlp-grpc-address <OTLP_GRPC_ADDRESS>
          Address used by the gRPC OTLP listener
          [default: 0.0.0.0]
      --otlp-grpc-port <OTLP_GRPC_PORT>
          Port used by the gRPC OTLP listener
          [default: 4317]
      --admin-port <ADMIN_PORT>
          Port used by the HTTP admin port (endpoints: /stop)
          [default: 4320]
      --inactivity-timeout <INACTIVITY_TIMEOUT>
          Max inactivity time in seconds before stopping the listener
          [default: 10]
      --advice-policies <ADVICE_POLICIES>
          Advice policies directory. Set this to override the default policies
      --advice-preprocessor <ADVICE_PREPROCESSOR>
          Advice preprocessor. A jq script to preprocess the registry data before passing to rego.
  -h, --help
```

**WeaverGen v2 Implications:**
- Real-time telemetry validation
- Multiple input sources (file, stdin, OTLP)
- Streaming vs batch mode
- gRPC server capabilities
- Admin interface for control
- JQ preprocessing pipeline
- Rego policy advice system

---

## 🔧 DIAGNOSTIC COMMANDS

### `weaver diagnostic`

```
Manage Diagnostic Messages

Usage: weaver diagnostic [OPTIONS] <COMMAND>

Commands:
  init  Initializes a `diagnostic_templates` directory to define or override diagnostic output formats
  help  Print this message or the help of the given subcommand(s)

Options:
      --debug...
      --quiet
      --future
  -h, --help
```

### `weaver diagnostic init`

```
Initializes a `diagnostic_templates` directory to define or override diagnostic output formats

Usage: weaver diagnostic init [OPTIONS] [TARGET]

Arguments:
  [TARGET]  Optional target to initialize the diagnostic templates for. If empty, all default templates will be extracted [default: ]

Options:
      --debug...
  -t, --diagnostic-templates-dir <DIAGNOSTIC_TEMPLATES_DIR>
          Optional path where the diagnostic templates directory should be created [default: diagnostic_templates]
      --diagnostic-format <DIAGNOSTIC_FORMAT>
          Format used to render the diagnostic messages. Predefined formats are: ansi, json, gh_workflow_command [default: ansi]
      --quiet
      --diagnostic-template <DIAGNOSTIC_TEMPLATE>
          [default: diagnostic_templates]
      --future
      --diagnostic-stdout
  -h, --help
```

**WeaverGen v2 Implications:**
- Template-driven diagnostic system
- Customizable diagnostic output formats
- GitHub Workflow integration support

---

## 🔧 UTILITY COMMANDS

### `weaver completion`

```
Generate shell completions

Usage: weaver completion [OPTIONS] <SHELL>

Arguments:
  <SHELL>  The shell to generate the completions for [possible values: bash, elvish, fish, powershell, zsh]

Options:
      --debug...
      --quiet
      --future
  -h, --help
```

**WeaverGen v2 Implications:**
- Multi-shell completion support
- Developer experience enhancement

---

## 🎯 WEAVERGEN V2 ARCHITECTURE REQUIREMENTS

Based on this comprehensive command analysis, WeaverGen v2 should provide:

### Core Architecture

1. **Registry Management Layer**
   - Local, Git, and Git archive registry support
   - Symlink handling and subfolder syntax parsing
   - Baseline comparison and version diffing

2. **Template Engine Integration**
   - Jinja2 template system with Weaver compatibility
   - Parameter passing (CLI and file-based)
   - Template directory management
   - Multiple output format support

3. **Policy Engine Wrapper**
   - Rego policy validation
   - Policy coverage reporting
   - Advice system integration

4. **Live Telemetry Interface**
   - OTLP server capabilities
   - Real-time validation and checking
   - Streaming and batch mode support

5. **Diagnostic System**
   - Multiple output formats (ANSI, JSON, GitHub Workflow)
   - Template-driven diagnostics
   - Customizable error reporting

### Enhanced Python Features

1. **Pydantic Model Generation**
   - From resolved registry schemas
   - Type-safe registry interactions
   - Validation model creation

2. **AI-Enhanced Operations**
   - LLM-assisted template generation
   - Intelligent convention analysis
   - Automated documentation generation

3. **BPMN Workflow Integration**
   - Visual workflow orchestration
   - Multi-step generation pipelines
   - Error handling and recovery

4. **Span-Based Validation**
   - OpenTelemetry instrumentation
   - Performance monitoring
   - Real execution validation

### CLI Design Principles

1. **Compatibility**: Maintain Weaver CLI patterns and options
2. **Enhancement**: Add Python-specific capabilities
3. **Integration**: Seamless Weaver binary integration
4. **Usability**: Rich console output and interactive features

---

**Document Status:** ✅ Complete  
**Next Step:** Design WeaverGen v2 architecture based on this reference  
**Validation:** All Weaver commands documented with implications analysis