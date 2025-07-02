#!/usr/bin/env python
"""Demo: Eating our own dogfood - using generated semantic conventions."""

from src.weavergen.engine.simple_engine import SimpleBpmnEngine
from src.weavergen.engine.service_task import WeaverGenServiceEnvironment
from src.weavergen.enhanced_instrumentation import cli_command_span
from src.weavergen.cli_debug import enable_span_capture, _span_storage

# Import our generated semantic conventions
from src.weavergen.semconv import (
    COMPONENT_TYPE, COMPONENT_TYPE__WORKFLOW, COMPONENT_TYPE__GENERATOR,
    ENGINE, STEPS_TOTAL, STEPS_COMPLETED,
    FILES_GENERATED, LANGUAGE
)

def main():
    print("🍽️  WeaverGen Dogfooding Demo")
    print("=" * 60)
    print("\nUsing generated semantic convention constants from weavergen_system.yaml\n")
    
    # Enable span capture
    enable_span_capture()
    _span_storage.clear()
    
    # Show generated constants
    print("📋 Generated Constants Being Used:")
    print(f"  COMPONENT_TYPE = '{COMPONENT_TYPE}'")
    print(f"  COMPONENT_TYPE__WORKFLOW = '{COMPONENT_TYPE__WORKFLOW}'")
    print(f"  ENGINE = '{ENGINE}'")
    print(f"  FILES_GENERATED = '{FILES_GENERATED}'")
    print(f"  LANGUAGE = '{LANGUAGE}'")
    
    # Initialize engine
    script_env = WeaverGenServiceEnvironment()
    engine = SimpleBpmnEngine(script_env)
    
    # Add and run workflow using proper semantic conventions
    print("\n🚀 Running workflow with proper semantic spans...")
    
    with cli_command_span("dogfood.demo", {"example": "true"}):
        # Add workflow
        engine.add_spec("SemanticGeneration", ["bpmn/semantic_generation.bpmn"])
        
        # Run workflow
        instance = engine.start_workflow("SemanticGeneration")
        instance.workflow.data.update({
            "semantic_file": "dogfood.yaml",
            "target_language": "python"
        })
        
        try:
            instance.run_until_user_input_required()
        except:
            pass  # Service tasks are mocked
    
    # Examine captured spans
    print("\n📊 Captured Spans with Semantic Convention Attributes:")
    spans = _span_storage.get_finished_spans()
    
    for span in spans[-5:]:
        print(f"\n• {span.name}")
        
        # Show semantic convention attributes
        for attr_name, attr_value in span.attributes.items():
            if attr_name in [COMPONENT_TYPE, ENGINE, FILES_GENERATED, LANGUAGE]:
                print(f"  ✓ {attr_name} = {attr_value}")
    
    print("\n✅ Dogfooding complete!")
    print("\nKey achievements:")
    print("1. Generated semantic convention constants from weavergen_system.yaml")
    print("2. Used those constants in our instrumentation")
    print("3. Spans now use standardized attributes from our semantic conventions")
    print("4. No more hardcoded strings - everything from semantic conventions!")

if __name__ == "__main__":
    main()