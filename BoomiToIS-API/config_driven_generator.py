"""
Configuration-Driven SAP CPI iFlow Generator
Uses template configurations to ensure SAP CPI compliance
"""

import xml.etree.ElementTree as ET
import json
import os
from typing import Dict, List, Any, Tuple
import re

# Import our configuration
from config.iflow_templates import (
    COMPONENT_TEMPLATES, EVENT_TEMPLATES, ADAPTER_TEMPLATES, 
    VALIDATION_RULES, COLLABORATION_PROPERTIES, PROCESS_PROPERTIES,
    SAP_CONSTANTS, ROUTER_FLOW_PROPERTIES, DIAGRAM_POSITIONS
)


class ConfigDrivenIFlowGenerator:
    """Enhanced iFlow generator using configuration-driven approach"""
    
    def __init__(self):
        self.component_templates = COMPONENT_TEMPLATES
        self.event_templates = EVENT_TEMPLATES
        self.adapter_templates = ADAPTER_TEMPLATES
        self.validation_rules = VALIDATION_RULES
        self.collaboration_props = COLLABORATION_PROPERTIES
        self.process_props = PROCESS_PROPERTIES
        self.sap_constants = SAP_CONSTANTS
        self.router_flow_props = ROUTER_FLOW_PROPERTIES
        self.diagram_positions = DIAGRAM_POSITIONS
        
        # Register namespaces
        ET.register_namespace('bpmn2', "http://www.omg.org/spec/BPMN/20100524/MODEL")
        ET.register_namespace('bpmndi', "http://www.omg.org/spec/BPMN/20100524/DI")
        ET.register_namespace('dc', "http://www.omg.org/spec/DD/20100524/DC")
        ET.register_namespace('di', "http://www.omg.org/spec/DD/20100524/DI")
        ET.register_namespace('ifl', "http:///com.sap.ifl.model/Ifl.xsd")
        ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

    def validate_json_against_instructions(self, json_blueprint: Dict) -> List[str]:
        """Validate JSON blueprint against instruction requirements"""
        errors = []
        
        # Check component types are valid
        valid_types = set(self.component_templates.keys())
        for endpoint in json_blueprint.get("endpoints", []):
            for component in endpoint.get("components", []):
                comp_type = component.get("type")
                if comp_type not in valid_types:
                    errors.append(f"Invalid component type: {comp_type}")
        
        # Check sequence flow connectivity
        for endpoint in json_blueprint.get("endpoints", []):
            components = {c["id"]: c for c in endpoint.get("components", [])}
            for flow in endpoint.get("sequence_flows", []):
                if flow["source_ref"] not in components:
                    errors.append(f"Unknown source component: {flow['source_ref']}")
                if flow["target_ref"] not in components and flow["target_ref"] not in ["EndEvent_2", "StartEvent_2"]:
                    errors.append(f"Unknown target component: {flow['target_ref']}")
        
        # Validate forbidden connections
        errors.extend(self._validate_forbidden_connections(json_blueprint))
        
        return errors

    def _validate_forbidden_connections(self, json_blueprint: Dict) -> List[str]:
        """Check for forbidden connection patterns"""
        errors = []
        
        for endpoint in json_blueprint.get("endpoints", []):
            components = {c["id"]: c for c in endpoint.get("components", [])}
            
            for flow in endpoint.get("sequence_flows", []):
                source_ref = flow["source_ref"]
                target_ref = flow["target_ref"]
                
                # Check if source is exception subprocess connecting to main flow
                if source_ref.startswith("SubProcess_") and target_ref == "EndEvent_2":
                    errors.append("FORBIDDEN: Exception subprocess cannot connect to main EndEvent_2")
                
                # Check if source component exists and get its type
                source_comp = components.get(source_ref)
                if source_comp:
                    source_type = source_comp.get("type")
                    
                    # Check for multicast with multiple outgoing (if we had multicast)
                    if source_type == "multicast":
                        outgoing_count = sum(1 for f in endpoint.get("sequence_flows", []) 
                                           if f["source_ref"] == source_ref)
                        if outgoing_count > 1:
                            errors.append(f"FORBIDDEN: Component {source_ref} has multiple outgoing flows")
        
        return errors

    def generate_component(self, component_json: Dict) -> ET.Element:
        """Generate component using configuration templates"""
        component_type = component_json.get("type")
        template = self.component_templates.get(component_type)
        
        if not template:
            raise ValueError(f"Unsupported component type: {component_type}")
        
        # Create element with correct type from instructions
        element = ET.Element(f"bpmn2:{template['element_type']}")
        element.set("id", component_json["id"])
        element.set("name", component_json.get("name", ""))
        
        # Add mandatory attributes (like default for routers, calledElement for LIPs)
        if "mandatory_attributes" in template:
            for attr in template["mandatory_attributes"]:
                if attr == "default" and component_type == "router":
                    # Find default route from config
                    conditions = component_json.get("config", {}).get("conditions", [])
                    default_route = next((c["id"] for c in conditions if c.get("default")), None)
                    if default_route:
                        element.set("default", default_route)
                elif attr == "calledElement" and component_type == "local_integration_process":
                    # Set calledElement to the process ID
                    process_id = f"Process_{component_json['id']}"
                    element.set("calledElement", process_id)
        
        # Handle special cases
        if template.get("special_handling") == "exception_subprocess":
            # Exception subprocess requires specific internal structure
            return self._generate_exception_subprocess(component_json)
        
        # Add extension elements with mandatory properties
        ext_elements = ET.SubElement(element, "bpmn2:extensionElements")
        
        # Add mandatory properties from template
        for prop in template["mandatory_properties"]:
            prop_elem = ET.SubElement(ext_elements, "ifl:property")
            key_elem = ET.SubElement(prop_elem, "key")
            key_elem.text = prop["key"]
            value_elem = ET.SubElement(prop_elem, "value")
            value_elem.text = prop["value"]
        
        # Map config values using instruction mappings
        if "config_mapping" in template:
            config = component_json.get("config", {})
            for json_key, xml_key in template["config_mapping"].items():
                if json_key in config:
                    prop_elem = ET.SubElement(ext_elements, "ifl:property")
                    key_elem = ET.SubElement(prop_elem, "key")
                    key_elem.text = xml_key
                    value_elem = ET.SubElement(prop_elem, "value")
                    value_elem.text = str(config[json_key])
        
        # Special handling for Local Integration Process
        if component_type == "local_integration_process":
            # Add processId property with the process reference
            process_id = f"Process_{component_json['id']}"
            prop_elem = ET.SubElement(ext_elements, "ifl:property")
            key_elem = ET.SubElement(prop_elem, "key")
            key_elem.text = "processId"
            value_elem = ET.SubElement(prop_elem, "value")
            value_elem.text = process_id
        
        # Add incoming/outgoing for gateways (required for property sheets)
        if template.get("requires_incoming_outgoing"):
            # These will be populated during sequence flow processing
            pass
        
        return element

    def _generate_exception_subprocess(self, component_json: Dict) -> ET.Element:
        """Generate exception subprocess with proper SAP CPI structure"""
        subprocess_id = component_json["id"]
        subprocess_name = component_json.get("name", "Exception Subprocess")
        
        # Create subprocess element
        subprocess = ET.Element("bpmn2:subProcess")
        subprocess.set("id", subprocess_id)
        subprocess.set("name", subprocess_name)
        
        # Add mandatory extension elements
        ext_elements = ET.SubElement(subprocess, "bpmn2:extensionElements")
        mandatory_props = [
            {"key": "componentVersion", "value": "1.1"},
            {"key": "activityType", "value": "ErrorEventSubProcessTemplate"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::ErrorEventSubProcessTemplate/version::1.1.0"}
        ]
        
        for prop in mandatory_props:
            prop_elem = ET.SubElement(ext_elements, "ifl:property")
            key_elem = ET.SubElement(prop_elem, "key")
            key_elem.text = prop["key"]
            value_elem = ET.SubElement(prop_elem, "value")
            value_elem.text = prop["value"]
        
        # Add internal structure: EndEvent first, then StartEvent, then SequenceFlow
        end_event_id = f"EndEvent_{subprocess_id}"
        start_event_id = f"StartEvent_{subprocess_id}"
        flow_id = f"SequenceFlow_{subprocess_id}"
        
        # End Event (comes first in working examples)
        end_event = ET.SubElement(subprocess, "bpmn2:endEvent")
        end_event.set("id", end_event_id)
        end_event.set("name", "Error End")
        
        end_ext = ET.SubElement(end_event, "bpmn2:extensionElements")
        end_props = [
            {"key": "componentVersion", "value": "1.1"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0"}
        ]
        for prop in end_props:
            prop_elem = ET.SubElement(end_ext, "ifl:property")
            key_elem = ET.SubElement(prop_elem, "key")
            key_elem.text = prop["key"]
            value_elem = ET.SubElement(prop_elem, "value")
            value_elem.text = prop["value"]
        
        incoming_elem = ET.SubElement(end_event, "bpmn2:incoming")
        incoming_elem.text = flow_id
        
        msg_def_end = ET.SubElement(end_event, "bpmn2:messageEventDefinition")
        
        # Start Event (Error Start)
        start_event = ET.SubElement(subprocess, "bpmn2:startEvent")
        start_event.set("id", start_event_id)
        start_event.set("name", "Error Start")
        
        outgoing_elem = ET.SubElement(start_event, "bpmn2:outgoing")
        outgoing_elem.text = flow_id
        
        # Error event definition with nested extensions
        error_def = ET.SubElement(start_event, "bpmn2:errorEventDefinition")
        error_ext = ET.SubElement(error_def, "bpmn2:extensionElements")
        error_props = [
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::ErrorStartEvent"},
            {"key": "activityType", "value": "StartErrorEvent"}
        ]
        for prop in error_props:
            prop_elem = ET.SubElement(error_ext, "ifl:property")
            key_elem = ET.SubElement(prop_elem, "key")
            key_elem.text = prop["key"]
            value_elem = ET.SubElement(prop_elem, "value")
            value_elem.text = prop["value"]
        
        # Sequence Flow
        seq_flow = ET.SubElement(subprocess, "bpmn2:sequenceFlow")
        seq_flow.set("id", flow_id)
        seq_flow.set("sourceRef", start_event_id)
        seq_flow.set("targetRef", end_event_id)
        
        return subprocess

    def generate_start_event(self) -> ET.Element:
        """Generate standard message start event"""
        template = self.event_templates["start_event"]
        
        start_event = ET.Element("bpmn2:startEvent")
        start_event.set("id", "StartEvent_2")
        start_event.set("name", "Start")
        
        # Add extension elements
        ext_elements = ET.SubElement(start_event, "bpmn2:extensionElements")
        for prop in template["mandatory_properties"]:
            prop_elem = ET.SubElement(ext_elements, "ifl:property")
            key_elem = ET.SubElement(prop_elem, "key")
            key_elem.text = prop["key"]
            value_elem = ET.SubElement(prop_elem, "value")
            value_elem.text = prop["value"]
        
        # Add outgoing flow placeholder
        outgoing = ET.SubElement(start_event, "bpmn2:outgoing")
        outgoing.text = "{{outgoing_flow}}"
        
        # Add message event definition
        msg_def = ET.SubElement(start_event, "bpmn2:messageEventDefinition")
        msg_def.set("id", "MessageEventDefinition_StartEvent_2")
        
        return start_event

    def generate_end_event(self) -> ET.Element:
        """Generate standard message end event"""
        template = self.event_templates["end_event"]
        
        end_event = ET.Element("bpmn2:endEvent")
        end_event.set("id", "EndEvent_2")
        end_event.set("name", "End")
        
        # Add extension elements
        ext_elements = ET.SubElement(end_event, "bpmn2:extensionElements")
        for prop in template["mandatory_properties"]:
            prop_elem = ET.SubElement(ext_elements, "ifl:property")
            key_elem = ET.SubElement(prop_elem, "key")
            key_elem.text = prop["key"]
            value_elem = ET.SubElement(prop_elem, "value")
            value_elem.text = prop["value"]
        
        # Add incoming flow placeholders
        incoming = ET.SubElement(end_event, "bpmn2:incoming")
        incoming.text = "{{incoming_flows}}"
        
        # Add message event definition
        msg_def = ET.SubElement(end_event, "bpmn2:messageEventDefinition")
        msg_def.set("id", "MessageEventDefinition_EndEvent_2")
        
        return end_event

    def generate_sequence_flow(self, flow_json: Dict, components: Dict) -> ET.Element:
        """Generate sequence flow with proper SAP CPI attributes"""
        flow = ET.Element("bpmn2:sequenceFlow")
        flow.set("id", flow_json["id"])
        flow.set("sourceRef", flow_json["source_ref"])
        flow.set("targetRef", flow_json["target_ref"])
        flow.set("isImmediate", "true")  # Mandatory per instructions
        
        # Check if this is a router conditional flow
        source_comp = components.get(flow_json["source_ref"])
        if source_comp and source_comp.get("type") == "router":
            # Find the condition for this flow
            conditions = source_comp.get("config", {}).get("conditions", [])
            condition = next((c for c in conditions if c.get("id") == flow_json["id"]), None)
            
            if condition:
                # Add name attribute
                if condition.get("name"):
                    flow.set("name", condition["name"])
                
                # Add conditional expression and extensions for non-default routes
                if not condition.get("default", False):
                    # Add condition expression
                    cond_expr = ET.SubElement(flow, "bpmn2:conditionExpression")
                    cond_expr.set("{http://www.w3.org/2001/XMLSchema-instance}type", "bpmn2:tFormalExpression")
                    cond_expr.text = condition.get("expression", "")
                    
                    # Add SAP-specific extensions for conditional routes
                    ext_elements = ET.SubElement(flow, "bpmn2:extensionElements")
                    for prop in self.router_flow_props["conditional"]:
                        prop_elem = ET.SubElement(ext_elements, "ifl:property")
                        key_elem = ET.SubElement(prop_elem, "key")
                        key_elem.text = prop["key"]
                        value_elem = ET.SubElement(prop_elem, "value")
                        value_elem.text = prop["value"]
                else:
                    # Default route extensions
                    ext_elements = ET.SubElement(flow, "bpmn2:extensionElements")
                    for prop in self.router_flow_props["default"]:
                        prop_elem = ET.SubElement(ext_elements, "ifl:property")
                        key_elem = ET.SubElement(prop_elem, "key")
                        key_elem.text = prop["key"]
                        value_elem = ET.SubElement(prop_elem, "value")
                        value_elem.text = prop["value"]
        
        return flow

    def generate_collaboration(self, components: List[Dict]) -> ET.Element:
        """Generate collaboration with mandatory properties"""
        collaboration = ET.Element("bpmn2:collaboration")
        collaboration.set("id", "Collaboration_1")
        collaboration.set("name", "Default Collaboration")
        
        # Add mandatory extension elements
        ext_elements = ET.SubElement(collaboration, "bpmn2:extensionElements")
        for prop in self.collaboration_props:
            prop_elem = ET.SubElement(ext_elements, "ifl:property")
            key_elem = ET.SubElement(prop_elem, "key")
            key_elem.text = prop["key"]
            value_elem = ET.SubElement(prop_elem, "value")
            value_elem.text = prop["value"]
        
        # Add participants
        # Sender participant
        sender = ET.SubElement(collaboration, "bpmn2:participant")
        sender.set("id", "Participant_Sender")
        sender.set("ifl:type", self.sap_constants["ENDPOINT_SENDER"])
        sender.set("name", "Sender")
        
        sender_ext = ET.SubElement(sender, "bpmn2:extensionElements")
        sender_prop = ET.SubElement(sender_ext, "ifl:property")
        sender_key = ET.SubElement(sender_prop, "key")
        sender_key.text = "ifl:type"
        sender_value = ET.SubElement(sender_prop, "value")
        sender_value.text = self.sap_constants["ENDPOINT_SENDER"]
        
        # Integration Process participant
        int_process = ET.SubElement(collaboration, "bpmn2:participant")
        int_process.set("id", "Participant_Process_1")
        int_process.set("ifl:type", self.sap_constants["INTEGRATION_PROCESS"])
        int_process.set("name", "Integration Process")
        int_process.set("processRef", "Process_1")
        
        int_ext = ET.SubElement(int_process, "bpmn2:extensionElements")
        
        # Add receiver participants for components that need them
        for comp in components:
            comp_type = comp.get("type")
            if comp_type in ["request_reply", "odata", "soap", "successfactors"]:
                # Create receiver participant
                receiver = ET.SubElement(collaboration, "bpmn2:participant")
                receiver.set("id", f"Participant_{comp['id']}")
                receiver.set("ifl:type", self.sap_constants["ENDPOINT_RECEIVER_TYPO"])  # SAP's typo
                receiver.set("name", f"{comp.get('name', comp['id'])}_Receiver")
                
                receiver_ext = ET.SubElement(receiver, "bpmn2:extensionElements")
                receiver_prop = ET.SubElement(receiver_ext, "ifl:property")
                receiver_key = ET.SubElement(receiver_prop, "key")
                receiver_key.text = "ifl:type"
                receiver_value = ET.SubElement(receiver_prop, "value")
                receiver_value.text = self.sap_constants["ENDPOINT_RECEIVER_TYPO"]
        
        return collaboration

    def generate_process(self, components: List[Dict], sequence_flows: List[Dict]) -> ET.Element:
        """Generate process with mandatory properties"""
        process = ET.Element("bpmn2:process")
        process.set("id", "Process_1")
        process.set("name", "Integration Process")
        process.set("isExecutable", "true")  # MANDATORY per instructions
        
        # Add mandatory extension elements
        ext_elements = ET.SubElement(process, "bpmn2:extensionElements")
        for prop in self.process_props:
            prop_elem = ET.SubElement(ext_elements, "ifl:property")
            key_elem = ET.SubElement(prop_elem, "key")
            key_elem.text = prop["key"]
            value_elem = ET.SubElement(prop_elem, "value")
            value_elem.text = prop["value"]
        
        # Add start event
        start_event = self.generate_start_event()
        process.append(start_event)
        
        # Add components
        component_map = {}
        for comp in components:
            element = self.generate_component(comp)
            process.append(element)
            component_map[comp["id"]] = element
        
        # Add end event
        end_event = self.generate_end_event()
        process.append(end_event)
        
        # Add sequence flows
        for flow_json in sequence_flows:
            flow = self.generate_sequence_flow(flow_json, {c["id"]: c for c in components})
            process.append(flow)
        
        # Update gateway incoming/outgoing references for property sheets
        self._update_gateway_references(process, sequence_flows)
        
        return process

    def _update_gateway_references(self, process: ET.Element, sequence_flows: List[Dict]):
        """Update gateway incoming/outgoing references for proper property sheet display"""
        ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        
        # Build flow maps
        incoming_map = {}
        outgoing_map = {}
        
        for flow in sequence_flows:
            source = flow["source_ref"]
            target = flow["target_ref"]
            flow_id = flow["id"]
            
            if target not in incoming_map:
                incoming_map[target] = []
            incoming_map[target].append(flow_id)
            
            if source not in outgoing_map:
                outgoing_map[source] = []
            outgoing_map[source].append(flow_id)
        
        # Update gateways
        for gateway in process.findall(".//bpmn2:exclusiveGateway", ns):
            gateway_id = gateway.get("id")
            
            # Add incoming
            if gateway_id in incoming_map:
                for flow_id in incoming_map[gateway_id]:
                    incoming = ET.SubElement(gateway, "bpmn2:incoming")
                    incoming.text = flow_id
            
            # Add outgoing
            if gateway_id in outgoing_map:
                for flow_id in outgoing_map[gateway_id]:
                    outgoing = ET.SubElement(gateway, "bpmn2:outgoing")
                    outgoing.text = flow_id

    def post_process_xml(self, root: ET.Element, components: List[Dict]) -> ET.Element:
        """Apply instruction-based post-processing to ensure compliance"""
        
        # 1. Ensure mandatory elements
        self._ensure_mandatory_elements(root)
        
        # 2. Fix router flows
        self._fix_router_flows(root, components)
        
        # 3. Remove forbidden connections
        self._remove_forbidden_connections(root)
        
        # 4. Ensure proper flow connectivity
        self._ensure_flow_connectivity(root)
        
        return root

    def _ensure_mandatory_elements(self, root: ET.Element):
        """Add mandatory elements from instructions"""
        ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        
        # Ensure process has isExecutable="true"
        for process in root.findall(".//bpmn2:process", ns):
            process.set("isExecutable", "true")
        
        # Ensure collaboration has mandatory properties
        collaboration = root.find(".//bpmn2:collaboration", ns)
        if collaboration is not None:
            self._add_mandatory_collaboration_properties(collaboration)

    def _add_mandatory_collaboration_properties(self, collaboration: ET.Element):
        """Add mandatory collaboration properties if missing"""
        ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        
        ext_elements = collaboration.find("bpmn2:extensionElements", ns)
        if ext_elements is None:
            ext_elements = ET.SubElement(collaboration, "bpmn2:extensionElements")
        
        # Check existing properties
        existing_keys = set()
        for prop in ext_elements.findall("ifl:property", {"ifl": "http:///com.sap.ifl.model/Ifl.xsd"}):
            key_elem = prop.find("key")
            if key_elem is not None:
                existing_keys.add(key_elem.text)
        
        # Add missing mandatory properties
        for prop in self.collaboration_props:
            if prop["key"] not in existing_keys:
                prop_elem = ET.SubElement(ext_elements, "ifl:property")
                key_elem = ET.SubElement(prop_elem, "key")
                key_elem.text = prop["key"]
                value_elem = ET.SubElement(prop_elem, "value")
                value_elem.text = prop["value"]

    def _remove_forbidden_connections(self, root: ET.Element):
        """Remove forbidden connections per SAP CPI instructions"""
        ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        
        # Find exception subprocess IDs
        exc_ids = set()
        for subprocess in root.findall(".//bpmn2:subProcess", ns):
            subprocess_id = subprocess.get("id", "")
            if subprocess_id.startswith("SubProcess_"):
                exc_ids.add(subprocess_id)
        
        # Remove flows from exception subprocess to main EndEvent_2
        for process in root.findall(".//bpmn2:process", ns):
            for flow in list(process.findall(".//bpmn2:sequenceFlow", ns)):
                source_ref = flow.get("sourceRef")
                target_ref = flow.get("targetRef")
                
                if source_ref in exc_ids and target_ref == "EndEvent_2":
                    process.remove(flow)
                    print(f"Removed forbidden connection: {source_ref} -> {target_ref}")

    def _ensure_flow_connectivity(self, root: ET.Element):
        """Ensure all main routing branches connect to EndEvent_2"""
        ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        
        # This would be implemented based on specific flow patterns
        # For now, just ensure basic connectivity rules are met
        pass

    def _fix_router_flows(self, root: ET.Element, components: List[Dict]):
        """Fix router flows according to instruction rules"""
        # This method would enhance router flows with proper extensions
        # Already handled in generate_sequence_flow method
        pass
