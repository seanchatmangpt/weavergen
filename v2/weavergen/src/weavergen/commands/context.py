from pathlib import Path
import re
import difflib
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table

from ..enhanced_instrumentation import cli_command_span

console = Console()
error_console = Console(stderr=True)

context_app = typer.Typer()


@context_app.command()
def generate(
    output_file: Path = typer.Option(
        "context_window.txt",
        "--output",
        "-o",
        help="Output file to write the context to.",
    ),
    include_pyproject: bool = typer.Option(
        True, "--pyproject", help="Include pyproject.toml in the context."
    ),
    include_src_weavergen: bool = typer.Option(
        True,
        "--src-weavergen",
        help="Include all .py files in src/weavergen in the context.",
    ),
):
    """
    Generates a context file for WeaverGen v2.
    This command gathers the source of pertinent files and pyproject.toml
    to fill the context window for AI models.
    """
    with cli_command_span(
        "context.generate",
        {
            "output_file": str(output_file),
            "include_pyproject": include_pyproject,
            "include_src_weavergen": include_src_weavergen,
        },
    ):
        context_content = []

        if include_pyproject:
            pyproject_path = Path("/Users/sac/dev/weavergen/v2/weavergen/pyproject.toml")
            if pyproject_path.exists():
                context_content.append(f"--- {pyproject_path.name} ---")
                context_content.append(pyproject_path.read_text())
                context_content.append("")
            else:
                error_console.print(f"[yellow]Warning: {pyproject_path} not found.[/yellow]")

        if include_src_weavergen:
            src_weavergen_dir = Path("/Users/sac/dev/weavergen/v2/weavergen/src/weavergen")
            if src_weavergen_dir.exists() and src_weavergen_dir.is_dir():
                for file_path in sorted(src_weavergen_dir.rglob("*.py")):
                    context_content.append(
                        f"--- {file_path.relative_to(src_weavergen_dir.parent)} ---"
                    )
                    context_content.append(file_path.read_text())
                    context_content.append("")
            else:
                error_console.print(
                    f"[yellow]Warning: {src_weavergen_dir} not found or is not a directory.[/yellow]"
                )

        try:
            output_file.write_text("\n".join(context_content))
            error_console.print(f"[green]Context written to {output_file}[/green]")
        except Exception as e:
            error_console.print(f"[red]Error writing context to file: {e}[/red]")
            raise


@context_app.command(name="load")
def load_context(
    input_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the context file to load.",
    ),
):
    """
    Loads and displays the content of a specified context file.
    """
    with cli_command_span("context.load", {"input_file": str(input_file)}):
        try:
            content = input_file.read_text()
            console.print(f"[bold green]Content of {input_file}:[/bold green]")
            console.print(content, markup=False)
        except Exception as e:
            console.print(f"[red]Error reading context file {input_file}: {e}[/red]", markup=False)


@context_app.command(name="filter")
def filter_context(
    input_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the context file to filter.",
    ),
    pattern: str = typer.Argument(..., help="Regular expression pattern to filter by."),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file to write the filtered context to. If not provided, prints to console.",
    ),
):
    """
    Filters a context file based on a regular expression pattern.
    """
    with cli_command_span(
        "context.filter",
        {"input_file": str(input_file), "pattern": pattern, "output_file": str(output_file) if output_file else None},
    ):
        try:
            content = input_file.read_text()
            filtered_lines = []
            for line in content.splitlines():
                if re.search(pattern, line):
                    filtered_lines.append(line)
            filtered_content = "\n".join(filtered_lines)

            if output_file:
                output_file.write_text(filtered_content)
                error_console.print(f"[green]Filtered context written to {output_file}[/green]")
            else:
                console.print(f"[bold green]Filtered content from {input_file}:[/bold green]")
                console.print(filtered_content)
        except Exception as e:
            console.print(f"[red]Error filtering context file {input_file}: {e}[/red]")


@context_app.command(name="summarize")
def summarize_context(
    input_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the context file to summarize.",
    ),
):
    """
    Provides a summary of the context file, including file counts, total lines, and total characters.
    """
    with cli_command_span("context.summarize", {"input_file": str(input_file)}):
        try:
            content = input_file.read_text()
            lines = content.splitlines()
            total_lines = len(lines)
            total_characters = len(content)
            
            file_count = 0
            for line in lines:
                if line.startswith("--- ") and line.endswith(" ---"):
                    file_count += 1

            table = Table(title=f"Summary of {input_file.name}")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("Number of Files", str(file_count))
            table.add_row("Total Lines", str(total_lines))
            table.add_row("Total Characters", str(total_characters))
            
            console.print(table)

        except Exception as e:
            console.print(f"[red]Error summarizing context file {input_file}: {e}[/red]")


@context_app.command(name="diff")
def diff_context(
    file1: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the first context file.",
    ),
    file2: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the second context file.",
    ),
):
    """
    Compares two context files and displays their differences.
    """
    with cli_command_span("context.diff", {"file1": str(file1), "file2": str(file2)}):
        try:
            content1 = file1.read_text().splitlines()
            content2 = file2.read_text().splitlines()

            diff = difflib.unified_diff(
                content1, content2, fromfile=str(file1), tofile=str(file2)
            )
            console.print("\n".join(list(diff)), markup=False)
        except Exception as e:
            console.print(f"[red]Error comparing context files: {e}[/red]")


@context_app.command(name="combine")
def combine_contexts(
    input_files: List[Path] = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Paths to the context files to combine.",
    ),
    output_file: Path = typer.Option(
        "combined_context.txt",
        "--output",
        "-o",
        help="Output file to write the combined context to.",
    ),
):
    """
    Combines multiple context files into a single output file.
    """
    with cli_command_span(
        "context.combine",
        {"input_files": [str(f) for f in input_files], "output_file": str(output_file)},
    ):
        combined_content = []
        for input_file in input_files:
            try:
                combined_content.append(f"--- {input_file.name} ---")
                combined_content.append(input_file.read_text())
                combined_content.append("")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not read {input_file}: {e}[/yellow]")
        
        try:
            output_file.write_text("\n".join(combined_content))
            console.print(f"[green]Combined context written to {output_file}[/green]")
        except Exception as e:
            console.print(f"[red]Error writing combined context to file: {e}[/red]")


@context_app.command(name="validate")
def validate_context(
    input_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the context file to validate.",
    ),
):
    """
    Validates the structure of a context file, checking for empty files or malformed sections.
    """
    with cli_command_span("context.validate", {"input_file": str(input_file)}):
        try:
            content = input_file.read_text()
            lines = content.splitlines()
            
            is_valid = True
            current_file = None
            file_content_lines = 0

            for line in lines:
                if line.startswith("--- ") and line.endswith(" ---"):
                    if current_file and file_content_lines == 0:
                        console.print(f"[yellow]Warning: File '{current_file}' has no content.[/yellow]")
                        is_valid = False
                    current_file = line[4:-4].strip()
                    file_content_lines = 0
                elif current_file:
                    file_content_lines += 1
            
            if current_file and file_content_lines == 0:
                console.print(f"[yellow]Warning: File '{current_file}' has no content.[/yellow]")
                is_valid = False

            if is_valid:
                console.print(f"[green]Context file {input_file} is valid.[/green]")
            else:
                console.print(f"[red]Context file {input_file} has validation issues.[/red]")

        except Exception as e:
            console.print(f"[red]Error validating context file {input_file}: {e}[/red]")


if __name__ == "__main__":
    typer.run(generate)

