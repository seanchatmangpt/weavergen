"""SQL Generation Example with Ollama.

This example demonstrates using pydantic-ai with Ollama to generate SQL queries
from natural language descriptions. Based on the pydantic-ai SQL generation example
but adapted to use Ollama instead of Gemini.
"""

import asyncio
import os
import re
from datetime import date
from typing import Optional

import asyncpg
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent, ModelRetry, RunContext
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
    ("find logs with user_id attribute",
     "SELECT * FROM records WHERE attributes ? 'user_id' ORDER BY created_at DESC LIMIT 100"),
    ("show unique trace IDs from today",
     "SELECT DISTINCT trace_id FROM records WHERE created_at >= CURRENT_DATE ORDER BY trace_id")
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


class SqlGenAgent:
    """SQL generation agent using Ollama."""
    
    def __init__(self, model_name: str = "llama3.2:latest", base_url: str = "http://localhost:11434/v1"):
        """Initialize the SQL generation agent.
        
        Args:
            model_name: Ollama model to use (default: llama3.2:latest)
            base_url: Ollama API endpoint (default: http://localhost:11434/v1)
        """
        self.console = Console()
        
        # Create OpenAI-compatible model pointing to Ollama
        # Ollama provides an OpenAI-compatible API at /v1
        # Set environment variables for OpenAI client to use Ollama
        os.environ["OPENAI_API_KEY"] = "ollama"
        os.environ["OPENAI_BASE_URL"] = base_url
        
        model = OpenAIModel(model_name=model_name)
        
        # Create the agent with dynamic system prompt
        self.agent = Agent(
            model=model,
            result_type=SqlQuery,
            system_prompt=self._build_system_prompt,
            deps_type=asyncpg.Connection,
            retries=2
        )
        
        # Register result validator
        self.agent.result_validator(self._validate_query)
    
    def _build_system_prompt(self, ctx: RunContext[asyncpg.Connection]) -> str:
        """Build dynamic system prompt with schema and examples."""
        examples = "\n\n".join(
            f"User: {q}\nSQL: {sql}"
            for q, sql in QUERY_EXAMPLES
        )
        
        return f"""You are a PostgreSQL expert that generates SQL queries.

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
    
    async def _validate_query(
        self, 
        ctx: RunContext[asyncpg.Connection], 
        result: SqlQuery
    ) -> SqlQuery:
        """Validate the generated SQL query using EXPLAIN."""
        try:
            # Use EXPLAIN to validate query syntax without executing
            await ctx.deps.execute(f"EXPLAIN {result.query}")
            return result
        except asyncpg.PostgresSyntaxError as e:
            # Give the model a chance to fix syntax errors
            raise ModelRetry(f"SQL syntax error: {e}")
        except Exception as e:
            # Other errors should fail immediately
            raise ValueError(f"Query validation failed: {e}")
    
    async def generate_query(
        self, 
        prompt: str, 
        conn: asyncpg.Connection
    ) -> SqlQuery:
        """Generate a SQL query from natural language prompt.
        
        Args:
            prompt: Natural language description of desired query
            conn: PostgreSQL connection for validation
            
        Returns:
            Validated SQL query result
        """
        result = await self.agent.run(prompt, deps=conn)
        return result.data
    
    def display_result(self, result: SqlQuery):
        """Display the generated query with syntax highlighting."""
        # Display explanation
        self.console.print(Panel(
            result.explanation,
            title="Query Explanation",
            border_style="blue"
        ))
        
        # Display SQL with syntax highlighting
        syntax = Syntax(
            result.query, 
            "sql", 
            theme="monokai", 
            line_numbers=True
        )
        self.console.print(Panel(
            syntax,
            title="Generated SQL",
            border_style="green"
        ))


async def setup_database(conn: asyncpg.Connection):
    """Set up the example database schema."""
    # Drop and recreate the schema
    await conn.execute("DROP TABLE IF EXISTS records CASCADE")
    await conn.execute(SCHEMA)
    
    # Insert some sample data
    sample_data = [
        ("error", "Database connection failed", {"service": "api", "user_id": 123}),
        ("info", "User login successful", {"service": "auth", "user_id": 456}),
        ("warning", "High memory usage detected", {"service": "monitor", "threshold": 80}),
        ("error", "Payment processing failed", {"service": "payment", "user_id": 789}),
        ("debug", "Cache miss for key: user_profile", {"service": "cache", "key": "user_profile"}),
    ]
    
    for level, message, attributes in sample_data:
        await conn.execute(
            """
            INSERT INTO records (span_id, trace_id, level, message, attributes)
            VALUES ($1, $2, $3, $4, $5)
            """,
            "0" * 16,  # Dummy span_id
            "0" * 32,  # Dummy trace_id
            level,
            message,
            attributes
        )


async def main():
    """Run the SQL generation example."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate SQL queries using Ollama")
    parser.add_argument("prompt", help="Natural language query description")
    parser.add_argument("--model", default="llama3.2:latest", help="Ollama model to use")
    parser.add_argument("--ollama-url", default="http://localhost:11434/v1", help="Ollama API URL")
    parser.add_argument("--setup", action="store_true", help="Set up example database")
    parser.add_argument("--db-host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--db-port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("--db-name", default="postgres", help="Database name")
    parser.add_argument("--db-user", default="postgres", help="Database user")
    parser.add_argument("--db-password", default="postgres", help="Database password")
    
    args = parser.parse_args()
    
    console = Console()
    
    # Connect to PostgreSQL
    try:
        conn = await asyncpg.connect(
            host=args.db_host,
            port=args.db_port,
            database=args.db_name,
            user=args.db_user,
            password=args.db_password
        )
    except Exception as e:
        console.print(f"[red]Failed to connect to PostgreSQL: {e}[/red]")
        console.print("\n[yellow]Make sure PostgreSQL is running. You can use Docker:[/yellow]")
        console.print("docker run --rm -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres")
        return
    
    try:
        # Optionally set up the database
        if args.setup:
            console.print("[blue]Setting up example database...[/blue]")
            await setup_database(conn)
            console.print("[green]Database setup complete![/green]\n")
        
        # Create agent and generate query
        agent = SqlGenAgent(model_name=args.model, base_url=args.ollama_url)
        console.print(f"[blue]Generating SQL for:[/blue] {args.prompt}\n")
        
        result = await agent.generate_query(args.prompt, conn)
        agent.display_result(result)
        
        # Optionally execute the query and show results
        console.print("\n[yellow]Execute query? (y/n):[/yellow] ", end="")
        if input().lower() == "y":
            rows = await conn.fetch(result.query)
            console.print(f"\n[green]Results ({len(rows)} rows):[/green]")
            for row in rows[:10]:  # Show first 10 rows
                console.print(dict(row))
            if len(rows) > 10:
                console.print(f"... and {len(rows) - 10} more rows")
    
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())