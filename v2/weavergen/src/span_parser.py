"""
OpenTelemetry Span File Parser for Mermaid Conversion
Supports multiple span formats and generates rich mermaid visualizations
"""

import json
import csv
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime, timezone
import re
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ParsedSpan:
    """Structured span data for mermaid generation"""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    status: str
    error: bool
    attributes: Dict[str, Any]
    events: List[Dict[str, Any]]
    tags: Dict[str, str]
    
    @property
    def duration_display(self) -> str:
        """Human readable duration"""
        if self.duration_ms < 1:
            return f"{self.duration_ms * 1000:.1f}μs"
        elif self.duration_ms < 1000:
            return f"{self.duration_ms:.1f}ms"
        else:
            return f"{self.duration_ms / 1000:.2f}s"
    
    @property
    def status_icon(self) -> str:
        """Status icon for display"""
        if self.error:
            return "❌"
        elif self.status.lower() in ["ok", "success"]:
            return "✅"
        else:
            return "⏳"


class SpanFileParser:
    """Parser for various OpenTelemetry span file formats"""
    
    def __init__(self):
        self.spans: List[ParsedSpan] = []
        self.trace_tree: Dict[str, List[ParsedSpan]] = defaultdict(list)
        self.service_spans: Dict[str, List[ParsedSpan]] = defaultdict(list)
        
    def parse_file(self, file_path: Path) -> List[ParsedSpan]:
        """Parse span file and return structured spans"""
        if not file_path.exists():
            raise FileNotFoundError(f"Span file not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.json':
            return self._parse_json_file(file_path)
        elif file_ext == '.jsonl':
            return self._parse_jsonl_file(file_path)
        elif file_ext == '.csv':
            return self._parse_csv_file(file_path)
        elif file_ext in ['.txt', '.log']:
            return self._parse_log_file(file_path)
        else:
            # Try to detect format from content
            return self._auto_detect_and_parse(file_path)
    
    def _parse_json_file(self, file_path: Path) -> List[ParsedSpan]:
        """Parse JSON format span file"""
        with open(file_path) as f:
            data = json.load(f)
        
        spans = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            # Array of spans
            for span_data in data:
                span = self._parse_span_object(span_data)
                if span:
                    spans.append(span)
        elif isinstance(data, dict):
            if 'spans' in data:
                # Structured format with spans array
                for span_data in data['spans']:
                    span = self._parse_span_object(span_data)
                    if span:
                        spans.append(span)
            elif 'resourceSpans' in data:
                # OTLP format
                spans = self._parse_otlp_format(data)
            else:
                # Single span object
                span = self._parse_span_object(data)
                if span:
                    spans.append(span)
        
        self._build_indexes(spans)
        return spans
    
    def _parse_jsonl_file(self, file_path: Path) -> List[ParsedSpan]:
        """Parse JSON Lines format"""
        spans = []
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        span_data = json.loads(line)
                        span = self._parse_span_object(span_data)
                        if span:
                            spans.append(span)
                    except json.JSONDecodeError:
                        continue
        
        self._build_indexes(spans)
        return spans
    
    def _parse_csv_file(self, file_path: Path) -> List[ParsedSpan]:
        """Parse CSV format span file"""
        spans = []
        with open(file_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                span = self._parse_csv_row(row)
                if span:
                    spans.append(span)
        
        self._build_indexes(spans)
        return spans
    
    def _parse_log_file(self, file_path: Path) -> List[ParsedSpan]:
        """Parse log format span file"""
        spans = []
        with open(file_path) as f:
            content = f.read()
            
        # Try to extract JSON objects from log lines
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, content)
        
        for match in matches:
            try:
                span_data = json.loads(match)
                span = self._parse_span_object(span_data)
                if span:
                    spans.append(span)
            except json.JSONDecodeError:
                continue
        
        self._build_indexes(spans)
        return spans
    
    def _auto_detect_and_parse(self, file_path: Path) -> List[ParsedSpan]:
        """Auto-detect format and parse"""
        with open(file_path) as f:
            content = f.read(1024)  # Read first 1KB
        
        if content.strip().startswith('{') or content.strip().startswith('['):
            return self._parse_json_file(file_path)
        elif ',' in content and '\n' in content:
            return self._parse_csv_file(file_path)
        else:
            return self._parse_log_file(file_path)
    
    def _parse_span_object(self, span_data: Dict[str, Any]) -> Optional[ParsedSpan]:
        """Parse individual span object"""
        try:
            # Extract basic span info with flexible field names
            span_id = self._extract_field(span_data, ['spanId', 'span_id', 'id', 'spanID'])
            trace_id = self._extract_field(span_data, ['traceId', 'trace_id', 'traceID'])
            parent_span_id = self._extract_field(span_data, ['parentSpanId', 'parent_span_id', 'parentID'])
            
            operation_name = self._extract_field(span_data, ['operationName', 'operation_name', 'name', 'spanName'])
            service_name = self._extract_field(span_data, ['serviceName', 'service_name', 'service']) or "unknown-service"
            
            # Parse timestamps
            start_time = self._parse_timestamp(self._extract_field(span_data, ['startTime', 'start_time', 'timestamp']))
            end_time = self._parse_timestamp(self._extract_field(span_data, ['endTime', 'end_time', 'finishTime']))
            
            if not end_time and 'duration' in span_data:
                duration = span_data['duration']
                if isinstance(duration, (int, float)):
                    end_time = start_time + datetime.timedelta(microseconds=duration)
            
            # Calculate duration
            if start_time and end_time:
                duration_ms = (end_time - start_time).total_seconds() * 1000
            else:
                duration_ms = float(self._extract_field(span_data, ['duration', 'durationMs']) or 0)
            
            # Extract status and error info
            status = self._extract_field(span_data, ['status', 'statusCode']) or "unknown"
            error = self._is_error_span(span_data)
            
            # Extract attributes and tags
            attributes = span_data.get('attributes', {}) or span_data.get('tags', {}) or {}
            events = span_data.get('events', []) or span_data.get('logs', []) or []
            tags = span_data.get('tags', {}) or {}
            
            return ParsedSpan(
                span_id=span_id or "unknown",
                trace_id=trace_id or "unknown",
                parent_span_id=parent_span_id,
                operation_name=operation_name or "unknown-operation",
                service_name=service_name,
                start_time=start_time or datetime.now(timezone.utc),
                end_time=end_time or datetime.now(timezone.utc),
                duration_ms=duration_ms,
                status=status,
                error=error,
                attributes=attributes,
                events=events,
                tags=tags
            )
            
        except Exception as e:
            print(f"Error parsing span: {e}")
            return None
    
    def _parse_csv_row(self, row: Dict[str, str]) -> Optional[ParsedSpan]:
        """Parse CSV row into span"""
        try:
            return ParsedSpan(
                span_id=row.get('span_id', ''),
                trace_id=row.get('trace_id', ''),
                parent_span_id=row.get('parent_span_id'),
                operation_name=row.get('operation_name', ''),
                service_name=row.get('service_name', 'unknown'),
                start_time=self._parse_timestamp(row.get('start_time')),
                end_time=self._parse_timestamp(row.get('end_time')),
                duration_ms=float(row.get('duration_ms', 0)),
                status=row.get('status', 'unknown'),
                error=row.get('error', '').lower() in ['true', '1', 'yes'],
                attributes={},
                events=[],
                tags={}
            )
        except Exception:
            return None
    
    def _parse_otlp_format(self, data: Dict[str, Any]) -> List[ParsedSpan]:
        """Parse OTLP (OpenTelemetry Protocol) format"""
        spans = []
        
        for resource_span in data.get('resourceSpans', []):
            resource_attrs = resource_span.get('resource', {}).get('attributes', [])
            service_name = self._extract_service_name_from_attrs(resource_attrs)
            
            for scope_span in resource_span.get('scopeSpans', []):
                for span_data in scope_span.get('spans', []):
                    span_data['serviceName'] = service_name
                    span = self._parse_span_object(span_data)
                    if span:
                        spans.append(span)
        
        return spans
    
    def _extract_field(self, data: Dict[str, Any], field_names: List[str]) -> Any:
        """Extract field value trying multiple possible names"""
        for field_name in field_names:
            if field_name in data:
                return data[field_name]
        return None
    
    def _parse_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """Parse various timestamp formats"""
        if not timestamp:
            return None
        
        try:
            if isinstance(timestamp, (int, float)):
                # Assume Unix timestamp in seconds or nanoseconds
                if timestamp > 1e12:  # Nanoseconds
                    return datetime.fromtimestamp(timestamp / 1e9, timezone.utc)
                else:  # Seconds
                    return datetime.fromtimestamp(timestamp, timezone.utc)
            elif isinstance(timestamp, str):
                # Try various ISO formats
                for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(timestamp, fmt).replace(tzinfo=timezone.utc)
                    except ValueError:
                        continue
        except Exception:
            pass
        
        return None
    
    def _is_error_span(self, span_data: Dict[str, Any]) -> bool:
        """Determine if span represents an error"""
        status = span_data.get('status', {})
        if isinstance(status, dict):
            return status.get('code') == 'ERROR' or status.get('message') is not None
        
        tags = span_data.get('tags', {})
        return tags.get('error') == 'true' or tags.get('error') is True
    
    def _extract_service_name_from_attrs(self, attributes: List[Dict[str, Any]]) -> str:
        """Extract service name from OTLP attributes"""
        for attr in attributes:
            if attr.get('key') == 'service.name':
                return attr.get('value', {}).get('stringValue', 'unknown-service')
        return 'unknown-service'
    
    def _build_indexes(self, spans: List[ParsedSpan]):
        """Build indexes for efficient querying"""
        self.spans = spans
        self.trace_tree.clear()
        self.service_spans.clear()
        
        for span in spans:
            self.trace_tree[span.trace_id].append(span)
            self.service_spans[span.service_name].append(span)
    
    def get_trace_tree(self, trace_id: str) -> List[ParsedSpan]:
        """Get all spans for a trace"""
        return self.trace_tree.get(trace_id, [])
    
    def get_service_spans(self, service_name: str) -> List[ParsedSpan]:
        """Get all spans for a service"""
        return self.service_spans.get(service_name, [])
    
    def get_root_spans(self) -> List[ParsedSpan]:
        """Get spans that have no parent"""
        return [span for span in self.spans if not span.parent_span_id]
    
    def get_span_children(self, parent_span_id: str) -> List[ParsedSpan]:
        """Get child spans of a parent"""
        return [span for span in self.spans if span.parent_span_id == parent_span_id]


class SpanToMermaidConverter:
    """Convert parsed spans to various mermaid diagram formats"""
    
    def __init__(self, spans: List[ParsedSpan]):
        self.spans = spans
        self.parser = SpanFileParser()
        self.parser._build_indexes(spans)
    
    def to_sequence_diagram(self, max_spans: int = 50, include_timing: bool = True) -> str:
        """Convert spans to mermaid sequence diagram"""
        lines = ["sequenceDiagram"]
        
        # Get unique services
        services = sorted(set(span.service_name for span in self.spans[:max_spans]))
        
        # Add participants
        for service in services:
            sanitized = self._sanitize_name(service)
            lines.append(f"    participant {sanitized}")
        
        # Add span interactions
        for span in self.spans[:max_spans]:
            service = self._sanitize_name(span.service_name)
            
            if span.parent_span_id:
                # Find parent span
                parent = next((s for s in self.spans if s.span_id == span.parent_span_id), None)
                if parent:
                    parent_service = self._sanitize_name(parent.service_name)
                    lines.append(f"    {parent_service}->>{service}: {span.operation_name}")
                else:
                    lines.append(f"    Client->>{service}: {span.operation_name}")
            else:
                lines.append(f"    Client->>{service}: {span.operation_name}")
            
            if include_timing:
                lines.append(f"    Note over {service}: {span.duration_display} {span.status_icon}")
        
        return "\n".join(lines)
    
    def to_trace_flow_diagram(self, trace_id: Optional[str] = None) -> str:
        """Convert spans to trace flow diagram"""
        if trace_id:
            spans = self.parser.get_trace_tree(trace_id)
        else:
            spans = self.spans
        
        lines = ["graph TD"]
        lines.append(f"    %% Trace Flow ({len(spans)} spans)")
        
        # Add nodes for each span
        for i, span in enumerate(spans):
            node_id = f"S{i}"
            status_color = "fill:#ffebee,stroke:#f44336" if span.error else "fill:#e8f5e9,stroke:#4caf50"
            
            lines.append(f"    {node_id}[\"{span.operation_name}<br/>{span.service_name}<br/>{span.duration_display}\"]")
            lines.append(f"    classDef span{i} {status_color}")
            lines.append(f"    class {node_id} span{i}")
        
        # Add connections based on parent-child relationships
        span_to_node = {span.span_id: f"S{i}" for i, span in enumerate(spans)}
        
        for i, span in enumerate(spans):
            if span.parent_span_id and span.parent_span_id in span_to_node:
                parent_node = span_to_node[span.parent_span_id]
                child_node = f"S{i}"
                lines.append(f"    {parent_node} --> {child_node}")
        
        return "\n".join(lines)
    
    def to_service_map_diagram(self) -> str:
        """Convert spans to service dependency map"""
        lines = ["graph LR"]
        lines.append("    %% Service Dependency Map")
        
        services = set()
        connections = set()
        
        for span in self.spans:
            services.add(span.service_name)
            
            if span.parent_span_id:
                parent = next((s for s in self.spans if s.span_id == span.parent_span_id), None)
                if parent and parent.service_name != span.service_name:
                    connections.add((parent.service_name, span.service_name))
        
        # Add service nodes
        for service in sorted(services):
            sanitized = self._sanitize_name(service)
            span_count = len(self.parser.get_service_spans(service))
            error_count = len([s for s in self.parser.get_service_spans(service) if s.error])
            
            if error_count > 0:
                lines.append(f"    {sanitized}[\"{service}<br/>{span_count} spans<br/>{error_count} errors\"]")
                lines.append(f"    classDef {sanitized}_class fill:#ffebee,stroke:#f44336")
            else:
                lines.append(f"    {sanitized}[\"{service}<br/>{span_count} spans\"]")
                lines.append(f"    classDef {sanitized}_class fill:#e8f5e9,stroke:#4caf50")
            
            lines.append(f"    class {sanitized} {sanitized}_class")
        
        # Add connections
        for from_service, to_service in connections:
            from_sanitized = self._sanitize_name(from_service)
            to_sanitized = self._sanitize_name(to_service)
            lines.append(f"    {from_sanitized} --> {to_sanitized}")
        
        return "\n".join(lines)
    
    def to_timeline_diagram(self, max_spans: int = 20) -> str:
        """Convert spans to timeline gantt diagram"""
        lines = ["gantt"]
        lines.append("    title Span Timeline")
        lines.append("    dateFormat X")
        lines.append("    axisFormat %H:%M:%S")
        
        # Sort spans by start time
        sorted_spans = sorted(self.spans[:max_spans], key=lambda s: s.start_time)
        
        if not sorted_spans:
            return "gantt\n    title No Spans Found"
        
        # Calculate relative times
        base_time = sorted_spans[0].start_time
        
        current_service = None
        for span in sorted_spans:
            if span.service_name != current_service:
                current_service = span.service_name
                lines.append(f"    section {current_service}")
            
            start_offset = int((span.start_time - base_time).total_seconds())
            end_offset = int((span.end_time - base_time).total_seconds())
            
            status = "crit" if span.error else "done" if span.status.lower() == "ok" else "active"
            lines.append(f"    {span.operation_name[:20]} :{status}, {start_offset}, {end_offset}")
        
        return "\n".join(lines)
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for mermaid"""
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)


def convert_span_file_to_mermaid(
    file_path: Path, 
    diagram_type: str = "sequence",
    max_spans: int = 50,
    trace_id: Optional[str] = None,
    output_file: Optional[Path] = None
) -> str:
    """Main function to convert span file to mermaid diagram"""
    
    parser = SpanFileParser()
    spans = parser.parse_file(file_path)
    
    if not spans:
        return "No spans found in file"
    
    converter = SpanToMermaidConverter(spans)
    
    if diagram_type == "sequence":
        diagram = converter.to_sequence_diagram(max_spans=max_spans)
    elif diagram_type == "trace":
        diagram = converter.to_trace_flow_diagram(trace_id=trace_id)
    elif diagram_type == "service":
        diagram = converter.to_service_map_diagram()
    elif diagram_type == "timeline":
        diagram = converter.to_timeline_diagram(max_spans=max_spans)
    else:
        raise ValueError(f"Unknown diagram type: {diagram_type}")
    
    # Wrap in code block
    full_diagram = f"```mermaid\n{diagram}\n```"
    
    if output_file:
        output_file.write_text(full_diagram)
    
    return full_diagram