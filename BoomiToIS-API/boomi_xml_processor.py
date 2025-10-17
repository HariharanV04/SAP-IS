#!/usr/bin/env python3
"""
Boomi XML Processor - Utility to process Boomi XML files and convert them to markdown for GenAI analysis
"""

import os
import zipfile
import xml.etree.ElementTree as ET
import tempfile
import shutil
from typing import List, Dict, Any

class BoomiXMLProcessor:
    """Process Boomi XML files and extract meaningful information for conversion"""
    
    def __init__(self):
        self.components = []
        self.process_info = {}
    
    def process_zip_file(self, zip_path: str) -> str:
        """
        Process a ZIP file containing Boomi XML components
        
        Args:
            zip_path (str): Path to the ZIP file
            
        Returns:
            str: Markdown representation of the Boomi process
        """
        print(f"📦 Processing Boomi ZIP file: {zip_path}")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            # Find all XML files
            xml_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.xml'):
                        xml_files.append(os.path.join(root, file))
            
            print(f"📄 Found {len(xml_files)} XML files")
            
            # Process each XML file
            for xml_file in xml_files:
                self._process_xml_file(xml_file)
            
            # Generate markdown representation
            return self._generate_markdown()
    
    def _process_xml_file(self, xml_path: str):
        """Process a single Boomi XML file (may contain multiple XML documents)"""
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split content by XML declaration to handle multiple documents
            xml_documents = self._split_xml_documents(content)

            for i, xml_doc in enumerate(xml_documents):
                if xml_doc.strip():
                    try:
                        # Parse each XML document separately
                        root = ET.fromstring(xml_doc)

                        # Extract component information
                        component_info = self._extract_component_info(root, xml_doc)
                        if component_info:
                            self.components.append(component_info)
                            print(f"✅ Processed component {i+1}: {component_info['name']} ({component_info['type']})")
                    except ET.XMLSyntaxError as e:
                        print(f"⚠️ XML parsing error in document {i+1}: {e}")
                        continue

        except Exception as e:
            print(f"❌ Error processing {xml_path}: {e}")

    def _split_xml_documents(self, content: str) -> List[str]:
        """Split content into separate XML documents"""
        # Look for XML declarations to split documents
        import re

        # Find all XML declarations
        xml_pattern = r'<\?xml[^>]*\?>'
        matches = list(re.finditer(xml_pattern, content))

        if len(matches) <= 1:
            # Single document
            return [content]

        documents = []
        for i, match in enumerate(matches):
            start = match.start()
            if i + 1 < len(matches):
                end = matches[i + 1].start()
                documents.append(content[start:end])
            else:
                documents.append(content[start:])

        return documents
    
    def _extract_component_info(self, root: ET.Element, raw_content: str) -> Dict[str, Any]:
        """Extract component information from XML"""
        
        # Get basic component attributes
        component_info = {
            'id': root.get('componentId', ''),
            'name': root.get('name', ''),
            'type': root.get('type', ''),
            'subtype': root.get('subType', ''),
            'description': '',
            'mappings': [],
            'operations': [],
            'functions': [],
            'raw_content': raw_content
        }
        
        # Extract description
        desc_elem = root.find('.//{http://api.platform.boomi.com/}description')
        if desc_elem is not None:
            component_info['description'] = desc_elem.text or ''
        
        # Process based on component type
        if component_info['type'] == 'transform.map':
            self._extract_map_info(root, component_info)
        elif component_info['type'] == 'connector-action':
            self._extract_connector_info(root, component_info)
        
        return component_info
    
    def _extract_map_info(self, root: ET.Element, component_info: Dict[str, Any]):
        """Extract information from transform/map components"""
        
        # Find mappings
        for mapping in root.findall('.//Mapping'):
            mapping_info = {
                'from_key': mapping.get('fromKey', ''),
                'to_key': mapping.get('toKey', ''),
                'from_type': mapping.get('fromType', ''),
                'to_type': mapping.get('toType', ''),
                'to_name_path': mapping.get('toNamePath', ''),
                'from_function': mapping.get('fromFunction', '')
            }
            component_info['mappings'].append(mapping_info)
        
        # Find functions
        for function in root.findall('.//FunctionStep'):
            function_info = {
                'name': function.get('name', ''),
                'type': function.get('type', ''),
                'category': function.get('category', ''),
                'key': function.get('key', '')
            }
            
            # Extract document properties
            doc_prop = function.find('.//DocumentProperty')
            if doc_prop is not None:
                function_info['property_id'] = doc_prop.get('propertyId', '')
                function_info['property_name'] = doc_prop.get('propertyName', '')
            
            component_info['functions'].append(function_info)
    
    def _extract_connector_info(self, root: ET.Element, component_info: Dict[str, Any]):
        """Extract information from connector action components"""
        
        # Find Salesforce operations
        sf_action = root.find('.//SalesforceSendAction')
        if sf_action is not None:
            operation_info = {
                'type': 'salesforce',
                'object_action': sf_action.get('objectAction', ''),
                'object_name': sf_action.get('objectName', ''),
                'batch_size': sf_action.get('batchSize', ''),
                'use_bulk_api': sf_action.get('useBulkAPI', ''),
                'fields': []
            }
            
            # Extract field information
            for field in sf_action.findall('.//SalesforceField'):
                field_info = {
                    'name': field.get('name', ''),
                    'data_type': field.get('dataType', ''),
                    'custom': field.get('custom', ''),
                    'nillable': field.get('nillable', ''),
                    'enabled': field.get('fEnabled', '')
                }
                operation_info['fields'].append(field_info)
            
            component_info['operations'].append(operation_info)
    
    def _generate_markdown(self) -> str:
        """Generate markdown representation of the Boomi process"""
        
        if not self.components:
            return "# Boomi Process\n\nNo components found in the uploaded files."
        
        # Determine process name from components
        process_name = "Boomi Integration Process"
        if self.components:
            # Try to extract a meaningful name from component names or descriptions
            names = [comp['name'] for comp in self.components if comp['name']]
            if names:
                process_name = f"Boomi Process: {' + '.join(names[:2])}"
        
        markdown = f"# {process_name}\n\n"
        
        # Add process overview
        markdown += "## Process Overview\n\n"
        markdown += f"This Boomi integration process contains {len(self.components)} components:\n\n"
        
        for i, comp in enumerate(self.components, 1):
            markdown += f"{i}. **{comp['name']}** ({comp['type']})\n"
        
        markdown += "\n"
        
        # Add detailed component information
        for i, comp in enumerate(self.components, 1):
            markdown += f"## Component {i}: {comp['name']}\n\n"
            markdown += f"**Type**: {comp['type']}\n"
            if comp['subtype']:
                markdown += f"**Subtype**: {comp['subtype']}\n"
            if comp['description']:
                markdown += f"**Description**: {comp['description']}\n"
            markdown += "\n"
            
            # Add mappings for transform components
            if comp['mappings']:
                markdown += "### Data Mappings\n\n"
                for mapping in comp['mappings']:
                    if mapping['to_name_path']:
                        markdown += f"- **{mapping['to_name_path']}**: Mapped from {mapping['from_type']}\n"
                    else:
                        markdown += f"- **{mapping['to_key']}**: Mapped from {mapping['from_key']}\n"
                markdown += "\n"
            
            # Add functions for transform components
            if comp['functions']:
                markdown += "### Functions\n\n"
                for func in comp['functions']:
                    markdown += f"- **{func['name']}** ({func['type']})\n"
                    if func.get('property_name'):
                        markdown += f"  - Property: {func['property_name']}\n"
                markdown += "\n"
            
            # Add operations for connector components
            if comp['operations']:
                markdown += "### Operations\n\n"
                for op in comp['operations']:
                    if op['type'] == 'salesforce':
                        markdown += f"**Salesforce {op['object_action'].upper()} Operation**\n\n"
                        markdown += f"- **Object**: {op['object_name']}\n"
                        markdown += f"- **Action**: {op['object_action']}\n"
                        if op['batch_size']:
                            markdown += f"- **Batch Size**: {op['batch_size']}\n"
                        
                        if op['fields']:
                            markdown += f"\n**Fields** ({len(op['fields'])} total):\n"
                            # Show first 10 fields to avoid overwhelming the prompt
                            for field in op['fields'][:10]:
                                markdown += f"- {field['name']} ({field['data_type']})\n"
                            if len(op['fields']) > 10:
                                markdown += f"- ... and {len(op['fields']) - 10} more fields\n"
                markdown += "\n"
            
            # Add raw XML content (truncated for prompt efficiency)
            markdown += "### XML Configuration\n\n"
            markdown += "```xml\n"
            # Truncate very long XML content
            xml_content = comp['raw_content']
            if len(xml_content) > 2000:
                xml_content = xml_content[:2000] + "\n<!-- Content truncated for brevity -->\n"
            markdown += xml_content
            markdown += "\n```\n\n"
        
        return markdown

# Example usage function
def process_boomi_zip(zip_path: str) -> str:
    """
    Convenience function to process a Boomi ZIP file
    
    Args:
        zip_path (str): Path to the Boomi ZIP file
        
    Returns:
        str: Markdown representation suitable for GenAI processing
    """
    processor = BoomiXMLProcessor()
    return processor.process_zip_file(zip_path)

if __name__ == "__main__":
    # Test with the sample files
    print("🧪 Testing Boomi XML Processor")
    
    # Create a test ZIP file
    test_zip = "test_boomi.zip"
    with zipfile.ZipFile(test_zip, 'w') as zf:
        zf.write("../boomi-api/comp1.xml", "comp1.xml")
        zf.write("../boomi-api/comp2.xml", "comp2.xml")
    
    try:
        # Process the ZIP file
        markdown = process_boomi_zip(test_zip)
        print(f"✅ Generated markdown ({len(markdown)} characters)")
        
        # Save the result
        with open("boomi_process_analysis.md", "w", encoding="utf-8") as f:
            f.write(markdown)
        print("✅ Saved analysis to boomi_process_analysis.md")
        
    finally:
        # Cleanup
        if os.path.exists(test_zip):
            os.remove(test_zip)
