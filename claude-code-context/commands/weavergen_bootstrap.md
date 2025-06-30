# WeaverGen Session Bootstrap

Initialize new OTel code generation session with intelligent project discovery and context setup.

## Instructions

1. **Project Discovery**
   - Scan current directory for existing semantic convention files
   - Detect previous generation outputs and target languages
   - Identify OTel Weaver binary installation and configuration
   - Discover relevant templates and customizations

2. **Session Initialization**
   - Create new CCCS generation session with unique identifier
   - Configure target languages based on project context or user preferences
   - Setup output directory structure following best practices
   - Initialize performance tracking and validation settings

3. **Context Setup**
   - Load semantic convention registries from local files or URLs
   - Configure generation templates and language-specific settings
   - Setup automation loops for continuous validation and optimization
   - Initialize predictive context loading for enhanced productivity

4. **Readiness Verification**
   - Validate OTel Weaver binary availability and version compatibility
   - Test generation pipeline with small sample to ensure functionality
   - Verify output directory permissions and storage availability
   - Confirm session state persistence and recovery mechanisms

## Usage

```bash
/weavergen:bootstrap $ARGUMENTS
```

## Arguments

- `registry_url` (string, optional): Initial semantic convention registry to load
- `--languages` (string, optional): Comma-separated target languages (defaults to auto-detection)
- `--output-dir` (string, optional): Base output directory (defaults to ./generated)
- `--template-dir` (string, optional): Custom template directory path
- `--force-new` (flag, optional): Force creation of new session even if active session exists
- `--auto-configure` (flag, optional): Automatically configure based on project discovery

## Example

```bash
/weavergen:bootstrap https://github.com/open-telemetry/semantic-conventions.git --languages python,rust,go --auto-configure
```

## Expected Output

Session bootstrap results including:
- New session ID and configuration summary
- Discovered project context and automatically configured settings
- Target language setup and output directory structure
- OTel Weaver binary validation and readiness status
- Initial generation readiness test results
- Session state saved to CCCS for guaranteed continuity
- Recommended next steps for starting generation workflows