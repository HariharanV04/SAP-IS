#!/usr/bin/env python3
"""Verify generated iFlow structure - check for placeholders and flow connections"""

import zipfile
import re
import sys

def verify_iflow(zip_path):
    print("=" * 70)
    print("iFlow Structure Verification")
    print("=" * 70)
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        content = z.read('src/main/resources/scenarioflows/integrationflow/Test_iFlow_4_Components_Validation.iflw').decode('utf-8')
    
    # Check for placeholders
    print("\n1. Checking for placeholders:")
    placeholder_patterns = [
        r'<placeholder>',
        r'&lt;placeholder&gt;',
        r'value>\s*&lt;[^&]*&gt;\s*</value>',
        r'value>\s*<[^>]*>\s*</value>',
    ]
    found_placeholders = []
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            found_placeholders.extend(matches)
    
    if found_placeholders:
        print(f"   ❌ Found {len(found_placeholders)} placeholder(s)")
        for p in found_placeholders[:5]:
            print(f"      - {p}")
    else:
        print("   ✅ No placeholders found")
    
    # Extract components
    print("\n2. Components in order:")
    components = []
    for match in re.finditer(r'<bpmn2:callActivity[^>]*id="([^"]+)"[^>]*name="([^"]+)"', content):
        components.append((match.group(1), match.group(2)))
    
    expected_components = [
        'content_modifier_001',
        'filter_001',
        'base64_encoder_001',
        'xml_to_json_001'
    ]
    
    print(f"   Found {len(components)} component(s)")
    for i, (comp_id, comp_name) in enumerate(components, 1):
        print(f"   [{i}] {comp_id}: {comp_name}")
        if i <= len(expected_components) and comp_id != expected_components[i-1]:
            print(f"      ⚠️  Expected: {expected_components[i-1]}")
    
    if len(components) == len(expected_components):
        print("   ✅ All expected components found")
    
    # Extract sequence flows
    print("\n3. Sequence flows:")
    flows = {}
    for match in re.finditer(r'<bpmn2:sequenceFlow[^>]*id="([^"]+)"[^>]*sourceRef="([^"]+)"[^>]*targetRef="([^"]+)"', content):
        flow_id = match.group(1)
        source = match.group(2)
        target = match.group(3)
        flows[flow_id] = {'source': source, 'target': target}
    
    print(f"   Found {len(flows)} sequence flow(s)")
    for flow_id, flow_data in flows.items():
        print(f"   - {flow_id}: {flow_data['source']} -> {flow_data['target']}")
    
    # Verify flow chain
    print("\n4. Verifying complete flow chain:")
    expected_chain = [
        'StartEvent_1',
        'content_modifier_001',
        'filter_001',
        'base64_encoder_001',
        'xml_to_json_001',
        'EndEvent_1'
    ]
    
    # Build actual chain
    actual_chain = ['StartEvent_1']
    current = 'StartEvent_1'
    
    while current != 'EndEvent_1':
        found = False
        for flow_id, flow_data in flows.items():
            if flow_data['source'] == current:
                current = flow_data['target']
                actual_chain.append(current)
                found = True
                break
        if not found:
            print(f"   ⚠️  No outgoing flow from {current}")
            break
        if current == 'EndEvent_1':
            break
    
    print(f"   Expected: {' -> '.join(expected_chain)}")
    print(f"   Actual:   {' -> '.join(actual_chain)}")
    
    if actual_chain == expected_chain:
        print("   ✅ Flow chain is complete and correct")
    else:
        print("   ❌ Flow chain doesn't match expected order")
        missing = set(expected_chain) - set(actual_chain)
        extra = set(actual_chain) - set(expected_chain)
        if missing:
            print(f"      Missing: {missing}")
        if extra:
            print(f"      Extra: {extra}")
    
    # Check component connections (incoming/outgoing)
    print("\n5. Component connections:")
    for comp_id in expected_components:
        # Find component section
        comp_match = re.search(rf'<bpmn2:callActivity[^>]*id="{comp_id}"[^>]*>.*?</bpmn2:callActivity>', content, re.DOTALL)
        if comp_match:
            comp_section = comp_match.group(0)
            incoming = re.findall(r'<bpmn2:incoming>([^<]+)</bpmn2:incoming>', comp_section)
            outgoing = re.findall(r'<bpmn2:outgoing>([^<]+)</bpmn2:outgoing>', comp_section)
            print(f"   {comp_id}:")
            print(f"      Incoming: {incoming}")
            print(f"      Outgoing: {outgoing}")
            if not incoming and comp_id != 'content_modifier_001':  # First component gets from StartEvent
                print(f"      ⚠️  No incoming flow")
            if not outgoing and comp_id != 'xml_to_json_001':  # Last component goes to EndEvent
                print(f"      ⚠️  No outgoing flow")
    
    # Check Start/End events
    print("\n6. Start and End events:")
    start_match = re.search(r'<bpmn2:startEvent[^>]*id="StartEvent_1"[^>]*>.*?</bpmn2:startEvent>', content, re.DOTALL)
    if start_match:
        start_section = start_match.group(0)
        start_outgoing = re.findall(r'<bpmn2:outgoing>([^<]+)</bpmn2:outgoing>', start_section)
        print(f"   StartEvent_1 outgoing: {start_outgoing}")
        if start_outgoing:
            print("   ✅ Start event has outgoing flow")
        else:
            print("   ❌ Start event missing outgoing flow")
    
    end_match = re.search(r'<bpmn2:endEvent[^>]*id="EndEvent_1"[^>]*>.*?</bpmn2:endEvent>', content, re.DOTALL)
    if end_match:
        end_section = end_match.group(0)
        end_incoming = re.findall(r'<bpmn2:incoming>([^<]+)</bpmn2:incoming>', end_section)
        print(f"   EndEvent_1 incoming: {end_incoming}")
        if end_incoming:
            print("   ✅ End event has incoming flow")
        else:
            print("   ❌ End event missing incoming flow")
    
    # Check for empty or problematic property values
    print("\n7. Checking property values:")
    empty_props = re.findall(r'<key>([^<]+)</key>\s*<value\s*/>', content)
    if empty_props:
        print(f"   Found {len(empty_props)} empty properties (may be OK for some fields)")
        print(f"   Examples: {empty_props[:3]}")
    else:
        print("   No empty properties found")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    
    all_ok = True
    if found_placeholders:
        print("❌ Placeholders found in XML")
        all_ok = False
    else:
        print("✅ No placeholders")
    
    if len(components) == len(expected_components):
        print("✅ All components present")
    else:
        print(f"❌ Component count mismatch: {len(components)} vs {len(expected_components)}")
        all_ok = False
    
    if actual_chain == expected_chain:
        print("✅ Flow chain complete and correct")
    else:
        print("❌ Flow chain incomplete or incorrect")
        all_ok = False
    
    if all_ok:
        print("\n✅ ALL CHECKS PASSED - iFlow structure is complete and correct!")
    else:
        print("\n❌ SOME ISSUES FOUND - Please review above")
    
    return all_ok

if __name__ == "__main__":
    zip_path = sys.argv[1] if len(sys.argv) > 1 else "test_output_structure_fixed/Test_iFlow_4_Components_Validation.zip"
    verify_iflow(zip_path)




