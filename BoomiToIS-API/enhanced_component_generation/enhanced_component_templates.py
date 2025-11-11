"""
Enhanced Component Templates Library

Comprehensive template library for all 76+ SAP Integration Suite components
with full property support from components.json metadata.

Structure is HARDCODED, properties are DYNAMIC from JSON config.
"""

import xml.sax.saxutils
import time
import uuid
from typing import Dict, List, Optional, Union, Any


class EnhancedComponentTemplates:
    """
    Comprehensive collection of templates for SAP Integration Suite components.
    All 76+ components from components.json metadata plus all adapter templates.
    """
    
    def __init__(self):
        """Initialize the templates library"""
        pass
    
    # ===== HELPER METHODS =====
    
    def _escape_xml(self, value: Any) -> str:
        """Escape XML special characters in property values"""
        if value is None:
            return ""
        value_str = str(value)
        # Escape XML entities
        return xml.sax.saxutils.escape(value_str, {"'": "&apos;", '"': "&quot;"})
    
    def _format_property_value(self, value: Any) -> str:
        """Format property value for XML - handle empty values"""
        if value is None:
            return ""
        if isinstance(value, str):
            if not value or value == "<placeholder>" or value.startswith("<") and value.endswith(">"):
                return ""
            return self._escape_xml(value)
        # Convert non-string types to string
        return self._escape_xml(str(value))
    
    def _flatten_nested_object(self, obj: Dict[str, Any], parent_key: str = "", max_depth: int = 3) -> Dict[str, Any]:
        """
        Flatten nested objects into dot-notation keys or use property name directly.
        
        Args:
            obj: Nested dictionary to flatten
            parent_key: Parent key prefix (for dot notation)
            max_depth: Maximum recursion depth
        
        Returns:
            Flattened dictionary
        """
        if max_depth <= 0:
            return {}
        
        flattened = {}
        # Special mappings for common nested objects (SAP property names)
        nested_key_mappings = {
            "authentication": {
                "type": "authenticationMethod",  # authentication.type -> authenticationMethod
                "credentialName": "credentialName",
                "clientId": "clientId",
                "clientSecret": "clientSecret",
                "tokenServiceUrl": "tokenServiceUrl",
                "privateKeyAlias": "privateKeyAlias",
                "keyStoreAlias": "keyStoreAlias",
                "user": "user",
                "passwordAlias": "passwordAlias"
            },
            "proxy": {
                "proxyType": "proxyType",
                "proxyHost": "proxyHost",
                "proxyPort": "proxyPort"
            },
            "retry": {
                "enabled": "retryEnabled",
                "retryOnConnectionFailure": "retryOnConnectionFailure",
                "retryInterval": "retryInterval",
                "maximumReconnectAttempts": "maximumReconnectAttempts"
            },
            "ssl": {
                "sslProtocol": "sslProtocol",
                "trustedCertificates": "trustedCertificates"  # Will be handled as array
            }
        }
        
        for key, value in obj.items():
            # Check if we have a mapping for this nested object
            if parent_key in nested_key_mappings and key in nested_key_mappings[parent_key]:
                flattened_key = nested_key_mappings[parent_key][key]
            else:
                # Use dot notation for other nested objects
                flattened_key = f"{parent_key}.{key}" if parent_key else key
            
            # Recursively flatten if value is still a dict
            if isinstance(value, dict):
                nested_flattened = self._flatten_nested_object(value, flattened_key, max_depth - 1)
                flattened.update(nested_flattened)
            else:
                flattened[flattened_key] = value
        
        return flattened
    
    def _format_array_value(self, arr: List[Any], array_key: str = "") -> str:
        """
        Format array value for XML property.
        Handles both simple arrays (strings/numbers) and arrays of objects.
        
        Args:
            arr: Array to format
            array_key: Key name to determine formatting strategy
        
        Returns:
            Formatted string value
        """
        if not arr:
            return ""
        
        # Arrays of objects (like headers, properties) are handled separately as XML tables
        # Return empty string - specific templates will handle these
        if isinstance(arr[0], dict):
            # These should be converted to XML tables by specific templates
            # Return empty string here, templates will handle headerTable/propertyTable
            return ""
        
        # Simple arrays: convert to comma-separated string
        return ",".join(str(item) for item in arr if item is not None and item != "")
    
    def _generate_property_xml(self, config: Dict[str, Any], skip_empty: bool = True, skip_keys: Optional[List[str]] = None) -> str:
        """
        Dynamically generate <ifl:property> elements from config dict.
        Handles nested objects (flattened) and arrays (comma-separated or XML tables).
        
        Args:
            config: Configuration dictionary
            skip_empty: Skip empty/placeholder values
            skip_keys: List of keys to skip (e.g., 'routing_conditions', 'headers', 'properties' handled separately)
        
        Returns:
            XML string of all properties
        """
        if skip_keys is None:
            skip_keys = []
        
        # Flatten the config to handle nested objects
        flattened_config = {}
        for key, value in config.items():
            if key in skip_keys:
                continue
            
            # Flatten nested objects
            if isinstance(value, dict):
                # Common nested objects that should be flattened
                if key in ["authentication", "proxy", "retry", "ssl", "ackConfiguration", "log_configuration", "idempotentCondition", "originalMessage", "lookupMessage", "signerParameters", "validationParameters", "xadesBES", "xadesEPES"]:
                    flattened = self._flatten_nested_object(value, key)
                    flattened_config.update(flattened)
                else:
                    # For other nested objects, try JSON encoding as fallback
                    import json
                    try:
                        flattened_config[key] = json.dumps(value)
                    except:
                        # If JSON encoding fails, skip it
                        continue
            else:
                flattened_config[key] = value
        
        properties = []
        # Properties that contain XML/code and should be CDATA-wrapped
        cdata_properties = ['bodyContent', 'scriptContent', 'script', 'groovyScript',
                           'xsltMapping', 'mappingContent', 'wsdlContent']

        for key, value in flattened_config.items():
            # Skip empty values if requested (but allow empty strings if explicitly set in skip_empty=False)
            if skip_empty:
                if value is None:
                    continue
                # Allow empty string for namespaceContext and similar fields if they're explicitly in config
                if value == "" and key not in ["namespaceContext", "bodyNamespaceMapping"]:
                    continue
                # Skip placeholder values, but NOT for CDATA properties which may contain XML
                if key not in cdata_properties and isinstance(value, str) and (value == "<placeholder>" or (value.startswith("<") and value.endswith(">") and "|" not in value)):
                    continue
            
            # Handle arrays
            if isinstance(value, list):
                # Special handling for xmlJsonPathTable (XPath path table for XML to JSON converter)
                if key == "xmlJsonPathTable":
                    # Convert list of XPath expressions to HTML-encoded table format
                    value = self._create_xpath_path_table_xml(value)
                    if not value and skip_empty:
                        continue
                else:
                    # Arrays of objects are handled by specific templates (headerTable, propertyTable)
                    # Simple arrays become comma-separated strings
                    formatted_array = self._format_array_value(value, key)
                    if not formatted_array and skip_empty:
                        continue
                    value = formatted_array if formatted_array else ""
            
            # Generate property XML
            # Special case: xmlJsonPathTable is already HTML-encoded, don't escape it again
            if key == "xmlJsonPathTable":
                formatted_value = value  # Already HTML-encoded by _create_xpath_path_table_xml()
            elif key in cdata_properties and value and not str(value).startswith('<![CDATA['):
                # For CDATA properties, use raw value without escaping
                formatted_value = value
            else:
                formatted_value = self._format_property_value(value)

            if skip_empty and not formatted_value:
                continue

            # Use empty tag format for empty values to match SAP IS format
            if formatted_value:
                if key in cdata_properties and not str(formatted_value).startswith('<![CDATA['):
                    # Wrap in CDATA to preserve XML/code content
                    properties.append(f'                <ifl:property>\n                    <key>{self._escape_xml(key)}</key>\n                    <value><![CDATA[{formatted_value}]]></value>\n                </ifl:property>')
                else:
                    properties.append(f'                <ifl:property>\n                    <key>{self._escape_xml(key)}</key>\n                    <value>{formatted_value}</value>\n                </ifl:property>')
            else:
                properties.append(f'                <ifl:property>\n                    <key>{self._escape_xml(key)}</key>\n                    <value />\n                </ifl:property>')
        
        return '\n'.join(properties) if properties else '                <ifl:property>\n                    <key>componentVersion</key>\n                    <value>1.0</value>\n                </ifl:property>'

    def _create_xpath_path_table_xml(self, xpath_paths: Union[List[str], str]) -> str:
        """
        Convert array of XPath expressions to HTML-encoded XML table format for xmlJsonPathTable.

        SAP IS format: &lt;row&gt;&lt;cell&gt;/xpath/expression&lt;/cell&gt;&lt;cell&gt;&lt;/cell&gt;&lt;/row&gt;...

        Args:
            xpath_paths: List of XPath expressions or pre-formatted string

        Returns:
            HTML-encoded XML table string

        Examples:
            Input (list): ["/Titles/Title/businessUnits", "/Titles/Title"]
            Output: "&lt;row&gt;&lt;cell&gt;/Titles/Title/businessUnits&lt;/cell&gt;&lt;cell&gt;&lt;/cell&gt;&lt;/row&gt;&lt;row&gt;&lt;cell&gt;/Titles/Title&lt;/cell&gt;&lt;cell&gt;&lt;/cell&gt;&lt;/row&gt;"
        """
        # If already a string, return as-is
        if isinstance(xpath_paths, str):
            return xpath_paths

        # If not a list or empty, return empty
        if not isinstance(xpath_paths, list) or not xpath_paths:
            return ""

        # Build the table rows
        rows = []
        for xpath in xpath_paths:
            if xpath:
                # Escape any XML special characters in the XPath
                escaped_xpath = self._escape_xml(str(xpath))
                # Create a row with two cells (second cell is empty as per SAP IS format)
                row = f'<row><cell>{escaped_xpath}</cell><cell></cell></row>'
                rows.append(row)

        # Join all rows into a single XML string
        raw_xml = ''.join(rows)

        # HTML-encode the entire XML string
        import html
        html_encoded = html.escape(raw_xml)

        return html_encoded

    def _create_property_table_xml(self, properties: List[Dict[str, Any]]) -> str:
        """
        Convert array of property objects to XML table format.
        
        Args:
            properties: List of property dicts with keys like Action, Type, Name, Value, Default, DataType, etc.
        
        Returns:
            XML table string (can be empty if no properties)
        """
        if not properties:
            return ""
        
        rows = []
        for prop in properties:
            action = prop.get("Action", prop.get("action", "Create"))
            prop_type = prop.get("Type", prop.get("type", "constant"))
            name = prop.get("Name", prop.get("name", ""))
            value = prop.get("Value", prop.get("value", ""))
            default = prop.get("Default", prop.get("default", ""))
            datatype = prop.get("DataType", prop.get("datatype", prop.get("Datatype", "")))
            expression_lang = prop.get("ExpressionLanguage", prop.get("expressionLanguage", ""))
            enabled = prop.get("Enabled", prop.get("enabled", "true"))
            
            # Escape XML in values
            action = self._escape_xml(str(action))
            prop_type = self._escape_xml(str(prop_type))
            name = self._escape_xml(str(name))
            value = self._escape_xml(str(value))
            default = self._escape_xml(str(default))
            datatype = self._escape_xml(str(datatype))
            expression_lang = self._escape_xml(str(expression_lang))
            enabled = self._escape_xml(str(enabled))
            
            row = f'<row><cell id="Action">{action}</cell><cell id="Type">{prop_type}</cell><cell id="Name">{name}</cell><cell id="Value">{value}</cell><cell id="Default">{default}</cell><cell id="Datatype">{datatype}</cell>'
            if expression_lang:
                row += f'<cell id="ExpressionLanguage">{expression_lang}</cell>'
            if enabled:
                row += f'<cell id="Enabled">{enabled}</cell>'
            row += '</row>'
            rows.append(row)
        
        return ''.join(rows)
    
    def _create_header_table_xml(self, headers: List[Dict[str, Any]]) -> str:
        """
        Convert array of header objects to XML table format.
        Same format as property table.
        
        Args:
            headers: List of header dicts with keys like Action, Type, Name, Value, Default, DataType
        
        Returns:
            XML table string (can be empty if no headers)
        """
        return self._create_property_table_xml(headers)
    
    def _create_modifications_table_xml(self, modifications: List[Dict[str, Any]]) -> str:
        """
        Convert array of modification objects to XML table format.
        
        Args:
            modifications: List of modification dicts with keys like Action, Path, Value, Type, Namespace, etc.
        
        Returns:
            XML table string
        """
        if not modifications:
            return ""
        
        rows = []
        for mod in modifications:
            action = mod.get("Action", mod.get("action", "Add"))
            path = mod.get("Path", mod.get("path", ""))
            value = mod.get("Value", mod.get("value", ""))
            mod_type = mod.get("Type", mod.get("type", "Element"))
            namespace = mod.get("Namespace", mod.get("namespace", ""))
            namespace_prefix = mod.get("NamespacePrefix", mod.get("namespacePrefix", mod.get("NamespacePrefix", "")))
            
            # Escape XML
            action = self._escape_xml(str(action))
            path = self._escape_xml(str(path))
            value = self._escape_xml(str(value))
            mod_type = self._escape_xml(str(mod_type))
            namespace = self._escape_xml(str(namespace))
            namespace_prefix = self._escape_xml(str(namespace_prefix))
            
            row = f'<row><cell id="Action">{action}</cell><cell id="Path">{path}</cell><cell id="Value">{value}</cell><cell id="Type">{mod_type}</cell>'
            if namespace:
                row += f'<cell id="Namespace">{namespace}</cell>'
            if namespace_prefix:
                row += f'<cell id="NamespacePrefix">{namespace_prefix}</cell>'
            row += '</row>'
            rows.append(row)
        
        # Return raw XML (will be wrapped in CDATA when used in property value)
        return ''.join(rows)
    
    def _generate_unique_id(self, prefix: str = "") -> str:
        """Generate a unique ID for components"""
        unique_id = str(uuid.uuid4()).replace('-', '')[:8]
        timestamp = str(int(time.time() * 1000))[-4:]
        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}"
        return f"ID_{timestamp}_{unique_id}"
    
    # ===== iFlow Configuration =====
    
    def iflow_configuration_template(self, namespace_mapping="", log_level="All events", csrf_protection="false"):
        """
        Template for iFlow configuration
        
        Args:
            namespace_mapping: XML namespace mappings
            log_level: Logging level
            csrf_protection: CSRF protection enabled
        """
        properties_xml = f'''            <ifl:property>
                <key>namespaceMapping</key>
                <value>{self._format_property_value(namespace_mapping) if namespace_mapping else ""}</value>
            </ifl:property>
            <ifl:property>
                <key>httpSessionHandling</key>
                <value>None</value>
            </ifl:property>
            <ifl:property>
                <key>returnExceptionToSender</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>log</key>
                <value>{log_level}</value>
            </ifl:property>
            <ifl:property>
                <key>corsEnabled</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>componentVersion</key>
                <value>1.2</value>
            </ifl:property>
            <ifl:property>
                <key>ServerTrace</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>xsrfProtection</key>
                <value>{csrf_protection}</value>
            </ifl:property>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::IFlowVariant/cname::IFlowConfiguration/version::1.2.4</value>
            </ifl:property>'''
        
        return f'''<bpmn2:extensionElements>
{properties_xml}
        </bpmn2:extensionElements>'''
    
    # ===== Participant Templates =====
    
    def participant_template(self, id: str, name: str, participant_type: str = "EndpointRecevier", enable_basic_auth: str = "false", config: Optional[Dict[str, Any]] = None):
        """
        Template for Participant (Sender/Receiver)
        
        Args:
            id: Participant ID
            name: Participant name
            participant_type: Participant type (EndpointSender, EndpointRecevier, IntegrationProcess)
            enable_basic_auth: Enable basic authentication
            config: Additional config properties
        """
        if config is None:
            config = {}
        
        auth_property = ""
        if participant_type == "EndpointSender":
            auth_property = f'''
                <ifl:property>
                    <key>enableBasicAuthentication</key>
                    <value>{enable_basic_auth}</value>
                </ifl:property>'''
        
        additional_props = self._generate_property_xml(config, skip_keys=['ifl_type']) if config else ""
        
        return f'''<bpmn2:participant id="{id}" ifl:type="{participant_type}" name="{name}">
            <bpmn2:extensionElements>{auth_property}
                <ifl:property>
                    <key>ifl:type</key>
                    <value>{participant_type}</value>
                </ifl:property>
{additional_props}
            </bpmn2:extensionElements>
        </bpmn2:participant>'''
    
    def integration_process_participant_template(self, id: str, name: str, process_ref: str):
        """Template for Integration Process Participant"""
        return f'''<bpmn2:participant id="{id}" ifl:type="IntegrationProcess" name="{name}" processRef="{process_ref}">
            <bpmn2:extensionElements />
        </bpmn2:participant>'''
    
    # ===== Adapter Templates =====
    
    def https_sender_template(self, id: str, name: str, config: Dict[str, Any]):
        """
        Template for HTTPS Sender Adapter
        Maps all properties from config to XML
        """
        url_path = config.get("urlPath", "/")
        sender_auth = config.get("senderAuthType", "None")
        user_role = config.get("userRole", "ESBMessaging.send")
        csrf_protection = config.get("xsrfProtection", "false")
        client_certificates = config.get("clientCertificates", "")
        
        # Generate all properties from config
        properties_xml = self._generate_property_xml(config, skip_keys=['urlPath', 'senderAuthType', 'userRole', 'xsrfProtection', 'clientCertificates'])
        
        # Ensure required properties are present
        required_props = f'''                <ifl:property>
                    <key>ComponentType</key>
                    <value>HTTPS</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value />
                </ifl:property>
                <ifl:property>
                    <key>maximumBodySize</key>
                    <value>{config.get("maximumBodySize", "40")}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.4")}</value>
                </ifl:property>
                <ifl:property>
                    <key>urlPath</key>
                    <value>{url_path}</value>
                </ifl:property>
                <ifl:property>
                    <key>Name</key>
                    <value>HTTPS</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>{config.get("TransportProtocolVersion", "1.4.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>{config.get("system", "ESBMessaging")}</value>
                </ifl:property>
                <ifl:property>
                    <key>xsrfProtection</key>
                    <value>{csrf_protection}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTPS</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::AdapterVariant/cname::sap:HTTPS/tp::HTTPS/mp::None/direction::Sender/version::1.4.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>userRole</key>
                    <value>{user_role}</value>
                </ifl:property>
                <ifl:property>
                    <key>senderAuthType</key>
                    <value>{sender_auth}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>None</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>{config.get("MessageProtocolVersion", "1.4.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVId</key>
                    <value>{config.get("ComponentSWCVId", "1.4.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Sender</value>
                </ifl:property>
                <ifl:property>
                    <key>clientCertificates</key>
                    <value>{client_certificates}</value>
                </ifl:property>
{properties_xml}'''
        
        return f'''<bpmn2:messageFlow id="{id}" name="HTTPS" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''
    
    def http_receiver_template(self, id: str, name: str, config: Dict[str, Any]):
        """Template for HTTP Receiver Adapter"""
        address = config.get("httpAddressWithoutQuery", config.get("address", ""))
        auth_method = config.get("authenticationMethod", "None")
        credential_name = config.get("credentialName", "")
        timeout = config.get("httpRequestTimeout", "60000")
        throw_exception = config.get("throwExceptionOnFailure", "true")
        system = config.get("system", "")
        http_method = config.get("httpMethod", "POST")
        
        # Generate all properties from config
        properties_xml = self._generate_property_xml(config, skip_keys=['httpAddressWithoutQuery', 'address', 'authenticationMethod', 'credentialName', 'httpRequestTimeout', 'throwExceptionOnFailure', 'system', 'httpMethod'])
        
        required_props = f'''                <ifl:property>
                    <key>Description</key>
                    <value />
                </ifl:property>
                <ifl:property>
                    <key>httpMethod</key>
                    <value>{http_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>httpRequestTimeout</key>
                    <value>{timeout}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>authenticationMethod</key>
                    <value>{auth_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>credentialName</key>
                    <value>{credential_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>None</value>
                </ifl:property>
                <ifl:property>
                    <key>httpAddressWithoutQuery</key>
                    <value define="true">{address}</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Receiver</value>
                </ifl:property>
                <ifl:property>
                    <key>throwExceptionOnFailure</key>
                    <value>{throw_exception}</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>{system}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.16")}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None/direction::Receiver/version::1.16.2")}</value>
                </ifl:property>
{properties_xml}'''
        
        return f'''<bpmn2:messageFlow id="{id}" name="{name}" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''
    
    def odata_receiver_template(self, id: str, name: str, config: Dict[str, Any]):
        """Template for OData Receiver Adapter"""
        service_url = config.get("address", config.get("serviceUrl", ""))
        entity_set = config.get("entitySet", "")
        auth_method = config.get("authenticationMethod", "None")
        credential_name = config.get("credentialName", "")
        timeout = config.get("httpRequestTimeout", "60000")
        system = config.get("system", "")
        operation = config.get("operation", "Query(GET)")
        resource_path = config.get("resourcePath", entity_set)
        
        properties_xml = self._generate_property_xml(config, skip_keys=['address', 'serviceUrl', 'entitySet', 'authenticationMethod', 'credentialName', 'httpRequestTimeout', 'system', 'operation', 'resourcePath'])
        
        required_props = f'''                <ifl:property>
                    <key>ComponentType</key>
                    <value>HCIOData</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value>OData connection to {entity_set}</value>
                </ifl:property>
                <ifl:property>
                    <key>Name</key>
                    <value>OData</value>
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>{service_url}</value>
                </ifl:property>
                <ifl:property>
                    <key>resourcePath</key>
                    <value>{resource_path}</value>
                </ifl:property>
                <ifl:property>
                    <key>operation</key>
                    <value>{operation}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.25")}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>{config.get("TransportProtocolVersion", "1.25.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>{config.get("MessageProtocolVersion", "1.25.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>authenticationMethod</key>
                    <value>{auth_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>credentialName</key>
                    <value>{credential_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>httpRequestTimeout</key>
                    <value>{timeout}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>OData V2</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Receiver</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>{system}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::AdapterVariant/cname::sap:HCIOData/tp::HTTP/mp::OData V2/direction::Receiver/version::1.25.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>isCSRFEnabled</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>enableMPLAttachments</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>contentType</key>
                    <value>application/atom+xml</value>
                </ifl:property>
                <ifl:property>
                    <key>proxyType</key>
                    <value>default</value>
                </ifl:property>
{properties_xml}'''
        
        return f'''<bpmn2:messageFlow id="{id}" name="{name}" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''
    
    def soap_receiver_template(self, id: str, name: str, config: Dict[str, Any]):
        """Template for SOAP Receiver Adapter"""
        address = config.get("address", "")
        auth_method = config.get("authenticationMethod", config.get("authentication", "None"))
        credential_name = config.get("credentialName", "")
        timeout = config.get("requestTimeout", config.get("httpRequestTimeout", "60000"))
        system = config.get("system", "")
        compress_message = config.get("CompressMessage", "false")
        location_id = config.get("location_id", "")
        
        properties_xml = self._generate_property_xml(config, skip_keys=['address', 'authenticationMethod', 'authentication', 'credentialName', 'requestTimeout', 'httpRequestTimeout', 'system', 'CompressMessage', 'location_id'])
        
        required_props = f'''                <ifl:property>
                    <key>cleanupHeaders</key>
                    <value>1</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value />
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>location_id</key>
                    <value>{location_id}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>{config.get("TransportProtocolVersion", "1.10.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>CompressMessage</key>
                    <value>{compress_message}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>Plain SOAP</value>
                </ifl:property>
                <ifl:property>
                    <key>requestTimeout</key>
                    <value>{timeout}</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Receiver</value>
                </ifl:property>
                <ifl:property>
                    <key>authentication</key>
                    <value>{auth_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>SOAP</value>
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>{address}</value>
                </ifl:property>
                <ifl:property>
                    <key>allowChunking</key>
                    <value>1</value>
                </ifl:property>
                <ifl:property>
                    <key>SapRmMessageIdDetermination</key>
                    <value>Reuse</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.9")}</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>{system}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::AdapterVariant/cname::sap:SOAP/tp::HTTP/mp::Plain SOAP/direction::Receiver/version::1.9.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>credentialName</key>
                    <value>{credential_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>{config.get("MessageProtocolVersion", "1.10.0")}</value>
                </ifl:property>
{properties_xml}'''
        
        return f'''<bpmn2:messageFlow id="{id}" name="{name}" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''
    
    def process_direct_template(self, id: str, name: str, config: Dict[str, Any]):
        """Template for ProcessDirect Adapter"""
        address = config.get("address", "")
        system = config.get("system", "")
        
        properties_xml = self._generate_property_xml(config, skip_keys=['address', 'system'])
        
        required_props = f'''                <ifl:property>
                    <key>ComponentType</key>
                    <value>ProcessDirect</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value />
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>{address}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>Vendor</key>
                    <value>SAP</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>{config.get("TransportProtocolVersion", "1.1.2")}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>{system}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>Not Applicable</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::AdapterVariant/cname::ProcessDirect/vendor::SAP/tp::Not Applicable/mp::Not Applicable/direction::Receiver/version::1.1.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>Not Applicable</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>{config.get("MessageProtocolVersion", "1.1.2")}</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Receiver</value>
                </ifl:property>
{properties_xml}'''
        
        return f'''<bpmn2:messageFlow id="{id}" name="ProcessDirect" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''
    
    # ===== Generic Component Template Method =====
    
    def generic_component_template(self, id: str, name: str, sap_activity_type: str, config: Dict[str, Any], bpmn_element: str = "callActivity", incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None) -> str:
        """
        Generic template method for components based on sap_activity_type.
        Handles most components with callActivity, serviceTask, etc.
        
        Args:
            id: Component ID
            name: Component name
            sap_activity_type: SAP activity type (e.g., "MessageMapping", "Enricher", "Filter")
            config: Configuration dictionary
            bpmn_element: BPMN2 element type (callActivity, serviceTask, etc.)
            incoming_flows: List of sequence flow IDs that connect TO this component
            outgoing_flows: List of sequence flow IDs that connect FROM this component
        """
        # Generate properties from config
        properties_xml = self._generate_property_xml(config, skip_empty=True)
        
        # Ensure required properties
        activity_type = config.get("activityType", sap_activity_type)
        component_version = config.get("componentVersion", "1.0")
        cmd_variant_uri = config.get("cmdVariantUri", f"ctype::FlowstepVariant/cname::{sap_activity_type}/version::{component_version}")
        
        # Generate properties, skipping keys that are already in required_props
        skip_keys_for_props = ['componentVersion', 'activityType', 'cmdVariantUri']
        properties_xml_filtered = self._generate_property_xml(config, skip_keys=skip_keys_for_props)
        
        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{component_version}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>{activity_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{cmd_variant_uri}</value>
                </ifl:property>
{properties_xml_filtered}'''
        
        # Generate incoming flows XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"
        
        # Generate outgoing flows XML
        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"
        
        if bpmn_element == "serviceTask":
            return f'''<bpmn2:serviceTask id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:serviceTask>'''
        elif bpmn_element == "callActivity":
            return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:callActivity>'''
        else:
            # Default to callActivity
            return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:callActivity>'''
    
    # ===== Router and Gateway Templates =====
    
    def router_template(self, id: str, name: str, config: Dict[str, Any], default_flow_id: Optional[str] = None, incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """
        Template for Router (Exclusive Gateway) component.
        Supports multiple routing branches with conditions.
        """
        throw_exception = config.get("throwException", "false")
        gateway_type = config.get("gatewayType", "Exclusive")

        properties_xml = self._generate_property_xml(config, skip_keys=['throwException', 'gatewayType', 'defaultFlowId', 'routes'])

        default_attr = f' default="{default_flow_id}"' if default_flow_id else ""

        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>{config.get("activityType", "ExclusiveGateway")}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.1.2")}</value>
                </ifl:property>
                <ifl:property>
                    <key>throwException</key>
                    <value>{throw_exception}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:exclusiveGateway{default_attr} id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:exclusiveGateway>'''
    
    def gateway_route_template(self, id: str, name: str, source_ref: str, target_ref: str, config: Dict[str, Any], condition_expression: Optional[str] = None, expression_type: str = "XML"):
        """
        Template for Gateway Route (sequence flow from router to target).
        Handles conditional and default routes.
        """
        properties_xml = self._generate_property_xml(config, skip_keys=['sourceGatewayId', 'target', 'conditionExpression', 'expressionType', 'isDefault'])
        
        # Generate condition expression if provided
        condition_xml = ""
        if condition_expression and condition_expression.strip():
            expression_content = condition_expression.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            expression_id = f"FormalExpression_{id}_{int(time.time() * 1000)}"
            condition_xml = f'''
            <bpmn2:conditionExpression id="{expression_id}" xsi:type="bpmn2:tFormalExpression">{expression_content}</bpmn2:conditionExpression>'''
        
        required_props = f'''                <ifl:property>
                    <key>expressionType</key>
                    <value>{expression_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0")}</value>
                </ifl:property>
{properties_xml}'''
        
        return f'''<bpmn2:sequenceFlow id="{id}" name="{name}" sourceRef="{source_ref}" targetRef="{target_ref}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{condition_xml}
        </bpmn2:sequenceFlow>'''
    
    # ===== Script Component Templates =====
    
    def groovy_script_template(self, id: str, name: str, config: Dict[str, Any], script_filename: Optional[str] = None, incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """
        Template for Groovy Script component.
        Requires script file to be created separately.
        """
        if script_filename is None:
            script_filename = config.get("script", config.get("scriptFilename", f"{id}.groovy"))

        properties_xml = self._generate_property_xml(config, skip_keys=['script', 'scriptFilename', 'scriptFunction', 'scriptBundleId', 'subActivityType'])

        script_function = config.get("scriptFunction", "processMessage")
        script_bundle_id = config.get("scriptBundleId", "")

        required_props = f'''                <ifl:property>
                    <key>activityType</key>
                    <value>Script</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::GroovyScript/version::1.1.2")}</value>
                </ifl:property>
                <ifl:property>
                    <key>script</key>
                    <value>{script_filename}</value>
                </ifl:property>
                <ifl:property>
                    <key>scriptFunction</key>
                    <value>{script_function}</value>
                </ifl:property>
                <ifl:property>
                    <key>scriptBundleId</key>
                    <value>{script_bundle_id}</value>
                </ifl:property>
                <ifl:property>
                    <key>subActivityType</key>
                    <value>GroovyScript</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:callActivity>'''

    def javascript_template(self, id: str, name: str, config: Dict[str, Any], script_filename: Optional[str] = None, incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for JavaScript component (same as Groovy)"""
        return self.groovy_script_template(id, name, config, script_filename, incoming_flows, outgoing_flows)

    def script_template(self, id: str, name: str, config: Dict[str, Any], script_filename: Optional[str] = None, incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Generic script template (alias for groovy_script_template)"""
        return self.groovy_script_template(id, name, config, script_filename, incoming_flows, outgoing_flows)
    
    # ===== Event Templates =====
    
    def start_event_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Start Event"""
        properties_xml = self._generate_property_xml(config, skip_keys=['eventType'])

        required_props = f'''                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::MessageStartEvent/version::1.1.0")}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:startEvent id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
            <bpmn2:messageEventDefinition />
        </bpmn2:startEvent>'''

    def end_event_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for End Event"""
        properties_xml = self._generate_property_xml(config, skip_keys=['eventType'])

        required_props = f'''                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0")}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:endEvent id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
            <bpmn2:messageEventDefinition />
        </bpmn2:endEvent>'''

    def message_start_event_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Message Start Event"""
        return self.start_event_template(id, name, config, incoming_flows, outgoing_flows)

    def message_end_event_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Message End Event"""
        return self.end_event_template(id, name, config, incoming_flows, outgoing_flows)

    def error_start_event_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Error Start Event"""
        properties_xml = self._generate_property_xml(config)

        required_props = f'''                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::ErrorStartEvent/version::1.0.0")}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:startEvent id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
            <bpmn2:errorEventDefinition />
        </bpmn2:startEvent>'''

    def error_end_event_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Error End Event"""
        properties_xml = self._generate_property_xml(config)

        required_props = f'''                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::ErrorEndEvent/version::1.0.0")}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:endEvent id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
            <bpmn2:errorEventDefinition />
        </bpmn2:endEvent>'''

    def escalation_end_event_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Escalation End Event"""
        properties_xml = self._generate_property_xml(config)

        required_props = f'''                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::EscalationEndEvent/version::1.0.0")}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:endEvent id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
            <bpmn2:escalationEventDefinition />
        </bpmn2:endEvent>'''

    def terminate_end_event_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Terminate End Event"""
        properties_xml = self._generate_property_xml(config)

        required_props = f'''                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::TerminateEndEvent/version::1.0.0")}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:endEvent id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
            <bpmn2:terminateEventDefinition />
        </bpmn2:endEvent>'''

    def timer_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Timer component"""
        properties_xml = self._generate_property_xml(config, skip_keys=['scheduleType', 'cronExpression', 'repeatInterval'])

        schedule_type = config.get("scheduleType", "Cron")
        cron_expression = config.get("cronExpression", "")
        repeat_interval = config.get("repeatInterval", "")

        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>{config.get("activityType", "Timer")}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::Timer/version::1.0.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>scheduleType</key>
                    <value>{schedule_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>cronExpression</key>
                    <value>{cron_expression}</value>
                </ifl:property>
                <ifl:property>
                    <key>repeatInterval</key>
                    <value>{repeat_interval}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:startEvent id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
            <bpmn2:timerEventDefinition />
        </bpmn2:startEvent>'''
    
    # ===== Content Modifier and Enricher Templates =====
    
    def content_modifier_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Content Modifier (Enricher) component"""
        # Extract headers and properties arrays to convert to XML tables
        headers = config.get("headers", [])
        properties_list = config.get("properties", [])
        modifications = config.get("modifications", [])  # For XML Modifier compatibility
        
        # Convert arrays to XML tables if they exist
        header_table_xml = self._create_header_table_xml(headers) if headers else ""
        property_table_xml = self._create_property_table_xml(properties_list) if properties_list else ""
        modifications_table_xml = self._create_modifications_table_xml(modifications) if modifications else ""
        
        # Use headerTable/propertyTable from config if provided, otherwise use generated tables
        # Note: If config provides tables, they may already be CDATA-wrapped or plain XML
        # Generated tables are now CDATA-wrapped
        header_table = config.get("headerTable", header_table_xml)
        property_table = config.get("propertyTable", property_table_xml)
        modifications_table = config.get("modificationsTable", modifications_table_xml)
        
        # Ensure tables are CDATA-wrapped if they contain XML (but not already wrapped)
        # Note: Empty tables should use <value /> format, not empty string
        if header_table and not header_table.startswith('<![CDATA[') and '<row>' in header_table:
            header_table = f'<![CDATA[{header_table}]]>'
        elif not header_table:
            header_table = ""  # Will be rendered as <value /> in template
        
        if property_table and not property_table.startswith('<![CDATA[') and '<row>' in property_table:
            property_table = f'<![CDATA[{property_table}]]>'
        elif not property_table:
            property_table = ""  # Will be rendered as <value /> in template
        
        if modifications_table and not modifications_table.startswith('<![CDATA[') and '<row>' in modifications_table:
            modifications_table = f'<![CDATA[{modifications_table}]]>'
        elif not modifications_table:
            modifications_table = ""  # Will be rendered as <value /> in template
        
        # Skip keys that are handled specially (arrays converted to tables) OR already in required_props
        skip_keys = ['bodyType', 'bodyContent', 'bodyEncoding', 'wrapContent', 'headerTable', 'propertyTable', 
                     'bodyTable', 'modificationsTable', 'headers', 'properties', 'modifications', 
                     'componentVersion', 'activityType', 'cmdVariantUri']
        properties_xml = self._generate_property_xml(config, skip_keys=skip_keys)
        
        body_type = config.get("bodyType", "none")
        body_content = config.get("bodyContent", "")
        body_encoding = config.get("bodyEncoding", "UTF-8")
        wrap_content = config.get("wrapContent", "")
        body_table = config.get("bodyTable", "")

        # Wrap bodyContent in CDATA if it contains XML
        if body_content and body_content.strip().startswith('<') and not body_content.startswith('<![CDATA['):
            body_content_value = f'<![CDATA[{body_content}]]>'
        else:
            body_content_value = body_content

        required_props = f'''                <ifl:property>
                    <key>bodyType</key>
                    <value>{body_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>propertyTable</key>
                    <value>{property_table if property_table else ""}</value>
                </ifl:property>
                <ifl:property>
                    <key>headerTable</key>
                    <value>{header_table if header_table else ""}</value>
                </ifl:property>
                <ifl:property>
                    <key>wrapContent</key>
                    <value>{wrap_content}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.6")}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>{config.get("activityType", "Enricher")}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::Enricher/version::1.4.2")}</value>
                </ifl:property>
                <ifl:property>
                    <key>bodyContent</key>
                    <value>{body_content_value}</value>
                </ifl:property>
                <ifl:property>
                    <key>bodyEncoding</key>
                    <value>{body_encoding}</value>
                </ifl:property>
{properties_xml}'''
        
        # Generate incoming flows XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n                <bpmn2:incoming>{flow_id}</bpmn2:incoming>"
        
        # Generate outgoing flows XML
        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n                <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"
        
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:callActivity>'''
    
    def enricher_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Enricher (alias for content_modifier)"""
        return self.content_modifier_template(id, name, config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)
    
    # ===== Mapping Templates =====
    
    def message_mapping_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Message Mapping component"""
        properties_xml = self._generate_property_xml(config, skip_keys=['mappinguri', 'mappingname', 'mappingpath', 'resource', 'mmapFile', 'mappingType'])

        mapping_uri = config.get("mappinguri", config.get("mappingUri", ""))
        mapping_name = config.get("mappingname", config.get("mappingName", name))
        mapping_path = config.get("mappingpath", config.get("mappingPath", ""))
        resource = config.get("resource", "")
        mmap_file = config.get("mmapFile", "")
        mapping_type = config.get("mappingType", "MessageMapping")

        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.5")}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Mapping</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::MessageMapping/version::1.5.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>mappinguri</key>
                    <value>{mapping_uri}</value>
                </ifl:property>
                <ifl:property>
                    <key>mappingname</key>
                    <value>{mapping_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>mappingpath</key>
                    <value>{mapping_path}</value>
                </ifl:property>
                <ifl:property>
                    <key>resource</key>
                    <value>{resource}</value>
                </ifl:property>
                <ifl:property>
                    <key>mmapFile</key>
                    <value>{mmap_file}</value>
                </ifl:property>
                <ifl:property>
                    <key>mappingType</key>
                    <value>{mapping_type}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:callActivity>'''

    def operation_mapping_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Operation Mapping component"""
        return self.message_mapping_template(id, name, config, incoming_flows, outgoing_flows)

    def xslt_mapping_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for XSLT Mapping component"""
        properties_xml = self._generate_property_xml(config, skip_keys=['mappinguri', 'mappingname', 'mappingpath', 'resource', 'xsltFilename'])

        mapping_uri = config.get("mappinguri", config.get("mappingUri", ""))
        mapping_name = config.get("mappingname", config.get("mappingName", name))
        mapping_path = config.get("mappingpath", config.get("mappingPath", ""))
        resource = config.get("resource", "")
        xslt_filename = config.get("xsltFilename", "")

        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>XSLTMapping</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::XsltMapping/version::1.1.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>mappinguri</key>
                    <value>{mapping_uri}</value>
                </ifl:property>
                <ifl:property>
                    <key>mappingname</key>
                    <value>{mapping_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>mappingpath</key>
                    <value>{mapping_path}</value>
                </ifl:property>
                <ifl:property>
                    <key>resource</key>
                    <value>{resource}</value>
                </ifl:property>
                <ifl:property>
                    <key>xsltFilename</key>
                    <value>{xslt_filename}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:callActivity>'''
    
    # ===== Request-Reply Template =====
    
    def request_reply_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Request-Reply (ExternalCall) component"""
        properties_xml = self._generate_property_xml(config)

        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>ExternalCall</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::ExternalCall/version::1.0.4")}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:serviceTask id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:serviceTask>'''

    # ===== Additional Component Templates =====
    # Note: The following templates use the generic_component_template method
    # but have specific implementations for components that need special handling

    def id_mapping_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for ID Mapping component"""
        return self.generic_component_template(id, name, "IDMapping", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def filter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Filter component"""
        return self.generic_component_template(id, name, "Filter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def message_digest_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Message Digest component"""
        # Ensure required properties specific to Message Digest service task
        component_version = config.get("componentVersion", "1.0")
        activity_type = config.get("activityType", "MessageDigest")
        cmd_variant_uri = config.get("cmdVariantUri", f"ctype::FlowstepVariant/cname::MessageDigest/version::{component_version}.0")

        # Exclude keys that are already represented in required properties
        skip_keys_for_props = ['componentVersion', 'activityType', 'cmdVariantUri']
        properties_xml_filtered = self._generate_property_xml(config, skip_keys=skip_keys_for_props)

        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{component_version}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>{activity_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{cmd_variant_uri}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentType</key>
                    <value>ServiceTask</value>
                </ifl:property>
{properties_xml_filtered}'''

        # Generate incoming/outgoing flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:serviceTask id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:serviceTask>'''

    def xml_modifier_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for XML Modifier component"""
        # Extract modifications array to convert to XML table
        modifications = config.get("modifications", [])
        modifications_table_xml = self._create_modifications_table_xml(modifications) if modifications else ""

        # Use modificationsTable from config if provided, otherwise use generated table
        modifications_table = config.get("modificationsTable", modifications_table_xml)

        # Skip modifications array (handled as table) and use modificationsTable property
        skip_keys = ['modifications']
        properties_xml = self._generate_property_xml(config, skip_keys=skip_keys)

        # Ensure modificationsTable is included
        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>{config.get("activityType", "XMLModifier")}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::XMLModifier/version::1.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>modificationsTable</key>
                    <value>{modifications_table if modifications_table else ""}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:callActivity>'''

    def poll_enrich_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Poll Enrich component"""
        return self.generic_component_template(id, name, "PollEnrich", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def send_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Send component"""
        return self.generic_component_template(id, name, "Send", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def process_call_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Process Call component"""
        return self.generic_component_template(id, name, "ProcessCallElement", config, "callActivity", incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def idempotent_process_call_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Idempotent Process Call component"""
        return self.generic_component_template(id, name, "IdempotentProcessCall", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def looping_process_call_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Looping Process Call component"""
        return self.generic_component_template(id, name, "LoopingProcessCall", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def aggregator_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Aggregator component"""
        return self.generic_component_template(id, name, "Aggregator", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def gather_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Gather component"""
        return self.generic_component_template(id, name, "Gather", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def join_gateway_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Join Gateway component"""
        return self.generic_component_template(id, name, "JoinGateway", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def parallel_multicast_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Parallel Multicast component"""
        return self.generic_component_template(id, name, "ParallelMulticast", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def sequential_multicast_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Sequential Multicast component"""
        return self.generic_component_template(id, name, "SequentialMulticast", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def multicast_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Multicast component"""
        return self.parallel_multicast_template(id, name, config, incoming_flows, outgoing_flows)
    
    # ===== Converter Templates =====

    def csv_to_xml_converter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """
        Template for CSV to XML Converter (dedicated, aligned with SAP IS and test309.iflw)
        
        Note: activityType is always set to "CsvToXmlConverter" for this component type,
        regardless of the value in the config dictionary. This ensures correct SAP IS behavior.
        """
        # Extract well-known fields; do not hardcode example defaults to keep placeholders flexible
        field_separator = config.get("Field_Separator_in_CSV", "")
        ignore_first_line = config.get("ignoreFirstLineAsHeader", "")
        record_identifier = config.get("Record_Identifier_in_CSV", "")
        xsd_path = config.get("XML_Schema_File_Path", "")
        xpath_field_location = config.get("XPath_Field_Location", "")
        header_mapping = config.get("headerMapping", "")

        # Exclude keys covered by required properties and template-specific fields
        skip_keys = [
            "Field_Separator_in_CSV",
            "ignoreFirstLineAsHeader",
            "Record_Identifier_in_CSV",
            "XML_Schema_File_Path",
            "XPath_Field_Location",
            "headerMapping",
            "componentVersion",
            "activityType",
            "cmdVariantUri",
        ]
        properties_xml = self._generate_property_xml(config, skip_keys=skip_keys)

        # Required properties as per SAP IS CsvToXmlConverter
        required_props = f'''                <ifl:property>
                    <key>Field_Separator_in_CSV</key>
                    <value>{self._format_property_value(field_separator)}</value>
                </ifl:property>
                <ifl:property>
                    <key>ignoreFirstLineAsHeader</key>
                    <value>{ignore_first_line}</value>
                </ifl:property>
                <ifl:property>
                    <key>XML_Schema_File_Path</key>
                    <value>{self._format_property_value(xsd_path)}</value>
                </ifl:property>
                <ifl:property>
                    <key>headerMapping</key>
                    <value>{self._format_property_value(header_mapping)}</value>
                </ifl:property>
                <ifl:property>
                    <key>Record_Identifier_in_CSV</key>
                    <value>{self._format_property_value(record_identifier)}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.4")}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>CsvToXmlConverter</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::CsvToXmlConverter/version::1.4.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>XPath_Field_Location</key>
                    <value>{self._format_property_value(xpath_field_location)}</value>
                </ifl:property>
{properties_xml}'''

        # Build incoming/outgoing flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        # Return callActivity element consistent with other templates
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:callActivity>'''

    def edi_to_xml_converter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for EDI to XML Converter"""
        return self.generic_component_template(id, name, "EDIToXMLConverter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def json_to_xml_converter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for JSON to XML Converter"""
        return self.generic_component_template(id, name, "JsonToXmlConverter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def xml_to_csv_converter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for XML to CSV Converter"""
        return self.generic_component_template(id, name, "XMLToCSVConverter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def xml_to_edi_converter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for XML to EDI Converter"""
        return self.generic_component_template(id, name, "XMLToEDIConverter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def xml_to_json_converter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for XML to JSON Converter"""
        return self.generic_component_template(id, name, "XmlToJsonConverter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    # ===== Encoder/Decoder Templates =====

    def base64_decoder_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Base64 Decoder"""
        return self.generic_component_template(id, name, "Base64Decoder", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def gzip_decompressor_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for GZIP Decompressor"""
        return self.generic_component_template(id, name, "GzipDecompressor", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def mime_multipart_decoder_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for MIME Multipart Decoder"""
        return self.generic_component_template(id, name, "MimeMultipartDecoder", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def zip_decompressor_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for ZIP Decompressor"""
        return self.generic_component_template(id, name, "ZipDecompressor", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def edi_extractor_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for EDI Extractor"""
        return self.generic_component_template(id, name, "EDIExtractor", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def base64_encoder_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Base64 Encoder"""
        return self.generic_component_template(id, name, "Base64Encoder", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def gzip_compressor_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for GZIP Compressor"""
        return self.generic_component_template(id, name, "GzipCompressor", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def mime_multipart_encoder_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for MIME Multipart Encoder"""
        return self.generic_component_template(id, name, "MimeMultipartEncoder", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def zip_compressor_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for ZIP Compressor"""
        return self.generic_component_template(id, name, "ZipCompressor", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    # ===== Splitter Templates =====

    def edi_splitter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for EDI Splitter"""
        return self.generic_component_template(id, name, "EDISplitter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def general_splitter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for General Splitter"""
        return self.generic_component_template(id, name, "Splitter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def idoc_splitter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for IDoc Splitter"""
        return self.generic_component_template(id, name, "IDocSplitter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def iterating_splitter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Iterating Splitter"""
        return self.generic_component_template(id, name, "IteratingSplitter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def pkcs7_splitter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for PKCS7 Splitter"""
        return self.generic_component_template(id, name, "PKCS7Splitter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def tar_splitter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for TAR Splitter"""
        return self.generic_component_template(id, name, "TarSplitter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def zip_splitter_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for ZIP Splitter"""
        return self.generic_component_template(id, name, "ZipSplitter", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    # ===== Security Templates =====

    def pgp_decryptor_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for PGP Decryptor"""
        return self.generic_component_template(id, name, "PGPDecryptor", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def pkcs7_decryptor_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for PKCS7 Decryptor"""
        return self.generic_component_template(id, name, "PKCS7Decryptor", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def pgp_encryptor_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for PGP Encryptor"""
        return self.generic_component_template(id, name, "PGPEncryptor", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def pkcs7_encryptor_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for PKCS7 Encryptor"""
        return self.generic_component_template(id, name, "PKCS7Encryptor", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def pkcs7_signer_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for PKCS7 Signer"""
        return self.generic_component_template(id, name, "PKCS7Signer", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def simple_signer_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Simple Signer"""
        return self.generic_component_template(id, name, "SimpleSigner", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def xml_digital_signer_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for XML Digital Signer"""
        return self.generic_component_template(id, name, "XMLDigitalSigner", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def pkcs7_signature_verifier_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for PKCS7 Signature Verifier"""
        return self.generic_component_template(id, name, "PKCS7SignatureVerifier", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def xml_signature_verifier_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for XML Signature Verifier"""
        return self.generic_component_template(id, name, "XMLSignatureVerifier", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    # ===== Data Store Templates =====

    def data_store_delete_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Data Store Delete"""
        return self.generic_component_template(id, name, "DataStoreDelete", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def data_store_get_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Data Store Get"""
        return self.generic_component_template(id, name, "DataStoreGet", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def data_store_select_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Data Store Select"""
        return self.generic_component_template(id, name, "DataStoreSelect", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def data_store_write_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Data Store Write"""
        return self.generic_component_template(id, name, "DataStoreWrite", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    # ===== Variable Templates =====

    def persist_message_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Persist Message"""
        return self.generic_component_template(id, name, "PersistMessage", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)
    
    def write_variables_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for Write Variables - handles variables array"""
        # Extract variables array and convert to XML table format
        variables = config.get("variables", [])
        variables_table_xml = self._create_property_table_xml(variables) if variables else ""

        # Skip variables array (handled as table)
        skip_keys = ['variables']
        properties_xml = self._generate_property_xml(config, skip_keys=skip_keys)

        # Variables table is typically stored in a property or encoded
        # SAP IS may expect this as a specific property - using variablesTable
        variables_table = config.get("variablesTable", variables_table_xml)

        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>{config.get("activityType", "WriteVariables")}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowstepVariant/cname::WriteVariables/version::1.1.0")}</value>
                </ifl:property>
                <ifl:property>
                    <key>variablesTable</key>
                    <value>{variables_table if variables_table else ""}</value>
                </ifl:property>
{properties_xml}'''

        # Generate flow XML
        incoming_xml = ""
        if incoming_flows:
            for flow_id in incoming_flows:
                incoming_xml += f"\n            <bpmn2:incoming>{flow_id}</bpmn2:incoming>"

        outgoing_xml = ""
        if outgoing_flows:
            for flow_id in outgoing_flows:
                outgoing_xml += f"\n            <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>"

        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>{incoming_xml}{outgoing_xml}
        </bpmn2:callActivity>'''

    # ===== Validator Templates =====

    def edi_validator_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for EDI Validator"""
        return self.generic_component_template(id, name, "EDIValidator", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)

    def xml_validator_template(self, id: str, name: str, config: Dict[str, Any], incoming_flows: Optional[List[str]] = None, outgoing_flows: Optional[List[str]] = None):
        """Template for XML Validator"""
        return self.generic_component_template(id, name, "XMLValidator", config, incoming_flows=incoming_flows, outgoing_flows=outgoing_flows)
    
    # ===== Process Templates =====
    
    def integration_process_template(self, id: str, name: str, config: Dict[str, Any]):
        """Template for Integration Process"""
        properties_xml = self._generate_property_xml(config)
        
        required_props = f'''                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.2")}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowElementVariant/cname::IntegrationProcess/version::1.2.1")}</value>
                </ifl:property>
{properties_xml}'''
        
        return f'''<bpmn2:process id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>
            {{process_content}}
        </bpmn2:process>'''
    
    def exception_subprocess_template(self, id: str, name: str, config: Dict[str, Any]):
        """Template for Exception Subprocess"""
        return self.generic_component_template(id, name, "ExceptionSubprocess", config)
    
    def local_integration_process_template(self, id: str, name: str, config: Dict[str, Any]):
        """Template for Local Integration Process"""
        properties_xml = self._generate_property_xml(config, skip_keys=['process_id', 'process_name', 'processType'])
        
        process_id = config.get("process_id", config.get("processId", id))
        process_name = config.get("process_name", config.get("processName", name))
        process_type = config.get("processType", "directCall")
        
        required_props = f'''                <ifl:property>
                    <key>processId</key>
                    <value>{process_id}</value>
                </ifl:property>
                <ifl:property>
                    <key>processName</key>
                    <value>{process_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>processType</key>
                    <value>{process_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>{config.get("componentVersion", "1.1")}</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>{config.get("cmdVariantUri", "ctype::FlowElementVariant/cname::LocalIntegrationProcess/version::1.1.3")}</value>
                </ifl:property>
{properties_xml}'''
        
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
{required_props}
            </bpmn2:extensionElements>
        </bpmn2:callActivity>'''
    
    def receiver_template(self, id: str, name: str, config: Dict[str, Any]):
        """Template for Receiver endpoint"""
        return self.participant_template(id, name, "EndpointRecevier", "false", config)
    
    def sender_template(self, id: str, name: str, config: Dict[str, Any]):
        """Template for Sender endpoint"""
        enable_auth = config.get("enableBasicAuthentication", "false")
        return self.participant_template(id, name, "EndpointSender", enable_auth, config)

