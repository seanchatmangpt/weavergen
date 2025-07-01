"""
XES Converter - Professional Process Mining Integration

This module provides XES (eXtensible Event Stream) format conversion capabilities
for professional process mining tools integration with PM4Py.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import xml.etree.ElementTree as ET
from xml.dom import minidom

import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

try:
    import pm4py
    from pm4py.objects.log.obj import EventLog, Trace, Event
    from pm4py.objects.log.exporter import xes as xes_exporter
    from pm4py.objects.log.importer import xes as xes_importer
    from pm4py.algo.discovery.inductive import algorithm as inductive_miner
    from pm4py.visualization.petri_net import visualizer as pn_visualizer
    from pm4py.visualization.process_tree import visualizer as pt_visualizer
    PM4PY_AVAILABLE = True
except ImportError:
    PM4PY_AVAILABLE = False


class XESConverter:
    """
    Professional XES format converter for process mining integration.
    
    Features:
    - Convert OpenTelemetry spans to XES format
    - Export to professional process mining tools
    - Import existing XES files for analysis
    - Generate process models using PM4Py
    """
    
    def __init__(self):
        self.console = Console()
        if not PM4PY_AVAILABLE:
            self.console.print("[yellow]⚠️  PM4Py not available. Install with: pip install pm4py[/yellow]")
    
    def spans_to_xes(
        self, 
        spans: List[Dict[str, Any]], 
        output_path: str,
        case_id_field: str = "trace_id",
        activity_field: str = "task",
        timestamp_field: str = "timestamp"
    ) -> str:
        """
        Convert OpenTelemetry spans to XES format.
        
        Args:
            spans: List of span dictionaries
            output_path: Path to save XES file
            case_id_field: Field name for case identification
            activity_field: Field name for activity identification
            timestamp_field: Field name for timestamp
            
        Returns:
            Path to generated XES file
        """
        
        if not PM4PY_AVAILABLE:
            return self._manual_xes_export(spans, output_path, case_id_field, activity_field, timestamp_field)
        
        self.console.print(f"\n[cyan]🔄 Converting {len(spans)} spans to XES format...[/cyan]")
        
        # Group spans by case (trace)
        cases = {}
        for span in spans:
            case_id = span.get(case_id_field, "unknown_case")
            if case_id not in cases:
                cases[case_id] = []
            cases[case_id].append(span)
        
        # Create PM4Py EventLog
        log = EventLog()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Processing traces...", total=len(cases))
            
            for case_id, case_spans in cases.items():
                # Sort spans by timestamp
                case_spans.sort(key=lambda s: s.get(timestamp_field, ""))
                
                # Create trace
                trace = Trace()
                trace.attributes["concept:name"] = case_id
                
                # Add events to trace
                for span in case_spans:
                    event = Event()
                    
                    # Required XES attributes
                    event["concept:name"] = span.get(activity_field, "unknown_activity")
                    
                    # Parse timestamp
                    timestamp_str = span.get(timestamp_field, "")
                    if timestamp_str:
                        try:
                            if timestamp_str.endswith('Z'):
                                timestamp_str = timestamp_str[:-1] + '+00:00'
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            event["time:timestamp"] = timestamp
                        except:
                            event["time:timestamp"] = datetime.now()
                    else:
                        event["time:timestamp"] = datetime.now()
                    
                    # Add span attributes as event attributes
                    if "attributes" in span:
                        for key, value in span["attributes"].items():
                            # Convert to XES-compatible format
                            xes_key = key.replace(".", ":").replace("_", ":")
                            event[xes_key] = str(value)
                    
                    # Add other span fields
                    for key, value in span.items():
                        if key not in [case_id_field, activity_field, timestamp_field, "attributes"]:
                            xes_key = f"span:{key}"
                            event[xes_key] = str(value)
                    
                    trace.append(event)
                
                log.append(trace)
                progress.advance(task)
        
        # Export to XES
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        xes_exporter.apply(log, str(output_file))
        
        self.console.print(f"[green]✅ Exported {len(log)} traces to {output_file}[/green]")
        
        return str(output_file)
    
    def _manual_xes_export(
        self, 
        spans: List[Dict[str, Any]], 
        output_path: str,
        case_id_field: str,
        activity_field: str,
        timestamp_field: str
    ) -> str:
        """Manual XES export without PM4Py"""
        
        self.console.print("[yellow]Using manual XES export (PM4Py not available)[/yellow]")
        
        # Create XES XML structure
        root = ET.Element("log", {
            "xes.version": "1.0",
            "xes.features": "nested-attributes",
            "xmlns": "http://www.xes-standard.org/"
        })
        
        # Add extensions
        extension = ET.SubElement(root, "extension", {
            "name": "Concept",
            "prefix": "concept",
            "uri": "http://www.xes-standard.org/concept.xesext"
        })
        
        extension = ET.SubElement(root, "extension", {
            "name": "Time", 
            "prefix": "time",
            "uri": "http://www.xes-standard.org/time.xesext"
        })
        
        # Group spans by case
        cases = {}
        for span in spans:
            case_id = span.get(case_id_field, "unknown_case")
            if case_id not in cases:
                cases[case_id] = []
            cases[case_id].append(span)
        
        # Create traces
        for case_id, case_spans in cases.items():
            case_spans.sort(key=lambda s: s.get(timestamp_field, ""))
            
            trace = ET.SubElement(root, "trace")
            
            # Add case attributes
            case_name = ET.SubElement(trace, "string", {"key": "concept:name", "value": case_id})
            
            # Add events
            for span in case_spans:
                event = ET.SubElement(trace, "event")
                
                # Activity name
                activity = ET.SubElement(event, "string", {
                    "key": "concept:name",
                    "value": span.get(activity_field, "unknown_activity")
                })
                
                # Timestamp
                timestamp_str = span.get(timestamp_field, "")
                if timestamp_str:
                    try:
                        if timestamp_str.endswith('Z'):
                            timestamp_str = timestamp_str[:-1] + '+00:00'
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        ts_elem = ET.SubElement(event, "date", {
                            "key": "time:timestamp",
                            "value": timestamp.isoformat()
                        })
                    except:
                        pass
                
                # Add other attributes
                if "attributes" in span:
                    for key, value in span["attributes"].items():
                        attr = ET.SubElement(event, "string", {
                            "key": key.replace(".", ":"),
                            "value": str(value)
                        })
        
        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        with open(output_file, 'w') as f:
            f.write(xml_str)
        
        self.console.print(f"[green]✅ Manual XES export: {output_file}[/green]")
        
        return str(output_file)
    
    def analyze_xes(self, xes_path: str) -> Dict[str, Any]:
        """
        Analyze XES file and generate process insights.
        
        Args:
            xes_path: Path to XES file
            
        Returns:
            Analysis results dictionary
        """
        
        if not PM4PY_AVAILABLE:
            return self._manual_xes_analysis(xes_path)
        
        self.console.print(f"\n[cyan]📊 Analyzing XES file: {xes_path}[/cyan]")
        
        # Import XES file
        log = xes_importer.apply(xes_path)
        
        # Basic statistics
        analysis = {
            "traces": len(log),
            "events": sum(len(trace) for trace in log),
            "activities": len(set(event["concept:name"] for trace in log for event in trace)),
            "variants": len(pm4py.get_variants(log)),
            "start_activities": list(pm4py.get_start_activities(log).keys()),
            "end_activities": list(pm4py.get_end_activities(log).keys())
        }
        
        # Process discovery
        try:
            net, initial_marking, final_marking = inductive_miner.apply(log)
            analysis["process_model"] = {
                "places": len(net.places),
                "transitions": len(net.transitions),
                "arcs": len(net.arcs)
            }
        except Exception as e:
            analysis["process_model"] = {"error": str(e)}
        
        # Performance analysis
        try:
            dfg, start_activities, end_activities = pm4py.discover_dfg(log)
            analysis["directly_follows"] = len(dfg)
        except:
            analysis["directly_follows"] = 0
        
        self._print_analysis_results(analysis)
        
        return analysis
    
    def _manual_xes_analysis(self, xes_path: str) -> Dict[str, Any]:
        """Manual XES analysis without PM4Py"""
        
        self.console.print("[yellow]Using manual XES analysis (PM4Py not available)[/yellow]")
        
        try:
            tree = ET.parse(xes_path)
            root = tree.getroot()
            
            traces = root.findall(".//trace")
            events = root.findall(".//event")
            
            activities = set()
            for event in events:
                name_elem = event.find(".//string[@key='concept:name']")
                if name_elem is not None:
                    activities.add(name_elem.get("value", ""))
            
            analysis = {
                "traces": len(traces),
                "events": len(events),
                "activities": len(activities),
                "activity_list": sorted(list(activities))
            }
            
            self._print_analysis_results(analysis)
            
            return analysis
            
        except Exception as e:
            self.console.print(f"[red]Error analyzing XES: {e}[/red]")
            return {"error": str(e)}
    
    def _print_analysis_results(self, analysis: Dict[str, Any]):
        """Print analysis results in a formatted table"""
        
        table = Table(title="XES Process Mining Analysis", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Traces", str(analysis.get("traces", 0)))
        table.add_row("Events", str(analysis.get("events", 0)))
        table.add_row("Activities", str(analysis.get("activities", 0)))
        
        if "variants" in analysis:
            table.add_row("Process Variants", str(analysis["variants"]))
        
        if "start_activities" in analysis:
            start_acts = ", ".join(analysis["start_activities"][:3])
            if len(analysis["start_activities"]) > 3:
                start_acts += "..."
            table.add_row("Start Activities", start_acts)
        
        if "end_activities" in analysis:
            end_acts = ", ".join(analysis["end_activities"][:3])
            if len(analysis["end_activities"]) > 3:
                end_acts += "..."
            table.add_row("End Activities", end_acts)
        
        if "process_model" in analysis and "places" in analysis["process_model"]:
            model = analysis["process_model"]
            table.add_row("Process Model", f"{model['places']} places, {model['transitions']} transitions")
        
        self.console.print(table)
    
    def spans_to_dataframe(self, spans: List[Dict[str, Any]]) -> 'pd.DataFrame':
        """
        Convert spans to pandas DataFrame for analysis.
        
        Args:
            spans: List of span dictionaries
            
        Returns:
            DataFrame with flattened span data
        """
        
        rows = []
        
        for span in spans:
            row = {
                "case_id": span.get("trace_id", "unknown"),
                "activity": span.get("task", span.get("name", "unknown")),
                "timestamp": span.get("timestamp", ""),
                "duration_ms": span.get("duration_ms", 0),
                "status": span.get("status", "OK")
            }
            
            # Flatten attributes
            if "attributes" in span:
                for key, value in span["attributes"].items():
                    row[f"attr_{key}"] = value
            
            # Add other span fields
            for key, value in span.items():
                if key not in ["trace_id", "task", "name", "timestamp", "duration_ms", "status", "attributes"]:
                    row[f"span_{key}"] = value
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def generate_process_model(self, xes_path: str, output_dir: str = "process_models") -> Dict[str, str]:
        """
        Generate process models from XES file.
        
        Args:
            xes_path: Path to XES file
            output_dir: Directory to save models
            
        Returns:
            Dictionary of generated model files
        """
        
        if not PM4PY_AVAILABLE:
            self.console.print("[yellow]Process model generation requires PM4Py[/yellow]")
            return {}
        
        self.console.print(f"\n[cyan]🏗️  Generating process models from {xes_path}...[/cyan]")
        
        # Import log
        log = xes_importer.apply(xes_path)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        try:
            # Discover process model using Inductive Miner
            net, initial_marking, final_marking = inductive_miner.apply(log)
            
            # Save Petri net visualization
            gviz = pn_visualizer.apply(net, initial_marking, final_marking)
            petri_file = output_path / "petri_net.png"
            pn_visualizer.save(gviz, str(petri_file))
            generated_files["petri_net"] = str(petri_file)
            
            # Discover process tree
            tree = pm4py.discover_process_tree_inductive(log)
            
            # Save process tree visualization
            gviz = pt_visualizer.apply(tree)
            tree_file = output_path / "process_tree.png"
            pt_visualizer.save(gviz, str(tree_file))
            generated_files["process_tree"] = str(tree_file)
            
            # Generate DFG (Directly-Follows Graph)
            dfg, start_activities, end_activities = pm4py.discover_dfg(log)
            
            # Save DFG as simple format
            dfg_data = {
                "directly_follows": {f"{k[0]} -> {k[1]}": v for k, v in dfg.items()},
                "start_activities": start_activities,
                "end_activities": end_activities
            }
            
            dfg_file = output_path / "dfg.json"
            with open(dfg_file, 'w') as f:
                json.dump(dfg_data, f, indent=2)
            generated_files["dfg"] = str(dfg_file)
            
            self.console.print(f"[green]✅ Generated {len(generated_files)} process models in {output_path}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error generating models: {e}[/red]")
            
        return generated_files
    
    def xes_to_bpmn(self, xes_path: str, output_path: str) -> str:
        """
        Convert XES log to BPMN model (simplified).
        
        Args:
            xes_path: Path to XES file
            output_path: Path to save BPMN file
            
        Returns:
            Path to generated BPMN file
        """
        
        self.console.print(f"\n[cyan]🔄 Converting XES to BPMN: {xes_path}[/cyan]")
        
        # Analyze XES to get activities and flows
        analysis = self.analyze_xes(xes_path)
        
        # Create basic BPMN structure
        bpmn = ET.Element("definitions", {
            "xmlns": "http://www.omg.org/spec/BPMN/20100524/MODEL",
            "targetNamespace": "http://weavergen/mined"
        })
        
        process = ET.SubElement(bpmn, "process", {
            "id": "MinedProcess",
            "isExecutable": "true"
        })
        
        # Add start event
        start = ET.SubElement(process, "startEvent", {"id": "start"})
        
        # Add activities as service tasks
        activities = analysis.get("activity_list", analysis.get("start_activities", []))
        flow_id = 0
        
        prev_id = "start"
        for i, activity in enumerate(activities[:10]):  # Limit to 10 activities
            task_id = f"task_{i}"
            task = ET.SubElement(process, "serviceTask", {
                "id": task_id,
                "name": activity
            })
            
            # Add flow
            flow_id += 1
            ET.SubElement(process, "sequenceFlow", {
                "id": f"flow_{flow_id}",
                "sourceRef": prev_id,
                "targetRef": task_id
            })
            
            prev_id = task_id
        
        # Add end event
        end = ET.SubElement(process, "endEvent", {"id": "end"})
        flow_id += 1
        ET.SubElement(process, "sequenceFlow", {
            "id": f"flow_{flow_id}",
            "sourceRef": prev_id,
            "targetRef": "end"
        })
        
        # Save BPMN
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        xml_str = minidom.parseString(ET.tostring(bpmn)).toprettyxml(indent="  ")
        
        with open(output_file, 'w') as f:
            f.write(xml_str)
        
        self.console.print(f"[green]✅ Generated BPMN: {output_file}[/green]")
        
        return str(output_file)