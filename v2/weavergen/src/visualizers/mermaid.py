"""
WeaverGen v2 Mermaid Visualization Module
Comprehensive mermaid diagram generation for all system components
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json
from pathlib import Path


class MermaidVisualizer:
    """Unified mermaid diagram generator for WeaverGen v2"""
    
    def __init__(self):
        self.style_definitions = {
            "semantic": "fill:#e1f5e1,stroke:#4caf50,stroke-width:2px",
            "agent": "fill:#e3f2fd,stroke:#2196f3,stroke-width:2px", 
            "validation": "fill:#fff3e0,stroke:#ff9800,stroke-width:2px",
            "bpmn": "fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px",
            "error": "fill:#ffebee,stroke:#f44336,stroke-width:3px",
            "success": "fill:#e8f5e9,stroke:#4caf50,stroke-width:2px"
        }
    
    def generate_lifecycle_diagram(self, lifecycle_data: Dict[str, Any]) -> str:
        """Generate comprehensive lifecycle diagram from semantic conventions to runtime"""
        lines = ["graph TB"]
        lines.append("    %% Lifecycle: Semantic Conventions → Runtime Execution")
        
        # Define main phases
        phases = {
            "semantic": "Semantic Conventions",
            "generation": "Code Generation", 
            "validation": "Validation",
            "agents": "Agent Creation",
            "runtime": "Runtime Execution"
        }
        
        # Create phase nodes
        for phase_id, phase_name in phases.items():
            lines.append(f"    {phase_id}[\"{phase_name}\"]")
        
        # Add phase connections
        lines.append("    semantic --> generation")
        lines.append("    generation --> validation")
        lines.append("    validation --> agents")
        lines.append("    agents --> runtime")
        
        # Add sub-components for each phase
        if "components" in lifecycle_data:
            for phase, components in lifecycle_data["components"].items():
                for i, comp in enumerate(components):
                    comp_id = f"{phase}_{i}"
                    lines.append(f"    {comp_id}[{comp['name']}]")
                    lines.append(f"    {phase} --> {comp_id}")
        
        # Add styling
        lines.extend(self._add_styles(["semantic", "generation", "validation", "agents", "runtime"]))
        
        return "\n".join(lines)
    
    def generate_span_trace_diagram(self, spans: List[Dict[str, Any]], 
                                   max_spans: int = 50) -> str:
        """Generate sequence diagram from OpenTelemetry spans"""
        lines = ["sequenceDiagram"]
        lines.append("    participant Client")
        
        # Extract unique services/components
        services = set()
        for span in spans[:max_spans]:
            service = span.get("attributes", {}).get("service.name", "Unknown")
            services.add(service)
        
        # Add participants
        for service in sorted(services):
            lines.append(f"    participant {self._sanitize_id(service)}")
        
        # Add span interactions
        for i, span in enumerate(spans[:max_spans]):
            service = span.get("attributes", {}).get("service.name", "Unknown")
            operation = span.get("name", "unknown")
            duration = self._calculate_duration(span)
            status = "✅" if not span.get("error") else "❌"
            
            if i == 0:
                lines.append(f"    Client->>{self._sanitize_id(service)}: {operation}")
            else:
                prev_service = spans[i-1].get("attributes", {}).get("service.name", "Unknown")
                lines.append(f"    {self._sanitize_id(prev_service)}->>{self._sanitize_id(service)}: {operation}")
            
            lines.append(f"    Note over {self._sanitize_id(service)}: {duration}ms {status}")
        
        return "\n".join(lines)
    
    def generate_workflow_visualization(self, workflow_data: Dict[str, Any]) -> str:
        """Generate BPMN-style workflow diagram"""
        lines = ["graph TD"]
        lines.append("    Start([Start])")
        
        tasks = workflow_data.get("tasks", [])
        gateways = workflow_data.get("gateways", [])
        
        # Add tasks
        for i, task in enumerate(tasks):
            task_id = f"T{i}"
            task_type = task.get("type", "task")
            task_name = task.get("name", f"Task {i}")
            
            if task_type == "service":
                lines.append(f"    {task_id}[\"{task_name}\"]")
            elif task_type == "user":
                lines.append(f"    {task_id}([{task_name}])")
            else:
                lines.append(f"    {task_id}[{task_name}]")
        
        # Add gateways
        for i, gateway in enumerate(gateways):
            gw_id = f"G{i}"
            gw_type = gateway.get("type", "exclusive")
            
            if gw_type == "parallel":
                lines.append(f"    {gw_id}{{Parallel Gateway}}")
            else:
                lines.append(f"    {gw_id}{{Exclusive Gateway}}")
        
        # Add connections
        connections = workflow_data.get("connections", [])
        for conn in connections:
            from_node = conn["from"]
            to_node = conn["to"]
            label = conn.get("label", "")
            
            if label:
                lines.append(f"    {from_node} -->|{label}| {to_node}")
            else:
                lines.append(f"    {from_node} --> {to_node}")
        
        lines.append("    End([End])")
        
        # Add styling
        lines.append("    classDef serviceTask fill:#e3f2fd,stroke:#2196f3")
        lines.append("    classDef userTask fill:#fff3e0,stroke:#ff9800")
        
        return "\n".join(lines)
    
    def generate_agent_communication_diagram(self, communication_data: Dict[str, Any]) -> str:
        """Generate agent communication flow diagram"""
        lines = ["sequenceDiagram"]
        
        agents = communication_data.get("agents", [])
        messages = communication_data.get("messages", [])
        
        # Add participants
        for agent in agents:
            lines.append(f"    participant {agent['id']} as {agent['name']}")
        
        lines.append("    participant OTel as OpenTelemetry")
        
        # Add messages
        for msg in messages:
            from_agent = msg["from"]
            to_agent = msg.get("to", "OTel")
            msg_type = msg["type"]
            content = msg.get("content", "")
            
            if msg_type == "decision":
                lines.append(f"    {from_agent}->>{to_agent}: Decision: {content}")
            elif msg_type == "request":
                lines.append(f"    {from_agent}->>{to_agent}: Request: {content}")
            elif msg_type == "response":
                lines.append(f"    {from_agent}-->>{to_agent}: Response: {content}")
            else:
                lines.append(f"    {from_agent}->>{to_agent}: {msg_type}: {content}")
            
            # Add thinking time if present
            if "duration_ms" in msg:
                lines.append(f"    Note over {from_agent}: Thinking: {msg['duration_ms']}ms")
        
        return "\n".join(lines)
    
    def generate_system_architecture_diagram(self, arch_data: Dict[str, Any]) -> str:
        """Generate system architecture diagram"""
        from ..data_providers import ProjectStructureProvider
        from pathlib import Path
        
        # Use real project structure if not provided
        if not arch_data.get("components"):
            provider = ProjectStructureProvider(Path("/Users/sac/dev/weavergen"))
            arch_data = provider.get_architecture_data()
        
        lines = ["graph TB"]
        lines.append("    %% WeaverGen v2 Architecture (Detected)")
        
        components = arch_data.get("components", {})
        
        # Core components
        if components.get("core"):
            lines.append("    subgraph Core[Core Engine]")
            for i, comp in enumerate(components["core"]):
                comp_id = f"C{i}"
                lines.append(f"        {comp_id}[{comp}]")
            lines.append("    end")
        
        # Layers
        if components.get("layers"):
            lines.append("    subgraph Layers[System Layers]")
            for i, layer in enumerate(components["layers"]):
                layer_id = f"L{i}"
                lines.append(f"        {layer_id}[{layer}]")
            lines.append("    end")
            
            # Connect layers sequentially
            for i in range(len(components["layers"]) - 1):
                lines.append(f"    L{i} --> L{i+1}")
        
        # External systems
        if components.get("external"):
            lines.append("    subgraph External[External Systems]")
            for i, ext in enumerate(components["external"]):
                ext_id = f"E{i}"
                lines.append(f"        {ext_id}[{ext}]")
            lines.append("    end")
        
        # Add connections between main groups
        if components.get("core") and components.get("layers"):
            lines.append("    Core --> Layers")
        if components.get("layers") and components.get("external"):
            lines.append("    Layers --> External")
        
        return "\n".join(lines)
    
    def generate_validation_flow_diagram(self, validation_data: Dict[str, Any]) -> str:
        """Generate validation flow diagram"""
        lines = ["graph TD"]
        
        validators = validation_data.get("validators", [])
        
        lines.append("    Start([Start Validation])")
        
        for i, validator in enumerate(validators):
            val_id = f"V{i}"
            val_name = validator["name"]
            val_type = validator.get("type", "standard")
            
            if val_type == "semantic":
                lines.append(f"    {val_id}[\"{val_name}<br/>Semantic Validation\"]")
            elif val_type == "span":
                lines.append(f"    {val_id}[\"{val_name}<br/>Span-based Validation\"]")
            else:
                lines.append(f"    {val_id}[{val_name}]")
            
            if i == 0:
                lines.append(f"    Start --> {val_id}")
            else:
                lines.append(f"    V{i-1} --> {val_id}")
        
        lines.append(f"    V{len(validators)-1} --> Result{{Validation Result}}")
        lines.append("    Result -->|Pass| Success([Success])")
        lines.append("    Result -->|Fail| Failure([Failure])")
        
        # Add styling
        lines.append("    classDef semantic fill:#e1f5e1,stroke:#4caf50")
        lines.append("    classDef span fill:#e3f2fd,stroke:#2196f3")
        
        return "\n".join(lines)
    
    def generate_performance_diagram(self, perf_data: Dict[str, Any]) -> str:
        """Generate performance metrics diagram"""
        from ..data_providers import SystemMetricsProvider
        
        # Use real metrics if not provided
        if not perf_data.get("metrics"):
            provider = SystemMetricsProvider()
            perf_data = provider.get_performance_data()
        
        lines = ["graph LR"]
        
        metrics = perf_data.get("metrics", {})
        system_info = perf_data.get("system_info", {})
        
        lines.append("    subgraph Metrics[Performance Metrics (Real-time)]")
        lines.append(f"        LAT[Latency<br/>{metrics.get('avg_latency_ms', 0):.1f}ms]")
        lines.append(f"        THR[Throughput<br/>{metrics.get('throughput_ops_sec', 0):.1f} ops/s]")
        lines.append(f"        MEM[Memory<br/>{metrics.get('memory_mb', 0):.1f}MB]")
        lines.append(f"        CPU[CPU<br/>{metrics.get('cpu_percent', 0):.1f}%]")
        if "error_rate" in metrics:
            lines.append(f"        ERR[Errors<br/>{metrics['error_rate']:.2%}]")
        lines.append("    end")
        
        # Add system info if available
        if system_info:
            lines.append("    subgraph System[System Info]")
            if "total_memory_mb" in system_info:
                lines.append(f"        TMEM[Total RAM<br/>{system_info['total_memory_mb']:.0f}MB]")
            if "cpu_count" in system_info:
                lines.append(f"        CORES[CPU Cores<br/>{system_info['cpu_count']}]")
            lines.append("    end")
        
        # Add performance thresholds with actual comparison
        latency_status = "✅" if metrics.get('avg_latency_ms', 0) < 100 else "⚠️"
        throughput_status = "✅" if metrics.get('throughput_ops_sec', 0) > 1000 else "⚠️"
        
        lines.append(f"    LAT -->|Target 100ms {latency_status}| T1{{Latency Check}}")
        lines.append(f"    THR -->|Target 1000 ops/s {throughput_status}| T2{{Throughput Check}}")
        
        return "\n".join(lines)
    
    def _sanitize_id(self, text: str) -> str:
        """Sanitize text for use as mermaid ID"""
        return text.replace(" ", "_").replace("-", "_").replace(".", "_")
    
    def _calculate_duration(self, span: Dict[str, Any]) -> float:
        """Calculate span duration in milliseconds"""
        start = span.get("start_time", 0)
        end = span.get("end_time", 0)
        
        if isinstance(start, str) and isinstance(end, str):
            # Parse ISO timestamps
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                return (end_dt - start_dt).total_seconds() * 1000
            except:
                return 0.0
        
        return (end - start) / 1_000_000  # nanoseconds to milliseconds
    
    def _add_styles(self, node_types: List[str]) -> List[str]:
        """Add mermaid style definitions"""
        lines = []
        lines.append("    %% Styling")
        
        for node_type in node_types:
            if node_type in self.style_definitions:
                lines.append(f"    classDef {node_type} {self.style_definitions[node_type]}")
                lines.append(f"    class {node_type} {node_type}")
        
        return lines


class MermaidLifecycleGenerator:
    """Specialized generator for lifecycle diagrams"""
    
    def __init__(self, visualizer: Optional[MermaidVisualizer] = None):
        self.visualizer = visualizer or MermaidVisualizer()
    
    def generate_semantic_to_runtime_lifecycle(self, semantic_file: Path) -> str:
        """Generate complete lifecycle from semantic conventions to runtime"""
        from ..data_providers import SemanticConventionProvider
        
        provider = SemanticConventionProvider(semantic_file)
        lifecycle_data = {
            "components": provider.get_lifecycle_components()
        }
        
        return self.visualizer.generate_lifecycle_diagram(lifecycle_data)
    
    def generate_bpmn_lifecycle(self, workflow_name: str) -> str:
        """Generate BPMN workflow lifecycle diagram"""
        from ..data_providers import BPMNWorkflowProvider
        
        # Try to find actual BPMN file for the workflow
        workflow_file = None
        if workflow_name != "DefaultWorkflow":
            from pathlib import Path
            potential_files = list(Path("/Users/sac/dev/weavergen").rglob(f"*{workflow_name}*.bpmn"))
            if potential_files:
                workflow_file = potential_files[0]
        
        provider = BPMNWorkflowProvider(workflow_file)
        workflow_data = provider.workflow_data
        
        return self.visualizer.generate_workflow_visualization(workflow_data)
    
    def generate_agent_lifecycle(self, agent_count: int = 3) -> str:
        """Generate agent system lifecycle diagram"""
        from ..data_providers import AgentSystemProvider
        
        provider = AgentSystemProvider()
        agent_data = provider.agent_data
        
        lines = ["stateDiagram-v2"]
        lines.append("    [*] --> Initialization")
        
        # Build states based on actual agent configuration
        agents = agent_data.get("agents", [])
        if len(agents) > 1:
            lines.append("    Initialization --> Multi_Agent_Setup")
            lines.append("    Multi_Agent_Setup --> Configuration")
        else:
            lines.append("    Initialization --> Configuration")
        
        lines.append("    Configuration --> Ready")
        lines.append("    Ready --> Processing")
        lines.append("    Processing --> Decision")
        lines.append("    Decision --> Communication")
        
        # Add communication patterns based on agent roles
        comm_patterns = agent_data.get("communication_patterns", [])
        if any(p.get("type") == "span_based" for p in comm_patterns):
            lines.append("    Communication --> Span_Tracking")
            lines.append("    Span_Tracking --> Processing: Continue")
        else:
            lines.append("    Communication --> Processing: More Tasks")
        
        lines.append("    Communication --> Completion: Done")
        lines.append("    Completion --> [*]")
        
        # Add processing sub-state based on agent roles
        lines.append("")
        lines.append("    state Processing {")
        lines.append("        [*] --> ReceiveTask")
        
        if any(agent.get("role") == "validation" for agent in agents):
            lines.append("        ReceiveTask --> Validate")
            lines.append("        Validate --> Execute")
        else:
            lines.append("        ReceiveTask --> Analyze")
            lines.append("        Analyze --> Execute")
        
        lines.append("        Execute --> [*]")
        lines.append("    }")
        
        return "\n".join(lines)
    
    def generate_validation_lifecycle(self) -> str:
        """Generate validation lifecycle diagram"""
        lines = ["graph TD"]
        lines.append("    subgraph Validation Lifecycle")
        lines.append("        PreVal[Pre-validation]")
        lines.append("        SemVal[Semantic Validation]")
        lines.append("        SpanVal[Span Validation]")
        lines.append("        IntVal[Integration Validation]")
        lines.append("        Report[Validation Report]")
        lines.append("    end")
        
        lines.append("    PreVal --> SemVal")
        lines.append("    SemVal --> SpanVal")
        lines.append("    SpanVal --> IntVal")
        lines.append("    IntVal --> Report")
        
        lines.append("    Report -->|Pass| Deploy[Deploy to Production]")
        lines.append("    Report -->|Fail| Fix[Fix Issues]")
        lines.append("    Fix --> PreVal")
        
        return "\n".join(lines)