"""
Fix sample JSON files to match SAP IS compatibility requirements

Issues to fix:
1. Remove cmdVariantUri check for sender/receiver (they don't need it)
2. Fix component type mismatches:
   - groovy_script -> script
   - edi_to_xml -> edi_to_xml_converter
   - xml_to_edi -> xml_to_edi_converter
   - json_to_xml -> json_to_xml_converter
   - xslt_transform -> xslt_mapping
"""
import json
import os
import sys

def fix_component_types(component):
    """Fix component type naming to match metadata template"""
    type_mapping = {
        "groovy_script": "script",
        "edi_to_xml": "edi_to_xml_converter",
        "xml_to_edi": "xml_to_edi_converter",
        "json_to_xml": "json_to_xml_converter",
        "xslt_transform": "xslt_mapping"
    }

    if component["type"] in type_mapping:
        old_type = component["type"]
        new_type = type_mapping[old_type]
        component["type"] = new_type
        print(f"      Fixed: '{old_type}' -> '{new_type}'")
        return True
    return False

def fix_sample_file(file_path):
    """Fix a single sample JSON file"""
    print(f"\nProcessing: {os.path.basename(file_path)}")
    print("="*80)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load JSON: {e}")
        return False

    changes_made = False

    # Process each endpoint
    for endpoint_idx, endpoint in enumerate(data.get("endpoints", [])):
        endpoint_name = endpoint.get("name", f"Endpoint {endpoint_idx}")

        # Process each component
        for comp_idx, component in enumerate(endpoint.get("components", [])):
            comp_type = component.get("type", "unknown")
            comp_id = component.get("id", f"component_{comp_idx}")

            # Fix component type if needed
            if fix_component_types(component):
                changes_made = True

    if changes_made:
        # Save fixed file
        backup_path = file_path + ".backup"
        os.rename(file_path, backup_path)
        print(f"  Backup saved: {backup_path}")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Fixed file saved: {file_path}")
        return True
    else:
        print(f"  No changes needed")
        return False

def main():
    """Main function"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    samples_dir = os.path.join(base_dir, "sample_metadata_jsons")

    # Find all sample JSON files
    sample_files = []
    for file in os.listdir(samples_dir):
        if file.endswith(".json") and not file.endswith(".backup"):
            sample_files.append(os.path.join(samples_dir, file))

    print(f"Found {len(sample_files)} sample files to process")

    # Fix each sample
    fixed_count = 0
    for sample_file in sorted(sample_files):
        if fix_sample_file(sample_file):
            fixed_count += 1

    # Final summary
    print(f"\n\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"Total files processed: {len(sample_files)}")
    print(f"Files fixed: {fixed_count}")
    print(f"Files unchanged: {len(sample_files) - fixed_count}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
