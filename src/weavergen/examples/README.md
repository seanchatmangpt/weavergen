# WeaverGen Examples

This directory contains examples of using pydantic-ai with various LLM providers.

## Structured Output Examples

### 1. Basic Structured Output (`structured_output_ollama.py`)

Demonstrates core pydantic-ai structured output features:
- **Basic Models**: Simple data extraction (City information)
- **Complex Nested Structures**: Recipe with ingredients and steps
- **Union Types and Enums**: Project management with tasks
- **Dynamic Schemas**: Runtime model generation
- **Output Modes**: JSON output and prompted output modes

```bash
python -m weavergen.examples.structured_output_ollama
```

### 2. Validation and Retries (`validation_retries_ollama.py`)

Shows advanced validation and error handling:
- **Field Validation**: Email, phone, regex patterns
- **Model Validation**: Cross-field validation, business rules
- **Automatic Retries**: Using `ModelRetry` for feedback
- **Complex Validation**: Financial data, code generation

```bash
python -m weavergen.examples.validation_retries_ollama
```

### 3. Streaming Output (`streaming_output_ollama.py`)

Demonstrates real-time streaming capabilities:
- **List Streaming**: Progressive todo list generation
- **Analysis Steps**: Step-by-step analysis with progress
- **Content Streaming**: Story generation with live updates
- **Custom Handlers**: Advanced streaming control

```bash
python -m weavergen.examples.streaming_output_ollama
```

## SQL Generation with Ollama

The SQL generation example demonstrates how to use pydantic-ai with Ollama (via OpenAI compatibility mode) to generate SQL queries from natural language descriptions.

### Files

- `sql_gen_ollama.py` - Full example with PostgreSQL validation
- `sql_gen_ollama_simple.py` - Simplified example without database dependency

### Prerequisites

1. **Install Ollama**
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Setup Check** (Recommended)
   ```bash
   # Run the setup checker to verify everything is configured
   python -m weavergen.examples.check_setup
   ```
   
   This will:
   - Check Ollama installation
   - Start the service if needed
   - Verify models are installed
   - Test the OpenAI compatibility endpoint
   - Run a quick validation test

3. **Pull a model** (if not already installed)
   ```bash
   # Recommended model
   ollama pull qwen3:latest
   
   # Alternatives
   ollama pull llama3.2:latest
   ollama pull mistral:latest
   ollama pull codellama:latest  # Better for code generation
   ```

4. **Install Python dependencies**
   ```bash
   pip install -e ".[examples]"
   ```

### Running the Examples

#### Simple Example (No Database)
```bash
python -m weavergen.examples.sql_gen_ollama_simple
```

#### Full Example with PostgreSQL

1. **Start PostgreSQL** (using Docker):
   ```bash
   docker run --rm -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres
   ```

2. **Run with database setup**:
   ```bash
   python -m weavergen.examples.sql_gen_ollama --setup "show me error logs"
   ```

3. **Run queries**:
   ```bash
   # Basic query
   python -m weavergen.examples.sql_gen_ollama "count logs by level"
   
   # With different model
   python -m weavergen.examples.sql_gen_ollama --model qwen2.5:latest "find logs with user_id"
   
   # With custom Ollama URL
   python -m weavergen.examples.sql_gen_ollama --ollama-url http://localhost:11434/v1 "show recent errors"
   ```

### How It Works

1. **Ollama OpenAI Compatibility**: Ollama provides an OpenAI-compatible API endpoint at `/v1`
2. **Pydantic-AI Integration**: Uses `OpenAIModel` with environment variables to point to Ollama
3. **Structured Output**: Defines `SqlQuery` model with validation
4. **Dynamic System Prompt**: Includes database schema and example queries
5. **Query Validation**: Uses PostgreSQL `EXPLAIN` to validate generated queries

### Example Output

```
Query: show me error logs

╭─ Query Explanation ─────────────────────────────────────╮
│ Retrieves all records with 'error' level, ordered by    │
│ creation time in descending order                       │
╰──────────────────────────────────────────────────────────╯

╭─ Generated SQL ─────────────────────────────────────────╮
│ 1  SELECT * FROM records                                │
│ 2  WHERE level = 'error'                                │
│ 3  ORDER BY created_at DESC                             │
│ 4  LIMIT 100                                            │
╰──────────────────────────────────────────────────────────╯
```

### Customization

- **Models**: Change `--model` to use different Ollama models
- **Schema**: Modify `SCHEMA` constant to match your database
- **Examples**: Add more query examples to `QUERY_EXAMPLES`
- **Validation**: Customize validation logic in `_validate_query`

### Troubleshooting

1. **"model not found"**: Pull the model first with `ollama pull <model>`
2. **Connection refused**: Ensure Ollama is running with `ollama serve`
3. **PostgreSQL errors**: Check database is running and accessible
4. **API errors**: Verify Ollama URL (default: `http://localhost:11434/v1`)

## New Features

### Error Handling (`ollama_utils.py`)

The examples now include robust error handling:

```python
from weavergen.examples.ollama_utils import get_ollama_model, handle_ollama_error

# Get model with automatic fallbacks
model = get_ollama_model(
    model_name="qwen3:latest",
    fallback_models=["llama3.2:latest", "mistral:latest"],
    check_connection=True
)

# Decorator for error handling
@handle_ollama_error
def main():
    # Your code here
    pass
```

### Setup Verification (`check_setup.py`)

Check your environment before running examples:

```bash
python -m weavergen.examples.check_setup
```

Features:
- Verifies Ollama installation
- Checks service status
- Lists available models
- Tests OpenAI compatibility
- Runs quick validation

### Integration Testing

Run the test suite to validate all examples:

```bash
# Run all integration tests
pytest tests/test_ollama_integration.py -v

# Run with Ollama-specific tests
pytest tests/test_ollama_integration.py -v -m ollama
```

## Common Patterns and Best Practices

### Using Ollama with pydantic-ai

All examples use Ollama through OpenAI compatibility mode:

```python
import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Configure Ollama
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"

# Create agent
agent = Agent(
    OpenAIModel(model_name="llama3.2:latest"),
    result_type=YourModel,
    system_prompt="Your instructions here"
)
```

### Structured Output Best Practices

1. **Field Descriptions**: Always include descriptions for clarity
   ```python
   name: str = Field(description="Person's full name")
   age: int = Field(gt=0, description="Age in years")
   ```

2. **Validation Layers**:
   - Field-level: Use `field_validator` for single field validation
   - Model-level: Use `model_validator` for cross-field validation
   - Agent-level: Use `result_validator` for business logic

3. **Retry Strategy**:
   ```python
   # In agent
   agent = Agent(..., retries=3)
   
   # In validator
   @agent.result_validator
   async def validate(ctx, result):
       if not_valid:
           raise ModelRetry("Specific feedback for the model")
       return result
   ```

4. **Streaming Considerations**:
   - Use `run_stream()` for progressive output
   - Handle partial results in `ModelResponseStreamEvent`
   - Always await `stream.get_data()` for final result

### Performance Tips

1. **Model Selection**: 
   - `qwen3:latest` - Best overall performance (recommended)
   - `llama3.2:latest` - Good balance of speed and quality
   - `mistral:latest` - Fast for simple tasks
   - `codellama:latest` - Optimized for code generation

2. **Batch Processing**: Process multiple items concurrently
   ```python
   tasks = [agent.run(prompt) for prompt in prompts]
   results = await asyncio.gather(*tasks)
   ```

3. **Caching**: Reuse agents for multiple queries
   ```python
   agent = Agent(...)  # Create once
   for prompt in prompts:
       result = await agent.run(prompt)  # Reuse
   ```