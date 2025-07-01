"""
Micro BPMN Demo: 80/20 BPMN Implementation in Action
====================================================

This demo shows how the 80/20 principle transforms BPMN from complex XML 
to simple Python decorators, providing the same workflow capabilities 
with 90% less complexity.

Comparison:
- Traditional BPMN: XML files, complex parsers, heavyweight engines
- Micro BPMN: Python decorators, 100-line engine, immediate execution
"""

import asyncio
import time
from pathlib import Path
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from weavergen.micro_bpmn import (
    bpmn_process, service_task, exclusive_gateway, parallel_gateway,
    semantic_span, BPMNContext, MicroBPMNEngine, ProcessBuilder,
    register_process, execute_process
)

# ============================================================================
# Example 1: WeaverGen Orchestration (Replaces 463 lines with 30)
# ============================================================================

@bpmn_process("weavergen_orchestration")
class WeaverGenOrchestration:
    """Main WeaverGen workflow - semantic convention to generated code"""
    
    @service_task
    @semantic_span("bpmn", "load_semantics")
    def load_semantics(self, ctx: BPMNContext) -> dict:
        """Load semantic conventions"""
        semantic_file = ctx.get("semantic_file", "semantic_conventions/weavergen_system.yaml")
        
        # Simulate loading semantics
        time.sleep(0.1)  # Simulate file I/O
        
        return {
            "semantics": {
                "groups": ["weavergen.system", "weavergen.agent", "weavergen.workflow"],
                "metrics": ["generation.duration", "validation.success_rate"]
            },
            "semantic_file": semantic_file,
            "loaded_at": time.time()
        }
    
    @service_task
    @semantic_span("bpmn", "validate_semantics")
    def validate_semantics(self, ctx: BPMNContext) -> dict:
        """Validate semantic convention structure"""
        semantics = ctx.get("semantics", {})
        groups = semantics.get("groups", [])
        
        # Validation logic
        required_groups = ["weavergen.system", "weavergen.agent", "weavergen.workflow"]
        missing = [g for g in required_groups if g not in groups]
        
        valid = len(missing) == 0
        
        return {
            "semantic_valid": valid,
            "semantic_issues": [f"Missing group: {g}" for g in missing],
            "validation_completed_at": time.time()
        }
    
    @exclusive_gateway
    def is_semantic_valid(self, ctx: BPMNContext) -> bool:
        """Decision: Are semantics valid?"""
        return ctx.get("semantic_valid", False)
    
    @parallel_gateway
    async def generate_components(self, ctx: BPMNContext) -> dict:
        """Generate agents and validators in parallel"""
        
        # Simulate parallel component generation
        agent_task = asyncio.create_task(self._generate_agents(ctx))
        validator_task = asyncio.create_task(self._generate_validators(ctx))
        
        agents_result, validators_result = await asyncio.gather(agent_task, validator_task)
        
        return {
            "agents_generated": agents_result,
            "validators_generated": validators_result,
            "components_completed_at": time.time()
        }
    
    async def _generate_agents(self, ctx: BPMNContext) -> dict:
        """Generate agent classes"""
        await asyncio.sleep(0.2)  # Simulate AI generation
        return {
            "coordinator_agent": "generated",
            "analyst_agent": "generated", 
            "validator_agent": "generated"
        }
    
    async def _generate_validators(self, ctx: BPMNContext) -> dict:
        """Generate validation logic"""
        await asyncio.sleep(0.15)  # Simulate generation
        return {
            "span_validator": "generated",
            "health_scoring": "generated"
        }

# ============================================================================
# Example 2: Agent Workflow (Pure Python instead of XML)
# ============================================================================

@bpmn_process("agent_coordination")
class AgentCoordination:
    """Multi-agent coordination workflow"""
    
    @service_task
    @semantic_span("agent", "semantic_analysis")
    async def analyze_semantic_convention(self, ctx: BPMNContext) -> dict:
        """Analyze semantic convention with AI"""
        convention = ctx.get("semantic_convention", {})
        
        # Simulate AI analysis
        await asyncio.sleep(0.3)
        
        return {
            "analysis_result": {
                "complexity": "medium",
                "target_languages": ["python", "rust", "go"],
                "estimated_tokens": 1500
            },
            "analyzed_at": time.time()
        }
    
    @service_task
    @semantic_span("agent", "code_generation")
    async def generate_code(self, ctx: BPMNContext) -> dict:
        """Generate code using multi-agent system"""
        analysis = ctx.get("analysis_result", {})
        languages = analysis.get("target_languages", ["python"])
        
        # Simulate multi-agent generation
        results = {}
        for lang in languages:
            await asyncio.sleep(0.1)  # Simulate per-language generation
            results[f"{lang}_code"] = f"Generated {lang} code"
        
        return {
            "generated_code": results,
            "generation_completed_at": time.time()
        }
    
    @exclusive_gateway
    def all_languages_generated(self, ctx: BPMNContext) -> bool:
        """Check if all target languages were generated"""
        generated = ctx.get("generated_code", {})
        analysis = ctx.get("analysis_result", {})
        target_languages = analysis.get("target_languages", [])
        
        return len(generated) >= len(target_languages)

# ============================================================================
# Example 3: Fluent API for Complex Flows
# ============================================================================

def create_validation_workflow():
    """Create a validation workflow using fluent API"""
    
    def validate_syntax(self, ctx):
        time.sleep(0.05)
        return {"syntax_valid": True}
    
    def validate_semantics(self, ctx):
        time.sleep(0.08)
        return {"semantics_valid": True}
    
    def validate_performance(self, ctx):
        time.sleep(0.12)
        return {"performance_valid": True}
    
    def is_all_valid(self, ctx):
        return (ctx.get("syntax_valid", False) and 
                ctx.get("semantics_valid", False) and 
                ctx.get("performance_valid", False))
    
    # Build process using fluent API
    return (ProcessBuilder("validation_workflow")
            .service_task("validate_syntax", validate_syntax)
            .service_task("validate_semantics", validate_semantics) 
            .service_task("validate_performance", validate_performance)
            .exclusive_gateway("all_valid", is_all_valid)
            .build())

# ============================================================================
# Demo Execution and Results
# ============================================================================

async def run_demo():
    """Run the micro BPMN demo"""
    print("🚀 Micro BPMN Demo: 80/20 Implementation")
    print("=" * 50)
    
    # Create engine
    engine = MicroBPMNEngine()
    
    # Register processes
    engine.register_process(WeaverGenOrchestration)
    engine.register_process(AgentCoordination)
    
    # Register fluent API process
    validation_process = create_validation_workflow()
    engine.register_process(validation_process)
    
    print(f"📋 Registered {len(engine.processes)} processes")
    print()
    
    # Execute WeaverGen orchestration
    print("🔄 Executing WeaverGen Orchestration...")
    start_time = time.time()
    
    result1 = await engine.execute_process("weavergen_orchestration", {
        "semantic_file": "examples/demo_semantics.yaml"
    })
    
    duration1 = (time.time() - start_time) * 1000
    print(f"✅ Completed in {duration1:.1f}ms")
    print(f"   Spans generated: {len(result1.spans)}")
    print(f"   Semantic valid: {result1.get('semantic_valid')}")
    print(f"   Components: {list(result1.get('agents_generated', {}).keys())}")
    print()
    
    # Execute agent coordination
    print("🤖 Executing Agent Coordination...")
    start_time = time.time()
    
    result2 = await engine.execute_process("agent_coordination", {
        "semantic_convention": {"id": "demo.convention", "brief": "Demo convention"}
    })
    
    duration2 = (time.time() - start_time) * 1000
    print(f"✅ Completed in {duration2:.1f}ms")
    print(f"   Languages generated: {len(result2.get('generated_code', {}))}")
    print(f"   Analysis complexity: {result2.get('analysis_result', {}).get('complexity')}")
    print()
    
    # Execute fluent API workflow
    print("📋 Executing Validation Workflow (Fluent API)...")
    start_time = time.time()
    
    result3 = await engine.execute_process("validation_workflow", {})
    
    duration3 = (time.time() - start_time) * 1000
    print(f"✅ Completed in {duration3:.1f}ms")
    print(f"   All validations passed: {result3.get('all_valid_decision')}")
    print()
    
    # Show execution summary
    summary = engine.get_execution_summary()
    print("📊 Execution Summary:")
    print(f"   Total executions: {summary['executions']}")
    print(f"   Total spans: {summary['total_spans']}")
    print(f"   Success rate: {summary['success_rate']:.1%}")
    print(f"   Avg duration: {summary['avg_duration_ms']:.1f}ms")
    print()
    
    # Generate Mermaid diagrams
    print("📈 Process Diagrams:")
    for process_name in engine.processes.keys():
        print(f"\n{process_name.title()} Flow:")
        print("```mermaid")
        print(engine.generate_mermaid_diagram(process_name))
        print("```")
    
    return {
        "total_executions": summary['executions'],
        "total_duration_ms": duration1 + duration2 + duration3,
        "total_spans": summary['total_spans'],
        "processes_executed": list(engine.processes.keys())
    }

# ============================================================================
# Integration with WeaverGen System
# ============================================================================

async def integrate_with_weavergen():
    """Show integration with existing WeaverGen system"""
    print("\n🔗 Integration with WeaverGen System")
    print("=" * 40)
    
    # Register with global engine for CLI integration
    register_process(WeaverGenOrchestration)
    register_process(AgentCoordination)
    
    # Execute using global functions
    result = await execute_process("weavergen_orchestration", {
        "semantic_file": "semantic_conventions/weavergen_system.yaml",
        "output_dir": "generated_output"
    })
    
    print(f"✅ Global execution completed")
    print(f"   Context data keys: {list(result.data.keys())}")
    print(f"   Span count: {len(result.spans)}")
    
    # Show span details for observability
    print("\n📊 Observability Spans:")
    for span in result.spans[-3:]:  # Show last 3 spans
        print(f"   {span['name']}: {span['duration_ms']:.1f}ms ({span['status']})")

if __name__ == "__main__":
    # Run the demo
    demo_result = asyncio.run(run_demo())
    
    # Show 80/20 comparison
    print("\n🎯 80/20 Comparison:")
    print("=" * 30)
    print("Traditional BPMN:")
    print("  - XML files + parsers: 463+ lines")
    print("  - SpiffWorkflow dependency")
    print("  - Complex execution engine")
    print("  - Mock fallbacks needed")
    print()
    print("Micro BPMN (80/20):")
    print("  - Python decorators: ~100 lines")
    print("  - Zero external dependencies")
    print("  - Immediate execution")
    print("  - Built-in observability")
    print()
    
    asyncio.run(integrate_with_weavergen())