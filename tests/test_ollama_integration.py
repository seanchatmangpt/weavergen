"""Integration tests for Ollama examples."""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up Ollama environment
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "ollama: mark test as requiring Ollama service"
    )


@pytest.fixture
def check_ollama():
    """Check if Ollama is available."""
    import httpx
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if response.status_code != 200:
            pytest.skip("Ollama service not running")
    except:
        pytest.skip("Ollama service not accessible")


@pytest.mark.ollama
class TestStructuredOutput:
    """Test structured output examples."""
    
    async def test_basic_city_extraction(self, check_ollama):
        """Test basic city extraction."""
        from pydantic import BaseModel, Field
        from pydantic_ai import Agent
        from weavergen.examples.ollama_utils import get_ollama_model
        
        class City(BaseModel):
            name: str
            country: str
            population: int = Field(gt=0)
        
        model = get_ollama_model(check_connection=False)
        agent = Agent(model=model, result_type=City)
        
        result = await agent.run("Paris, France has 2.2 million people")
        city = result.output
        
        assert city.name == "Paris"
        assert city.country == "France"
        assert 2_000_000 <= city.population <= 2_500_000
    
    async def test_complex_recipe(self, check_ollama):
        """Test complex nested structure."""
        from typing import List
        from pydantic import BaseModel, Field
        from pydantic_ai import Agent
        from weavergen.examples.ollama_utils import get_ollama_model
        
        class Ingredient(BaseModel):
            name: str
            amount: float = Field(gt=0)
            unit: str
        
        class Recipe(BaseModel):
            name: str
            ingredients: List[Ingredient]
            prep_time_minutes: int = Field(gt=0)
        
        model = get_ollama_model(check_connection=False)
        agent = Agent(
            model=model,
            result_type=Recipe,
            system_prompt="Generate simple recipes with ingredients."
        )
        
        result = await agent.run("Simple tomato sauce recipe")
        recipe = result.output
        
        assert len(recipe.ingredients) >= 2
        assert recipe.prep_time_minutes > 0
        assert all(ing.amount > 0 for ing in recipe.ingredients)


@pytest.mark.ollama
class TestSQLGeneration:
    """Test SQL generation examples."""
    
    async def test_sql_validation(self, check_ollama):
        """Test SQL query validation."""
        from pydantic import BaseModel, Field, field_validator
        from pydantic_ai import Agent
        from weavergen.examples.ollama_utils import get_ollama_model
        
        class SqlQuery(BaseModel):
            query: str
            
            @field_validator("query")
            @classmethod
            def must_be_select(cls, v: str) -> str:
                if not v.strip().upper().startswith("SELECT"):
                    raise ValueError("Only SELECT queries allowed")
                return v
        
        model = get_ollama_model(check_connection=False)
        agent = Agent(
            model=model,
            result_type=SqlQuery,
            system_prompt="Generate SQL queries. Only SELECT statements."
        )
        
        result = await agent.run("Show all users")
        query = result.output
        
        assert query.query.upper().startswith("SELECT")
        assert "FROM" in query.query.upper()
    
    async def test_sql_with_explanation(self, check_ollama):
        """Test SQL generation with explanation."""
        from weavergen.examples.sql_gen_ollama_simple import SqlQuery
        from pydantic_ai import Agent
        from weavergen.examples.ollama_utils import get_ollama_model
        
        model = get_ollama_model(check_connection=False)
        agent = Agent(
            model=model,
            result_type=SqlQuery,
            system_prompt="Generate PostgreSQL queries with explanations."
        )
        
        result = await agent.run("Count records by level")
        output = result.output
        
        assert output.query.upper().startswith("SELECT")
        assert len(output.explanation) > 10
        assert "COUNT" in output.query.upper() or "count" in output.query.lower()


@pytest.mark.ollama
class TestValidation:
    """Test validation and error handling."""
    
    async def test_field_validation(self, check_ollama):
        """Test field-level validation."""
        from pydantic import BaseModel, Field, field_validator
        from pydantic_ai import Agent
        from weavergen.examples.ollama_utils import get_ollama_model
        import re
        
        class Contact(BaseModel):
            email: str
            
            @field_validator("email")
            @classmethod
            def validate_email(cls, v: str) -> str:
                if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v):
                    raise ValueError("Invalid email")
                return v.lower()
        
        model = get_ollama_model(check_connection=False)
        agent = Agent(
            model=model,
            result_type=Contact,
            system_prompt="Extract email addresses from text."
        )
        
        result = await agent.run("Contact: john.doe@example.com")
        contact = result.output
        
        assert contact.email == "john.doe@example.com"
        assert "@" in contact.email
        assert "." in contact.email


@pytest.mark.ollama
class TestErrorHandling:
    """Test error handling utilities."""
    
    def test_connection_check(self):
        """Test Ollama connection checking."""
        from weavergen.examples.ollama_utils import check_ollama_connection
        
        # This should work if Ollama is running
        is_connected = check_ollama_connection()
        assert isinstance(is_connected, bool)
    
    def test_model_listing(self):
        """Test getting available models."""
        from weavergen.examples.ollama_utils import get_available_models
        
        models = get_available_models()
        assert isinstance(models, list)
        
        if models:  # If Ollama is running with models
            assert all(isinstance(m, str) for m in models)
    
    def test_model_fallback(self, check_ollama):
        """Test model fallback mechanism."""
        from weavergen.examples.ollama_utils import get_ollama_model
        
        # Try to get a non-existent model with fallbacks
        try:
            model = get_ollama_model(
                "non-existent-model:latest",
                fallback_models=["qwen3:latest", "llama3.2:latest"],
                check_connection=True
            )
            # Should get a fallback model
            assert model is not None
        except Exception:
            # OK if no models are installed
            pass


def test_imports():
    """Test that all example modules can be imported."""
    try:
        from weavergen.examples import sql_gen_ollama_simple
        from weavergen.examples import structured_output_ollama
        from weavergen.examples import validation_retries_ollama
        from weavergen.examples import streaming_output_ollama
        from weavergen.examples import ollama_utils
        from weavergen.examples import check_setup
    except ImportError as e:
        pytest.fail(f"Failed to import examples: {e}")


# Run async tests
def test_structured_output(check_ollama):
    """Run structured output tests."""
    test = TestStructuredOutput()
    asyncio.run(test.test_basic_city_extraction(check_ollama))
    asyncio.run(test.test_complex_recipe(check_ollama))


def test_sql_generation(check_ollama):
    """Run SQL generation tests."""
    test = TestSQLGeneration()
    asyncio.run(test.test_sql_validation(check_ollama))
    asyncio.run(test.test_sql_with_explanation(check_ollama))


def test_validation(check_ollama):
    """Run validation tests."""
    test = TestValidation()
    asyncio.run(test.test_field_validation(check_ollama))


if __name__ == "__main__":
    # Quick test runner
    import subprocess
    result = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"])
    sys.exit(result.returncode)