"""
Validate sample JSON files against components.json metadata template
"""
import json
import os
import sys

def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_sample(sample_path, components_metadata):
    """Validate a sample JSON file"""
    print(f"\n{'='*80}")
    print(f"Validating: {os.path.basename(sample_path)}")
    print(f"{'='*80}")

    try:
        sample = load_json(sample_path)
    except Exception as e:
        print(f"ERROR: Could not load JSON: {e}")
        return False

    issues = []

    # Check iflow_info
    if "iflow_info" not in sample:
        issues.append("Missing 'iflow_info' section")
    else:
        iflow_info = sample["iflow_info"]
        required_fields = ["id", "name"]
        for field in required_fields:
            if field not in iflow_info:
                issues.append(f"Missing required field 'iflow_info.{field}'")

    # Check endpoints
    if "endpoints" not in sample:
        issues.append("Missing 'endpoints' array")
        return False

    endpoints = sample["endpoints"]
    if not endpoints:
        issues.append("'endpoints' array is empty")
        return False

    # Validate each endpoint
    for idx, endpoint in enumerate(endpoints):
        endpoint_name = endpoint.get("name", f"Endpoint {idx}")
        print(f"\n--- Endpoint: {endpoint_name} ---")

        if "components" not in endpoint:
            issues.append(f"Endpoint '{endpoint_name}' missing 'components' array")
            continue

        components = endpoint["components"]
        print(f"Components: {len(components)}")

        # Validate each component
        for comp_idx, component in enumerate(components):
            comp_type = component.get("type", "unknown")
            comp_id = component.get("id", f"component_{comp_idx}")
            comp_name = component.get("name", "Unnamed")

            print(f"\n  [{comp_idx + 1}] {comp_type}")
            print(f"      ID: {comp_id}")
            print(f"      Name: {comp_name}")

            # Check required fields
            if "type" not in component:
                issues.append(f"Component {comp_idx} missing 'type' field")
                continue

            if "config" not in component:
                issues.append(f"Component '{comp_id}' missing 'config' section")
                print(f"      ERROR: Missing 'config' section")
                continue

            config = component["config"]

            # Check critical SAP IS properties
            # Note: sender/receiver don't need cmdVariantUri (they're endpoint participants, not flow steps)
            critical_props = []
            if comp_type not in ["sender", "receiver"]:
                critical_props = ["componentVersion", "cmdVariantUri"]

            missing_props = []
            for prop in critical_props:
                if prop not in config:
                    missing_props.append(prop)

            if missing_props:
                issues.append(f"Component '{comp_id}' missing critical properties: {', '.join(missing_props)}")
                print(f"      WARNING: Missing properties: {', '.join(missing_props)}")
            elif critical_props:  # Only print if we checked for properties
                print(f"      componentVersion: {config['componentVersion']}")
                print(f"      cmdVariantUri: {config['cmdVariantUri']}")

            # Count total properties
            print(f"      Total properties: {len(config)}")

            # Check if component type exists in metadata (if we have it loaded)
            # This is just informational
            if components_metadata:
                template_key = None
                for key in components_metadata.get("component_templates", {}).keys():
                    template = components_metadata["component_templates"][key]
                    if isinstance(template, dict) and template.get("type") == comp_type:
                        template_key = key
                        break

                if not template_key:
                    print(f"      INFO: Component type '{comp_type}' not found in metadata template")

    # Summary
    print(f"\n{'='*80}")
    if issues:
        print(f"ISSUES FOUND: {len(issues)}")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("VALIDATION PASSED")
        return True

def main():
    """Main validation function"""
    # Paths
    base_dir = os.path.dirname(os.path.dirname(__file__))
    samples_dir = os.path.join(base_dir, "sample_metadata_jsons")
    metadata_file = os.path.join(base_dir, "metadata_template", "components.json")

    # Load metadata template
    print(f"Loading metadata template from: {metadata_file}")
    try:
        components_metadata = load_json(metadata_file)
        print(f"Metadata loaded successfully")
    except Exception as e:
        print(f"WARNING: Could not load metadata template: {e}")
        components_metadata = None

    # Find all sample JSON files
    sample_files = []
    for file in os.listdir(samples_dir):
        if file.endswith(".json"):
            sample_files.append(os.path.join(samples_dir, file))

    print(f"\nFound {len(sample_files)} sample files to validate")

    # Validate each sample
    results = {}
    for sample_file in sorted(sample_files):
        result = validate_sample(sample_file, components_metadata)
        results[os.path.basename(sample_file)] = result

    # Final summary
    print(f"\n\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    passed = sum(1 for r in results.values() if r)
    failed = len(results) - passed
    print(f"Total files: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    for file, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {file}")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
