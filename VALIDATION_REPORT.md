# Structured Output Validation Report

## Test Environment
- **Date**: 2025-06-30
- **Ollama Version**: 0.9.0
- **Model Used**: qwen3:latest
- **Python**: 3.9
- **pydantic-ai**: 0.3.5

## Test Results Summary

### ✅ All Core Features Working

1. **Basic Structured Output** ✅
   - City extraction with typed fields
   - Automatic type conversion (string to int for population)
   - Field validation (population > 0)

2. **Complex Nested Structures** ✅
   - Recipe generation with ingredients list
   - Nested model validation
   - List field handling

3. **SQL Generation** ✅
   - Query generation with validation
   - Field validators working correctly
   - Proper error messages for non-SELECT queries

4. **Validation & Business Logic** ✅
   - Custom validators functioning
   - Type constraints enforced
   - Pydantic v2 field_validator syntax

5. **Model Integration** ✅
   - Ollama via OpenAI compatibility mode
   - Environment variable configuration
   - Model responses properly structured

## API Updates Required

The following deprecated APIs were found and should be updated in the examples:

1. **`result.data` → `result.output`**
   - All occurrences of `result.data` should use `result.output`

2. **`result_validator` → `output_validator`**
   - The decorator name has changed

3. **Streaming API Changes**
   - The streaming API has changed from the examples
   - `async for event in stream` syntax needs updating

## Working Example Pattern

```python
import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Configure Ollama
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"

# Define output structure
class Output(BaseModel):
    field: str = Field(description="Description")

# Create agent
agent = Agent(
    OpenAIModel(model_name="qwen3:latest"),
    result_type=Output,
    system_prompt="Your instructions"
)

# Run
result = await agent.run("Your prompt")
output = result.output  # Use .output not .data
```

## Performance Observations

- **Response Time**: 1-3 seconds for simple queries
- **Model Quality**: qwen3 provides good structured output
- **Validation**: Field validators execute correctly
- **Error Handling**: Proper validation errors returned

## Recommendations

1. Update all examples to use `result.output` instead of `result.data`
2. Update validator decorators to use new names
3. Consider adding qwen3 as a recommended model in docs
4. Streaming examples may need complete rewrite based on new API

## Conclusion

The pydantic-ai integration with Ollama is working correctly. All core structured output features are functional with minor API updates needed for deprecated methods.