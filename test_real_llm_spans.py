#!/usr/bin/env python3
"""
Test the Pydantic AI BPMN pipeline with real LLM and comprehensive span analysis
"""

import asyncio
import os
import subprocess
from src.weavergen.pydantic_ai_bpmn_engine import PydanticAIBPMNEngine, PydanticAIContext

async def test_with_real_llm():
    print('🤖 Testing with REAL LLM agent and span capture...')
    
    # Check if Ollama is available
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print('⚠️  Ollama not available, using enhanced mock mode with real spans')
            use_real_llm = False
        else:
            print('✅ Ollama detected, using real LLM')
            models = result.stdout
            print(f'Available models: {models.strip()}')
            use_real_llm = 'llama' in models.lower() or 'mistral' in models.lower()
    except Exception as e:
        print(f'⚠️  Ollama check failed: {e}, using enhanced mock mode')
        use_real_llm = False
    
    # Create context for real LLM test
    context = PydanticAIContext(
        semantic_file='semantic_conventions/test_valid.yaml',
        output_dir='pydantic_ai_output_real',
        agent_roles=['analyst', 'coordinator']  # Reduce for faster testing
    )
    
    # Try to force real LLM usage if we have any model available
    if not use_real_llm and 'qwen' in models.lower():
        print('🔄 Attempting to use Qwen model for real LLM testing...')
        use_real_llm = True
        model_name = 'qwen3:latest'
    elif not use_real_llm and 'phi' in models.lower():
        print('🔄 Attempting to use Phi model for real LLM testing...')
        use_real_llm = True  
        model_name = 'phi4-reasoning:plus'
    else:
        model_name = 'gpt-4o-mini'
    
    # Use real LLM if available, otherwise enhanced mock
    engine = PydanticAIBPMNEngine(
        model_name=model_name if use_real_llm else 'gpt-4o-mini',
        use_mock=not use_real_llm
    )
    
    print(f'🔧 Engine mode: {"REAL LLM" if not engine.use_mock else "ENHANCED MOCK"}')
    
    try:
        # Execute the workflow
        result = await engine.execute_workflow('PydanticAIGeneration', context)
        
        print('\n🎯 EXECUTION RESULTS:')
        print(f'  Success: {result.get("success", False)}')
        print(f'  Models Generated: {result.get("models_generated", 0)}')
        print(f'  Agents Generated: {result.get("agents_generated", 0)}')
        print(f'  Spans Captured: {len(result.get("spans", []))}')
        print(f'  Quality Score: {result.get("quality_score", 0):.2%}')
        
        # Analyze captured spans
        spans = result.get('spans', [])
        print(f'\n📊 SPAN ANALYSIS ({len(spans)} total spans):')
        
        for i, span in enumerate(spans[:5]):  # Show first 5 spans
            span_name = span.get('name', span.get('task', 'unknown'))
            duration = span.get('duration_ms', 0)
            status = span.get('status', 'unknown')
            timestamp = span.get('timestamp', 'unknown')
            
            print(f'  Span {i+1}: {span_name}')
            print(f'    ⏱️  Duration: {duration}ms')
            print(f'    📍 Status: {status}')
            print(f'    🕒 Time: {timestamp}')
            print(f'    🔗 Trace ID: {span.get("trace_id", "unknown")}')
            
            # Show task result summary
            task_result = span.get('result', {})
            if isinstance(task_result, dict):
                if 'models' in task_result:
                    print(f'    📋 Generated {len(task_result["models"])} models')
                elif 'agents' in task_result:
                    print(f'    🤖 Generated {len(task_result["agents"])} agents')
                elif 'quality_score' in task_result:
                    print(f'    ⭐ Quality: {task_result["quality_score"]:.2%}')
            print()
        
        if len(spans) > 5:
            print(f'  ... and {len(spans) - 5} more spans')
        
        # Generate detailed execution report
        table = engine.generate_execution_report(result)
        from rich.console import Console
        console = Console()
        print('\n📋 DETAILED EXECUTION REPORT:')
        console.print(table)
        
        # Generate Mermaid trace
        mermaid = engine.generate_mermaid_trace(result)
        print('\n🔗 BPMN Execution Trace (Mermaid):')
        print(mermaid)
        
        # Test span validation specifically
        print('\n🔍 SPAN VALIDATION TEST:')
        from src.weavergen.span_validator import SpanValidator
        validator = SpanValidator()
        validation_result = validator.validate_spans(spans)
        
        print(f'  Health Score: {validation_result.health_score:.2%}')
        print(f'  Semantic Compliance: {validation_result.semantic_compliance:.2%}')
        print(f'  Performance Score: {validation_result.performance_score:.2%}')
        print(f'  Coverage Score: {validation_result.coverage_score:.2%}')
        print(f'  Total Spans: {validation_result.total_spans}')
        print(f'  Valid Spans: {validation_result.valid_spans}')
        print(f'  Total Issues: {len(validation_result.issues)}')
        
        if validation_result.issues:
            print('  Issues found:')
            for issue in validation_result.issues[:3]:
                print(f'    ⚠️  {issue}')
        
        return result
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    asyncio.run(test_with_real_llm())