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
                         metadata: Optional[Dict[str, Any]] = None, groovy_content: str = None) -> str:
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
                    component_xml, component_type, component_name, package_dir, groovy_content
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
    
    def package_complete_iflow_corrected(self, components: List[Dict[str, str]], iflow_name: str, 
                              flow_description: str = "", groovy_files: Dict[str, str] = None,
                              complete_iflow_template: List[Dict[str, Any]] = None) -> str:
        """
        CORRECTED: Package multiple components into a complete iFlow with proper BPMN structure.
        
        This method creates a complete iFlow package that matches the working reference structure.
        
        Args:
            components: List of components with 'xml', 'type', 'name', 'id' keys
            iflow_name: Name for the complete iFlow
            flow_description: Description for the iFlow  
            groovy_files: Dict of groovy filenames to content
        
        Returns:
            Path to the created ZIP file
        """
        # Use provided iflow_name parameter
        logger.info(f"Packaging corrected complete iFlow: {iflow_name} with {len(components)} components")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = os.path.join(temp_dir, "package")
            os.makedirs(package_dir)
            
            try:
                # Create proper directory structure
                resources_dir = os.path.join(package_dir, "src", "main", "resources")
                os.makedirs(resources_dir, exist_ok=True)
                
                # 1. Create all component files (groovy scripts, message mappings, etc.)
                all_component_files = {}
                for component in components:
                    component_files = self._create_component_files(
                        component['xml'], component['type'], 
                        component['name'], package_dir
                    )
                    all_component_files.update(component_files)
                
                # Also handle groovy_files dict if provided (legacy support)
                if groovy_files:
                    script_dir = os.path.join(resources_dir, "script")
                    os.makedirs(script_dir, exist_ok=True)
                    for filename, content in groovy_files.items():
                        script_path = os.path.join(script_dir, filename)
                        with open(script_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"Created groovy script file: script/{filename}")
                
                # 2. Create corrected BPMN iFlow XML with template data
                iflow_xml = self._create_corrected_complete_iflow_xml(components, iflow_name, complete_iflow_template)
                
                # Save iFlow XML
                iflow_dir = os.path.join(resources_dir, "scenarioflows", "integrationflow")
                os.makedirs(iflow_dir, exist_ok=True)
                iflow_path = os.path.join(iflow_dir, f"{iflow_name}.iflw")
                with open(iflow_path, 'w', encoding='utf-8') as f:
                    f.write(iflow_xml)
                
                # 3. Create manifest and support files
                self._create_manifest_files(package_dir, "IntegrationFlow", iflow_name, {
                    'description': flow_description,
                    'components': len(components)
                })
                
                # 4. Create project file
                self._create_project_file(package_dir)
                
                # 5. Create ZIP package
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_filename = f"{iflow_name}_Complete_{timestamp}.zip"
                zip_path = os.path.join(self.output_directory, zip_filename)
                
                self._create_zip_package(package_dir, zip_path)
                
                logger.info(f"✅ Successfully packaged corrected complete iFlow as: {zip_path}")
                return zip_path
                
            except Exception as e:
                logger.error(f"❌ Error packaging corrected complete iFlow: {e}")
                raise

    def _inject_flow_references(self, process_elements: List[tuple], sequence_flows: List[str]) -> List[tuple]:
        """
        Inject <bpmn2:incoming> and <bpmn2:outgoing> references into components.
        SAP requires these for proper editing and validation.
        
        Args:
            process_elements: List of (element_id, xml_string) tuples
            sequence_flows: List of sequence flow XML strings
            
        Returns:
            Updated process_elements with flow references injected
        """
        import re
        
        # Build mapping: element_id -> {incoming: [flow_ids], outgoing: [flow_ids]}
        flow_map = {}
        
        for flow_xml in sequence_flows:
            # Extract flow ID, sourceRef, targetRef
            flow_id_match = re.search(r'id="([^"]+)"', flow_xml)
            source_match = re.search(r'sourceRef="([^"]+)"', flow_xml)
            target_match = re.search(r'targetRef="([^"]+)"', flow_xml)
            
            if flow_id_match and source_match and target_match:
                flow_id = flow_id_match.group(1)
                source_id = source_match.group(1)
                target_id = target_match.group(1)
                
                # Add outgoing to source
                if source_id not in flow_map:
                    flow_map[source_id] = {'incoming': [], 'outgoing': []}
                flow_map[source_id]['outgoing'].append(flow_id)
                
                # Add incoming to target
                if target_id not in flow_map:
                    flow_map[target_id] = {'incoming': [], 'outgoing': []}
                flow_map[target_id]['incoming'].append(flow_id)
        
        # Inject flow references into each element
        updated_elements = []
        for elem_id, elem_xml in process_elements:
            if elem_id in flow_map:
                flows = flow_map[elem_id]
                
                # Build incoming/outgoing tags
                incoming_tags = ''.join([f'\n    <bpmn2:incoming>{flow_id}</bpmn2:incoming>' for flow_id in flows['incoming']])
                outgoing_tags = ''.join([f'\n    <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>' for flow_id in flows['outgoing']])
                
                # Insert AFTER </bpmn2:extensionElements> (SAP requirement)
                # If no extensionElements, insert after opening tag
                if '</bpmn2:extensionElements>' in elem_xml:
                    # Insert after extensionElements closing tag
                    updated_xml = elem_xml.replace(
                        '</bpmn2:extensionElements>',
                        '</bpmn2:extensionElements>' + incoming_tags + outgoing_tags,
                        1  # Replace only first occurrence
                    )
                    updated_elements.append((elem_id, updated_xml))
                else:
                    # No extensionElements, insert after opening tag
                    match = re.search(r'(<bpmn2:\w+[^>]*>)', elem_xml)
                    if match:
                        opening_tag = match.group(1)
                        updated_xml = elem_xml.replace(
                            opening_tag,
                            opening_tag + incoming_tags + outgoing_tags,
                            1
                        )
                        updated_elements.append((elem_id, updated_xml))
                    else:
                        # Couldn't parse, leave as-is
                        updated_elements.append((elem_id, elem_xml))
            else:
                # No flows connected to this element
                updated_elements.append((elem_id, elem_xml))
        
        return updated_elements
    
    def _create_corrected_complete_iflow_xml(self, components: List[Dict[str, str]], iflow_name: str, 
                                            complete_iflow_template: List[Dict[str, Any]] = None) -> str:
        """Create corrected BPMN XML with dynamic, query-driven flow.

        Rules implemented:
        - Always include Start and End events. If user provided any Start/End, do not duplicate.
        - Add additional components only from input (no placeholders).
        - Connect components linearly with <bpmn2:sequenceFlow> in the provided order.
        - Support SAP-specific components such as callActivity, serviceTask, gateways, etc., using agent XML as-is.
        - Keep collaboration/process structure and packaging behavior unchanged.
        """
        import uuid
        import re
        
        # Generate unique IDs
        collaboration_id = f"Collaboration_{uuid.uuid4().hex[:8]}"
        process_id = f"Process_{uuid.uuid4().hex[:8]}"
        
        # Extract collaboration properties from RAG template content
        collaboration_properties = self._extract_collaboration_properties_from_rag(complete_iflow_template)
        logger.info(f"Extracted {len(collaboration_properties)} collaboration properties from RAG")
        
        # Separate components by placement
        participants = []
        process_elements = []  # (element_id, xml)
        message_flows = []
        sequence_flows = []

        # Utility: extract first tag and id
        def extract_tag_and_id(xml_str: str) -> (str, str):
            import re
            tag_match = re.search(r'<\s*([a-zA-Z0-9:]+)', xml_str)
            id_match = re.search(r'id="([^"]+)"', xml_str)
            tag = tag_match.group(1) if tag_match else ''
            eid = id_match.group(1) if id_match else f"Elem_{uuid.uuid4().hex[:8]}"
            return tag.lower(), eid

        provided_start_ids = []
        provided_end_ids = []
        linear_ids = []  # ids to connect in order, excluding pure collaboration items

        for comp in components:
            comp_type = comp.get('type', '')
            comp_name = comp.get('name', '')
            xml_body = (comp.get('xml') or '').strip()
            tag, actual_id = extract_tag_and_id(xml_body)

            if comp_type == 'EndpointSender':
                participants.append(f'''        <bpmn2:participant id="EndpointSender_{uuid.uuid4().hex[:8]}" ifl:type="EndpointSender" name="{comp_name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>enableBasicAuthentication</key>
                    <value>false</value>
                </ifl:property>
                <ifl:property>
                    <key>ifl:type</key>
                    <value>EndpointSender</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:participant>''')
                continue
            
            elif comp_type == 'EndpointRecevier':
                # Use the provided XML directly for EndpointRecevier to preserve intentional typo
                participants.append(f"        {xml_body}")
                continue
            
            elif comp_type == 'MessageFlow':
                # MessageFlows belong in collaboration, not process
                message_flows.append(f"        {xml_body}")
                continue

            # Process-level elements: accept as-is
            process_elements.append((actual_id, f"        {xml_body}"))

            if '<bpmn2:startevent' in xml_body.lower():
                provided_start_ids.append(actual_id)
            elif '<bpmn2:endevent' in xml_body.lower():
                provided_end_ids.append(actual_id)
            else:
                # Linear element (serviceTask, callActivity, gateway, etc.)
                linear_ids.append(actual_id)

        # Ensure Start and End exist if not provided
        default_start_id = None
        default_end_id = None

        if not provided_start_ids:
            default_start_id = f"StartEvent_{uuid.uuid4().hex[:8]}"
            process_elements.insert(0, (default_start_id, f'''        <bpmn2:startEvent id="{default_start_id}" name="Start">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::MessageStartEvent</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:messageEventDefinition/>
        </bpmn2:startEvent>'''))
            provided_start_ids.append(default_start_id)

        if not provided_end_ids:
            default_end_id = f"EndEvent_{uuid.uuid4().hex[:8]}"
            process_elements.append((default_end_id, f'''        <bpmn2:endEvent id="{default_end_id}" name="End">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:messageEventDefinition/>
        </bpmn2:endEvent>'''))
            provided_end_ids.append(default_end_id)

        # Build sequence: Start -> linear elements -> End(s)
        # Enhanced: Handle Router branching with component assignments
        gateway_ids = [eid for eid in linear_ids if 'ExclusiveGateway' in eid or 'ParallelGateway' in eid or 'InclusiveGateway' in eid]
        end_ids = provided_end_ids
        
        # Check if any component has branching metadata
        router_comps = [c for c in components if c.get('type') == 'Router' and c.get('branches')]
        has_router_branches = len(router_comps) > 0
        
        if gateway_ids and has_router_branches:
            # Router branching case with component assignments
            router_comp = router_comps[0]
            router_id = None
            for eid in gateway_ids:
                if 'ExclusiveGateway' in eid:
                    router_id = eid
                    break
            
            if router_id:
                logger.info(f"🔀 [ROUTER_BRANCHING] Detected Router with {len(router_comp['branches'])} branches")
                
                # Build chain: Start -> components before router -> Router
                non_gateway_ids = [eid for eid in linear_ids if eid not in gateway_ids]
                components_before_router = []
                branch_component_ids = set()
                
                # Identify components in branches
                for branch_info in router_comp['branches']:
                    branch_component_ids.update(branch_info.get('component_ids', []))
                
                # Separate pre-router and branch components
                for eid in non_gateway_ids:
                    if eid not in branch_component_ids:
                        components_before_router.append(eid)
                
                # Main chain: Start -> pre-router components -> Router
                main_chain = [provided_start_ids[0]] + components_before_router + [router_id]
                
                # Connect main chain
                for i in range(len(main_chain) - 1):
                    src = main_chain[i]
                    tgt = main_chain[i + 1]
                    seq_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
                    sequence_flows.append(f'''        <bpmn2:sequenceFlow id="{seq_id}" sourceRef="{src}" targetRef="{tgt}"/>''')
                
                # Create branches from Router
                total_branches = len(router_comp['branches'])
                default_route_id = None  # Track the default route ID
                
                for branch_info in router_comp['branches']:
                    branch_num = branch_info['branch_number']
                    branch_comp_ids = branch_info.get('component_ids', [])
                    routing_condition = branch_info.get('routing_condition', '')
                    is_last_branch = (branch_num == total_branches)
                    
                    if not branch_comp_ids:
                        # Empty branch: Router -> End
                        seq_id = f"SequenceFlow_Branch{branch_num}_{uuid.uuid4().hex[:8]}"
                        end_id = end_ids[0] if end_ids else default_end_id
                        
                        route_name = f"Route {branch_num}"
                        
                        if is_last_branch or routing_condition == "default":
                            # Last branch is ALWAYS the default route (NO conditionExpression at all)
                            default_route_id = seq_id  # Store the default route ID
                            logger.info(f"   🔀 [ROUTE{branch_num}] Name: '{route_name}', Condition: NONE (default), Order: {branch_num}")
                            sequence_flows.append(f'''        <bpmn2:sequenceFlow id="{seq_id}" name="{route_name}" sourceRef="{router_id}" targetRef="{end_id}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>expressionType</key>
                    <value>nonXML</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:sequenceFlow>''')
                        else:
                            # Conditional branch with routing condition
                            logger.info(f"   🔀 [ROUTE{branch_num}] Name: '{route_name}', Condition: {routing_condition}, Order: {branch_num}")
                            sequence_flows.append(f'''        <bpmn2:sequenceFlow id="{seq_id}" name="{route_name}" sourceRef="{router_id}" targetRef="{end_id}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>expressionType</key>
                    <value>nonXML</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:conditionExpression id="FormalExpression_{seq_id}_{uuid.uuid4().hex[:13]}" xsi:type="bpmn2:tFormalExpression"><![CDATA[{routing_condition}]]></bpmn2:conditionExpression>
        </bpmn2:sequenceFlow>''')
                    else:
                        # Branch with components: Router -> Comp1 -> Comp2 -> ... -> End
                        # CRITICAL FIX: Filter out Participants and MessageFlows - they're NOT process elements!
                        # sequenceFlow can ONLY connect process elements (tasks, gateways, events)
                        process_element_ids = [eid for eid, _ in process_elements]
                        branch_process_ids = [cid for cid in branch_comp_ids if cid in process_element_ids]
                        
                        logger.info(f"   📋 [BRANCH{branch_num}] Filtered {len(branch_comp_ids)} total IDs → {len(branch_process_ids)} process IDs")
                        logger.info(f"   📋 [BRANCH{branch_num}] Process IDs: {branch_process_ids}")
                        
                        branch_chain = [router_id] + branch_process_ids + [end_ids[0] if end_ids else default_end_id]
                        
                        for i in range(len(branch_chain) - 1):
                            src = branch_chain[i]
                            tgt = branch_chain[i + 1]
                            seq_id = f"SequenceFlow_Branch{branch_num}_{uuid.uuid4().hex[:8]}"
                            
                            # Add routing condition to first sequence flow from router
                            if i == 0:
                                route_name = f"Route {branch_num}"
                                
                                # First flow from Router to branch component
                                if is_last_branch or routing_condition == "default":
                                    # Last branch is default (NO conditionExpression at all)
                                    default_route_id = seq_id  # Store the default route ID
                                    logger.info(f"   🔀 [ROUTE{branch_num}] Name: '{route_name}', Condition: NONE (default), Order: {branch_num}")
                                    sequence_flows.append(f'''        <bpmn2:sequenceFlow id="{seq_id}" name="{route_name}" sourceRef="{src}" targetRef="{tgt}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>expressionType</key>
                    <value>nonXML</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:sequenceFlow>''')
                                else:
                                    # Conditional route with routing condition
                                    logger.info(f"   🔀 [ROUTE{branch_num}] Name: '{route_name}', Condition: {routing_condition}, Order: {branch_num}")
                                    sequence_flows.append(f'''        <bpmn2:sequenceFlow id="{seq_id}" name="{route_name}" sourceRef="{src}" targetRef="{tgt}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>expressionType</key>
                    <value>nonXML</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:conditionExpression id="FormalExpression_{seq_id}_{uuid.uuid4().hex[:13]}" xsi:type="bpmn2:tFormalExpression"><![CDATA[{routing_condition}]]></bpmn2:conditionExpression>
        </bpmn2:sequenceFlow>''')
                            else:
                                # Subsequent flows within branch
                                sequence_flows.append(f'''        <bpmn2:sequenceFlow id="{seq_id}" sourceRef="{src}" targetRef="{tgt}"/>''')
                    
                    logger.info(f"   ✅ [BRANCH{branch_num}] Created sequence flows with condition: {routing_condition}")
                
                # Update Router XML to include the actual default route ID and REMOVE legacy routingConditions
                if default_route_id:
                    for i, (elem_id, elem_xml) in enumerate(process_elements):
                        if elem_id == router_id:
                            # Remove the routingConditions property (SAP doesn't use it when name attribute is present)
                            import re
                            updated_xml = re.sub(
                                r'<ifl:property>\s*<key>routingConditions</key>\s*<value>.*?</value>\s*</ifl:property>',
                                '',
                                elem_xml,
                                flags=re.DOTALL
                            )
                            
                            # Update the Router's default attribute
                            updated_xml = updated_xml.replace(
                                f'<bpmn2:exclusiveGateway id="{router_id}"',
                                f'<bpmn2:exclusiveGateway id="{router_id}" default="{default_route_id}"'
                            )
                            
                            process_elements[i] = (elem_id, updated_xml)
                            logger.info(f"   ✅ [ROUTER] Updated Router with default route: {default_route_id}")
                            logger.info(f"   ✅ [ROUTER] Removed legacy routingConditions property")
                            break
        
        elif gateway_ids and len(end_ids) > 1:
            # Legacy branching case: Start -> ... -> Gateway -> End1, End2
            gateway_id = gateway_ids[0]
            non_gateway_ids = [eid for eid in linear_ids if eid not in gateway_ids]
            
            # Build main chain: Start -> non-gateway elements -> Gateway
            main_chain = [provided_start_ids[0]] + non_gateway_ids + [gateway_id]
            
            # Connect main chain
            for i in range(len(main_chain) - 1):
                src = main_chain[i]
                tgt = main_chain[i + 1]
                seq_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
                sequence_flows.append(f'''        <bpmn2:sequenceFlow id="{seq_id}" sourceRef="{src}" targetRef="{tgt}"/>''')
            
            # Connect gateway to both ends
            for end_id in end_ids:
                seq_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
                sequence_flows.append(f'''        <bpmn2:sequenceFlow id="{seq_id}" sourceRef="{gateway_id}" targetRef="{end_id}"/>''')
        else:
            # Linear case: Start -> linear elements -> End
            sequence_chain = []
            if linear_ids:
                sequence_chain = [provided_start_ids[0]] + linear_ids + [provided_end_ids[0]]
            else:
                # Minimal: Start -> End
                sequence_chain = [provided_start_ids[0], provided_end_ids[0]]

            for i in range(len(sequence_chain) - 1):
                src = sequence_chain[i]
                tgt = sequence_chain[i + 1]
                seq_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
                sequence_flows.append(f'''        <bpmn2:sequenceFlow id="{seq_id}" sourceRef="{src}" targetRef="{tgt}"/>''')
        
        # Create HTTPS message flow if we have sender (not receiver) and a start event
        sender_participants = [p for p in participants if 'EndpointSender' in p]
        if sender_participants and provided_start_ids:
            sender_id = sender_participants[0].split('id="')[1].split('"')[0]
            start_id = provided_start_ids[0]
            message_flow_id = f"MessageFlow_{uuid.uuid4().hex[:8]}"
            message_flows.append(f'''        <bpmn2:messageFlow id="{message_flow_id}" name="HTTPS" sourceRef="{sender_id}" targetRef="{start_id}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>HTTPS</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>maximumBodySize</key>
                    <value>40</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>urlPath</key>
                    <value>/example</value>
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>/example</value>
                </ifl:property>
                <ifl:property>
                    <key>Name</key>
                    <value>HTTPS</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>1.1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>Sender1</value>
                </ifl:property>
                <ifl:property>
                    <key>xsrfProtection</key>
                    <value>0</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTPS</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::AdapterVariant/cname::sap:HTTPS/tp::HTTPS/mp::None/direction::Sender/version::1.1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>userRole</key>
                    <value>ESBMessaging.send</value>
                </ifl:property>
                <ifl:property>
                    <key>senderAuthType</key>
                    <value>RoleBased</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>None</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>1.1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVId</key>
                    <value>1.1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Sender</value>
                </ifl:property>
                <ifl:property>
                    <key>clientCertificates</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>authenticationMethod</key>
                    <value>RoleBased</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>''')
        
        # Inject incoming/outgoing references into components based on sequence flows
        # SAP requires these for proper editing/validation
        process_elements = self._inject_flow_references(process_elements, sequence_flows)
        
        # Build the complete XML with RAG-extracted collaboration properties
        namespace_decls = ' '.join([f'xmlns:{prefix}="{uri}"' for prefix, uri in self.namespaces.items()])
        
        iflow_xml = f'''<?xml version="1.0" encoding="UTF-8"?><bpmn2:definitions {namespace_decls} id="Definitions_1">
    <bpmn2:collaboration id="{collaboration_id}" name="Default Collaboration">
        <bpmn2:extensionElements>'''
        
        # Add collaboration properties (from RAG or defaults)
        for prop_key, prop_value in collaboration_properties.items():
            iflow_xml += f'''
            <ifl:property>
                <key>{prop_key}</key>
                <value>{prop_value}</value>
            </ifl:property>'''
        
        iflow_xml += f'''
        </bpmn2:extensionElements>
{chr(10).join(participants)}
        <bpmn2:participant id="Participant_Process_1" ifl:type="IntegrationProcess" name="Integration Process" processRef="{process_id}">
            <bpmn2:extensionElements/>
        </bpmn2:participant>
{chr(10).join(message_flows)}
    </bpmn2:collaboration>
    <bpmn2:process id="{process_id}" name="Integration Process">
        <bpmn2:extensionElements>
            <ifl:property>
                <key>transactionTimeout</key>
                <value>30</value>
            </ifl:property>
            <ifl:property>
                <key>componentVersion</key>
                <value>1.2</value>
            </ifl:property>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::FlowElementVariant/cname::IntegrationProcess/version::1.2.1</value>
            </ifl:property>
            <ifl:property>
                <key>transactionalHandling</key>
                <value>Not Required</value>
            </ifl:property>
        </bpmn2:extensionElements>
{chr(10).join([element[1] for element in process_elements])}
{chr(10).join(sequence_flows)}
    </bpmn2:process>
    {self._generate_bpmn_diagram(collaboration_id, process_id, participants, process_elements, sequence_flows, message_flows)}
</bpmn2:definitions>'''
        
        return iflow_xml

    def _extract_collaboration_properties_from_rag(self, complete_iflow_template: List[Dict[str, Any]] = None) -> Dict[str, str]:
        """Extract collaboration properties from RAG template content."""
        import re
        
        # Default collaboration properties (fallback)
        default_properties = {
            'namespaceMapping': '',
            'httpSessionHandling': 'None',
            'accessControlMaxAge': '',
            'returnExceptionToSender': 'false',
            'log': 'All events',
            'corsEnabled': 'false',
            'exposedHeaders': '',
            'componentVersion': '1.2',
            'allowedHeaderList': '',
            'ServerTrace': 'false',
            'allowedOrigins': '',
            'accessControlAllowCredentials': 'false',
            'allowedHeaders': '',
            'allowedMethods': '',
            'cmdVariantUri': 'ctype::IFlowVariant/cname::IFlowConfiguration/version::1.2.4'
        }
        
        if not complete_iflow_template:
            logger.info("No RAG template content provided, using defaults")
            return default_properties
        
        # Extract properties from RAG content
        extracted_properties = {}
        
        for rag_item in complete_iflow_template:
            content = rag_item.get('content', '') if isinstance(rag_item, dict) else str(rag_item)
            
            # Look for collaboration extensionElements with properties
            if '<bpmn2:collaboration' in content and 'extensionElements' in content:
                # Extract all ifl:property elements from collaboration section
                property_pattern = r'<ifl:property>\s*<key>\s*([^<]+?)\s*</key>\s*<value>\s*(.*?)\s*</value>\s*</ifl:property>'
                property_matches = re.findall(property_pattern, content, re.DOTALL)
                
                for key, value in property_matches:
                    key = key.strip()
                    value = value.strip()
                    
                    # Only extract known collaboration properties
                    if key in default_properties:
                        extracted_properties[key] = value
                        logger.info(f"Extracted collaboration property from RAG: {key} = {value}")
        
        # Merge extracted with defaults (extracted takes priority)
        final_properties = default_properties.copy()
        final_properties.update(extracted_properties)
        
        logger.info(f"Final collaboration properties: {len(final_properties)} total ({len(extracted_properties)} from RAG)")
        return final_properties

    def _generate_bpmn_diagram(self, collaboration_id: str, process_id: str, 
                              participants: list, process_elements: list, 
                              sequence_flows: list, message_flows: list) -> str:
        """Generate BPMN diagram section for visual representation."""
        import uuid
        
        diagram_xml = f'''<bpmndi:BPMNDiagram id="BPMNDiagram_1" name="Default Collaboration Diagram">
        <bpmndi:BPMNPlane bpmnElement="{collaboration_id}" id="BPMNPlane_1">'''
        
        # Generate shapes for ALL process elements - CRITICAL for SAP Integration Suite import!
        call_activity_shapes = []
        service_task_shapes = []
        gateway_shapes = []
        start_event_shapes = []
        end_event_shapes = []

        for element_id, element_xml in process_elements:
            lowered_xml = element_xml.lower()
            if '<bpmn2:callactivity' in lowered_xml:
                call_activity_shapes.append((element_id, element_xml))
            elif '<bpmn2:servicetask' in lowered_xml:
                service_task_shapes.append((element_id, element_xml))
            elif '<bpmn2:exclusivegateway' in lowered_xml or '<bpmn2:parallelgateway' in lowered_xml or '<bpmn2:inclusivegateway' in lowered_xml:
                gateway_shapes.append((element_id, element_xml))
            elif '<bpmn2:startevent' in lowered_xml:
                start_event_shapes.append((element_id, element_xml))
            elif '<bpmn2:endevent' in lowered_xml:
                end_event_shapes.append((element_id, element_xml))

        # Shapes positions (space callActivities horizontally so they don't overlap)
        call_positions = {}
        gateway_positions = {}
        service_positions = {}
        for idx, (element_id, _) in enumerate(call_activity_shapes):
            x = 415.0 + (166.0 * idx)
            y = 131.0
            diagram_xml += f'''
            <bpmndi:BPMNShape bpmnElement="{element_id}" id="BPMNShape_{element_id}">
                <dc:Bounds height="60.0" width="100.0" x="{x}" y="{y}"/>
            </bpmndi:BPMNShape>'''
            call_positions[element_id] = (x, y, 100.0, 60.0)

        for idx, (element_id, _) in enumerate(service_task_shapes):
            x = 415.0 + (166.0 * idx)
            y = 200.0
            diagram_xml += f'''
            <bpmndi:BPMNShape bpmnElement="{element_id}" id="BPMNShape_{element_id}">
                <dc:Bounds height="60.0" width="100.0" x="{x}" y="{y}"/>
            </bpmndi:BPMNShape>'''
            service_positions[element_id] = (x, y, 100.0, 60.0)

        for idx, (element_id, _) in enumerate(gateway_shapes):
            x = 465.0 + (166.0 * idx)
            y = 160.0
            diagram_xml += f'''
            <bpmndi:BPMNShape bpmnElement="{element_id}" id="BPMNShape_{element_id}">
                <dc:Bounds height="50.0" width="50.0" x="{x}" y="{y}"/>
            </bpmndi:BPMNShape>'''
            gateway_positions[element_id] = (x, y, 50.0, 50.0)
        
        # Process participant shape (MUST be added before individual elements!)
        diagram_xml += f'''
            <bpmndi:BPMNShape bpmnElement="Participant_Process_1" id="BPMNShape_Participant_Process_1">
                <dc:Bounds height="225.0" width="540.0" x="250.0" y="60.0"/>
            </bpmndi:BPMNShape>'''
            
        # Add StartEvent shapes (positioned at 299, 140)
        start_positions = {}
        for element_id, element_xml in start_event_shapes:
            diagram_xml += f'''
            <bpmndi:BPMNShape bpmnElement="{element_id}" id="BPMNShape_{element_id}">
                <dc:Bounds height="32.0" width="32.0" x="299.0" y="140.0"/>
            </bpmndi:BPMNShape>'''
            start_positions[element_id] = (299.0, 140.0, 32.0, 32.0)
        
        # Add EndEvent shapes (positioned at 626, 140)
        end_positions = {}
        for element_id, element_xml in end_event_shapes:
            diagram_xml += f'''
            <bpmndi:BPMNShape bpmnElement="{element_id}" id="BPMNShape_{element_id}">
                <dc:Bounds height="32.0" width="32.0" x="626.0" y="140.0"/>
            </bpmndi:BPMNShape>'''
            end_positions[element_id] = (626.0, 140.0, 32.0, 32.0)
        
        # External participants (both Sender and Receiver)
        sender_y = 103
        receiver_y = 103
        for participant in participants:
            # Extract participant ID
            import re
            participant_id_match = re.search(r'id="([^"]+)"', participant)
            if participant_id_match:
                participant_id = participant_id_match.group(1)
                
                if 'EndpointSender' in participant:
                    diagram_xml += f'''
            <bpmndi:BPMNShape bpmnElement="{participant_id}" id="BPMNShape_{participant_id}">
                <dc:Bounds height="140.0" width="100.0" x="93.0" y="{sender_y}"/>
            </bpmndi:BPMNShape>'''
                    sender_y += 150  # Space multiple senders vertically
                    
                elif 'EndpointRecevier' in participant or 'EndpointReceiver' in participant:
                    diagram_xml += f'''
            <bpmndi:BPMNShape bpmnElement="{participant_id}" id="BPMNShape_{participant_id}">
                <dc:Bounds height="140.0" width="100.0" x="750.0" y="{receiver_y}"/>
            </bpmndi:BPMNShape>'''
                    receiver_y += 150  # Space multiple receivers vertically
        
        # Generate edges for sequence flows
        for seq_flow in sequence_flows:
            # Extract sequence flow details
            import re
            seq_id_match = re.search(r'id="([^"]+)"', seq_flow)
            source_match = re.search(r'sourceRef="([^"]+)"', seq_flow)
            target_match = re.search(r'targetRef="([^"]+)"', seq_flow)
            
            if seq_id_match and source_match and target_match:
                seq_id = seq_id_match.group(1)
                source_id = source_match.group(1)
                target_id = target_match.group(1)
                
                diagram_xml += f'''
            <bpmndi:BPMNEdge bpmnElement="{seq_id}" id="BPMNEdge_{seq_id}" sourceElement="BPMNShape_{source_id}" targetElement="BPMNShape_{target_id}">'''

                # Compute waypoints using positions if known
                def center_right(pos):
                    x, y, w, h = pos
                    return (x + w, y + h/2.0)
                def center_left(pos):
                    x, y, w, h = pos
                    return (x, y + h/2.0)

                pos_map = {}
                pos_map.update(call_positions)
                pos_map.update(service_positions)
                pos_map.update(gateway_positions)
                pos_map.update(start_positions)
                pos_map.update(end_positions)
                
                if source_id in pos_map and target_id in pos_map:
                    sx, sy = center_right(pos_map[source_id])
                    tx, ty = center_left(pos_map[target_id])
                    diagram_xml += f'''
                <di:waypoint x="{sx}" xsi:type="dc:Point" y="{sy}"/>
                <di:waypoint x="{tx}" xsi:type="dc:Point" y="{ty}"/>'''
                else:
                    # Fallback to prior constants
                    diagram_xml += f'''
                <di:waypoint x="315.0" xsi:type="dc:Point" y="158.5"/>
                <di:waypoint x="415.5" xsi:type="dc:Point" y="158.5"/>'''
                
                diagram_xml += '''
            </bpmndi:BPMNEdge>'''
        
        # Generate edges for message flows
        for msg_flow in message_flows:
            import re
            msg_id_match = re.search(r'id="([^"]+)"', msg_flow)
            source_match = re.search(r'sourceRef="([^"]+)"', msg_flow)
            target_match = re.search(r'targetRef="([^"]+)"', msg_flow)
            
            if msg_id_match and source_match and target_match:
                msg_id = msg_id_match.group(1)
                source_id = source_match.group(1)
                target_id = target_match.group(1)
                
                # Calculate proper waypoints based on element positions
                def get_center_position(element_id):
                    # Check if it's a process element (serviceTask, etc.)
                    for eid, _ in process_elements:
                        if eid == element_id:
                            # ServiceTask is typically at x=415, y=200
                            return (465.0, 230.0)  # Center of serviceTask
                    
                    # Check if it's an external participant
                    for participant in participants:
                        if element_id in participant:
                            if 'EndpointSender' in participant:
                                return (143.0, 173.0)  # Left side sender
                            elif 'EndpointRecevier' in participant or 'EndpointReceiver' in participant:
                                return (800.0, 173.0)  # Right side receiver
                    
                    # Default fallback
                    return (465.0, 230.0)
                
                source_x, source_y = get_center_position(source_id)
                target_x, target_y = get_center_position(target_id)
                
                diagram_xml += f'''
            <bpmndi:BPMNEdge bpmnElement="{msg_id}" id="BPMNEdge_{msg_id}" sourceElement="BPMNShape_{source_id}" targetElement="BPMNShape_{target_id}">
                <di:waypoint x="{source_x}" xsi:type="dc:Point" y="{source_y}"/>
                <di:waypoint x="{target_x}" xsi:type="dc:Point" y="{target_y}"/>
            </bpmndi:BPMNEdge>'''
        
        diagram_xml += '''
        </bpmndi:BPMNPlane>
    </bpmndi:BPMNDiagram>'''
        
        return diagram_xml

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
    
    def _extract_mapping_content(self, component_xml: str) -> str:
        """
        Extract message mapping content from XML comments added by the agent.
        The agent embeds actual mapping content from RAG within XML comments.
        """
        import re
        
        # Look for mapping content markers in XML comments
        pattern = r'<!-- MAPPING_CONTENT_START\s*(.*?)\s*MAPPING_CONTENT_END -->'
        match = re.search(pattern, component_xml, re.DOTALL)
        
        if match:
            mapping_content = match.group(1).strip()
            logger.info(f"Extracted mapping content from agent XML ({len(mapping_content)} chars)")
            return mapping_content
        
        return None
    
    def _create_component_files(self, component_xml: str, component_type: str, 
                              component_name: str, package_dir: str, groovy_content: str = None) -> Dict[str, str]:
        """Create component files - agent's XML as-is in proper directories, plus groovy files if needed"""
        files_created = {}
        resources_dir = os.path.join(package_dir, "src", "main", "resources")
        
        # Special handling for GroovyScript
        if component_type == 'GroovyScript':
            # Create script directory and groovy file
            script_dir = os.path.join(resources_dir, "script")
            os.makedirs(script_dir, exist_ok=True)
            
            # Create the .groovy file with content from agent
            # Replace spaces with underscores for valid filenames
            groovy_filename = f"{component_name.lower().replace(' ', '_')}.groovy"
            groovy_path = os.path.join(script_dir, groovy_filename)
            
            # Use provided groovy content or default
            if groovy_content:
                content = groovy_content
            else:
                # Default groovy script template
                content = f'''/* Generated {component_name} groovy script */
import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;

def Message processData(Message message) {{
    // Body processing
    def body = message.getBody(String.class);
    
    // Headers processing
    def headers = message.getHeaders();
    
    // Properties processing  
    def properties = message.getProperties();
    
    // Process the message here
    // Add your {component_name} logic
    
    return message;
}}'''
            
            with open(groovy_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            files_created['script'] = f"script/{groovy_filename}"
            logger.info(f"Created groovy script file: script/{groovy_filename}")
        
        # Special handling for MessageMapping
        elif component_type == 'MessageMapping':
            # Create mapping directory and .mmap file
            mapping_dir = os.path.join(resources_dir, "mapping")
            os.makedirs(mapping_dir, exist_ok=True)
            
            # Create the .mmap file with minimal valid mapping content
            # Replace spaces with underscores for valid filenames
            mapping_filename = f"{component_name.replace(' ', '_')}.mmap"
            mapping_path = os.path.join(mapping_dir, mapping_filename)
            
            # Extract mapping content from component XML (if provided by agent)
            mapping_content = self._extract_mapping_content(component_xml)
            
            # If no mapping content found, use default structure
            if not mapping_content:
                mapping_content = '''<?xml version="1.0" encoding="UTF-8"?>
<mapping:Mapping xmlns:mapping="http://sap.com/xi/transformation/mm">
    <mapping:MappingDefinition name="MessageMapping" description="Generated message mapping">
        <mapping:Source>
            <mapping:Schema/>
        </mapping:Source>
        <mapping:Target>
            <mapping:Schema/>
        </mapping:Target>
    </mapping:MappingDefinition>
</mapping:Mapping>'''
                logger.info(f"Using default mapping content for {mapping_filename}")
            else:
                logger.info(f"Using RAG-extracted mapping content for {mapping_filename} ({len(mapping_content)} chars)")
            
            with open(mapping_path, 'w', encoding='utf-8') as f:
                f.write(mapping_content)
            
            files_created['mapping'] = f"mapping/{mapping_filename}"
            logger.info(f"Created message mapping file: mapping/{mapping_filename}")
            
        else:
            # Handle other component types (XML-based)
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
        """Create BPMN iFlow matching SAP Integration Suite working reference structure"""
        
        # Extract component ID from the XML to add diagram shape
        import re
        component_id_match = re.search(r'id="([^"]+)"', component_xml)
        component_id = component_id_match.group(1) if component_id_match else "CallActivity_4"
        
        # Create namespace declarations
        namespace_decls = ' '.join([f'xmlns:{prefix}="{uri}"' for prefix, uri in self.namespaces.items()])
        
        # Create the BPMN XML structure matching working reference exactly
        iflow_xml = f'''<?xml version="1.0" encoding="UTF-8"?><bpmn2:definitions {namespace_decls} id="Definitions_1">
    <bpmn2:collaboration id="Collaboration_1" name="Default Collaboration">
        <bpmn2:extensionElements>
            <ifl:property>
                <key>namespaceMapping</key>
                <value/>
            </ifl:property>
            <ifl:property>
                <key>httpSessionHandling</key>
                <value>None</value>
            </ifl:property>
            <ifl:property>
                <key>accessControlMaxAge</key>
                <value/>
            </ifl:property>
            <ifl:property>
                <key>returnExceptionToSender</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>log</key>
                <value>All events</value>
            </ifl:property>
            <ifl:property>
                <key>corsEnabled</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>exposedHeaders</key>
                <value/>
            </ifl:property>
            <ifl:property>
                <key>componentVersion</key>
                <value>1.2</value>
            </ifl:property>
            <ifl:property>
                <key>allowedHeaderList</key>
                <value/>
            </ifl:property>
            <ifl:property>
                <key>ServerTrace</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>allowedOrigins</key>
                <value/>
            </ifl:property>
            <ifl:property>
                <key>accessControlAllowCredentials</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>allowedHeaders</key>
                <value/>
            </ifl:property>
            <ifl:property>
                <key>allowedMethods</key>
                <value/>
            </ifl:property>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::IFlowVariant/cname::IFlowConfiguration/version::1.2.4</value>
            </ifl:property>
        </bpmn2:extensionElements>
        <bpmn2:participant id="Participant_Process_1" ifl:type="IntegrationProcess" name="Integration Process" processRef="Process_1">
            <bpmn2:extensionElements/>
        </bpmn2:participant>
    </bpmn2:collaboration>
    <bpmn2:process id="Process_1" name="Integration Process">
        <bpmn2:extensionElements>
            <ifl:property>
                <key>transactionTimeout</key>
                <value>30</value>
            </ifl:property>
            <ifl:property>
                <key>componentVersion</key>
                <value>1.2</value>
            </ifl:property>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::FlowElementVariant/cname::IntegrationProcess/version::1.2.1</value>
            </ifl:property>
            <ifl:property>
                <key>transactionalHandling</key>
                <value>Not Required</value>
            </ifl:property>
        </bpmn2:extensionElements>
        <!-- Agent's complete XML embedded here (no start/end events needed) -->
        {component_xml}
    </bpmn2:process>
    <bpmndi:BPMNDiagram id="BPMNDiagram_1" name="Default Collaboration Diagram">
        <bpmndi:BPMNPlane bpmnElement="Collaboration_1" id="BPMNPlane_1">
            <bpmndi:BPMNShape bpmnElement="Participant_Process_1" id="BPMNShape_Participant_Process_1">
                <dc:Bounds height="220.0" width="540.0" x="250.0" y="60.0"/>
            </bpmndi:BPMNShape>
            <bpmndi:BPMNShape bpmnElement="{component_id}" id="BPMNShape_{component_id}">
                <dc:Bounds height="60.0" width="100.0" x="387.0" y="140.0"/>
            </bpmndi:BPMNShape>
        </bpmndi:BPMNPlane>
    </bpmndi:BPMNDiagram>
</bpmn2:definitions>'''
        
        return iflow_xml  # Don't format - keep it exactly as working reference
    
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
        
        # MANIFEST.MF - Match working reference exactly
        manifest_content = f"""Manifest-Version: 1.0
Bundle-ManifestVersion: 2
Bundle-Name: {component_name}
Bundle-SymbolicName: {component_name}; singleton:=true
Bundle-Version: 1.0.0
SAP-BundleType: {"MessageMapping" if bundle_type == "MessageMapping" else "IntegrationFlow"}
SAP-NodeType: IFLMAP
SAP-RuntimeProfile: iflmap
Import-Package: com.sap.esb.application.services.cxf.interceptor,com.sap
 .esb.security,com.sap.it.op.agent.api,com.sap.it.op.agent.collector.cam
 el,com.sap.it.op.agent.collector.cxf,com.sap.it.op.agent.mpl,javax.jms,
 javax.jws,javax.wsdl,javax.xml.bind.annotation,javax.xml.namespace,java
 x.xml.ws,org.apache.camel,org.apache.camel.builder,org.apache.camel.com
 ponent.cxf,org.apache.camel.model,org.apache.camel.processor,org.apache
 .camel.processor.aggregate,org.apache.camel.spring.spi,org.apache.commo
 ns.logging,org.apache.cxf.binding,org.apache.cxf.binding.soap,org.apach
 e.cxf.binding.soap.spring,org.apache.cxf.bus,org.apache.cxf.bus.resourc
 e,org.apache.cxf.bus.spring,org.apache.cxf.buslifecycle,org.apache.cxf.
 catalog,org.apache.cxf.configuration.jsse,org.apache.cxf.configuration.
 spring,org.apache.cxf.endpoint,org.apache.cxf.headers,org.apache.cxf.in
 terceptor,org.apache.cxf.management.counters,org.apache.cxf.message,org
 .apache.cxf.phase,org.apache.cxf.resource,org.apache.cxf.service.factor
 y,org.apache.cxf.service.model,org.apache.cxf.transport,org.apache.cxf.
 transport.common.gzip,org.apache.cxf.transport.http,org.apache.cxf.tran
 sport.http.policy,org.apache.cxf.workqueue,org.apache.cxf.ws.rm.persist
 ence,org.apache.cxf.wsdl11,org.osgi.framework,org.slf4j,org.springframe
 work.beans.factory.config,com.sap.esb.camel.security.cms,org.apache.cam
 el.spi,com.sap.esb.webservice.audit.log,com.sap.esb.camel.endpoint.conf
 igurator.api,com.sap.esb.camel.jdbc.idempotency.reorg,javax.sql,org.apa
 che.camel.processor.idempotent.jdbc,org.osgi.service.blueprint
Origin-Bundle-Name: {component_name}
Origin-Bundle-SymbolicName: {component_name}

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
