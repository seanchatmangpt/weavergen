"""Validation and Retries Example with Ollama.

This example demonstrates:
- Result validation with custom validators
- Automatic retries on validation failures
- Using ModelRetry to give the model feedback
- Handling complex validation scenarios
"""

import os
import re
from datetime import datetime, date
from typing import List, Optional
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


# Set up Ollama
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"

console = Console()


# Example 1: Email validation with retries
class ContactInfo(BaseModel):
    """Contact information with validation."""
    name: str = Field(min_length=2, description="Full name")
    email: str = Field(description="Valid email address")
    phone: Optional[str] = Field(None, description="Phone number with country code")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        # Simple email validation
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, v):
            raise ValueError(f"Invalid email format: {v}")
        return v.lower()
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s\-()]', '', v)
        # Check if it starts with + and has 10-15 digits
        if not re.match(r'^\+\d{10,15}$', cleaned):
            raise ValueError(f"Phone must start with + and have 10-15 digits, got: {v}")
        return cleaned


# Example 2: Financial data with complex validation
class Transaction(BaseModel):
    """Financial transaction with validation."""
    id: str = Field(description="Transaction ID (format: TXN-YYYYMMDD-XXXX)")
    date: date = Field(description="Transaction date")
    amount: Decimal = Field(gt=0, description="Transaction amount (positive)")
    currency: str = Field(pattern=r'^[A-Z]{3}$', description="3-letter currency code")
    description: str = Field(min_length=5, max_length=200)
    
    @field_validator("id")
    @classmethod
    def validate_transaction_id(cls, v: str) -> str:
        pattern = r'^TXN-\d{8}-\d{4}$'
        if not re.match(pattern, v):
            raise ValueError(f"ID must match format TXN-YYYYMMDD-XXXX, got: {v}")
        
        # Extract and validate date portion
        date_str = v[4:12]
        try:
            datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            raise ValueError(f"Invalid date in transaction ID: {date_str}")
        
        return v
    
    @field_validator("amount", mode="before")
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert string or float to Decimal."""
        if isinstance(v, str):
            v = v.replace(',', '').replace('$', '')
        return Decimal(str(v))


class AccountStatement(BaseModel):
    """Bank account statement with transactions."""
    account_number: str = Field(pattern=r'^\d{10,12}$', description="Account number")
    period_start: date
    period_end: date
    opening_balance: Decimal
    closing_balance: Decimal
    transactions: List[Transaction]
    
    @model_validator(mode="after")
    def validate_dates_and_balance(self):
        # Ensure period_end is after period_start
        if self.period_end <= self.period_start:
            raise ValueError("Period end must be after period start")
        
        # Validate all transactions are within the period
        for txn in self.transactions:
            if not (self.period_start <= txn.date <= self.period_end):
                raise ValueError(
                    f"Transaction {txn.id} date {txn.date} is outside statement period"
                )
        
        # Calculate expected closing balance
        total_amount = sum(txn.amount for txn in self.transactions)
        expected_closing = self.opening_balance + total_amount
        
        # Allow small rounding differences
        if abs(expected_closing - self.closing_balance) > Decimal('0.01'):
            raise ValueError(
                f"Closing balance {self.closing_balance} doesn't match "
                f"calculated balance {expected_closing}"
            )
        
        return self


# Example 3: Code generation with syntax validation
class CodeSnippet(BaseModel):
    """Code snippet with validation."""
    language: str = Field(description="Programming language")
    code: str = Field(description="The code snippet")
    imports: List[str] = Field(default_factory=list, description="Required imports")
    is_complete: bool = Field(description="Whether the code is complete and runnable")
    
    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        supported = ["python", "javascript", "typescript", "java", "go", "rust"]
        if v.lower() not in supported:
            raise ValueError(f"Unsupported language: {v}. Use one of: {supported}")
        return v.lower()
    
    @model_validator(mode="after")
    def validate_code_structure(self):
        if self.language == "python" and self.is_complete:
            # Check for basic Python syntax
            if "def " not in self.code and "class " not in self.code:
                if not any(self.code.strip().startswith(keyword) 
                          for keyword in ["print", "import", "from", "#"]):
                    raise ValueError("Complete Python code should contain function, class, or valid statements")
            
            # Check if imports are used
            for imp in self.imports:
                module = imp.split()[1] if imp.startswith("from") else imp.split()[1]
                if module not in self.code:
                    raise ValueError(f"Import '{imp}' is listed but not used in code")
        
        return self


async def example_contact_validation():
    """Example 1: Contact info with email/phone validation and retries."""
    console.print("\n[bold blue]Example 1: Contact Validation with Retries[/bold blue]")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=ContactInfo,
        system_prompt="""Extract contact information from the text.
        Ensure email addresses are valid and phone numbers include country code.
        Phone numbers should start with + followed by country code.""",
        retries=3  # Allow up to 3 retries
    )
    
    # Add custom result validator
    @agent.result_validator
    async def validate_contact(ctx: RunContext[None], result: ContactInfo) -> ContactInfo:
        # Additional business logic validation
        if result.email.endswith(".test"):
            raise ModelRetry("Please provide a real email address, not a test domain")
        
        if result.name.lower() in ["test", "example", "demo"]:
            raise ModelRetry("Please extract the actual person's name, not a placeholder")
        
        return result
    
    test_inputs = [
        "Contact John Doe at john.doe@example.com or call +1-555-123-4567",
        "Email: bad-email-format or phone: 123456",  # This should fail and retry
        "Jane Smith (jane@test) phone: 555-1234",  # Multiple issues
    ]
    
    for input_text in test_inputs:
        console.print(f"\n[yellow]Input:[/yellow] {input_text}")
        try:
            result = await agent.run(input_text)
            contact = result.output
            
            table = Table()
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Name", contact.name)
            table.add_row("Email", contact.email)
            table.add_row("Phone", contact.phone or "N/A")
            console.print(table)
            
            # Show retry information
            if result.new_message_index > 1:
                console.print(f"[dim]Succeeded after {result.new_message_index - 1} retries[/dim]")
                
        except Exception as e:
            console.print(f"[red]Failed after all retries:[/red] {e}")


async def example_financial_validation():
    """Example 2: Financial data with complex validation rules."""
    console.print("\n[bold blue]Example 2: Financial Data Validation[/bold blue]")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=AccountStatement,
        system_prompt="""Generate a bank account statement with transactions.
        Rules:
        - Transaction IDs must be format: TXN-YYYYMMDD-XXXX (sequential number)
        - All amounts must be positive (use separate debit/credit transactions)
        - Closing balance = Opening balance + sum of all transactions
        - All transactions must be within the statement period
        - Currency codes must be 3 uppercase letters (USD, EUR, GBP, etc.)""",
        retries=3
    )
    
    @agent.result_validator
    async def validate_statement(ctx: RunContext[None], result: AccountStatement) -> AccountStatement:
        # Check for duplicate transaction IDs
        tx_ids = [tx.id for tx in result.transactions]
        if len(tx_ids) != len(set(tx_ids)):
            raise ModelRetry("Transaction IDs must be unique")
        
        # Ensure transactions are sorted by date
        sorted_txs = sorted(result.transactions, key=lambda x: x.date)
        if result.transactions != sorted_txs:
            raise ModelRetry("Transactions should be sorted by date")
        
        return result
    
    prompt = """Create a bank statement for account 123456789012 for October 2024
    with opening balance $1,000. Include at least 5 transactions."""
    
    try:
        result = await agent.run(prompt)
        statement = result.output
        
        # Display statement header
        console.print(Panel(
            f"[bold]Account Statement[/bold]\n"
            f"Account: {statement.account_number}\n"
            f"Period: {statement.period_start} to {statement.period_end}\n"
            f"Opening Balance: ${statement.opening_balance:,.2f}\n"
            f"Closing Balance: ${statement.closing_balance:,.2f}",
            title="Statement Summary"
        ))
        
        # Display transactions
        tx_table = Table(title="Transactions")
        tx_table.add_column("ID", style="cyan")
        tx_table.add_column("Date", style="yellow")
        tx_table.add_column("Description", style="white")
        tx_table.add_column("Amount", style="green", justify="right")
        tx_table.add_column("Currency", style="blue")
        
        for tx in statement.transactions:
            tx_table.add_row(
                tx.id,
                str(tx.date),
                tx.description[:30] + "..." if len(tx.description) > 30 else tx.description,
                f"${tx.amount:,.2f}",
                tx.currency
            )
        
        console.print(tx_table)
        
        if result.new_message_index > 1:
            console.print(f"\n[dim]Generated correctly after {result.new_message_index - 1} retries[/dim]")
        
    except Exception as e:
        console.print(f"[red]Failed to generate valid statement:[/red] {e}")


async def example_code_validation():
    """Example 3: Code generation with syntax and structure validation."""
    console.print("\n[bold blue]Example 3: Code Generation with Validation[/bold blue]")
    
    agent = Agent(
        OpenAIModel(model_name="qwen3:latest"),
        result_type=CodeSnippet,
        system_prompt="""Generate code snippets based on the request.
        Rules:
        - Include all necessary imports
        - Code must be syntactically correct
        - Mark as complete only if it's runnable as-is
        - List imports separately from the code""",
        retries=2
    )
    
    @agent.result_validator
    async def validate_code(ctx: RunContext[None], result: CodeSnippet) -> CodeSnippet:
        if result.language == "python":
            # Check for common Python errors
            if "print(" in result.code and "print " in result.code:
                raise ModelRetry("Use consistent print syntax (with parentheses for Python 3)")
            
            # Check indentation
            lines = result.code.split('\n')
            if any(line.startswith(' ') and not line.startswith('    ') for line in lines):
                raise ModelRetry("Python code should use 4-space indentation")
        
        # Ensure code is not empty
        if not result.code.strip():
            raise ModelRetry("Code snippet cannot be empty")
        
        return result
    
    prompts = [
        "Create a Python function to calculate factorial",
        "Write JavaScript code to fetch data from an API",
        "Generate a Python class for a simple todo list",
    ]
    
    for prompt in prompts:
        console.print(f"\n[yellow]Request:[/yellow] {prompt}")
        try:
            result = await agent.run(prompt)
            snippet = result.output
            
            # Display metadata
            console.print(Panel(
                f"Language: {snippet.language}\n"
                f"Complete: {'Yes' if snippet.is_complete else 'No'}\n"
                f"Imports: {', '.join(snippet.imports) if snippet.imports else 'None'}",
                title="Code Metadata"
            ))
            
            # Display code with syntax highlighting
            console.print("\n[bold]Generated Code:[/bold]")
            # Display imports first if any
            if snippet.imports:
                for imp in snippet.imports:
                    console.print(f"[dim]{imp}[/dim]")
                console.print()
            
            console.print(snippet.code)
            
            if result.new_message_index > 1:
                console.print(f"\n[dim]Validated after {result.new_message_index - 1} retries[/dim]")
                
        except Exception as e:
            console.print(f"[red]Code generation failed:[/red] {e}")


async def main():
    """Run all validation and retry examples."""
    console.print("[bold green]Validation and Retries Examples with Ollama[/bold green]")
    console.print("=" * 60)
    
    await example_contact_validation()
    await example_financial_validation()
    await example_code_validation()
    
    console.print("\n[bold green]All validation examples completed![/bold green]")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())