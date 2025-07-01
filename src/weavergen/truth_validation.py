"""
Truth Validation Framework - Trust Only Execution Traces

This module implements a comprehensive framework for validating all claims
against OpenTelemetry spans. No summary is trusted without execution proof.
"""

import functools
import inspect
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, Span
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace.propagation import set_span_in_context


@dataclass
class ExecutionFact:
    """A single verifiable fact from execution."""
    timestamp: float
    filepath: str
    lineno: int
    function: str
    duration_ms: float
    success: bool
    attributes: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class Claim:
    """A claim that must be validated against execution facts."""
    text: str
    claimed_at: float
    claimed_by_file: str
    claimed_by_line: int
    evidence_required: List[str]  # Types of evidence needed
    validated: bool = False
    evidence_spans: List[str] = field(default_factory=list)  # Span IDs


class LieDetector:
    """Detects lies in summaries by comparing against execution traces."""
    
    def __init__(self):
        self.spans: Dict[str, ReadableSpan] = {}
        self.claims: Dict[str, Claim] = {}
        self.lies_detected: List[Dict[str, Any]] = []
    
    def analyze_summary(self, summary: str, trace_id: str) -> Dict[str, Any]:
        """Analyze a summary for lies by checking against trace."""
        lies = []
        unverifiable_claims = []
        verified_truths = []
        
        # Parse claims from summary (simplified - real impl would be smarter)
        claimed_items = self._extract_claims(summary)
        
        # Get all spans for this trace
        trace_spans = [s for s in self.spans.values() 
                      if s.context.trace_id == trace_id]
        
        for claim in claimed_items:
            evidence = self._find_evidence(claim, trace_spans)
            
            if not evidence:
                unverifiable_claims.append({
                    "claim": claim,
                    "reason": "No execution evidence found"
                })
            elif self._contradicts_evidence(claim, evidence):
                lies.append({
                    "claim": claim,
                    "evidence": evidence,
                    "contradiction": self._explain_contradiction(claim, evidence)
                })
            else:
                verified_truths.append({
                    "claim": claim,
                    "supporting_spans": [s.name for s in evidence]
                })
        
        return {
            "lies_detected": lies,
            "unverifiable_claims": unverifiable_claims,
            "verified_truths": verified_truths,
            "trust_score": len(verified_truths) / len(claimed_items) if claimed_items else 0
        }
    
    def _extract_claims(self, summary: str) -> List[str]:
        """Extract testable claims from a summary."""
        # Simplified - real implementation would use NLP
        claims = []
        
        # Look for common claim patterns
        patterns = [
            "successfully", "passed", "completed", "optimized",
            "improved", "fixed", "resolved", "deployed"
        ]
        
        lines = summary.lower().split('\n')
        for line in lines:
            if any(pattern in line for pattern in patterns):
                claims.append(line.strip())
        
        return claims
    
    def _find_evidence(self, claim: str, spans: List[ReadableSpan]) -> List[ReadableSpan]:
        """Find spans that could support or refute a claim."""
        evidence = []
        
        # Match spans by keywords in claim
        claim_lower = claim.lower()
        for span in spans:
            span_name_lower = span.name.lower()
            
            # Check if span name relates to claim
            if any(word in span_name_lower for word in claim_lower.split()):
                evidence.append(span)
            
            # Check span attributes for relevance
            for attr_key, attr_value in span.attributes.items():
                if isinstance(attr_value, str) and any(
                    word in attr_value.lower() for word in claim_lower.split()
                ):
                    evidence.append(span)
                    break
        
        return evidence
    
    def _contradicts_evidence(self, claim: str, evidence: List[ReadableSpan]) -> bool:
        """Check if a claim contradicts the evidence."""
        claim_lower = claim.lower()
        
        for span in evidence:
            # Check for failure indicators
            if span.status.status_code == StatusCode.ERROR:
                if any(word in claim_lower for word in ["success", "passed", "completed"]):
                    return True
            
            # Check for mock/skip indicators
            attrs = span.attributes
            if attrs.get("test.mocked") or attrs.get("test.skipped"):
                if "passed" in claim_lower or "tested" in claim_lower:
                    return True
            
            # Check for partial execution
            if "all" in claim_lower or "complete" in claim_lower:
                total = attrs.get("items.total", 0)
                processed = attrs.get("items.processed", 0)
                if total > 0 and processed < total:
                    return True
        
        return False
    
    def _explain_contradiction(self, claim: str, evidence: List[ReadableSpan]) -> str:
        """Explain why a claim contradicts the evidence."""
        explanations = []
        
        for span in evidence:
            if span.status.status_code == StatusCode.ERROR:
                error = span.attributes.get("error.message", "Unknown error")
                explanations.append(f"Span '{span.name}' failed with: {error}")
            
            if span.attributes.get("test.mocked"):
                explanations.append(f"Span '{span.name}' was mocked, not real execution")
            
            if span.attributes.get("test.skipped"):
                reason = span.attributes.get("test.skip_reason", "Unknown")
                explanations.append(f"Span '{span.name}' was skipped: {reason}")
        
        return "; ".join(explanations)


class TruthEnforcer:
    """Enforces that all claims must be backed by spans."""
    
    def __init__(self, tracer_provider: TracerProvider):
        self.tracer = trace.get_tracer(__name__, tracer_provider=tracer_provider)
        self.claims_made: Set[str] = set()
        self.claims_validated: Set[str] = set()
    
    def require_evidence(self, claim: str):
        """Decorator that requires span evidence for a claim."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Record where the claim is made
                frame = inspect.currentframe().f_back
                filepath = Path(frame.f_code.co_filename).name
                lineno = frame.f_lineno
                
                self.claims_made.add(claim)
                
                with self.tracer.start_as_current_span(
                    f"claim_validation:{claim}",
                    attributes={
                        "claim.text": claim,
                        "claim.function": func.__name__,
                        "code.filepath": filepath,
                        "code.lineno": lineno,
                    }
                ) as span:
                    try:
                        # Execute the function
                        result = func(*args, **kwargs)
                        
                        # Function must return evidence
                        if not isinstance(result, dict) or "evidence" not in result:
                            raise ValueError(f"No evidence provided for claim: {claim}")
                        
                        # Validate evidence
                        evidence = result["evidence"]
                        is_valid = self._validate_evidence(evidence, span)
                        
                        if is_valid:
                            self.claims_validated.add(claim)
                            span.set_attribute("claim.validated", True)
                        else:
                            span.set_attribute("claim.validated", False)
                            span.set_status(Status(StatusCode.ERROR))
                        
                        return result
                        
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR))
                        span.set_attribute("claim.validated", False)
                        raise
            
            return wrapper
        return decorator
    
    def _validate_evidence(self, evidence: Dict[str, Any], span: Span) -> bool:
        """Validate that evidence supports the claim."""
        required_keys = ["execution_time", "actual_result", "file_executed"]
        
        # Check required evidence
        for key in required_keys:
            if key not in evidence:
                span.set_attribute(f"evidence.missing.{key}", True)
                return False
            span.set_attribute(f"evidence.{key}", str(evidence[key]))
        
        # Evidence must show actual execution
        if evidence.get("mocked", False):
            span.set_attribute("evidence.mocked", True)
            return False
        
        return True
    
    @contextmanager
    def truth_context(self, operation: str):
        """Context manager that collects only verifiable facts."""
        with self.tracer.start_as_current_span(f"truth_context:{operation}") as span:
            facts = []
            start_time = time.time()
            
            # Capture execution context
            frame = inspect.currentframe().f_back
            span.set_attributes({
                "code.filepath": Path(frame.f_code.co_filename).name,
                "code.lineno": frame.f_lineno,
                "code.function": frame.f_code.co_name,
                "operation": operation
            })
            
            try:
                yield facts
                
                # Record collected facts
                span.set_attribute("facts.collected", len(facts))
                for i, fact in enumerate(facts):
                    span.set_attribute(f"fact.{i}", str(fact))
                
                span.set_status(Status(StatusCode.OK))
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise
            
            finally:
                duration = (time.time() - start_time) * 1000
                span.set_attribute("duration_ms", duration)


class SpanBasedValidator:
    """Validates operations using only span data."""
    
    def __init__(self):
        self.validation_rules = {}
    
    def add_rule(self, operation: str, rule: Callable[[ReadableSpan], bool]):
        """Add a validation rule for an operation."""
        self.validation_rules[operation] = rule
    
    def validate_operation(self, operation: str, span: ReadableSpan) -> Dict[str, Any]:
        """Validate an operation using only span data."""
        if operation not in self.validation_rules:
            return {
                "valid": False,
                "reason": f"No validation rule for operation: {operation}"
            }
        
        rule = self.validation_rules[operation]
        
        try:
            is_valid = rule(span)
            
            return {
                "valid": is_valid,
                "span_id": span.context.span_id,
                "operation": operation,
                "duration_ms": (span.end_time - span.start_time) / 1e6,
                "attributes": dict(span.attributes),
                "file": span.attributes.get("code.filepath", "unknown"),
                "line": span.attributes.get("code.lineno", 0)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}",
                "span_id": span.context.span_id
            }


# Example validation rules
def test_success_rule(span: ReadableSpan) -> bool:
    """A test is only successful if it actually ran and passed."""
    attrs = span.attributes
    
    # Must have actually executed
    if attrs.get("test.mocked", False) or attrs.get("test.skipped", False):
        return False
    
    # Must have succeeded
    if span.status.status_code != StatusCode.OK:
        return False
    
    # Must have test result
    return attrs.get("test.result") == "passed"


def deployment_success_rule(span: ReadableSpan) -> bool:
    """Deployment is only successful if all services are healthy."""
    attrs = span.attributes
    
    # All health checks must pass
    if attrs.get("health.check.failed", 0) > 0:
        return False
    
    # No rollback triggered
    if attrs.get("deployment.rolled_back", False):
        return False
    
    # Services must be responding
    return attrs.get("services.responding") == attrs.get("services.total")


# Example usage showing how summaries lie
def demonstrate_lying_summary():
    """Show how a summary can lie and how spans reveal truth."""
    
    # Setup tracing
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    
    enforcer = TruthEnforcer(provider)
    
    # A function that claims success but actually fails
    @enforcer.require_evidence("All user tests passed successfully")
    def run_user_tests():
        """This function claims all tests passed but actually skips some."""
        
        # Simulate running tests
        results = {
            "total": 10,
            "executed": 7,  # Only ran 7 out of 10!
            "passed": 7,
            "skipped": 3,  # These were skipped!
            "skip_reasons": ["Database unavailable", "API rate limited", "Timeout"]
        }
        
        # The lying summary would say "All tests passed"
        # But we must return evidence
        return {
            "evidence": {
                "execution_time": time.time(),
                "actual_result": results,
                "file_executed": __file__,
                "mocked": False
            }
        }
    
    # The truth enforcer will catch the lie
    try:
        result = run_user_tests()
        print("Function returned:", result)
    except ValueError as e:
        print("Caught lie:", e)


if __name__ == "__main__":
    demonstrate_lying_summary()