#!/usr/bin/env python3
"""
Cleanup script for src/weavergen module structure
Identifies generated, experimental, and duplicate files vs core functionality
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Set
import subprocess
import json
from datetime import datetime

def get_git_tracked_files() -> Set[str]:
    """Get list of git-tracked files in src/weavergen/"""
    try:
        result = subprocess.run(
            ["git", "ls-files", "src/weavergen/"],
            capture_output=True,
            text=True,
            cwd="/Users/sac/dev/weavergen"
        )
        if result.returncode == 0:
            return set(result.stdout.strip().split('\n'))
        return set()
    except Exception:
        return set()

def get_git_status() -> Dict[str, str]:
    """Get git status for src/weavergen files"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "src/weavergen/"],
            capture_output=True,
            text=True,
            cwd="/Users/sac/dev/weavergen"
        )
        status = {}
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    status_code = line[:2]
                    filepath = line[3:]
                    status[filepath] = status_code
        return status
    except Exception:
        return {}

def analyze_file_content(filepath: Path) -> Dict[str, any]:
    """Analyze a Python file to understand its purpose and relationships"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'size': len(content),
            'lines': len(content.split('\n')),
            'imports': [],
            'classes': [],
            'functions': [],
            'has_main': '__main__' in content,
            'has_cli': any(x in content.lower() for x in ['typer', 'click', 'argparse', 'cli']),
            'has_ai': any(x in content.lower() for x in ['pydantic_ai', 'agent', 'llm', 'ai']),
            'has_tests': any(x in content.lower() for x in ['test', 'pytest', 'unittest']),
            'docstring': None
        }
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                analysis['imports'].append(stripped)
            elif stripped.startswith('class '):
                analysis['classes'].append(stripped.split('(')[0].replace('class ', ''))
            elif stripped.startswith('def '):
                analysis['functions'].append(stripped.split('(')[0].replace('def ', ''))
            elif i < 5 and stripped.startswith('"""'):
                # Capture docstring from first few lines
                analysis['docstring'] = stripped.strip('"""')
                break
        
        return analysis
    except Exception as e:
        return {'error': str(e)}

def categorize_weavergen_files() -> Dict[str, List[Tuple[str, Dict]]]:
    """Categorize all files in src/weavergen"""
    weavergen_dir = Path("/Users/sac/dev/weavergen/src/weavergen")
    
    if not weavergen_dir.exists():
        return {"error": ["Directory not found"]}
    
    tracked_files = get_git_tracked_files()
    git_status = get_git_status()
    
    categories = {
        "core_tracked": [],      # Essential tracked files
        "modified_tracked": [],  # Tracked files with modifications
        "experimental": [],      # Untracked experimental files
        "cli_variants": [],      # Multiple CLI implementations
        "semantic_extensions": [], # AI/semantic functionality
        "duplicates": [],        # Potential duplicate functionality
        "cache": [],            # Cache and temporary files
        "deletable": []         # Safe to delete
    }
    
    for file_path in weavergen_dir.iterdir():
        if file_path.is_file():
            rel_path = str(file_path.relative_to(Path("/Users/sac/dev/weavergen")))
            filename = file_path.name
            
            # Analyze file content
            analysis = analyze_file_content(file_path)
            file_info = (rel_path, {
                'filename': filename,
                'size_kb': file_path.stat().st_size / 1024,
                'analysis': analysis,
                'git_status': git_status.get(rel_path, 'untracked')
            })
            
            # Categorize based on patterns and git status
            if filename.startswith('__pycache__') or filename.endswith('.pyc'):
                categories["cache"].append(file_info)
            elif rel_path in tracked_files:
                if rel_path in git_status and git_status[rel_path].strip() == 'M':
                    categories["modified_tracked"].append(file_info)
                else:
                    categories["core_tracked"].append(file_info)
            elif 'cli' in filename and filename != 'cli.py':
                categories["cli_variants"].append(file_info)
            elif 'semantic' in filename:
                categories["semantic_extensions"].append(file_info)
            elif any(x in filename for x in ['comprehensive', 'v1', 'mock', 'enhancement']):
                categories["experimental"].append(file_info)
            else:
                categories["experimental"].append(file_info)
    
    # Identify potential duplicates and deletables
    cli_files = [f for f in categories["cli_variants"] if 'cli' in f[1]['filename']]
    if len(cli_files) > 1:
        # Mark additional CLI files as potential duplicates
        for cli_file in cli_files[1:]:  # Keep first, mark others as duplicates
            categories["duplicates"].append(cli_file)
            if cli_file in categories["cli_variants"]:
                categories["cli_variants"].remove(cli_file)
    
    # Mark cache files as deletable
    categories["deletable"] = categories["cache"]
    
    return categories

def generate_cleanup_recommendations() -> Dict[str, any]:
    """Generate specific cleanup recommendations for src/weavergen"""
    categories = categorize_weavergen_files()
    
    recommendations = {
        "keep_essential": [],
        "evaluate_for_integration": [],
        "safe_to_delete": [],
        "requires_review": [],
        "stats": {}
    }
    
    # Essential files to keep
    recommendations["keep_essential"] = (
        categories.get("core_tracked", []) + 
        categories.get("modified_tracked", [])
    )
    
    # Files that might need integration
    recommendations["evaluate_for_integration"] = (
        categories.get("semantic_extensions", []) +
        categories.get("cli_variants", [])
    )
    
    # Safe to delete
    recommendations["safe_to_delete"] = (
        categories.get("cache", []) +
        categories.get("duplicates", [])
    )
    
    # Requires manual review
    recommendations["requires_review"] = categories.get("experimental", [])
    
    # Calculate stats
    total_files = sum(len(cat) for cat in categories.values())
    deletable_size = sum(f[1]['size_kb'] for f in recommendations["safe_to_delete"])
    
    recommendations["stats"] = {
        "total_files": total_files,
        "keep_count": len(recommendations["keep_essential"]),
        "evaluate_count": len(recommendations["evaluate_for_integration"]),
        "delete_count": len(recommendations["safe_to_delete"]),
        "review_count": len(recommendations["requires_review"]),
        "deletable_size_kb": deletable_size
    }
    
    return recommendations

def create_cleanup_report() -> str:
    """Create a detailed cleanup report"""
    recommendations = generate_cleanup_recommendations()
    
    report = f"""
# WeaverGen Module Cleanup Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total files: {recommendations['stats']['total_files']}
- Keep (essential): {recommendations['stats']['keep_count']}
- Evaluate for integration: {recommendations['stats']['evaluate_count']} 
- Safe to delete: {recommendations['stats']['delete_count']}
- Requires review: {recommendations['stats']['review_count']}
- Deletable size: {recommendations['stats']['deletable_size_kb']:.2f} KB

## Keep Essential (Core Functionality)
"""
    
    for filepath, info in recommendations["keep_essential"]:
        status = info['git_status']
        docstring = info['analysis'].get('docstring', 'No description')
        report += f"✅ {filepath} ({status}) - {docstring}\n"
    
    report += "\n## Evaluate for Integration\n"
    for filepath, info in recommendations["evaluate_for_integration"]:
        docstring = info['analysis'].get('docstring', 'No description')
        has_cli = info['analysis'].get('has_cli', False)
        has_ai = info['analysis'].get('has_ai', False)
        size = info['size_kb']
        report += f"🔄 {filepath} ({size:.1f}KB) - {docstring}\n"
        if has_cli:
            report += f"   - Contains CLI functionality\n"
        if has_ai:
            report += f"   - Contains AI/Pydantic features\n"
    
    report += "\n## Safe to Delete\n"
    for filepath, info in recommendations["safe_to_delete"]:
        size = info['size_kb']
        reason = "Cache file" if info['filename'].startswith('__') else "Duplicate"
        report += f"❌ {filepath} ({size:.1f}KB) - {reason}\n"
    
    report += "\n## Requires Manual Review\n"
    for filepath, info in recommendations["requires_review"]:
        docstring = info['analysis'].get('docstring', 'No description')
        size = info['size_kb']
        lines = info['analysis'].get('lines', 0)
        report += f"❓ {filepath} ({size:.1f}KB, {lines} lines) - {docstring}\n"
    
    return report

def execute_safe_cleanup(dry_run=True) -> Dict[str, any]:
    """Execute the safe cleanup operations"""
    recommendations = generate_cleanup_recommendations()
    results = {"deleted": [], "errors": [], "dry_run": dry_run}
    
    for filepath, info in recommendations["safe_to_delete"]:
        full_path = Path("/Users/sac/dev/weavergen") / filepath
        
        try:
            if not dry_run:
                if full_path.exists():
                    if full_path.is_file():
                        full_path.unlink()
                    elif full_path.is_dir():
                        shutil.rmtree(full_path)
                    results["deleted"].append(str(filepath))
            else:
                results["deleted"].append(f"[DRY RUN] {filepath}")
        except Exception as e:
            results["errors"].append(f"Error deleting {filepath}: {e}")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print("🧹 Executing safe cleanup...")
        results = execute_safe_cleanup(dry_run=False)
        print(f"Deleted {len(results['deleted'])} items")
        if results['errors']:
            print(f"Errors: {results['errors']}")
    elif len(sys.argv) > 1 and sys.argv[1] == "--json":
        recommendations = generate_cleanup_recommendations()
        print(json.dumps(recommendations, indent=2))
    else:
        print("🔍 WeaverGen Module Analysis")
        print("=" * 50)
        report = create_cleanup_report()
        print(report)
        print("\nRun with --execute to perform safe cleanup")
        print("Run with --json for machine-readable output")