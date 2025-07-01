This Python file, `run_forge.py`, demonstrates the usage of `CompleteForgeGenerator` from the `weavergen.forge_complete` module.
It is a simple script to generate a 4-layer architecture from a semantic convention file.
The script first defines `semantic_file` and `output_dir` paths.
It includes logic to create a dummy `test_semantic.yaml` file if it doesn't already exist, defining basic HTTP span attributes.
It then initializes `CompleteForgeGenerator` with the semantic file and output directory.
Finally, it calls the `generate_4_layer_architecture()` method to perform the code generation.
The script prints a success message and lists the generated files if the generation is successful, otherwise, it prints an error message.
This file serves as a quick example or test case for generating code using the `CompleteForgeGenerator`.