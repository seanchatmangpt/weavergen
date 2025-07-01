# Definition of Done: BPMN-Driven Weaver Forge with UltraThink Validation

## Core Principle
**ALL claims of completion MUST be validated by OpenTelemetry spans. No exceptions.**

## Telemetry Requirements ✅

Every span MUST include:

### 1. Code Attribution
```json
{
  "code.filepath": "/absolute/path/to/file.py",
  "code.lineno": 142,
  "code.function": "execute_task",
  "code.module": "weavergen.bpmn_engine"
}
```

### 2. BPMN Attribution
```json
{
  "bpmn.workflow.file": "workflows/bpmn/weaver_forge_orchestration.bpmn",
  "bpmn.workflow.id": "WeaverForgeOrchestration",
  "bpmn.process.name": "Weaver Forge BPMN Orchestration",
  "bpmn.task.id": "Task_InitWeaver",
  "bpmn.task.name": "Initialize Weaver Binary",
  "bpmn.task.type": "serviceTask"
}
```

### 3. Execution Context
```json
{
  "execution.timestamp": "2024-07-01T10:30:45.123Z",
  "execution.success": true,
  "execution.duration_ms": 45.3,
  "execution.host": "hostname",
  "execution.user": "username"
}
```

### 4. Weaver-Specific (when applicable)
```json
{
  "weaver.command": "registry generate",
  "weaver.target": "python",
  "weaver.template": "metrics.j2",
  "weaver.output.file": "generated/metrics.py",
  "weaver.output.size_bytes": 1234
}
```

## Validation Criteria 🎯

### Level 1: Basic Execution (Minimum Viable)
- [ ] Span exists with correct name
- [ ] Span has valid trace_id and span_id
- [ ] Span has start_time and end_time
- [ ] Duration is positive and reasonable (< 30s)
- [ ] Parent-child relationships are valid

### Level 2: Full Attribution (Required)
- [ ] Code filepath exists and is absolute
- [ ] Line number is > 0
- [ ] Function name matches actual function
- [ ] BPMN workflow file exists
- [ ] BPMN task ID matches BPMN definition
- [ ] Execution timestamp is ISO 8601 format

### Level 3: Semantic Compliance (Production)
- [ ] All required attributes per span type
- [ ] Consistent naming conventions
- [ ] Error spans include exception details
- [ ] Resource attributes identify service
- [ ] Links between related spans

## Validation Rules 📏

### Rule 1: No Span, No Claim
If you claim something executed but there's no span, it's a **LIE**.

### Rule 2: File Must Exist
If `code.filepath` doesn't exist on disk, it's a **LIE**.

### Rule 3: BPMN Must Match
If `bpmn.task.id` doesn't exist in the referenced BPMN file, it's a **LIE**.

### Rule 4: Success Must Be Proven
If you claim success but `execution.success != true`, it's a **LIE**.

### Rule 5: Performance Must Be Measured
If you claim "fast" but no duration_ms is recorded, it's a **LIE**.

## Implementation Checklist 📋

### 1. Span Decorator
```python
@ultra_span("task.name", bpmn_file="workflow.bpmn", task_id="Task_123")
def execute_task():
    # Automatically captures all required attributes
    pass
```

### 2. BPMN Parser Integration
```python
class BPMNSpanEnricher:
    def enrich_span(self, span, bpmn_file, task_id):
        bpmn_data = self.parse_bpmn(bpmn_file)
        task = bpmn_data.find_task(task_id)
        
        span.set_attribute("bpmn.workflow.file", bpmn_file)
        span.set_attribute("bpmn.workflow.id", bpmn_data.process_id)
        span.set_attribute("bpmn.task.id", task_id)
        span.set_attribute("bpmn.task.name", task.name)
        span.set_attribute("bpmn.task.type", task.type)
```

### 3. Validation Pipeline
```python
class UltraThinkPipeline:
    def validate_done(self, spans: List[Span]) -> ValidationResult:
        for span in spans:
            # Level 1: Basic checks
            assert span.name, "Span must have name"
            assert span.trace_id, "Span must have trace_id"
            
            # Level 2: Attribution checks
            attrs = span.attributes
            assert os.path.exists(attrs["code.filepath"]), "File must exist"
            assert self.bpmn_exists(attrs["bpmn.workflow.file"]), "BPMN must exist"
            
            # Level 3: Semantic checks
            assert attrs["execution.timestamp"], "Must have timestamp"
            assert isinstance(attrs["execution.success"], bool), "Success must be boolean"
```

## Testing Definition of Done 🧪

### Test 1: Happy Path
1. Execute BPMN workflow
2. Capture all spans
3. Validate 100% have required attributes
4. Verify file paths exist
5. Confirm BPMN task IDs match

### Test 2: Failure Detection
1. Create span with fake file path
2. Validation must flag as LIE
3. Create span with non-existent BPMN task
4. Validation must flag as LIE

### Test 3: Performance Validation
1. Claim operation is "fast" (< 100ms)
2. Span must have duration_ms
3. If duration_ms > 100, flag as LIE

## Automated Enforcement 🤖

### CI/CD Integration
```yaml
- name: Validate Definition of Done
  run: |
    # Generate spans from test execution
    weavergen bpmn execute TestWorkflow --capture-spans
    
    # Validate all spans meet criteria
    weavergen ultrathink validate --spans captured_spans.json
    
    # Fail if trust score < 95%
    if [ $TRUST_SCORE -lt 95 ]; then
      echo "FAILED: Trust score $TRUST_SCORE% < 95%"
      exit 1
    fi
```

## Success Metrics 📊

### Minimum Acceptable
- Trust Score ≥ 80%
- All Level 1 criteria met
- No missing file attributions

### Target
- Trust Score ≥ 95%
- All Level 1 & 2 criteria met
- < 5% unverifiable claims

### Excellence
- Trust Score = 100%
- All Level 1, 2 & 3 criteria met
- Zero unverifiable claims
- Full BPMN traceability

## Summary

**Definition of Done = Telemetry Proves It**

No telemetry → No trust → Not done.

Every claim must be backed by a span that includes:
- The exact file and line that executed
- The BPMN workflow and task that triggered it
- Success/failure status with timing
- All semantic attributes for the operation type

This is not negotiable. This is how we build systems we can trust.