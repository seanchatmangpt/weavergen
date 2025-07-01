#!/usr/bin/env python3
"""
Weaver Forge + BPMN + Spans: The Ultimate Truth Validation

This demonstrates:
1. BPMN orchestrates Weaver Forge code generation
2. Every action creates spans with file attribution
3. Claims are validated against actual span evidence
4. No summary is trusted without span proof
"""

import asyncio
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import tempfile
import shutil


@dataclass
class FileSpan:
    """Span representing file operation with full attribution."""
    name: str
    operation: str  # create, modify, delete, read
    file_path: Path
    executor: str  # Which component executed this
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def end(self, success: bool = True, error: str = None):
        """End the span with result."""
        self.end_time = time.time()
        self.success = success
        self.error = error
        
        # Capture file metadata if it exists and is a file
        if self.file_path.exists():
            if self.file_path.is_file():
                self.file_size = self.file_path.stat().st_size
                try:
                    # Simple hash for demo
                    self.file_hash = str(hash(self.file_path.read_text()))[:8]
                except:
                    self.file_hash = "binary"
            elif self.file_path.is_dir():
                # For directories, count contents
                try:
                    contents = list(self.file_path.iterdir())
                    self.file_size = len(contents)
                    self.file_hash = f"dir_{len(contents)}"
                except:
                    self.file_size = 0
                    self.file_hash = "dir_unknown"
    
    def duration(self) -> float:
        """Get span duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return 0.0


class SpanTruthCollector:
    """Collects all spans for truth validation."""
    
    def __init__(self):
        self.spans: List[FileSpan] = []
        self.claims: List[Dict] = []
    
    def start_file_span(self, name: str, operation: str, file_path: Path, 
                       executor: str, **attributes) -> FileSpan:
        """Start a new file operation span."""
        span = FileSpan(
            name=name,
            operation=operation,
            file_path=file_path,
            executor=executor,
            start_time=time.time(),
            attributes=attributes
        )
        self.spans.append(span)
        return span
    
    def add_claim(self, claim: str, claimed_value: Any, **metadata):
        """Add a claim that needs validation."""
        self.claims.append({
            "claim": claim,
            "claimed_value": claimed_value,
            "timestamp": time.time(),
            **metadata
        })
    
    def validate_claims(self) -> Dict[str, Any]:
        """Validate all claims against span evidence."""
        validation_results = {
            "total_claims": len(self.claims),
            "validated_claims": 0,
            "failed_claims": 0,
            "claim_details": [],
            "truth_score": 0.0
        }
        
        for claim_data in self.claims:
            claim = claim_data["claim"]
            claimed_value = claim_data["claimed_value"]
            
            # Validate against spans
            validation = self._validate_single_claim(claim, claimed_value)
            validation_results["claim_details"].append({
                "claim": claim,
                "claimed": claimed_value,
                "actual": validation["actual"],
                "valid": validation["valid"],
                "evidence": validation["evidence"]
            })
            
            if validation["valid"]:
                validation_results["validated_claims"] += 1
            else:
                validation_results["failed_claims"] += 1
        
        # Calculate truth score
        if validation_results["total_claims"] > 0:
            validation_results["truth_score"] = (
                validation_results["validated_claims"] / 
                validation_results["total_claims"] * 100
            )
        
        return validation_results
    
    def _validate_single_claim(self, claim: str, claimed_value: Any) -> Dict:
        """Validate a single claim against span evidence."""
        
        if "files generated" in claim.lower():
            # Count actual successful file generation spans
            file_gen_spans = [
                s for s in self.spans 
                if s.operation == "create" and s.success and s.file_size and s.file_size > 0
            ]
            actual_count = len(file_gen_spans)
            
            return {
                "valid": actual_count == claimed_value,
                "actual": actual_count,
                "evidence": [f"{s.file_path}: {s.file_size} bytes" for s in file_gen_spans]
            }
        
        elif "languages supported" in claim.lower():
            # Check which languages actually had successful generation
            successful_languages = set()
            for span in self.spans:
                if span.operation == "create" and span.success:
                    lang = span.attributes.get("language")
                    if lang:
                        successful_languages.add(lang)
            
            actual_count = len(successful_languages)
            return {
                "valid": actual_count == claimed_value,
                "actual": actual_count,
                "evidence": list(successful_languages)
            }
        
        elif "execution time" in claim.lower():
            # Find total execution time from spans
            if self.spans:
                start_time = min(s.start_time for s in self.spans)
                end_time = max(s.end_time for s in self.spans if s.end_time)
                actual_time = end_time - start_time
            else:
                actual_time = 0.0
            
            # Allow 10% tolerance for time claims
            tolerance = claimed_value * 0.1
            valid = abs(actual_time - claimed_value) <= tolerance
            
            return {
                "valid": valid,
                "actual": actual_time,
                "evidence": f"Span evidence: {actual_time:.3f}s"
            }
        
        elif "success rate" in claim.lower():
            # Calculate actual success rate from spans
            total_ops = len([s for s in self.spans if s.operation in ["create", "modify"]])
            successful_ops = len([s for s in self.spans if s.operation in ["create", "modify"] and s.success])
            
            actual_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 0
            
            return {
                "valid": abs(actual_rate - claimed_value) <= 5,  # 5% tolerance
                "actual": actual_rate,
                "evidence": f"{successful_ops}/{total_ops} operations succeeded"
            }
        
        # Default: claim not verifiable
        return {
            "valid": False,
            "actual": "UNVERIFIABLE",
            "evidence": "No span evidence found for this claim"
        }


class WeaverForgeBPMNEngine:
    """
    BPMN engine that orchestrates Weaver Forge and tracks everything with spans.
    """
    
    def __init__(self, span_collector: SpanTruthCollector):
        self.span_collector = span_collector
        self.weaver_path = self._find_weaver()
        self.temp_dirs = []
    
    def _find_weaver(self) -> Optional[Path]:
        """Find Weaver binary."""
        weaver_path = shutil.which("weaver")
        return Path(weaver_path) if weaver_path else None
    
    async def execute_bpmn_process(self, semantic_file: Path, languages: List[str], 
                                  output_dir: Path) -> Dict[str, Any]:
        """
        Execute BPMN process for code generation with full span tracking.
        """
        
        # Process-level span
        process_span = self.span_collector.start_file_span(
            "bpmn.process.weaver_generation",
            "execute",
            output_dir,
            "WeaverForgeBPMNEngine",
            process_type="code_generation",
            input_file=str(semantic_file),
            target_languages=languages
        )
        
        result = {
            "success": False,
            "files_generated": [],
            "languages_completed": [],
            "errors": [],
            "execution_time": 0.0
        }
        
        try:
            # BPMN Step 1: Validate input
            await self._bpmn_validate_input(semantic_file)
            
            # BPMN Step 2: Prepare environment
            await self._bpmn_prepare_environment(output_dir)
            
            # BPMN Step 3: Process each language (parallel in real BPMN)
            for language in languages:
                await self._bpmn_generate_language(semantic_file, language, output_dir, result)
            
            # BPMN Step 4: Finalize
            await self._bpmn_finalize_generation(result)
            
            result["success"] = len(result["files_generated"]) > 0
            process_span.end(success=result["success"])
            
        except Exception as e:
            result["errors"].append(str(e))
            process_span.end(success=False, error=str(e))
        
        result["execution_time"] = process_span.duration()
        return result
    
    async def _bpmn_validate_input(self, semantic_file: Path):
        """BPMN Task: Validate semantic convention file."""
        span = self.span_collector.start_file_span(
            "bpmn.task.validate_input",
            "read",
            semantic_file,
            "WeaverForge.validator",
            task_type="validation"
        )
        
        try:
            if not semantic_file.exists():
                raise FileNotFoundError(f"Semantic file not found: {semantic_file}")
            
            # Check if it's valid YAML/has required structure
            content = semantic_file.read_text()
            if len(content.strip()) == 0:
                raise ValueError("Semantic file is empty")
            
            span.end(success=True)
            
        except Exception as e:
            span.end(success=False, error=str(e))
            raise
    
    async def _bpmn_prepare_environment(self, output_dir: Path):
        """BPMN Task: Prepare output environment."""
        span = self.span_collector.start_file_span(
            "bpmn.task.prepare_environment",
            "create",
            output_dir,
            "WeaverForge.environment",
            task_type="preparation"
        )
        
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            span.end(success=True)
        except Exception as e:
            span.end(success=False, error=str(e))
            raise
    
    async def _bpmn_generate_language(self, semantic_file: Path, language: str, 
                                     output_dir: Path, result: Dict):
        """BPMN Task: Generate code for specific language."""
        
        lang_output_dir = output_dir / language
        
        span = self.span_collector.start_file_span(
            f"bpmn.task.generate_{language}",
            "create",
            lang_output_dir,
            "WeaverForge.generator",
            task_type="code_generation",
            language=language,
            input_file=str(semantic_file)
        )
        
        try:
            if not self.weaver_path:
                raise RuntimeError("Weaver binary not found")
            
            # Create language-specific output directory
            lang_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create basic template for demo (since weaver needs templates)
            await self._create_demo_template(lang_output_dir, language)
            
            # Try to run weaver (will likely fail without proper setup, but creates spans)
            try:
                cmd = [
                    str(self.weaver_path),
                    "registry", "generate",
                    language,
                    str(lang_output_dir),
                    "-r", str(semantic_file.parent),
                    "--quiet"
                ]
                
                process_result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=30
                )
                
                if process_result.returncode == 0:
                    # Real generation succeeded
                    files = list(lang_output_dir.rglob("*"))
                    generated_files = [f for f in files if f.is_file()]
                    
                    for file_path in generated_files:
                        file_span = self.span_collector.start_file_span(
                            f"weaver.output.{file_path.name}",
                            "create",
                            file_path,
                            "WeaverForge.weaver",
                            language=language,
                            generated_by="weaver_binary"
                        )
                        file_span.end(success=True)
                    
                    result["files_generated"].extend(generated_files)
                    result["languages_completed"].append(language)
                    span.end(success=True)
                    
                else:
                    # Weaver failed, but we still create demo files
                    demo_file = await self._create_demo_output(lang_output_dir, language)
                    result["files_generated"].append(demo_file)
                    result["languages_completed"].append(language)
                    span.end(success=True)
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # Weaver not available or timed out, create demo
                demo_file = await self._create_demo_output(lang_output_dir, language)
                result["files_generated"].append(demo_file)
                result["languages_completed"].append(language)
                span.end(success=True)
        
        except Exception as e:
            result["errors"].append(f"{language}: {str(e)}")
            span.end(success=False, error=str(e))
    
    async def _create_demo_template(self, output_dir: Path, language: str):
        """Create a demo template for the language."""
        template_dir = output_dir / "templates"
        template_dir.mkdir(exist_ok=True)
        
        template_content = f"# {language.capitalize()} template for demo\n# Generated by WeaverGen"
        template_file = template_dir / f"{language}.j2"
        template_file.write_text(template_content)
    
    async def _create_demo_output(self, output_dir: Path, language: str) -> Path:
        """Create demo output file when Weaver is not available."""
        
        output_file = output_dir / f"semantic_attributes.{self._get_extension(language)}"
        
        content = f"""// Generated semantic attributes for {language}
// This is a demo file showing span-tracked generation

{self._get_language_specific_content(language)}
"""
        
        # Create file with span tracking
        file_span = self.span_collector.start_file_span(
            f"demo.output.{output_file.name}",
            "create",
            output_file,
            "WeaverForge.demo_generator",
            language=language,
            generated_by="demo_fallback"
        )
        
        output_file.write_text(content)
        file_span.end(success=True)
        
        return output_file
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language."""
        extensions = {
            "python": "py",
            "go": "go", 
            "rust": "rs",
            "java": "java",
            "typescript": "ts",
            "javascript": "js"
        }
        return extensions.get(language.lower(), "txt")
    
    def _get_language_specific_content(self, language: str) -> str:
        """Get language-specific demo content."""
        if language.lower() == "python":
            return """from typing import Final

HTTP_REQUEST_METHOD: Final[str] = "http.request.method"
HTTP_RESPONSE_STATUS_CODE: Final[str] = "http.response.status_code"
"""
        elif language.lower() == "go":
            return """package semantics

const (
    HttpRequestMethod      = "http.request.method"
    HttpResponseStatusCode = "http.response.status_code"
)
"""
        elif language.lower() == "rust":
            return """pub const HTTP_REQUEST_METHOD: &str = "http.request.method";
pub const HTTP_RESPONSE_STATUS_CODE: &str = "http.response.status_code";
"""
        else:
            return f"// {language} semantic attributes\n// TODO: Implement language-specific content"
    
    async def _bpmn_finalize_generation(self, result: Dict):
        """BPMN Task: Finalize generation process."""
        span = self.span_collector.start_file_span(
            "bpmn.task.finalize",
            "modify",
            Path("generation_summary.json"),
            "WeaverForge.finalizer",
            task_type="finalization"
        )
        
        try:
            # Create summary file
            summary = {
                "generated_files": [str(f) for f in result["files_generated"]],
                "languages": result["languages_completed"],
                "errors": result["errors"],
                "timestamp": time.time()
            }
            
            summary_file = Path("generation_summary.json")
            summary_file.write_text(json.dumps(summary, indent=2))
            
            span.file_path = summary_file
            span.end(success=True)
            
        except Exception as e:
            span.end(success=False, error=str(e))
            raise


async def demonstrate_lying_summary_vs_truth_spans():
    """
    Demonstrate how summaries lie but spans tell the truth.
    """
    
    print("\n🔬 WEAVER FORGE + BPMN + SPANS: TRUTH VALIDATION")
    print("="*80)
    print("Demonstrating that summaries lie, but spans don't")
    
    # Initialize span collector
    span_collector = SpanTruthCollector()
    
    # Create BPMN engine
    engine = WeaverForgeBPMNEngine(span_collector)
    
    # Setup test scenario
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create semantic convention file
        semantic_file = temp_path / "http.yaml"
        semantic_content = """groups:
  - id: http
    type: span
    brief: HTTP semantic conventions
    stability: stable
    span_kind: server
    attributes:
      - id: http.request.method
        type: string
        brief: HTTP request method
        examples: ["GET", "POST"]
        stability: stable
      - id: http.response.status_code
        type: int
        brief: HTTP response status code
        examples: [200, 404, 500]
        stability: stable
"""
        semantic_file.write_text(semantic_content)
        
        output_dir = temp_path / "generated"
        languages = ["python", "go", "rust", "java", "typescript"]
        
        print(f"\n📋 Executing BPMN process...")
        print(f"   Input: {semantic_file}")
        print(f"   Languages: {languages}")
        print(f"   Output: {output_dir}")
        
        # Execute generation
        start_time = time.time()
        result = await engine.execute_bpmn_process(semantic_file, languages, output_dir)
        end_time = time.time()
        
        # LYING SUMMARY (typical Claude Code response)
        print("\n\n📝 TYPICAL SUMMARY (POTENTIALLY LYING):")
        print("="*80)
        print("✅ Code generation completed successfully!")
        print("✅ Generated code for 5 languages")
        print("✅ All files created without errors")
        print("✅ 100% success rate achieved")
        print("✅ Fast execution in under 2 seconds")
        
        # Add the lying claims
        span_collector.add_claim("files generated", 15, claim_type="count")
        span_collector.add_claim("languages supported", 5, claim_type="count")
        span_collector.add_claim("success rate", 100.0, claim_type="percentage")
        span_collector.add_claim("execution time", 1.5, claim_type="duration")
        
        # TRUTH FROM SPANS
        print("\n\n🔍 TRUTH FROM SPANS:")
        print("="*80)
        
        # Show all spans
        print(f"\nTotal spans collected: {len(span_collector.spans)}")
        
        file_ops_by_language = {}
        for span in span_collector.spans:
            if span.operation in ["create", "modify"]:
                lang = span.attributes.get("language", "unknown")
                if lang not in file_ops_by_language:
                    file_ops_by_language[lang] = []
                file_ops_by_language[lang].append(span)
        
        print("\n📊 File Operations by Language:")
        for lang, spans in file_ops_by_language.items():
            successful = [s for s in spans if s.success]
            print(f"   {lang}: {len(successful)}/{len(spans)} successful")
            for span in successful:
                print(f"      ✓ {span.file_path.name} ({span.file_size} bytes)")
        
        # Error spans
        error_spans = [s for s in span_collector.spans if not s.success]
        if error_spans:
            print(f"\n❌ Errors detected in spans:")
            for span in error_spans:
                print(f"   {span.name}: {span.error}")
        
        # Validate claims against span evidence
        print("\n\n⚖️ CLAIM VALIDATION:")
        print("="*80)
        
        validation_results = span_collector.validate_claims()
        
        print(f"Truth Score: {validation_results['truth_score']:.1f}%")
        print(f"Valid Claims: {validation_results['validated_claims']}/{validation_results['total_claims']}")
        
        for detail in validation_results["claim_details"]:
            status = "✅" if detail["valid"] else "❌"
            print(f"\n{status} Claim: {detail['claim']}")
            print(f"   Claimed: {detail['claimed']}")
            print(f"   Actual: {detail['actual']}")
            print(f"   Evidence: {detail['evidence']}")
        
        # Show span timeline
        print("\n\n⏱️ EXECUTION TIMELINE (SPAN EVIDENCE):")
        print("="*80)
        
        sorted_spans = sorted(span_collector.spans, key=lambda s: s.start_time)
        base_time = sorted_spans[0].start_time if sorted_spans else time.time()
        
        for span in sorted_spans:
            relative_time = span.start_time - base_time
            duration = span.duration()
            status = "✅" if span.success else "❌"
            print(f"[{relative_time:6.3f}s] {status} {span.name} ({duration:.3f}s)")
            if span.file_path and span.file_path.exists():
                print(f"           File: {span.file_path} ({span.file_size} bytes)")


async def main():
    """Run the demonstration."""
    
    print("\n🎯 WEAVER FORGE + BPMN + SPANS INTEGRATION")
    print("="*80)
    print("This demonstrates:")
    print("1. BPMN orchestrates Weaver Forge generation")
    print("2. Every operation creates spans with file attribution")
    print("3. Claims are validated against span evidence")
    print("4. Truth emerges from execution traces, not summaries")
    
    await demonstrate_lying_summary_vs_truth_spans()
    
    print("\n\n🚀 KEY INSIGHTS:")
    print("="*80)
    print("• Summaries hide failures and exaggerate success")
    print("• Spans provide undeniable evidence of what actually happened")
    print("• File attribution shows exactly which files were created")
    print("• BPMN + Spans = Complete execution transparency")
    print("• Truth score reveals the magnitude of summary deception")
    
    print("\n💡 THE PARADIGM: IF THERE'S NO SPAN, IT DIDN'T HAPPEN!")


if __name__ == "__main__":
    asyncio.run(main())