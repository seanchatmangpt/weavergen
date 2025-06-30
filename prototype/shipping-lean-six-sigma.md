# Shipping Decision Matrix: Lean Six Sigma Approach

## The Fundamental Equation

```
Ship = (Critical Path Cpk > 1.33) ∧ (JTBD Completion ≥ 80%) ∧ (Evolution ROI < Cost of Delay)
```

## DMAIC-Based Shipping Decision

### Define: What Does "Shippable" Mean?

**Traditional Definition**: All features complete, all tests pass

**Lean Semantic Definition**: Critical jobs achievable with statistical confidence

```python
shippable = {
    "jobs_completed": sum(job.is_achievable for job in critical_jobs) / len(critical_jobs) >= 0.8,
    "process_capability": all(op.cpk > 1.33 for op in critical_path_operations),
    "customer_pull": paying_customer_waiting or competitive_pressure_exists
}
```

### Measure: Statistical Shipping Criteria

| Metric | Red (Don't Ship) | Yellow (Consider) | Green (Ship) |
|--------|------------------|-------------------|--------------|
| Critical Path Coverage | < 95% | 95-99% | 100% |
| JTBD Completion | < 60% | 60-79% | ≥ 80% |
| Defect Rate (DPMO) | > 50,000 | 10,000-50,000 | < 10,000 |
| Process Capability (Cpk) | < 1.0 | 1.0-1.32 | > 1.33 |
| Telemetry Coverage | < 80% | 80-95% | > 95% |
| Evolution Success Rate | < 50% | 50-80% | > 80% |

### Analyze: Pareto-Optimized Shipping

```python
def analyze_shipping_readiness():
    # 80/20 Analysis
    critical_operations = identify_top_20_percent_by_usage()
    critical_jobs = identify_top_20_percent_by_value()
    
    # These MUST be ready
    blockers = []
    
    for op in critical_operations:
        if op.cpk < 1.33:
            blockers.append(f"{op.name}: Cpk={op.cpk}")
    
    for job in critical_jobs:
        if job.completion < 1.0:
            blockers.append(f"{job.name}: {job.completion*100}% complete")
    
    return {
        "ship": len(blockers) == 0,
        "blockers": blockers
    }
```

### Improve: Minimum Viable Semantic Product (MVSP)

```yaml
# The MVSP Formula
mvsp:
  includes:
    - 100% of critical path operations
    - 80% of customer job outcomes
    - Six Sigma quality on revenue path
    - Telemetry for all critical operations
    - Evolution capability (not active)
  
  excludes:
    - Edge cases (< 5% usage)
    - Nice-to-have features
    - Optimizations without data
    - Speculative semantics
```

### Control: Statistical Process Control for Shipping

```python
class ShippingControlChart:
    def __init__(self):
        self.ucl = 0.01  # 1% defect rate upper control limit
        self.lcl = 0.0   # 0% defect rate lower control limit
        self.target = 0.001  # 0.1% target
    
    def should_ship(self, telemetry_data):
        defect_rate = calculate_defect_rate(telemetry_data)
        
        if defect_rate > self.ucl:
            return "NO: Process out of control"
        elif defect_rate > self.target * 2:
            return "MAYBE: Monitor closely"
        else:
            return "YES: Process in control"
```

## The JTBD Shipping Checklist

### Critical Jobs Assessment

```yaml
job_1_authentication:
  importance: 10/10
  completion: 100%
  status: ✓ READY

job_2_data_caching:
  importance: 9/10
  completion: 100%
  status: ✓ READY

job_3_payment_processing:
  importance: 8/10
  completion: 90%
  status: ✓ READY (>80% threshold)

job_4_advanced_analytics:
  importance: 4/10
  completion: 20%
  status: ⊘ NOT BLOCKING (not critical)

overall: 3/3 critical jobs ready = SHIP
```

## The Cost of Delay Analysis

```python
def calculate_shipping_decision():
    # Cost of shipping now
    cost_of_shipping = {
        "incomplete_features": estimate_support_cost(missing_20_percent),
        "potential_defects": estimate_defect_cost(current_dpmo),
        "evolution_debt": 0  # Can evolve later
    }
    
    # Cost of delaying
    cost_of_delay = {
        "lost_revenue": days_delayed * daily_revenue_opportunity,
        "competitive_loss": competitor_advantage_per_day * days_delayed,
        "team_morale": team_momentum_loss * days_delayed
    }
    
    return "SHIP" if cost_of_delay > cost_of_shipping else "WAIT"
```

## Six Sigma Shipping Gates

### Gate 1: Tollgate Review (Define/Measure)
- [ ] Critical jobs identified via JTBD analysis
- [ ] 80/20 analysis complete
- [ ] CTQs defined for each critical operation
- [ ] Measurement system in place

**Gate Decision**: Proceed if core semantics defined

### Gate 2: Process Capability (Analyze)
- [ ] Cpk calculated for critical operations
- [ ] Defect Pareto completed
- [ ] Root cause analysis on top defects
- [ ] Statistical control achieved

**Gate Decision**: Proceed if Cpk > 1.0

### Gate 3: Solution Validation (Improve)
- [ ] Critical path operations tested
- [ ] JTBD completion verified
- [ ] Evolution mechanism tested
- [ ] Rollback plan confirmed

**Gate Decision**: Proceed if 80% jobs complete

### Gate 4: Control Plan (Control)
- [ ] Monitoring in place
- [ ] Control limits set
- [ ] Evolution triggers defined
- [ ] Response plan documented

**Gate Decision**: SHIP if all controls active

## The Lean Waste Prevention Check

### Before Shipping, Eliminate:

1. **Defects**: Contracts prevent them
2. **Overproduction**: No unused semantics
3. **Waiting**: No blocking operations
4. **Transportation**: Direct semantic paths
5. **Inventory**: No generated dead code
6. **Motion**: No manual steps required
7. **Over-processing**: No gold-plating

```python
waste_check = {
    "unused_semantics": count_unused_operations() == 0,
    "manual_steps": count_manual_processes() == 0,
    "redundant_operations": count_duplicates() == 0
}

ship_if_lean = all(waste_check.values())
```

## The One-Page Shipping Dashboard

```
┌─────────────────────────────────────────────┐
│          SHIPPING DECISION DASHBOARD         │
├─────────────────────────────────────────────┤
│ Critical Path Coverage:    [████████] 100%  │
│ JTBD Completion:          [██████░░]  82%  │
│ Process Capability:        Cpk = 1.41 ✓     │
│ Defect Rate:              847 DPMO ✓       │
│ Evolution Tested:          YES ✓            │
├─────────────────────────────────────────────┤
│ Cost of Delay:            $45K/day         │
│ Cost of Shipping Now:     $12K one-time    │
│ ROI of Shipping:          275% ✓           │
├─────────────────────────────────────────────┤
│ DECISION: ████ SHIP NOW ████               │
└─────────────────────────────────────────────┘
```

## The Final Formula

```python
def should_ship_now():
    pareto_ready = critical_20_percent_coverage == 1.0
    jobs_ready = jtbd_completion >= 0.8
    quality_ready = critical_path_cpk > 1.33
    economics_ready = cost_of_delay > cost_of_shipping
    
    return all([pareto_ready, jobs_ready, quality_ready, economics_ready])
```

## Remember

**You're not shipping perfection. You're shipping statistical confidence in job completion.**

The goal is to ship when:
1. The **vital few** operations work with **Six Sigma quality**
2. **80% of customer jobs** can be completed
3. **Evolution capability** exists for the rest
4. **Cost of delay** exceeds cost of incompleteness

This is Lean Semantic Shipping: Maximum customer value with minimum waste.

---

*"Ship when the critical path is in statistical control and customer jobs are achievable. Evolution handles everything else."*