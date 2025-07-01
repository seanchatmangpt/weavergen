#!/usr/bin/env python3
"""
Direct test of Ollama integration with Pydantic AI
"""

import asyncio
import os

async def test_ollama_pydantic_ai():
    print('🤖 Testing direct Ollama + Pydantic AI integration...')
    
    try:
        # Try to import and use Pydantic AI with Ollama
        from pydantic_ai import Agent
        
        # Create an agent with Ollama model - try different formats
        model_formats = [
            'qwen3:latest',
            'openai:qwen3',  # Different format
            'groq:llama3-8b-8192'  # Fallback to Groq if available
        ]
        
        agent = None
        for model_format in model_formats:
            try:
                print(f'🔄 Trying model format: {model_format}')
                agent = Agent(
                    model_format,
                    system_prompt="You are a helpful assistant. Generate a simple Pydantic model for a user profile."
                )
                print(f'✅ Successfully created agent with: {model_format}')
                break
            except Exception as e:
                print(f'❌ Failed with {model_format}: {e}')
                continue
        
        if not agent:
            print('❌ Could not create agent with any model format')
            return None
        
        print('✅ Agent created successfully')
        print('🔄 Running inference test...')
        
        # Test the agent
        result = await agent.run("Create a Pydantic model for a user with name, email, and age fields")
        
        print('✅ Inference completed!')
        print(f'📋 Result type: {type(result)}')
        print(f'📄 Result: {result}')
        
        return result
        
    except ImportError as e:
        print(f'❌ Import error: {e}')
        print('💡 You may need to install pydantic-ai: pip install pydantic-ai')
        return None
    except Exception as e:
        print(f'❌ Ollama test failed: {e}')
        print(f'🔍 Error type: {type(e)}')
        import traceback
        traceback.print_exc()
        return None

async def test_ollama_direct():
    print('🔄 Testing Ollama direct connection...')
    
    try:
        import subprocess
        
        # Test ollama list
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        print(f'📋 Ollama models: {result.stdout}')
        
        # Test simple generation
        result = subprocess.run([
            'ollama', 'run', 'qwen3:latest', 
            'Write one sentence about Python programming.'
        ], capture_output=True, text=True, timeout=30)
        
        print(f'✅ Ollama response: {result.stdout.strip()}')
        return True
        
    except Exception as e:
        print(f'❌ Direct Ollama test failed: {e}')
        return False

if __name__ == '__main__':
    print('🧪 OLLAMA INTEGRATION TESTS')
    print('=' * 40)
    
    # Test direct Ollama
    ollama_works = asyncio.run(test_ollama_direct())
    
    print('\n' + '=' * 40)
    
    # Test Pydantic AI with Ollama
    if ollama_works:
        asyncio.run(test_ollama_pydantic_ai())
    else:
        print('⚠️ Skipping Pydantic AI test - Ollama not working')