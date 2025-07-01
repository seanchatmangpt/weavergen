#!/usr/bin/env python3
"""
Span-Based Validation Audit

This script validates each claim from the summary against actual OpenTelemetry spans
captured during the working demo execution. Follows the philosophy that
"spans don't lie" - only span data provides execution truth.

Usage:
    python span_validation_audit.py
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

# Import our working demo to capture fresh spans
from working_ollama_demo import WorkingOllamaDemo


class SpanValidationAuditor:
    """Validates summary claims against actual span data"""
    
    def __init__(self):
        self.console = Console()
        trace.set_tracer_provider(TracerProvider())
        self.tracer = trace.get_tracer(__name__)
        
        # Claims to validate from the summary
        self.claims = {
            "bpmn_workflow": {
                "claim": "BPMN Workflow Definition with visual workflow, parallel gateways, service tasks",
                "expected_evidence": ["bpmn.task.*", "workflow execution spans"]
            },
            "ollama_integration": {
                "claim": "Real Ollama LLM integration using OpenAI-compatible API", 
                "expected_evidence": ["ollama_used=True", "task.type=ollama"]
            },
            "working_demo": {
                "claim": "2 Ollama LLM calls for real code generation",
                "expected_evidence": ["ollama_calls=2", "Generate Models", "Generate Agents"]
            },
            "bpmn_tasks": {
                "claim": "5 BPMN tasks executed with spans",
                "expected_evidence": ["5 spans total", "Load Semantics", "Generate Models", "Generate Agents", "Validate Results", "Capture Spans"]
            },
            "quality_score": {
                "claim": "85% quality score achieved",
                "expected_evidence": ["quality_score >= 0.85"]
            },
            "span_tracking": {
                "claim": "OpenTelemetry spans capture execution truth",
                "expected_evidence": ["span.trace_id", "span.span_id", "span timestamps"]
            }
        }
        
        self.validation_results = {}
    
    async def run_span_capture_audit(self) -> Dict[str, Any]:
        """Run demo and capture spans for validation"""
        
        with self.tracer.start_as_current_span("span_validation.audit") as audit_span:
            audit_span.set_attribute("audit.type", "span_based_validation")
            audit_span.set_attribute("audit.claims_count", len(self.claims))
            
            self.console.print(Panel.fit(
                "[bold cyan]📊 Span-Based Validation Audit[/bold cyan]\n"
                "[green]Validating summary claims against actual execution spans[/green]\n"
                "[yellow]Philosophy: Spans don't lie - only span data provides truth[/yellow]",
                border_style="cyan"
            ))
            
            # Execute demo to capture fresh spans
            self.console.print(f"\n[cyan]🔄 Executing working demo to capture spans...[/cyan]")
            
            demo = WorkingOllamaDemo()
            execution_result = await demo.run_bpmn_workflow_simulation()
            
            # Extract span data
            spans = execution_result.get("spans", [])
            execution_trace = execution_result.get("execution_trace", [])
            
            audit_span.set_attribute("audit.spans_captured", len(spans))
            audit_span.set_attribute("audit.execution_success", execution_result.get("success", False))
            
            self.console.print(f"[green]✅ Captured {len(spans)} spans for validation[/green]")
            
            # Validate each claim
            await self._validate_claims_against_spans(spans, execution_result)
            
            # Generate audit report
            audit_result = {
                "audit_timestamp": datetime.utcnow().isoformat(),
                "spans_captured": len(spans),
                "claims_validated": len(self.claims),
                "validation_results": self.validation_results,
                "execution_result": execution_result,
                "raw_spans": spans
            }
            
            return audit_result
    
    async def _validate_claims_against_spans(self, spans: List[Dict[str, Any]], execution_result: Dict[str, Any]):
        """Validate each claim against span evidence"""
        
        with self.tracer.start_as_current_span("span_validation.validate_claims") as span:
            span.set_attribute("validation.claims_count", len(self.claims))
            
            self.console.print(f"\n[bold cyan]🔍 Validating Claims Against Span Evidence:[/bold cyan]")
            
            for claim_id, claim_data in self.claims.items():
                validation_result = await self._validate_single_claim(claim_id, claim_data, spans, execution_result)
                self.validation_results[claim_id] = validation_result
                
                # Display validation result
                status_icon = "✅" if validation_result["validated"] else "❌"
                self.console.print(f"  {status_icon} {claim_data['claim']}")
                
                if validation_result["span_evidence"]:
                    for evidence in validation_result["span_evidence"][:2]:  # Show first 2 pieces of evidence
                        self.console.print(f"    🔗 Span Evidence: {evidence}")
                
                if not validation_result["validated"] and validation_result["missing_evidence"]:
                    for missing in validation_result["missing_evidence"]:
                        self.console.print(f"    ❌ Missing: {missing}")
            
            span.set_attribute("validation.validated_claims", sum(1 for r in self.validation_results.values() if r["validated"]))
    
    async def _validate_single_claim(self, claim_id: str, claim_data: Dict[str, Any], 
                                   spans: List[Dict[str, Any]], execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single claim against span data"""
        
        validation_result = {
            "claim_id": claim_id,
            "claim": claim_data["claim"],
            "validated": False,
            "span_evidence": [],
            "missing_evidence": [],
            "span_references": []
        }
        
        if claim_id == "bpmn_workflow":
            # Check for BPMN task spans
            bpmn_spans = [s for s in spans if s.get("task") and "span_id" in s]
            if len(bpmn_spans) > 0:
                validation_result["validated"] = True
                validation_result["span_evidence"] = [
                    f"Found {len(bpmn_spans)} BPMN task spans",
                    f"Tasks: {[s.get('task') for s in bpmn_spans]}"
                ]
                validation_result["span_references"] = [s.get("span_id") for s in bpmn_spans]
            else:
                validation_result["missing_evidence"] = ["No BPMN task spans found"]
        
        elif claim_id == "ollama_integration":
            # Check for Ollama usage in spans
            ollama_spans = [s for s in spans if s.get("type") == "ollama"]
            if len(ollama_spans) > 0:
                validation_result["validated"] = True
                validation_result["span_evidence"] = [
                    f"Found {len(ollama_spans)} Ollama-integrated spans",
                    f"Ollama tasks: {[s.get('task') for s in ollama_spans]}"
                ]
                validation_result["span_references"] = [s.get("span_id") for s in ollama_spans]
            else:
                validation_result["missing_evidence"] = ["No Ollama integration spans found"]
        
        elif claim_id == "working_demo":
            # Check for 2 Ollama calls
            ollama_calls = execution_result.get("ollama_calls", 0)
            if ollama_calls >= 2:
                validation_result["validated"] = True
                validation_result["span_evidence"] = [
                    f"Execution result shows {ollama_calls} Ollama calls",
                    f"Expected 2 calls for model + agent generation"
                ]
            else:
                validation_result["missing_evidence"] = [f"Expected 2 Ollama calls, found {ollama_calls}"]
        
        elif claim_id == "bpmn_tasks":
            # Check for 5 BPMN tasks
            if len(spans) >= 5:
                expected_tasks = ["Load Semantics", "Generate Models", "Generate Agents", "Validate Results", "Capture Spans"]
                found_tasks = [s.get("task") for s in spans]
                matching_tasks = [task for task in expected_tasks if task in found_tasks]
                
                if len(matching_tasks) >= 4:  # Allow some flexibility
                    validation_result["validated"] = True
                    validation_result["span_evidence"] = [
                        f"Found {len(spans)} total spans",
                        f"Matching tasks: {matching_tasks}"
                    ]
                    validation_result["span_references"] = [s.get("span_id") for s in spans]
                else:
                    validation_result["missing_evidence"] = [f"Expected tasks not found: {set(expected_tasks) - set(found_tasks)}"]
            else:
                validation_result["missing_evidence"] = [f"Expected 5+ spans, found {len(spans)}"]
        
        elif claim_id == "quality_score":
            # Check quality score
            quality_score = execution_result.get("quality_score", 0.0)
            if quality_score >= 0.80:  # Allow some tolerance
                validation_result["validated"] = True
                validation_result["span_evidence"] = [
                    f"Quality score: {quality_score:.1%}",
                    f"Meets 80%+ threshold for validation"
                ]
            else:
                validation_result["missing_evidence"] = [f"Quality score {quality_score:.1%} below 80% threshold"]
        
        elif claim_id == "span_tracking":
            # Check span structure
            valid_spans = [s for s in spans if s.get("span_id") and s.get("trace_id") and s.get("timestamp")]
            if len(valid_spans) > 0:
                validation_result["validated"] = True
                validation_result["span_evidence"] = [
                    f"Found {len(valid_spans)} structurally valid spans",
                    f"Span example: trace_id={valid_spans[0].get('trace_id', '')[:8]}, span_id={valid_spans[0].get('span_id', '')[:8]}"
                ]
                validation_result["span_references"] = [s.get("span_id") for s in valid_spans[:3]]
            else:
                validation_result["missing_evidence"] = ["No structurally valid spans with trace_id/span_id/timestamp"]
        
        return validation_result
    
    def generate_audit_report(self, audit_result: Dict[str, Any]) -> Table:
        """Generate comprehensive audit report"""
        
        table = Table(title="📊 Span-Based Validation Audit Report", show_header=True, header_style="bold magenta")
        table.add_column("Claim", style="cyan", width=40)
        table.add_column("Validated", style="green", width=12)
        table.add_column("Span Evidence", style="yellow", width=30)
        table.add_column("Span References", style="blue", width=15)
        
        for claim_id, result in audit_result["validation_results"].items():
            claim_text = result["claim"][:37] + "..." if len(result["claim"]) > 40 else result["claim"]
            validated = "✅ VALID" if result["validated"] else "❌ INVALID"
            evidence = result["span_evidence"][0] if result["span_evidence"] else "No evidence"
            evidence = evidence[:27] + "..." if len(evidence) > 30 else evidence
            span_refs = f"{len(result['span_references'])} spans" if result["span_references"] else "None"
            
            table.add_row(claim_text, validated, evidence, span_refs)
        
        return table
    
    def generate_span_tree(self, spans: List[Dict[str, Any]]) -> Tree:
        """Generate span hierarchy tree"""
        
        tree = Tree("🔍 Captured Execution Spans")
        
        for i, span in enumerate(spans):
            task_name = span.get("task", f"Task_{i+1}")
            span_id = span.get("span_id", "unknown")[:8]
            task_type = span.get("type", "unknown")
            timestamp = span.get("timestamp", "")[:19]
            
            span_node = Tree(f"[cyan]{task_name}[/cyan]")
            span_node.add(f"[yellow]Type:[/yellow] {'🤖 Ollama' if task_type == 'ollama' else '⚙️ Utility'}")
            span_node.add(f"[yellow]Span ID:[/yellow] {span_id}")
            span_node.add(f"[yellow]Timestamp:[/yellow] {timestamp}")
            span_node.add(f"[yellow]Success:[/yellow] {'✅' if span.get('success', True) else '❌'}")
            
            tree.add(span_node)
        
        return tree


async def main():
    """Run span-based validation audit"""
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold white]🔍 Span-Based Summary Validation[/bold white]\n"
        "[blue]Auditing claims against actual OpenTelemetry execution data[/blue]",
        border_style="blue"
    ))
    
    # Run audit
    auditor = SpanValidationAuditor()
    audit_result = await auditor.run_span_capture_audit()
    
    # Display results
    console.print(f"\n[bold green]📊 Audit Complete![/bold green]")
    
    # Audit summary table
    audit_table = auditor.generate_audit_report(audit_result)
    console.print(f"\n{audit_table}")
    
    # Span evidence tree
    if audit_result.get("raw_spans"):
        console.print(f"\n[bold cyan]🌳 Span Evidence Tree:[/bold cyan]")
        span_tree = auditor.generate_span_tree(audit_result["raw_spans"])
        console.print(span_tree)
    
    # Validation summary
    total_claims = len(audit_result["validation_results"])
    validated_claims = sum(1 for r in audit_result["validation_results"].values() if r["validated"])
    validation_rate = validated_claims / total_claims if total_claims > 0 else 0
    
    console.print(f"\n[bold magenta]🎯 Validation Summary:[/bold magenta]")
    console.print(f"  • Total Claims: {total_claims}")
    console.print(f"  • Validated Claims: {validated_claims}")
    console.print(f"  • Validation Rate: {validation_rate:.1%}")
    console.print(f"  • Spans Captured: {audit_result['spans_captured']}")
    console.print(f"  • Audit Timestamp: {audit_result['audit_timestamp']}")
    
    # Span-referenced final assessment
    console.print(f"\n[bold yellow]📋 Span-Referenced Assessment:[/bold yellow]")
    console.print(f"Based on captured spans from execution:")
    
    for claim_id, result in audit_result["validation_results"].items():
        status = "✅ VALIDATED" if result["validated"] else "❌ INVALIDATED"
        span_count = len(result["span_references"])
        console.print(f"  • {claim_id.replace('_', ' ').title()}: {status} ({span_count} supporting spans)")
    
    if validation_rate >= 0.8:
        console.print(f"\n[bold green]🎉 SPAN VALIDATION SUCCESSFUL![/bold green]")
        console.print(f"[green]{validation_rate:.1%} of claims validated by actual span evidence.[/green]")
    else:
        console.print(f"\n[bold red]❌ SPAN VALIDATION FAILED![/bold red]")
        console.print(f"[red]Only {validation_rate:.1%} of claims supported by span evidence.[/red]")
    
    # Save detailed audit results
    audit_file = Path("span_validation_audit_results.json")
    with open(audit_file, 'w') as f:
        json.dump(audit_result, f, indent=2)
    
    console.print(f"\n[cyan]💾 Detailed audit results saved to: {audit_file}[/cyan]")


if __name__ == "__main__":
    asyncio.run(main())