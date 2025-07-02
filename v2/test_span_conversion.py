#!/usr/bin/env python3
"""
Test script for span file to mermaid conversion
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from weavergen.src.span_parser import SpanFileParser, SpanToMermaidConverter

def main():
    print("=== SPAN FILE TO MERMAID CONVERSION TEST ===\n")
    
    span_file = Path("sample_spans.json")
    
    if not span_file.exists():
        print(f"Error: {span_file} not found")
        return
    
    print(f"📁 Processing span file: {span_file}")
    
    # Parse span file
    parser = SpanFileParser()
    spans = parser.parse_file(span_file)
    
    print(f"✅ Parsed {len(spans)} spans")
    
    # Show span summary
    services = set(span.service_name for span in spans)
    traces = set(span.trace_id for span in spans)
    errors = [span for span in spans if span.error]
    
    print(f"   🏗️  Services: {len(services)} ({', '.join(sorted(services))})")
    print(f"   🔗 Traces: {len(traces)}")
    print(f"   ❌ Errors: {len(errors)}")
    print()
    
    # Convert to different diagram types
    converter = SpanToMermaidConverter(spans)
    
    # 1. Sequence Diagram
    print("1. SEQUENCE DIAGRAM")
    print("-" * 30)
    sequence_diagram = converter.to_sequence_diagram(max_spans=10, include_timing=True)
    print("```mermaid")
    print(sequence_diagram)
    print("```\n")
    
    # 2. Trace Flow Diagram
    print("2. TRACE FLOW DIAGRAM (First Trace)")
    print("-" * 30)
    first_trace = list(traces)[0]
    trace_diagram = converter.to_trace_flow_diagram(trace_id=first_trace)
    print("```mermaid")
    print(trace_diagram)
    print("```\n")
    
    # 3. Service Map
    print("3. SERVICE DEPENDENCY MAP")
    print("-" * 30)
    service_diagram = converter.to_service_map_diagram()
    print("```mermaid")
    print(service_diagram)
    print("```\n")
    
    # 4. Timeline
    print("4. TIMELINE DIAGRAM")
    print("-" * 30)
    timeline_diagram = converter.to_timeline_diagram(max_spans=8)
    print("```mermaid")
    print(timeline_diagram)
    print("```\n")
    
    # Show detailed span info
    print("5. SPAN DETAILS")
    print("-" * 30)
    for i, span in enumerate(spans[:5]):
        print(f"Span {i+1}: {span.operation_name}")
        print(f"   Service: {span.service_name}")
        print(f"   Duration: {span.duration_display}")
        print(f"   Status: {span.status_icon} {span.status}")
        if span.error:
            print(f"   Error: {span.attributes.get('error.message', 'Unknown error')}")
        print()

if __name__ == "__main__":
    main()