File: weavergen_simple.py

This module provides a "dead simple" wrapper around the OpenTelemetry Weaver binary, designed for straightforward code generation from semantic conventions. It emphasizes minimalism, with no BPMN, AI, or unnecessary complexity, aiming to be a <300-line solution.

Key components and functionalities:

- **`WeaverGen` Class**:
    - **`_find_weaver`**: Locates the `weaver` binary in the system's PATH, Cargo installation directory, or local development paths. If not found, it prompts the user to install it.
    - **`generate`**: Generates code for a specified language (e.g., Python, Go, Rust, Java, JavaScript) from a semantic convention YAML file. It maps common language names to Weaver template names and executes the `weaver generate` command.
    - **`validate`**: Validates a semantic convention file using the `weaver check` command.

- **Typer CLI Application (`app`)**:
    - **`generate` command**: The primary command for code generation. It takes a semantic convention YAML file, a list of target languages, and an output directory. It can optionally validate the semantic file before generation. It provides rich console output with progress indicators.
    - **`validate` command**: Validates a given semantic convention YAML file and reports whether it's valid or not.
    - **`install` command**: Installs the `weaver-forge` binary via Cargo. It checks for Cargo availability and provides instructions if not found. It also streams the installation output to the console.
    - **`list_languages` command**: Displays a table of supported target languages, their file extensions, and descriptions.
    - **`version` command**: Shows version information for `WeaverGen Simple` and attempts to retrieve the version of the underlying `weaver` binary.

The module uses `typer` for building the command-line interface, `rich` for enhanced console output (including progress bars, spinners, and tables), `subprocess` for executing the `weaver` binary, `pathlib` for file system operations, and `shutil` for finding executables. It serves as a lean and efficient tool for semantic convention-driven code generation.