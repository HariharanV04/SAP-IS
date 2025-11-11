#!/usr/bin/env python3
"""
Validation script for generated iFlow ZIP files
"""
import zipfile
import xml.etree.ElementTree as ET
import sys

def validate_iflow(zip_path):
    """Validate the iFlow ZIP file structure and content"""
    print("=" * 70)
    print("iFlow File Validation Report")
    print("=" * 70)
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Check file structure
            print("\n📦 ZIP File Structure:")
            files = sorted(z.namelist())
            required_files = [
                'META-INF/MANIFEST.MF',
                'metainfo.prop',
                '.project',
                'src/main/resources/parameters.prop',
                'src/main/resources/parameters.propdef'
            ]
            
            for req_file in required_files:
                if req_file in files:
                    print(f"  ✅ {req_file}")
                    results['passed'].append(f"File present: {req_file}")
                else:
                    print(f"  ❌ {req_file} - MISSING")
                    results['failed'].append(f"Missing file: {req_file}")
            
            # Find iflow file
            iflow_files = [f for f in files if f.endswith('.iflw')]
            if not iflow_files:
                print("  ❌ No .iflw file found!")
                results['failed'].append("No .iflw file in ZIP")
                return results
            iflow_file = iflow_files[0]
            print(f"  ✅ {iflow_file}")
            
            # Parse XML
            print("\n📄 XML Structure Validation:")
            content = z.read(iflow_file).decode('utf-8')
            try:
                root = ET.fromstring(content)
                print("  ✅ XML is well-formed")
                results['passed'].append("XML is well-formed")
            except ET.ParseError as e:
                print(f"  ❌ XML parsing error: {e}")
                results['failed'].append(f"XML parsing error: {e}")
                return results
            
            # Define namespaces
            ns = {
                'bpmn2': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
                'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
                'ifl': 'http:///com.sap.ifl.model/Ifl.xsd',
                'dc': 'http://www.omg.org/spec/DD/20100524/DC',
                'di': 'http://www.omg.org/spec/DD/20100524/DI'
            }
            
            # Check main sections
            process = root.find('.//bpmn2:process', ns)
            collab = root.find('.//bpmn2:collaboration', ns)
            diagram = root.find('.//bpmndi:BPMNDiagram', ns)
            
            if process:
                print(f"  ✅ Process found: {process.get('id')}")
                results['passed'].append(f"Process section: {process.get('id')}")
            else:
                print("  ❌ Process section not found")
                results['failed'].append("Process section missing")
            
            if collab:
                print(f"  ✅ Collaboration found: {collab.get('id')}")
                results['passed'].append(f"Collaboration section: {collab.get('id')}")
            else:
                print("  ❌ Collaboration section not found")
                results['failed'].append("Collaboration section missing")
            
            if diagram:
                print(f"  ✅ Diagram found: {diagram.get('id')}")
                results['passed'].append(f"Diagram section: {diagram.get('id')}")
            else:
                print("  ❌ Diagram section not found")
                results['failed'].append("Diagram section missing")
            
            # Check components
            print("\n🔧 Component Validation:")
            components = root.findall('.//bpmn2:callActivity', ns)
            start_events = root.findall('.//bpmn2:startEvent', ns)
            end_events = root.findall('.//bpmn2:endEvent', ns)
            flows = root.findall('.//bpmn2:sequenceFlow', ns)
            
            print(f"  Components (callActivity): {len(components)}")
            print(f"  Start Events: {len(start_events)}")
            print(f"  End Events: {len(end_events)}")
            print(f"  Sequence Flows: {len(flows)}")
            
            if len(components) > 0:
                results['passed'].append(f"{len(components)} components found")
            else:
                results['warnings'].append("No components found")
            
            if len(start_events) == 1:
                results['passed'].append("Start event present")
            else:
                results['failed'].append(f"Expected 1 start event, found {len(start_events)}")
            
            if len(end_events) == 1:
                results['passed'].append("End event present")
            else:
                results['failed'].append(f"Expected 1 end event, found {len(end_events)}")
            
            if len(flows) > 0:
                results['passed'].append(f"{len(flows)} sequence flows found")
            else:
                results['failed'].append("No sequence flows found")
            
            # Check component properties
            print("\n📋 Component Properties:")
            required_props = ['componentVersion', 'cmdVariantUri']
            all_have_props = True
            for c in components:
                props = c.findall('.//ifl:property', ns)
                prop_keys = [p.find('key') for p in props if p.find('key') is not None]
                prop_keys = [k.text for k in prop_keys if k is not None]
                missing = [rp for rp in required_props if rp not in prop_keys]
                if missing:
                    print(f"  ⚠️  {c.get('id')}: Missing {missing}")
                    results['warnings'].append(f"{c.get('id')} missing properties: {missing}")
                    all_have_props = False
                else:
                    print(f"  ✅ {c.get('id')}: Has required properties")
            
            if all_have_props:
                results['passed'].append("All components have required properties")
            
            # Check processRef match
            print("\n🔗 Reference Validation:")
            if process and collab:
                participant = collab.find('.//bpmn2:participant', ns)
                if participant:
                    process_id = process.get('id')
                    process_ref = participant.get('processRef')
                    if process_id == process_ref:
                        print(f"  ✅ Process ID matches participant processRef: {process_id}")
                        results['passed'].append("ProcessRef matches process ID")
                    else:
                        print(f"  ❌ Process ID mismatch: process='{process_id}', processRef='{process_ref}'")
                        results['failed'].append(f"ProcessRef mismatch: {process_id} != {process_ref}")
            
            # Check diagram
            print("\n🎨 Diagram Validation:")
            if diagram:
                shapes = root.findall('.//bpmndi:BPMNShape', ns)
                edges = root.findall('.//bpmndi:BPMNEdge', ns)
                plane = root.find('.//bpmndi:BPMNPlane', ns)
                
                print(f"  Shapes: {len(shapes)}")
                print(f"  Edges: {len(edges)}")
                
                if plane:
                    plane_ref = plane.get('bpmnElement')
                    print(f"  BPMNPlane bpmnElement: {plane_ref}")
                    if collab and plane_ref == collab.get('id'):
                        print("  ✅ Plane references correct collaboration")
                        results['passed'].append("BPMNPlane references collaboration")
                    else:
                        print(f"  ⚠️  Plane references '{plane_ref}' but collaboration is '{collab.get('id') if collab else 'N/A'}'")
                        results['warnings'].append("BPMNPlane may reference wrong collaboration")
                
                if len(shapes) >= len(components) + 2:  # components + start + end
                    results['passed'].append(f"{len(shapes)} shapes created")
                else:
                    results['warnings'].append(f"Only {len(shapes)} shapes for {len(components)} components")
                
                if len(edges) == len(flows):
                    results['passed'].append(f"{len(edges)} edges match {len(flows)} flows")
                else:
                    results['warnings'].append(f"{len(edges)} edges but {len(flows)} flows")
            
            # Check metadata files
            print("\n📝 Metadata Files:")
            try:
                manifest = z.read('META-INF/MANIFEST.MF').decode('utf-8')
                if 'Bundle-SymbolicName' in manifest and 'SAP-BundleType' in manifest:
                    print("  ✅ MANIFEST.MF valid")
                    results['passed'].append("MANIFEST.MF valid")
                else:
                    print("  ⚠️  MANIFEST.MF may be incomplete")
                    results['warnings'].append("MANIFEST.MF may be incomplete")
            except:
                pass
    
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        results['failed'].append(f"Validation error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("Validation Summary:")
    print("=" * 70)
    print(f"✅ Passed: {len(results['passed'])}")
    print(f"⚠️  Warnings: {len(results['warnings'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailures:")
        for f in results['failed']:
            print(f"  ❌ {f}")
    
    if results['warnings']:
        print("\nWarnings:")
        for w in results['warnings']:
            print(f"  ⚠️  {w}")
    
    print("\n" + "=" * 70)
    if len(results['failed']) == 0:
        print("✅ VALIDATION PASSED - File appears to be correctly structured")
        return True
    else:
        print("❌ VALIDATION FAILED - Issues found")
        return False

if __name__ == '__main__':
    zip_path = sys.argv[1] if len(sys.argv) > 1 else 'test_output_diagram_fixed/Test_iFlow_4_Components_Validation.zip'
    validate_iflow(zip_path)




