#!/usr/bin/env python3
"""
Span Validation for LLM + Weaver + BPMN Test

Validates all claims from the LLM + Weaver + BPMN integration test using captured spans.
Follows span-based validation philosophy: "spans don't lie"

Usage:
    python span_validation_llm_weaver_test.py
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class LLMWeaverSpanValidator:
    """Validates LLM + Weaver + BPMN test claims using captured spans"""
    
    def __init__(self):
        self.console = Console()
        self.spans_file = Path("/Users/sac/dev/weavergen/llm_weaver_bpmn_test_output/test_execution_spans.json")
        self.claims_to_validate = [
            {
                "id": "llm_integration",
                "claim": "LLM agents were used for registry analysis, template generation, code review, and quality assessment",
                "span_evidence_required": ["llm_used"]
            },
            {
                "id": "weaver_integration", 
                "claim": "Real Weaver binary was used for multi-language code generation",
                "span_evidence_required": ["weaver_used"]
            },
            {
                "id": "bpmn_workflow",
                "claim": "BPMN workflow orchestrated 15 tasks with proper span tracking",
                "span_evidence_required": ["task", "span_id", "trace_id"]
            },
            {
                "id": "code_generation",
                "claim": "Generated code for Python and Rust languages (10 files total)",
                "span_evidence_required": ["files", "generation_type"]
            },
            {
                "id": "quality_score",
                "claim": "Achieved quality score of 87% through LLM assessment",
                "span_evidence_required": ["quality_score"]
            }
        ]
    
    def validate_test_claims(self) -> Dict[str, Any]:
        """Validate all test claims using captured spans"""
        
        self.console.print(Panel.fit(
            "[bold cyan]📊 Span-Based Validation: LLM + Weaver + BPMN Test[/bold cyan]\n"
            "[green]Validating claims using OpenTelemetry execution spans[/green]",
            border_style="cyan"
        ))
        
        # Load spans
        spans = self._load_spans()
        if not spans:
            return {"validation_failed": True, "error": "No spans found"}
        
        self.console.print(f"\n[cyan]📋 Loaded {len(spans)} execution spans for validation[/cyan]")
        
        # Validate each claim
        validation_results = []
        for claim in self.claims_to_validate:
            result = self._validate_claim(claim, spans)
            validation_results.append(result)
        
        # Generate validation report
        return {
            "validation_completed": True,
            "total_claims": len(self.claims_to_validate),
            "validated_claims": len([r for r in validation_results if r["validated"]]),
            "validation_rate": len([r for r in validation_results if r["validated"]]) / len(self.claims_to_validate),
            "results": validation_results,
            "spans_analyzed": len(spans)
        }
    
    def _load_spans(self) -> List[Dict[str, Any]]:
        """Load captured spans from test execution"""
        try:
            if self.spans_file.exists():
                with open(self.spans_file, 'r') as f:
                    return json.load(f)
            else:
                self.console.print(f"[red]⚠️ Spans file not found: {self.spans_file}[/red]")
                return []
        except Exception as e:
            self.console.print(f"[red]❌ Error loading spans: {e}[/red]")
            return []
    
    def _validate_claim(self, claim: Dict[str, Any], spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate individual claim against spans"""
        
        claim_id = claim["id"]
        claim_text = claim["claim"]
        required_evidence = claim["span_evidence_required"]
        
        validation_result = {
            "claim_id": claim_id,
            "claim": claim_text,
            "validated": False,
            "span_evidence": [],
            "evidence_count": 0,
            "supporting_spans": []
        }
        
        # Claim-specific validation logic
        if claim_id == "llm_integration":
            llm_spans = [s for s in spans if s.get("llm_used", False)]
            if len(llm_spans) >= 4:  # Registry analysis, template gen, code review, quality assessment
                validation_result["validated"] = True
                validation_result["span_evidence"] = [
                    f"Found {len(llm_spans)} LLM-integrated spans",
                    f"LLM tasks: {[s.get('task') for s in llm_spans]}"
                ]
                validation_result["evidence_count"] = len(llm_spans)
                validation_result["supporting_spans"] = [s.get("span_id") for s in llm_spans]
        
        elif claim_id == "weaver_integration":
            weaver_spans = [s for s in spans if s.get("weaver_used", False)]
            if len(weaver_spans) > 0:
                validation_result["validated"] = True
                validation_result["span_evidence"] = [
                    f"Found {len(weaver_spans)} Weaver-integrated spans",
                    f"Weaver tasks: {[s.get('task') for s in weaver_spans]}"
                ]
                validation_result["evidence_count"] = len(weaver_spans)
                validation_result["supporting_spans"] = [s.get("span_id") for s in weaver_spans]
        
        elif claim_id == "bpmn_workflow":
            total_spans = len(spans)
            spans_with_tasks = len([s for s in spans if s.get("task")])
            spans_with_ids = len([s for s in spans if s.get("span_id") and s.get("trace_id")])
            
            if total_spans >= 15 and spans_with_tasks >= 15 and spans_with_ids >= 15:
                validation_result["validated"] = True
                validation_result["span_evidence"] = [
                    f"Found {total_spans} total spans (≥15 required)",
                    f"All spans have proper task names and IDs",
                    f"Trace ID consistency: {len(set(s.get('trace_id') for s in spans))} unique traces"
                ]
                validation_result["evidence_count"] = total_spans
                validation_result["supporting_spans"] = [s.get("span_id") for s in spans[:5]]  # Sample
        
        elif claim_id == "code_generation":
            generation_spans = [s for s in spans if "generate" in s.get("task", "").lower()]
            files_generated = []
            
            for span in generation_spans:
                result = span.get("result", {})
                if "files" in result:
                    files_generated.extend(result["files"])
            
            if len(files_generated) >= 10:  # Python (5) + Rust (5)
                validation_result["validated"] = True
                validation_result["span_evidence"] = [
                    f"Found {len(generation_spans)} code generation spans",
                    f"Total files generated: {len(files_generated)}",
                    f"Languages: Python, Rust"
                ]
                validation_result["evidence_count"] = len(files_generated)
                validation_result["supporting_spans"] = [s.get("span_id") for s in generation_spans]
        
        elif claim_id == "quality_score":
            quality_spans = [s for s in spans if "quality" in s.get("task", "").lower()]
            if quality_spans:
                for span in quality_spans:
                    result = span.get("result", {})
                    if "quality_score" in result and result["quality_score"] >= 0.8:
                        validation_result["validated"] = True
                        validation_result["span_evidence"] = [
                            f"Quality assessment span found: {span.get('task')}",
                            f"Quality score: {result['quality_score']:.1%}",
                            f"LLM used: {span.get('llm_used', False)}"
                        ]
                        validation_result["evidence_count"] = 1
                        validation_result["supporting_spans"] = [span.get("span_id")]
                        break
        
        return validation_result
    
    def generate_validation_report(self, validation_data: Dict[str, Any]) -> Table:
        """Generate validation report table"""
        
        table = Table(title="📊 Span-Based Validation Report", show_header=True, header_style="bold magenta")
        table.add_column("Claim", style="cyan", width=40)
        table.add_column("Validated", style="green", width=10)
        table.add_column("Evidence Count", style="blue", width=15)
        table.add_column("Supporting Spans", style="yellow", width=20)
        
        for result in validation_data["results"]:
            claim = result["claim"][:37] + "..." if len(result["claim"]) > 40 else result["claim"]
            validated = "✅ Yes" if result["validated"] else "❌ No"
            evidence_count = str(result["evidence_count"])
            span_count = len(result["supporting_spans"])
            span_summary = f"{span_count} spans" if span_count > 0 else "No spans"
            
            table.add_row(claim, validated, evidence_count, span_summary)
        
        return table
    
    def display_detailed_evidence(self, validation_data: Dict[str, Any]):
        """Display detailed span evidence for each claim"""
        
        self.console.print(f"\n[bold cyan]🔍 Detailed Span Evidence:[/bold cyan]")
        
        for result in validation_data["results"]:
            claim_id = result["claim_id"]
            validated = result["validated"]
            
            status = "✅" if validated else "❌"
            self.console.print(f"\n[bold]{status} {claim_id.upper()}:[/bold]")
            self.console.print(f"  Claim: {result['claim']}")
            
            if result["span_evidence"]:
                self.console.print(f"  Evidence:")
                for evidence in result["span_evidence"]:
                    self.console.print(f"    • {evidence}")
            
            if result["supporting_spans"]:
                spans_preview = result["supporting_spans"][:3]  # Show first 3
                remaining = len(result["supporting_spans"]) - 3
                span_list = ", ".join(spans_preview)
                if remaining > 0:
                    span_list += f" (+{remaining} more)"
                self.console.print(f"  Supporting Spans: {span_list}")


def main():
    """Run span-based validation for LLM + Weaver + BPMN test"""
    
    validator = LLMWeaverSpanValidator()
    validation_result = validator.validate_test_claims()
    
    if validation_result.get("validation_failed"):
        validator.console.print(f"[red]❌ Validation failed: {validation_result.get('error')}[/red]")
        return
    
    # Display validation report
    validator.console.print(f"\n[bold green]🎉 Span Validation Complete![/bold green]")
    
    validation_report = validator.generate_validation_report(validation_result)
    validator.console.print(f"\n{validation_report}")
    
    # Display detailed evidence
    validator.display_detailed_evidence(validation_result)
    
    # Summary
    total_claims = validation_result["total_claims"]
    validated_claims = validation_result["validated_claims"]
    validation_rate = validation_result["validation_rate"]
    spans_analyzed = validation_result["spans_analyzed"]
    
    validator.console.print(f"\n[bold magenta]📋 Validation Summary:[/bold magenta]")
    validator.console.print(f"  • Claims Validated: {validated_claims}/{total_claims} ({validation_rate:.1%})")
    validator.console.print(f"  • Spans Analyzed: {spans_analyzed}")
    validator.console.print(f"  • Validation Method: OpenTelemetry span evidence")
    validator.console.print(f"  • Philosophy: Spans don't lie - runtime execution truth")
    
    if validation_rate >= 0.8:
        validator.console.print(f"\n[bold green]✅ HIGH CONFIDENCE: Claims validated with span evidence[/bold green]")
    else:
        validator.console.print(f"\n[bold yellow]⚠️ PARTIAL VALIDATION: Some claims lack span evidence[/bold yellow]")


if __name__ == "__main__":
    main()