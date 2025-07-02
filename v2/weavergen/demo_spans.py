#!/usr/bin/env python
"""Demo script showing WeaverGen v2 OpenTelemetry span support."""

import json
import time
from src.weavergen.cli_debug import enable_span_capture, _span_storage
from src.weavergen.engine.simple_engine import SimpleBpmnEngine
from src.weavergen.engine.service_task import WeaverGenServiceEnvironment
from src.weavergen.enhanced_instrumentation import cli_command_span, add_span_event

def main():
    print("🔍 WeaverGen v2 OpenTelemetry Span Demo")
    print("=" * 60)
    
    # Enable span capture
    enable_span_capture()
    print("✓ Span capture enabled\n")
    
    # Clear previous spans
    _span_storage.clear()
    
    # Initialize engine
    script_env = WeaverGenServiceEnvironment()
    engine = SimpleBpmnEngine(script_env)
    
    # 1. Add workflows with span tracking
    print("1️⃣  Adding workflows...")
    with cli_command_span("demo.add_workflows", {"count": 2}):
        engine.add_spec("SimpleWorkflow", ["bpmn/simple_workflow.bpmn"])
        print("   ✓ Added SimpleWorkflow")
        
        engine.add_spec("SemanticGeneration", ["bpmn/semantic_generation.bpmn"])
        print("   ✓ Added SemanticGeneration")
    
    # 2. Run simple workflow
    print("\n2️⃣  Running SimpleWorkflow...")
    with cli_command_span("demo.run_simple", {"workflow": "SimpleWorkflow"}):
        instance = engine.start_workflow("SimpleWorkflow")
        instance.run_until_user_input_required()
        print(f"   Status: {'Completed' if instance.workflow.is_completed() else 'Active'}")
    
    # 3. Run semantic generation with service tasks
    print("\n3️⃣  Running SemanticGeneration with service tasks...")
    with cli_command_span("demo.run_semantic", {"workflow": "SemanticGeneration"}):
        instance = engine.start_workflow("SemanticGeneration")
        instance.workflow.data.update({
            "semantic_file": "test.yaml",
            "target_language": "python"
        })
        
        add_span_event("demo.data_set", {
            "semantic_file": "test.yaml",
            "target_language": "python"
        })
        
        try:
            instance.run_until_user_input_required()
            print(f"   Status: {'Completed' if instance.workflow.is_completed() else 'Active'}")
        except Exception as e:
            print(f"   Note: {e}")
    
    # Wait for spans to be exported
    time.sleep(0.5)
    
    # 4. Show captured spans
    print("\n4️⃣  Captured Spans Summary:")
    spans = _span_storage.get_finished_spans()
    print(f"   Total spans: {len(spans)}")
    
    # Group by type
    by_type = {}
    for span in spans:
        span_type = span.attributes.get("weaver.type", "unknown")
        by_type[span_type] = by_type.get(span_type, 0) + 1
    
    print("\n   By Type:")
    for span_type, count in sorted(by_type.items()):
        print(f"   • {span_type}: {count}")
    
    # Show some example spans
    print("\n   Recent Spans:")
    for span in spans[-5:]:
        duration = (span.end_time - span.start_time) / 1e6 if span.end_time else 0
        print(f"   • {span.name} [{duration:.2f}ms] - {span.attributes.get('weaver.type', 'unknown')}")
    
    # 5. Show span events
    print("\n5️⃣  Span Events:")
    event_count = 0
    for span in spans:
        event_count += len(span.events)
    print(f"   Total events: {event_count}")
    
    # Show last few events
    all_events = []
    for span in spans:
        for event in span.events:
            all_events.append((span.name, event))
    
    print("\n   Recent Events:")
    for span_name, event in all_events[-5:]:
        print(f"   • [{span_name}] {event.name}")
        if event.attributes:
            for k, v in list(event.attributes.items())[:2]:
                print(f"     - {k}: {v}")
    
    print("\n✨ Span demo complete!")
    print("\n💡 Try these commands to explore spans:")
    print("   uv run weavergen debug spans")
    print("   uv run weavergen debug stats")
    print("   uv run weavergen debug trace SemanticGeneration")
    print("   uv run weavergen debug export spans.json")

if __name__ == "__main__":
    main()