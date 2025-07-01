This Python file defines the `SemanticConventionRuntime` class, which acts as a runtime engine for processing semantic conventions.
It integrates `SemanticConventionParser` for parsing and validating convention files.
It uses `WeaverGenTemplateEngine` to generate code from the parsed conventions.
The `process_convention` asynchronous method orchestrates the workflow:
1. Parses the semantic convention file.
2. Validates the parsed convention, returning errors if any issues are found.
3. Creates the output directory if it doesn't exist.
4. Generates Pydantic models from the convention data using the template engine.
5. Generates validators from the convention data using the template engine.
6. Writes the generated models and validators to Python files within the specified output directory.
This module is a key component in the WeaverGen system for transforming semantic convention definitions into executable code artifacts.