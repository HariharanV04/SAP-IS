import zipfile
import re

with zipfile.ZipFile('test_output_final/Test_iFlow_4_Components_Validation.zip', 'r') as z:
    content = z.read('src/main/resources/scenarioflows/integrationflow/Test_iFlow_4_Components_Validation.iflw').decode('utf-8')

print("=== Full content_modifier_001 section ===")
# Find the component and a bit after it
comp_pos = content.find('id="content_modifier_001"')
if comp_pos != -1:
    # Get 1500 characters starting from the component
    section = content[comp_pos:comp_pos+1500]
    print(section)
    print("\n=== Checking for incoming/outgoing ===")
    print(f"Incoming found: {'<bpmn2:incoming>' in section}")
    print(f"Outgoing found: {'<bpmn2:outgoing>' in section}")




