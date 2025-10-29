import os
import sys
import json
import logging
import glob
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "final"))

# Import necessary modules
try:
    from mule_flow_documentation import FlowDocumentationGenerator, MuleFlowParser
    from additional_file_parser import AdditionalFileParser
except ImportError as e:
    logging.error(f"Error importing required modules: {str(e)}")
    sys.exit(1)

class EnhancedDocumentationGenerator(FlowDocumentationGenerator):
    """
    Enhanced documentation generator that extends the base FlowDocumentationGenerator
    to include additional file types like DWL, YAML, and RAML in the documentation.
    """
    
    def __init__(self):
        super().__init__()
        self.additional_parser = AdditionalFileParser()
    
    def generate_documentation(self, parsed_data: Dict, additional_files: Dict = None, project_dir: str = None) -> str:
        """
        Generate complete documentation including additional file types.
        
        Args:
            parsed_data: Dictionary with parsed Mule flows and components from MuleFlowParser
            additional_files: Dictionary with parsed additional files (DWL, YAML, RAML)
            project_dir: Root directory of the project for finding existing markdown files
            
        Returns:
            Markdown documentation as a string
        """
        try:
            # Get base documentation from parent class
            doc = super().generate_documentation(parsed_data)
            
            # If no additional files, check if we should still look for markdown
            if not additional_files:
                if project_dir:
                    return self._include_existing_markdown_files(doc, project_dir)
                return doc
            
            # Add separator and additional files section
            doc += "\n\n# Additional Resources\n\n"
            doc += "This section contains documentation for additional resources used in the Mule application.\n\n"
            
            # Add API Documentation (RAML) first since it's most important
            doc += self._generate_raml_documentation(additional_files.get('raml_files', {}))
            
            # Add DataWeave transformations
            doc += self._generate_dwl_documentation(additional_files.get('dwl_files', {}))
            
            # Add YAML configurations
            doc += self._generate_yaml_documentation(additional_files.get('yaml_files', {}))
            
            # Add properties files
            doc += self._generate_properties_documentation(additional_files.get('properties_files', {}))
            
            # Add JSON files
            doc += self._generate_json_documentation(additional_files.get('json_files', {}))
            
            # Include existing markdown documentation if project directory is provided
            if project_dir:
                doc = self._include_existing_markdown_files(doc, project_dir)
            
            return doc
            
        except Exception as e:
            logging.error(f"Error generating enhanced documentation: {e}")
            return doc + f"\n\n## Error Adding Additional Resources\n\nAn error occurred while adding additional resources to the documentation: {str(e)}\n"
    
    def _include_existing_markdown_files(self, doc: str, project_dir: str) -> str:
        """
        Find and include existing markdown files from the project's documentation folders.
        
        Args:
            doc: The current documentation as a string
            project_dir: Root directory of the project
            
        Returns:
            Updated documentation string with existing markdown content
        """
        try:
            # Look for documentation directories - common patterns
            doc_dirs = []
            
            # Check for 'documentation' folder at the same level as 'src'
            src_parent = os.path.dirname(os.path.join(project_dir, 'src')) if os.path.exists(os.path.join(project_dir, 'src')) else project_dir
            doc_dir = os.path.join(src_parent, 'documentation')
            if os.path.exists(doc_dir) and os.path.isdir(doc_dir):
                doc_dirs.append(doc_dir)
            
            # Check for 'docs' folder at the root
            docs_dir = os.path.join(project_dir, 'docs')
            if os.path.exists(docs_dir) and os.path.isdir(docs_dir):
                doc_dirs.append(docs_dir)
            
            # Check for any folder containing "doc" in the name at the root level
            for item in os.listdir(project_dir):
                if 'doc' in item.lower() and os.path.isdir(os.path.join(project_dir, item)):
                    doc_path = os.path.join(project_dir, item)
                    if doc_path not in doc_dirs:
                        doc_dirs.append(doc_path)
            
            if not doc_dirs:
                return doc
            
            # Find markdown files in the doc directories (including subdirectories)
            markdown_files = []
            for doc_dir in doc_dirs:
                for root, _, files in os.walk(doc_dir):
                    for file in files:
                        if file.lower().endswith(('.md', '.markdown')) and not file.startswith('.'):
                            # Skip files that are likely to be auto-generated or not useful for inclusion
                            if file.lower() in ['readme.md', 'changelog.md', 'license.md']:
                                continue
                            markdown_files.append(os.path.join(root, file))
            
            if not markdown_files:
                return doc
            
            # Add existing documentation section
            doc += "\n\n# Existing Project Documentation\n\n"
            doc += "This section includes existing markdown documentation found in the project.\n\n"
            
            # Sort files by name for consistent output
            markdown_files.sort(key=lambda x: os.path.basename(x).lower())
            
            # Generate a table of contents for the markdown files
            doc += "## Available Documentation Files\n\n"
            doc += "| # | File Name | Location | Size |\n"
            doc += "|---|-----------|----------|------|\n"
            
            for i, file_path in enumerate(markdown_files, 1):
                file_name = os.path.basename(file_path)
                rel_path = os.path.relpath(file_path, project_dir)
                size = f"{os.path.getsize(file_path) / 1024:.1f} KB"
                
                doc += f"| {i} | {file_name} | {rel_path} | {size} |\n"
            
            doc += "\n"
            
            # Include the content of each markdown file
            for file_path in markdown_files:
                file_name = os.path.basename(file_path)
                rel_path = os.path.relpath(file_path, project_dir)
                
                doc += f"## {file_name}\n\n"
                doc += f"**Path:** `{rel_path}`\n\n"
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Look for title in the markdown
                        title = None
                        if content.startswith('# '):
                            title = content.split('\n')[0].lstrip('# ').strip()
                        
                        if title:
                            doc += f"**Title:** {title}\n\n"
                        
                        # Add a separator for clarity
                        doc += "---\n\n"
                        
                        # Add the content
                        doc += content
                        
                        # Add a separator between files
                        doc += "\n\n---\n\n"
                except Exception as e:
                    doc += f"*Error reading file: {str(e)}*\n\n---\n\n"
            
            return doc
            
        except Exception as e:
            logging.error(f"Error including existing markdown files: {e}")
            return doc + f"\n\n## Error Including Existing Documentation\n\nAn error occurred while including existing markdown files: {str(e)}\n"
    
    def _generate_dwl_documentation(self, dwl_files: Dict) -> str:
        """Generate documentation for DataWeave files."""
        if not dwl_files:
            return ""
        
        doc = "## DataWeave Transformations\n\n"
        doc += f"The application includes {len(dwl_files)} DataWeave transformation files.\n\n"
        
        # Add summary table of all DWL files
        doc += "| # | File Name | DataWeave Version | Type | Size |\n"
        doc += "|---|-----------|-------------------|------|------|\n"
        
        # Sort files by name for consistent output
        sorted_files = sorted(dwl_files.items(), key=lambda x: os.path.basename(x[0]).lower())
        for i, (file_path, file_data) in enumerate(sorted_files, 1):
            file_name = os.path.basename(file_path)
            version = file_data.get('dw_version', 'Unknown')
            type_hints = ", ".join(file_data.get('type_hints', ['']))[:30] + ("..." if len(", ".join(file_data.get('type_hints', ['']))) > 30 else "")
            size = f"{file_data.get('size', 0) / 1024:.1f} KB"
            
            doc += f"| {i} | {file_name} | {version} | {type_hints} | {size} |\n"
        
        doc += "\n### Individual DataWeave Files\n\n"
        
        # Add detailed section for each file
        for file_path, file_data in sorted_files:
            doc += f"#### {os.path.basename(file_path)}\n\n"
            
            # Add metadata about the transformation
            doc += f"**Path:** `{file_path}`\n\n"
            
            if 'dw_version' in file_data:
                doc += f"**DataWeave Version:** {file_data['dw_version']}\n\n"
            
            if 'type_hints' in file_data and file_data['type_hints']:
                doc += f"**Type:** {', '.join(file_data['type_hints'])}\n\n"
            
            if 'functions' in file_data and file_data['functions']:
                doc += "**Functions:**\n"
                for func in file_data['functions']:
                    doc += f"- `{func}`\n"
                doc += "\n"
            
            if 'variables' in file_data and file_data['variables']:
                doc += "**Variables:**\n"
                for var in file_data['variables']:
                    doc += f"- `{var}`\n"
                doc += "\n"
            
            # Add content with syntax highlighting
            if 'content' in file_data and file_data['content'] and not isinstance(file_data['content'], dict):
                # Limit content length to prevent extremely large files
                content = file_data['content']
                if len(content) > 2000:
                    content = content[:2000] + "\n\n... (content truncated) ..."
                
                doc += "**Source:**\n\n```dataweave\n"
                doc += content
                doc += "\n```\n\n"
            
            doc += "---\n\n"
        
        return doc
    
    def _generate_raml_documentation(self, raml_files: Dict) -> str:
        """Generate documentation for RAML API definition files."""
        if not raml_files:
            return ""
        
        doc = "## API Definitions (RAML)\n\n"
        doc += f"The application includes {len(raml_files)} RAML API definition files.\n\n"
        
        # Identify main API definition files (those with title, endpoints, etc)
        main_api_files = {}
        library_files = {}
        type_files = {}
        example_files = {}
        other_files = {}
        
        # Categorize RAML files
        for file_path, file_data in raml_files.items():
            file_name = os.path.basename(file_path)
            
            # Skip files with parsing errors
            if 'error' in file_data:
                other_files[file_path] = file_data
                continue
                
            # Check if it's a main API definition file
            if 'api_info' in file_data and file_data['api_info'].get('title') and file_data['api_info'].get('endpoints'):
                main_api_files[file_path] = file_data
            # Check if it's a library file
            elif 'Library' in file_name:
                library_files[file_path] = file_data
            # Check if it's a type definition
            elif 'Type' in file_name:
                type_files[file_path] = file_data
            # Check if it's an example file
            elif 'Example' in file_name:
                example_files[file_path] = file_data
            # Other RAML files
            else:
                other_files[file_path] = file_data
        
        # Add summary of all RAML files
        doc += "### RAML Files Summary\n\n"
        doc += "| # | File Name | Type | Description |\n"
        doc += "|---|-----------|------|-------------|\n"
        
        # Group files by category for the summary table
        all_files_sorted = []
        for file_path, file_data in sorted(main_api_files.items(), key=lambda x: os.path.basename(x[0]).lower()):
            all_files_sorted.append((file_path, file_data, "Main API Definition"))
        
        for file_path, file_data in sorted(library_files.items(), key=lambda x: os.path.basename(x[0]).lower()):
            all_files_sorted.append((file_path, file_data, "Library"))
            
        for file_path, file_data in sorted(type_files.items(), key=lambda x: os.path.basename(x[0]).lower()):
            all_files_sorted.append((file_path, file_data, "Type Definition"))
            
        for file_path, file_data in sorted(example_files.items(), key=lambda x: os.path.basename(x[0]).lower()):
            all_files_sorted.append((file_path, file_data, "Example"))
            
        for file_path, file_data in sorted(other_files.items(), key=lambda x: os.path.basename(x[0]).lower()):
            all_files_sorted.append((file_path, file_data, "Other"))
        
        # Generate summary table rows
        for i, (file_path, file_data, file_type) in enumerate(all_files_sorted, 1):
            file_name = os.path.basename(file_path)
            
            # Get description based on file type
            if file_type == "Main API Definition" and 'api_info' in file_data:
                description = file_data['api_info'].get('title', 'Unknown API')
            elif 'error' in file_data:
                description = f"Error parsing file: {file_data['error'][:50]}..."
            elif file_type == "Library":
                library_name = file_name.replace('.raml', '').replace('Library', '') 
                description = f"Library for {library_name} functionality"
            elif file_type == "Type Definition":
                type_name = file_name.replace('.raml', '').replace('Type', '')
                description = f"Type definition for {type_name}"
            elif file_type == "Example":
                example_name = file_name.replace('.raml', '').replace('Example', '')
                description = f"Example for {example_name}"
            else:
                description = "RAML component"
            
            doc += f"| {i} | {file_name} | {file_type} | {description} |\n"
        
        doc += "\n"
        
        # Document main API definition files first
        if main_api_files:
            doc += "### Main API Definitions\n\n"
            
            for file_path, file_data in sorted(main_api_files.items(), key=lambda x: os.path.basename(x[0]).lower()):
                file_name = os.path.basename(file_path)
                doc += f"#### {file_name}\n\n"
                
                # Add metadata about the API
                doc += f"**Path:** `{file_path}`\n\n"
                
                if 'raml_version' in file_data:
                    doc += f"**RAML Version:** {file_data['raml_version']}\n\n"
                
                if 'api_info' in file_data and isinstance(file_data['api_info'], dict):
                    api_info = file_data['api_info']
                    
                    doc += f"**API Title:** {api_info.get('title', 'Unknown')}\n\n"
                    doc += f"**Version:** {api_info.get('version', 'Unknown')}\n\n"
                    
                    if api_info.get('base_uri'):
                        doc += f"**Base URI:** `{api_info['base_uri']}`\n\n"
                    
                    if api_info.get('protocols'):
                        doc += f"**Protocols:** {', '.join(api_info['protocols'])}\n\n"
                    
                    if api_info.get('media_type'):
                        doc += f"**Media Type:** {api_info['media_type']}\n\n"
                    
                    # Document endpoints
                    if 'endpoints' in api_info and api_info['endpoints']:
                        doc += "**Endpoints:**\n\n"
                        
                        for endpoint in api_info['endpoints']:
                            doc += f"- `{endpoint['path']}`\n"
                            
                            if 'methods' in endpoint and endpoint['methods']:
                                for method in endpoint['methods']:
                                    doc += f"  - **{method.get('method', 'Unknown')}**"
                                    
                                    if method.get('description'):
                                        doc += f": {method['description']}"
                                    
                                    doc += "\n"
                                    
                                    if 'responses' in method:
                                        doc += f"    - Responses: {', '.join(method['responses'])}\n"
                        
                        doc += "\n"
                
                doc += "---\n\n"
        
        # Document libraries
        if library_files:
            doc += "### RAML Libraries\n\n"
            doc += "Libraries contain reusable components that are imported by other RAML files.\n\n"
            
            for file_path, file_data in sorted(library_files.items(), key=lambda x: os.path.basename(x[0]).lower()):
                file_name = os.path.basename(file_path)
                doc += f"#### {file_name}\n\n"
                doc += f"**Path:** `{file_path}`\n\n"
                
                # Add raw content for libraries (limited length)
                if 'raw_content' in file_data and file_data['raw_content']:
                    content = file_data['raw_content']
                    if len(content) > 500:  # Shorter excerpt for libraries
                        content = content[:500] + "\n\n... (content truncated) ..."
                    
                    doc += "**Content:**\n\n```yaml\n"
                    doc += content
                    doc += "\n```\n\n"
                
                doc += "---\n\n"
        
        # Document type definitions
        if type_files:
            doc += "### RAML Type Definitions\n\n"
            doc += "Type definitions describe the structure of data used in the API.\n\n"
            
            for file_path, file_data in sorted(type_files.items(), key=lambda x: os.path.basename(x[0]).lower()):
                file_name = os.path.basename(file_path)
                doc += f"#### {file_name}\n\n"
                doc += f"**Path:** `{file_path}`\n\n"
                
                # Add raw content for type definitions (limited length)
                if 'raw_content' in file_data and file_data['raw_content']:
                    content = file_data['raw_content']
                    if len(content) > 500:  # Shorter excerpt for type definitions
                        content = content[:500] + "\n\n... (content truncated) ..."
                    
                    doc += "**Content:**\n\n```yaml\n"
                    doc += content
                    doc += "\n```\n\n"
                
                doc += "---\n\n"
        
        # Add a note about other RAML files
        other_count = len(example_files) + len(other_files)
        if other_count > 0:
            doc += "### Additional RAML Files\n\n"
            doc += f"The project includes {other_count} additional RAML files with examples, traits, and other components.\n"
            doc += "These files are referenced by the main API definition and provide supporting functionality.\n\n"
        
        return doc
    
    def _generate_yaml_documentation(self, yaml_files: Dict) -> str:
        """Generate documentation for YAML configuration files."""
        if not yaml_files:
            return ""
        
        doc = "## YAML Configurations\n\n"
        doc += f"The application includes {len(yaml_files)} YAML configuration files.\n\n"
        
        # Add summary table of all YAML files
        doc += "| # | File Name | Type | Key Elements | Size |\n"
        doc += "|---|-----------|------|--------------|------|\n"
        
        # Sort files by name for consistent output
        sorted_files = sorted(yaml_files.items(), key=lambda x: os.path.basename(x[0]).lower())
        for i, (file_path, file_data) in enumerate(sorted_files, 1):
            file_name = os.path.basename(file_path)
            file_type = "Configuration" if file_data.get('is_config', False) else "Data File"
            elements = ", ".join(file_data.get('top_level_keys', []))[:30] + ("..." if len(", ".join(file_data.get('top_level_keys', []))) > 30 else "")
            size = f"{file_data.get('size', 0) / 1024:.1f} KB"
            
            doc += f"| {i} | {file_name} | {file_type} | {elements} | {size} |\n"
        
        doc += "\n### Individual YAML Files\n\n"
        
        # Sort files by name for consistent output
        for file_path, file_data in sorted_files:
            doc += f"#### {os.path.basename(file_path)}\n\n"
            
            # Add metadata about the configuration
            doc += f"**Path:** `{file_path}`\n\n"
            
            if 'is_config' in file_data:
                doc += f"**Configuration File:** {'Yes' if file_data['is_config'] else 'No'}\n\n"
            
            if 'top_level_keys' in file_data and file_data['top_level_keys']:
                doc += f"**Top-Level Elements:** {', '.join(file_data['top_level_keys'])}\n\n"
            
            # Add content with syntax highlighting
            if 'raw_content' in file_data and file_data['raw_content'] and not isinstance(file_data['raw_content'], dict):
                # Limit content length to prevent extremely large files
                content = file_data['raw_content']
                if len(content) > 2000:
                    content = content[:2000] + "\n\n... (content truncated) ..."
                
                doc += "**Content:**\n\n```yaml\n"
                doc += content
                doc += "\n```\n\n"
            
            doc += "---\n\n"
        
        return doc
    
    def _generate_properties_documentation(self, properties_files: Dict) -> str:
        """Generate documentation for properties files."""
        if not properties_files:
            return ""
        
        doc = "## Properties Files\n\n"
        doc += f"The application includes {len(properties_files)} properties files for configuration.\n\n"
        
        # Add summary table of all properties files
        doc += "| # | File Name | Property Count | Size |\n"
        doc += "|---|-----------|---------------|------|\n"
        
        # Sort files by name for consistent output
        sorted_files = sorted(properties_files.items(), key=lambda x: os.path.basename(x[0]).lower())
        for i, (file_path, file_data) in enumerate(sorted_files, 1):
            file_name = os.path.basename(file_path)
            property_count = file_data.get('property_count', 0)
            size = f"{file_data.get('size', 0) / 1024:.1f} KB"
            
            doc += f"| {i} | {file_name} | {property_count} | {size} |\n"
        
        doc += "\n### Individual Properties Files\n\n"
        
        # Sort files by name for consistent output
        for file_path, file_data in sorted_files:
            doc += f"#### {os.path.basename(file_path)}\n\n"
            
            # Add metadata
            doc += f"**Path:** `{file_path}`\n\n"
            
            if 'property_count' in file_data:
                doc += f"**Properties Count:** {file_data['property_count']}\n\n"
            
            # Add properties table
            if 'properties' in file_data and file_data['properties']:
                doc += "**Properties:**\n\n"
                doc += "| Property Key | Value |\n"
                doc += "|-------------|-------|\n"
                
                for key, value in file_data['properties'].items():
                    # Mask sensitive values
                    if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                        value = '******** (masked for security)'
                    
                    # Limit value length for display
                    if len(value) > 50:
                        value = value[:50] + "..."
                    
                    doc += f"| `{key}` | `{value}` |\n"
                
                doc += "\n"
            
            doc += "---\n\n"
        
        return doc
    
    def _generate_json_documentation(self, json_files: Dict) -> str:
        """Generate documentation for JSON files."""
        if not json_files:
            return ""
        
        doc = "## JSON Files\n\n"
        doc += f"The application includes {len(json_files)} JSON files.\n\n"
        
        # Add summary table of all JSON files
        doc += "| # | File Name | Type | Details | Size |\n"
        doc += "|---|-----------|------|---------|------|\n"
        
        # Sort files by name for consistent output
        sorted_files = sorted(json_files.items(), key=lambda x: os.path.basename(x[0]).lower())
        for i, (file_path, file_data) in enumerate(sorted_files, 1):
            file_name = os.path.basename(file_path)
            file_type = file_data.get('file_type', 'Unknown')
            details = ", ".join(file_data.get('type_hints', []))[:30] + ("..." if len(", ".join(file_data.get('type_hints', []))) > 30 else "")
            size = f"{file_data.get('size', 0) / 1024:.1f} KB"
            
            doc += f"| {i} | {file_name} | {file_type} | {details} | {size} |\n"
        
        doc += "\n### Individual JSON Files\n\n"
        
        # Sort files by name for consistent output
        for file_path, file_data in sorted_files:
            doc += f"#### {os.path.basename(file_path)}\n\n"
            
            # Add metadata
            doc += f"**Path:** `{file_path}`\n\n"
            
            if 'file_type' in file_data and file_data['file_type'] != "Unknown":
                doc += f"**Type:** {file_data['file_type']}\n\n"
            
            if 'type_hints' in file_data and file_data['type_hints']:
                doc += f"**Details:** {', '.join(file_data['type_hints'])}\n\n"
            
            # Add content with syntax highlighting (limited length)
            if 'raw_content' in file_data and file_data['raw_content'] and not isinstance(file_data['raw_content'], dict):
                # Limit content length to prevent extremely large files
                content = file_data['raw_content']
                if len(content) > 2000:
                    content = content[:2000] + "\n\n... (content truncated) ..."
                
                doc += "**Content:**\n\n```json\n"
                doc += content
                doc += "\n```\n\n"
            
            doc += "---\n\n"
        
        return doc

# Helper function to process all files in a directory
def generate_enhanced_documentation(mule_dir: str, include_additional_files: bool = True) -> str:
    """
    Process all files in a directory and generate enhanced documentation.
    
    Args:
        mule_dir: Directory containing MuleSoft XML files
        include_additional_files: Whether to include additional file types
        
    Returns:
        Markdown documentation as a string
    """
    try:
        # Parse Mule XML files
        mule_parser = MuleFlowParser()
        parsed_data = mule_parser.parse_mule_files(mule_dir)
        
        # Parse additional files if requested
        additional_files = None
        if include_additional_files:
            additional_parser = AdditionalFileParser()
            additional_files = additional_parser.parse_directory(mule_dir)
        
        # Generate documentation
        doc_generator = EnhancedDocumentationGenerator()
        return doc_generator.generate_documentation(parsed_data, additional_files, mule_dir)
        
    except Exception as e:
        logging.error(f"Error generating enhanced documentation: {str(e)}")
        return f"# Error Generating Documentation\n\nAn error occurred: {str(e)}\n"

if __name__ == "__main__":
    # Test documentation generation if run directly
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        print(f"Generating documentation for: {directory}")
        
        documentation = generate_enhanced_documentation(directory)
        
        output_file = "enhanced_documentation.md"
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(documentation)
            
        print(f"Documentation saved to: {output_file}") 

