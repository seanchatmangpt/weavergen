#!/usr/bin/env python3
"""Complete end-to-end example combining all pydantic-ai features with Ollama.

This example shows a practical use case: analyzing code repositories
and generating structured reports.
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent, ModelRetry
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

from .ollama_utils import get_ollama_model, handle_ollama_error


console = Console()


# Data models for code analysis
class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    OTHER = "other"


class CodeComplexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FileAnalysis(BaseModel):
    """Analysis of a single code file."""
    filename: str
    language: Language
    lines_of_code: int = Field(gt=0)
    complexity: CodeComplexity
    has_tests: bool
    main_purpose: str
    dependencies: List[str] = Field(default_factory=list)
    
    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Filename cannot be empty")
        return v


class SecurityIssue(BaseModel):
    """Potential security issue found."""
    severity: str = Field(description="high, medium, or low")
    type: str
    description: str
    file: str
    recommendation: str


class ProjectReport(BaseModel):
    """Complete project analysis report."""
    project_name: str
    analysis_date: datetime = Field(default_factory=datetime.now)
    total_files: int = Field(ge=0)
    primary_language: Language
    files_analyzed: List[FileAnalysis]
    security_issues: List[SecurityIssue] = Field(default_factory=list)
    test_coverage_estimate: float = Field(ge=0, le=100)
    recommendations: List[str]
    
    @property
    def complexity_summary(self) -> Dict[str, int]:
        """Summary of complexity levels."""
        summary = {"low": 0, "medium": 0, "high": 0}
        for file in self.files_analyzed:
            summary[file.complexity.value] += 1
        return summary


class CodeAnalyzer:
    """Analyzes code repositories using pydantic-ai."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.model = get_ollama_model("qwen3:latest")
        
        # Agent for file analysis
        self.file_agent = Agent(
            model=self.model,
            result_type=FileAnalysis,
            system_prompt="""Analyze the given code file information.
            Determine the language, complexity, and main purpose.
            Be accurate with line counts and dependency detection."""
        )
        
        # Agent for security analysis
        self.security_agent = Agent(
            model=self.model,
            result_type=List[SecurityIssue],
            system_prompt="""Analyze code for potential security issues.
            Focus on common vulnerabilities like SQL injection, XSS, 
            hardcoded secrets, and insecure dependencies.
            Provide actionable recommendations.""",
            retries=2
        )
        
        # Agent for project report
        self.report_agent = Agent(
            model=self.model,
            result_type=ProjectReport,
            system_prompt="""Generate a comprehensive project analysis report.
            Include all provided file analyses and security findings.
            Provide actionable recommendations for improvement."""
        )
        
        # Add validation to security agent
        @self.security_agent.output_validator
        async def validate_security(ctx, result):
            for issue in result:
                if issue.severity not in ["high", "medium", "low"]:
                    raise ModelRetry(f"Invalid severity: {issue.severity}")
            return result
    
    async def analyze_file(self, file_info: str) -> FileAnalysis:
        """Analyze a single file."""
        result = await self.file_agent.run(file_info)
        return result.output
    
    async def find_security_issues(self, project_desc: str) -> List[SecurityIssue]:
        """Find security issues in the project."""
        result = await self.security_agent.run(project_desc)
        return result.output
    
    async def generate_report(
        self, 
        project_name: str,
        file_analyses: List[FileAnalysis],
        security_issues: List[SecurityIssue]
    ) -> ProjectReport:
        """Generate final project report."""
        context = f"""
        Project: {project_name}
        Files analyzed: {len(file_analyses)}
        File details: {[f.model_dump() for f in file_analyses]}
        Security issues found: {len(security_issues)}
        Security details: {[s.model_dump() for s in security_issues]}
        """
        
        result = await self.report_agent.run(context)
        return result.output
    
    def display_report(self, report: ProjectReport):
        """Display the report in a nice format."""
        # Header
        console.print(Panel.fit(
            f"[bold]{report.project_name}[/bold]\n"
            f"Analysis Date: {report.analysis_date.strftime('%Y-%m-%d %H:%M')}",
            title="Project Analysis Report",
            border_style="blue"
        ))
        
        # Summary stats
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Total Files: {report.total_files}")
        console.print(f"  Primary Language: {report.primary_language.value}")
        console.print(f"  Test Coverage Estimate: {report.test_coverage_estimate:.1f}%")
        
        # Complexity breakdown
        console.print("\n[bold]Complexity Analysis:[/bold]")
        complexity = report.complexity_summary
        table = Table(show_header=False, box=None)
        table.add_column("Level", style="cyan")
        table.add_column("Count", style="yellow")
        
        for level, count in complexity.items():
            table.add_row(level.capitalize(), str(count))
        
        console.print(table)
        
        # Security issues
        if report.security_issues:
            console.print(f"\n[bold red]Security Issues Found ({len(report.security_issues)}):[/bold red]")
            for issue in report.security_issues:
                console.print(f"  • [{issue.severity.upper()}] {issue.type}: {issue.description}")
                console.print(f"    File: {issue.file}")
                console.print(f"    Fix: {issue.recommendation}")
        else:
            console.print("\n[green]✓ No security issues found[/green]")
        
        # Recommendations
        console.print("\n[bold]Recommendations:[/bold]")
        for i, rec in enumerate(report.recommendations, 1):
            console.print(f"  {i}. {rec}")


@handle_ollama_error
async def main():
    """Run the complete example."""
    console.print("[bold]Code Repository Analyzer[/bold]")
    console.print("Using pydantic-ai with Ollama for structured analysis\n")
    
    analyzer = CodeAnalyzer()
    
    # Simulate analyzing a project
    console.print("Analyzing project files...")
    
    # Sample file descriptions
    file_descriptions = [
        "app.py: Main Flask application with 450 lines, imports flask, sqlalchemy, handles user auth",
        "models.py: Database models, 200 lines, defines User, Product, Order classes with SQLAlchemy",
        "utils.py: Utility functions, 150 lines, includes password hashing and email validation",
        "test_app.py: Unit tests for app routes, 300 lines, uses pytest",
        "config.py: Configuration file, 50 lines, contains database URLs and API keys"
    ]
    
    # Analyze files
    file_analyses = []
    for desc in track(file_descriptions, description="Analyzing files"):
        analysis = await analyzer.analyze_file(desc)
        file_analyses.append(analysis)
        await asyncio.sleep(0.5)  # Simulate processing
    
    # Security scan
    console.print("\nScanning for security issues...")
    project_desc = """
    Flask web application with user authentication, SQLAlchemy database,
    configuration files containing API keys, password hashing utilities.
    """
    security_issues = await analyzer.find_security_issues(project_desc)
    
    # Generate report
    console.print("\nGenerating final report...")
    report = await analyzer.generate_report(
        "Flask Web Application",
        file_analyses,
        security_issues
    )
    
    # Display results
    console.print("\n")
    analyzer.display_report(report)
    
    # Save report option
    console.print("\n[yellow]Report generated successfully![/yellow]")
    
    # Show how to access the structured data
    console.print("\n[dim]Structured data is available as:[/dim]")
    console.print(f"[dim]- report.model_dump() for full dictionary[/dim]")
    console.print(f"[dim]- report.model_dump_json() for JSON export[/dim]")


if __name__ == "__main__":
    asyncio.run(main())