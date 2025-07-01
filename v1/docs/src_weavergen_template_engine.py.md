This Python file implements the WeaverGen Template Engine, responsible for generating code from semantic conventions using Jinja2 templates.
It initializes a Jinja2 environment and ensures the presence of default templates for Pydantic models, validators, and CLI commands.
`generate_pydantic_models` creates Pydantic `BaseModel` classes based on the attributes and groups defined in a semantic convention.
`generate_validators` generates Python code for validating OpenTelemetry spans against the requirements specified in the semantic convention.
`generate_cli_commands` produces Typer-based CLI commands for interacting with the generated code.
The `_ensure_default_templates` method writes predefined Jinja2 template content to files if they don't already exist, ensuring a baseline for code generation.
The templates use placeholders for convention details, attributes, and groups, allowing dynamic code generation.
This module is a core component of WeaverGen, enabling the transformation of high-level semantic definitions into concrete, executable code artifacts.