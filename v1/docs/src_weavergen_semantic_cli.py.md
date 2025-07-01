This Python file defines a CLI extension for WeaverGen, specifically for semantic convention operations.
It uses `typer` for command-line interface creation and `rich` for enhanced console output.
The `generate_semantic` command triggers code generation from a specified semantic convention file.
It utilizes `SemanticConventionRuntime` to process the convention and generate code.
The `validate_semantic` command validates a semantic convention file.
It uses `SemanticConventionParser` to parse and validate the convention, reporting any issues found.
This module provides a direct command-line interface for interacting with the semantic convention processing capabilities of WeaverGen.