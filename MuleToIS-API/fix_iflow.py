import xml.etree.ElementTree as ET
import re
import os
import shutil
import zipfile
import datetime
from collections import defaultdict

def escape_ampersands_in_query_options(xml_content):
    """
    Specifically target and escape ampersands in OData query options.
    This is the first step to fix parsing errors.
    """
    # Find all OData query options
    query_options_pattern = r'(<key>queryOptions<\/key>\s*<value>)(.*?)(<\/value>)'
    
    def escape_ampersands_in_match(match):
        key_part = match.group(1)
        value_part = match.group(2)
        end_part = match.group(3)
        
        # Replace ampersands in query parameters with &amp;
        escaped_value = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', value_part)
        
        return key_part + escaped_value + end_part
    
    # Apply replacement
    return re.sub(query_options_pattern, escape_ampersands_in_match, xml_content, flags=re.DOTALL)

def fix_attribute_ampersands(xml_content):
    """
    Fix ampersands in XML attribute values.
    """
    # Pattern to match attribute values that might contain unescaped ampersands
    attr_pattern = r'(=["\'])(.*?)(["\'])'
    
    def escape_ampersands_in_attr(match):
        equals_quote = match.group(1)
        attr_value = match.group(2)
        end_quote = match.group(3)
        
        # Replace ampersands in attribute value with &amp;
        escaped_value = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', attr_value)
        
        return equals_quote + escaped_value + end_quote
    
    # Apply replacement
    return re.sub(attr_pattern, escape_ampersands_in_attr, xml_content)

def preprocess_xml(xml_content):
    """
    Pre-process XML content to fix common syntax issues.
    """
    # First fix the ampersands in OData query options
    xml_content = escape_ampersands_in_query_options(xml_content)
    
    # Then fix ampersands in attribute values
    xml_content = fix_attribute_ampersands(xml_content)
    
    # Replace remaining unescaped ampersands
    xml_content = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', xml_content)
    
    # Fix unclosed tags (this is a simple approach and might not catch all cases)
    xml_content = re.sub(r'<([a-zA-Z0-9_:]+)([^>]*)>([^<]*)</\1>', r'<\1\2>\3</\1>', xml_content)
    
    # Remove invalid XML characters
    xml_content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_content)
    
    return xml_content

def fix_iflow_xml(xml_content):
    """
    Post-process the iFlow XML to fix common issues with component references,
    sequence flows, and diagram elements.
    """
    # Parse the XML
    try:
        # Add namespace prefixes to parse BPMN XML properly
        namespaces = {
            'bpmn2': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI', 
            'ifl': 'http:///com.sap.ifl.model/Ifl.xsd',
            'dc': 'http://www.omg.org/spec/DD/20100524/DC',
            'di': 'http://www.omg.org/spec/DD/20100524/DI'
        }
        
        # Register all namespaces
        for prefix, uri in namespaces.items():
            ET.register_namespace(prefix, uri)
        
        root = ET.fromstring(xml_content)
    except Exception as e:
        # Provide more detailed error information
        print(f"Error parsing XML: {str(e)}")
        
        # Extract line and column numbers if available
        match = re.search(r'line (\d+), column (\d+)', str(e))
        if match:
            line_num = int(match.group(1))
            col_num = int(match.group(2))
            lines = xml_content.split('\n')
            if 0 <= line_num-1 < len(lines):
                context_start = max(0, line_num-3)
                context_end = min(len(lines), line_num+2)
                
                print("\nXML Context:")
                for i in range(context_start, context_end):
                    prefix = "-> " if i == line_num-1 else "   "
                    print(f"{prefix}Line {i+1}: {lines[i]}")
                
                if col_num > 0 and col_num <= len(lines[line_num-1]):
                    print(f"   {' ' * (col_num+6)}^")
        
        return f"Error parsing XML: {str(e)}", False, str(e)
    
    # Track changes made
    changes = []
    success = True
    
    # Collect all components and their IDs
    component_ids = set()
    id_mapping = {}  # Maps incorrect references to correct IDs
    components_by_type = defaultdict(list)
    
    # Find all process elements
    for elem in root.findall('.//bpmn2:process//*[@id]', namespaces):
        elem_id = elem.get('id')
        component_ids.add(elem_id)
        elem_type = elem.tag.split('}')[-1]
        components_by_type[elem_type].append(elem_id)
    
    # 1. Check for duplicate participant shapes in diagram
    participant_shapes = defaultdict(list)
    for shape in root.findall('.//bpmndi:BPMNShape', namespaces):
        bpmn_elem = shape.get('bpmnElement')
        if bpmn_elem and bpmn_elem.startswith('Participant_'):
            participant_shapes[bpmn_elem].append(shape)
    
    # Remove duplicate participant shapes - without using complex XPath
    for participant_id, shapes in participant_shapes.items():
        if len(shapes) > 1:
            # We need to find the parent of these shapes to remove them
            # Since we can't use getparent(), we'll rebuild the diagram plane
            for plane in root.findall('.//bpmndi:BPMNPlane', namespaces):
                # Collect all shapes
                all_shapes = []
                for child in plane:
                    all_shapes.append(child)
                
                # Clear the plane
                for child in list(plane):
                    plane.remove(child)
                
                # Add back only the shapes we want to keep
                kept_participants = set()
                for shape in all_shapes:
                    if shape.tag.endswith('BPMNShape'):
                        bpmn_elem = shape.get('bpmnElement')
                        if bpmn_elem and bpmn_elem.startswith('Participant_'):
                            if bpmn_elem in kept_participants:
                                changes.append(f"Removed duplicate shape for {bpmn_elem}")
                                continue
                            kept_participants.add(bpmn_elem)
                    plane.append(shape)
    
    # 2. Find and fix sequence flow references
    sequence_flows = {}
    for seq_flow in root.findall('.//bpmn2:sequenceFlow', namespaces):
        flow_id = seq_flow.get('id')
        source_ref = seq_flow.get('sourceRef')
        target_ref = seq_flow.get('targetRef')
        sequence_flows[flow_id] = (source_ref, target_ref)
        
        # Check if source and target refs exist
        if source_ref not in component_ids:
            # Try to find a component with similar ID
            for comp_id in component_ids:
                if source_ref.lower() in comp_id.lower() or comp_id.lower() in source_ref.lower():
                    seq_flow.set('sourceRef', comp_id)
                    changes.append(f"Fixed sourceRef from {source_ref} to {comp_id} in {flow_id}")
                    id_mapping[source_ref] = comp_id
                    break
        
        if target_ref not in component_ids:
            # Try to find a component with similar ID
            for comp_id in component_ids:
                if target_ref.lower() in comp_id.lower() or comp_id.lower() in target_ref.lower():
                    seq_flow.set('targetRef', comp_id)
                    changes.append(f"Fixed targetRef from {target_ref} to {comp_id} in {flow_id}")
                    id_mapping[target_ref] = comp_id
                    break
    
    # 3. Check for duplicate sequence flow IDs
    seq_flow_ids = defaultdict(int)
    for seq_flow in root.findall('.//bpmn2:sequenceFlow', namespaces):
        flow_id = seq_flow.get('id')
        seq_flow_ids[flow_id] += 1
    
    # Fix duplicate sequence flow IDs
    seq_flow_counter = 1
    for seq_flow in root.findall('.//bpmn2:sequenceFlow', namespaces):
        flow_id = seq_flow.get('id')
        if seq_flow_ids[flow_id] > 1:
            source_ref = seq_flow.get('sourceRef')
            target_ref = seq_flow.get('targetRef')
            new_id = f"flow_{source_ref}_to_{target_ref}_{seq_flow_counter}"
            seq_flow.set('id', new_id)
            changes.append(f"Renamed duplicate flow ID from {flow_id} to {new_id}")
            seq_flow_counter += 1
            
            # Update any diagram elements referencing this flow
            for edge in root.findall('.//bpmndi:BPMNEdge', namespaces):
                if edge.get('bpmnElement') == flow_id:
                    edge.set('bpmnElement', new_id)
                    edge.set('id', f"BPMNEdge_{new_id}")
                    changes.append(f"Updated edge reference from {flow_id} to {new_id}")
    
    # 4. Fix incoming/outgoing references in components (without complex XPath)
    # Handle startEvent, endEvent, serviceTask, callActivity, etc. separately
    for tag_name in ['startEvent', 'endEvent', 'serviceTask', 'callActivity', 'exclusiveGateway', 'task']:
        for component in root.findall(f'.//bpmn2:{tag_name}', namespaces):
            # Fix incoming references
            for incoming in component.findall('./bpmn2:incoming', namespaces):
                ref = incoming.text
                if ref and ref in id_mapping:
                    incoming.text = id_mapping[ref]
                    changes.append(f"Fixed incoming reference from {ref} to {id_mapping[ref]} in {component.get('id')}")
            
            # Fix outgoing references
            for outgoing in component.findall('./bpmn2:outgoing', namespaces):
                ref = outgoing.text
                if ref and ref in id_mapping:
                    outgoing.text = id_mapping[ref]
                    changes.append(f"Fixed outgoing reference from {ref} to {id_mapping[ref]} in {component.get('id')}")
    
    # 5. Check for OData service tasks with missing flows
    for task in root.findall('.//bpmn2:serviceTask', namespaces):
        task_id = task.get('id')
        
        # Find incoming and outgoing elements
        incoming_elems = task.findall('./bpmn2:incoming', namespaces)
        outgoing_elems = task.findall('./bpmn2:outgoing', namespaces)
        
        # If the service task references non-existent sequence flows, fix them
        for incoming in incoming_elems:
            if incoming.text not in sequence_flows:
                # Find sequence flows targeting this task
                matching_flows = [(flow_id, src) for flow_id, (src, tgt) in sequence_flows.items() if tgt == task_id]
                if matching_flows:
                    flow_id, src = matching_flows[0]
                    incoming.text = flow_id
                    changes.append(f"Fixed incoming reference in {task_id} to {flow_id}")
        
        for outgoing in outgoing_elems:
            if outgoing.text not in sequence_flows:
                # Find sequence flows sourced from this task
                matching_flows = [(flow_id, tgt) for flow_id, (src, tgt) in sequence_flows.items() if src == task_id]
                if matching_flows:
                    flow_id, tgt = matching_flows[0]
                    outgoing.text = flow_id
                    changes.append(f"Fixed outgoing reference in {task_id} to {flow_id}")
    
    # 6. Fix diagram element references
    for shape in root.findall('.//bpmndi:BPMNShape', namespaces):
        bpmn_elem = shape.get('bpmnElement')
        if bpmn_elem in id_mapping:
            shape.set('bpmnElement', id_mapping[bpmn_elem])
            shape.set('id', f"BPMNShape_{id_mapping[bpmn_elem]}")
            changes.append(f"Updated shape reference from {bpmn_elem} to {id_mapping[bpmn_elem]}")
    
    for edge in root.findall('.//bpmndi:BPMNEdge', namespaces):
        bpmn_elem = edge.get('bpmnElement')
        if bpmn_elem in id_mapping:
            edge.set('bpmnElement', id_mapping[bpmn_elem])
            edge.set('id', f"BPMNEdge_{id_mapping[bpmn_elem]}")
            changes.append(f"Updated edge reference from {bpmn_elem} to {id_mapping[bpmn_elem]}")
        
        # Also check sourceElement and targetElement attributes
        source_elem = edge.get('sourceElement')
        if source_elem and source_elem.startswith('BPMNShape_') and source_elem[10:] in id_mapping:
            edge.set('sourceElement', f"BPMNShape_{id_mapping[source_elem[10:]]}")
            changes.append(f"Updated edge sourceElement from {source_elem} to BPMNShape_{id_mapping[source_elem[10:]]}")
        
        target_elem = edge.get('targetElement')
        if target_elem and target_elem.startswith('BPMNShape_') and target_elem[10:] in id_mapping:
            edge.set('targetElement', f"BPMNShape_{id_mapping[target_elem[10:]]}")
            changes.append(f"Updated edge targetElement from {target_elem} to BPMNShape_{id_mapping[target_elem[10:]]}")
    
    # Convert back to string
    fixed_xml = ET.tostring(root, encoding='utf-8').decode('utf-8')
    
    # Add XML declaration
    fixed_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + fixed_xml
    
    # Return the fixed XML and a summary of changes
    change_summary = "\n".join(changes) if changes else "No changes were needed"
    return fixed_xml, success, change_summary

def fix_file_directly(file_path):
    """
    Directly fix a known issue with ampersands in query options without parsing XML.
    This is a fallback for when the XML is too malformed to parse.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix ampersands in queryOptions
    pattern = r'(<key>queryOptions</key>\s*<value>.*?)&(.*?</value>)'
    content = re.sub(pattern, r'\1&amp;\2', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return "Applied emergency fix for ampersands in query options"

def find_iflow_files(root_dir):
    """Find all iFlow files in the directory structure"""
    iflow_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.iflw'):
                iflow_files.append(os.path.join(root, file))
    return iflow_files

# Main execution code
if __name__ == "__main__":
    # Base directory of the project
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for iFlow file in the expected location
    iflow_path = os.path.join(base_dir, "src", "main", "resources", "scenarioflows", "integrationflow", "IFlow_631248fe.iflw")
    iflow_path = iflow_path.replace('\\', os.path.sep)  # Fix path separators
    
    if not os.path.exists(iflow_path):
        print(f"Iflow file not found at expected path: {iflow_path}")
        print("Searching for iFlow files in project directory...")
        
        # Search for iFlow files
        iflow_files = find_iflow_files(base_dir)
        
        if iflow_files:
            print("Found iFlow files:")
            for i, file_path in enumerate(iflow_files):
                print(f"[{i+1}] {os.path.relpath(file_path, base_dir)}")
            
            choice = input("Select a file to process (number) or press Enter to use the first one: ")
            if choice.strip() and choice.isdigit() and 1 <= int(choice) <= len(iflow_files):
                iflow_path = iflow_files[int(choice) - 1]
            else:
                iflow_path = iflow_files[0]
            
            print(f"Using iFlow file: {os.path.relpath(iflow_path, base_dir)}")
        else:
            print("No iFlow files found. Please check the project structure.")
            exit(1)
    
    try:
        print(f"Processing iFlow file: {iflow_path}")
        
        # Read the iflow file
        with open(iflow_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Try direct fix if the XML is severely malformed
        if "&$select=" in xml_content or "&$filter=" in xml_content:
            print("Found unescaped ampersands in query options, applying emergency fix...")
            emergency_message = fix_file_directly(iflow_path)
            print(f"Emergency fix applied: {emergency_message}")
            print("Reloading file with emergency fixes...")
            with open(iflow_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
        
        # Pre-process the XML to fix common issues
        xml_content = preprocess_xml(xml_content)
        
        # Fix the XML
        fixed_xml, success, changes = fix_iflow_xml(xml_content)
        
        if success:
            print("XML fixed successfully!")
            print("Changes made:")
            print(changes)
            
            # Backup the original file
            backup_file = f"{iflow_path}.backup.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(iflow_path, backup_file)
            print(f"Backup of original file created at {backup_file}")
            
            # Write the fixed XML back to the original file
            with open(iflow_path, 'w', encoding='utf-8') as f:
                f.write(fixed_xml)
            print(f"Fixed XML written to {iflow_path}")
            
            print("Process completed successfully!")
            
        else:
            print("Errors found while fixing XML:")
            print(changes)
            
            # Ask if user wants to attempt emergency fix
            if "&$select=" in xml_content or "&$filter=" in xml_content:
                emergency_fix = input("Would you like to attempt an emergency fix for ampersands in query options? (y/n): ")
                if emergency_fix.lower() == 'y':
                    emergency_message = fix_file_directly(iflow_path)
                    print(f"Emergency fix applied: {emergency_message}")
                    print("Please run the script again to complete the fixes.")
    except Exception as e:
        print(f"Error processing the iflow file: {str(e)}")
        import traceback
        traceback.print_exc()