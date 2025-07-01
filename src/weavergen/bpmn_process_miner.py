"""
BPMN Process Mining - Discover and Generate Workflows from Execution Traces

This module implements process mining capabilities that analyze execution spans
to automatically discover and generate optimized BPMN workflows.
"""

import json
from collections import defaultdict, Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import xml.etree.ElementTree as ET
from xml.dom import minidom

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from .span_validator import SpanValidator


@dataclass
class ProcessNode:
    """Node in the discovered process"""
    task_name: str
    frequency: int
    avg_duration: float
    next_tasks: Dict[str, int]  # task_name -> count
    previous_tasks: Dict[str, int]
    attributes: Dict[str, Any]


@dataclass
class ProcessPattern:
    """Discovered process pattern"""
    pattern_type: str  # sequence, parallel, choice, loop
    tasks: List[str]
    frequency: float
    confidence: float
    performance_impact: float


@dataclass
class DiscoveredWorkflow:
    """Complete discovered workflow"""
    name: str
    nodes: Dict[str, ProcessNode]
    patterns: List[ProcessPattern]
    start_tasks: Set[str]
    end_tasks: Set[str]
    quality_metrics: Dict[str, float]


class BPMNProcessMiner:
    """
    Process mining engine that discovers BPMN workflows from execution traces.
    
    Features:
    - Automatic pattern discovery
    - BPMN generation from traces
    - Performance optimization
    - Quality assessment
    """
    
    def __init__(self):
        self.console = Console()
        self.span_validator = SpanValidator()
        
    def mine_workflow(self, spans: List[Dict[str, Any]], workflow_name: str = "DiscoveredWorkflow") -> DiscoveredWorkflow:
        """
        Mine a complete workflow from execution spans.
        
        Args:
            spans: List of execution spans
            workflow_name: Name for the discovered workflow
            
        Returns:
            DiscoveredWorkflow with patterns and metrics
        """
        
        self.console.print(f"\n[cyan]⛏️  Mining workflow from {len(spans)} spans...[/cyan]")
        
        # Build process graph
        nodes = self._build_process_graph(spans)
        
        # Identify start and end tasks
        start_tasks = self._find_start_tasks(nodes)
        end_tasks = self._find_end_tasks(nodes)
        
        # Discover patterns
        patterns = self._discover_patterns(nodes, spans)
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(nodes, patterns)
        
        workflow = DiscoveredWorkflow(
            name=workflow_name,
            nodes=nodes,
            patterns=patterns,
            start_tasks=start_tasks,
            end_tasks=end_tasks,
            quality_metrics=quality_metrics
        )
        
        self._print_discovery_summary(workflow)
        
        return workflow
        
    def _build_process_graph(self, spans: List[Dict[str, Any]]) -> Dict[str, ProcessNode]:
        """Build a process graph from spans"""
        
        nodes = {}
        
        # Group spans by trace
        traces = defaultdict(list)
        for span in spans:
            trace_id = span.get("trace_id", "unknown")
            traces[trace_id].append(span)
            
        # Sort spans in each trace by timestamp
        for trace_id, trace_spans in traces.items():
            trace_spans.sort(key=lambda s: s.get("timestamp", ""))
            
            # Build sequential relationships
            for i, span in enumerate(trace_spans):
                task_name = span.get("task", span.get("name", "unknown"))
                
                # Create or update node
                if task_name not in nodes:
                    nodes[task_name] = ProcessNode(
                        task_name=task_name,
                        frequency=0,
                        avg_duration=0,
                        next_tasks=defaultdict(int),
                        previous_tasks=defaultdict(int),
                        attributes={}
                    )
                    
                node = nodes[task_name]
                node.frequency += 1
                
                # Update duration
                duration = span.get("duration_ms", 0)
                if duration:
                    # Running average
                    node.avg_duration = ((node.avg_duration * (node.frequency - 1)) + duration) / node.frequency
                    
                # Update relationships
                if i > 0:
                    prev_task = trace_spans[i-1].get("task", trace_spans[i-1].get("name"))
                    node.previous_tasks[prev_task] += 1
                    
                if i < len(trace_spans) - 1:
                    next_task = trace_spans[i+1].get("task", trace_spans[i+1].get("name"))
                    node.next_tasks[next_task] += 1
                    
                # Collect common attributes
                if span.get("attributes"):
                    for key, value in span["attributes"].items():
                        if key not in node.attributes:
                            node.attributes[key] = []
                        node.attributes[key].append(value)
                        
        return nodes
        
    def _find_start_tasks(self, nodes: Dict[str, ProcessNode]) -> Set[str]:
        """Identify tasks that start workflows"""
        
        start_tasks = set()
        
        for task_name, node in nodes.items():
            # Tasks with no predecessors or significantly more occurrences than predecessors
            if not node.previous_tasks:
                start_tasks.add(task_name)
            else:
                predecessor_count = sum(node.previous_tasks.values())
                if node.frequency > predecessor_count * 1.5:
                    start_tasks.add(task_name)
                    
        return start_tasks
        
    def _find_end_tasks(self, nodes: Dict[str, ProcessNode]) -> Set[str]:
        """Identify tasks that end workflows"""
        
        end_tasks = set()
        
        for task_name, node in nodes.items():
            # Tasks with no successors
            if not node.next_tasks:
                end_tasks.add(task_name)
                
        return end_tasks
        
    def _discover_patterns(self, nodes: Dict[str, ProcessNode], spans: List[Dict[str, Any]]) -> List[ProcessPattern]:
        """Discover process patterns from the graph"""
        
        patterns = []
        
        # Discover sequences
        sequences = self._find_sequences(nodes)
        patterns.extend(sequences)
        
        # Discover parallel patterns
        parallels = self._find_parallel_patterns(nodes, spans)
        patterns.extend(parallels)
        
        # Discover choice patterns
        choices = self._find_choice_patterns(nodes)
        patterns.extend(choices)
        
        # Discover loops
        loops = self._find_loops(nodes)
        patterns.extend(loops)
        
        return patterns
        
    def _find_sequences(self, nodes: Dict[str, ProcessNode]) -> List[ProcessPattern]:
        """Find sequential execution patterns"""
        
        sequences = []
        visited = set()
        
        for start_task in nodes:
            if start_task in visited:
                continue
                
            # Find longest sequence starting from this task
            sequence = [start_task]
            current = start_task
            
            while True:
                node = nodes[current]
                
                # Continue if there's exactly one next task with high probability
                if len(node.next_tasks) == 1:
                    next_task = list(node.next_tasks.keys())[0]
                    next_node = nodes.get(next_task)
                    
                    if next_node and len(next_node.previous_tasks) == 1:
                        sequence.append(next_task)
                        visited.add(next_task)
                        current = next_task
                    else:
                        break
                else:
                    break
                    
            if len(sequence) > 1:
                # Calculate pattern metrics
                total_freq = min(nodes[task].frequency for task in sequence)
                avg_duration = sum(nodes[task].avg_duration for task in sequence)
                
                sequences.append(ProcessPattern(
                    pattern_type="sequence",
                    tasks=sequence,
                    frequency=total_freq / max(nodes[t].frequency for t in nodes),
                    confidence=0.9,  # High confidence for clear sequences
                    performance_impact=avg_duration
                ))
                
        return sequences
        
    def _find_parallel_patterns(self, nodes: Dict[str, ProcessNode], spans: List[Dict[str, Any]]) -> List[ProcessPattern]:
        """Find parallel execution patterns"""
        
        parallels = []
        
        # Group spans by trace and analyze overlapping timestamps
        traces = defaultdict(list)
        for span in spans:
            trace_id = span.get("trace_id", "unknown")
            traces[trace_id].append(span)
            
        parallel_tasks = defaultdict(int)
        
        for trace_spans in traces.values():
            # Find overlapping tasks
            for i, span1 in enumerate(trace_spans):
                for span2 in trace_spans[i+1:]:
                    # Check if tasks overlap in time
                    if self._tasks_overlap(span1, span2):
                        task1 = span1.get("task", span1.get("name"))
                        task2 = span2.get("task", span2.get("name"))
                        
                        if task1 != task2:
                            key = tuple(sorted([task1, task2]))
                            parallel_tasks[key] += 1
                            
        # Create patterns for frequent parallel executions
        for (task1, task2), count in parallel_tasks.items():
            if count > len(traces) * 0.3:  # At least 30% of traces
                parallels.append(ProcessPattern(
                    pattern_type="parallel",
                    tasks=[task1, task2],
                    frequency=count / len(traces),
                    confidence=0.7,
                    performance_impact=max(nodes[task1].avg_duration, nodes[task2].avg_duration)
                ))
                
        return parallels
        
    def _find_choice_patterns(self, nodes: Dict[str, ProcessNode]) -> List[ProcessPattern]:
        """Find exclusive choice patterns (XOR gateways)"""
        
        choices = []
        
        for task_name, node in nodes.items():
            if len(node.next_tasks) > 1:
                # This task leads to multiple choices
                total_transitions = sum(node.next_tasks.values())
                
                choice_tasks = []
                for next_task, count in node.next_tasks.items():
                    probability = count / total_transitions
                    if probability > 0.1:  # At least 10% probability
                        choice_tasks.append(next_task)
                        
                if len(choice_tasks) > 1:
                    choices.append(ProcessPattern(
                        pattern_type="choice",
                        tasks=[task_name] + choice_tasks,
                        frequency=node.frequency / max(n.frequency for n in nodes.values()),
                        confidence=0.8,
                        performance_impact=sum(nodes[t].avg_duration for t in choice_tasks) / len(choice_tasks)
                    ))
                    
        return choices
        
    def _find_loops(self, nodes: Dict[str, ProcessNode]) -> List[ProcessPattern]:
        """Find loop patterns"""
        
        loops = []
        
        # Simple loop detection: task that points back to earlier task
        for task_name, node in nodes.items():
            for prev_task in node.previous_tasks:
                if prev_task in node.next_tasks:
                    # Potential loop
                    loop_count = min(node.previous_tasks[prev_task], node.next_tasks[prev_task])
                    
                    if loop_count > node.frequency * 0.2:  # At least 20% of executions
                        loops.append(ProcessPattern(
                            pattern_type="loop",
                            tasks=[prev_task, task_name],
                            frequency=loop_count / node.frequency,
                            confidence=0.6,
                            performance_impact=nodes[prev_task].avg_duration + node.avg_duration
                        ))
                        
        return loops
        
    def _tasks_overlap(self, span1: Dict, span2: Dict) -> bool:
        """Check if two tasks overlap in time"""
        
        # Parse timestamps
        try:
            start1 = datetime.fromisoformat(span1.get("timestamp", ""))
            duration1 = span1.get("duration_ms", 0)
            end1 = start1.timestamp() + (duration1 / 1000)
            
            start2 = datetime.fromisoformat(span2.get("timestamp", ""))
            duration2 = span2.get("duration_ms", 0)
            end2 = start2.timestamp() + (duration2 / 1000)
            
            # Check overlap
            return start1.timestamp() < end2 and start2.timestamp() < end1
            
        except:
            return False
            
    def _calculate_quality_metrics(self, nodes: Dict[str, ProcessNode], patterns: List[ProcessPattern]) -> Dict[str, float]:
        """Calculate quality metrics for the discovered workflow"""
        
        metrics = {}
        
        # Completeness: how many tasks are covered by patterns
        pattern_tasks = set()
        for pattern in patterns:
            pattern_tasks.update(pattern.tasks)
            
        metrics["completeness"] = len(pattern_tasks) / len(nodes) if nodes else 0
        
        # Precision: average confidence of patterns
        if patterns:
            metrics["precision"] = sum(p.confidence for p in patterns) / len(patterns)
        else:
            metrics["precision"] = 0
            
        # Fitness: how well patterns match the data
        total_freq = sum(n.frequency for n in nodes.values())
        pattern_freq = sum(p.frequency * p.confidence for p in patterns)
        metrics["fitness"] = pattern_freq / total_freq if total_freq > 0 else 0
        
        # Simplicity: inverse of pattern count (normalized)
        metrics["simplicity"] = 1 / (1 + len(patterns) / 10)
        
        return metrics
        
    def generate_bpmn(self, workflow: DiscoveredWorkflow, output_path: str) -> str:
        """
        Generate BPMN XML from discovered workflow.
        
        Args:
            workflow: Discovered workflow
            output_path: Path to save BPMN file
            
        Returns:
            Path to generated BPMN file
        """
        
        # Create BPMN root elements
        bpmn = ET.Element("definitions", {
            "xmlns": "http://www.omg.org/spec/BPMN/20100524/MODEL",
            "xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
            "targetNamespace": "http://weavergen/discovered"
        })
        
        process = ET.SubElement(bpmn, "process", {
            "id": workflow.name,
            "isExecutable": "true"
        })
        
        # Add start event
        start_event = ET.SubElement(process, "startEvent", {"id": "start"})
        
        # Track created elements
        created_elements = {"start": start_event}
        
        # Create service tasks
        for task_name, node in workflow.nodes.items():
            task = ET.SubElement(process, "serviceTask", {
                "id": self._sanitize_id(task_name),
                "name": task_name
            })
            created_elements[task_name] = task
            
        # Add end event
        end_event = ET.SubElement(process, "endEvent", {"id": "end"})
        created_elements["end"] = end_event
        
        # Create flows based on patterns
        flow_id = 0
        
        # Connect start to start tasks
        for start_task in workflow.start_tasks:
            flow_id += 1
            ET.SubElement(process, "sequenceFlow", {
                "id": f"flow_{flow_id}",
                "sourceRef": "start",
                "targetRef": self._sanitize_id(start_task)
            })
            
        # Create flows from patterns
        for pattern in workflow.patterns:
            if pattern.pattern_type == "sequence":
                # Sequential flow
                for i in range(len(pattern.tasks) - 1):
                    flow_id += 1
                    ET.SubElement(process, "sequenceFlow", {
                        "id": f"flow_{flow_id}",
                        "sourceRef": self._sanitize_id(pattern.tasks[i]),
                        "targetRef": self._sanitize_id(pattern.tasks[i + 1])
                    })
                    
            elif pattern.pattern_type == "parallel":
                # Create parallel gateway
                flow_id += 1
                split_gw = ET.SubElement(process, "parallelGateway", {
                    "id": f"parallel_split_{flow_id}"
                })
                join_gw = ET.SubElement(process, "parallelGateway", {
                    "id": f"parallel_join_{flow_id}"
                })
                
                # Connect tasks through gateways
                for task in pattern.tasks:
                    flow_id += 1
                    ET.SubElement(process, "sequenceFlow", {
                        "id": f"flow_{flow_id}",
                        "sourceRef": split_gw.get("id"),
                        "targetRef": self._sanitize_id(task)
                    })
                    flow_id += 1
                    ET.SubElement(process, "sequenceFlow", {
                        "id": f"flow_{flow_id}",
                        "sourceRef": self._sanitize_id(task),
                        "targetRef": join_gw.get("id")
                    })
                    
        # Connect end tasks to end
        for end_task in workflow.end_tasks:
            flow_id += 1
            ET.SubElement(process, "sequenceFlow", {
                "id": f"flow_{flow_id}",
                "sourceRef": self._sanitize_id(end_task),
                "targetRef": "end"
            })
            
        # Pretty print XML
        xml_str = minidom.parseString(ET.tostring(bpmn)).toprettyxml(indent="  ")
        
        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(xml_str)
            
        self.console.print(f"[green]✅ Generated BPMN: {output_file}[/green]")
        
        return str(output_file)
    
    def patterns_to_bpmn(self, discovered_workflow: DiscoveredWorkflow, output_path: str) -> str:
        """
        Generate executable BPMN workflow from discovered patterns.
        
        Args:
            discovered_workflow: Discovered workflow with patterns
            output_path: Path to save BPMN file
            
        Returns:
            Path to generated BPMN file
        """
        
        self.console.print(f"\n[cyan]🏗️  Generating BPMN from mined patterns: {discovered_workflow.name}[/cyan]")
        
        # Create BPMN structure
        bpmn = ET.Element("definitions", {
            "xmlns": "http://www.omg.org/spec/BPMN/20100524/MODEL",
            "xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
            "xmlns:dc": "http://www.omg.org/spec/DD/20100524/DC",
            "xmlns:di": "http://www.omg.org/spec/DD/20100524/DI",
            "targetNamespace": "http://weavergen.ai/mined",
            "id": f"mined_{discovered_workflow.name}"
        })
        
        process = ET.SubElement(bpmn, "process", {
            "id": f"Process_{discovered_workflow.name}",
            "name": f"Mined Process: {discovered_workflow.name}",
            "isExecutable": "true"
        })
        
        # Add start event
        start_event = ET.SubElement(process, "startEvent", {
            "id": "StartEvent_1",
            "name": "Start"
        })
        
        # Track flows and generate IDs
        flow_id = 1
        task_positions = {}
        
        # Add start tasks (nodes with no predecessors)
        start_tasks = [name for name, node in discovered_workflow.nodes.items() 
                      if not node.previous_tasks]
        
        if not start_tasks:
            start_tasks = list(discovered_workflow.start_tasks) if discovered_workflow.start_tasks else [list(discovered_workflow.nodes.keys())[0]]
        
        # Generate service tasks for each discovered node
        for task_name, node in discovered_workflow.nodes.items():
            task_id = f"Task_{task_name.replace(' ', '_')}"
            
            # Determine task type based on patterns
            task_type = "serviceTask"
            parallel_patterns = [p for p in discovered_workflow.patterns if p.pattern_type == "parallel" and task_name in p.description]
            
            if parallel_patterns:
                task_type = "parallelGateway"
            
            task_elem = ET.SubElement(process, task_type, {
                "id": task_id,
                "name": task_name
            })
            
            # Add task documentation with mining metadata
            documentation = ET.SubElement(task_elem, "documentation")
            doc_text = f"""
Mined Task Metadata:
- Frequency: {node.frequency}
- Avg Duration: {node.avg_duration}ms
- Quality Score: {node.attributes.get('quality.score', ['N/A'])[0]}
- Next Tasks: {', '.join(node.next_tasks.keys())}
            """.strip()
            documentation.text = doc_text
            
            task_positions[task_name] = task_id
        
        # Generate sequence flows based on discovered patterns
        sequential_patterns = [p for p in discovered_workflow.patterns if p.pattern_type == "sequential"]
        
        # Connect start event to start tasks
        for start_task in start_tasks[:1]:  # Connect to first start task
            if start_task in task_positions:
                flow = ET.SubElement(process, "sequenceFlow", {
                    "id": f"Flow_{flow_id}",
                    "sourceRef": "StartEvent_1",
                    "targetRef": task_positions[start_task]
                })
                flow_id += 1
        
        # Add sequence flows from patterns
        for pattern in sequential_patterns:
            if "→" in pattern.description:
                parts = pattern.description.split("→")
                for i in range(len(parts) - 1):
                    source_task = parts[i].strip()
                    target_task = parts[i + 1].strip()
                    
                    if source_task in task_positions and target_task in task_positions:
                        flow = ET.SubElement(process, "sequenceFlow", {
                            "id": f"Flow_{flow_id}",
                            "sourceRef": task_positions[source_task],
                            "targetRef": task_positions[target_task]
                        })
                        
                        # Add condition if pattern has low confidence
                        if pattern.confidence < 0.8:
                            condition = ET.SubElement(flow, "conditionExpression")
                            condition.text = f"${{quality_score >= {pattern.confidence}}}"
                        
                        flow_id += 1
        
        # Add end event connected to end tasks
        end_event = ET.SubElement(process, "endEvent", {
            "id": "EndEvent_1",
            "name": "End"
        })
        
        end_tasks = [name for name, node in discovered_workflow.nodes.items() 
                    if not node.next_tasks]
        
        if not end_tasks:
            end_tasks = list(discovered_workflow.end_tasks) if discovered_workflow.end_tasks else [list(discovered_workflow.nodes.keys())[-1]]
        
        # Connect end tasks to end event
        for end_task in end_tasks:
            if end_task in task_positions:
                flow = ET.SubElement(process, "sequenceFlow", {
                    "id": f"Flow_{flow_id}",
                    "sourceRef": task_positions[end_task],
                    "targetRef": "EndEvent_1"
                })
                flow_id += 1
        
        # Add parallel gateways for parallel patterns
        parallel_patterns = [p for p in discovered_workflow.patterns if p.pattern_type == "parallel"]
        gateway_id = 1
        
        for pattern in parallel_patterns[:3]:  # Limit to 3 parallel patterns
            if "parallel:" in pattern.description and "→" in pattern.description:
                gateway_split_id = f"ParallelGateway_Split_{gateway_id}"
                gateway_join_id = f"ParallelGateway_Join_{gateway_id}"
                
                # Add split gateway
                split_gateway = ET.SubElement(process, "parallelGateway", {
                    "id": gateway_split_id,
                    "name": f"Split {gateway_id}"
                })
                
                # Add join gateway  
                join_gateway = ET.SubElement(process, "parallelGateway", {
                    "id": gateway_join_id,
                    "name": f"Join {gateway_id}"
                })
                
                gateway_id += 1
        
        # Save BPMN file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        xml_str = minidom.parseString(ET.tostring(bpmn)).toprettyxml(indent="  ")
        
        with open(output_file, 'w') as f:
            f.write(xml_str)
        
        self.console.print(f"[green]✅ Generated executable BPMN: {output_file}[/green]")
        
        # Generate execution statistics
        stats = {
            "total_tasks": len(discovered_workflow.nodes),
            "sequential_patterns": len([p for p in discovered_workflow.patterns if p.pattern_type == "sequential"]),
            "parallel_patterns": len([p for p in discovered_workflow.patterns if p.pattern_type == "parallel"]),
            "start_tasks": len(start_tasks),
            "end_tasks": len(end_tasks),
            "quality_score": discovered_workflow.quality_metrics.get("overall_quality", 0.0),
            "generated_flows": flow_id - 1
        }
        
        stats_file = output_file.with_suffix('.stats.json')
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return str(output_file)
        
    def _sanitize_id(self, task_name: str) -> str:
        """Sanitize task name for use as BPMN ID"""
        
        # Replace special characters
        sanitized = task_name.lower()
        sanitized = sanitized.replace(" ", "_")
        sanitized = sanitized.replace("-", "_")
        sanitized = sanitized.replace(".", "_")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
        
        return sanitized
        
    def _print_discovery_summary(self, workflow: DiscoveredWorkflow):
        """Print a summary of the discovered workflow"""
        
        panel = Panel(
            f"[bold]Discovered Workflow: {workflow.name}[/bold]\n\n"
            f"Tasks: {len(workflow.nodes)}\n"
            f"Patterns: {len(workflow.patterns)}\n"
            f"Start Tasks: {', '.join(workflow.start_tasks)}\n"
            f"End Tasks: {', '.join(workflow.end_tasks)}\n\n"
            f"Quality Metrics:\n"
            f"  Completeness: {workflow.quality_metrics.get('completeness', 0):.1%}\n"
            f"  Precision: {workflow.quality_metrics.get('precision', 0):.1%}\n"
            f"  Fitness: {workflow.quality_metrics.get('fitness', 0):.1%}\n"
            f"  Simplicity: {workflow.quality_metrics.get('simplicity', 0):.1%}",
            title="Process Mining Results",
            border_style="cyan"
        )
        
        self.console.print(panel)
        
        # Print discovered patterns
        if workflow.patterns:
            tree = Tree("Discovered Patterns")
            
            for pattern in sorted(workflow.patterns, key=lambda p: p.frequency, reverse=True):
                pattern_text = f"{pattern.pattern_type}: {' → '.join(pattern.tasks)}"
                pattern_node = tree.add(pattern_text)
                pattern_node.add(f"Frequency: {pattern.frequency:.1%}")
                pattern_node.add(f"Confidence: {pattern.confidence:.1%}")
                
            self.console.print(tree)