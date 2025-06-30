# Forge Prototype - Semantic Quine Proof of Concept

This is a minimal prototype that proves the semantic quine concept - a system that can generate itself from its own semantic definition.

## Quick Start

```bash
# Run the self-generation test (proves the concept)
python3 forge_mvp.py --self-test

# Or run the full test suite
./test_prototype.sh
```

## What This Proves

1. **Semantic Generation**: Can generate valid semantic conventions from descriptions
2. **Code Generation**: Can generate working Python code from semantics
3. **Self-Reference**: Can generate its own semantic definition and then generate itself
4. **Observability**: Built-in telemetry tracking from day one

## Core Operations (The Critical 20%)

1. `generate_semantic` - Creates YAML semantic conventions
2. `validate_semantic` - Validates with Weaver (optional)
3. `generate_code` - Generates Python code from semantics

## Usage Examples

```bash
# Generate a semantic convention
python3 forge_mvp.py "cache get operation"

# Generate with custom output
python3 forge_mvp.py "user authentication" --output auth.yaml

# Show metrics
python3 forge_mvp.py --metrics

# THE BIG TEST - Self-generation
python3 forge_mvp.py --self-test
```

## How Self-Generation Works

1. Forge generates a semantic definition of itself
2. It validates this semantic (if Weaver is available)
3. It generates code from its own semantic definition
4. It tests that the generated code works
5. If successful, the semantic quine is proven!

## Prototype Limitations

This is a PROTOTYPE focused on proving the concept:

- Uses hardcoded templates (no LLM integration yet)
- Simple semantic structure (only span type)
- Basic code generation (minimal template)
- No async operations
- No contract validation

These are all intentional to keep focus on the core concept.

## Success Criteria Met ✓

- [x] Generate semantic YAML from text description
- [x] Generate Python code from semantics
- [x] Self-generation works
- [x] Basic telemetry/metrics
- [x] <60 second generation time

## Next Steps (Evolution)

After proving the concept, these can be added:

1. LLM integration (Ollama/OpenAI)
2. Full Weaver template system
3. Contract validation (icontract)
4. OpenTelemetry integration
5. Async operations

But NOT in the prototype. The prototype ships when the loop works once.

## The Key Insight

> "A system that can generate valid, observable code from semantic definitions,
> and can generate itself, proves that semantic-driven development is viable."

This prototype demonstrates that telemetry and application code can be unified
from the same semantic source - they're only separate due to human cognitive
limitations, not architectural necessity.
