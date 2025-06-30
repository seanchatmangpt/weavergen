# Weaver Forge Prototype Scope

## Mission: Prove the Semantic Quine in 2 Weeks

Build a **minimal viable semantic system** that generates itself and completes one critical job with measurable quality.

## The Critical 20% for Prototype

### Single Job Focus (JTBD)
```yaml
job:
  actor: "Developer"
  context: "Needs to generate telemetry code from semantics"
  hire_criteria: "When I define what I want semantically, generate observable code automatically"
  success_metric: "Working code in < 60 seconds with zero manual editing"
```

### Three Core Operations (80/20)
```yaml
critical_operations:  # The absolute minimum to prove the concept
  1_generate_semantic:
    importance: 40%  # Most critical
    complexity: "High"
    
  2_validate_semantic:
    importance: 35%  # Quality gate
    complexity: "Low"
    
  3_generate_code:
    importance: 25%  # Output
    complexity: "Medium"
    
  total: 100% of prototype value
```

### Minimum Viable Semantics
```yaml
# weaver_forge_mvp.yaml
groups:
  - id: forge.generate
    type: span
    brief: 'Generate semantic convention from description'
    attributes:
      - id: forge.input.description
        type: string
        requirement_level: required
      - id: forge.output.path  
        type: string
        requirement_level: required
      - id: forge.success
        type: boolean
        requirement_level: required
```

## Prototype Success Criteria (Six Sigma)

### Critical Path Metrics
| Operation | CTQ Metric | Target | Measurement |
|-----------|------------|--------|-------------|
| Generate Semantic | Success Rate | >90% | Count success/total |
| Validate Semantic | Valid Output | 100% | Pass Weaver check |
| Generate Code | Runs Without Error | 100% | Python imports work |

### Minimum Process Capability
- **Cpk Target**: 1.0 (prototype level, not production 1.33)
- **Defect Tolerance**: 10% for prototype
- **Measurement**: Built-in from day 1

## Technical Scope

### Week 1: Core Pipeline
```python
# Day 1-2: Basic semantic generation
class MinimalGenerator:
    def generate(self, description: str) -> str:
        # Hardcoded template with LLM fill-in
        # Proves concept without complexity
        
# Day 3-4: Weaver integration
def validate_and_generate(semantic_yaml: str):
    # Call Weaver CLI
    # Generate Python code
    # Return success/failure
    
# Day 5: Telemetry
def track_operation(op_name: str, success: bool, duration: float):
    # Simple metrics to CSV
    # Proves observability concept
```

### Week 2: Self-Reference Loop
```python
# Day 6-7: Generate Forge semantics
forge_semantics = generate("semantic generator with validation")

# Day 8-9: Generate Forge from itself
forge_code = generate_from_semantics(forge_semantics)

# Day 10: Prove the loop works
new_forge = use_generated_forge_to_generate_itself()
```

## What's IN Scope ✓

### Must Have (Critical 20%)
1. **Generate valid semantic YAML from text description**
   - Use Ollama with hardcoded prompts
   - Support single operation type (span)
   - Output passes Weaver validation

2. **Generate Python code from semantics**
   - Commands/operations/runtime pattern
   - Minimal templates (no complexity)
   - Generated code can be imported

3. **Self-generation proof**
   - Forge generates its own semantics
   - Uses those to generate itself
   - Second generation works

4. **Basic telemetry**
   - Every operation logs: success, duration, timestamp
   - Simple CSV output (no OpenTelemetry yet)
   - Can calculate success rate

### Should Have (If Time)
- Basic error handling
- Simple CLI interface
- README with usage

## What's OUT of Scope ✗

### Save for Evolution
- ❌ Multiple LLM providers (just Ollama)
- ❌ Complex semantic types (just span)
- ❌ Full OpenTelemetry integration
- ❌ Async operations
- ❌ Contract validation (icontract)
- ❌ Web UI
- ❌ Multiple programming languages
- ❌ Caching/optimization
- ❌ Advanced templates

### Never in Prototype
- ❌ Edge cases
- ❌ Perfect error messages
- ❌ Configuration files
- ❌ Authentication
- ❌ Deployment tools

## Deliverables Checklist

### Day 14 Demo Must Show:

1. **Live Generation** (2 min)
   ```bash
   $ python forge_mvp.py "cache get operation"
   ✓ Generated: cache_get.yaml
   ✓ Validated: Pass
   ✓ Generated: cache_get.py
   ```

2. **Self-Reference** (3 min)
   ```bash
   $ python forge_mvp.py "semantic generator"
   ✓ Generated: forge.yaml
   $ python forge_mvp.py --from-semantic forge.yaml
   ✓ Generated: forge v2
   $ python forge_v2.py "another operation"
   ✓ Works! Forge generated itself
   ```

3. **Metrics Proof** (2 min)
   ```bash
   $ cat telemetry.csv
   generate_semantic,success,0.45s
   validate_semantic,success,0.12s
   generate_code,success,0.23s
   
   Success Rate: 100% (3/3)
   Avg Duration: 0.27s
   ```

## Risk Mitigation

### High Risk → Mitigation
1. **LLM unreliable** → Hardcoded templates with small LLM parts
2. **Weaver complexity** → Use simplest possible semantics
3. **Self-reference fails** → Manual verification step allowed

### Acceptable Prototype Compromises
- Hardcoded paths OK
- Single file output OK  
- No error recovery OK
- Manual Ollama start OK

## Success Metrics

### Quantitative (Measurable)
- [ ] 3 operations work end-to-end
- [ ] Self-generation succeeds 1 time
- [ ] Success rate > 90%
- [ ] Generation time < 60 seconds

### Qualitative (Demonstrable)
- [ ] "Wow" moment when Forge generates itself
- [ ] Clear path to production visible
- [ ] Stakeholders understand the value
- [ ] Team excited to continue

## Daily Standup Focus

```yaml
day_1: "Can we generate any YAML from text?"
day_2: "Does Weaver validate our YAML?"
day_3: "Can we call Weaver's generator?"
day_4: "Does generated code import?"
day_5: "Can we measure success rate?"
day_6: "Can we generate Forge's semantics?"
day_7: "Can Forge generate itself?"
day_8: "Does self-generated Forge work?"
day_9: "Can we demo the full loop?"
day_10: "Polish demo, document results"
```

## The One Thing That Matters

**If we can only prove one thing:**

> A system that generates valid, observable code from semantic definitions, 
> and can generate itself, proving the semantic quine concept works.

Everything else is evolution.

## Post-Prototype Evolution Path

Week 3+:
1. Add contracts (icontract)
2. Real OpenTelemetry integration
3. Multiple LLM support
4. Async operations
5. More semantic types

But NOT in the prototype. **Ship the prototype when the loop works once.**

---

**Remember: This prototype proves the concept, not production readiness. One working self-generation is worth a thousand features.**