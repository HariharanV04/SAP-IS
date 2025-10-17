import os
import sys
import json
import logging
import yaml
import re
from typing import Dict, List, Optional, Union, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdditionalFileParser:
    """
    Parser for additional file types like DataWeave (DWL), YAML, and RAML.
    Extracts relevant information from these files for documentation purposes.
    """
    
    def __init__(self):
        """Initialize the additional file parser."""
        self.supported_extensions = ['.dwl', '.yaml', '.yml', '.raml', '.properties', '.json']
    
    def parse_directory(self, directory: str) -> Dict:
        """
        Parse all supported files in the specified directory and its subdirectories.
        
        Args:
            directory: Path to the directory to parse
            
        Returns:
            Dictionary with parsed file information by type
        """
        result = {
            'dwl_files': {},
            'yaml_files': {},
            'raml_files': {},
            'properties_files': {},
            'json_files': {}
        }
        
        logger.info(f"Parsing additional files in {directory}")
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                if ext in self.supported_extensions:
                    try:
                        if ext == '.dwl':
                            result['dwl_files'][file_path] = self._parse_dwl_file(file_path)
                        elif ext in ['.yaml', '.yml']:
                            result['yaml_files'][file_path] = self._parse_yaml_file(file_path)
                        elif ext == '.raml':
                            result['raml_files'][file_path] = self._parse_raml_file(file_path)
                        elif ext == '.properties':
                            result['properties_files'][file_path] = self._parse_properties_file(file_path)
                        elif ext == '.json':
                            result['json_files'][file_path] = self._parse_json_file(file_path)
                    except Exception as e:
                        logger.error(f"Error parsing {file_path}: {str(e)}")
                        # Still include the file with error information
                        if ext == '.dwl':
                            result['dwl_files'][file_path] = {'error': str(e), 'size': os.path.getsize(file_path)}
                        elif ext in ['.yaml', '.yml']:
                            result['yaml_files'][file_path] = {'error': str(e), 'size': os.path.getsize(file_path)}
                        elif ext == '.raml':
                            result['raml_files'][file_path] = {'error': str(e), 'size': os.path.getsize(file_path)}
                        elif ext == '.properties':
                            result['properties_files'][file_path] = {'error': str(e), 'size': os.path.getsize(file_path)}
                        elif ext == '.json':
                            result['json_files'][file_path] = {'error': str(e), 'size': os.path.getsize(file_path)}
        
        # Log summary
        logger.info(f"Found {len(result['dwl_files'])} DataWeave files")
        logger.info(f"Found {len(result['yaml_files'])} YAML files")
        logger.info(f"Found {len(result['raml_files'])} RAML files")
        logger.info(f"Found {len(result['properties_files'])} Properties files")
        logger.info(f"Found {len(result['json_files'])} JSON files")
        
        return result
    
    def _parse_dwl_file(self, file_path: str) -> Dict:
        """
        Parse a DataWeave (DWL) file and extract relevant information.
        
        Args:
            file_path: Path to the DWL file
            
        Returns:
            Dictionary with parsed information
        """
        result = {'size': os.path.getsize(file_path)}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            result['content'] = content
            
            # Detect DataWeave version
            version_match = re.search(r'%dw\s+(\d+\.\d+)', content)
            if version_match:
                result['dw_version'] = version_match.group(1)
            else:
                result['dw_version'] = "Unknown"
            
            # Extract type hints
            type_hints = []
            if "input" in content or "payload" in content:
                type_hints.append("Transformation")
            if "fun" in content or "function" in content:
                type_hints.append("Function Library")
            if "var" in content and "=" in content:
                type_hints.append("Variables")
            if "///" in content:
                type_hints.append("Documented")
            result['type_hints'] = type_hints
            
            # Extract functions
            functions = re.findall(r'fun\s+([a-zA-Z0-9_]+)\s*\(', content)
            result['functions'] = functions
            
            # Extract variables
            variables = re.findall(r'var\s+([a-zA-Z0-9_]+)\s*=', content)
            result['variables'] = variables
        
        return result
    
    def _parse_yaml_file(self, file_path: str) -> Dict:
        """
        Parse a YAML file and extract relevant information.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Dictionary with parsed information
        """
        result = {'size': os.path.getsize(file_path)}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            result['raw_content'] = content
            
            try:
                yaml_data = yaml.safe_load(content)
                if isinstance(yaml_data, dict):
                    result['top_level_keys'] = list(yaml_data.keys())
                    
                    # Determine if it's a configuration file
                    is_config = False
                    for key in yaml_data.keys():
                        if key in ['apis', 'apiVersion', 'server', 'config', 'configuration', 'settings']:
                            is_config = True
                            break
                    result['is_config'] = is_config
                    
                    # Extract more detailed information based on content patterns
                    if 'api' in result['top_level_keys'] or 'apis' in result['top_level_keys']:
                        result['type_hints'] = ['API Configuration']
                    elif 'server' in result['top_level_keys'] or 'services' in result['top_level_keys']:
                        result['type_hints'] = ['Server Configuration']
                    else:
                        result['type_hints'] = ['Configuration' if is_config else 'Data File']
                
                elif isinstance(yaml_data, list):
                    result['is_config'] = False
                    result['type_hints'] = ['Data Array']
                    result['array_length'] = len(yaml_data)
                    result['top_level_keys'] = []
            except Exception as e:
                logger.warning(f"Error parsing YAML content in {file_path}: {str(e)}")
                result['error'] = str(e)
        
        return result
    
    def _parse_raml_file(self, file_path: str) -> Dict:
        """
        Parse a RAML file and extract relevant information.
        
        Args:
            file_path: Path to the RAML file
            
        Returns:
            Dictionary with parsed information
        """
        result = {'size': os.path.getsize(file_path)}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            result['raw_content'] = content
            
            # Basic RAML version detection
            version_match = re.match(r'#%RAML\s+(\S+)', content)
            if version_match:
                result['raml_version'] = version_match.group(1)
            
            # Check if it's a library
            is_library = 'uses:' in content or re.search(r'#%RAML.+Library', content) is not None
            result['is_library'] = is_library
            
            # More detailed parsing for main API files
            try:
                # We'll attempt to parse the RAML content as YAML, which is the underlying format
                yaml_content = yaml.safe_load(content)
                
                if isinstance(yaml_content, dict):
                    api_info = {}
                    
                    # Extract basic API info
                    if 'title' in yaml_content:
                        api_info['title'] = yaml_content.get('title', 'Unnamed API')
                    
                    if 'version' in yaml_content:
                        api_info['version'] = yaml_content.get('version', 'Unknown')
                    
                    if 'baseUri' in yaml_content:
                        api_info['base_uri'] = yaml_content.get('baseUri')
                    
                    if 'protocols' in yaml_content:
                        api_info['protocols'] = yaml_content.get('protocols', [])
                    
                    if 'mediaType' in yaml_content:
                        api_info['media_type'] = yaml_content.get('mediaType')
                    
                    # Extract endpoints (resources)
                    endpoints = []
                    for key, value in yaml_content.items():
                        if key.startswith('/'):
                            endpoint = {'path': key, 'methods': []}
                            
                            if isinstance(value, dict):
                                # Extract HTTP methods
                                for method_key, method_value in value.items():
                                    if method_key in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                                        method_info = {
                                            'method': method_key.upper(),
                                            'responses': []
                                        }
                                        
                                        if isinstance(method_value, dict):
                                            if 'description' in method_value:
                                                method_info['description'] = method_value.get('description')
                                            
                                            # Extract responses
                                            if 'responses' in method_value and isinstance(method_value['responses'], dict):
                                                method_info['responses'] = list(method_value['responses'].keys())
                                        
                                        endpoint['methods'].append(method_info)
                            
                            endpoints.append(endpoint)
                    
                    if endpoints:
                        api_info['endpoints'] = endpoints
                    
                    result['api_info'] = api_info
                
                # Determine the RAML file type
                if is_library:
                    result['raml_type'] = 'Library'
                elif 'resourceTypes' in yaml_content:
                    result['raml_type'] = 'Resource Type'
                elif 'traits' in yaml_content:
                    result['raml_type'] = 'Trait'
                elif 'types' in yaml_content:
                    result['raml_type'] = 'Data Type'
                elif re.search(r'Example', os.path.basename(file_path)) is not None:
                    result['raml_type'] = 'Example'
                elif api_info.get('endpoints'):
                    result['raml_type'] = 'API Definition'
                else:
                    result['raml_type'] = 'Other'
                
            except Exception as e:
                logger.warning(f"Error parsing RAML content as YAML in {file_path}: {str(e)}")
                result['error'] = str(e)
        
        return result
    
    def _parse_properties_file(self, file_path: str) -> Dict:
        """
        Parse a properties file and extract key-value pairs.
        
        Args:
            file_path: Path to the properties file
            
        Returns:
            Dictionary with parsed information
        """
        result = {'size': os.path.getsize(file_path)}
        properties = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#') or line.startswith('!'):
                    continue
                
                # Split at the first '=' or ':'
                if '=' in line:
                    key, value = line.split('=', 1)
                elif ':' in line:
                    key, value = line.split(':', 1)
                else:
                    continue
                
                key = key.strip()
                value = value.strip()
                properties[key] = value
        
        result['properties'] = properties
        result['property_count'] = len(properties)
        
        return result
    
    def _parse_json_file(self, file_path: str) -> Dict:
        """
        Parse a JSON file and extract relevant information.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary with parsed information
        """
        result = {'size': os.path.getsize(file_path)}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            result['raw_content'] = content
            
            try:
                json_data = json.loads(content)
                
                # Determine the type of JSON file
                if isinstance(json_data, dict):
                    # Extract top-level keys
                    result['top_level_keys'] = list(json_data.keys())
                    
                    # Look for specific patterns to identify the JSON type
                    type_hints = []
                    
                    if 'swagger' in json_data or 'openapi' in json_data:
                        file_type = 'OpenAPI/Swagger Definition'
                        type_hints.append(f"API Version: {json_data.get('swagger', json_data.get('openapi', 'Unknown'))}")
                    elif 'info' in json_data and 'paths' in json_data:
                        file_type = 'API Definition'
                    elif 'api' in json_data or 'apis' in json_data:
                        file_type = 'API Configuration'
                    elif 'config' in json_data or 'configuration' in json_data:
                        file_type = 'Configuration'
                    elif 'schema' in json_data or '$schema' in json_data:
                        file_type = 'JSON Schema'
                    elif 'data' in json_data:
                        file_type = 'Data Container'
                    else:
                        file_type = 'General JSON'
                    
                    # Add some statistics
                    if isinstance(json_data, dict):
                        type_hints.append(f"Keys: {len(json_data)}")
                    
                    result['file_type'] = file_type
                    result['type_hints'] = type_hints
                
                elif isinstance(json_data, list):
                    # For arrays, check the contents
                    file_type = 'Data Array'
                    type_hints = [f"Items: {len(json_data)}"]
                    
                    if len(json_data) > 0:
                        if isinstance(json_data[0], dict):
                            type_hints.append(f"Object Array")
                            # Sample some keys from the first object
                            if len(json_data[0]) > 0:
                                sample_keys = list(json_data[0].keys())[:3]
                                type_hints.append(f"Sample keys: {', '.join(sample_keys)}")
                        else:
                            type_hints.append(f"Primitive Array")
                    
                    result['file_type'] = file_type
                    result['type_hints'] = type_hints
                
                else:
                    result['file_type'] = 'Unknown'
                    result['type_hints'] = []
            
            except Exception as e:
                logger.warning(f"Error parsing JSON content in {file_path}: {str(e)}")
                result['error'] = str(e)
                result['file_type'] = 'Invalid JSON'
        
        return result


# Test the parser if run directly
if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        parser = AdditionalFileParser()
        results = parser.parse_directory(directory)
        
        # Output summary
        print(f"Found {len(results['dwl_files'])} DataWeave files")
        print(f"Found {len(results['yaml_files'])} YAML files")
        print(f"Found {len(results['raml_files'])} RAML files")
        print(f"Found {len(results['properties_files'])} Properties files")
        print(f"Found {len(results['json_files'])} JSON files")
        
        # Output detailed results for each file type
        if len(results['raml_files']) > 0:
            print("\nRAML Files:")
            for file_path, data in results['raml_files'].items():
                print(f"  - {os.path.basename(file_path)}")
                if 'api_info' in data and 'title' in data['api_info']:
                    print(f"    Title: {data['api_info']['title']}")
                if 'raml_type' in data:
                    print(f"    Type: {data['raml_type']}")
                if 'error' in data:
                    print(f"    Error: {data['error']}")
        
        if len(results['dwl_files']) > 0:
            print("\nDataWeave Files:")
            for file_path, data in results['dwl_files'].items():
                print(f"  - {os.path.basename(file_path)}")
                if 'dw_version' in data:
                    print(f"    Version: {data['dw_version']}")
                if 'type_hints' in data:
                    print(f"    Type: {', '.join(data['type_hints'])}")
                if 'error' in data:
                    print(f"    Error: {data['error']}") 
