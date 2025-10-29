#!/usr/bin/env python3
"""
Script to convert all .txt files in current directory to .xml files
"""

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

def is_already_xml(content):
    """Check if content is already in XML format"""
    stripped = content.strip()
    return stripped.startswith('<?xml') or stripped.startswith('<')

def convert_text_to_xml(content, filename):
    """Convert plain text content to XML format"""
    # Remove file extension for use in XML
    base_name = os.path.splitext(filename)[0]
    
    # Create root element
    root_name = re.sub(r'[^a-zA-Z0-9_-]', '_', base_name).lower()
    root = ET.Element(f"boomi_{root_name}")
    
    # Add metadata
    metadata = ET.SubElement(root, "metadata")
    ET.SubElement(metadata, "filename").text = filename
    ET.SubElement(metadata, "converted_date").text = datetime.now().isoformat()
    ET.SubElement(metadata, "original_format").text = "text"
    
    # Add content
    content_elem = ET.SubElement(root, "content")
    
    # Split content into lines and create structured XML
    lines = content.strip().split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line:
            line_elem = ET.SubElement(content_elem, "line")
            line_elem.set("number", str(i + 1))
            line_elem.text = line
    
    # Convert to string with proper formatting
    rough_string = ET.tostring(root, encoding='unicode')
    
    # Add XML declaration and format
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + rough_string
    
    return xml_content

def format_xml_string(xml_string):
    """Format XML string with proper indentation"""
    try:
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_string)
        return dom.toprettyxml(indent="    ", encoding=None)
    except:
        return xml_string

def convert_files_in_current_directory():
    """Convert all .txt files in the current directory to .xml files"""
    
    current_dir = os.getcwd()
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
    
    if not txt_files:
        print(f"No .txt files found in {current_dir}")
        return
    
    print(f"Found {len(txt_files)} .txt files to convert:")
    
    for txt_file in txt_files:
        xml_file = txt_file.replace('.txt', '.xml')
        
        print(f"Converting: {txt_file} -> {xml_file}")
        
        try:
            # Read the text file
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check if it's already XML
            if is_already_xml(content):
                print(f"  ✓ {txt_file} is already in XML format, copying as-is")
                xml_content = content
            else:
                print(f"  ✓ Converting {txt_file} from text to XML format")
                xml_content = convert_text_to_xml(content, txt_file)
                xml_content = format_xml_string(xml_content)
            
            # Write the XML file
            with open(xml_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            print(f"  ✅ Successfully created {xml_file}")
            
        except Exception as e:
            print(f"  ❌ Error converting {txt_file}: {str(e)}")

def main():
    """Main function"""
    print("🔄 Starting conversion of .txt files to .xml files...")
    print(f"📁 Current directory: {os.getcwd()}")
    print("-" * 50)
    
    convert_files_in_current_directory()
    
    print("-" * 50)
    print("✅ Conversion completed!")

if __name__ == "__main__":
    main()
