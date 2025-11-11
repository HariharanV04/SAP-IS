#!/usr/bin/env python3
"""
Simple wrapper to run the enhanced iFlow generator without Unicode issues
"""
import sys
import os
from enhanced_component_generation.enhanced_iflow_generator import EnhancedIFlowGenerator

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_generator.py <input_json> <output_dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    print(f"Generating iFlow from {input_file}...")
    print(f"Output directory: {output_dir}")

    generator = EnhancedIFlowGenerator()
    try:
        zip_path = generator.generate_iflow(input_file, output_dir, "SimpleXMLtoJSON")
        print(f"Success! Generated: {zip_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
