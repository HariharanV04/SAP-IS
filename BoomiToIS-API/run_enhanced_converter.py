#!/usr/bin/env python3
"""
Wrapper script to run the enhanced JSON to iFlow converter
"""
import sys
from pathlib import Path
from enhanced_component_generation.enhanced_json_to_iflow_converter import EnhancedJSONToIFlowConverter

def main():
    if len(sys.argv) < 3:
        print("Usage: python run_enhanced_converter.py <input_json> <output_directory>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_dir = sys.argv[2]

    print(f"Converting {input_json} to iFlow in {output_dir}...")

    converter = EnhancedJSONToIFlowConverter()
    result = converter.convert(input_json, output_dir)

    print(f"Conversion complete! Output: {result}")

if __name__ == "__main__":
    main()
