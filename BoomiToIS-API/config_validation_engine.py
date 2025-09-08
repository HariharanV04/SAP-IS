"""
Configuration-Based Validation Engine for SAP CPI iFlow Generation
Validates JSON blueprints and generated XML against SAP CPI instruction requirements
"""

import xml.etree.ElementTree as ET
import json
import re
from typing import Dict, List, Any, Tuple, Set

from config.iflow_templates import VALIDATION_RULES, SAP_CONSTANTS


class ConfigValidationEngine:
    """Validation engine using configuration-driven rules"""
    
    def __init__(self):
        self.validation_rules = VALIDATION_RULES
        self.sap_constants = SAP_CONSTANTS

    def validate_json_blueprint(self, json_blueprint: Dict) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation of JSON blueprint against SAP CPI requirements
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # 1. Structural validation
        errors.extend(self._validate_structure(json_blueprint))
        
        # 2. Component type validation
        errors.extend(self._validate_component_types(json_blueprint))
        
        # 3. Sequence flow validation
        errors.extend(self._validate_sequence_flows(json_blueprint))
        
        # 4. Forbidden connections validation
        errors.extend(self._validate_forbidden_connections(json_blueprint))
        
        # 5. Flow continuity validation
        errors.extend(self._validate_flow_continuity(json_blueprint))
        
        # 6. Router validation
        errors.extend(self._validate_routers(json_blueprint))
        
        # 7. Exception subprocess validation
        errors.extend(self._validate_exception_subprocesses(json_blueprint))
        
        is_valid = len(errors) == 0
        return is_valid, errors

    def _validate_structure(self, json_blueprint: Dict) -> List[str]:
        """Validate basic JSON structure"""
        errors = []
        
        if not isinstance(json_blueprint, dict):
            errors.append("JSON blueprint must be a dictionary")
            return errors
        
        if "endpoints" not in json_blueprint:
            errors.append("JSON blueprint must contain 'endpoints' array")
            return errors
        
        endpoints = json_blueprint.get("endpoints", [])
        if not isinstance(endpoints, list) or len(endpoints) == 0:
            errors.append("'endpoints' must be a non-empty array")
            return errors
        
        for i, endpoint in enumerate(endpoints):
            if not isinstance(endpoint, dict):
                errors.append(f"Endpoint {i} must be a dictionary")
                continue
            
            if "components" not in endpoint:
                errors.append(f"Endpoint {i} must contain 'components' array")
            
            if "sequence_flows" not in endpoint:
                errors.append(f"Endpoint {i} should contain 'sequence_flows' array")
        
        return errors

    def _validate_component_types(self, json_blueprint: Dict) -> List[str]:
        """Validate that all component types are supported"""
        errors = []
        
        # Import here to avoid circular imports
        from config.iflow_templates import COMPONENT_TEMPLATES
        
        valid_types = set(COMPONENT_TEMPLATES.keys())
        
        for endpoint in json_blueprint.get("endpoints", []):
            for i, component in enumerate(endpoint.get("components", [])):
                if not isinstance(component, dict):
                    errors.append(f"Component {i} must be a dictionary")
                    continue
                
                comp_type = component.get("type")
                if not comp_type:
                    errors.append(f"Component {i} missing 'type' field")
                    continue
                
                if comp_type not in valid_types:
                    errors.append(f"Unsupported component type: '{comp_type}' in component {component.get('id', i)}")
                
                # Check required fields
                if not component.get("id"):
                    errors.append(f"Component {i} missing 'id' field")
                
                if not component.get("name"):
                    errors.append(f"Component {component.get('id', i)} missing 'name' field")
        
        return errors

    def _validate_sequence_flows(self, json_blueprint: Dict) -> List[str]:
        """Validate sequence flow connectivity"""
        errors = []
        
        for endpoint in json_blueprint.get("endpoints", []):
            components = {c["id"]: c for c in endpoint.get("components", []) if c.get("id")}
            sequence_flows = endpoint.get("sequence_flows", [])
            
            # Check all flows have required fields
            for i, flow in enumerate(sequence_flows):
                if not isinstance(flow, dict):
                    errors.append(f"Sequence flow {i} must be a dictionary")
                    continue
                
                required_fields = ["id", "source_ref", "target_ref"]
                for field in required_fields:
                    if not flow.get(field):
                        errors.append(f"Sequence flow {i} missing '{field}' field")
                
                # Check source and target exist
                source_ref = flow.get("source_ref")
                target_ref = flow.get("target_ref")
                
                if source_ref and source_ref not in components and source_ref != "StartEvent_2":
                    errors.append(f"Flow {flow.get('id', i)}: Unknown source component '{source_ref}'")
                
                if target_ref and target_ref not in components and target_ref not in ["EndEvent_2", "StartEvent_2"]:
                    errors.append(f"Flow {flow.get('id', i)}: Unknown target component '{target_ref}'")
            
            # Check for duplicate flow IDs
            flow_ids = [f["id"] for f in sequence_flows if f.get("id")]
            duplicate_ids = [fid for fid in flow_ids if flow_ids.count(fid) > 1]
            if duplicate_ids:
                errors.append(f"Duplicate sequence flow IDs: {set(duplicate_ids)}")
        
        return errors

    def _validate_forbidden_connections(self, json_blueprint: Dict) -> List[str]:
        """Validate against forbidden connection patterns"""
        errors = []
        
        for endpoint in json_blueprint.get("endpoints", []):
            components = {c["id"]: c for c in endpoint.get("components", []) if c.get("id")}
            sequence_flows = endpoint.get("sequence_flows", [])
            
            for flow in sequence_flows:
                source_ref = flow.get("source_ref")
                target_ref = flow.get("target_ref")
                
                if not source_ref or not target_ref:
                    continue
                
                # Rule 1: Exception subprocess cannot connect to main EndEvent_2
                if source_ref.startswith("SubProcess_") and target_ref == "EndEvent_2":
                    errors.append(f"FORBIDDEN: Exception subprocess '{source_ref}' cannot connect to main EndEvent_2")
                
                # Rule 2: Check for multiple outgoing flows from non-gateway components
                source_comp = components.get(source_ref)
                if source_comp:
                    source_type = source_comp.get("type")
                    if source_type not in ["router", "parallel_gateway", "exclusive_gateway"]:
                        # Count outgoing flows from this component
                        outgoing_count = sum(1 for f in sequence_flows if f.get("source_ref") == source_ref)
                        if outgoing_count > 1:
                            errors.append(f"FORBIDDEN: Non-gateway component '{source_ref}' has multiple outgoing flows")
        
        return errors

    def _validate_flow_continuity(self, json_blueprint: Dict) -> List[str]:
        """Validate flow continuity requirements"""
        errors = []
        
        for endpoint in json_blueprint.get("endpoints", []):
            components = {c["id"]: c for c in endpoint.get("components", []) if c.get("id")}
            sequence_flows = endpoint.get("sequence_flows", [])
            
            # Build incoming/outgoing maps
            incoming_map = {}
            outgoing_map = {}
            
            for flow in sequence_flows:
                source_ref = flow.get("source_ref")
                target_ref = flow.get("target_ref")
                
                if target_ref:
                    if target_ref not in incoming_map:
                        incoming_map[target_ref] = []
                    incoming_map[target_ref].append(source_ref)
                
                if source_ref:
                    if source_ref not in outgoing_map:
                        outgoing_map[source_ref] = []
                    outgoing_map[source_ref].append(target_ref)
            
            # Rule 1: Every component except StartEvent and first component must have incoming flow
            # Find the first component (connected to StartEvent)
            start_targets = outgoing_map.get("StartEvent_2", [])
            first_component = start_targets[0] if start_targets else None
            
            for comp_id, comp in components.items():
                comp_type = comp.get("type")
                # Skip validation for first component and exception subprocess
                if comp_id == first_component or comp_type == "exception_subprocess":
                    continue
                    
                if comp_id not in incoming_map:
                    errors.append(f"CONTINUITY: Component '{comp_id}' has no incoming flow")
            
            # Rule 2: Every component except EndEvent and Exception Subprocess must have outgoing flow
            for comp_id, comp in components.items():
                comp_type = comp.get("type")
                if comp_type != "exception_subprocess" and comp_id not in outgoing_map:
                    errors.append(f"CONTINUITY: Component '{comp_id}' has no outgoing flow")
            
            # Rule 3: All main branches should end at EndEvent_2
            end_targets = outgoing_map.get("EndEvent_2", [])
            main_components = [cid for cid, comp in components.items() 
                             if comp.get("type") != "exception_subprocess"]
            
            # Find components that don't connect to EndEvent_2 (warning, not error)
            for comp_id in main_components:
                if comp_id in outgoing_map:
                    targets = outgoing_map[comp_id]
                    if "EndEvent_2" not in targets and all(t in components for t in targets):
                        # This component connects to other components, check if they eventually reach EndEvent_2
                        if not self._can_reach_end_event(comp_id, outgoing_map, components):
                            errors.append(f"WARNING: Component '{comp_id}' may not reach EndEvent_2")
        
        return errors

    def _can_reach_end_event(self, start_comp: str, outgoing_map: Dict, components: Dict, visited: Set[str] = None) -> bool:
        """Check if a component can reach EndEvent_2 through sequence flows"""
        if visited is None:
            visited = set()
        
        if start_comp in visited:
            return False  # Circular reference
        
        visited.add(start_comp)
        
        targets = outgoing_map.get(start_comp, [])
        
        if "EndEvent_2" in targets:
            return True
        
        for target in targets:
            if target in components:  # Only follow to other components
                if self._can_reach_end_event(target, outgoing_map, components, visited.copy()):
                    return True
        
        return False

    def _validate_routers(self, json_blueprint: Dict) -> List[str]:
        """Validate router-specific requirements"""
        errors = []
        
        for endpoint in json_blueprint.get("endpoints", []):
            components = {c["id"]: c for c in endpoint.get("components", []) if c.get("id")}
            sequence_flows = endpoint.get("sequence_flows", [])
            
            # Find routers
            routers = {cid: comp for cid, comp in components.items() if comp.get("type") == "router"}
            
            for router_id, router in routers.items():
                config = router.get("config", {})
                conditions = config.get("conditions", [])
                
                # Check that router has conditions
                if not conditions:
                    errors.append(f"Router '{router_id}' has no conditions defined")
                    continue
                
                # Check that exactly one condition is marked as default
                default_conditions = [c for c in conditions if c.get("default", False)]
                if len(default_conditions) != 1:
                    errors.append(f"Router '{router_id}' must have exactly one default condition, found {len(default_conditions)}")
                
                # Check that all conditions have corresponding sequence flows
                condition_ids = {c.get("id") for c in conditions if c.get("id")}
                router_flows = {f["id"] for f in sequence_flows if f.get("source_ref") == router_id}
                
                missing_flows = condition_ids - router_flows
                if missing_flows:
                    errors.append(f"Router '{router_id}' missing sequence flows for conditions: {missing_flows}")
                
                extra_flows = router_flows - condition_ids
                if extra_flows:
                    errors.append(f"Router '{router_id}' has extra sequence flows not in conditions: {extra_flows}")
        
        return errors

    def _validate_exception_subprocesses(self, json_blueprint: Dict) -> List[str]:
        """Validate exception subprocess requirements"""
        errors = []
        
        for endpoint in json_blueprint.get("endpoints", []):
            components = {c["id"]: c for c in endpoint.get("components", []) if c.get("id")}
            sequence_flows = endpoint.get("sequence_flows", [])
            
            # Find exception subprocesses
            exc_subprocesses = {cid: comp for cid, comp in components.items() 
                              if comp.get("type") == "exception_subprocess"}
            
            for exc_id, exc_comp in exc_subprocesses.items():
                # Check that exception subprocess doesn't have outgoing flows to main process
                outgoing_flows = [f for f in sequence_flows if f.get("source_ref") == exc_id]
                for flow in outgoing_flows:
                    target = flow.get("target_ref")
                    if target == "EndEvent_2":
                        errors.append(f"Exception subprocess '{exc_id}' cannot connect to main EndEvent_2")
                    elif target in components and components[target].get("type") != "exception_subprocess":
                        errors.append(f"Exception subprocess '{exc_id}' cannot connect to main process component '{target}'")
        
        return errors

    def validate_generated_xml(self, xml_content: str) -> Tuple[bool, List[str]]:
        """
        Validate generated XML against SAP CPI requirements
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            errors.append(f"XML Parse Error: {e}")
            return False, errors
        
        # 1. Namespace validation
        errors.extend(self._validate_xml_namespaces(root))
        
        # 2. Mandatory attributes validation
        errors.extend(self._validate_mandatory_attributes(root))
        
        # 3. SAP-specific validation
        errors.extend(self._validate_sap_specifics(root))
        
        # 4. Component properties validation
        errors.extend(self._validate_component_properties(root))
        
        # 5. Flow structure validation
        errors.extend(self._validate_xml_flow_structure(root))
        
        is_valid = len(errors) == 0
        return is_valid, errors

    def _validate_xml_namespaces(self, root: ET.Element) -> List[str]:
        """Validate XML namespaces"""
        errors = []
        
        required_namespaces = [
            "http://www.omg.org/spec/BPMN/20100524/MODEL",
            "http://www.omg.org/spec/BPMN/20100524/DI",
            "http://www.omg.org/spec/DD/20100524/DC",
            "http://www.omg.org/spec/DD/20100524/DI",
            "http:///com.sap.ifl.model/Ifl.xsd",
            "http://www.w3.org/2001/XMLSchema-instance"
        ]
        
        # Check if all required namespaces are declared
        xmlns_attrs = {k: v for k, v in root.attrib.items() if k.startswith("{http://www.w3.org/2000/xmlns/}")}
        declared_namespaces = set(xmlns_attrs.values())
        
        missing_namespaces = [ns for ns in required_namespaces if ns not in declared_namespaces]
        if missing_namespaces:
            errors.append(f"Missing required namespaces: {missing_namespaces}")
        
        return errors

    def _validate_mandatory_attributes(self, root: ET.Element) -> List[str]:
        """Validate mandatory attributes"""
        errors = []
        ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        
        # Check processes have isExecutable="true"
        processes = root.findall(".//bpmn2:process", ns)
        for process in processes:
            if process.get("isExecutable") != "true":
                errors.append(f"Process '{process.get('id')}' must have isExecutable='true'")
        
        # Check sequence flows have mandatory attributes
        seq_flows = root.findall(".//bpmn2:sequenceFlow", ns)
        for flow in seq_flows:
            flow_id = flow.get("id", "unknown")
            required_attrs = ["id", "sourceRef", "targetRef", "isImmediate"]
            
            for attr in required_attrs:
                if not flow.get(attr):
                    errors.append(f"SequenceFlow '{flow_id}' missing mandatory attribute '{attr}'")
        
        # Check exclusive gateways have default attribute
        gateways = root.findall(".//bpmn2:exclusiveGateway", ns)
        for gateway in gateways:
            gateway_id = gateway.get("id", "unknown")
            if not gateway.get("default"):
                errors.append(f"ExclusiveGateway '{gateway_id}' missing mandatory 'default' attribute")
        
        return errors

    def _validate_sap_specifics(self, root: ET.Element) -> List[str]:
        """Validate SAP-specific requirements"""
        errors = []
        ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        
        # Check for correct EndpointRecevier spelling (SAP's typo)
        participants = root.findall(".//bpmn2:participant", ns)
        for participant in participants:
            ifl_type = participant.get("ifl:type")
            if ifl_type and "Receiver" in ifl_type and ifl_type != self.sap_constants["ENDPOINT_RECEIVER_TYPO"]:
                errors.append(f"Participant '{participant.get('id')}' should use 'EndpointRecevier' (SAP's intentional typo), not '{ifl_type}'")
        
        return errors

    def _validate_component_properties(self, root: ET.Element) -> List[str]:
        """Validate component extension properties"""
        errors = []
        ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL",
              "ifl": "http:///com.sap.ifl.model/Ifl.xsd"}
        
        # Check that all components have required extension properties
        components = (root.findall(".//bpmn2:callActivity", ns) + 
                     root.findall(".//bpmn2:serviceTask", ns) +
                     root.findall(".//bpmn2:exclusiveGateway", ns) +
                     root.findall(".//bpmn2:subProcess", ns))
        
        for component in components:
            comp_id = component.get("id", "unknown")
            ext_elements = component.find("bpmn2:extensionElements", ns)
            
            if ext_elements is None:
                errors.append(f"Component '{comp_id}' missing extensionElements")
                continue
            
            # Check for mandatory properties
            properties = ext_elements.findall("ifl:property", ns)
            prop_keys = set()
            
            for prop in properties:
                key_elem = prop.find("key")
                if key_elem is not None:
                    prop_keys.add(key_elem.text)
            
            # All components should have these
            required_props = ["componentVersion", "activityType", "cmdVariantUri"]
            missing_props = [prop for prop in required_props if prop not in prop_keys]
            
            if missing_props:
                errors.append(f"Component '{comp_id}' missing required properties: {missing_props}")
        
        return errors

    def _validate_xml_flow_structure(self, root: ET.Element) -> List[str]:
        """Validate XML flow structure"""
        errors = []
        ns = {"bpmn2": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        
        # Check for forbidden exception subprocess connections
        subprocesses = root.findall(".//bpmn2:subProcess", ns)
        exc_subprocess_ids = {sp.get("id") for sp in subprocesses if sp.get("id", "").startswith("SubProcess_")}
        
        seq_flows = root.findall(".//bpmn2:sequenceFlow", ns)
        for flow in seq_flows:
            source_ref = flow.get("sourceRef")
            target_ref = flow.get("targetRef")
            
            if source_ref in exc_subprocess_ids and target_ref == "EndEvent_2":
                errors.append(f"XML VALIDATION: Exception subprocess '{source_ref}' connects to main EndEvent_2")
        
        return errors

    def generate_validation_report(self, json_blueprint: Dict, xml_content: str = None) -> str:
        """Generate comprehensive validation report"""
        report = ["=" * 60]
        report.append("SAP CPI iFlow Validation Report")
        report.append("=" * 60)
        
        # JSON validation
        json_valid, json_errors = self.validate_json_blueprint(json_blueprint)
        
        report.append(f"\n1. JSON BLUEPRINT VALIDATION")
        report.append(f"   Status: {'✅ PASSED' if json_valid else '❌ FAILED'}")
        
        if json_errors:
            report.append(f"   Errors ({len(json_errors)}):")
            for error in json_errors:
                report.append(f"     • {error}")
        else:
            report.append("   No errors found")
        
        # XML validation (if provided)
        if xml_content:
            xml_valid, xml_errors = self.validate_generated_xml(xml_content)
            
            report.append(f"\n2. GENERATED XML VALIDATION")
            report.append(f"   Status: {'✅ PASSED' if xml_valid else '❌ FAILED'}")
            
            if xml_errors:
                report.append(f"   Errors ({len(xml_errors)}):")
                for error in xml_errors:
                    report.append(f"     • {error}")
            else:
                report.append("   No errors found")
        
        # Overall status
        overall_valid = json_valid and (xml_content is None or xml_valid)
        report.append(f"\n3. OVERALL STATUS")
        report.append(f"   Result: {'✅ COMPLIANT' if overall_valid else '❌ NON-COMPLIANT'}")
        
        if overall_valid:
            report.append("   The iFlow meets all SAP CPI requirements")
        else:
            report.append("   The iFlow requires fixes before deployment")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
