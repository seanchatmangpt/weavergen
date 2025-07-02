#!/usr/bin/env python3
"""
Demo script to show mermaid visualizations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from weavergen.src.visualizers.mermaid import MermaidVisualizer, MermaidLifecycleGenerator

def main():
    visualizer = MermaidVisualizer()
    lifecycle_gen = MermaidLifecycleGenerator(visualizer)
    
    print("=== WEAVERGEN V2 MERMAID VISUALIZATIONS ===\n")
    
    # 1. Semantic to Runtime Lifecycle
    print("1. SEMANTIC TO RUNTIME LIFECYCLE")
    print("-" * 40)
    semantic_lifecycle = lifecycle_gen.generate_semantic_to_runtime_lifecycle(Path("semantic.yaml"))
    print("```mermaid")
    print(semantic_lifecycle)
    print("```\n")
    
    # 2. System Architecture
    print("2. SYSTEM ARCHITECTURE")
    print("-" * 40)
    arch_data = {
        "style": "full",
        "include_flows": True,
        "components": {
            "core": ["SpiffWorkflow Engine", "Weaver Forge", "AI Agents"],
            "layers": ["Commands", "Operations", "Runtime", "Contracts"],
            "external": ["OpenTelemetry", "LLM Provider", "File System"]
        }
    }
    architecture = visualizer.generate_system_architecture_diagram(arch_data)
    print("```mermaid")
    print(architecture)
    print("```\n")
    
    # 3. Agent Communication
    print("3. AGENT COMMUNICATION FLOW")
    print("-" * 40)
    comm_data = {
        "agents": [
            {"id": "CEO", "name": "CEO Agent"},
            {"id": "CTO", "name": "CTO Agent"},
            {"id": "CPO", "name": "CPO Agent"}
        ],
        "messages": [
            {"from": "CEO", "to": "CTO", "type": "request", "content": "Validate technical approach"},
            {"from": "CEO", "to": "CPO", "type": "request", "content": "Check product requirements"},
            {"from": "CTO", "to": "CEO", "type": "decision", "content": "Approved", "duration_ms": 200},
            {"from": "CPO", "to": "CEO", "type": "decision", "content": "Needs refinement", "duration_ms": 150},
            {"from": "CEO", "to": "OTel", "type": "decision", "content": "Final: Iterate", "duration_ms": 100}
        ]
    }
    agent_comm = visualizer.generate_agent_communication_diagram(comm_data)
    print("```mermaid")
    print(agent_comm)
    print("```\n")
    
    # 4. BPMN Workflow
    print("4. BPMN WORKFLOW VISUALIZATION")
    print("-" * 40)
    workflow_data = {
        "tasks": [
            {"name": "Load Semantic Conventions", "type": "service"},
            {"name": "Parse YAML", "type": "service"},
            {"name": "Validate Schema", "type": "service"},
            {"name": "Generate Code", "type": "service"},
            {"name": "Run Validation", "type": "service"},
            {"name": "Deploy", "type": "user"}
        ],
        "gateways": [
            {"type": "exclusive", "name": "Schema Valid?"},
            {"type": "parallel", "name": "Multi-Language Gen"}
        ],
        "connections": [
            {"from": "Start", "to": "T0"},
            {"from": "T0", "to": "T1"},
            {"from": "T1", "to": "T2"},
            {"from": "T2", "to": "G0"},
            {"from": "G0", "to": "T3", "label": "Valid"},
            {"from": "G0", "to": "End", "label": "Invalid"},
            {"from": "T3", "to": "G1"},
            {"from": "G1", "to": "T4"},
            {"from": "T4", "to": "T5"},
            {"from": "T5", "to": "End"}
        ]
    }
    workflow = visualizer.generate_workflow_visualization(workflow_data)
    print("```mermaid")
    print(workflow)
    print("```\n")
    
    # 5. Agent Lifecycle
    print("5. AGENT SYSTEM LIFECYCLE")
    print("-" * 40)
    agent_lifecycle = lifecycle_gen.generate_agent_lifecycle(3)
    print("```mermaid")
    print(agent_lifecycle)
    print("```\n")
    
    # 6. Validation Flow
    print("6. VALIDATION FLOW")
    print("-" * 40)
    validation_data = {
        "validators": [
            {"name": "Schema Validator", "type": "semantic"},
            {"name": "Span Validator", "type": "span"},
            {"name": "Integration Validator", "type": "standard"},
            {"name": "Compliance Check", "type": "semantic"}
        ]
    }
    validation_flow = visualizer.generate_validation_flow_diagram(validation_data)
    print("```mermaid")
    print(validation_flow)
    print("```\n")
    
    # 7. Performance Metrics
    print("7. PERFORMANCE VISUALIZATION")
    print("-" * 40)
    perf_data = {
        "metrics": {
            "avg_latency_ms": 42.5,
            "throughput_ops_sec": 1250.3,
            "memory_mb": 512.8,
            "cpu_percent": 35.2
        }
    }
    performance = visualizer.generate_performance_diagram(perf_data)
    print("```mermaid")
    print(performance)
    print("```\n")
    
    # 8. Full System Lifecycle
    print("8. FULL SYSTEM LIFECYCLE")
    print("-" * 40)
    full_lifecycle = visualizer.generate_lifecycle_diagram({
        "components": {
            "semantic": [
                {"name": "Load YAML"},
                {"name": "Parse Conventions"},
                {"name": "Extract Attributes"}
            ],
            "generation": [
                {"name": "Weaver Forge"},
                {"name": "Template Engine"},
                {"name": "Code Generation"}
            ],
            "validation": [
                {"name": "Semantic Check"},
                {"name": "Span Validation"},
                {"name": "Integration Test"}
            ],
            "agents": [
                {"name": "Initialize AI"},
                {"name": "Configure Roles"},
                {"name": "Setup Communication"}
            ],
            "runtime": [
                {"name": "Execute Workflows"},
                {"name": "Capture Telemetry"},
                {"name": "Monitor Health"}
            ]
        }
    })
    print("```mermaid")
    print(full_lifecycle)
    print("```\n")

if __name__ == "__main__":
    main()