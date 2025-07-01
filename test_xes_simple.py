#!/usr/bin/env python3
"""Simple XES conversion test"""

import json
from src.weavergen.xes_converter import XESConverter
from rich.console import Console

def main():
    console = Console()
    
    # Load spans
    with open("final_8020_output/execution_spans.json") as f:
        spans = json.load(f)
    
    console.print(f"Loaded {len(spans)} spans")
    
    # Convert to XES
    converter = XESConverter()
    result = converter.spans_to_xes(spans, "simple_test.xes")
    
    console.print(f"✅ Converted to: {result}")

if __name__ == "__main__":
    main()