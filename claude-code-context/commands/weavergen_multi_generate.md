# WeaverGen Multi-Language Generation

Generate code for multiple target languages from semantic conventions using OTel Weaver Forge with full session continuity.

## Instructions

1. **Context Validation**
   - Check current generation session state and active registry
   - Validate target language configurations and output directories
   - Ensure OTel Weaver binary is available and configured

2. **Multi-Language Generation Execution**
   - Parse target languages from arguments (comma-separated)
   - Deploy parallel generation workflows for each language
   - Monitor generation progress with real-time feedback
   - Validate generated code quality and compliance

3. **Results Synthesis**
   - Aggregate generation results across all target languages
   - Provide performance metrics and quality assessment
   - Update session context with generation outcomes
   - Suggest next steps for validation or optimization

## Usage

```bash
/weavergen:multi-generate registry_url python,rust,go,java output_dir
```

## Arguments

$ARGUMENTS

- `registry_url` (string): URL or path to semantic convention registry
- `languages` (string): Comma-separated list of target languages
- `output_dir` (string, optional): Base output directory (defaults to ./generated)
- `--force` (flag, optional): Overwrite existing generated files
- `--validate` (flag, optional): Run validation after generation
- `--benchmark` (flag, optional): Include performance benchmarking

## Example

```bash
/weavergen:multi-generate https://github.com/open-telemetry/semantic-conventions.git python,rust,go ./sdk-outputs --validate
```

## Expected Output

Multi-language generation results with:
- Generated file counts and locations per language
- Performance metrics (generation time, throughput)
- Quality validation results
- Session context updates
- Recommended next actions for each language target