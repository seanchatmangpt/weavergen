#!/usr/bin/env python3
"""
Span-Based Validation System - Beyond Unit Tests
=================================================

Validates system behavior through OpenTelemetry spans, capturing
runtime reality that unit tests cannot:

- Semantic convention compliance
- Cross-system interactions  
- Temporal dependencies
- Resource lifecycles
- AI model behavior
- Generation fidelity
- Conversation quality
- Architecture boundary violations

Spans > Unit Tests for distributed system validation.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from opentelemetry.trace import Span
from opentelemetry.sdk.trace.export import SpanExporter
import hashlib


@dataclass
class ValidationResult:
    """Result of span-based validation"""
    valid: bool
    score: float = 0.0
    issues: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    span_evidence: List[str] = field(default_factory=list)


@dataclass
class QuineValidationResult:
    """Semantic quine property validation"""
    is_valid_quine: bool
    input_hash: str
    regenerated_hash: str
    cycles_tested: int
    convergence_proof: bool
    span_ids: List[str] = field(default_factory=list)


@dataclass
class ConversationQualityResult:
    """Conversation quality analysis from spans"""
    converged: bool
    consensus_trajectory: List[float]
    decision_quality_trajectory: List[float]
    participant_balance: float
    emergence_detected: bool
    quality_issues: List[str] = field(default_factory=list)


@dataclass
class ArchitectureBoundaryViolation:
    """4-layer architecture boundary violation"""
    from_layer: str
    to_layer: str
    span_id: str
    timestamp: datetime
    operation: str
    severity: str  # "warning", "error", "critical"


@dataclass
class ResourceLeakReport:
    """Resource lifecycle tracking report"""
    leaks_detected: int
    total_resources_tracked: int
    memory_growth_rate: float
    leaked_resources: List[Dict[str, Any]] = field(default_factory=list)
    lifecycle_violations: List[str] = field(default_factory=list)


class SpanBasedValidator:
    """
    Comprehensive validation using OpenTelemetry spans.
    
    Goes beyond unit tests to validate actual runtime behavior:
    - Real AI interactions (not mocked)
    - Cross-system dependencies
    - Temporal causality
    - Resource usage patterns
    - Emergent behaviors
    """
    
    def __init__(self, semantic_conventions: Optional[Dict[str, Any]] = None):
        self.semantic_conventions = semantic_conventions or {}
        self.validation_cache = {}
        
    def validate_semantic_quine_property(self, spans: List[Dict[str, Any]]) -> QuineValidationResult:
        """
        Validate that the system can actually regenerate itself.
        
        Unit tests can't test this - requires real Weaver execution.
        """
        generation_spans = [s for s in spans if s.get("name", "").startswith("forge.self")]
        
        if not generation_spans:
            return QuineValidationResult(
                is_valid_quine=False,
                input_hash="",
                regenerated_hash="",
                cycles_tested=0,
                convergence_proof=False
            )
        
        # Track regeneration cycles
        cycles = {}
        for span in generation_spans:
            attrs = span.get("attributes", {})
            cycle_id = attrs.get("regeneration.cycle.id")
            input_hash = attrs.get("semantic.input.hash")
            output_hash = attrs.get("semantic.output.hash")
            
            if cycle_id and input_hash and output_hash:
                cycles[cycle_id] = {
                    "input_hash": input_hash,
                    "output_hash": output_hash,
                    "span_id": span.get("context", {}).get("span_id")
                }
        
        # Validate quine property: input == output after regeneration
        valid_cycles = 0
        for cycle_id, cycle_data in cycles.items():
            if cycle_data["input_hash"] == cycle_data["output_hash"]:
                valid_cycles += 1
        
        is_valid = valid_cycles > 0 and valid_cycles == len(cycles)
        
        return QuineValidationResult(
            is_valid_quine=is_valid,
            input_hash=cycles.get("1", {}).get("input_hash", ""),
            regenerated_hash=cycles.get("1", {}).get("output_hash", ""),
            cycles_tested=len(cycles),
            convergence_proof=valid_cycles == len(cycles),
            span_ids=[c.get("span_id", "") for c in cycles.values()]
        )
    
    def validate_ai_agent_consistency(self, spans: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate AI agents make consistent decisions under similar conditions.
        
        Unit tests mock AI - this validates real AI behavior.
        """
        agent_decisions = {}
        inconsistencies = []
        
        ai_decision_spans = [s for s in spans if "agent" in s.get("name", "") and "decision" in s.get("name", "")]
        
        for span in ai_decision_spans:
            attrs = span.get("attributes", {})
            agent_id = attrs.get("agent.id")
            decision_context_hash = attrs.get("decision.context.hash")
            decision_output = attrs.get("decision.output")
            
            if agent_id and decision_context_hash and decision_output:
                key = f"{agent_id}:{decision_context_hash}"
                
                if key in agent_decisions:
                    # Same agent, same context - should be consistent
                    if agent_decisions[key] != decision_output:
                        inconsistencies.append(
                            f"Agent {agent_id} gave different decisions for same context: "
                            f"{agent_decisions[key]} vs {decision_output}"
                        )
                else:
                    agent_decisions[key] = decision_output
        
        consistency_score = 1.0 - (len(inconsistencies) / max(len(agent_decisions), 1))
        
        return ValidationResult(
            valid=len(inconsistencies) == 0,
            score=consistency_score,
            issues=inconsistencies,
            details={
                "total_decisions": len(agent_decisions),
                "inconsistencies": len(inconsistencies),
                "agents_tested": len(set(k.split(":")[0] for k in agent_decisions.keys()))
            }
        )
    
    def validate_4_layer_architecture_boundaries(self, spans: List[Dict[str, Any]]) -> List[ArchitectureBoundaryViolation]:
        """
        Validate that 4-layer architecture boundaries aren't violated at runtime.
        
        Unit tests can't catch cross-layer violations in real execution.
        """
        violations = []
        
        # Valid call patterns for 4-layer architecture
        valid_calls = {
            "commands": ["operations"],
            "operations": ["runtime", "contracts"],
            "runtime": [],  # Runtime should be leaf nodes
            "contracts": []  # Contracts should be leaf nodes
        }
        
        # Build span hierarchy
        span_map = {}
        for span in spans:
            span_id = span.get("context", {}).get("span_id")
            if span_id:
                span_map[span_id] = span
        
        for span in spans:
            attrs = span.get("attributes", {})
            current_layer = attrs.get("forge.layer")
            parent_span_id = span.get("parent_id")
            
            if current_layer and parent_span_id and parent_span_id in span_map:
                parent_span = span_map[parent_span_id]
                parent_layer = parent_span.get("attributes", {}).get("forge.layer")
                
                if parent_layer and current_layer not in valid_calls.get(parent_layer, []):
                    violations.append(ArchitectureBoundaryViolation(
                        from_layer=parent_layer,
                        to_layer=current_layer,
                        span_id=span.get("context", {}).get("span_id", ""),
                        timestamp=datetime.fromisoformat(span.get("start_time", "")),
                        operation=span.get("name", ""),
                        severity="error" if parent_layer == "runtime" else "warning"
                    ))
        
        return violations
    
    def validate_conversation_convergence(self, spans: List[Dict[str, Any]]) -> ConversationQualityResult:
        """
        Validate that conversations actually converge to meaningful outcomes.
        
        Unit tests can't simulate emergent conversation dynamics.
        """
        conversation_spans = [s for s in spans if "conversation" in s.get("name", "")]
        
        if not conversation_spans:
            return ConversationQualityResult(
                converged=False,
                consensus_trajectory=[],
                decision_quality_trajectory=[],
                participant_balance=0.0,
                emergence_detected=False,
                quality_issues=["No conversation spans found"]
            )
        
        # Analyze conversation progression
        consensus_trajectory = []
        decision_quality_trajectory = []
        participant_contributions = {}
        
        for conv_span in conversation_spans:
            attrs = conv_span.get("attributes", {})
            
            # Extract conversation metrics from spans
            if "consensus.level" in attrs:
                consensus_trajectory.append(float(attrs["consensus.level"]))
            
            if "decision.quality" in attrs:
                decision_quality_trajectory.append(float(attrs["decision.quality"]))
            
            # Track participant balance
            participant_id = attrs.get("participant.id")
            if participant_id:
                participant_contributions[participant_id] = participant_contributions.get(participant_id, 0) + 1
        
        # Calculate convergence
        converged = False
        if consensus_trajectory:
            # Check if consensus increases over time
            if len(consensus_trajectory) > 1:
                final_consensus = consensus_trajectory[-1]
                initial_consensus = consensus_trajectory[0]
                converged = final_consensus > initial_consensus and final_consensus > 0.7
        
        # Calculate participant balance (should be roughly equal)
        participant_balance = 0.0
        if participant_contributions:
            values = list(participant_contributions.values())
            avg = sum(values) / len(values)
            variance = sum((v - avg) ** 2 for v in values) / len(values)
            participant_balance = 1.0 / (1.0 + variance)  # Higher balance = lower variance
        
        # Detect emergence (non-linear conversation development)
        emergence_detected = self._detect_conversation_emergence(consensus_trajectory)
        
        quality_issues = []
        if not converged:
            quality_issues.append("Conversation did not converge")
        if participant_balance < 0.5:
            quality_issues.append("Unbalanced participant contributions")
        
        return ConversationQualityResult(
            converged=converged,
            consensus_trajectory=consensus_trajectory,
            decision_quality_trajectory=decision_quality_trajectory,
            participant_balance=participant_balance,
            emergence_detected=emergence_detected,
            quality_issues=quality_issues
        )
    
    def validate_resource_lifecycle(self, spans: List[Dict[str, Any]]) -> ResourceLeakReport:
        """
        Validate resource creation/destruction patterns.
        
        Unit tests don't run long enough to detect resource leaks.
        """
        resource_operations = {}
        memory_usage_over_time = []
        
        for span in spans:
            attrs = span.get("attributes", {})
            
            # Track resource operations
            if "resource.id" in attrs:
                resource_id = attrs["resource.id"]
                operation = attrs.get("resource.operation", "unknown")
                
                if resource_id not in resource_operations:
                    resource_operations[resource_id] = []
                
                resource_operations[resource_id].append({
                    "operation": operation,
                    "timestamp": span.get("start_time"),
                    "span_id": span.get("context", {}).get("span_id")
                })
            
            # Track memory usage
            if "memory.usage.bytes" in attrs:
                memory_usage_over_time.append({
                    "timestamp": span.get("start_time"),
                    "memory_bytes": int(attrs["memory.usage.bytes"])
                })
        
        # Detect resource leaks
        leaked_resources = []
        lifecycle_violations = []
        
        for resource_id, operations in resource_operations.items():
            create_count = sum(1 for op in operations if op["operation"] == "create")
            destroy_count = sum(1 for op in operations if op["operation"] == "destroy")
            
            if create_count > destroy_count:
                leaked_resources.append({
                    "resource_id": resource_id,
                    "created": create_count,
                    "destroyed": destroy_count,
                    "leaked": create_count - destroy_count
                })
            
            # Check for invalid lifecycle patterns
            operation_sequence = [op["operation"] for op in sorted(operations, key=lambda x: x["timestamp"])]
            if not self._is_valid_lifecycle_sequence(operation_sequence):
                lifecycle_violations.append(f"Invalid lifecycle for {resource_id}: {operation_sequence}")
        
        # Calculate memory growth rate
        memory_growth_rate = 0.0
        if len(memory_usage_over_time) > 1:
            sorted_memory = sorted(memory_usage_over_time, key=lambda x: x["timestamp"])
            initial_memory = sorted_memory[0]["memory_bytes"]
            final_memory = sorted_memory[-1]["memory_bytes"]
            memory_growth_rate = (final_memory - initial_memory) / initial_memory if initial_memory > 0 else 0.0
        
        return ResourceLeakReport(
            leaks_detected=len(leaked_resources),
            total_resources_tracked=len(resource_operations),
            memory_growth_rate=memory_growth_rate,
            leaked_resources=leaked_resources,
            lifecycle_violations=lifecycle_violations
        )
    
    def validate_structured_output_compliance(self, spans: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate that AI agents actually produce compliant structured outputs.
        
        Unit tests use mocked AI - this validates real LLM behavior.
        """
        ai_output_spans = [s for s in spans if "pydantic_ai" in s.get("name", "") or "structured_output" in s.get("name", "")]
        
        compliance_issues = []
        total_outputs = 0
        compliant_outputs = 0
        
        for span in ai_output_spans:
            attrs = span.get("attributes", {})
            
            if "ai.output.validation_errors" in attrs:
                total_outputs += 1
                validation_errors = attrs["ai.output.validation_errors"]
                
                if validation_errors and validation_errors != "[]":
                    compliance_issues.append(
                        f"Validation errors in span {span.get('context', {}).get('span_id')}: {validation_errors}"
                    )
                else:
                    compliant_outputs += 1
        
        compliance_rate = compliant_outputs / total_outputs if total_outputs > 0 else 0.0
        
        return ValidationResult(
            valid=len(compliance_issues) == 0,
            score=compliance_rate,
            issues=compliance_issues,
            details={
                "total_ai_outputs": total_outputs,
                "compliant_outputs": compliant_outputs,
                "compliance_rate": compliance_rate
            }
        )
    
    def validate_generation_fidelity(self, spans: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate that generated code actually behaves according to semantic conventions.
        
        Unit tests can't validate against semantic convention intentions.
        """
        generation_spans = [s for s in spans if "weaver.generate" in s.get("name", "")]
        fidelity_issues = []
        
        for span in generation_spans:
            attrs = span.get("attributes", {})
            
            semantic_group = attrs.get("semantic.group.id")
            expected_behavior_hash = attrs.get("semantic.expected_behavior.hash")
            actual_behavior_hash = attrs.get("runtime.actual_behavior.hash")
            
            if expected_behavior_hash and actual_behavior_hash:
                if expected_behavior_hash != actual_behavior_hash:
                    fidelity_issues.append(
                        f"Behavior mismatch for {semantic_group}: "
                        f"expected {expected_behavior_hash}, got {actual_behavior_hash}"
                    )
        
        fidelity_score = 1.0 - (len(fidelity_issues) / max(len(generation_spans), 1))
        
        return ValidationResult(
            valid=len(fidelity_issues) == 0,
            score=fidelity_score,
            issues=fidelity_issues,
            details={"generation_spans_analyzed": len(generation_spans)}
        )
    
    def _detect_conversation_emergence(self, consensus_trajectory: List[float]) -> bool:
        """Detect non-linear emergence in conversation development"""
        if len(consensus_trajectory) < 3:
            return False
        
        # Look for sudden jumps or non-linear patterns
        for i in range(1, len(consensus_trajectory) - 1):
            current_change = consensus_trajectory[i] - consensus_trajectory[i-1]
            next_change = consensus_trajectory[i+1] - consensus_trajectory[i]
            
            # Detect sudden acceleration (emergence)
            if abs(next_change) > 2 * abs(current_change) and abs(next_change) > 0.1:
                return True
        
        return False
    
    def _is_valid_lifecycle_sequence(self, operations: List[str]) -> bool:
        """Validate resource lifecycle operation sequence"""
        if not operations:
            return True
        
        # Simple validation: must start with create, end with destroy
        if operations[0] != "create":
            return False
        
        if len(operations) > 1 and operations[-1] != "destroy":
            return False
        
        # No double creates or destroys
        create_count = operations.count("create")
        destroy_count = operations.count("destroy")
        
        return create_count == 1 and destroy_count <= 1
    
    def run_comprehensive_validation(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run all span-based validations.
        
        Returns comprehensive report that unit tests simply cannot provide.
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_spans_analyzed": len(spans),
            "validations": {}
        }
        
        # Semantic quine validation
        quine_result = self.validate_semantic_quine_property(spans)
        results["validations"]["semantic_quine"] = {
            "valid": quine_result.is_valid_quine,
            "cycles_tested": quine_result.cycles_tested,
            "convergence_proof": quine_result.convergence_proof
        }
        
        # AI agent consistency
        ai_consistency = self.validate_ai_agent_consistency(spans)
        results["validations"]["ai_consistency"] = {
            "valid": ai_consistency.valid,
            "score": ai_consistency.score,
            "issues": ai_consistency.issues
        }
        
        # Architecture boundary validation
        boundary_violations = self.validate_4_layer_architecture_boundaries(spans)
        results["validations"]["architecture_boundaries"] = {
            "valid": len(boundary_violations) == 0,
            "violations": len(boundary_violations),
            "critical_violations": len([v for v in boundary_violations if v.severity == "critical"])
        }
        
        # Conversation quality
        conv_quality = self.validate_conversation_convergence(spans)
        results["validations"]["conversation_quality"] = {
            "converged": conv_quality.converged,
            "participant_balance": conv_quality.participant_balance,
            "emergence_detected": conv_quality.emergence_detected,
            "issues": conv_quality.quality_issues
        }
        
        # Resource lifecycle
        resource_report = self.validate_resource_lifecycle(spans)
        results["validations"]["resource_lifecycle"] = {
            "leaks_detected": resource_report.leaks_detected,
            "memory_growth_rate": resource_report.memory_growth_rate,
            "violations": len(resource_report.lifecycle_violations)
        }
        
        # Structured output compliance
        output_compliance = self.validate_structured_output_compliance(spans)
        results["validations"]["structured_output_compliance"] = {
            "valid": output_compliance.valid,
            "score": output_compliance.score,
            "issues": output_compliance.issues
        }
        
        # Generation fidelity
        generation_fidelity = self.validate_generation_fidelity(spans)
        results["validations"]["generation_fidelity"] = {
            "valid": generation_fidelity.valid,
            "score": generation_fidelity.score,
            "issues": generation_fidelity.issues
        }
        
        # Overall system health score
        scores = [
            1.0 if quine_result.is_valid_quine else 0.0,
            ai_consistency.score,
            1.0 if len(boundary_violations) == 0 else 0.5,
            1.0 if conv_quality.converged else 0.0,
            1.0 if resource_report.leaks_detected == 0 else 0.0,
            output_compliance.score,
            generation_fidelity.score
        ]
        
        results["overall_health_score"] = sum(scores) / len(scores)
        results["system_reliable"] = results["overall_health_score"] > 0.8
        
        return results


def validate_system_via_spans(span_data_file: Path, semantic_conventions_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Main entry point for span-based system validation.
    
    This replaces traditional unit testing with runtime behavior validation.
    """
    # Load span data
    with open(span_data_file) as f:
        spans = json.load(f)
    
    # Load semantic conventions if provided
    semantic_conventions = {}
    if semantic_conventions_file and semantic_conventions_file.exists():
        with open(semantic_conventions_file) as f:
            semantic_conventions = json.load(f)
    
    # Run validation
    validator = SpanBasedValidator(semantic_conventions)
    return validator.run_comprehensive_validation(spans)


if __name__ == "__main__":
    # Example usage
    span_file = Path("conversation_outputs/otel_spans.json") 
    semantic_file = Path("semantic_conventions.json")
    
    if span_file.exists():
        results = validate_system_via_spans(span_file, semantic_file)
        print(f"System Health Score: {results['overall_health_score']:.2f}")
        print(f"System Reliable: {results['system_reliable']}")
        
        for validation_name, validation_result in results["validations"].items():
            print(f"{validation_name}: {'✅' if validation_result.get('valid', False) else '❌'}")
    else:
        print("No span data found - run the system first to generate spans")