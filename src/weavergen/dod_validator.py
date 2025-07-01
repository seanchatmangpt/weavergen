"""
Definition of Done Validator

Implements the strict validation criteria where ALL claims must be
proven by telemetry including file paths and BPMN references.
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import json

from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class DoDViolation:
    """A Definition of Done violation"""
    level: str  # "L1", "L2", "L3"
    rule: str
    description: str
    span_id: str
    severity: str  # "critical", "major", "minor"
    evidence: Dict[str, Any]


@dataclass
class DoDValidationResult:
    """Complete DoD validation result"""
    total_spans: int = 0
    level1_pass: int = 0
    level2_pass: int = 0
    level3_pass: int = 0
    violations: List[DoDViolation] = field(default_factory=list)
    lies_detected: List[Dict[str, Any]] = field(default_factory=list)
    trust_score: float = 0.0
    is_done: bool = False


class BPMNValidator:
    """Validates BPMN references in spans"""
    
    def __init__(self):
        self.bpmn_cache: Dict[str, Dict[str, Any]] = {}
    
    def load_bpmn(self, bpmn_file: str) -> Optional[Dict[str, Any]]:
        """Load and parse BPMN file"""
        if bpmn_file in self.bpmn_cache:
            return self.bpmn_cache[bpmn_file]
        
        try:
            if not Path(bpmn_file).exists():
                return None
            
            tree = ET.parse(bpmn_file)
            root = tree.getroot()
            
            # Extract namespace
            ns = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
            
            # Find process
            process = root.find('.//bpmn:process', ns)
            if not process:
                return None
            
            # Extract tasks
            tasks = {}
            for task in process.findall('.//bpmn:serviceTask', ns):
                task_id = task.get('id')
                task_name = task.get('name', '')
                tasks[task_id] = {
                    'name': task_name,
                    'type': 'serviceTask'
                }
            
            # Add other task types
            for task in process.findall('.//bpmn:userTask', ns):
                task_id = task.get('id')
                tasks[task_id] = {
                    'name': task.get('name', ''),
                    'type': 'userTask'
                }
            
            result = {
                'process_id': process.get('id'),
                'process_name': process.get('name', ''),
                'tasks': tasks
            }
            
            self.bpmn_cache[bpmn_file] = result
            return result
            
        except Exception as e:
            console.print(f"[red]Error loading BPMN {bpmn_file}: {e}[/red]")
            return None
    
    def validate_task_reference(self, bpmn_file: str, task_id: str) -> Tuple[bool, str]:
        """Validate that a task ID exists in the BPMN file"""
        bpmn_data = self.load_bpmn(bpmn_file)
        
        if not bpmn_data:
            return False, f"BPMN file not found: {bpmn_file}"
        
        if task_id not in bpmn_data['tasks']:
            return False, f"Task ID '{task_id}' not found in BPMN"
        
        return True, "Valid"


class DefinitionOfDoneValidator:
    """Validates spans against the Definition of Done criteria"""
    
    def __init__(self):
        self.bpmn_validator = BPMNValidator()
    
    def validate_spans(self, spans: List[Dict[str, Any]]) -> DoDValidationResult:
        """Validate all spans against DoD criteria"""
        result = DoDValidationResult(total_spans=len(spans))
        
        for span in spans:
            span_id = span.get("span_id", "unknown")
            attrs = span.get("attributes", {})
            
            # Level 1: Basic Execution
            l1_pass = self._validate_level1(span, result)
            if l1_pass:
                result.level1_pass += 1
            
            # Level 2: Full Attribution
            l2_pass = self._validate_level2(span, attrs, result)
            if l2_pass:
                result.level2_pass += 1
            
            # Level 3: Semantic Compliance
            l3_pass = self._validate_level3(span, attrs, result)
            if l3_pass:
                result.level3_pass += 1
        
        # Calculate trust score
        if result.total_spans > 0:
            weights = {
                "level1": 0.3,
                "level2": 0.5,
                "level3": 0.2
            }
            
            result.trust_score = (
                (result.level1_pass / result.total_spans) * weights["level1"] +
                (result.level2_pass / result.total_spans) * weights["level2"] +
                (result.level3_pass / result.total_spans) * weights["level3"]
            )
        
        # Determine if done
        result.is_done = (
            result.trust_score >= 0.95 and
            len(result.lies_detected) == 0 and
            all(v.severity != "critical" for v in result.violations)
        )
        
        return result
    
    def _validate_level1(self, span: Dict[str, Any], result: DoDValidationResult) -> bool:
        """Validate Level 1: Basic Execution"""
        violations = []
        span_id = span.get("span_id", "unknown")
        
        # Check span name
        if not span.get("name"):
            violations.append(DoDViolation(
                level="L1",
                rule="No Span, No Claim",
                description="Span missing name",
                span_id=span_id,
                severity="critical",
                evidence={"name": None}
            ))
        
        # Check IDs
        if not span.get("trace_id"):
            violations.append(DoDViolation(
                level="L1",
                rule="Basic Structure",
                description="Missing trace_id",
                span_id=span_id,
                severity="critical",
                evidence={"trace_id": None}
            ))
        
        # Check timing
        start_time = span.get("start_time", 0)
        end_time = span.get("end_time", 0)
        duration = span.get("duration_ns", 0)
        
        if duration <= 0:
            violations.append(DoDViolation(
                level="L1",
                rule="Valid Duration",
                description="Invalid or missing duration",
                span_id=span_id,
                severity="major",
                evidence={"duration_ns": duration}
            ))
        
        # Check for unreasonable duration (> 30s)
        if duration > 30_000_000_000:  # 30 seconds in nanoseconds
            violations.append(DoDViolation(
                level="L1",
                rule="Reasonable Duration",
                description=f"Duration too long: {duration/1e9:.1f}s",
                span_id=span_id,
                severity="major",
                evidence={"duration_ns": duration}
            ))
        
        result.violations.extend(violations)
        return len(violations) == 0
    
    def _validate_level2(self, span: Dict[str, Any], attrs: Dict[str, Any], result: DoDValidationResult) -> bool:
        """Validate Level 2: Full Attribution"""
        violations = []
        lies = []
        span_id = span.get("span_id", "unknown")
        
        # Check code attribution
        filepath = attrs.get("code.filepath")
        if not filepath:
            violations.append(DoDViolation(
                level="L2",
                rule="File Must Exist",
                description="Missing code.filepath attribute",
                span_id=span_id,
                severity="critical",
                evidence={"code.filepath": None}
            ))
        elif not os.path.exists(filepath):
            lies.append({
                "claim": f"Executed from {filepath}",
                "reality": "File does not exist",
                "span_id": span_id,
                "type": "fake_file"
            })
            violations.append(DoDViolation(
                level="L2",
                rule="File Must Exist",
                description=f"File does not exist: {filepath}",
                span_id=span_id,
                severity="critical",
                evidence={"code.filepath": filepath, "exists": False}
            ))
        
        # Check line number
        lineno = attrs.get("code.lineno", 0)
        if lineno <= 0:
            violations.append(DoDViolation(
                level="L2",
                rule="Valid Line Number",
                description="Invalid or missing line number",
                span_id=span_id,
                severity="major",
                evidence={"code.lineno": lineno}
            ))
        
        # Check BPMN attribution
        bpmn_file = attrs.get("bpmn.workflow.file")
        task_id = attrs.get("bpmn.task.id")
        
        if bpmn_file:
            if not os.path.exists(bpmn_file):
                lies.append({
                    "claim": f"Executed BPMN workflow {bpmn_file}",
                    "reality": "BPMN file does not exist",
                    "span_id": span_id,
                    "type": "fake_bpmn"
                })
                violations.append(DoDViolation(
                    level="L2",
                    rule="BPMN Must Match",
                    description=f"BPMN file does not exist: {bpmn_file}",
                    span_id=span_id,
                    severity="critical",
                    evidence={"bpmn.workflow.file": bpmn_file, "exists": False}
                ))
            elif task_id:
                # Validate task exists in BPMN
                valid, msg = self.bpmn_validator.validate_task_reference(bpmn_file, task_id)
                if not valid:
                    lies.append({
                        "claim": f"Executed BPMN task {task_id}",
                        "reality": msg,
                        "span_id": span_id,
                        "type": "fake_task"
                    })
                    violations.append(DoDViolation(
                        level="L2",
                        rule="BPMN Must Match",
                        description=msg,
                        span_id=span_id,
                        severity="critical",
                        evidence={
                            "bpmn.workflow.file": bpmn_file,
                            "bpmn.task.id": task_id,
                            "valid": False
                        }
                    ))
        
        # Check execution timestamp
        if not attrs.get("execution.timestamp"):
            violations.append(DoDViolation(
                level="L2",
                rule="Timestamp Required",
                description="Missing execution.timestamp",
                span_id=span_id,
                severity="major",
                evidence={"execution.timestamp": None}
            ))
        
        result.violations.extend(violations)
        result.lies_detected.extend(lies)
        return len(violations) == 0
    
    def _validate_level3(self, span: Dict[str, Any], attrs: Dict[str, Any], result: DoDValidationResult) -> bool:
        """Validate Level 3: Semantic Compliance"""
        violations = []
        span_id = span.get("span_id", "unknown")
        span_name = span.get("name", "")
        
        # Check semantic attributes based on span type
        if "bpmn" in span_name:
            required = ["bpmn.workflow.id", "bpmn.task.type"]
            for attr in required:
                if attr not in attrs:
                    violations.append(DoDViolation(
                        level="L3",
                        rule="Semantic Compliance",
                        description=f"Missing required BPMN attribute: {attr}",
                        span_id=span_id,
                        severity="minor",
                        evidence={"missing_attribute": attr}
                    ))
        
        if "weaver" in span_name:
            required = ["weaver.command"]
            for attr in required:
                if attr not in attrs and "weaver.path" not in attrs:
                    violations.append(DoDViolation(
                        level="L3",
                        rule="Semantic Compliance",
                        description=f"Missing required Weaver attribute",
                        span_id=span_id,
                        severity="minor",
                        evidence={"span_type": "weaver"}
                    ))
        
        # Check success claims
        if attrs.get("execution.success") is True:
            # If claiming success, should not have errors
            if attrs.get("execution.error"):
                result.lies_detected.append({
                    "claim": "Execution succeeded",
                    "reality": f"Error present: {attrs['execution.error']}",
                    "span_id": span_id,
                    "type": "false_success"
                })
        
        result.violations.extend(violations)
        return len(violations) == 0
    
    def generate_report(self, result: DoDValidationResult) -> Table:
        """Generate validation report table"""
        table = Table(title="Definition of Done Validation", show_header=True)
        table.add_column("Criteria", style="cyan", width=30)
        table.add_column("Pass Rate", style="green", width=15)
        table.add_column("Violations", style="red", width=15)
        table.add_column("Status", style="bold", width=15)
        
        # Level 1
        l1_rate = result.level1_pass / result.total_spans if result.total_spans > 0 else 0
        l1_violations = len([v for v in result.violations if v.level == "L1"])
        table.add_row(
            "Level 1: Basic Execution",
            f"{l1_rate:.1%}",
            str(l1_violations),
            "✅" if l1_rate >= 0.95 else "❌"
        )
        
        # Level 2
        l2_rate = result.level2_pass / result.total_spans if result.total_spans > 0 else 0
        l2_violations = len([v for v in result.violations if v.level == "L2"])
        table.add_row(
            "Level 2: Full Attribution",
            f"{l2_rate:.1%}",
            str(l2_violations),
            "✅" if l2_rate >= 0.95 else "❌"
        )
        
        # Level 3
        l3_rate = result.level3_pass / result.total_spans if result.total_spans > 0 else 0
        l3_violations = len([v for v in result.violations if v.level == "L3"])
        table.add_row(
            "Level 3: Semantic Compliance",
            f"{l3_rate:.1%}",
            str(l3_violations),
            "✅" if l3_rate >= 0.90 else "⚠️"
        )
        
        return table
    
    def generate_lies_report(self, result: DoDValidationResult) -> Optional[Table]:
        """Generate report of detected lies"""
        if not result.lies_detected:
            return None
        
        table = Table(title="🚨 LIES DETECTED 🚨", show_header=True, style="red")
        table.add_column("Claim", style="yellow", width=40)
        table.add_column("Reality", style="red", width=40)
        table.add_column("Type", style="magenta", width=15)
        table.add_column("Span ID", style="cyan", width=20)
        
        for lie in result.lies_detected:
            table.add_row(
                lie["claim"],
                lie["reality"],
                lie["type"],
                lie["span_id"][:16] + "..."
            )
        
        return table


def validate_definition_of_done(span_file: Path) -> DoDValidationResult:
    """Main function to validate spans against DoD"""
    # Load spans
    with open(span_file) as f:
        spans = json.load(f)
    
    # Validate
    validator = DefinitionOfDoneValidator()
    result = validator.validate_spans(spans)
    
    # Show reports
    console.print(validator.generate_report(result))
    
    if result.lies_detected:
        console.print()
        console.print(validator.generate_lies_report(result))
    
    # Show violations by severity
    if result.violations:
        console.print("\n[bold red]Critical Violations:[/bold red]")
        for v in result.violations:
            if v.severity == "critical":
                console.print(f"  • {v.description} (Span: {v.span_id[:16]}...)")
    
    # Final verdict
    verdict = Panel(
        f"[bold]DEFINITION OF DONE VERDICT[/bold]\n\n"
        f"Trust Score: [{'green' if result.trust_score >= 0.95 else 'red'}]{result.trust_score:.1%}[/]\n"
        f"Lies Detected: [{'red' if result.lies_detected else 'green'}]{len(result.lies_detected)}[/]\n"
        f"Critical Violations: {len([v for v in result.violations if v.severity == 'critical'])}\n\n"
        f"IS DONE: [{'green' if result.is_done else 'red'}]{'YES' if result.is_done else 'NO'}[/]",
        style="cyan" if result.is_done else "red"
    )
    console.print(verdict)
    
    return result


if __name__ == "__main__":
    # Test with actual spans
    span_file = Path("bpmn_validation/test_spans.json")
    if span_file.exists():
        validate_definition_of_done(span_file)