"""
Enhanced JSON to SAP Integration Suite iFlow Converter
Converts JSON blueprint to SAP-compatible iFlow XML with proper BPMN structure
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import the schema validator
try:
    from .json_schema_validator import validate_iflow_json, ValidationResult
except ImportError:
    # Fallback if validator not available
    def validate_iflow_json(json_data):
        class DummyResult:
            def __init__(self):
                self.is_valid = True
                self.errors = []
                self.warnings = []
        return DummyResult()

class EnhancedJSONToIFlowConverter:
    """Converts JSON blueprint to SAP Integration Suite iFlow XML"""
    
    def __init__(self):
        self.component_positions = {}
        self.sequence_flows = []
        self.current_x_position = 150
        self.current_y_position = 150
        
    def convert(self, json_blueprint: str, output_path: str = None) -> str:
        """
        Convert JSON blueprint to SAP iFlow XML
        
        Args:
            json_blueprint: JSON string or file path
            output_path: Optional output file path
            
        Returns:
            Generated iFlow XML content
        """
        try:
            # Parse JSON
            if isinstance(json_blueprint, str):
                if json_blueprint.strip().startswith('{'):
                    # Direct JSON string
                    data = json.loads(json_blueprint)
                else:
                    # File path
                    with open(json_blueprint, 'r', encoding='utf-8') as f:
                        data = json.load(f)
            else:
                data = json_blueprint
                
            # 🔍 CRITICAL: Validate JSON against our schema
            validation_result = validate_iflow_json(data)
            
            if not validation_result.is_valid:
                error_msg = "JSON validation failed:\n" + "\n".join(validation_result.errors)
                if hasattr(validation_result, 'fixed_json') and validation_result.fixed_json:
                    print("⚠️  Attempting to auto-fix JSON issues...")
                    data = validation_result.fixed_json
                    # Re-validate fixed JSON
                    revalidation = validate_iflow_json(data)
                    if not revalidation.is_valid:
                        raise ValueError(f"Auto-fix failed. {error_msg}")
                    else:
                        print("✅ JSON auto-fixed successfully")
                else:
                    raise ValueError(error_msg)
            
            if hasattr(validation_result, 'warnings') and validation_result.warnings:
                print("⚠️  Validation warnings:")
                for warning in validation_result.warnings:
                    print(f"  - {warning}")
            
            # Generate iFlow XML
            iflow_xml = self._generate_iflow_xml(data)
            
            # Save to file if output path specified
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(iflow_xml)
                print(f"✅ iFlow saved to: {output_file}")
            
            return iflow_xml
            
        except Exception as e:
            raise Exception(f"Failed to convert JSON to iFlow: {str(e)}")

    def _generate_iflow_xml(self, data: Dict[str, Any]) -> str:
        """Generate the complete iFlow XML with proper SAP structure"""
        # Reset positions for new generation
        self.component_positions = {}
        self.sequence_flows = []
        self.current_x_position = 300
        self.current_y_position = 150
        
        # Handle both direct endpoints and nested components.endpoints structure
        endpoints = data.get("endpoints", [])
        if not endpoints and "components" in data:
            endpoints = data["components"].get("endpoints", [])
        
        # Generate collaboration section
        collaboration_xml = self._generate_collaboration_section()
        
        # Generate process section
        process_xml = self._generate_process_section(endpoints)
        
        # Generate BPMN diagram section
        diagram_xml = self._generate_bpmn_diagram_section()
        
        # Combine all sections
        complete_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL" 
                   xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" 
                   xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" 
                   xmlns:di="http://www.omg.org/spec/DD/20100524/DI" 
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                                       xmlns:ifl="http:///com.sap.ifl.model/Ifl.xsd" 
                   id="Definitions_1" 
                   targetNamespace="http://bpmn.io/schema/bpmn" 
                   exporter="bpmn-js (https://demo.bpmn.io)" 
                   exporterVersion="9.0.3">
{collaboration_xml}
{process_xml}
{diagram_xml}
</bpmn2:definitions>'''
        
        return complete_xml

    def _generate_collaboration_section(self) -> str:
        """Generate the collaboration section for SAP Integration Suite"""
        return '''  <bpmn2:collaboration id="Collaboration_1" name="Simple Test Integration">
    <bpmn2:participant id="Process_Participant" name="Integration Process" processRef="Process_1"/>
    <bpmn2:extensionElements>
      <ifl:property>
        <key>componentVersion</key>
        <value>1.0</value>
      </ifl:property>
      <ifl:property>
        <key>cmdVariantUri</key>
        <value>ctype::IFlowVariant/cname::IFlowConfiguration/version::1.0.0</value>
      </ifl:property>
    </bpmn2:extensionElements>
  </bpmn2:collaboration>'''

    def _generate_process_section(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate the process section with components and flows"""
        # Start with process and start/end events
        process_xml = '''  <bpmn2:process id="Process_1" isExecutable="true">
    <bpmn2:startEvent id="StartEvent_2" name="Start">
      <bpmn2:extensionElements>
        <ifl:property>
          <key>componentType</key>
          <value>StartEvent</value>
        </ifl:property>
        <ifl:property>
          <key>componentVersion</key>
          <value>1.0</value>
        </ifl:property>
      </bpmn2:extensionElements>
      <bpmn2:messageEventDefinition/>
    </bpmn2:startEvent>
    <bpmn2:endEvent id="EndEvent_2" name="End">
      <bpmn2:extensionElements>
        <ifl:property>
          <key>componentType</key>
          <value>EndEvent</value>
        </ifl:property>
        <ifl:property>
          <key>componentVersion</key>
          <value>1.0</value>
        </ifl:property>
      </bpmn2:extensionElements>
      <bpmn2:messageEventDefinition/>
    </bpmn2:endEvent>'''
        
        # Process each endpoint
        for endpoint in endpoints:
            endpoint_xml = self._process_endpoint(endpoint)
            process_xml += endpoint_xml
        
        # Close process section
        process_xml += '''
  </bpmn2:process>'''
        
        return process_xml

    def _generate_bpmn_diagram_section(self) -> str:
        """Generate the BPMN diagram section with shapes and edges"""
        # Generate BPMN shapes for all components
        shapes_xml = []
        edges_xml = []
        
        # Add Integration Process participant shape (the big container)
        shapes_xml.append('''      <bpmndi:BPMNShape bpmnElement="Process_Participant" id="BPMNShape_Process_Participant">
        <dc:Bounds height="300.0" width="1200.0" x="50" y="50"/>
        <bpmndi:BPMNLabel>
          <dc:Bounds height="14.0" width="200.0" x="50" y="30"/>
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>''')
        
        # Add start and end event shapes
        shapes_xml.append('''      <bpmndi:BPMNShape bpmnElement="StartEvent_2" id="BPMNShape_StartEvent_2">
        <dc:Bounds height="32.0" width="32.0" x="100" y="100"/>
        <bpmndi:BPMNLabel>
          <dc:Bounds height="14.0" width="32.0" x="100" y="140"/>
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>''')
        
        shapes_xml.append('''      <bpmndi:BPMNShape bpmnElement="EndEvent_2" id="BPMNShape_EndEvent_2">
        <dc:Bounds height="32.0" width="32.0" x="1200" y="100"/>
        <bpmndi:BPMNLabel>
          <dc:Bounds height="14.0" width="32.0" x="1200" y="140"/>
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>''')
        
        # Add shapes for all components
        for component_id, position in self.component_positions.items():
            shapes_xml.append(f'''      <bpmndi:BPMNShape bpmnElement="{component_id}" id="BPMNShape_{component_id}">
        <dc:Bounds height="80.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
        <bpmndi:BPMNLabel>
          <dc:Bounds height="14.0" width="100.0" x="{position['x']}" y="{position['y'] + 90}"/>
        </bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>''')
        
        # Add edges for all sequence flows
        for flow in self.sequence_flows:
            source_shape = f"BPMNShape_{flow['source_ref']}"
            target_shape = f"BPMNShape_{flow['target_ref']}"
            
            # Calculate waypoints for better visual flow
            source_x = self.component_positions.get(flow['source_ref'], {}).get('x', 100)
            source_y = self.component_positions.get(flow['source_ref'], {}).get('y', 100)
            target_x = self.component_positions.get(flow['target_ref'], {}).get('x', 200)
            target_y = self.component_positions.get(flow['target_ref'], {}).get('y', 100)
            
            # Adjust coordinates for start/end events
            if flow['source_ref'] == 'StartEvent_2':
                source_x = 132  # StartEvent_2 center
                source_y = 116  # StartEvent_2 center
            if flow['target_ref'] == 'EndEvent_2':
                target_x = 1168  # EndEvent_2 center
                target_y = 116  # EndEvent_2 center
            
            edges_xml.append(f'''      <bpmndi:BPMNEdge bpmnElement="{flow['id']}" id="BPMNEdge_{flow['id']}" sourceElement="{source_shape}" targetElement="{target_shape}">
        <di:waypoint x="{source_x + 50}" y="{source_y + 40}"/>
        <di:waypoint x="{target_x}" y="{target_y + 40}"/>
      </bpmndi:BPMNEdge>''')
        
        # Combine all parts
        shapes_str = '\n'.join(shapes_xml)
        edges_str = '\n'.join(edges_xml)
        
        return f'''  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane bpmnElement="Collaboration_1" id="BPMNPlane_1">
{shapes_str}
{edges_str}
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>'''

    def _process_endpoint(self, endpoint: Dict[str, Any]) -> str:
        """Process a single endpoint and generate its XML"""
        endpoint_id = endpoint.get("id", "default_endpoint")
        endpoint_name = endpoint.get("name", "Default Endpoint")
        
        # Process components
        components_xml = self._process_endpoint_components(endpoint)
        
        # Process sequence flows
        flows_xml = self._process_json_sequence_flows(endpoint)
        
        # Add flow references to all components
        self._add_flow_references_to_components()
        
        return f"""
    <!-- Endpoint: {endpoint_name} -->
{components_xml}
{flows_xml}"""

    def _process_endpoint_components(self, endpoint: Dict[str, Any]) -> str:
        """Process all components in an endpoint"""
        components = endpoint.get("components", [])
        if not components:
            return ""
        
        components_xml = []
        
        for i, component in enumerate(components):
            # Calculate position
            position = {
                "x": self.current_x_position + (i * 200),
                "y": self.current_y_position
            }
            
            # Create component
            component_xml = self._create_component(component, position)
            components_xml.append(component_xml)
            
            # Store position for sequence flows
            self.component_positions[component["id"]] = position
        
        # Update Y position for next endpoint
        self.current_y_position += 200
        
        return "\n".join(components_xml)

    def _create_component(self, component: Dict[str, Any], position: Dict[str, int]) -> str:
        """Create a component based on its type"""
        component_type = component.get("type", "")
        component_id = component.get("id", "")
        component_name = component.get("name", "")
        config = component.get("config", {})
        
        # 🔍 SMART COMPONENT TYPE DETECTION
        if component_type == "startEvent":
            # Start event - skip as it's already in the core structure
            return ""
        elif component_type == "endEvent":
            # End event - skip as it's already in the core structure
            return ""
        elif component_type in ["content_modifier", "modifier"]:
            # Determine if this should be Content Enricher or Content Modifier
            actual_type = self._determine_actual_component_type(component_type, config)
            if actual_type == "Content_Enricher":
                return self._create_content_enricher(component_id, component_name, config, position)
            else:
                return self._create_content_modifier(component_id, component_name, config, position)
        elif component_type == "enricher":
            # Direct enricher type - treat as content enricher
            return self._create_content_enricher(component_id, component_name, config, position)
        elif component_type == "script":
            return self._create_script(component_id, component_name, config, position)
        elif component_type == "groovy_script":
            # Groovy script type - treat as script
            return self._create_script(component_id, component_name, config, position)
        elif component_type == "gateway":
            return self._create_gateway(component_id, component_name, position)
        elif component_type in ["join", "parallel_join", "parallelGateway"]:
            return self._create_join_gateway(component_id, component_name, position)
        elif component_type == "message_mapping":
            return self._create_message_mapping(component_id, component_name, config, position)
        elif component_type == "subprocess":
            return self._create_subprocess(component_id, component_name, position)
        elif component_type == "exception_subprocess":
            return self._create_exception_subprocess(component_id, component_name, position)
        elif component_type == "request_reply":
            # Check if we have SAP-specific component type information
            sap_component_type = component.get("sap_component_type", "")
            if sap_component_type == "SuccessFactors":
                return self._create_successfactors_component(component_id, component_name, component, position)
            elif sap_component_type == "SFTP":
                return self._create_sftp_component(component_id, component_name, component, position)
            elif sap_component_type == "HTTP":
                return self._create_http_component(component_id, component_name, component, position)
            else:
                return self._create_service_task(component_id, component_name, position)
        elif component_type == "odata":
            return self._create_service_task(component_id, component_name, position)
        elif component_type == "sftp":
            return self._create_service_task(component_id, component_name, position)
        else:
            # Default to service task for unknown types
            return self._create_service_task(component_id, component_name, position)

    def _determine_actual_component_type(self, declared_type: str, config: Dict[str, Any]) -> str:
        """
        Determine the actual SAP component type based on configuration content.
        This fixes the issue where 'content_modifier' with headers should be 'Content_Enricher'.
        """
        if declared_type in ["content_modifier", "content_modifier_step"]:
            if "headers" in config:
                return "Content_Enricher"
            elif "body" in config or "bodyContent" in config:
                return "ContentModifier"
            else:
                return "ContentModifier"
        return declared_type

    def _create_content_enricher(self, id: str, name: str, config: Dict[str, Any], position: Dict[str, int]) -> Dict[str, str]:
        """Create a content enricher for header operations."""
        header_properties = []
        headers = config.get("headers", {})
        
        for i, (header_name, header_value) in enumerate(headers.items(), 1):
            header_properties.extend([
                f'        <ifl:property>',
                f'            <key>headerName{i}</key>',
                f'            <value>{header_name}</value>',
                f'        </ifl:property>',
                f'        <ifl:property>',
                f'            <key>headerValue{i}</key>',
                f'            <value>{header_value}</value>',
                f'        </ifl:property>',
                f'        <ifl:property>',
                f'            <key>headerAction{i}</key>',
                f'            <value>Create</value>',
                f'        </ifl:property>'
            ])
        
        header_xml = '\n'.join(header_properties) if header_properties else ''
    
        definition = f'''    <bpmn2:callActivity id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>EnrichContentStep</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
          <ifl:property>
              <key>activityType</key>
              <value>Enricher</value>
          </ifl:property>
          <ifl:property>
              <key>cmdVariantUri</key>
              <value>ctype::FlowstepVariant/cname::Enricher/version::1.0.0</value>
          </ifl:property>
{header_xml}
      </bpmn2:extensionElements>
    </bpmn2:callActivity>'''
        
        shape = f''''''
        
        return definition

    def _create_content_modifier(self, id: str, name: str, config: Dict[str, Any], position: Dict[str, int]) -> str:
        """Create a content modifier for body transformations"""
        body_type = config.get("body_type", "expression")
        body_content = config.get("body_content", "${body}")
        
        return f'''    <bpmn2:callActivity id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>ContentModifier</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
          <ifl:property>
              <key>bodyType</key>
              <value>{body_type}</value>
          </ifl:property>
          <ifl:property>
              <key>bodyContent</key>
              <value><![CDATA[{body_content}]]></value>
          </ifl:property>
          <ifl:property>
              <key>activityType</key>
              <value>ContentModifier</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:callActivity>'''

    def _create_script(self, id: str, name: str, config: Dict[str, Any], position: Dict[str, int]) -> str:
        """Create a script component with proper SAP Integration Suite script properties"""
        # Extract script properties from config with sensible defaults
        script_function = config.get("script_function", "processData")
        script_bundle_id = config.get("script_bundle_id", "com.company.integration.scripts")
        script_collection = config.get("script_collection", "groovy")
        resource_name = config.get("resource_name", name)  # Use component name as default resource name
        script_content = config.get("script", "log.info('Script executed'); return message;")
        
        return f'''    <bpmn2:callActivity id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>scriptFunction</key>
              <value>{script_function}</value>
          </ifl:property>
          <ifl:property>
              <key>scriptBundleId</key>
              <value>{script_bundle_id}</value>
          </ifl:property>
          <ifl:property>
              <key>scriptCollection</key>
              <value>{script_collection}</value>
          </ifl:property>
          <ifl:property>
              <key>resourceName</key>
              <value>{resource_name}</value>
          </ifl:property>
          <ifl:property>
              <key>activityType</key>
              <value>Script</value>
          </ifl:property>
          <ifl:property>
              <key>script</key>
              <value><![CDATA[{script_content}]]></value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:callActivity>'''

    def _create_gateway(self, id: str, name: str, position: Dict[str, int]) -> str:
        """Create a gateway component"""
        return f'''    <bpmn2:exclusiveGateway id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>ExclusiveGateway</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
          <ifl:property>
              <key>throwException</key>
              <value>false</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:exclusiveGateway>'''

    def _create_join_gateway(self, id: str, name: str, position: Dict[str, int]) -> str:
        """Create a Join (Parallel Gateway) component per SAP IS."""
        return f'''    <bpmn2:parallelGateway id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>activityType</key>
              <value>Join</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
          <ifl:property>
              <key>cmdVariantUri</key>
              <value>ctype::FlowstepVariant/cname::Join/version::1.0.0</value>
          </ifl:property>
          <ifl:property>
              <key>subActivityType</key>
              <value>parallel</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:parallelGateway>'''

    def _create_message_mapping(self, id: str, name: str, config: Dict[str, Any], position: Dict[str, int]) -> str:
        """Create a message mapping component"""
        mapping_name = config.get("mapping_name", "DefaultMapping")
        source_schema = config.get("source_schema", "Source.xsd")
        target_schema = config.get("target_schema", "Target.xsd")
        
        return f'''    <bpmn2:callActivity id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>MessageMapping</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
          <ifl:property>
              <key>mappingName</key>
              <value>{mapping_name}</value>
          </ifl:property>
          <ifl:property>
              <key>sourceSchema</key>
              <value>{source_schema}</value>
          </ifl:property>
          <ifl:property>
              <key>targetSchema</key>
              <value>{target_schema}</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:callActivity>'''

    def _create_subprocess(self, id: str, name: str, position: Dict[str, int]) -> str:
        """Create a subprocess component"""
        return f'''    <bpmn2:subProcess id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>Subprocess</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:subProcess>'''

    def _create_exception_subprocess(self, id: str, name: str, position: Dict[str, int]) -> str:
        """Create an exception subprocess component"""
        return f'''    <bpmn2:subProcess id="{id}" name="{name}" triggeredByEvent="true">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>ExceptionSubprocess</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:subProcess>'''

    def _create_service_task(self, id: str, name: str, position: Dict[str, int]) -> str:
        """Create a service task component"""
        return f'''    <bpmn2:serviceTask id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>ServiceTask</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
          <ifl:property>
              <key>activityType</key>
              <value>ExternalCall</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:serviceTask>'''

    def _create_successfactors_component(self, id: str, name: str, component: Dict[str, Any], position: Dict[str, int]) -> str:
        """Create a SuccessFactors component with proper SAP Integration Suite configuration"""
        endpoint_path = component.get("sap_endpoint_path", "/odata/v2/CompoundEmployee")
        operation = component.get("sap_operation", "get")
        
        return f'''    <bpmn2:serviceTask id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>SuccessFactors</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.11</value>
          </ifl:property>
          <ifl:property>
              <key>activityType</key>
              <value>ExternalCall</value>
          </ifl:property>
          <ifl:property>
              <key>address</key>
              <value>{endpoint_path}</value>
          </ifl:property>
          <ifl:property>
              <key>resourcePathForOdatav4</key>
              <value>{endpoint_path}</value>
          </ifl:property>
          <ifl:property>
              <key>operation</key>
              <value>{operation}</value>
          </ifl:property>
          <ifl:property>
              <key>MessageProtocol</key>
              <value>OData V4</value>
          </ifl:property>
          <ifl:property>
              <key>authenticationMethod</key>
              <value>OAuth2ClientCredentials</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:serviceTask>'''

    def _create_sftp_component(self, id: str, name: str, component: Dict[str, Any], position: Dict[str, int]) -> str:
        """Create an SFTP component with proper SAP Integration Suite configuration"""
        endpoint_path = component.get("sap_endpoint_path", "/incoming/employee-data/")
        operation = component.get("sap_operation", "put")
        
        return f'''    <bpmn2:serviceTask id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>SFTP</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
          <ifl:property>
              <key>activityType</key>
              <value>ExternalCall</value>
          </ifl:property>
          <ifl:property>
              <key>address</key>
              <value>{endpoint_path}</value>
          </ifl:property>
          <ifl:property>
              <key>operation</key>
              <value>{operation}</value>
          </ifl:property>
          <ifl:property>
              <key>MessageProtocol</key>
              <value>SFTP</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:serviceTask>'''

    def _create_http_component(self, id: str, name: str, component: Dict[str, Any], position: Dict[str, int]) -> str:
        """Create an HTTP component with proper SAP Integration Suite configuration"""
        endpoint_path = component.get("sap_endpoint_path", "/email/notification")
        operation = component.get("sap_operation", "post")
        
        return f'''    <bpmn2:serviceTask id="{id}" name="{name}">
      <bpmn2:extensionElements>
          <ifl:property>
              <key>componentType</key>
              <value>HTTP</value>
          </ifl:property>
          <ifl:property>
              <key>componentVersion</key>
              <value>1.0</value>
          </ifl:property>
          <ifl:property>
              <key>activityType</key>
              <value>ExternalCall</value>
          </ifl:property>
          <ifl:property>
              <key>address</key>
              <value>{endpoint_path}</value>
          </ifl:property>
          <ifl:property>
              <key>operation</key>
              <value>{operation}</value>
          </ifl:property>
          <ifl:property>
              <key>MessageProtocol</key>
              <value>HTTP</value>
          </ifl:property>
      </bpmn2:extensionElements>
    </bpmn2:serviceTask>'''

    def _process_json_sequence_flows(self, endpoint: Dict[str, Any]) -> str:
        """Process sequence flows defined in the JSON or auto-generate them"""
        sequence_flows = endpoint.get("sequence_flows", [])
        
        if not sequence_flows:
            # Auto-generate sequence flows based on component order
            sequence_flows = self._auto_generate_sequence_flows(endpoint)
        
        flows_xml = []
        
        for flow in sequence_flows:
            flow_id = flow.get("id", f"flow_{len(flows_xml)}")
            # accept both source/target and source_ref/target_ref
            source_ref = flow.get("source_ref", flow.get("source", ""))
            target_ref = flow.get("target_ref", flow.get("target", ""))
            condition = flow.get("condition")
            # Create sequence flow
            flow_xml = self._create_sequence_flow(flow_id, source_ref, target_ref, condition)
            flows_xml.append(flow_xml)
            
            # Store for flow references
            self.sequence_flows.append({
                "id": flow_id,
                "source_ref": source_ref,
                "target_ref": target_ref
            })
        
        return "\n".join(flows_xml)

    def _auto_generate_sequence_flows(self, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Auto-generate sequence flows based on component order"""
        components = endpoint.get("components", [])
        if len(components) < 2:
            return []
        
        flows = []
        
        # Start with the standard start event
        flows.append({
            "id": "flow_start_to_first",
            "source_ref": "StartEvent_2",
            "target_ref": components[0]["id"]
        })
        
        # Connect components in sequence
        for i in range(len(components) - 1):
            flows.append({
                "id": f"flow_{i}_to_{i+1}",
                "source_ref": components[i]["id"],
                "target_ref": components[i + 1]["id"]
            })
        
        # End with the standard end event
        flows.append({
            "id": "flow_last_to_end",
            "source_ref": components[-1]["id"],
            "target_ref": "EndEvent_2"
        })
        
        return flows

    def _create_sequence_flow(self, id: str, source_ref: str, target_ref: str, condition: str = None) -> str:
        """Create a sequence flow with optional condition"""
        if condition and condition != "default":
            return f'''    <bpmn2:sequenceFlow id="{id}" sourceRef="{source_ref}" targetRef="{target_ref}">
      <bpmn2:conditionExpression xsi:type="bpmn2:tFormalExpression">{condition}</bpmn2:conditionExpression>
    </bpmn2:sequenceFlow>'''
        else:
            return f'''    <bpmn2:sequenceFlow id="{id}" sourceRef="{source_ref}" targetRef="{target_ref}"/>'''

    def _add_flow_references_to_components(self):
        """Add incoming and outgoing flow references to all components"""
        # Build flow reference maps
        incoming_flows = {}
        outgoing_flows = {}
        
        for flow in self.sequence_flows:
            source = flow["source_ref"]
            target = flow["target_ref"]
            flow_id = flow["id"]
            
            # Add outgoing flow to source
            if source not in outgoing_flows:
                outgoing_flows[source] = []
            outgoing_flows[source].append(flow_id)
            
            # Add incoming flow to target
            if target not in incoming_flows:
                incoming_flows[target] = []
            incoming_flows[target].append(flow_id)
        
        # Add references to component XML (this would be implemented in the actual XML generation)
        # For now, we'll store this information for later use
        self.flow_references = {
            "incoming": incoming_flows,
            "outgoing": outgoing_flows
        }

    def _close_bpmn_structure(self) -> str:
        """Close the BPMN structure with complete BPMN diagram"""
        # Generate BPMN shapes for all components
        shapes_xml = []
        edges_xml = []
        
        # Add start and end event shapes
        shapes_xml.append('''''')
        
        shapes_xml.append('''''')
        
        # Add shapes for all components
        for component_id, position in self.component_positions.items():
            shapes_xml.append(f'''''')
        
        # Add edges for all sequence flows
        for flow in self.sequence_flows:
            source_shape = f"BPMNShape_{flow['source_ref']}"
            target_shape = f"BPMNShape_{flow['target_ref']}"
            
            # Calculate waypoints for better visual flow
            source_x = self.component_positions.get(flow['source_ref'], {}).get('x', 100)
            source_y = self.component_positions.get(flow['source_ref'], {}).get('y', 100)
            target_x = self.component_positions.get(flow['target_ref'], {}).get('x', 200)
            target_y = self.component_positions.get(flow['target_ref'], {}).get('y', 100)
            
            # Adjust coordinates for start/end events
            if flow['source_ref'] == 'StartEvent_2':
                source_x = 132  # StartEvent_2 center
                source_y = 116  # StartEvent_2 center
            if flow['target_ref'] == 'EndEvent_2':
                target_x = 1168  # EndEvent_2 center
                target_y = 116  # EndEvent_2 center
            
            edges_xml.append(f'''      <bpmndi:BPMNEdge bpmnElement="{flow['id']}" id="BPMNEdge_{flow['id']}" sourceElement="{source_shape}" targetElement="{target_shape}">
        <di:waypoint x="{source_x + 50}" y="{source_y + 40}"/>
        <di:waypoint x="{target_x}" y="{target_y + 40}"/>
      </bpmndi:BPMNEdge>''')
        
        # Combine all parts
        shapes_str = '\n'.join(shapes_xml)
        edges_str = '\n'.join(edges_xml)
        
        return f'''  </bpmn2:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane bpmnElement="Process_1" id="BPMNPlane_1">
{shapes_str}
{edges_str}
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn2:definitions>'''

    def _replace_placeholders(self, xml_content: str) -> str:
        """Replace any placeholders in the XML content"""
        # This method can be used to replace dynamic content
        return xml_content

# Convenience function for easy usage
def convert_json_to_iflow(json_blueprint: str, output_path: str = None) -> str:
    """
    Convert JSON blueprint to SAP iFlow XML
    
    Args:
        json_blueprint: JSON string or file path
        output_path: Optional output file path
        
    Returns:
        Generated iFlow XML content
    """
    converter = EnhancedJSONToIFlowConverter()
    return converter.convert(json_blueprint, output_path)