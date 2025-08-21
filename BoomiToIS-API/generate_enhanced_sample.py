#!/usr/bin/env python3
"""
Generate enhanced documentation sample to showcase improvements
"""

import os
from boomi_xml_processor import BoomiXMLProcessor

def generate_enhanced_sample():
    """Generate enhanced documentation sample"""
    
    # Test files
    test_files = [
        '../pepsi/Pepsi-boomi-xml/00_main_flow_3c0b145b-dd1a-45f4-9289-9aaf7d592a9a.xml',
        '../pepsi/Pepsi-boomi-xml/sub_4fef22a1/00_subprocess_4fef22a1-66b8-4874-bab0-74afe13bed36.xml',
        '../pepsi/Pepsi-boomi-xml/sub_31a87c8f/00_subprocess_31a87c8f-19d7-4288-a6c7-929e94724a6a.xml'
    ]
    
    processor = BoomiXMLProcessor()
    
    # Process all files
    for xml_file in test_files:
        if os.path.exists(xml_file):
            processor._process_xml_file(xml_file)
    
    # Generate enhanced markdown
    enhanced_markdown = processor._generate_markdown()
    
    # Save to file
    output_file = 'enhanced_pepsi_documentation_sample.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_markdown)
    
    print(f"✅ Enhanced documentation saved to: {output_file}")
    print(f"📊 Total length: {len(enhanced_markdown):,} characters")
    
    # Show first section as preview
    lines = enhanced_markdown.split('\n')
    preview_lines = lines[:50]  # First 50 lines
    
    print("\n🔍 PREVIEW OF ENHANCED DOCUMENTATION:")
    print("=" * 60)
    for line in preview_lines:
        print(line)
    print("=" * 60)
    print(f"... and {len(lines) - 50} more lines with detailed configurations!")

if __name__ == "__main__":
    generate_enhanced_sample()

