# WeaverGen Project

This project uses WeaverGen to generate code from OpenTelemetry semantic conventions.

## Quick Start

1. Generate code from semantic conventions:
   ```bash
   weavergen generate semantic-conventions/http.yaml --lang python --output generated
   ```

2. Check available languages:
   ```bash
   weavergen generate semantic-conventions/http.yaml --lang python,go,java --output generated
   ```

## Project Structure

```
test-weavergen-project/
├── semantic-conventions/   # Your semantic convention YAML files
│   └── http.yaml          # Sample HTTP semantic convention
├── templates/             # Custom Jinja2 templates (optional)
│   └── python_http.j2     # Sample Python template
└── generated/             # Generated code output (git ignored)
```

## Adding New Semantic Conventions

1. Create a new YAML file in `semantic-conventions/`
2. Run `weavergen generate` to generate code
3. Find your generated code in `generated/<language>/`

## Custom Templates

WeaverGen will use custom templates from the `templates/` directory if available.
Template naming convention: `<language>_<convention>.j2`

For more information: https://github.com/seanchatmangpt/weavergen
