#!/usr/bin/env python3
"""
Demonstration: How Summaries Lie and Spans Reveal Truth in WeaverGen

This example shows a real scenario where a summary claims successful
code generation across multiple languages, but the spans reveal that
several languages failed or were skipped.
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor, 
    ConsoleSpanExporter,
    SimpleSpanProcessor
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


# Setup tracing with in-memory export for analysis
memory_exporter = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(memory_exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


class LyingSummaryGenerator:
    """Generates summaries that hide the truth."""
    
    def generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary that looks good but hides problems."""
        
        # This is how summaries typically lie - by selective reporting
        summary = """
# WeaverGen Multi-Language Generation Report

✅ **Successfully generated code for multiple languages**

## Languages Processed:
- Python ✓
- Go ✓
- Java ✓
- Rust ✓
- JavaScript ✓

## Performance:
- Total time: 2.5 seconds
- Average per language: 0.5 seconds

## Quality:
- All templates validated
- Code generation completed without errors
- Output files created successfully

**Status: SUCCESS** 🎉
"""
        return summary.strip()


class TruthfulSpanGenerator:
    """Generates spans that reveal what actually happened."""
    
    def __init__(self):
        self.results = {}
    
    @tracer.start_as_current_span("weavergen.multi_language_generation")
    def generate_all_languages(self, semantic_yaml: str) -> Dict[str, Any]:
        """Actually try to generate code for all languages."""
        
        span = trace.get_current_span()
        span.set_attributes({
            "code.filepath": __file__,
            "code.lineno": 76,
            "semantic.yaml": semantic_yaml,
            "operation": "multi_language_generation"
        })
        
        languages = ["python", "go", "java", "rust", "javascript"]
        results = {}
        
        for lang in languages:
            with tracer.start_as_current_span(f"generate_{lang}") as lang_span:
                lang_span.set_attributes({
                    "code.filepath": __file__,
                    "code.lineno": 87,
                    "language": lang,
                    "semantic.yaml": semantic_yaml
                })
                
                # Simulate realistic failures
                result = self._generate_language(lang, semantic_yaml, lang_span)
                results[lang] = result
        
        # Set summary attributes
        successful = sum(1 for r in results.values() if r["success"])
        span.set_attributes({
            "languages.total": len(languages),
            "languages.successful": successful,
            "languages.failed": len(languages) - successful
        })
        
        return results
    
    def _generate_language(self, language: str, yaml_path: str, span) -> Dict[str, Any]:
        """Generate code for a specific language - with realistic failures."""
        
        start_time = time.time()
        
        try:
            if language == "python":
                # Python succeeds
                span.set_attributes({
                    "weaver.command": "weaver forge --yaml semantic.yaml --template python.j2",
                    "weaver.exit_code": 0,
                    "files.generated": 5,
                    "template.found": True
                })
                span.set_status(Status(StatusCode.OK))
                
                return {
                    "success": True,
                    "files": ["models.py", "metrics.py", "traces.py", "logs.py", "__init__.py"],
                    "duration": time.time() - start_time
                }
            
            elif language == "go":
                # Go fails due to missing template
                error_msg = "Template not found: go_template.j2"
                span.set_attributes({
                    "weaver.command": "weaver forge --yaml semantic.yaml --template go.j2",
                    "weaver.exit_code": 1,
                    "error.type": "TemplateNotFound",
                    "error.message": error_msg,
                    "template.found": False
                })
                span.set_status(Status(StatusCode.ERROR, error_msg))
                span.record_exception(FileNotFoundError(error_msg))
                
                return {
                    "success": False,
                    "error": error_msg,
                    "duration": time.time() - start_time
                }
            
            elif language == "java":
                # Java is skipped due to missing dependency
                skip_reason = "Maven not installed"
                span.set_attributes({
                    "generation.skipped": True,
                    "skip.reason": skip_reason,
                    "dependency.missing": "maven",
                    "weaver.command": "NOT_EXECUTED"
                })
                span.add_event("Skipped Java generation", {"reason": skip_reason})
                
                return {
                    "success": False,
                    "skipped": True,
                    "reason": skip_reason,
                    "duration": time.time() - start_time
                }
            
            elif language == "rust":
                # Rust partially succeeds (only generates some files)
                span.set_attributes({
                    "weaver.command": "weaver forge --yaml semantic.yaml --template rust.j2",
                    "weaver.exit_code": 0,
                    "files.expected": 8,
                    "files.generated": 3,  # Only 3 out of 8 files!
                    "generation.partial": True,
                    "warning": "Template incomplete - missing metric definitions"
                })
                span.set_status(Status(StatusCode.OK))  # Exit code 0, but incomplete
                
                return {
                    "success": True,  # Technically succeeded, but incomplete
                    "partial": True,
                    "files": ["lib.rs", "traces.rs", "common.rs"],
                    "missing": ["metrics.rs", "logs.rs", "events.rs", "attributes.rs", "mod.rs"],
                    "duration": time.time() - start_time
                }
            
            elif language == "javascript":
                # JavaScript times out
                timeout_duration = 30.0
                time.sleep(0.1)  # Simulate some work
                
                span.set_attributes({
                    "weaver.command": "weaver forge --yaml semantic.yaml --template js.j2",
                    "weaver.timeout": True,
                    "timeout.duration_seconds": timeout_duration,
                    "error.type": "TimeoutError"
                })
                span.set_status(Status(StatusCode.ERROR, "Generation timed out"))
                
                return {
                    "success": False,
                    "error": f"Timed out after {timeout_duration}s",
                    "timeout": True,
                    "duration": timeout_duration
                }
                
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }


def analyze_spans_for_truth(spans: List) -> Dict[str, Any]:
    """Analyze spans to extract the actual truth."""
    
    truth_report = {
        "total_languages_attempted": 0,
        "actually_succeeded": 0,
        "failed_with_errors": 0,
        "skipped_entirely": 0,
        "partial_success": 0,
        "specific_failures": [],
        "execution_facts": []
    }
    
    for span in spans:
        if "generate_" in span.name and span.name != "weavergen.multi_language_generation":
            language = span.attributes.get("language", "unknown")
            
            truth_report["total_languages_attempted"] += 1
            
            # Extract the truth from span attributes
            fact = {
                "language": language,
                "file": span.attributes.get("code.filepath"),
                "line": span.attributes.get("code.lineno"),
                "duration_ms": (span.end_time - span.start_time) / 1_000_000
            }
            
            if span.attributes.get("generation.skipped"):
                truth_report["skipped_entirely"] += 1
                fact["status"] = "SKIPPED"
                fact["reason"] = span.attributes.get("skip.reason")
                truth_report["specific_failures"].append(
                    f"{language}: Skipped - {span.attributes.get('skip.reason')}"
                )
            
            elif span.status.status_code == StatusCode.ERROR:
                truth_report["failed_with_errors"] += 1
                fact["status"] = "FAILED"
                fact["error"] = span.attributes.get("error.message", "Unknown error")
                truth_report["specific_failures"].append(
                    f"{language}: Failed - {span.attributes.get('error.message')}"
                )
            
            elif span.attributes.get("generation.partial"):
                truth_report["partial_success"] += 1
                fact["status"] = "PARTIAL"
                fact["files_generated"] = span.attributes.get("files.generated")
                fact["files_expected"] = span.attributes.get("files.expected")
                truth_report["specific_failures"].append(
                    f"{language}: Partial - Only {span.attributes.get('files.generated')}/{span.attributes.get('files.expected')} files generated"
                )
            
            else:
                truth_report["actually_succeeded"] += 1
                fact["status"] = "SUCCESS"
                fact["files_generated"] = span.attributes.get("files.generated")
            
            truth_report["execution_facts"].append(fact)
    
    return truth_report


def compare_summary_to_truth():
    """Run the demonstration comparing lying summary to span truth."""
    
    print("=" * 80)
    print("DEMONSTRATION: How Summaries Lie and Spans Reveal Truth")
    print("=" * 80)
    
    # Generate code for multiple languages
    generator = TruthfulSpanGenerator()
    results = generator.generate_all_languages("semantic-conventions/model/metrics/http.yaml")
    
    # Generate the lying summary
    summary_gen = LyingSummaryGenerator()
    lying_summary = summary_gen.generate_summary(results)
    
    print("\n📄 THE SUMMARY (What the developer claims):")
    print("-" * 40)
    print(lying_summary)
    print("-" * 40)
    
    # Get the truth from spans
    spans = memory_exporter.get_finished_spans()
    truth = analyze_spans_for_truth(spans)
    
    print("\n🔍 THE SPANS (What actually happened):")
    print("-" * 40)
    print(f"Total languages attempted: {truth['total_languages_attempted']}")
    print(f"Actually succeeded: {truth['actually_succeeded']}")
    print(f"Failed with errors: {truth['failed_with_errors']}")
    print(f"Skipped entirely: {truth['skipped_entirely']}")
    print(f"Partial success: {truth['partial_success']}")
    
    print("\n🚨 SPECIFIC FAILURES HIDDEN BY SUMMARY:")
    for failure in truth['specific_failures']:
        print(f"  - {failure}")
    
    print("\n📊 EXECUTION FACTS (With File Attribution):")
    for fact in truth['execution_facts']:
        print(f"\n  {fact['language'].upper()}:")
        print(f"    Status: {fact['status']}")
        print(f"    File: {Path(fact['file']).name}:{fact['line']}")
        print(f"    Duration: {fact['duration_ms']:.2f}ms")
        if 'error' in fact:
            print(f"    Error: {fact['error']}")
        if 'reason' in fact:
            print(f"    Skip Reason: {fact['reason']}")
        if fact.get('files_generated'):
            print(f"    Files Generated: {fact.get('files_generated')}")
            if fact.get('files_expected'):
                print(f"    Files Expected: {fact.get('files_expected')}")
    
    print("\n🎭 THE LIE EXPOSED:")
    print("-" * 40)
    print("Summary claimed: ✅ All 5 languages succeeded")
    print(f"Reality: ❌ Only {truth['actually_succeeded']}/5 fully succeeded")
    print(f"Hidden truth: {truth['failed_with_errors']} errors, {truth['skipped_entirely']} skipped, {truth['partial_success']} incomplete")
    
    # Calculate trust score
    trust_score = truth['actually_succeeded'] / truth['total_languages_attempted']
    print(f"\n📈 TRUST SCORE: {trust_score:.1%} (based on actual success rate)")
    
    print("\n💡 CONCLUSION:")
    print("The summary presents a false narrative of complete success.")
    print("Only the spans reveal the true state of the system.")
    print("Without spans, these failures would remain hidden.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    compare_summary_to_truth()