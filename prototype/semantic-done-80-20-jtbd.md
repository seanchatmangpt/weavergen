# Definition of Done: 80/20 JTBD Six Sigma Framework

## Core Principle: Pareto-Optimized Job Completion with Statistical Confidence

A semantic-driven application is **DONE** when it completes the critical 20% of semantics that deliver 80% of the Job-to-be-Done with Six Sigma confidence levels.

## The 80/20 Semantic Coverage Model

### Critical 20% Identification (DMAIC Define Phase)
**Use JTBD analysis to find the vital few semantics**

```yaml
# JTBD Analysis → Critical Semantics
Job: "Cache frequently accessed data"
Critical 20% Operations:
  - cache.get (60% of value)
  - cache.set (20% of value)
  = 80% of job done

Trivial 80% Operations:
  - cache.warm, cache.expire, cache.analyze...
  = 20% of value (implement through evolution)
```

### Measurement Criteria (DMAIC Measure Phase)
**Statistical confidence in the vital few**

| Metric | Six Sigma Target | 80/20 Reality |
|--------|-----------------|---------------|
| Semantic Coverage | 100% of operations | 20% critical operations |
| Defect Rate | 3.4 DPMO | <1% on critical path |
| Process Capability | Cp > 2.0 | Cpk > 1.33 for core |
| Customer Satisfaction | 100% | 80% job completion |

## JTBD-Driven Completion Criteria

### 1. Job Definition Clarity ✓
**The semantic model maps directly to customer jobs**

```python
# JTBD Mapping
customer_job = {
    "job": "Authenticate users securely",
    "context": "When accessing protected resources",
    "outcome": "Authorized access granted"
}

semantic_mapping = {
    "auth.validate": "Checks credentials",
    "auth.authorize": "Grants access",
    "auth.session": "Maintains state"
}

# DONE when: semantic_ops ⊇ job_critical_path
```

### 2. Pareto-Optimized Generation ✓
**Generate the 20% that matters first**

```python
def is_ready_to_ship():
    critical_ops = identify_critical_20_percent()
    coverage = semantic_coverage(critical_ops)
    
    # Ship at 100% of the critical 20%
    # NOT 20% of everything
    return coverage == 1.0
```

### 3. Statistical Process Control ✓
**Six Sigma confidence in core operations**

```python
# Control limits for critical operations
def calculate_process_capability():
    for operation in critical_20_percent:
        performance = measure_operation(operation)
        
        # Six Sigma: 3.4 defects per million
        # 80/20 Reality: 1% defect rate acceptable
        dpmo = performance.defects_per_million
        
        if dpmo > 10_000:  # 1% threshold
            return False
    
    return True
```

### 4. Job Outcome Verification ✓
**Measure job completion, not feature coverage**

```yaml
# Traditional: Feature checklist
features_implemented: 45/200  # 22.5%

# JTBD + 80/20: Job completion
jobs_completed: 4/5  # 80%
- ✓ Authenticate users
- ✓ Cache data
- ✓ Process payments  
- ✓ Send notifications
- ⧗ Advanced analytics (not critical)
```

### 5. Lean Evolution Readiness ✓
**Waste elimination through targeted improvement**

```python
# Lean principle: Only evolve based on pull (demand)
evolution_triggers = {
    "customer_pull": telemetry.unmet_jobs > threshold,
    "quality_pull": defect_rate > control_limit,
    "efficiency_pull": waste_ratio > target
}

# NOT: "because we can improve it"
```

## Design for Lean Six Sigma (DFLSS) Integration

### 1. Define Phase: JTBD Semantics
```yaml
# Map jobs to semantic groups
jobs:
  - id: user_authentication
    ctq: ["speed < 200ms", "success > 99.9%"]
    semantics: ["auth.validate", "auth.session"]
```

### 2. Measure Phase: Telemetry Baselines
```python
# Built-in measurement for every operation
@measure_performance
@track_defects  
@monitor_variation
def operation():
    # Automatic Six Sigma metrics
```

### 3. Analyze Phase: Pareto Analysis
```python
# Find the vital few defects
defect_pareto = analyze_telemetry()
# 80% of errors from 20% of operations
critical_improvements = defect_pareto.top_20_percent
```

### 4. Improve Phase: Targeted Evolution
```python
# Only evolve the critical 20%
if operation in critical_20_percent:
    if defect_rate > threshold:
        evolve_operation(operation)
```

### 5. Control Phase: Statistical Limits
```yaml
# Control limits for shipping
control_limits:
  critical_path_coverage: 
    LSL: 0.95  # 95% minimum
    Target: 1.0
    USL: 1.0
  
  defect_rate:
    LSL: 0
    Target: 0.001  # 0.1%
    USL: 0.01     # 1% max
  
  job_completion:
    LSL: 0.75  # 75% minimum
    Target: 0.80
    USL: 1.0
```

## The 80/20 Stop Conditions

### Ship When:

1. **Critical 20% Complete**
   ```
   Coverage(Critical Operations) = 100%
   Coverage(All Operations) ≥ 20%
   ```

2. **JTBD Satisfaction > 80%**
   ```
   Σ(Completed Jobs) / Σ(All Jobs) ≥ 0.8
   ```

3. **Six Sigma Confidence**
   ```
   P(Defect | Critical Path) < 0.001
   Cpk(Critical Operations) > 1.33
   ```

4. **Lean Waste Below Threshold**
   ```
   Value-Added Time / Total Time > 0.5
   Evolution ROI > Cost of Delay
   ```

## Anti-Patterns (Violating 80/20 JTBD Principles)

### ❌ Feature Parity Fallacy
"We need all 200 features from the old system"

**✓ JTBD Reality**: Users hire you for 5 jobs, not 200 features

### ❌ Six Sigma Everywhere
"Every operation needs 6σ quality"

**✓ 80/20 Reality**: Critical path needs 6σ, everything else needs "good enough"

### ❌ Semantic Completionism
"Model every possible attribute"

**✓ Pareto Reality**: Model the 20% of attributes used 80% of the time

## The Formula for Done

```
DONE = (Critical Coverage = 100%) ∧ 
       (Job Completion ≥ 80%) ∧ 
       (DPMO < 10,000) ∧
       (Evolution Capability = True)
```

## Remember

**You're not shipping 100% of possible features.**
**You're shipping 100% of the 20% that does 80% of the job.**

This is not compromise—it's optimization based on statistical reality and customer value.