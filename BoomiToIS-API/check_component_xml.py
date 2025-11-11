import zipfile
import re

with zipfile.ZipFile('test_output_structure_fixed/Test_iFlow_4_Components_Validation.zip', 'r') as z:
    content = z.read('src/main/resources/scenarioflows/integrationflow/Test_iFlow_4_Components_Validation.iflw').decode('utf-8')

print("=== Checking content_modifier_001 XML ===")
comp1 = re.search(r'<bpmn2:callActivity[^>]*id="content_modifier_001"[^>]*>.*?</bpmn2:callActivity>', content, re.DOTALL)
if comp1:
    comp_xml = comp1.group(0)
    print(comp_xml)
    print("\n=== Has incoming? ===")
    print('incoming' in comp_xml)
    print("\n=== Has outgoing? ===")
    print('outgoing' in comp_xml)
else:
    print("Component not found")




