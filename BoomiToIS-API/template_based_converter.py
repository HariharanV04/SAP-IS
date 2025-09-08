#!/usr/bin/env python3
"""
Template-Based SAP Integration Suite iFlow Converter
Uses the working test_step_1 template as a base and builds upon it
"""

import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TemplateBasedIFlowConverter:
    """Converts JSON blueprint to SAP iFlow XML using working template as base"""
    
    def __init__(self):
        self.template_dir = Path("test_step_1")
        self.component_positions = {}
        self.sequence_flows = []
        
    def convert(self, json_blueprint: str, output_path: str = None) -> str:
        """Convert JSON blueprint to SAP iFlow XML using template base"""
        try:
            # Parse JSON
            if isinstance(json_blueprint, str):
                if json_blueprint.strip().startswith('{'):
                    data = json.loads(json_blueprint)
                else:
                    with open(json_blueprint, 'r', encoding='utf-8') as f:
                        data = json.loads(f.read())
            else:
                data = json_blueprint
            
            # Generate iFlow XML based on template
            iflow_xml = self._generate_iflow_from_template(data)
            
            # Apply post-generation sanitization
            try:
                from iflow_sanitizer import sanitize_iflow
                print("🧹 Applying post-generation sanitization...")
                iflow_xml = sanitize_iflow(iflow_xml)
            except ImportError:
                print("⚠️ Sanitizer not available, skipping post-generation cleanup")
            
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
    
    def _generate_iflow_from_template(self, data: Dict[str, Any]) -> str:
        """Generate iFlow XML using the working template as base"""
        
        # Get endpoints and components
        endpoints = data.get("endpoints", [])
        if not endpoints and "components" in data:
            endpoints = data["components"].get("endpoints", [])
        
        # Start with the working template structure
        template_xml = self._get_template_structure()
        
        # Add components to the process section
        components_xml = self._generate_components_section(endpoints)
        
        # Add sequence flows
        flows_xml = self._generate_sequence_flows_section(endpoints)
        
        # Add BPMN shapes for components
        shapes_xml = self._generate_bpmn_shapes_section(endpoints)
        
        # Insert components and flows into the template
        template_xml = self._insert_into_template(template_xml, components_xml, flows_xml, shapes_xml)
        
        return template_xml
    
    def _get_template_structure(self) -> str:
        """Get the base template structure from test_step_1"""
        template_file = self.template_dir / "src/main/resources/scenarioflows/integrationflow/Simple_Test_Step1.iflw"
        
        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return template_content
    
    def _generate_components_section(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate components section based on JSON"""
        components_xml = []
        
        for endpoint in endpoints:
            components = endpoint.get("components", [])
            for i, component in enumerate(components):
                component_xml = self._create_component_xml(component, i)
                components_xml.append(component_xml)
                
                # Store position for BPMN shapes
                self.component_positions[component["id"]] = {
                    "x": 300 + (i * 200),
                    "y": 150
                }
        
        return "\n".join(components_xml)
    
    def _create_component_xml(self, component: Dict[str, Any], index: int) -> str:
        """Create component XML based on type"""
        component_type = component.get("type", "")
        component_id = component.get("id", "")
        component_name = component.get("name", "")
        config = component.get("config", {})
        
        # Map component types to SAP component types
        sap_component_type = self._map_to_sap_component_type(component_type, config)
        
        # Create component XML
        component_xml = f'''    <bpmn2:serviceTask id="{component_id}" name="{component_name}">
      <bpmn2:extensionElements>
        <ifl:property>
          <key>componentType</key>
          <value>{sap_component_type}</value>
        </ifl:property>
        <ifl:property>
          <key>componentVersion</key>
          <value>1.0</value>
        </ifl:property>'''
        
        # Add component-specific properties
        if component_type == "enricher" and "headers" in config:
            headers = config.get("headers", {})
            for header_name, header_value in headers.items():
                component_xml += f'''
        <ifl:property>
          <key>headerName</key>
          <value>{header_name}</value>
        </ifl:property>
        <ifl:property>
          <key>headerValue</key>
          <value>{header_value}</value>
        </ifl:property>'''
        
        elif component_type == "script":
            script_content = config.get("script", "log.info('Script executed'); return message;")
            component_xml += f'''
        <ifl:property>
          <key>script</key>
          <value><![CDATA[{script_content}]]></value>
        </ifl:property>'''
        
        elif component_type == "request_reply":
            endpoint_path = config.get("endpoint_path", "/api/test")
            component_xml += f'''
        <ifl:property>
          <key>endpointPath</key>
          <value>{endpoint_path}</value>
        </ifl:property>'''
        
        component_xml += '''
      </bpmn2:extensionElements>
    </bpmn2:serviceTask>'''
        
        return component_xml
    
    def _map_to_sap_component_type(self, component_type: str, config: Dict[str, Any]) -> str:
        """Map component type to SAP component type"""
        if component_type == "enricher":
            return "ContentEnricher"
        elif component_type == "script":
            return "Script"
        elif component_type == "request_reply":
            return "RequestReply"
        elif component_type == "gateway":
            return "ExclusiveGateway"
        elif component_type == "content_modifier":
            if "headers" in config:
                return "ContentEnricher"
            else:
                return "ContentModifier"
        else:
            return "ServiceTask"
    
    def _generate_sequence_flows_section(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate sequence flows section"""
        flows_xml = []
        
        for endpoint in endpoints:
            components = endpoint.get("components", [])
            
            if len(components) == 0:
                # No components - direct flow from start to end
                flows_xml.append('    <bpmn2:sequenceFlow id="flow_start_to_end" sourceRef="StartEvent_2" targetRef="EndEvent_2"/>')
            elif len(components) == 1:
                # Single component
                flows_xml.append(f'    <bpmn2:sequenceFlow id="flow_start_to_first" sourceRef="StartEvent_2" targetRef="{components[0]["id"]}"/>')
                flows_xml.append(f'    <bpmn2:sequenceFlow id="flow_last_to_end" sourceRef="{components[0]["id"]}" targetRef="EndEvent_2"/>')
            else:
                # Multiple components
                flows_xml.append(f'    <bpmn2:sequenceFlow id="flow_start_to_first" sourceRef="StartEvent_2" targetRef="{components[0]["id"]}"/>')
                
                for i in range(len(components) - 1):
                    flows_xml.append(f'    <bpmn2:sequenceFlow id="flow_{i}_to_{i+1}" sourceRef="{components[i]["id"]}" targetRef="{components[i+1]["id"]}"/>')
                
                flows_xml.append(f'    <bpmn2:sequenceFlow id="flow_last_to_end" sourceRef="{components[-1]["id"]}" targetRef="EndEvent_2"/>')
        
        return "\n".join(flows_xml)
    
    def _generate_bpmn_shapes_section(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate BPMN shapes for components"""
        shapes_xml = []
        
        # Add StartEvent shape first
        shapes_xml.append('''      <bpmndi:BPMNShape bpmnElement="StartEvent_2" id="BPMNShape_StartEvent_2">
        <dc:Bounds height="32.0" width="32.0" x="100" y="100"/>
      </bpmndi:BPMNShape>''')
        
        # Add component shapes
        for endpoint in endpoints:
            components = endpoint.get("components", [])
            for i, component in enumerate(components):
                x = 300 + (i * 200)
                y = 150
                shapes_xml.append(f'''      <bpmndi:BPMNShape bpmnElement="{component["id"]}" id="BPMNShape_{component["id"]}">
        <dc:Bounds height="80.0" width="100.0" x="{x}" y="{y}" />
      </bpmndi:BPMNShape>''')
        
        # Add EndEvent shape last
        end_x = 300 + (len([c for ep in endpoints for c in ep.get("components", [])]) * 200)
        shapes_xml.append(f'''      <bpmndi:BPMNShape bpmnElement="EndEvent_2" id="BPMNShape_EndEvent_2">
        <dc:Bounds height="32.0" width="32.0" x="{end_x}" y="100"/>
      </bpmndi:BPMNShape>''')
        
        return "\n".join(shapes_xml)
    
    def _insert_into_template(self, template_xml: str, components_xml: str, flows_xml: str, shapes_xml: str) -> str:
        """Insert components, flows, and shapes into the template"""
        
        # First, clean up the template by removing existing components and flows
        template_xml = self._clean_template(template_xml)
        
        # Find insertion points in the template
        process_end_marker = "  </bpmn2:process>"
        bpmn_plane_start = '<bpmndi:BPMNPlane bpmnElement="Process_1" id="BPMNPlane_1">'
        
        # Insert components and flows before process end
        if components_xml or flows_xml:
            template_xml = template_xml.replace(
                process_end_marker,
                f"{components_xml}\n{flows_xml}\n{process_end_marker}"
            )
        
        # Insert BPMN shapes after plane start
        if shapes_xml:
            template_xml = template_xml.replace(
                bpmn_plane_start,
                f"{bpmn_plane_start}\n{shapes_xml}"
            )
        
        return template_xml
    
    def _clean_template(self, template_xml: str) -> str:
        """Clean up the template by removing existing components and flows"""
        
        import re
        
        # Remove all serviceTask elements except StartEvent and EndEvent
        template_xml = re.sub(
            r'    <bpmn2:serviceTask id="[^"]*"[^>]*>.*?</bpmn2:serviceTask>',
            '',
            template_xml,
            flags=re.DOTALL
        )
        
        # Remove ALL existing sequence flows (we'll regenerate them cleanly)
        template_xml = re.sub(
            r'    <bpmn2:sequenceFlow[^>]*>.*?</bpmn2:sequenceFlow>',
            '',
            template_xml,
            flags=re.DOTALL
        )
        
        # Remove existing BPMN shapes for components (keep StartEvent and EndEvent)
        template_xml = re.sub(
            r'      <bpmndi:BPMNShape bpmnElement="[^"]*"[^>]*>.*?</bpmndi:BPMNShape>',
            '',
            template_xml,
            flags=re.DOTALL
        )
        
        # Remove message flows (we'll regenerate these if needed)
        template_xml = re.sub(
            r'    <bpmn2:messageFlow[^>]*>.*?</bpmn2:messageFlow>',
            '',
            template_xml,
            flags=re.DOTALL
        )
        
        # Remove HTTP participant (we'll regenerate if needed)
        template_xml = re.sub(
            r'    <bpmn2:participant id="Participant_HTTP"[^>]*>',
            '',
            template_xml,
            flags=re.DOTALL
        )
        
        # Remove any BPMN shapes that got mixed into the process section
        template_xml = re.sub(
            r'    <bpmndi:BPMNShape[^>]*>.*?</bpmndi:BPMNShape>',
            '',
            template_xml,
            flags=re.DOTALL
        )
        
        # Additional cleanup: remove any remaining orphaned sequence flows
        template_xml = re.sub(
            r'    <bpmn2:sequenceFlow[^>]*/>',
            '',
            template_xml
        )
        
        # Clean up any empty lines
        template_xml = re.sub(r'\n\s*\n', '\n', template_xml)
        
        return template_xml
    
    def create_sap_package(self, json_blueprint: str, package_name: str = "Generated_Integration") -> str:
        """Create complete SAP package using template base"""
        
        # Generate iFlow XML
        iflow_xml = self.convert(json_blueprint)
        
        # Create output directory
        output_dir = Path(f"{package_name}_output")
        output_dir.mkdir(exist_ok=True)
        
        # Copy template files and modify as needed
        self._copy_template_files(output_dir, package_name)
        
        # Save modified iFlow
        iflow_file = output_dir / "src/main/resources/scenarioflows/integrationflow" / f"{package_name}.iflw"
        iflow_file.parent.mkdir(parents=True, exist_ok=True)
        with open(iflow_file, 'w', encoding='utf-8') as f:
            f.write(iflow_xml)
        
        # Create ZIP package
        zip_file = output_dir / f"{package_name}.zip"
        self._create_zip_package(output_dir, zip_file)
        
        print(f"✅ SAP package created: {zip_file}")
        return str(zip_file)
    
    def _copy_template_files(self, output_dir: Path, package_name: str):
        """Copy and modify template files"""
        import shutil
        
        # Copy template directory structure
        for item in self.template_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, output_dir)
            elif item.is_dir():
                shutil.copytree(item, output_dir / item.name, dirs_exist_ok=True)
        
        # Remove the original template iFlow file to avoid duplication
        original_iflow = output_dir / "src/main/resources/scenarioflows/integrationflow/Simple_Test_Step1.iflw"
        if original_iflow.exists():
            original_iflow.unlink()
            print(f"🗑️ Removed original template iFlow: {original_iflow}")
        
        # Modify .project file
        project_file = output_dir / ".project"
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace("test_step_1", package_name)
            with open(project_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Modify MANIFEST.MF
        manifest_file = output_dir / "META-INF" / "MANIFEST.MF"
        if manifest_file.exists():
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace("test_step_1", package_name)
            with open(manifest_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _create_zip_package(self, source_dir: Path, zip_file: Path):
        """Create ZIP package from directory"""
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file() and file_path != zip_file:
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)

# Convenience function
def convert_json_to_iflow_template(json_blueprint: str, output_path: str = None) -> str:
    """Convert JSON blueprint to SAP iFlow XML using template base"""
    converter = TemplateBasedIFlowConverter()
    return converter.convert(json_blueprint, output_path)

def create_sap_package_template(json_blueprint: str, package_name: str = "Generated_Integration") -> str:
    """Create complete SAP package using template base"""
    converter = TemplateBasedIFlowConverter()
    return converter.create_sap_package(json_blueprint, package_name)
