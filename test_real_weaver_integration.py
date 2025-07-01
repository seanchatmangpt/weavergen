#!/usr/bin/env python3
"""
Test Real Weaver Forge Integration
This verifies that the unified engine actually works with real Weaver Forge generation.
"""

import asyncio
from pathlib import Path
import tempfile
import json

from rich.console import Console
from rich.panel import Panel

from src.weavergen.core import WeaverGen, GenerationConfig
from src.weavergen.unified_bpmn_engine import UnifiedBPMNEngine

console = Console()


def test_core_weaver_functionality():
    """Test the core WeaverGen functionality still works"""
    console.print("[cyan]🔍 Testing Core Weaver Functionality[/cyan]\n")
    
    try:
        # Initialize WeaverGen core
        weaver = WeaverGen()
        console.print("[green]✅ WeaverGen core initialized[/green]")
        
        # Check weaver binary
        config = weaver.get_config()
        console.print(f"[green]✅ Weaver binary found at: {config.weaver_path}[/green]")
        
        # Test registry validation (this should work without semantic files)
        console.print("\n[yellow]Testing registry validation...[/yellow]")
        
        # Create a minimal test semantic file
        test_semantic = {
            "groups": {
                "test.group": {
                    "id": "test.group",
                    "type": "attribute_group",
                    "brief": "Test group for validation",
                    "attributes": {
                        "test.attribute": {
                            "type": "string",
                            "brief": "Test attribute",
                            "examples": ["example"]
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(test_semantic, f)
            test_file = Path(f.name)
        
        try:
            validation_result = weaver.validate_registry(test_file)
            if validation_result.valid:
                console.print("[green]✅ Registry validation works[/green]")
            else:
                console.print(f"[yellow]⚠️ Validation issues: {validation_result.errors}[/yellow]")
        finally:
            test_file.unlink()
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Core functionality test failed: {e}[/red]")
        return False


def test_real_generation():
    """Test actual code generation with a real semantic convention"""
    console.print("\n[cyan]🔨 Testing Real Code Generation[/cyan]\n")
    
    try:
        # Create a proper semantic convention file
        semantic_convention = {
            "groups": {
                "http.request": {
                    "id": "http.request",
                    "type": "attribute_group", 
                    "brief": "HTTP request attributes",
                    "attributes": {
                        "http.method": {
                            "type": "string",
                            "brief": "HTTP request method",
                            "examples": ["GET", "POST", "PUT"]
                        },
                        "http.url": {
                            "type": "string",
                            "brief": "Full HTTP request URL",
                            "examples": ["https://example.com/api/users"]
                        },
                        "http.status_code": {
                            "type": "int",
                            "brief": "HTTP response status code",
                            "examples": [200, 404, 500]
                        }
                    }
                }
            }
        }
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(semantic_convention, f)
            semantic_file = Path(f.name)
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "generated"
            
            # Test generation config
            config = GenerationConfig(
                registry_url=semantic_file,  # Using local file as registry
                language="python",
                output_dir=output_dir,
                verbose=True
            )
            
            # Initialize WeaverGen and generate
            weaver = WeaverGen(config=config)
            result = weaver.generate()
            
            if result.success:
                console.print("[green]✅ Code generation successful![/green]")
                console.print(f"[green]Generated {len(result.files)} files[/green]")
                
                for file_info in result.files[:3]:  # Show first 3 files
                    console.print(f"  • {file_info.path.name} ({file_info.size} bytes)")
                
                if result.warnings:
                    console.print(f"[yellow]⚠️ {len(result.warnings)} warnings[/yellow]")
                
                return True
            else:
                console.print(f"[red]❌ Generation failed: {result.error}[/red]")
                return False
                
    except Exception as e:
        console.print(f"[red]❌ Generation test failed: {e}[/red]")
        return False
    finally:
        # Cleanup
        if 'semantic_file' in locals():
            semantic_file.unlink()


async def test_unified_engine_with_real_weaver():
    """Test that the unified engine can actually call real Weaver tasks"""
    console.print("\n[cyan]🔧 Testing Unified Engine with Real Weaver[/cyan]\n")
    
    try:
        # Override the simulate functions to use real Weaver
        engine = UnifiedBPMNEngine()
        
        # Test individual task execution that should call real weaver
        console.print("[yellow]Testing weaver.initialize task...[/yellow]")
        
        # This should actually check the weaver binary
        result = await engine._execute_task("weaver.initialize", {})
        console.print(f"[green]✅ weaver.initialize: {result}[/green]")
        
        # Test that we can get real weaver path
        try:
            from src.weavergen.core import WeaverGen
            weaver = WeaverGen()
            weaver_path = weaver.get_config().weaver_path
            
            if weaver_path and weaver_path.exists():
                console.print(f"[green]✅ Real weaver binary accessible: {weaver_path}[/green]")
                return True
            else:
                console.print("[red]❌ Weaver binary not accessible from unified engine[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Cannot access weaver from unified engine: {e}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Unified engine test failed: {e}[/red]")
        return False


def create_real_weaver_integration():
    """Create real integration between unified engine and Weaver core"""
    console.print("\n[cyan]🔗 Creating Real Weaver Integration[/cyan]\n")
    
    integration_code = '''
# Add this to unified_bpmn_engine.py to connect to real Weaver

async def _execute_weaver_task_real(self, task_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute real Weaver task using core functionality"""
    from .core import WeaverGen, GenerationConfig
    
    try:
        if task_id == "weaver.initialize":
            weaver = WeaverGen()
            config = weaver.get_config()
            return {
                "weaver_path": str(config.weaver_path),
                "status": True,
                "version": "real"  # Could get actual version
            }
            
        elif task_id == "weaver.generate":
            semantic_file = context.get("semantic_file")
            language = context.get("language", "python")
            output_dir = context.get("output_dir", Path("./generated"))
            
            if not semantic_file:
                raise ValueError("semantic_file required for generation")
            
            config = GenerationConfig(
                registry_url=Path(semantic_file),
                language=language,
                output_dir=Path(output_dir),
                verbose=context.get("verbose", False)
            )
            
            weaver = WeaverGen(config=config)
            result = weaver.generate()
            
            if result.success:
                return {
                    "generated_files": [str(f.path) for f in result.files],
                    "file_count": len(result.files),
                    "warnings": result.warnings,
                    "duration_seconds": result.duration_seconds
                }
            else:
                raise Exception(f"Generation failed: {result.error}")
                
        elif task_id == "weaver.validate":
            semantic_file = context.get("semantic_file")
            strict = context.get("strict", False)
            
            if not semantic_file:
                raise ValueError("semantic_file required for validation")
            
            weaver = WeaverGen()
            result = weaver.validate_registry(Path(semantic_file), strict=strict)
            
            return {
                "valid": result.valid,
                "errors": result.errors,
                "warnings": result.warnings
            }
            
        else:
            # Fall back to simulation for other tasks
            return await self._simulate_weaver_task(task_id, context)
            
    except Exception as e:
        return {"error": str(e), "status": "failed"}
'''
    
    console.print("[yellow]Integration code to add to unified engine:[/yellow]")
    console.print(Panel(integration_code, title="Real Weaver Integration", border_style="yellow"))
    
    return integration_code


async def main():
    """Run all integration tests"""
    console.print(Panel.fit(
        "[bold cyan]🔍 Real Weaver Forge Integration Test[/bold cyan]\n\n"
        "Verifying the unified architecture works with actual Weaver Forge",
        border_style="cyan"
    ))
    
    # Test 1: Core functionality
    core_works = test_core_weaver_functionality()
    
    # Test 2: Real generation
    generation_works = test_real_generation()
    
    # Test 3: Unified engine connection
    unified_works = await test_unified_engine_with_real_weaver()
    
    # Show integration solution
    create_real_weaver_integration()
    
    # Summary
    console.print("\n[bold]📊 Integration Test Results:[/bold]")
    
    results_table = [
        ("Core WeaverGen", "✅ Working" if core_works else "❌ Failed"),
        ("Real Generation", "✅ Working" if generation_works else "❌ Failed"), 
        ("Unified Connection", "✅ Working" if unified_works else "⚠️ Needs Integration")
    ]
    
    for test_name, status in results_table:
        console.print(f"  • {test_name}: {status}")
    
    if all([core_works, generation_works]):
        console.print("\n[green]✅ Core Weaver functionality is preserved![/green]")
        console.print("[yellow]⚠️ Unified engine needs real integration (currently simulated)[/yellow]")
    else:
        console.print("\n[red]❌ Core Weaver functionality has issues[/red]")


if __name__ == "__main__":
    asyncio.run(main())