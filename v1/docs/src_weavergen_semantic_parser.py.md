This Python file implements the WeaverGen Semantic Convention Parser.
It is designed to parse OpenTelemetry semantic conventions from YAML or JSON files.
The `ParsedConvention` dataclass defines the structure for a parsed semantic convention, including its name, type, brief description, stability, attributes, and groups.
The `SemanticConventionParser` class provides the core functionality:
1. `parse_convention_file`: Reads a YAML or JSON file, extracts metadata, and populates the `ParsedConvention` object.
2. It prioritizes extracting attributes from `groups` but also supports direct `attributes` definitions.
3. `validate_convention`: Performs basic validation on the parsed convention, checking for the presence of a name and attributes, and ensuring each attribute has an `id` and `type`.
This module is a fundamental component for WeaverGen, enabling it to understand and process semantic convention definitions for subsequent code generation and validation tasks.