"""Simple SQL Generation Example with Ollama - No DB dependency for testing."""

import os
from datetime import date
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax


# Database schema for the example
SCHEMA = """
CREATE TABLE records (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    span_id CHAR(16) NOT NULL,
    trace_id CHAR(32) NOT NULL,
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}'::JSONB
);
CREATE INDEX idx_created_at ON records(created_at);
CREATE INDEX idx_level ON records(level);
CREATE INDEX idx_attributes ON records USING GIN(attributes);
"""

# Example queries to help guide the model
QUERY_EXAMPLES = [
    ("show me error logs from yesterday", 
     "SELECT * FROM records WHERE level = 'error' AND created_at >= CURRENT_DATE - INTERVAL '1 day' AND created_at < CURRENT_DATE ORDER BY created_at DESC"),
    ("count logs by level in the last hour",
     "SELECT level, COUNT(*) as count FROM records WHERE created_at >= NOW() - INTERVAL '1 hour' GROUP BY level ORDER BY count DESC"),
]


class SqlQuery(BaseModel):
    """Validated SQL query output."""
    
    query: str = Field(description="SQL query to execute")
    explanation: str = Field(description="Brief explanation of what the query does")
    
    @field_validator("query")
    @classmethod
    def validate_select_query(cls, v: str) -> str:
        """Ensure query is a SELECT statement for safety."""
        if not v.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")
        return v


def main():
    """Run simple SQL generation example."""
    console = Console()
    
    # Set up Ollama via environment variables
    os.environ["OPENAI_API_KEY"] = "ollama"
    os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
    
    # Build system prompt
    examples = "\n\n".join(
        f"User: {q}\nSQL: {sql}"
        for q, sql in QUERY_EXAMPLES
    )
    
    system_prompt = f"""You are a PostgreSQL expert that generates SQL queries.

Database Schema:
{SCHEMA}

Today's date: {date.today()}

Example queries:
{examples}

Important rules:
1. Only generate SELECT queries (no modifications)
2. Use proper PostgreSQL syntax and functions
3. For JSON attributes, use JSONB operators (?, @>, ->, ->>, etc.)
4. Always include appropriate ORDER BY and LIMIT clauses
5. Use indexes efficiently (created_at, level, attributes)
6. Provide clear explanations of what each query does
"""
    
    # Create agent
    agent = Agent(
        model=OpenAIModel(model_name="llama3.2:latest"),
        result_type=SqlQuery,
        system_prompt=system_prompt
    )
    
    # Test queries
    test_queries = [
        "show me all error logs",
        "count logs by level",
        "find logs with user_id attribute",
    ]
    
    console.print("[bold blue]SQL Generation with Ollama Example[/bold blue]\n")
    
    for query in test_queries:
        console.print(f"[yellow]Query:[/yellow] {query}")
        
        try:
            # Run synchronously for simplicity
            result = agent.run_sync(query)
            
            # Display explanation
            console.print(Panel(
                result.data.explanation,
                title="Query Explanation",
                border_style="blue"
            ))
            
            # Display SQL with syntax highlighting
            syntax = Syntax(
                result.data.query, 
                "sql", 
                theme="monokai", 
                line_numbers=True
            )
            console.print(Panel(
                syntax,
                title="Generated SQL",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        
        console.print("\n" + "-"*60 + "\n")


if __name__ == "__main__":
    main()