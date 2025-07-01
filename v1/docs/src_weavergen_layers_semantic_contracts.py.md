This Python file defines the Contracts Layer Extension for WeaverGen, specifically for semantic convention support.
It uses Pydantic models to define data contracts.
`SemanticConventionContract` models the structure of a semantic convention, including its name, type, description, stability, attributes, and groups.
`GenerationContract` defines the contract for code generation requests, specifying the semantic convention, output directory, target language, template type, and whether validation is enabled.
`GenerationResultContract` outlines the expected structure of code generation results, including success status, list of generated files, validation outcomes, duration, and timestamp.
These contracts ensure clear data exchange and type safety across different components of the WeaverGen system, particularly when dealing with semantic conventions and code generation processes.