#!/usr/bin/env python3
"""
iFlow Post-Generation Sanitizer
Performs cleanup and validation after iFlow generation to ensure SAP compliance
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class IFlowSanitizer:
    """Sanitizes generated iFlow XML to ensure SAP Integration Suite compatibility"""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
    
    def sanitize_iflow(self, iflow_xml: str) -> str:
        """Main sanitization method - applies all cleanup steps"""
        print("🧹 Starting iFlow sanitization...")
        
        # Reset tracking
        self.issues_found = []
        self.fixes_applied = []
        
        # Apply sanitization steps
        iflow_xml = self._remove_orphaned_flows(iflow_xml)
        iflow_xml = self._fix_empty_flow_references(iflow_xml)
        iflow_xml = self._remove_duplicate_flows(iflow_xml)
        iflow_xml = self._generate_missing_bpmn_edges(iflow_xml)
        iflow_xml = self._generate_bpmn_edges_for_flows(iflow_xml) # Added this line
        iflow_xml = self._validate_flow_consistency(iflow_xml)
        iflow_xml = self._cleanup_empty_lines(iflow_xml)
        
        # Report results
        self._report_sanitization_results()
        
        return iflow_xml
    
    def _remove_orphaned_flows(self, iflow_xml: str) -> str:
        """Remove sequence flows that reference non-existent components"""
        print("  🔍 Checking for orphaned sequence flows...")
        
        # Find all sequence flows (both self-closing and opening/closing tags)
        flow_pattern = r'<bpmn2:sequenceFlow[^>]*(?:/>|>.*?</bpmn2:sequenceFlow>)'
        flows = re.findall(flow_pattern, iflow_xml, re.DOTALL)
        
        # Find all component IDs (StartEvent, EndEvent, serviceTask, etc.)
        component_pattern = r'<bpmn2:(?:startEvent|endEvent|serviceTask|callActivity|exclusiveGateway|inclusiveGateway|parallelGateway|subProcess|userTask|scriptTask|businessRuleTask|manualTask|receiveTask|sendTask|task)[^>]*id="([^"]*)"'
        component_ids = set(re.findall(component_pattern, iflow_xml))
        
        # Add StartEvent_2 and EndEvent_2 explicitly (they might not match the pattern)
        component_ids.add("StartEvent_2")
        component_ids.add("EndEvent_2")
        
        removed_flows = []
        
        for flow in flows:
            # Extract source and target references
            source_match = re.search(r'sourceRef="([^"]*)"', flow)
            target_match = re.search(r'targetRef="([^"]*)"', flow)
            
            if source_match and target_match:
                source_ref = source_match.group(1)
                target_ref = target_match.group(1)
                
                # Check if both references exist
                if source_ref not in component_ids or target_ref not in component_ids:
                    removed_flows.append(flow)
                    self.issues_found.append(f"Orphaned flow: {source_ref} -> {target_ref}")
                    self.fixes_applied.append(f"Removed orphaned flow: {flow[:50]}...")
        
        # Remove orphaned flows
        for flow in removed_flows:
            iflow_xml = iflow_xml.replace(flow, '')
        
        if removed_flows:
            print(f"    ✅ Removed {len(removed_flows)} orphaned flows")
        else:
            print("    ✅ No orphaned flows found")
        
        return iflow_xml
    
    def _fix_empty_flow_references(self, iflow_xml: str) -> str:
        """Fix sequence flows with empty sourceRef or targetRef"""
        print("  🔍 Checking for empty flow references...")
        
        # Find flows with empty references (both self-closing and opening/closing tags)
        empty_ref_pattern = r'<bpmn2:sequenceFlow[^>]*sourceRef=""[^>]*(?:/>|>.*?</bpmn2:sequenceFlow>)'
        empty_ref_flows = re.findall(empty_ref_pattern, iflow_xml, re.DOTALL)
        
        if empty_ref_flows:
            print(f"    ❌ Found {len(empty_ref_flows)} flows with empty references")
            self.issues_found.append(f"Found {len(empty_ref_flows)} flows with empty references")
            
            # Remove these invalid flows
            for flow in empty_ref_flows:
                iflow_xml = iflow_xml.replace(flow, '')
                self.fixes_applied.append(f"Removed flow with empty references: {flow[:50]}...")
            
            print(f"    ✅ Removed {len(empty_ref_flows)} invalid flows")
        else:
            print("    ✅ No empty flow references found")
        
        return iflow_xml
    
    def _remove_duplicate_flows(self, iflow_xml: str) -> str:
        """Remove duplicate sequence flows"""
        print("  🔍 Checking for duplicate flows...")
        
        # Find all sequence flows (both self-closing and opening/closing tags)
        flow_pattern = r'<bpmn2:sequenceFlow[^>]*(?:/>|>.*?</bpmn2:sequenceFlow>)'
        flows = re.findall(flow_pattern, iflow_xml, re.DOTALL)
        
        # Group flows by source and target
        flow_groups = {}
        duplicates = []
        
        for flow in flows:
            source_match = re.search(r'sourceRef="([^"]*)"', flow)
            target_match = re.search(r'targetRef="([^"]*)"', flow)
            
            if source_match and target_match:
                source_ref = source_match.group(1)
                target_ref = target_match.group(1)
                key = f"{source_ref}->{target_ref}"
                
                if key in flow_groups:
                    duplicates.append(flow)
                    self.issues_found.append(f"Duplicate flow: {source_ref} -> {target_ref}")
                    self.fixes_applied.append(f"Removed duplicate flow: {flow[:50]}...")
                else:
                    flow_groups[key] = flow
        
        # Remove duplicates
        for flow in duplicates:
            iflow_xml = iflow_xml.replace(flow, '')
        
        if duplicates:
            print(f"    ✅ Removed {len(duplicates)} duplicate flows")
        else:
            print("    ✅ No duplicate flows found")
        
        return iflow_xml
    
    def _generate_missing_bpmn_edges(self, iflow_xml: str) -> str:
        """Generate missing BPMN edges for sequence flows"""
        print("  🔍 Generating missing BPMN edges...")
        
        # Find all sequence flows (both self-closing and opening/closing tags)
        flow_pattern = r'<bpmn2:sequenceFlow[^>]*(?:/>|>.*?</bpmn2:sequenceFlow>)'
        flows = re.findall(flow_pattern, iflow_xml, re.DOTALL)
        
        # Find all component IDs (StartEvent, EndEvent, serviceTask, etc.)
        component_pattern = r'<bpmn2:(?:startEvent|endEvent|serviceTask|callActivity|exclusiveGateway|inclusiveGateway|parallelGateway|subProcess|userTask|scriptTask|businessRuleTask|manualTask|receiveTask|sendTask|task)[^>]*id="([^"]*)"'
        component_ids = set(re.findall(component_pattern, iflow_xml))
        
        # Add StartEvent_2 and EndEvent_2 explicitly (they might not match the pattern)
        component_ids.add("StartEvent_2")
        component_ids.add("EndEvent_2")
        
        # Find all sequence flows that reference non-existent components
        invalid_flows = []
        for flow in flows:
            source_match = re.search(r'sourceRef="([^"]*)"', flow)
            target_match = re.search(r'targetRef="([^"]*)"', flow)
            
            if source_match and target_match:
                source_ref = source_match.group(1)
                target_ref = target_match.group(1)
                
                if source_ref not in component_ids or target_ref not in component_ids:
                    invalid_flows.append(flow)
                    self.issues_found.append(f"Invalid flow reference: {source_ref} -> {target_ref}")
                    self.fixes_applied.append(f"Generated missing BPMN edge: {flow[:50]}...")
        
        # Generate missing edges
        for flow in invalid_flows:
            # Extract source and target references
            source_match = re.search(r'sourceRef="([^"]*)"', flow)
            target_match = re.search(r'targetRef="([^"]*)"', flow)
            
            if source_match and target_match:
                source_ref = source_match.group(1)
                target_ref = target_match.group(1)
                
                # Create a new sequence flow element
                new_flow = f'<bpmn2:sequenceFlow sourceRef="{source_ref}" targetRef="{target_ref}" />'
                
                # Insert it into the XML
                iflow_xml = iflow_xml.replace(flow, new_flow)
        
        if invalid_flows:
            print(f"    ✅ Generated {len(invalid_flows)} missing BPMN edges")
        else:
            print("    ✅ No missing BPMN edges found")
        
        return iflow_xml
    
    def _generate_bpmn_edges_for_flows(self, iflow_xml: str) -> str:
        """Generate BPMN edges in the diagram section for all sequence flows"""
        print("  🔍 Generating BPMN edges for sequence flows...")
        
        # Find all sequence flows (both self-closing and opening/closing tags)
        flow_pattern = r'<bpmn2:sequenceFlow[^>]*(?:/>|>.*?</bpmn2:sequenceFlow>)'
        flows = re.findall(flow_pattern, iflow_xml, re.DOTALL)
        
        # Find existing BPMN edges
        edge_pattern = r'<bpmndi:BPMNEdge[^>]*>.*?</bpmndi:BPMNEdge>'
        existing_edges = re.findall(edge_pattern, iflow_xml, re.DOTALL)
        
        print(f"    📊 Found {len(flows)} sequence flows and {len(existing_edges)} existing BPMN edges")
        
        # Extract flow IDs from existing edges
        existing_flow_ids = set()
        for edge in existing_edges:
            flow_match = re.search(r'bpmnElement="([^"]*)"', edge)
            if flow_match:
                existing_flow_ids.add(flow_match.group(1))
        
        # Generate missing edges
        new_edges = []
        for flow in flows:
            # Extract flow ID
            flow_id_match = re.search(r'id="([^"]*)"', flow)
            if flow_id_match:
                flow_id = flow_id_match.group(1)
                
                if flow_id not in existing_flow_ids:
                    # Extract source and target
                    source_match = re.search(r'sourceRef="([^"]*)"', flow)
                    target_match = re.search(r'targetRef="([^"]*)"', flow)
                    
                    if source_match and target_match:
                        source_ref = source_match.group(1)
                        target_ref = target_match.group(1)
                        
                        # Generate edge with waypoints
                        edge_xml = self._generate_edge_xml(flow_id, source_ref, target_ref)
                        new_edges.append(edge_xml)
                        
                        self.fixes_applied.append(f"Generated BPMN edge for flow: {flow_id}")
                        print(f"      🔧 Generating edge for flow: {flow_id} ({source_ref} -> {target_ref})")
        
        # Insert new edges into the BPMNPlane
        if new_edges:
            # Find the BPMNPlane section
            plane_pattern = r'(<bpmndi:BPMNPlane[^>]*>.*?)(</bpmndi:BPMNPlane>)'
            plane_match = re.search(plane_pattern, iflow_xml, re.DOTALL)
            
            if plane_match:
                plane_start = plane_match.group(1)
                plane_end = plane_match.group(2)
                
                # Insert edges before the closing tag
                edges_xml = '\n'.join(new_edges)
                new_plane = f"{plane_start}\n{edges_xml}\n{plane_end}"
                
                # Replace the entire plane section
                iflow_xml = iflow_xml.replace(plane_match.group(0), new_plane)
                
                print(f"    ✅ Generated {len(new_edges)} BPMN edges")
            else:
                print("    ⚠️ Could not find BPMNPlane section")
        else:
            print("    ✅ All BPMN edges already exist")
        
        return iflow_xml
    
    def _generate_edge_xml(self, flow_id: str, source_ref: str, target_ref: str) -> str:
        """Generate BPMN edge XML with proper waypoints"""
        
        # Get component positions (simplified calculation)
        # In a real implementation, you'd parse the BPMN shapes to get actual coordinates
        
        # Calculate waypoints based on component types
        if source_ref == "StartEvent_2":
            start_x, start_y = 116, 116  # Center of StartEvent (100 + 32/2, 100 + 32/2)
        else:
            # For other components, estimate position
            start_x, start_y = 350, 190  # Left edge of component
        
        if target_ref == "EndEvent_2":
            end_x, end_y = 316, 116  # Center of EndEvent (300 + 32/2, 100 + 32/2)
        else:
            # For other components, estimate position
            end_x, end_y = 300, 190  # Left edge of component
        
        edge_xml = f'''      <bpmndi:BPMNEdge bpmnElement="{flow_id}" id="BPMNEdge_{flow_id}">
        <di:waypoint x="{start_x}" y="{start_y}"/>
        <di:waypoint x="{end_x}" y="{end_y}"/>
      </bpmndi:BPMNEdge>'''
        
        return edge_xml
    
    def _validate_flow_consistency(self, iflow_xml: str) -> str:
        """Validate that all components have proper flow connections"""
        print("  🔍 Validating flow consistency...")
        
        # Find all components
        component_pattern = r'<bpmn2:(?:startEvent|endEvent|serviceTask|callActivity|exclusiveGateway|inclusiveGateway|parallelGateway|subProcess|userTask|scriptTask|businessRuleTask|manualTask|receiveTask|sendTask|task)[^>]*id="([^"]*)"'
        component_ids = set(re.findall(component_pattern, iflow_xml))
        
        # Add StartEvent_2 and EndEvent_2 explicitly
        component_ids.add("StartEvent_2")
        component_ids.add("EndEvent_2")
        
        # Find all sequence flows (both self-closing and opening/closing tags)
        flow_pattern = r'<bpmn2:sequenceFlow[^>]*(?:/>|>.*?</bpmn2:sequenceFlow>)'
        flows = re.findall(flow_pattern, iflow_xml, re.DOTALL)
        
        # Build flow graph
        flow_graph = {}
        for flow in flows:
            source_match = re.search(r'sourceRef="([^"]*)"', flow)
            target_match = re.search(r'targetRef="([^"]*)"', flow)
            
            if source_match and target_match:
                source_ref = source_match.group(1)
                target_ref = target_match.group(1)
                
                if source_ref not in flow_graph:
                    flow_graph[source_ref] = []
                flow_graph[source_ref].append(target_ref)
        
        # Check for isolated components
        isolated_components = []
        for component_id in component_ids:
            if component_id not in flow_graph and component_id != "EndEvent_2":
                # Check if this component is a target
                is_target = any(component_id in targets for targets in flow_graph.values())
                if not is_target:
                    isolated_components.append(component_id)
        
        if isolated_components:
            print(f"    ⚠️ Found {len(isolated_components)} isolated components: {isolated_components}")
            self.issues_found.append(f"Found {len(isolated_components)} isolated components")
        
        # Check for unreachable components
        unreachable = []
        for component_id in component_ids:
            if component_id != "StartEvent_2":
                # Check if there's a path from StartEvent_2 to this component
                if not self._is_reachable("StartEvent_2", component_id, flow_graph):
                    unreachable.append(component_id)
        
        if unreachable:
            print(f"    ⚠️ Found {len(unreachable)} unreachable components: {unreachable}")
            self.issues_found.append(f"Found {len(unreachable)} unreachable components")
        
        print("    ✅ Flow consistency validation completed")
        return iflow_xml
    
    def _is_reachable(self, start: str, target: str, graph: Dict[str, List[str]], visited: set = None) -> bool:
        """Check if target is reachable from start using DFS"""
        if visited is None:
            visited = set()
        
        if start == target:
            return True
        
        if start in visited:
            return False
        
        visited.add(start)
        
        if start in graph:
            for neighbor in graph[start]:
                if self._is_reachable(neighbor, target, graph, visited):
                    return True
        
        return False
    
    def _cleanup_empty_lines(self, iflow_xml: str) -> str:
        """Clean up excessive empty lines"""
        print("  🔍 Cleaning up empty lines...")
        
        # Remove multiple consecutive empty lines
        iflow_xml = re.sub(r'\n\s*\n\s*\n', '\n\n', iflow_xml)
        
        # Remove empty lines at the beginning and end
        iflow_xml = iflow_xml.strip()
        
        print("    ✅ Empty line cleanup completed")
        return iflow_xml
    
    def _report_sanitization_results(self):
        """Report all issues found and fixes applied"""
        print("\n📊 Sanitization Results:")
        print("=" * 50)
        
        if self.issues_found:
            print(f"❌ Issues Found: {len(self.issues_found)}")
            for issue in self.issues_found:
                print(f"  - {issue}")
        else:
            print("✅ No issues found")
        
        if self.fixes_applied:
            print(f"🔧 Fixes Applied: {len(self.fixes_applied)}")
            for fix in self.fixes_applied:
                print(f"  - {fix}")
        
        print("=" * 50)
    
    def validate_iflow_structure(self, iflow_xml: str) -> Dict[str, bool]:
        """Validate the overall iFlow structure"""
        print("\n🔍 Validating iFlow Structure...")
        
        validation_results = {}
        
        # Check for required BPMN elements
        required_elements = [
            "bpmn2:definitions",
            "bpmn2:collaboration", 
            "bpmn2:process",
            "bpmndi:BPMNDiagram",
            "bpmndi:BPMNPlane"
        ]
        
        for element in required_elements:
            exists = element in iflow_xml
            validation_results[element] = exists
            status = "✅" if exists else "❌"
            print(f"  {status} {element}")
        
        # Check for StartEvent and EndEvent
        has_start = "StartEvent_2" in iflow_xml
        has_end = "EndEvent_2" in iflow_xml
        validation_results["StartEvent_2"] = has_start
        validation_results["EndEvent_2"] = has_end
        
        status_start = "✅" if has_start else "❌"
        status_end = "✅" if has_end else "❌"
        print(f"  {status_start} StartEvent_2")
        print(f"  {status_end} EndEvent_2")
        
        # Check BPMN shapes placement
        process_section = iflow_xml.split("<bpmn2:process")[1].split("</bpmn2:process>")[0]
        diagram_section = iflow_xml.split("<bpmndi:BPMNDiagram")[1].split("</bpmndi:BPMNDiagram>")[0]
        
        shapes_in_process = process_section.count("bpmndi:BPMNShape")
        shapes_in_diagram = diagram_section.count("bpmndi:BPMNShape")
        
        validation_results["shapes_in_process"] = shapes_in_process == 0
        validation_results["shapes_in_diagram"] = shapes_in_diagram > 0
        
        status_process = "✅" if shapes_in_process == 0 else "❌"
        status_diagram = "✅" if shapes_in_diagram > 0 else "❌"
        print(f"  {status_process} BPMN shapes in process section: {shapes_in_process}")
        print(f"  {status_diagram} BPMN shapes in diagram section: {shapes_in_diagram}")
        
        # Check for empty flow references
        has_empty_refs = 'sourceRef=""' in iflow_xml or 'targetRef=""' in iflow_xml
        validation_results["no_empty_refs"] = not has_empty_refs
        
        status_refs = "✅" if not has_empty_refs else "❌"
        print(f"  {status_refs} No empty flow references")
        
        return validation_results


# Convenience functions
def sanitize_iflow(iflow_xml: str) -> str:
    """Sanitize an iFlow XML string"""
    sanitizer = IFlowSanitizer()
    return sanitizer.sanitize_iflow(iflow_xml)


def validate_iflow(iflow_xml: str) -> Dict[str, bool]:
    """Validate an iFlow XML string"""
    sanitizer = IFlowSanitizer()
    return sanitizer.validate_iflow_structure(iflow_xml)


def sanitize_iflow_file(input_file: str, output_file: str = None) -> str:
    """Sanitize an iFlow file"""
    if output_file is None:
        output_file = input_file.replace('.iflw', '_sanitized.iflw')
    
    with open(input_file, 'r', encoding='utf-8') as f:
        iflow_xml = f.read()
    
    sanitized_xml = sanitize_iflow(iflow_xml)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sanitized_xml)
    
    print(f"✅ Sanitized iFlow saved to: {output_file}")
    return output_file
