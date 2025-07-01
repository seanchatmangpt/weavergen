#!/usr/bin/env python3
"""
BPMN-Driven Examples - Demonstrating pure BPMN control flow.

Key principles:
1. BPMN processes control everything
2. Agents are stateless executors
3. No agent calls another agent
4. All coordination happens in BPMN
"""

import asyncio
from typing import Dict, Any
from pathlib import Path

from pydantic_ai.models.openai import OpenAIModel

from weavergen.bpmn.agent import BPMNAgent, BPMNProcessEngine, EXAMPLE_CODE_GEN_PROCESS


def get_ollama_model(model_name: str = "qwen3:latest"):
    """Get Ollama model configured for BPMN execution."""
    return OpenAIModel(
        model_name=model_name,
        base_url="http://localhost:11434/v1",
        api_key="not-needed"
    )


async def example_1_pure_bpmn_generation():
    """
    Example 1: Pure BPMN-driven code generation.
    
    The BPMN process completely controls the flow.
    Agents only execute when the process tells them to.
    """
    print("\n=== Example 1: Pure BPMN-Driven Generation ===\n")
    
    # Create process engine
    engine = BPMNProcessEngine()
    
    # Register specialized agents for each task type
    engine.register_agent("validator", BPMNAgent(
        get_ollama_model(),
        system_prompt="You are a semantic convention validator. Check for completeness and correctness."
    ))
    
    engine.register_agent("analyzer", BPMNAgent(
        get_ollama_model(),
        system_prompt="You are a semantic structure analyzer. Identify patterns and appropriate data structures."
    ))
    
    engine.register_agent("python_generator", BPMNAgent(
        get_ollama_model(),
        system_prompt="You are a Python code generator. Generate idiomatic Python code."
    ))
    
    engine.register_agent("go_generator", BPMNAgent(
        get_ollama_model(),
        system_prompt="You are a Go code generator. Generate idiomatic Go code."
    ))
    
    engine.register_agent("rust_generator", BPMNAgent(
        get_ollama_model(),
        system_prompt="You are a Rust code generator. Generate idiomatic Rust code."
    ))
    
    engine.register_agent("code_validator", BPMNAgent(
        get_ollama_model(),
        system_prompt="You are a code quality validator. Check syntax, conventions, and documentation."
    ))
    
    # Load the BPMN process
    engine.load_process("code_generation", EXAMPLE_CODE_GEN_PROCESS)
    
    # Execute with initial data
    initial_data = {
        "semantic_convention": {
            "id": "http.server",
            "type": "span",
            "attributes": [
                {
                    "id": "http.request.method",
                    "type": "string",
                    "brief": "HTTP request method",
                    "examples": ["GET", "POST", "PUT"]
                },
                {
                    "id": "http.response.status_code",
                    "type": "int",
                    "brief": "HTTP response status code",
                    "examples": [200, 404, 500]
                }
            ]
        }
    }
    
    # Execute the process - BPMN controls everything
    result = await engine.execute_process("code_generation", initial_data)
    
    print(f"Process completed: {result.instance_id}")
    print(f"Execution path: {' -> '.join(result.execution_path)}")
    print(f"\nGenerated code stored in context:")
    for key, value in result.variables.items():
        if key.endswith("_code"):
            print(f"\n{key}:")
            print(value)


async def example_2_event_driven_bpmn():
    """
    Example 2: Event-driven BPMN process.
    
    Shows how BPMN can react to events and control flow dynamically.
    """
    print("\n=== Example 2: Event-Driven BPMN ===\n")
    
    # Define event-driven process
    event_process = {
        "id": "EventDrivenGeneration",
        "elements": [
            {
                "id": "start",
                "type": "startEvent",
                "name": "Start Generation"
            },
            {
                "id": "waitForChange",
                "type": "intermediateCatchEvent",
                "name": "Wait for Schema Change",
                "eventType": "message",
                "messageRef": "schemaChanged"
            },
            {
                "id": "analyzeChange",
                "type": "serviceTask",
                "name": "Analyze What Changed",
                "agent": "change_analyzer",
                "documentation": "Determine what parts of the schema changed and what needs regeneration"
            },
            {
                "id": "selectiveGeneration",
                "type": "serviceTask",
                "name": "Regenerate Affected Code",
                "agent": "selective_generator",
                "documentation": "Only regenerate code for the parts that changed"
            },
            {
                "id": "notify",
                "type": "sendTask",
                "name": "Notify Completion",
                "message": "Code regeneration complete"
            },
            {
                "id": "end",
                "type": "endEvent",
                "name": "Generation Complete"
            }
        ],
        "flows": [
            {"sourceRef": "start", "targetRef": "waitForChange"},
            {"sourceRef": "waitForChange", "targetRef": "analyzeChange"},
            {"sourceRef": "analyzeChange", "targetRef": "selectiveGeneration"},
            {"sourceRef": "selectiveGeneration", "targetRef": "notify"},
            {"sourceRef": "notify", "targetRef": "end"}
        ]
    }
    
    engine = BPMNProcessEngine()
    
    # Register event-aware agents
    engine.register_agent("change_analyzer", BPMNAgent(
        get_ollama_model(),
        system_prompt="Analyze schema changes and determine impact on generated code."
    ))
    
    engine.register_agent("selective_generator", BPMNAgent(
        get_ollama_model(),
        system_prompt="Generate only the code affected by schema changes."
    ))
    
    engine.load_process("event_driven", event_process)
    
    # Simulate execution (simplified)
    print("Event-driven process loaded and waiting for schema changes...")
    print("BPMN process controls when regeneration happens")


async def example_3_hierarchical_bpmn():
    """
    Example 3: Hierarchical BPMN with subprocesses.
    
    Shows how complex generation can be decomposed into BPMN subprocesses.
    """
    print("\n=== Example 3: Hierarchical BPMN ===\n")
    
    # Define process with subprocesses
    hierarchical_process = {
        "id": "HierarchicalGeneration",
        "elements": [
            {
                "id": "start",
                "type": "startEvent",
                "name": "Start"
            },
            {
                "id": "generateModels",
                "type": "callActivity",
                "name": "Generate Data Models",
                "calledElement": "ModelGenerationSubprocess",
                "documentation": "Subprocess for generating data models"
            },
            {
                "id": "generateAPIs",
                "type": "callActivity", 
                "name": "Generate API Interfaces",
                "calledElement": "APIGenerationSubprocess",
                "documentation": "Subprocess for generating API interfaces"
            },
            {
                "id": "generateTests",
                "type": "callActivity",
                "name": "Generate Test Cases",
                "calledElement": "TestGenerationSubprocess",
                "documentation": "Subprocess for generating tests"
            },
            {
                "id": "end",
                "type": "endEvent",
                "name": "Complete"
            }
        ],
        "flows": [
            {"sourceRef": "start", "targetRef": "generateModels"},
            {"sourceRef": "generateModels", "targetRef": "generateAPIs"},
            {"sourceRef": "generateAPIs", "targetRef": "generateTests"},
            {"sourceRef": "generateTests", "targetRef": "end"}
        ]
    }
    
    # Model generation subprocess
    model_subprocess = {
        "id": "ModelGenerationSubprocess",
        "elements": [
            {
                "id": "model_start",
                "type": "startEvent"
            },
            {
                "id": "identifyEntities",
                "type": "serviceTask",
                "name": "Identify Entities",
                "agent": "entity_identifier",
                "documentation": "Identify data entities from semantic conventions"
            },
            {
                "id": "generateClasses",
                "type": "serviceTask",
                "name": "Generate Model Classes",
                "agent": "model_generator",
                "documentation": "Generate data model classes"
            },
            {
                "id": "model_end",
                "type": "endEvent"
            }
        ],
        "flows": [
            {"sourceRef": "model_start", "targetRef": "identifyEntities"},
            {"sourceRef": "identifyEntities", "targetRef": "generateClasses"},
            {"sourceRef": "generateClasses", "targetRef": "model_end"}
        ]
    }
    
    print("Hierarchical BPMN structure:")
    print("Main Process")
    print("  ├── Model Generation Subprocess")
    print("  │   ├── Identify Entities (Agent Task)")
    print("  │   └── Generate Classes (Agent Task)")
    print("  ├── API Generation Subprocess")
    print("  └── Test Generation Subprocess")
    print("\nBPMN orchestrates at every level - agents never call each other")


async def example_4_decision_based_bpmn():
    """
    Example 4: Decision-based BPMN flow.
    
    Shows how BPMN makes all routing decisions, not agents.
    """
    print("\n=== Example 4: Decision-Based BPMN ===\n")
    
    decision_process = {
        "id": "DecisionBasedGeneration",
        "elements": [
            {
                "id": "start",
                "type": "startEvent"
            },
            {
                "id": "analyzeComplexity",
                "type": "serviceTask",
                "name": "Analyze Schema Complexity",
                "agent": "complexity_analyzer",
                "documentation": "Determine complexity level of semantic convention",
                "outputVariable": "complexity_level"
            },
            {
                "id": "complexityGateway",
                "type": "exclusiveGateway",
                "name": "Complexity Level?",
                "conditions": [
                    {
                        "expression": "complexity_level == 'simple'",
                        "targetRef": "simpleGeneration"
                    },
                    {
                        "expression": "complexity_level == 'moderate'",
                        "targetRef": "moderateGeneration"
                    },
                    {
                        "expression": "complexity_level == 'complex'",
                        "targetRef": "complexGeneration"
                    }
                ]
            },
            {
                "id": "simpleGeneration",
                "type": "serviceTask",
                "name": "Simple Generation",
                "agent": "simple_generator",
                "documentation": "Generate code using simple templates"
            },
            {
                "id": "moderateGeneration",
                "type": "serviceTask",
                "name": "Moderate Generation",
                "agent": "moderate_generator",
                "documentation": "Generate code with advanced patterns"
            },
            {
                "id": "complexGeneration",
                "type": "serviceTask",
                "name": "Complex Generation",
                "agent": "complex_generator",
                "documentation": "Generate code with full architecture"
            },
            {
                "id": "mergeGateway",
                "type": "exclusiveGateway",
                "name": "Merge Paths"
            },
            {
                "id": "end",
                "type": "endEvent"
            }
        ],
        "flows": [
            {"sourceRef": "start", "targetRef": "analyzeComplexity"},
            {"sourceRef": "analyzeComplexity", "targetRef": "complexityGateway"},
            {"sourceRef": "simpleGeneration", "targetRef": "mergeGateway"},
            {"sourceRef": "moderateGeneration", "targetRef": "mergeGateway"},
            {"sourceRef": "complexGeneration", "targetRef": "mergeGateway"},
            {"sourceRef": "mergeGateway", "targetRef": "end"}
        ]
    }
    
    print("BPMN makes all decisions based on data:")
    print("1. Agent analyzes complexity → returns data")
    print("2. BPMN gateway evaluates data → chooses path")
    print("3. Appropriate agent executes → returns result")
    print("4. BPMN continues flow")
    print("\nAgents NEVER decide what happens next - BPMN does")


async def example_5_self_modifying_bpmn():
    """
    Example 5: Self-modifying BPMN process.
    
    Shows how BPMN processes can generate other BPMN processes.
    """
    print("\n=== Example 5: Self-Modifying BPMN ===\n")
    
    meta_process = {
        "id": "BPMNGeneratorProcess",
        "elements": [
            {
                "id": "start",
                "type": "startEvent",
                "name": "Receive Requirements"
            },
            {
                "id": "analyzeRequirements",
                "type": "serviceTask",
                "name": "Analyze Generation Requirements",
                "agent": "requirements_analyzer",
                "documentation": "Understand what kind of code generation is needed"
            },
            {
                "id": "designProcess",
                "type": "serviceTask",
                "name": "Design BPMN Process",
                "agent": "bpmn_designer",
                "documentation": "Design a BPMN process for the specific generation needs",
                "outputVariable": "new_bpmn_process"
            },
            {
                "id": "validateProcess",
                "type": "serviceTask",
                "name": "Validate BPMN Process",
                "agent": "bpmn_validator",
                "documentation": "Ensure the generated BPMN process is valid and complete"
            },
            {
                "id": "deployProcess",
                "type": "serviceTask",
                "name": "Deploy New Process",
                "agent": "process_deployer",
                "documentation": "Deploy the new BPMN process for execution"
            },
            {
                "id": "end",
                "type": "endEvent",
                "name": "Process Deployed"
            }
        ],
        "flows": [
            {"sourceRef": "start", "targetRef": "analyzeRequirements"},
            {"sourceRef": "analyzeRequirements", "targetRef": "designProcess"},
            {"sourceRef": "designProcess", "targetRef": "validateProcess"},
            {"sourceRef": "validateProcess", "targetRef": "deployProcess"},
            {"sourceRef": "deployProcess", "targetRef": "end"}
        ]
    }
    
    print("Self-modifying BPMN flow:")
    print("1. BPMN process receives requirements")
    print("2. Agent analyzes what's needed")
    print("3. Agent designs new BPMN process")
    print("4. Agent validates the design")
    print("5. BPMN deploys itself!")
    print("\nThe ultimate recursion: BPMN processes creating BPMN processes")


async def main():
    """Run all BPMN-driven examples."""
    
    print("\n" + "="*60)
    print("BPMN-DRIVEN WEAVERGEN EXAMPLES")
    print("="*60)
    print("\nKey Principles:")
    print("• BPMN processes control ALL flow")
    print("• Agents are stateless task executors")
    print("• No agent-to-agent communication")
    print("• All coordination through BPMN")
    
    # Run examples
    try:
        # Example 1 is fully implemented
        await example_1_pure_bpmn_generation()
    except Exception as e:
        print(f"Example 1 error: {e}")
    
    # Other examples show concepts
    await example_2_event_driven_bpmn()
    await example_3_hierarchical_bpmn()
    await example_4_decision_based_bpmn()
    await example_5_self_modifying_bpmn()
    
    print("\n" + "="*60)
    print("BPMN-first architecture: Processes control, agents execute")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())