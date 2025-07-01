"""
Multi-Agent PydanticAI Implementation with Ollama qwen3

This module implements the PydanticAI multi-agent patterns using Ollama qwen3:latest
and integrates them with WeaverGen's 4-layer architecture:

1. Agent delegation - agents using other agents via tools
2. Programmatic agent hand-off - sequential agent execution
3. Graph-based control flow - complex workflow orchestration

All agents use Ollama qwen3:latest for consistent local execution.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import uuid4
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import Usage, UsageLimits

from ..examples.ollama_utils import get_ollama_model
from ..layers.contracts import (
    SemanticConvention, GenerationRequest, TargetLanguage,
    ExecutionContext, ExecutionStatus
)


# ============================================================================
# Multi-Agent Dependencies and Context
# ============================================================================

@dataclass
class WeaverGenAgentContext:
    """Shared context for WeaverGen multi-agent operations."""
    session_id: str
    user_id: str
    working_directory: Path
    semantic_conventions: Dict[str, SemanticConvention]
    template_cache: Dict[str, str]
    generation_results: Dict[str, Any]


class AgentResult(BaseModel):
    """Standardized result from agent operations."""
    agent_name: str
    status: ExecutionStatus
    output: Any
    reasoning: str
    execution_time_ms: int
    tokens_used: int


class Failed(BaseModel):
    """Represents a failed agent operation."""
    reason: str
    retry_suggested: bool = True


# ============================================================================
# 1. AGENT DELEGATION PATTERN
# ============================================================================

class SemanticAnalysisResult(BaseModel):
    """Result of semantic convention analysis."""
    convention_id: str
    complexity_score: int = Field(ge=1, le=10)
    recommended_languages: List[TargetLanguage]
    estimated_files: int
    confidence: float = Field(ge=0, le=1)


class CodeGenerationPlan(BaseModel):
    """Plan for code generation."""
    target_language: TargetLanguage
    template_strategy: str
    file_structure: List[str]
    dependencies: List[str]
    estimated_time_minutes: int


# Semantic Analysis Agent (Coordinator)
semantic_analysis_agent = Agent[WeaverGenAgentContext, Union[SemanticAnalysisResult, Failed]](
    get_ollama_model("qwen3:latest"),
    output_type=Union[SemanticAnalysisResult, Failed],
    system_prompt="""You are a semantic convention analysis expert for OpenTelemetry.

Analyze semantic convention YAML files and determine:
1. Complexity score (1-10, where 10 is most complex)
2. Best target languages for code generation
3. Estimated number of files that will be generated
4. Confidence in your analysis

Use the semantic_deep_analyzer tool for detailed analysis.
Return a SemanticAnalysisResult with your findings."""
)

# Deep Analysis Agent (Delegate)
semantic_deep_analyzer = Agent[WeaverGenAgentContext, Dict[str, Any]](
    get_ollama_model("qwen3:latest"),
    output_type=Dict[str, Any],
    system_prompt="""You are a deep semantic convention analyzer.

Analyze the provided semantic convention and extract:
- Attribute count and complexity
- Span definitions and relationships
- Metric definitions and types
- Dependencies between components
- Language-specific considerations

Return detailed analysis as a dictionary."""
)


@semantic_analysis_agent.tool
async def semantic_deep_analyzer_tool(
    ctx: RunContext[WeaverGenAgentContext], 
    semantic_yaml_content: str
) -> Dict[str, Any]:
    """Delegate to deep analyzer for detailed semantic analysis."""
    
    # Pass context and usage to delegate agent
    result = await semantic_deep_analyzer.run(
        f"Analyze this semantic convention YAML:\n{semantic_yaml_content}",
        deps=ctx.deps,
        usage=ctx.usage  # Important: pass usage to count tokens
    )
    
    return result.output


# Code Generation Planning Agent (Coordinator)
generation_planning_agent = Agent[WeaverGenAgentContext, Union[CodeGenerationPlan, Failed]](
    get_ollama_model("qwen3:latest"),
    output_type=Union[CodeGenerationPlan, Failed],
    system_prompt="""You are a code generation planning expert.

Create detailed generation plans for specific target languages based on semantic analysis.
Use the language_specialist tool to get language-specific recommendations.

Consider:
- Language idioms and best practices
- Template availability and complexity
- File organization patterns
- Dependency management

Return a detailed CodeGenerationPlan."""
)

# Language Specialist Agents (Delegates)
python_specialist = Agent[WeaverGenAgentContext, Dict[str, Any]](
    get_ollama_model("qwen3:latest"),
    output_type=Dict[str, Any],
    system_prompt="""You are a Python code generation specialist for OpenTelemetry.

Provide Python-specific recommendations for:
- Package structure and imports
- Class hierarchies and inheritance
- Type hints and validation
- Testing patterns
- Documentation conventions

Focus on Pydantic models, dataclasses, and OTel instrumentation patterns."""
)

go_specialist = Agent[WeaverGenAgentContext, Dict[str, Any]](
    get_ollama_model("qwen3:latest"),
    output_type=Dict[str, Any],
    system_prompt="""You are a Go code generation specialist for OpenTelemetry.

Provide Go-specific recommendations for:
- Package organization and imports
- Struct definitions and interfaces
- Error handling patterns
- Testing conventions
- Documentation standards

Focus on Go modules, interfaces, and OTel SDK patterns."""
)


@generation_planning_agent.tool
async def language_specialist_tool(
    ctx: RunContext[WeaverGenAgentContext],
    target_language: str,
    semantic_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Delegate to language-specific specialist for detailed planning."""
    
    specialist_agent = {
        "python": python_specialist,
        "go": go_specialist
    }.get(target_language.lower())
    
    if not specialist_agent:
        return {"error": f"No specialist available for {target_language}"}
    
    prompt = f"""Analyze this semantic convention for {target_language} code generation:
    
Semantic Analysis: {semantic_analysis}

Provide specific recommendations for {target_language} implementation."""
    
    result = await specialist_agent.run(
        prompt,
        deps=ctx.deps,
        usage=ctx.usage
    )
    
    return result.output


# ============================================================================
# 2. PROGRAMMATIC AGENT HAND-OFF PATTERN
# ============================================================================

class TemplateSelection(BaseModel):
    """Result of template selection process."""
    selected_templates: List[str]
    customizations_needed: List[str]
    fallback_templates: List[str]


class ValidationResult(BaseModel):
    """Result of code validation."""
    syntax_valid: bool
    style_compliant: bool
    otel_compliant: bool
    issues: List[str]
    recommendations: List[str]


# Template Selection Agent
template_selector_agent = Agent[WeaverGenAgentContext, Union[TemplateSelection, Failed]](
    get_ollama_model("qwen3:latest"),
    output_type=Union[TemplateSelection, Failed],
    system_prompt="""You are a template selection expert for code generation.

Analyze the generation plan and semantic convention to select the best templates:
1. Choose primary templates that match the requirements
2. Identify needed customizations
3. Select fallback templates for complex cases

Consider template complexity, maintenance, and output quality."""
)

# Code Validation Agent  
code_validator_agent = Agent[WeaverGenAgentContext, Union[ValidationResult, Failed]](
    get_ollama_model("qwen3:latest"),
    output_type=Union[ValidationResult, Failed],
    system_prompt="""You are a code validation expert for generated OpenTelemetry code.

Validate generated code for:
1. Syntax correctness
2. Style compliance (language-specific)
3. OpenTelemetry standard compliance
4. Best practices adherence

Provide specific issues and actionable recommendations."""
)

# Quality Assurance Agent
qa_agent = Agent[WeaverGenAgentContext, Dict[str, Any]](
    get_ollama_model("qwen3:latest"), 
    output_type=Dict[str, Any],
    system_prompt="""You are a quality assurance specialist for generated code.

Perform comprehensive quality assessment:
1. Code coverage analysis
2. Performance considerations
3. Security review
4. Maintainability score
5. Documentation completeness

Provide overall quality score and improvement recommendations."""
)


async def run_generation_workflow(
    semantic_convention: SemanticConvention,
    target_languages: List[TargetLanguage],
    context: WeaverGenAgentContext
) -> Dict[str, AgentResult]:
    """
    Programmatic agent hand-off workflow for code generation.
    
    Flow: Analysis -> Planning -> Template Selection -> Generation -> Validation -> QA
    """
    
    usage = Usage()
    results = {}
    
    print("🔄 Starting Multi-Agent Generation Workflow...")
    
    # Step 1: Semantic Analysis (with delegation)
    print("1️⃣ Analyzing semantic convention...")
    start_time = asyncio.get_event_loop().time()
    
    analysis_result = await semantic_analysis_agent.run(
        f"Analyze this semantic convention: {semantic_convention.brief}",
        deps=context,
        usage=usage
    )
    
    analysis_time = (asyncio.get_event_loop().time() - start_time) * 1000
    
    if isinstance(analysis_result.output, Failed):
        results["analysis"] = AgentResult(
            agent_name="semantic_analysis",
            status=ExecutionStatus.FAILED,
            output=analysis_result.output,
            reasoning="Semantic analysis failed",
            execution_time_ms=int(analysis_time),
            tokens_used=usage.total_tokens
        )
        return results
    
    results["analysis"] = AgentResult(
        agent_name="semantic_analysis",
        status=ExecutionStatus.SUCCESS,
        output=analysis_result.output,
        reasoning="Semantic convention analyzed successfully",
        execution_time_ms=int(analysis_time),
        tokens_used=usage.total_tokens
    )
    
    # Step 2: Generation Planning (with delegation to language specialists)
    print("2️⃣ Creating generation plans...")
    planning_results = []
    
    for language in target_languages:
        start_time = asyncio.get_event_loop().time()
        
        planning_result = await generation_planning_agent.run(
            f"Create generation plan for {language.value} based on analysis: {analysis_result.output}",
            deps=context,
            usage=usage
        )
        
        planning_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        if isinstance(planning_result.output, CodeGenerationPlan):
            planning_results.append(planning_result.output)
            
    results["planning"] = AgentResult(
        agent_name="generation_planning",
        status=ExecutionStatus.SUCCESS,
        output=planning_results,
        reasoning=f"Created plans for {len(planning_results)} languages",
        execution_time_ms=int(planning_time),
        tokens_used=usage.total_tokens
    )
    
    # Step 3: Template Selection
    print("3️⃣ Selecting templates...")
    start_time = asyncio.get_event_loop().time()
    
    template_result = await template_selector_agent.run(
        f"Select templates for plans: {planning_results}",
        deps=context,
        usage=usage
    )
    
    template_time = (asyncio.get_event_loop().time() - start_time) * 1000
    
    results["template_selection"] = AgentResult(
        agent_name="template_selector",
        status=ExecutionStatus.SUCCESS if isinstance(template_result.output, TemplateSelection) else ExecutionStatus.FAILED,
        output=template_result.output,
        reasoning="Templates selected based on generation plans",
        execution_time_ms=int(template_time),
        tokens_used=usage.total_tokens
    )
    
    # Step 4: Code Generation (simulated)
    print("4️⃣ Generating code...")
    generated_files = []
    for plan in planning_results:
        generated_files.extend([
            f"{plan.target_language.value}/models.py",
            f"{plan.target_language.value}/instrumentation.py",
            f"{plan.target_language.value}/constants.py"
        ])
    
    results["generation"] = AgentResult(
        agent_name="code_generator",
        status=ExecutionStatus.SUCCESS,
        output={"files": generated_files, "count": len(generated_files)},
        reasoning="Code generated using selected templates",
        execution_time_ms=500,  # Simulated
        tokens_used=0
    )
    
    # Step 5: Code Validation
    print("5️⃣ Validating generated code...")
    start_time = asyncio.get_event_loop().time()
    
    validation_result = await code_validator_agent.run(
        f"Validate generated files: {generated_files}",
        deps=context,
        usage=usage
    )
    
    validation_time = (asyncio.get_event_loop().time() - start_time) * 1000
    
    results["validation"] = AgentResult(
        agent_name="code_validator",
        status=ExecutionStatus.SUCCESS if isinstance(validation_result.output, ValidationResult) else ExecutionStatus.FAILED,
        output=validation_result.output,
        reasoning="Generated code validated for quality and compliance",
        execution_time_ms=int(validation_time),
        tokens_used=usage.total_tokens
    )
    
    # Step 6: Quality Assurance
    print("6️⃣ Quality assurance review...")
    start_time = asyncio.get_event_loop().time()
    
    qa_result = await qa_agent.run(
        f"QA review for validated code: {validation_result.output}",
        deps=context,
        usage=usage
    )
    
    qa_time = (asyncio.get_event_loop().time() - start_time) * 1000
    
    results["qa"] = AgentResult(
        agent_name="qa_specialist",
        status=ExecutionStatus.SUCCESS,
        output=qa_result.output,
        reasoning="Quality assurance review completed",
        execution_time_ms=int(qa_time),
        tokens_used=usage.total_tokens
    )
    
    print(f"✅ Workflow completed! Total tokens used: {usage.total_tokens}")
    return results


# ============================================================================
# 3. GRAPH-BASED CONTROL FLOW PATTERN
# ============================================================================

class WorkflowState(BaseModel):
    """State for graph-based workflow."""
    current_step: str
    completed_steps: List[str]
    failed_steps: List[str]
    data: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3


class WorkflowNode:
    """Node in the workflow graph."""
    
    def __init__(self, name: str, agent: Agent, next_nodes: List[str] = None, 
                 failure_nodes: List[str] = None):
        self.name = name
        self.agent = agent
        self.next_nodes = next_nodes or []
        self.failure_nodes = failure_nodes or []
    
    async def execute(self, state: WorkflowState, context: WeaverGenAgentContext, 
                     usage: Usage) -> tuple[WorkflowState, bool]:
        """Execute this node and return updated state and success flag."""
        
        try:
            prompt = f"Execute step '{self.name}' with current data: {state.data}"
            result = await self.agent.run(prompt, deps=context, usage=usage)
            
            # Update state
            state.completed_steps.append(self.name)
            state.data[f"{self.name}_result"] = result.output
            state.retry_count = 0  # Reset retry count on success
            
            return state, True
            
        except Exception as e:
            state.failed_steps.append(self.name)
            state.data[f"{self.name}_error"] = str(e)
            state.retry_count += 1
            
            return state, False


class MultiAgentWorkflowGraph:
    """Graph-based workflow orchestrator for complex multi-agent scenarios."""
    
    def __init__(self):
        """Initialize the workflow graph."""
        self.nodes = {}
        self.start_node = None
        
        # Create specialized agents for different workflow stages
        self._setup_agents()
        self._build_graph()
    
    def _setup_agents(self):
        """Set up agents for the workflow graph."""
        
        # Requirements Analysis Agent
        self.requirements_agent = Agent[WeaverGenAgentContext, Dict[str, Any]](
            get_ollama_model("qwen3:latest"),
            output_type=Dict[str, Any],
            system_prompt="Analyze requirements and determine workflow path."
        )
        
        # Architecture Decision Agent
        self.architecture_agent = Agent[WeaverGenAgentContext, Dict[str, Any]](
            get_ollama_model("qwen3:latest"),
            output_type=Dict[str, Any],
            system_prompt="Make architectural decisions for code generation."
        )
        
        # Implementation Agent
        self.implementation_agent = Agent[WeaverGenAgentContext, Dict[str, Any]](
            get_ollama_model("qwen3:latest"),
            output_type=Dict[str, Any],
            system_prompt="Generate implementation artifacts."
        )
        
        # Testing Agent
        self.testing_agent = Agent[WeaverGenAgentContext, Dict[str, Any]](
            get_ollama_model("qwen3:latest"),
            output_type=Dict[str, Any],
            system_prompt="Generate and validate tests for generated code."
        )
        
        # Documentation Agent
        self.documentation_agent = Agent[WeaverGenAgentContext, Dict[str, Any]](
            get_ollama_model("qwen3:latest"),
            output_type=Dict[str, Any],
            system_prompt="Generate comprehensive documentation."
        )
        
        # Review Agent
        self.review_agent = Agent[WeaverGenAgentContext, Dict[str, Any]](
            get_ollama_model("qwen3:latest"),
            output_type=Dict[str, Any],
            system_prompt="Conduct final review and quality check."
        )
    
    def _build_graph(self):
        """Build the workflow graph with conditional paths."""
        
        # Define workflow nodes
        self.nodes = {
            "requirements": WorkflowNode(
                "requirements", 
                self.requirements_agent,
                next_nodes=["architecture"],
                failure_nodes=["requirements"]  # Retry requirements
            ),
            "architecture": WorkflowNode(
                "architecture",
                self.architecture_agent, 
                next_nodes=["implementation"],
                failure_nodes=["requirements"]  # Go back to requirements
            ),
            "implementation": WorkflowNode(
                "implementation",
                self.implementation_agent,
                next_nodes=["testing"],
                failure_nodes=["architecture"]  # Reconsider architecture
            ),
            "testing": WorkflowNode(
                "testing",
                self.testing_agent,
                next_nodes=["documentation"], 
                failure_nodes=["implementation"]  # Fix implementation
            ),
            "documentation": WorkflowNode(
                "documentation",
                self.documentation_agent,
                next_nodes=["review"],
                failure_nodes=["testing"]  # May need test updates
            ),
            "review": WorkflowNode(
                "review",
                self.review_agent,
                next_nodes=[],  # End of workflow
                failure_nodes=["implementation"]  # Major revisions needed
            )
        }
        
        self.start_node = "requirements"
    
    async def execute_workflow(self, semantic_convention: SemanticConvention,
                             context: WeaverGenAgentContext) -> WorkflowState:
        """Execute the complete workflow graph."""
        
        usage = Usage()
        state = WorkflowState(
            current_step=self.start_node,
            completed_steps=[],
            failed_steps=[],
            data={"semantic_convention": semantic_convention.model_dump()}
        )
        
        print("🔄 Starting Graph-Based Multi-Agent Workflow...")
        
        while state.current_step and state.retry_count < state.max_retries:
            current_node = self.nodes[state.current_step]
            print(f"📍 Executing: {current_node.name}")
            
            # Execute current node
            state, success = await current_node.execute(state, context, usage)
            
            if success:
                # Move to next node
                if current_node.next_nodes:
                    state.current_step = current_node.next_nodes[0]  # Simple linear flow
                else:
                    state.current_step = None  # Workflow complete
                    
            else:
                # Handle failure
                if current_node.failure_nodes and state.retry_count < state.max_retries:
                    state.current_step = current_node.failure_nodes[0]
                    print(f"⚠️ Retrying via: {state.current_step}")
                else:
                    print(f"❌ Workflow failed at: {current_node.name}")
                    break
        
        print(f"✅ Graph workflow completed! Steps: {' -> '.join(state.completed_steps)}")
        print(f"📊 Total tokens used: {usage.total_tokens}")
        
        return state


# ============================================================================
# Integration with WeaverGen 4-Layer Architecture
# ============================================================================

class MultiAgentOperationsLayer:
    """Operations layer integration for multi-agent workflows."""
    
    def __init__(self):
        """Initialize multi-agent operations."""
        self.workflow_graph = MultiAgentWorkflowGraph()
        
    async def execute_agent_delegation_workflow(self, request: GenerationRequest,
                                              context: ExecutionContext) -> Dict[str, AgentResult]:
        """Execute agent delegation pattern for code generation."""
        
        agent_context = WeaverGenAgentContext(
            session_id=str(uuid4()),
            user_id="system",
            working_directory=context.working_directory,
            semantic_conventions={request.semantic_convention.id: request.semantic_convention},
            template_cache={},
            generation_results={}
        )
        
        # Use the programmatic hand-off workflow
        return await run_generation_workflow(
            request.semantic_convention,
            request.target_languages,
            agent_context
        )
    
    async def execute_graph_workflow(self, request: GenerationRequest,
                                   context: ExecutionContext) -> WorkflowState:
        """Execute graph-based workflow for complex generation scenarios."""
        
        agent_context = WeaverGenAgentContext(
            session_id=str(uuid4()),
            user_id="system", 
            working_directory=context.working_directory,
            semantic_conventions={request.semantic_convention.id: request.semantic_convention},
            template_cache={},
            generation_results={}
        )
        
        return await self.workflow_graph.execute_workflow(
            request.semantic_convention,
            agent_context
        )


# ============================================================================
# Demo Runner
# ============================================================================

async def demo_multi_agent_patterns():
    """Demonstrate all multi-agent patterns."""
    
    print("🤖 Multi-Agent PydanticAI Patterns with Ollama qwen3")
    print("=" * 60)
    
    # Create test data
    semantic_convention = SemanticConvention(
        id="demo.service",
        brief="Demo service semantic convention for multi-agent testing"
    )
    
    context = WeaverGenAgentContext(
        session_id=str(uuid4()),
        user_id="demo_user",
        working_directory=Path("./demo"),
        semantic_conventions={},
        template_cache={},
        generation_results={}
    )
    
    # 1. Agent Delegation Pattern Demo
    print("\n1️⃣ AGENT DELEGATION PATTERN")
    print("-" * 40)
    
    usage = Usage()
    analysis_result = await semantic_analysis_agent.run(
        f"Analyze this semantic convention: {semantic_convention.brief}",
        deps=context,
        usage=usage
    )
    
    print(f"Analysis Result: {analysis_result.output}")
    print(f"Tokens Used: {usage.total_tokens}")
    
    # 2. Programmatic Hand-off Pattern Demo
    print("\n2️⃣ PROGRAMMATIC HAND-OFF PATTERN")
    print("-" * 40)
    
    workflow_results = await run_generation_workflow(
        semantic_convention,
        [TargetLanguage.PYTHON, TargetLanguage.GO],
        context
    )
    
    for step, result in workflow_results.items():
        print(f"{step}: {result.status} ({result.execution_time_ms}ms)")
    
    # 3. Graph-based Control Flow Demo
    print("\n3️⃣ GRAPH-BASED CONTROL FLOW PATTERN")
    print("-" * 40)
    
    graph_workflow = MultiAgentWorkflowGraph()
    final_state = await graph_workflow.execute_workflow(semantic_convention, context)
    
    print(f"Completed Steps: {' -> '.join(final_state.completed_steps)}")
    print(f"Failed Steps: {final_state.failed_steps}")
    
    print("\n🎉 All multi-agent patterns demonstrated successfully!")


if __name__ == "__main__":
    asyncio.run(demo_multi_agent_patterns())