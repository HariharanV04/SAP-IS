#!/usr/bin/env python3
"""Verify all SAP IS import fixes have been applied"""

import zipfile
import re
import sys

def verify_sap_fixes(zip_path):
    print("=" * 70)
    print("SAP IS Import Fixes Verification")
    print("=" * 70)
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        content = z.read('src/main/resources/scenarioflows/integrationflow/Test_iFlow_4_Components_Validation.iflw').decode('utf-8')
    
    issues_found = []
    fixes_verified = []
    
    # 1. Check namespace URI
    print("\n1. XML Namespace URI:")
    ns_match = re.search(r'xmlns:ifl="([^"]+)"', content)
    if ns_match:
        ns_uri = ns_match.group(1)
        if ns_uri == "http:///com.sap.ifl.model/Ifl.xsd":
            print("   ✅ Correct: http:///com.sap.ifl.model/Ifl.xsd")
            fixes_verified.append("Namespace URI")
        else:
            print(f"   ❌ Wrong: {ns_uri}")
            print("   Expected: http:///com.sap.ifl.model/Ifl.xsd")
            issues_found.append("Wrong namespace URI")
    else:
        print("   ❌ Namespace not found")
        issues_found.append("Missing namespace")
    
    # Check for exporter attributes (should not be present)
    if 'exporter=' in content or 'exporterVersion=' in content:
        print("   ⚠️  Exporter attributes found (may cause issues)")
        issues_found.append("Has exporter attributes")
    else:
        print("   ✅ No exporter attributes")
        fixes_verified.append("No exporter attributes")
    
    # 2. Check for nested extensionElements
    print("\n2. Nested extensionElements:")
    nested_pattern = r'<bpmn2:extensionElements>.*?<bpmn2:extensionElements>'
    if re.search(nested_pattern, content, re.DOTALL):
        print("   ❌ Found nested extensionElements")
        issues_found.append("Nested extensionElements")
    else:
        print("   ✅ No nested extensionElements found")
        fixes_verified.append("No nested extensionElements")
    
    # 3. Check diagram references
    print("\n3. BPMN Diagram References:")
    participant_shape = re.search(r'bpmnElement="Participant_Process_1"', content)
    if participant_shape:
        print("   ✅ Participant_Process_1 reference found in diagram")
        fixes_verified.append("Correct diagram reference")
    else:
        print("   ❌ Participant_Process_1 reference NOT found")
        # Check what reference is used
        alt_ref = re.search(r'bpmnElement="([^"]+)"', content)
        if alt_ref:
            print(f"   Found instead: {alt_ref.group(1)}")
        issues_found.append("Wrong diagram reference")
    
    # 4. Check CDATA wrapping
    print("\n4. CDATA Wrapping for XML Tables:")
    cdata_count = len(re.findall(r'<!\[CDATA\[', content))
    print(f"   Found {cdata_count} CDATA section(s)")
    
    # Check propertyTable
    prop_table = re.search(r'<key>propertyTable</key>\s*<value>(.*?)</value>', content, re.DOTALL)
    if prop_table:
        pt_value = prop_table.group(1)
        if '<row>' in pt_value:
            if '<![CDATA[' in pt_value:
                print("   ✅ propertyTable wrapped in CDATA")
                fixes_verified.append("propertyTable CDATA")
            else:
                print("   ❌ propertyTable has XML but NOT wrapped in CDATA")
                issues_found.append("propertyTable missing CDATA")
        else:
            print("   ℹ️  propertyTable is empty or has no XML")
    
    # Check headerTable
    header_table = re.search(r'<key>headerTable</key>\s*<value>(.*?)</value>', content, re.DOTALL)
    if header_table:
        ht_value = header_table.group(1)
        if '<row>' in ht_value:
            if '<![CDATA[' in ht_value:
                print("   ✅ headerTable wrapped in CDATA")
                fixes_verified.append("headerTable CDATA")
            else:
                print("   ❌ headerTable has XML but NOT wrapped in CDATA")
                issues_found.append("headerTable missing CDATA")
        else:
            print("   ℹ️  headerTable is empty or has no XML")
    
    # 5. Check version consistency
    print("\n5. Version Consistency:")
    enricher = re.search(r'id="content_modifier_001".*?</bpmn2:callActivity>', content, re.DOTALL)
    if enricher:
        enricher_section = enricher.group(0)
        cv_match = re.search(r'<key>componentVersion</key>\s*<value>([^<]+)</value>', enricher_section)
        cvuri_match = re.search(r'<key>cmdVariantUri</key>\s*<value>.*?version::([^"]+)', enricher_section)
        if cv_match and cvuri_match:
            cv = cv_match.group(1)
            cvuri_ver = cvuri_match.group(1)
            # Extract major.minor from componentVersion
            cv_parts = cv.split('.')
            cv_major_minor = f"{cv_parts[0]}.{cv_parts[1]}" if len(cv_parts) > 1 else cv
            cvuri_parts = cvuri_ver.split('.')
            cvuri_major_minor = f"{cvuri_parts[0]}.{cvuri_parts[1]}" if len(cvuri_parts) > 1 else cvuri_ver
            if cv_major_minor == cvuri_major_minor:
                print(f"   ✅ Versions match: {cv} ↔ {cvuri_ver}")
                fixes_verified.append("Version consistency")
            else:
                print(f"   ❌ Versions mismatch: {cv} vs {cvuri_ver}")
                issues_found.append("Version mismatch")
        else:
            print("   ⚠️  Could not find version info")
    else:
        print("   ⚠️  Could not find content_modifier component")
    
    # 6. Check sequence flow connectivity
    print("\n6. Sequence Flow Connectivity:")
    flows = re.findall(r'<bpmn2:sequenceFlow[^>]*sourceRef="([^"]+)"[^>]*targetRef="([^"]+)"', content)
    print(f"   Found {len(flows)} sequence flow(s)")
    
    # Check that all flows are connected
    all_connected = True
    for source, target in flows:
        # Check source has outgoing
        source_outgoing = re.search(rf'id="{re.escape(source)}"[^>]*>.*?<bpmn2:outgoing>.*?</bpmn2:outgoing>', content, re.DOTALL)
        if not source_outgoing and source != "StartEvent_1":
            print(f"   ⚠️  Source {source} missing outgoing reference")
            all_connected = False
        
        # Check target has incoming
        target_incoming = re.search(rf'id="{re.escape(target)}"[^>]*>.*?<bpmn2:incoming>.*?</bpmn2:incoming>', content, re.DOTALL)
        if not target_incoming and target != "EndEvent_1":
            print(f"   ⚠️  Target {target} missing incoming reference")
            all_connected = False
    
    if all_connected:
        print("   ✅ All flows properly connected")
        fixes_verified.append("Flow connectivity")
    else:
        issues_found.append("Flow connectivity issues")
    
    # 7. Check component naming
    print("\n7. Component Naming Pattern:")
    components = re.findall(r'<bpmn2:callActivity[^>]*id="([^"]+)"', content)
    print(f"   Found {len(components)} component(s)")
    for comp_id in components[:5]:
        print(f"      - {comp_id}")
        # Check pattern: lowercase with underscores
        if comp_id == comp_id.lower() and '_' in comp_id:
            print(f"         ✅ Matches pattern (lowercase, underscores)")
        else:
            print(f"         ⚠️  May not match pattern")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    print(f"✅ Fixes Verified: {len(fixes_verified)}")
    for fix in fixes_verified:
        print(f"   - {fix}")
    
    if issues_found:
        print(f"\n❌ Issues Found: {len(issues_found)}")
        for issue in issues_found:
            print(f"   - {issue}")
        print("\n❌ SOME ISSUES REMAIN - Please review above")
        return False
    else:
        print("\n✅ ALL FIXES VERIFIED - iFlow should import successfully!")
        return True

if __name__ == "__main__":
    zip_path = sys.argv[1] if len(sys.argv) > 1 else "test_output_sap_fixed_final/Test_iFlow_4_Components_Validation.zip"
    success = verify_sap_fixes(zip_path)
    sys.exit(0 if success else 1)




