#!/usr/bin/env python3
"""
SAP Integration Suite iFlow Packaging System - Clean Version
============================================================

PURE PACKAGING SCRIPT - Takes agent's complete XML and packages it for SAP Integration Suite

This script ONLY handles:
1. Taking complete XML from your agent (as-is)
2. Stitching components together into proper BPMN structure  
3. Creating proper SAP Integration Suite folder structure
4. Generating required files (MANIFEST.MF, parameters.prop, etc.)
5. Packaging into importable ZIP files

NO component generation - your agent provides complete XML.
"""

import os
import uuid
import zipfile
import tempfile
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class IFlowPackager:
    """
    Pure packaging system for SAP Integration Suite iFlows
    Takes agent's complete XML and packages it properly
    """
    
    def __init__(self, output_directory: str = "packaged_iflows"):
        """Initialize the packager"""
        self.output_directory = output_directory
        self.ensure_output_directory()
        
        # BPMN 2.0 namespace definitions
        self.namespaces = {
            'bpmn2': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
            'dc': 'http://www.omg.org/spec/DD/20100524/DC',
            'di': 'http://www.omg.org/spec/DD/20100524/DI',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'ifl': 'http://com.sap.ifl.model/Ifl.xsd'
        }
        
        # SAP Integration Suite spelling requirements (intentional "mistakes")
        self.sap_spelling = {
            'endpoint_receiver': 'EndpointRecevier',  # Missing 'i' is REQUIRED by SAP
            'endpoint_sender': 'EndpointSender'
        }
        
        # Component file placement - simplified for packaging only
        self.component_types = {
            'MessageMapping': {'extension': '.mmap', 'directory': 'mapping'},
            'GroovyScript': {'extension': '.groovy', 'directory': 'script'},
            'XSLTMapping': {'extension': '.xsl', 'directory': 'mapping'},
            'Schema': {'extension': '.xsd', 'directory': 'xsd'},
            'WSDL': {'extension': '.wsdl', 'directory': 'wsdl'},
            'ContentEnricher': {'extension': '.xml', 'directory': 'enricher'}
        }
        
    def ensure_output_directory(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
            logger.info(f"Created output directory: {self.output_directory}")
    
    def package_component(self, component_xml: str, component_type: str, component_name: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Package a single component from agent's complete XML
        
        Args:
            component_xml: Complete XML from your agent (used as-is)
            component_type: Type of component for file placement
            component_name: Name for the component
            metadata: Optional metadata for the package
        
        Returns:
            Path to the created ZIP file
        """
        logger.info(f"Packaging {component_type}: {component_name}")
        
        # Create temporary directory for package assembly
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = os.path.join(temp_dir, "package")
            os.makedirs(package_dir)
            
            try:
                # 1. Create component files (agent's XML as-is)
                component_files = self._create_component_files(
                    component_xml, component_type, component_name, package_dir
                )
                
                # 2. Create iFlow XML (stitch component into BPMN structure)
                if component_type != 'MessageMapping':  # MessageMapping is standalone
                    flow_id = f"IntegrationProcess_{uuid.uuid4().hex[:8]}"
                    iflow_xml = self._create_basic_iflow_with_component(
                        component_xml, component_type, component_name, flow_id
                    )
                    
                    # Save iFlow XML
                    iflow_dir = os.path.join(package_dir, "src", "main", "resources", 
                                           "scenarioflows", "integrationflow")
                    os.makedirs(iflow_dir, exist_ok=True)
                    iflow_path = os.path.join(iflow_dir, f"{component_name}.iflw")
                    with open(iflow_path, 'w', encoding='utf-8') as f:
                        f.write(iflow_xml)
                
                # 3. Create required SAP Integration Suite files
                self._create_manifest_files(package_dir, component_type, component_name, metadata)
                
                # 4. Create project file
                self._create_project_file(package_dir)
                
                # 5. Create ZIP package
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_filename = f"{component_name}_{timestamp}.zip"
                zip_path = os.path.join(self.output_directory, zip_filename)
                
                self._create_zip_package(package_dir, zip_path)
                
                logger.info(f"✅ Successfully packaged {component_type} as: {zip_path}")
                return zip_path
                
            except Exception as e:
                logger.error(f"❌ Error packaging {component_type}: {e}")
                raise
    
    def package_complete_iflow(self, components: List[Dict[str, str]], iflow_name: str, 
                              flow_description: str = "") -> str:
        """
        Package multiple components from agent into a complete iFlow
        
        Args:
            components: List of components with 'xml', 'type', 'name', 'id' keys
            iflow_name: Name for the complete iFlow
            flow_description: Description for the iFlow
        
        Returns:
            Path to the created ZIP file
        """
        logger.info(f"Packaging complete iFlow: {iflow_name} with {len(components)} components")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = os.path.join(temp_dir, "package")
            os.makedirs(package_dir)
            
            try:
                # 1. Create all component files (agent's XML as-is)
                all_component_files = {}
                for component in components:
                    component_files = self._create_component_files(
                        component['xml'], component['type'], 
                        component['name'], package_dir
                    )
                    all_component_files.update(component_files)
                
                # 2. Create complete iFlow XML (stitch all components together)
                flow_id = f"IntegrationProcess_{uuid.uuid4().hex[:8]}"
                iflow_xml = self._create_complete_iflow(components, iflow_name, flow_id)
                
                # Save iFlow XML
                iflow_dir = os.path.join(package_dir, "src", "main", "resources", 
                                       "scenarioflows", "integrationflow")
                os.makedirs(iflow_dir, exist_ok=True)
                iflow_path = os.path.join(iflow_dir, f"{iflow_name}.iflw")
                with open(iflow_path, 'w', encoding='utf-8') as f:
                    f.write(iflow_xml)
                
                # 3. Create required SAP Integration Suite files
                metadata = {'description': flow_description, 'components': len(components)}
                self._create_manifest_files(package_dir, 'IntegrationFlow', iflow_name, metadata)
                
                # 4. Create project file
                self._create_project_file(package_dir)
                
                # 5. Create ZIP package
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_filename = f"{iflow_name}_{timestamp}.zip"
                zip_path = os.path.join(self.output_directory, zip_filename)
                
                self._create_zip_package(package_dir, zip_path)
                
                logger.info(f"✅ Successfully packaged complete iFlow as: {zip_path}")
                return zip_path
                
            except Exception as e:
                logger.error(f"❌ Error packaging complete iFlow: {e}")
                raise
    
    def _create_component_files(self, component_xml: str, component_type: str, 
                              component_name: str, package_dir: str) -> Dict[str, str]:
        """Create component files - agent's XML as-is in proper directories"""
        files_created = {}
        resources_dir = os.path.join(package_dir, "src", "main", "resources")
        
        # Get component configuration or use default
        if component_type in self.component_types:
            config = self.component_types[component_type]
        else:
            logger.warning(f"Unknown component type: {component_type}, using default")
            config = {'extension': '.xml', 'directory': 'config'}
        
        # Create directory and file
        target_dir = os.path.join(resources_dir, config['directory'])
        os.makedirs(target_dir, exist_ok=True)
        
        filename = f"{component_name}{config['extension']}"
        file_path = os.path.join(target_dir, filename)
        
        # Write agent's complete XML as-is
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(component_xml)
        
        files_created[config['directory']] = f"{config['directory']}/{filename}"
        return files_created
    
    def _create_basic_iflow_with_component(self, component_xml: str, component_type: str, 
                                         component_name: str, flow_id: str) -> str:
        """Stitch agent's complete XML into basic BPMN iFlow structure"""
        
        # Generate unique IDs
        start_id = f"StartEvent_{uuid.uuid4().hex[:8]}"
        end_id = f"EndEvent_{uuid.uuid4().hex[:8]}"
        component_id = f"{component_type}_{uuid.uuid4().hex[:8]}"
        flow1_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
        flow2_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
        
        # Create namespace declarations
        namespace_decls = ' '.join([f'xmlns:{prefix}="{uri}"' for prefix, uri in self.namespaces.items()])
        
        # Create the BPMN XML structure with agent's component XML embedded
        iflow_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions {namespace_decls}
    id="Definitions_{uuid.uuid4().hex[:8]}"
    targetNamespace="http://www.omg.org/spec/BPMN/20100524/MODEL">
    
    <bpmn2:collaboration id="Collaboration_{uuid.uuid4().hex[:8]}" name="{component_name}">
        <bpmn2:participant id="Participant_Process_{uuid.uuid4().hex[:8]}" 
                          ifl:type="IntegrationProcess" 
                          name="{component_name}" 
                          processRef="{flow_id}">
            <bpmn2:extensionElements/>
        </bpmn2:participant>
    </bpmn2:collaboration>
    
    <bpmn2:process id="{flow_id}" name="Integration Process" isExecutable="true">
        <bpmn2:startEvent id="{start_id}" name="Start">
            <bpmn2:outgoing>{flow1_id}</bpmn2:outgoing>
        </bpmn2:startEvent>
        
        <!-- Agent's complete XML embedded here -->
        {component_xml}
        
        <bpmn2:endEvent id="{end_id}" name="End">
            <bpmn2:incoming>{flow2_id}</bpmn2:incoming>
        </bpmn2:endEvent>
        
        <bpmn2:sequenceFlow id="{flow1_id}" sourceRef="{start_id}" targetRef="{component_id}"/>
        <bpmn2:sequenceFlow id="{flow2_id}" sourceRef="{component_id}" targetRef="{end_id}"/>
    </bpmn2:process>
    
</bpmn2:definitions>'''
        
        return self._format_xml(iflow_xml)
    
    def _create_complete_iflow(self, components: List[Dict[str, str]], iflow_name: str, flow_id: str) -> str:
        """Stitch multiple agent components together into complete BPMN iFlow"""
        
        start_id = f"StartEvent_{uuid.uuid4().hex[:8]}"
        end_id = f"EndEvent_{uuid.uuid4().hex[:8]}"
        
        # Create namespace declarations
        namespace_decls = ' '.join([f'xmlns:{prefix}="{uri}"' for prefix, uri in self.namespaces.items()])
        
        # Generate sequence flows between components
        sequence_flows = []
        component_elements = []
        
        for i, component in enumerate(components):
            comp_id = component.get('id', f"{component['type']}_{uuid.uuid4().hex[:8]}")
            
            if i == 0:
                # First component connects to start
                flow_in = f"StartFlow_{uuid.uuid4().hex[:8]}"
                sequence_flows.append(f'<bpmn2:sequenceFlow id="{flow_in}" sourceRef="{start_id}" targetRef="{comp_id}"/>')
            else:
                flow_in = f"Flow_{i}_{uuid.uuid4().hex[:8]}"
                prev_comp_id = components[i-1].get('id', f"{components[i-1]['type']}_{uuid.uuid4().hex[:8]}")
                sequence_flows.append(f'<bpmn2:sequenceFlow id="{flow_in}" sourceRef="{prev_comp_id}" targetRef="{comp_id}"/>')
            
            if i == len(components) - 1:
                # Last component connects to end
                flow_out = f"EndFlow_{uuid.uuid4().hex[:8]}"
                sequence_flows.append(f'<bpmn2:sequenceFlow id="{flow_out}" sourceRef="{comp_id}" targetRef="{end_id}"/>')
            
            # Add agent's complete XML as-is
            component_elements.append(f"<!-- {component['name']} ({component['type']}) -->")
            component_elements.append(component['xml'])
        
        # Create the complete BPMN XML structure
        iflow_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions {namespace_decls}
    id="Definitions_{uuid.uuid4().hex[:8]}"
    targetNamespace="http://www.omg.org/spec/BPMN/20100524/MODEL">
    
    <bpmn2:collaboration id="Collaboration_{uuid.uuid4().hex[:8]}" name="{iflow_name}">
        <bpmn2:participant id="Participant_Process_{uuid.uuid4().hex[:8]}" 
                          ifl:type="IntegrationProcess" 
                          name="{iflow_name}" 
                          processRef="{flow_id}">
            <bpmn2:extensionElements/>
        </bpmn2:participant>
    </bpmn2:collaboration>
    
    <bpmn2:process id="{flow_id}" name="Integration Process" isExecutable="true">
        <bpmn2:startEvent id="{start_id}" name="Start">
            <bpmn2:outgoing>StartFlow_{uuid.uuid4().hex[:8]}</bpmn2:outgoing>
        </bpmn2:startEvent>
        
        <!-- Agent's complete XML components embedded here -->
        {"".join(component_elements)}
        
        <bpmn2:endEvent id="{end_id}" name="End">
            <bpmn2:incoming>EndFlow_{uuid.uuid4().hex[:8]}</bpmn2:incoming>
        </bpmn2:endEvent>
        
        <!-- Sequence flows connecting components -->
        {"".join(sequence_flows)}
    </bpmn2:process>
    
</bpmn2:definitions>'''
        
        return self._format_xml(iflow_xml)
    
    def _create_manifest_files(self, package_dir: str, bundle_type: str, 
                             component_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Create required SAP Integration Suite manifest and property files"""
        
        # Create META-INF directory
        meta_inf_dir = os.path.join(package_dir, "META-INF")
        os.makedirs(meta_inf_dir, exist_ok=True)
        
        # MANIFEST.MF
        manifest_content = f"""Manifest-Version: 1.0
Bundle-SymbolicName: {component_name}
Bundle-Name: {component_name}
Bundle-Version: 1.0.0
Bundle-ManifestVersion: 2
Import-Package: com.sap.esb.model.impl.v240,
 com.sap.esb.model.util.v240,
 com.sap.it.op.agent.api,
 com.sap.it.op.agent.collector.camel,
 com.sap.it.op.agent.mpl
SAP-BundleType: {"MessageMapping" if bundle_type == "MessageMapping" else "IntegrationFlow"}
SAP-NodeType: IFLMAP
Origin-Bundle-Name: {component_name}
Origin-Bundle-Version: 1.0.0
"""
        
        with open(os.path.join(meta_inf_dir, "MANIFEST.MF"), 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        # metainfo.prop (only for IntegrationFlow)
        if bundle_type != 'MessageMapping':
            metainfo_content = f"""#Store metainfo properties
#{datetime.now().strftime('%a %b %d %H:%M:%S UTC %Y')}
description={metadata.get('description', '') if metadata else ''}
SAP-MarkedForDeletion=false
source=Manual
"""
            with open(os.path.join(package_dir, "metainfo.prop"), 'w', encoding='utf-8') as f:
                f.write(metainfo_content)
        
        # Create parameters files
        resources_dir = os.path.join(package_dir, "src", "main", "resources")
        os.makedirs(resources_dir, exist_ok=True)
        
        # parameters.prop
        with open(os.path.join(resources_dir, "parameters.prop"), 'w', encoding='utf-8') as f:
            f.write(f"#{datetime.now().strftime('%a %b %d %H:%M:%S UTC %Y')}\n")
        
        # parameters.propdef
        with open(os.path.join(resources_dir, "parameters.propdef"), 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<parameters/>\n')
    
    def _create_project_file(self, package_dir: str):
        """Create .project file for Eclipse/SAP IS compatibility"""
        project_content = '''<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>iflow</name>
    <comment></comment>
    <projects>
    </projects>
    <buildSpec>
        <buildCommand>
            <name>org.eclipse.jdt.core.javabuilder</name>
            <arguments>
            </arguments>
        </buildCommand>
    </buildSpec>
    <natures>
        <nature>org.eclipse.jdt.core.javanature</nature>
        <nature>com.sap.ide.ifl.project.support.project.nature</nature>
        <nature>com.sap.ide.ifl.bsn</nature>
    </natures>
</projectDescription>'''
        
        with open(os.path.join(package_dir, ".project"), 'w', encoding='utf-8') as f:
            f.write(project_content)
    
    def _create_zip_package(self, package_dir: str, zip_path: str):
        """Create ZIP package from the assembled directory"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, package_dir)
                    zipf.write(file_path, arcname)
        
        logger.info(f"Created zip package: {zip_path}")
    
    def _format_xml(self, xml_string: str) -> str:
        """Format XML for better readability"""
        try:
            import xml.dom.minidom
            dom = xml.dom.minidom.parseString(xml_string)
            formatted = dom.toprettyxml(indent="    ", encoding=None)
            # Remove empty lines and fix declaration
            lines = [line for line in formatted.split('\n') if line.strip()]
            if lines and lines[0].startswith('<?xml'):
                lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
            return '\n'.join(lines)
        except:
            return xml_string


# Example usage
if __name__ == "__main__":
    # Example: Package agent's complete XML
    packager = IFlowPackager(output_directory='clean_packages')
    
    # Agent's complete SFTP XML (as-is)
    agent_sftp_xml = '''<bpmn2:serviceTask id="SFTPTask_001" name="SFTP File Transfer" activityType="ExternalCall">
        <bpmn2:extensionElements>
            <ifl:property>
                <key>ComponentType</key>
                <value>SFTP</value>
            </ifl:property>
            <ifl:property>
                <key>host</key>
                <value>{{SFTP_Host}}</value>
            </ifl:property>
            <ifl:property>
                <key>credentialName</key>
                <value>{{SFTP_Credentials}}</value>
            </ifl:property>
        </bpmn2:extensionElements>
    </bpmn2:serviceTask>'''
    
    # Package it (no modification, just packaging)
    result = packager.package_component(agent_sftp_xml, 'SFTPAdapter', 'CustomerSFTP')
    print(f"Packaged: {result}")
