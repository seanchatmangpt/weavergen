This Python file defines the core `WeaverGen` class, which acts as a Python wrapper around the OpenTelemetry Weaver Forge binary.
It manages the configuration, installation, and execution of the Weaver binary.
`WeaverGen` handles loading and saving its configuration (including the Weaver binary path) from `~/.weavergen/config.json`.
It includes logic to `_ensure_weaver_binary` is available, attempting to find it in PATH, common installation locations, or performing an `_auto_install_weaver` if necessary.
Auto-installation supports `cargo` (Rust's package manager) and direct `download` from GitHub releases, adapting to the operating system (macOS, Linux, Windows) and architecture.
`generate` method executes the `weaver registry generate` command to produce code from semantic conventions, collecting generated files and parsing warnings.
`validate_registry` method runs `weaver registry check` to validate semantic convention files.
`list_templates` provides information about available code generation templates (currently with example data).
It defines custom exceptions: `WeaverGenError` for general errors and `WeaverNotFoundError` when the binary is not found.
This module is fundamental to WeaverGen's operation, abstracting the complexities of interacting with the external Weaver Forge tool and providing a user-friendly interface for code generation and validation.