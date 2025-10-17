import os
import sys
import xml.etree.ElementTree as ET
import json
from typing import Dict, List, Optional
from pathlib import Path
import markdown
import logging
import argparse

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # First try to load from the local directory
    local_env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(local_env_path):
        load_dotenv(local_env_path)
        print(f"Loaded environment variables from: {local_env_path}")
    else:
        # Try to load from parent directory
        parent_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(parent_env_path):
            load_dotenv(parent_env_path)
            print(f"Loaded environment variables from: {parent_env_path}")
except ImportError:
    print("dotenv package not installed. Run 'pip install python-dotenv' to enable .env file loading.")
    pass

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import local documentation enhancer instead of the one from src/llm
from documentation_enhancer import DocumentationEnhancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mule_flow_parser.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class MuleFlowParser:
    def __init__(self):
        self.namespaces = {
            'mule': 'http://www.mulesoft.org/schema/mule/core',
            'doc': 'http://www.mulesoft.org/schema/mule/documentation',
            'http': 'http://www.mulesoft.org/schema/mule/http',
            'apikit': 'http://www.mulesoft.org/schema/mule/mule-apikit',
            'ee': 'http://www.mulesoft.org/schema/mule/ee/core'
        }
        
        self.component_colors = {
            'http:listener': '#4CAF50',
            'http:request': '#4CAF50',
            'ee:transform': '#9C27B0',
            'flow-ref': '#2196F3',
            'error-handler': '#F44336',
            'logger': '#FF9800',
            'try': '#03A9F4',
            'choice': '#673AB7',
            'foreach': '#795548',
            'set-variable': '#607D8B'
        }

    def safe_parse_xml(self, file_path: str) -> Optional[ET.ElementTree]:
        """Safely parse XML file with error handling."""
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove any invalid characters
            content = ''.join(char for char in content if ord(char) < 128)
            
            # Parse the cleaned content
            return ET.ElementTree(ET.fromstring(content))
        except ET.ParseError as e:
            logging.error(f"XML parsing error in {file_path}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            return None

    def parse_mule_files(self, directory: str) -> Dict:
        """Parse all MuleSoft XML files in the given directory."""
        flows = {}
        subflows = {}  # Initialize subflows here
        configs = {}
        error_handlers = {}
        
        logging.info(f"Starting to parse MuleSoft files in: {directory}")
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    logging.info(f"Processing file: {file_path}")
                    
                    tree = self.safe_parse_xml(file_path)
                    if tree is None:
                        continue
                        
                    root_elem = tree.getroot()
                    
                    try:
                        # Parse flows
                        for flow in root_elem.findall('.//mule:flow', self.namespaces):
                            flow_name = flow.get('name')
                            if flow_name:
                                flows[flow_name] = self.parse_flow(flow)
                                logging.info(f"Parsed flow: {flow_name}")
                        
                        # Parse subflows
                        for subflow in root_elem.findall('.//mule:sub-flow', self.namespaces):
                            subflow_name = subflow.get('name')
                            if subflow_name:
                                subflows[subflow_name] = self.parse_flow(subflow)
                                logging.info(f"Parsed subflow: {subflow_name}")
                        
                        # Parse configurations
                        for config in root_elem.findall('.//*[@name]'):
                            if 'config' in config.tag.lower():
                                config_name = config.get('name')
                                if config_name:
                                    configs[config_name] = self.parse_config(config)
                                    logging.info(f"Parsed config: {config_name}")
                        
                        # Parse error handlers
                        for error in root_elem.findall('.//mule:error-handler', self.namespaces):
                            error_name = error.get('name', 'default-error-handler')
                            error_handlers[error_name] = self.parse_error_handler(error)
                            logging.info(f"Parsed error handler: {error_name}")
                            
                    except Exception as e:
                        logging.error(f"Error parsing elements in {file_path}: {str(e)}")
                        continue
        
        # Return combined results after processing all files
        return {
            'flows': flows,
            'subflows': subflows,
            'configs': configs,
            'error_handlers': error_handlers
        }

    def parse_flow(self, flow_elem: ET.Element) -> Dict:
        """Parse a single flow element with more detailed content extraction."""
        components = []
        try:
            for child in flow_elem.iter():
                if '}' in child.tag:
                    component_type = child.tag.split('}')[1]
                    
                    # Get only the name attribute without documentation namespace
                    component_name = child.get('name', '')
                    
                    component = {
                        'type': component_type,
                        'name': component_name,
                        'config_ref': child.get('config-ref', ''),
                        'color': self.get_component_color(component_type),
                        'attributes': self.get_component_attributes(child),
                        'content': self.extract_component_content(child)  # Add content extraction
                    }
                    components.append(component)
        except Exception as e:
            logging.error(f"Error parsing flow components: {str(e)}")
        
        return {
            'name': flow_elem.get('name'),
            'components': components
        }

    def extract_component_content(self, component: ET.Element) -> Dict:
        """
        Simplified component content extractor focused on reliably extracting OData expressions.
        This avoids complex XPath and focuses on direct text extraction.
        """
        content = {}
        
        try:
            component_tag = component.tag
            component_type = component_tag.split('}')[1] if '}' in component_tag else component_tag
            
            # Verbose debug for HTTP request components
            if component_type == 'request':
                logging.info(f"Found HTTP request component: {component_type}")
                logging.info(f"Component attributes: {component.attrib}")
                
                # Debug all child elements
                for child in component:
                    child_tag = child.tag.split('}')[1] if '}' in child.tag else child.tag
                    logging.info(f"Child element: {child_tag}")
                    
                    # Look for query-params in any child element
                    if 'query-params' in child.tag:
                        logging.info(f"Found query-params element")
                        if child.text:
                            logging.info(f"Query params text: {child.text[:100]}...")
                            if child.text.strip():
                                query_text = child.text.strip()
                                # normalize any "\$" → "$" so our regexes see the real OData keys
                                query_text = query_text.replace(r'\$', '$')
                                content['query_params'] = query_text

                                
                                # Log the content for debugging
                                logging.info(f"Looking for OData patterns in: {query_text[:100]}...")
                                
                                # Extract OData parameters using regex
                                try:
                                    import re
                                    
                                    # Log dollar sign presence
                                    if '$' in query_text or '\\$' in query_text:
                                        logging.info(f"Found $ symbol in query text, checking for OData params")
                                    else:
                                        logging.info("No $ symbol found in query text, OData parameters unlikely")
                                    
                                    # Try multiple patterns for $filter
                                    if '\\$filter' in query_text or '$filter' in query_text:
                                        logging.info(f"Found filter keyword in query text")
                                        
                                        # Try these patterns in sequence
                                        filter_patterns = [
                                            r'\$filter[^:]*:[^"\']*["\'](.*?)["\'"](?:,|})',  # Standard JSON pattern
                                            r'\$filter[^:]*:[^"\']*["\'](.*?)(?:["\'"](?:,|})|(?:,|})|$)', # Alternative with possible unclosed quotes
                                            r'[\\\$]filter["\']?\s*:\s*["\']([^"\']+)["\']', # Original pattern
                                            r'\$filter\s*=\s*([^&]+)',  # URL parameter style
                                            r'\$filter\s*:\s*([^,}]+)'  # Simple colon separator
                                        ]
                                        
                                        filter_found = False
                                        for i, pattern in enumerate(filter_patterns):
                                            try:
                                                filter_match = re.search(pattern, query_text, re.DOTALL)
                                                if filter_match:
                                                    filter_found = True
                                                    content['odata_filter'] = filter_match.group(1).strip()
                                                    logging.info(f"Extracted filter with pattern {i+1}: {content['odata_filter']}")
                                                    break
                                            except Exception as e:
                                                logging.error(f"Error with filter pattern {i+1}: {e}")
                                        
                                        if not filter_found:
                                            logging.info("Could not extract filter with any pattern")
                                    
                                    # Try multiple patterns for $select
                                    if '\\$select' in query_text or '$select' in query_text:
                                        logging.info(f"Found select keyword in query text")
                                        
                                        # Try these patterns in sequence
                                        select_patterns = [
                                            r'\$select[^:]*:[^"\']*["\'](.*?)["\'"](?:,|})',  # Standard JSON pattern
                                            r'\$select[^:]*:[^"\']*["\'](.*?)(?:["\'"](?:,|})|(?:,|})|$)', # Alternative with possible unclosed quotes
                                            r'[\\\$]select["\']?\s*:\s*["\']([^"\']+)["\']', # Original pattern
                                            r'\$select\s*=\s*([^&]+)',  # URL parameter style
                                            r'\$select\s*:\s*([^,}]+)'  # Simple colon separator
                                        ]
                                        
                                        select_found = False
                                        for i, pattern in enumerate(select_patterns):
                                            try:
                                                select_match = re.search(pattern, query_text, re.DOTALL)
                                                if select_match:
                                                    select_found = True
                                                    content['odata_select'] = select_match.group(1).strip()
                                                    logging.info(f"Extracted select with pattern {i+1}: {content['odata_select']}")
                                                    break
                                            except Exception as e:
                                                logging.error(f"Error with select pattern {i+1}: {e}")
                                        
                                        if not select_found:
                                            logging.info("Could not extract select with any pattern")
                                    
                                    # Combine OData parameters if found
                                    odata_params = {}
                                    if 'odata_filter' in content:
                                        odata_params['$filter'] = content['odata_filter']
                                    if 'odata_select' in content:
                                        odata_params['$select'] = content['odata_select']
                                    
                                    if odata_params:
                                        content['odata_params'] = odata_params
                                        logging.info(f"Final OData params: {odata_params}")
                                
                                except Exception as e:
                                    logging.error(f"Error processing OData parameters: {e}")
                        else:
                            logging.info("Query-params element has no text content")
            
            # Handle DataWeave transformations
            if component_type == 'transform':
                # Extract set-payload content
                for elem in component.iter():
                    if elem.tag.endswith('set-payload') and elem.text:
                        content['set_payload'] = elem.text.strip()
                    
                    # Extract variable assignments
                    if elem.tag.endswith('set-variable') and 'variableName' in elem.attrib and elem.text:
                        var_name = elem.attrib['variableName']
                        content[f'variable_{var_name}'] = elem.text.strip()
            
            # Handle logger messages
            if component_type == 'logger' and 'message' in component.attrib:
                content['message'] = component.attrib['message']
            
            # Handle flow references
            if component_type == 'flow-ref' and 'name' in component.attrib:
                content['target_flow'] = component.attrib['name']
            
            # Handle choice conditions
            if component_type == 'choice':
                conditions = []
                for elem in component.iter():
                    if elem.tag.endswith('when') and 'expression' in elem.attrib:
                        conditions.append(elem.attrib['expression'])
                
                if conditions:
                    content['conditions'] = conditions
        
        except Exception as e:
            logging.error(f"Error extracting component content: {e}")
        
        return content

    def parse_config(self, config_elem: ET.Element) -> Dict:
        """Parse a configuration element."""
        try:
            return {
                'type': config_elem.tag.split('}')[1] if '}' in config_elem.tag else config_elem.tag,
                'name': config_elem.get('name', ''),
                'attributes': self.get_component_attributes(config_elem)
            }
        except Exception as e:
            logging.error(f"Error parsing config: {str(e)}")
            return {'type': 'unknown', 'attributes': {}}

    def parse_error_handler(self, error_elem: ET.Element) -> Dict:
        """Parse an error handler element."""
        handlers = []
        try:
            for handler in error_elem:
                if '}' in handler.tag:
                    handler_type = handler.tag.split('}')[1]
                    handlers.append({
                        'type': handler_type,
                        'when': handler.get('when', ''),
                        'type_to_match': handler.get('type', '')
                    })
        except Exception as e:
            logging.error(f"Error parsing error handler: {str(e)}")
        return {'handlers': handlers}

    def get_component_attributes(self, elem: ET.Element) -> Dict:
        """Get all attributes of a component."""
        try:
            # Filter out documentation namespace attributes
            return {k: v for k, v in elem.attrib.items() 
                   if not k.startswith('{http://www.mulesoft.org/schema/mule/documentation}')}
        except Exception as e:
            logging.error(f"Error getting component attributes: {str(e)}")
            return {}

    def get_component_color(self, component_type: str) -> str:
        """Get the color for a component type."""
        for key, color in self.component_colors.items():
            if key in component_type.lower():
                return color
        return '#9E9E9E'  # Default color

class HTMLGenerator:
    def __init__(self):
        self.css = """
        :root {
            --component-http: #4CAF50;
            --component-transform: #9C27B0;
            --component-flow: #2196F3;
            --component-error: #F44336;
            --component-logger: #FF9800;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            display: flex;
            gap: 20px;
        }
        .sidebar {
            width: 300px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: fixed;
            height: calc(100vh - 40px);
            overflow-y: auto;
        }
        .main-content {
            margin-left: 320px;
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .flow {
            margin-bottom: 30px;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        .component {
            margin: 10px 0;
            padding: 10px;
            border-radius: 4px;
            color: white;
            position: relative;
        }
        .component::before {
            content: "↓";
            position: absolute;
            left: -20px;
            color: #666;
        }
        .component:first-child::before {
            display: none;
        }
        .component-details {
            font-size: 0.9em;
            margin-top: 5px;
        }
        """

    def generate_component_details(self, component: Dict) -> str:
        """Generate HTML for component details."""
        details = []
        if component['name']:
            details.append(f"name: {component['name']}")
        if component['config_ref']:
            details.append(f"config-ref: {component['config_ref']}")
        
        # Add other non-documentation attributes
        for key, value in component['attributes'].items():
            if key not in ['name', 'config-ref']:
                details.append(f"{key}: {value}")
                
        return "<br>".join(details)

    def generate_flows_html(self, flows: Dict) -> str:
        """Generate HTML for flows section."""
        if not flows:
            return "<p>No flows found</p>"
            
        html = ""
        for flow_name, flow_data in flows.items():
            html += f"""
            <div class="flow">
                <h3>{flow_name}</h3>
                <div class="components">
            """
            
            for component in flow_data['components']:
                details = self.generate_component_details(component)
                html += f"""
                    <div class="component" style="background-color: {component['color']}">
                        <h4>{component['type']}</h4>
                        <div class="component-details">
                            {details}
                        </div>
                    </div>
                """
                
            html += """
                </div>
            </div>
            """
        return html

    def generate_configs_html(self, configs: Dict) -> str:
        """Generate HTML for configurations section."""
        if not configs:
            return "<p>No configurations found</p>"
            
        html = ""
        for config_name, config_data in configs.items():
            details = []
            details.append(f"name: {config_name}")
            
            # Add non-documentation attributes
            for key, value in config_data['attributes'].items():
                if key != 'name':
                    details.append(f"{key}: {value}")
                    
            html += f"""
            <div class="flow">
                <h3>{config_name}</h3>
                <div class="component-details">
                    {('<br>'.join(details))}
                </div>
            </div>
            """
        return html

    def generate_error_handlers_html(self, error_handlers: Dict) -> str:
        """Generate HTML for error handlers."""
        try:
            html = ""
            for handler_name, handler_data in error_handlers.items():
                html += f"""
                <div class="flow">
                    <h3>{handler_name}</h3>
                    <div class="component-details">
                        {self.format_handlers(handler_data['handlers'])}
                    </div>
                </div>
                """
            return html
        except Exception as e:
            logging.error(f"Error generating error handlers HTML: {str(e)}")
            return "<div>Error generating error handlers visualization</div>"

    def format_attributes(self, attributes: Dict) -> str:
        """Format component attributes."""
        try:
            return '<br>'.join(f"{k}: {v}" for k, v in attributes.items())
        except Exception as e:
            logging.error(f"Error formatting attributes: {str(e)}")
            return "Error formatting attributes"

    def format_handlers(self, handlers: List[Dict]) -> str:
        """Format error handlers."""
        try:
            return '<br>'.join(f"{h['type']} - {h['type_to_match']}" for h in handlers)
        except Exception as e:
            logging.error(f"Error formatting handlers: {str(e)}")
            return "Error formatting handlers"

    def generate_html(self, parsed_data: Dict) -> str:
        """Generate HTML visualization from parsed data."""
        try:
            flows_html = self.generate_flows_html(parsed_data['flows'])
            configs_html = self.generate_configs_html(parsed_data['configs'])
            error_handlers_html = self.generate_error_handlers_html(parsed_data['error_handlers'])
            
            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>MuleSoft Flow Visualization</title>
                <style>{self.css}</style>
            </head>
            <body>
                <div class="container">
                    <div class="sidebar">
                        <h2>Navigation</h2>
                        <ul>
                            <li><a href="#flows">Flows</a></li>
                            <li><a href="#configs">Configurations</a></li>
                            <li><a href="#error-handlers">Error Handlers</a></li>
                        </ul>
                    </div>
                    <div class="main-content">
                        <section id="flows">
                            <h2>Flows</h2>
                            {flows_html}
                        </section>
                        <section id="configs">
                            <h2>Configurations</h2>
                            {configs_html}
                        </section>
                        <section id="error-handlers">
                            <h2>Error Handlers</h2>
                            {error_handlers_html}
                        </section>
                    </div>
                </div>
            </body>
            </html>
            """
        except Exception as e:
            logging.error(f"Error generating HTML: {str(e)}")
            return "<html><body><h1>Error generating visualization</h1><p>Check the logs for details.</p></body></html>"

class FlowDocumentationGenerator:
    def __init__(self):
        self.flow_patterns = {
            # HTTP Components
            'http:listener': 'This flow is triggered by an HTTP endpoint. It {action} when receiving {method} requests at {path}.',
            'http:request': 'Makes an HTTP {method} request to {url}.',
            'http:response': 'Configures the HTTP response with status code {statusCode}.',
            
            # Core Components
            'flow-ref': 'Calls another flow named "{target_flow}".',
            'async': 'Processes the following operations asynchronously.',
            'scatter-gather': 'Executes multiple operations in parallel and aggregates their results.',
            'choice': 'Makes a decision based on conditions and routes the flow accordingly.',
            'foreach': 'Iterates over a collection of items, processing each one.',
            'batch:job': 'Processes records in batches for improved performance.',
            
            # Error Handling
            'error-handler': 'Handles errors that may occur during flow execution.',
            'on-error-continue': 'Handles errors and continues flow execution.',
            'on-error-propagate': 'Handles errors and propagates them to the caller.',
            'try': 'Attempts to execute a series of operations with error handling.',
            
            # Variables and Properties
            'set-variable': 'Sets a variable named "{name}" for later use in the flow.',
            'set-property': 'Sets a property named "{name}" with value.',
            'remove-variable': 'Removes the variable named "{name}" from the flow.',
            
            # Transformation
            'ee:transform': 'Transforms the data using DataWeave. {purpose}',
            'json:json-to-object': 'Converts JSON string to a Java object.',
            'json:object-to-json': 'Converts Java object to JSON string.',
            'xml:xml-to-object': 'Converts XML string to a Java object.',
            'xml:object-to-xml': 'Converts Java object to XML string.',
            
            # Validation
            'validation:is-true': 'Validates that a condition is true.',
            'validation:matches-regex': 'Validates that a value matches the regex pattern.',
            'validation:validate-schema': 'Validates the payload against a schema.',
            
            # File Operations
            'file:read': 'Reads content from file at path {path}.',
            'file:write': 'Writes content to file at path {path}.',
            'file:list': 'Lists files in directory {directory}.',
            
            # Database Operations
            'db:select': 'Executes a SELECT query on the database.',
            'db:insert': 'Executes an INSERT query on the database.',
            'db:update': 'Executes an UPDATE query on the database.',
            'db:delete': 'Executes a DELETE query on the database.',
            
            # Logging and Monitoring
            'logger': 'Logs {message} for monitoring and debugging.',
            'custom-logger': 'Logs custom message with additional metadata.',
            
            # Security
            'crypto:encrypt': 'Encrypts the payload using specified algorithm.',
            'crypto:decrypt': 'Decrypts the payload using specified algorithm.',
            'secure-properties:encrypt': 'Encrypts sensitive configuration properties.',
            
            # Integration Patterns
            'aggregator': 'Aggregates messages based on specified criteria.',
            'splitter': 'Splits the payload into multiple parts for processing.',
            'collection-aggregator': 'Aggregates a collection of messages.',
            
            # Connectors
            'salesforce:create': 'Creates a new record in Salesforce.',
            'salesforce:query': 'Executes a SOQL query in Salesforce.',
            'sap:execute': 'Executes a function in SAP.',
            'jms:publish': 'Publishes a message to JMS queue/topic.',
            'jms:consume': 'Consumes messages from JMS queue/topic.',
            'vm:publish': 'Publishes a message to VM queue.',
            'vm:consume': 'Consumes messages from VM queue.',
            
            # API Kit
            'apikit:router': 'Routes API requests based on RAML/OAS specification.',
            'apikit:console': 'Provides API console for testing.',
            
            # Cache
            'cache:set': 'Stores value in cache with key {key}.',
            'cache:get': 'Retrieves value from cache with key {key}.',
            'cache:remove': 'Removes value from cache with key {key}.'
        }

    def generate_flow_description(self, flow_name: str, flow_data: Dict) -> str:
        """Generate a Markdown description of a flow with detailed component info."""
        description = f"## Flow: {flow_name}\n\n"
        description += "This flow performs the following operations:\n\n"
        
        components = flow_data.get('components', [])
        if not components:
            return description + "No components found in this flow.\n\n"
        
        description += "<ol>\n"
        for component in components:
            ctype = component.get('type', '')
            cname = component.get('name', '')
            content = component.get('content', {})

            # Start list item
            if cname:
                description += f"  <li><strong>{cname}</strong> ({ctype})\n"
            else:
                description += f"  <li>{ctype}\n"

            # HTTP request: raw + parsed OData
            if ctype == 'request':
                if 'query_params' in content:
                    description += "\n    **Query parameters (raw):**\n\n    ```\n"
                    description += content['query_params'] + "\n"
                    description += "    ```\n"
                if 'odata_filter' in content:
                    description += f"\n    • OData `$filter`: `{content['odata_filter']}`\n"
                if 'odata_select' in content:
                    description += f"\n    • OData `$select`: `{content['odata_select']}`\n"
                if 'odata_params' in content:
                    description += "\n    • All OData parameters:\n"
                    for p, v in content['odata_params'].items():
                        description += f"      - **{p}**: `{v}`\n"

            # DataWeave transform
            elif ctype == 'transform':
                if 'set_payload' in content:
                    description += "\n    **Transform payload:**\n\n    ```\n"
                    description += content['set_payload'] + "\n"
                    description += "    ```\n"
                for key, val in content.items():
                    if key.startswith('variable_'):
                        var = key.replace('variable_', '')
                        description += f"\n    • Set `{var}` =\n\n      ```\n      {val}\n      ```\n"

            # Logger
            elif ctype == 'logger' and 'message' in content:
                description += f"\n    • Log message: \"{content['message']}\"\n"

            # Choice
            elif ctype == 'choice' and 'conditions' in content:
                description += "\n    **Conditions:**\n"
                for cond in content['conditions']:
                    description += f"      - `{cond}`\n"

            # Fallback for other components
            else:
                description += f"\n    Executes `{ctype}` component.\n"

            description += "  </li>\n"

        description += "</ol>\n\n"
        return description
   
    def generate_config_description(self, configs: Dict) -> str:
        """Generate a natural language description of configurations."""
        if not configs:
            return ""
            
        description = "## Configurations\n\n"
        description += "The application uses the following configurations:\n\n"
        
        for config_name, config_data in configs.items():
            description += f"### {config_name}\n"
            description += f"Type: {config_data.get('type', 'unknown')}\n"
            
            if config_data.get('attributes'):
                description += "Configuration details:\n"
                for key, value in config_data['attributes'].items():
                    if not key.startswith('{http://www.mulesoft.org/schema/mule/documentation}'):
                        description += f"- {key}: {value}\n"
            
            description += "\n"
        
        return description

    def generate_error_handling_description(self, error_handlers: Dict) -> str:
        """Generate a natural language description of error handling."""
        if not error_handlers:
            return ""
            
        description = "## Error Handling\n\n"
        description += "The application implements the following error handling strategies:\n\n"
        
        for handler_name, handler_data in error_handlers.items():
            description += f"### {handler_name}\n"
            
            if handler_data.get('handlers'):
                for handler in handler_data['handlers']:
                    description += f"- Handles {handler.get('type_to_match', 'all')} errors"
                    if handler.get('when'):
                        description += f" when {handler['when']}"
                    description += f" using {handler.get('type', 'unknown')}\n"
            
            description += "\n"
        
        return description

    def generate_documentation(self, parsed_data: Dict) -> str:
        """Generate complete documentation in markdown format."""
        try:
            # Title and overview
            doc = "# MuleSoft Application Documentation\n\n"
            doc += "## Overview\n\n"
            doc += (
                "This document provides a comprehensive overview of the MuleSoft "
                "application's flows, subflows, configurations, and error handling strategies.\n\n"
            )
            
            # Main flows
            doc += "# Flows\n\n"
            for flow_name, flow_data in parsed_data.get('flows', {}).items():
                doc += self.generate_flow_description(flow_name, flow_data)
                doc += "\n"
            
            # Subflows
            subflows = parsed_data.get('subflows', {})
            if subflows:
                doc += "# Subflows\n\n"
                for subflow_name, subflow_data in subflows.items():
                    doc += self.generate_flow_description(subflow_name, subflow_data)
                    doc += "\n"
            
            # Configurations
            doc += self.generate_config_description(parsed_data.get('configs', {}))
            
            # Error handling
            doc += self.generate_error_handling_description(parsed_data.get('error_handlers', {}))
            
            return doc
        except Exception as e:
            logging.error(f"Error generating documentation: {e}")
            return (
                "# Error Generating Documentation\n\n"
                "An unexpected error occurred while generating the documentation. "
                "Please check the logs for details.\n"
            )

class LLMDocumentationEnhancer:
    def __init__(self):
        # Initialize with 'openai' provider instead of anthropic, allowing fallback
        self.service = 'openai'  # Changed from 'anthropic' to 'openai'
        try:
            self.enhancer = DocumentationEnhancer(selected_service=self.service)
            logging.info(f"DocumentationEnhancer initialized with '{self.service}' service.")
        except Exception as e:
            logging.error(f"Error initializing DocumentationEnhancer: {str(e)}")
            logging.info("Falling back to default service.")
            self.enhancer = DocumentationEnhancer()

    def enhance_documentation(self, base_documentation: str) -> str:
        """Enhance documentation using LLM.
        
        Args:
            base_documentation: Base documentation to enhance
            
        Returns:
            Enhanced documentation
        """
        # Always process as a single unit - no chunking
        logging.info(f"Processing documentation as a single unit (size: {len(base_documentation)} chars)")
        
        try:
            logging.info(f"Starting LLM enhancement with {self.service} service")
            enhanced_documentation = self.enhancer.enhance_documentation(base_documentation)
            
            # If the result is identical to the input, enhancement likely failed
            if enhanced_documentation and enhanced_documentation != base_documentation:
                logging.info(f"Documentation successfully enhanced with {self.service}.")
                return enhanced_documentation
            else:
                logging.warning(f"LLM enhancement did not produce different results - using original documentation.")
                return base_documentation
            
        except Exception as e:
            logging.error(f"Error during LLM enhancement: {str(e)}")
            return base_documentation

def main():
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description="Generate documentation for MuleSoft flows")
        parser.add_argument("--input", required=True, help="Directory containing MuleSoft XML files")
        parser.add_argument("--output", default="./output", help="Output directory for documentation files")
        parser.add_argument("--enhance", action="store_true", help="Use LLM to enhance documentation")
        args = parser.parse_args()

        flow_parser = MuleFlowParser()
        html_gen = HTMLGenerator()
        doc_gen = FlowDocumentationGenerator()
        llm_enhancer = LLMDocumentationEnhancer()
        
        input_dir = args.input
        output_dir = args.output
        
        # Ensure output_dir is treated as a directory
        if os.path.splitext(output_dir)[1]:  # If output has a file extension
            output_dir = os.path.dirname(output_dir)  # Get the directory part
        
        if not os.path.exists(input_dir):
            logging.error(f"Directory does not exist: {input_dir}")
            return
        
        # Parse MuleSoft files
        logging.info(f"Starting to parse MuleSoft files from: {input_dir}")
        parsed_data = flow_parser.parse_mule_files(input_dir)
        
        if not parsed_data['flows'] and not parsed_data['configs'] and not parsed_data['error_handlers']:
            logging.error("No valid MuleSoft components found in the specified directory")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate and save documentation
        logging.info("Generating documentation...")
        
        try:
            # Generate HTML visualization
            html_content = html_gen.generate_html(parsed_data)
            html_file = os.path.join(output_dir, "flow_visualization.html")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info(f"Visualization generated at: {html_file}")
            
            # Generate base documentation
            doc_content = doc_gen.generate_documentation(parsed_data)
            
            # Enhance documentation with LLM if requested
            if args.enhance:
                logging.info("Enhancing documentation with LLM insights...")
                doc_content = llm_enhancer.enhance_documentation(doc_content)
            
            # Save markdown documentation
            doc_file = os.path.join(output_dir, "flow_documentation.md")
            with open(doc_file, "w", encoding="utf-8") as f:
                f.write(doc_content)
            logging.info(f"Documentation generated at: {doc_file}")
            
            # Comment out HTML generation as we now use a dedicated script for this
            # that properly handles Mermaid diagrams
            # 
            # Generate HTML version of documentation
            # html_doc = markdown.markdown(doc_content)
            # with open(output_file, "w", encoding="utf-8") as f:
            #     f.write(f"""
            #     <!DOCTYPE html>
            #     <html lang="en">
            #     <head>
            #         <meta charset="UTF-8">
            #         <meta name="viewport" content="width=device-width, initial-scale=1.0">
            #         <title>MuleSoft Flow Documentation</title>
            #         <style>
            #             body {{
            #                 font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            #                 line-height: 1.6;
            #                 max-width: 1200px;
            #                 margin: 0 auto;
            #                 padding: 20px;
            #                 color: #333;
            #             }}
            #             h1, h2, h3 {{
            #                 color: #1565c0;
            #             }}
            #             pre {{
            #                 background: #f5f5f5;
            #                 padding: 15px;
            #                 border-radius: 5px;
            #                 overflow-x: auto;
            #             }}
            #             code {{
            #                 background: #f5f5f5;
            #                 padding: 2px 5px;
            #                 border-radius: 3px;
            #             }}
            #             ul, ol {{
            #                 padding-left: 20px;
            #             }}
            #             .note {{
            #                 background: #e3f2fd;
            #                 padding: 10px;
            #                 border-left: 4px solid #1565c0;
            #                 margin: 10px 0;
            #             }}
            #             .insights {{
            #                 background: #f3e5f5;
            #                 padding: 15px;
            #                 border-radius: 5px;
            #                 margin: 20px 0;
            #             }}
            #             .best-practices {{
            #                 background: #e8f5e9;
            #                 padding: 15px;
            #                 border-radius: 5px;
            #                 margin: 20px 0;
            #             }}
            #             .security {{
            #                 background: #ffebee;
            #                 padding: 15px;
            #                 border-radius: 5px;
            #                 margin: 20px 0;
            #             }}
            #         </style>
            #     </head>
            #     <body>
            #         {html_doc}
            #     </body>
            #     </html>
            #     """)
            # logging.info(f"HTML documentation generated at: {output_file}")
            
            # Add information about using the new script for proper Mermaid rendering
            logging.info("Use md_to_html_with_mermaid.py to convert the MD file to HTML with Mermaid support")
            
        except Exception as e:
            logging.error(f"Error generating documentation: {str(e)}")
            
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 