# WeaverGen Examples

This directory contains examples of using pydantic-ai with various LLM providers.

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

2. **Start Ollama service**
   ```bash
   ollama serve
   ```

3. **Pull a model**
   ```bash
   # Choose one of these models
   ollama pull llama3.2:latest
   ollama pull qwen2.5:latest
   ollama pull codellama:latest
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