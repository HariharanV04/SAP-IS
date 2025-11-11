#!/usr/bin/env python3
"""Count component templates in enhanced_component_templates.py"""

import re

with open('enhanced_component_generation/enhanced_component_templates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all template methods
templates = re.findall(r'def (\w+_template)\(self', content)

# Filter out helper methods and config templates
config_templates = {'iflow_configuration_template', 'participant_template', 'integration_process_participant_template'}
helper_methods = {'_escape_xml', '_format_property_value', '_flatten_nested_object', 
                  '_format_array_value', '_generate_property_xml', '_create_property_table_xml',
                  '_create_header_table_xml', '_create_modifications_table_xml', '_generate_unique_id'}

component_templates = [t for t in templates if not t.startswith('_') and t not in config_templates]

print(f"Total method definitions: {len(templates)}")
print(f"Helper methods: {len(helper_methods)}")
print(f"Configuration templates: {len(config_templates)}")
print(f"\n🎯 Component Templates (specific to components): {len(component_templates)}")
print(f"\nComponent templates list:")
for i, template in enumerate(sorted(component_templates), 1):
    print(f"  {i:2d}. {template}")




