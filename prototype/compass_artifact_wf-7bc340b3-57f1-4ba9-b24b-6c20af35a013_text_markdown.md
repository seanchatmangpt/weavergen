# OpenTelemetry Weaver Forge comprehensive documentation guide

OpenTelemetry Weaver Forge is a Rust-based template engine that generates documentation and code from semantic convention registries, processing the entire OpenTelemetry semantic convention registry in under 2 seconds. Built to replace the deprecated build-tools, Weaver uses **MiniJinja** (Jinja2-compatible) templating with **JQ-compatible** filters for data transformation, enabling language-specific code generation across multiple programming languages.

## Semantic convention YAML structure and required fields

Semantic convention YAML files in Weaver follow a structured format with specific required and optional fields. The basic structure defines groups of conventions with their attributes, relationships, and metadata.

### Core YAML schema

```yaml
groups:
  - id: <unique_identifier>
    type: <convention_type>
    brief: <brief_description>
    stability: <stability_level>
    note: <detailed_description>
    extends: <parent_convention_id>
    deprecated: <deprecation_info>
    attributes:
      - ref: <attribute_reference>
        requirement_level: <requirement>
        brief: <attribute_description>
        note: <additional_notes>
        examples: [<example_values>]
    span_kind: <span_kind>
    events: [<event_references>]
```

**Required fields** include `id` (unique string identifier), `type` (convention type enum), `brief` (string description), and `stability` (enum specifying maturity level). The `type` field supports values like `span`, `attribute_group`, `metric`, `event`, and `resource`, defaulting to `span` with a warning if omitted.

### Real-world example from semantic conventions

Here's an actual RPC span convention from the OpenTelemetry repository:

```yaml
groups:
  - id: rpc
    type: attribute_group
    brief: 'This document defines semantic conventions for remote procedure calls.'
    attributes:
      - ref: rpc.system
        requirement_level: required
      - ref: rpc.service
        requirement_level: recommended
      - ref: rpc.method
        requirement_level: recommended
      - ref: network.transport
        requirement_level: recommended

  - id: span.rpc.client
    type: span
    stability: experimental
    brief: 'This document defines semantic conventions for remote procedure call client spans.'
    extends: rpc
    span_kind: client
    events: [rpc.message]
    attributes:
      - ref: network.peer.address
        requirement_level: recommended
```

Attributes support requirement levels (`required`, `recommended`, `opt_in`), stability markers, and can include examples, deprecation notices, and detailed notes. The `extends` field enables inheritance from parent conventions, promoting reusability across the registry.

## Template syntax and context variables

Weaver Forge uses MiniJinja, providing full Jinja2 compatibility with custom extensions for semantic conventions. Templates process resolved convention data through the `ctx` object, which contains all necessary information for code generation.

### Context object structure

The `ctx` object provides access to:
- **`ctx.root_namespace`**: Root namespace of the semantic convention group
- **`ctx.attributes`**: Array of resolved attributes with full metadata
- **`ctx.id`**: Convention identifier
- **`ctx.type`**: Convention type (span, metric, etc.)
- **`ctx.brief`**: Brief description
- **`ctx.stability`**: Stability level
- **`ctx.note`**: Detailed documentation

Each attribute in `ctx.attributes` contains properties like `id`, `type`, `brief`, `stability`, `requirement_level`, `examples`, and `deprecated`.

### Template example with context usage

```jinja2
{%- set file_name = ctx.root_namespace | snake_case -%}
{{- template.set_file_name("attributes/" ~ file_name ~ ".md") -}}

# {{ ctx.root_namespace | title }} Attributes

{% for attribute in ctx.attributes %}
## {{ attribute.id }}

- **Type**: {{ attribute.type }}
- **Brief**: {{ attribute.brief }}
- **Stability**: {{ attribute.stability }}
{% if attribute.note %}
- **Note**: {{ attribute.note }}
{% endif %}
{% endfor %}
```

### Available filters and functions

Weaver provides case conversion filters (`snake_case`, `camel_case`, `pascal_case`, `kebab_case`) and semantic convention-specific filters like `snake_case_const` for generating language-appropriate constant names. The `map_text` filter enables type mapping based on configuration:

```jinja2
{{ attribute.type | map_text("rust_types") }}
```

## Directory structure requirements

Weaver follows a hierarchical template organization with specific structural requirements. The standard layout organizes templates by target output type under a `registry` directory.

### Required directory structure

```
templates/
└── registry/
    ├── go/
    │   ├── weaver.yaml
    │   └── *.j2
    ├── rust/
    │   ├── weaver.yaml
    │   └── *.j2
    ├── python/
    │   ├── weaver.yaml
    │   └── *.j2
    └── markdown/
        ├── weaver.yaml
        └── *.j2
```

Each target directory **must** contain a `weaver.yaml` configuration file defining template processing rules, filters, and parameters. Template files use the `.j2` extension following Jinja2 conventions.

### Configuration file structure

The `weaver.yaml` file controls template processing:

```yaml
# Type mappings for language-specific conversions
text_maps:
  rust_types:
    int: i64
    double: f64
    boolean: bool
    string: String
    string[]: Vec<String>

# Template parameters
params:
  excluded_namespaces: [ios, android, dotnet]
  output: "./"

# Template definitions
templates:
  - template: "attributes.j2"
    filter: semconv_grouped_attributes
    application_mode: each
    file_name: "attributes/{{ctx.root_namespace | snake_case}}.rs"
```

The `application_mode` setting determines processing behavior: `each` generates separate files per convention group, while `single` processes all groups together.

## Weaver Forge commands and usage

Weaver provides several registry commands for different stages of the generation pipeline. The primary command, `generate`, creates code and documentation from semantic conventions.

### Core command: registry generate

```bash
weaver registry generate [OPTIONS] <target>
```

Key options include:
- `--templates <PATH>`: Specify template directory or remote repository
- `--param <KEY>=<VALUE>`: Pass parameters to templates
- `--registry <URL>`: Override semantic convention source
- `-D<paramName>=<value>`: Legacy parameter syntax for build-tools compatibility

### Practical usage examples

Generate Java code from GitHub repository:
```bash
weaver registry generate \
  --templates https://github.com/open-telemetry/semantic-conventions-java.git[buildscripts/templates] \
  java
```

Generate Python code with custom parameters:
```bash
weaver registry generate \
  --templates https://github.com/open-telemetry/opentelemetry-python.git[scripts/semconv/templates] \
  --param output=./ \
  --param filter=any \
  ./
```

### Additional registry commands

- **`registry resolve`**: Resolves references and inheritance in conventions
- **`registry check`**: Validates against policy files
- **`registry stats`**: Displays registry statistics
- **`registry diff`**: Compares two registries
- **`registry update-markdown`**: Updates existing markdown documentation

Global options like `-d` (debug) provide additional logging for troubleshooting template processing.

## Naming conventions and patterns

Weaver enforces specific naming conventions across multiple levels, from file organization to semantic convention identifiers.

### File naming patterns

Template files follow snake_case convention with `.j2` extension: `semantic_attributes.j2`, `http_metrics.j2`. Generated files can be dynamically named using template functions:

```jinja2
{% set file_name = ctx.output + (ctx.root_namespace | snake_case) ~ "_attributes.py" -%}
{{- template.set_file_name(file_name) -}}
```

### Semantic convention naming rules

Attributes use dot notation for namespacing with snake_case for multi-word components:
- **Correct**: `http.request.method`, `http.response.status_code`
- **Avoid**: Underscores where dots make sense (`rate_limiting` not `rate.limiting`)

Namespace structure follows hierarchical patterns: `{domain}.{system}.{property}`, such as `db.cassandra.consistency_level` or `aws.s3.key`.

### Reserved prefixes and constraints

The `otel.*` prefix is reserved for OpenTelemetry specification use. Custom attributes should avoid conflicting with existing OpenTelemetry namespaces to prevent collisions.

## Best practices and advanced usage

Successful Weaver Forge projects follow established patterns for organization and workflow automation.

### Project organization

```
my-weaver-project/
├── templates/
│   └── registry/
│       ├── go/
│       ├── python/
│       └── rust/
├── output/
├── scripts/
│   └── generate.sh
└── README.md
```

### Automation workflow

Create generation scripts for consistent output:

```bash
#!/bin/bash
SEMCONV_VERSION="v1.32.0"

for target in go rust python java; do
  echo "Generating $target..."
  weaver registry generate \
    --templates ./templates \
    --param version=$SEMCONV_VERSION \
    --param output=./output/$target/ \
    $target
done
```

### JQ filter usage

Weaver's JQ filters enable sophisticated data preprocessing. The `semconv_grouped_attributes` filter groups attributes by namespace while excluding specified namespaces:

```yaml
filter: |
  semconv_grouped_attributes({
    "exclude_root_namespace": $excluded_namespaces
  }) | map({
    root_namespace: .root_namespace,
    attributes: .attributes | map(select(.stability != "deprecated")),
    output: $output + "attributes/"
  })
```

This comprehensive documentation provides the foundation for effectively using OpenTelemetry Weaver Forge to generate code and documentation from semantic conventions, following official patterns and best practices from the OpenTelemetry project.