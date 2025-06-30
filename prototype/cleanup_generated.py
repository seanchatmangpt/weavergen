#!/usr/bin/env python3
"""
Clean up generated files while preserving customized ones
Analyzes what can be safely deleted vs what should be kept
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple
import json

# Files/directories that can be safely deleted
DELETABLE_PATTERNS = {
    'directories': [
        'output/commands',
        'output/contracts', 
        'output/runtime',
        'output/roberts',
        'output/roberts_generated',
        'output/complete_system',
        'generated',
        'generated_cli',
        'generated_v2',
        'test_output',
        'otel_test_output',
        'logs',
        'telemetry',
        'temp',
        'venv',
        '__pycache__'
    ],
    'files': [
        'cli_validation_results.json',
        'concurrent_validation_results.json',
        'ollama_gpu_benchmark.json',
        'ollama_benchmark_results.json',
        'ollama_metal_benchmark.json',
        'roberts_otel_trace.csv',
        'telemetry.csv',
        'telemetry_5_agents.csv',
        'validation_test.json',
        'weaver_forge_roberts_telemetry.json',
        'prototype_export.json',
        'forge_output.json',
        'VALIDATION_SUMMARY.md'
    ],
    'patterns': [
        '*.pyc',
        '.pytest_cache',
        'temp_*'
    ]
}

# Files that were generated but customized (should keep)
CUSTOMIZED_FILES = [
    'output/operations/forge.py',  # AI-EDITABLE business logic
    'roberts_integrated_operations.py',  # Integration layer
    'complete_pydantic_models.py',  # Generated but useful
]

# Core files that must be kept (partial list for reference)
CORE_FILES = {
    'semantics': ['*.yaml'],
    'templates': ['templates/**'],
    'scripts': ['*.py'],
    'docs': ['*.md'],
    'config': ['Makefile', 'requirements.txt', 'setup.sh']
}

def analyze_deletable_files() -> Tuple[List[Path], List[Path], int]:
    """Analyze what can be deleted and calculate space savings"""
    deletable = []
    customized = []
    total_size = 0
    
    # Check directories
    for dir_pattern in DELETABLE_PATTERNS['directories']:
        dir_path = Path(dir_pattern)
        if dir_path.exists():
            # Check if it contains customized files
            has_customized = False
            if dir_path.name == 'operations':
                for custom in CUSTOMIZED_FILES:
                    if Path(custom).exists() and str(Path(custom).parent) == str(dir_path):
                        has_customized = True
                        customized.append(Path(custom))
            
            if not has_customized:
                deletable.append(dir_path)
                # Calculate size
                for item in dir_path.rglob('*'):
                    if item.is_file():
                        total_size += item.stat().st_size
    
    # Check individual files
    for file_pattern in DELETABLE_PATTERNS['files']:
        file_path = Path(file_pattern)
        if file_path.exists():
            deletable.append(file_path)
            total_size += file_path.stat().st_size
    
    # Check patterns
    for pattern in DELETABLE_PATTERNS['patterns']:
        for file_path in Path('.').rglob(pattern):
            if file_path.exists():
                deletable.append(file_path)
                if file_path.is_file():
                    total_size += file_path.stat().st_size
    
    return deletable, customized, total_size

def create_deletion_report():
    """Create a detailed report of what will be deleted"""
    deletable, customized, total_size = analyze_deletable_files()
    
    report = {
        'deletable': {
            'count': len(deletable),
            'size_mb': total_size / (1024 * 1024),
            'items': [str(p) for p in sorted(deletable)]
        },
        'customized_kept': {
            'count': len(customized),
            'items': [str(p) for p in sorted(customized)]
        },
        'summary': {
            'total_files': len(list(Path('.').rglob('*'))),
            'to_delete': len(deletable),
            'percentage': (len(deletable) / len(list(Path('.').rglob('*')))) * 100
        }
    }
    
    return report

def clean_generated_files(dry_run=True):
    """Clean up generated files"""
    deletable, customized, total_size = analyze_deletable_files()
    
    print(f"🧹 Cleanup Analysis")
    print("=" * 60)
    print(f"Files/dirs to delete: {len(deletable)}")
    print(f"Space to reclaim: {total_size / (1024 * 1024):.2f} MB")
    print(f"Customized files preserved: {len(customized)}")
    
    if dry_run:
        print("\n🔍 DRY RUN - No files will be deleted")
        print("\nFiles that would be deleted:")
        for item in sorted(deletable)[:10]:
            print(f"  • {item}")
        if len(deletable) > 10:
            print(f"  ... and {len(deletable) - 10} more")
    else:
        print("\n🗑️  Deleting files...")
        deleted = 0
        for item in deletable:
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                deleted += 1
            except Exception as e:
                print(f"  ❌ Error deleting {item}: {e}")
        
        print(f"\n✅ Deleted {deleted} items")
        print(f"   Reclaimed {total_size / (1024 * 1024):.2f} MB")
    
    # Save report
    report = create_deletion_report()
    with open('cleanup_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Report saved to cleanup_report.json")

def show_customized_files():
    """Show files that were generated but customized"""
    print("\n📝 Customized Generated Files (Preserved)")
    print("=" * 60)
    
    for file in CUSTOMIZED_FILES:
        if Path(file).exists():
            size = Path(file).stat().st_size / 1024
            print(f"✓ {file} ({size:.1f} KB)")
            
            # Check for AI-EDITABLE marker
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    if 'AI-EDITABLE' in content:
                        print(f"  → Contains AI-EDITABLE marker")
                    if 'DO NOT EDIT' not in content:
                        print(f"  → Safe to edit")
            except:
                pass

def main():
    """Main cleanup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean generated files from prototype')
    parser.add_argument('--execute', action='store_true', help='Actually delete files (default is dry run)')
    parser.add_argument('--report', action='store_true', help='Just show report without cleaning')
    parser.add_argument('--customized', action='store_true', help='Show customized files')
    
    args = parser.parse_args()
    
    if args.customized:
        show_customized_files()
    elif args.report:
        report = create_deletion_report()
        print(json.dumps(report, indent=2))
    else:
        clean_generated_files(dry_run=not args.execute)

if __name__ == "__main__":
    main()