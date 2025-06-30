# WeaverGen Comprehensive Validation

Perform comprehensive validation of semantic conventions and generated code with OTel compliance checking and quality assurance.

## Instructions

1. **Registry Validation**
   - Parse and validate semantic convention registry structure
   - Check compliance with OpenTelemetry semantic convention standards
   - Verify attribute definitions, stability levels, and documentation
   - Identify potential conflicts or inconsistencies

2. **Generated Code Validation**
   - Validate generated code syntax and compilation across target languages
   - Check type safety and API consistency
   - Verify documentation generation and completeness
   - Test integration points and backwards compatibility

3. **Performance Assessment**
   - Benchmark generation performance against baselines
   - Measure code quality metrics (complexity, maintainability)
   - Assess memory usage and runtime performance of generated SDKs
   - Validate observability instrumentation effectiveness

4. **Compliance Reporting**
   - Generate comprehensive validation report
   - Highlight compliance violations and quality issues
   - Provide actionable recommendations for improvements
   - Update session context with validation results

## Usage

```bash
/weavergen:validate $ARGUMENTS
```

## Arguments

- `target` (string): What to validate - 'registry', 'generated', 'all'
- `path` (string): Path to registry file or generated code directory
- `--strict` (flag, optional): Enable strict validation mode with enhanced checks
- `--languages` (string, optional): Comma-separated list of languages to validate
- `--output-format` (string, optional): Report format - 'console', 'json', 'html'
- `--fix` (flag, optional): Attempt to auto-fix minor validation issues

## Example

```bash
/weavergen:validate all ./generated --strict --languages python,rust --output-format html
```

## Expected Output

Comprehensive validation report including:
- Registry compliance assessment with detailed findings
- Generated code quality metrics per language
- Performance benchmark results
- Auto-fix summary (if enabled)
- Prioritized list of issues and recommendations
- Session context update with validation status