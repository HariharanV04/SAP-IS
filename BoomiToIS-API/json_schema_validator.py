#!/usr/bin/env python3
"""
JSON Schema Validator for SAP Integration Suite iFlow Generation
Ensures JSON follows the documented schema before processing
"""

import json
import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of JSON schema validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    fixed_json: Optional[Dict[str, Any]] = None

class SAPIFlowSchemaValidator:
    """Validates JSON against SAP iFlow schema requirements"""
    
    def __init__(self):
        # Valid component types from our schema
        self.valid_component_types = {
            "content_modifier", "script", "gateway", "message_mapping",
            "request_reply", "odata", "sftp", "subprocess", "exception_subprocess",
            "http_adapter", "rest", "groovy", "mapping", "router"
        }
        
        # Required fields for each component type
        self.component_requirements = {
            "content_modifier": {
                "required": ["id", "name", "config"],
                "config_required": ["headers"]  # Either headers or body
            },
            "gateway": {
                "required": ["id", "name", "config"],
                "config_required": ["routing_conditions"]
            },
            "script": {
                "required": ["id", "name", "config"],
                "config_required": ["script"]
            },
            "subprocess": {
                "required": ["id", "name", "config"],
                "config_required": ["components"]
            }
        }
        
        # Valid config keys for each component type
        self.valid_config_keys = {
            "content_modifier": ["headers", "body_type", "body_content"],
            "gateway": ["routing_conditions"],
            "script": ["script"],
            "message_mapping": ["mapping_name", "source_schema", "target_schema"],
            "request_reply": ["url", "method", "headers"],
            "odata": ["operation", "service_url", "entity_set"],
            "sftp": ["host", "port", "path", "username", "auth_type", "operation"],
            "subprocess": ["components"],
            "exception_subprocess": ["components"]
        }

    def validate_json_schema(self, json_data: Dict[str, Any]) -> ValidationResult:
        """
        Main validation method for SAP iFlow JSON
        Returns ValidationResult with validation status and any errors
        """
        errors = []
        warnings = []
        
        try:
            # Basic structure validation
            self._validate_root_structure(json_data, errors)
            
            if not errors:
                # Component validation
                self._validate_components(json_data, errors, warnings)
                
                # Flow validation
                self._validate_sequence_flows(json_data, errors, warnings)
                
                # SAP compliance validation
                self._validate_sap_compliance(json_data, errors, warnings)
            
            # Try to fix common issues
            fixed_json = None
            if errors:
                fixed_json = self._auto_fix_common_issues(json_data, errors)
                if fixed_json:
                    # Re-validate fixed JSON
                    revalidation = self.validate_json_schema(fixed_json)
                    if revalidation.is_valid:
                        warnings.append("JSON was automatically fixed and now passes validation")
                        return ValidationResult(True, [], warnings, fixed_json)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                fixed_json=fixed_json
            )
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return ValidationResult(False, errors, warnings)

    def _validate_root_structure(self, json_data: Dict[str, Any], errors: List[str]):
        """Validate root JSON structure"""
        if not isinstance(json_data, dict):
            errors.append("Root must be a JSON object")
            return
            
        if "endpoints" not in json_data:
            errors.append("Missing 'endpoints' array")
            return
            
        if not isinstance(json_data["endpoints"], list):
            errors.append("'endpoints' must be an array")
            return
            
        if len(json_data["endpoints"]) == 0:
            errors.append("'endpoints' array cannot be empty")

    def _validate_components(self, json_data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate all components in the JSON"""
        for endpoint_idx, endpoint in enumerate(json_data["endpoints"]):
            if "components" not in endpoint:
                errors.append(f"Endpoint {endpoint_idx}: Missing 'components' array")
                continue
                
            if not isinstance(endpoint["components"], list):
                errors.append(f"Endpoint {endpoint_idx}: 'components' must be an array")
                continue
                
            for comp_idx, component in enumerate(endpoint["components"]):
                self._validate_single_component(component, endpoint_idx, comp_idx, errors, warnings)

    def _validate_single_component(self, component: Dict[str, Any], endpoint_idx: int, comp_idx: int, 
                                 errors: List[str], warnings: List[str]):
        """Validate a single component"""
        # Check required fields
        if "type" not in component:
            errors.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: Missing 'type'")
            return
            
        if "id" not in component:
            errors.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: Missing 'id'")
            return
            
        if "name" not in component:
            errors.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: Missing 'name'")
            return
            
        # Validate component type
        comp_type = component["type"]
        if comp_type not in self.valid_component_types:
            errors.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: Invalid type '{comp_type}'. Valid types: {', '.join(sorted(self.valid_component_types))}")
            return
            
        # Validate component-specific requirements
        if comp_type in self.component_requirements:
            reqs = self.component_requirements[comp_type]
            
            # Check required fields
            for field in reqs["required"]:
                if field not in component:
                    errors.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: Missing required field '{field}' for type '{comp_type}'")
                    
            # Check config requirements
            if "config" in component and "config_required" in reqs:
                config = component["config"]
                if not isinstance(config, dict):
                    errors.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: 'config' must be an object")
                else:
                    for config_field in reqs["config_required"]:
                        if config_field not in config:
                            errors.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: Missing required config field '{config_field}' for type '{comp_type}'")
                            
        # Validate config keys
        if "config" in component and comp_type in self.valid_config_keys:
            config = component["config"]
            if isinstance(config, dict):
                valid_keys = self.valid_config_keys[comp_type]
                for key in config.keys():
                    if key not in valid_keys:
                        warnings.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: Unknown config key '{key}' for type '{comp_type}'. Valid keys: {', '.join(valid_keys)}")

    def _validate_sequence_flows(self, json_data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate sequence flows"""
        for endpoint_idx, endpoint in enumerate(json_data["endpoints"]):
            if "sequence_flows" not in endpoint:
                warnings.append(f"Endpoint {endpoint_idx}: No sequence flows defined - will use automatic flow generation")
                continue
                
            if not isinstance(endpoint["sequence_flows"], list):
                errors.append(f"Endpoint {endpoint_idx}: 'sequence_flows' must be an array")
                continue
                
            # Get component IDs for validation
            component_ids = {comp["id"] for comp in endpoint.get("components", [])}
            component_ids.add("StartEvent_2")  # Standard start event
            component_ids.add("EndEvent_2")    # Standard end event
            
            for flow_idx, flow in enumerate(endpoint["sequence_flows"]):
                self._validate_single_flow(flow, endpoint_idx, flow_idx, component_ids, errors, warnings)

    def _validate_single_flow(self, flow: Dict[str, Any], endpoint_idx: int, flow_idx: int, 
                             component_ids: set, errors: List[str], warnings: List[str]):
        """Validate a single sequence flow"""
        if "id" not in flow:
            errors.append(f"Endpoint {endpoint_idx}, Flow {flow_idx}: Missing 'id'")
            
        if "source_ref" not in flow:
            errors.append(f"Endpoint {endpoint_idx}, Flow {flow_idx}: Missing 'source_ref'")
            
        if "target_ref" not in flow:
            errors.append(f"Endpoint {endpoint_idx}, Flow {flow_idx}: Missing 'target_ref'")
            
        # Check if source and target components exist
        if "source_ref" in flow and flow["source_ref"] not in component_ids:
            errors.append(f"Endpoint {endpoint_idx}, Flow {flow_idx}: Source component '{flow['source_ref']}' not found")
            
        if "target_ref" in flow and flow["target_ref"] not in component_ids:
            errors.append(f"Endpoint {endpoint_idx}, Flow {flow_idx}: Target component '{flow['target_ref']}' not found")

    def _validate_sap_compliance(self, json_data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate SAP-specific compliance requirements"""
        # Check for common SAP compliance issues
        for endpoint_idx, endpoint in enumerate(json_data["endpoints"]):
            for comp_idx, component in enumerate(endpoint.get("components", [])):
                comp_type = component.get("type", "")
                
                # Content modifier with headers should be validated
                if comp_type == "content_modifier" and "config" in component:
                    config = component["config"]
                    if "headers" in config and "body" in config:
                        warnings.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: Component has both 'headers' and 'body' - headers will take precedence (Content Enricher)")
                        
                # Gateway validation
                if comp_type == "gateway" and "config" in component:
                    config = component["config"]
                    if "routing_conditions" in config:
                        conditions = config["routing_conditions"]
                        if not isinstance(conditions, list):
                            errors.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: 'routing_conditions' must be an array")
                        else:
                            # Check for default route
                            has_default = any(cond.get("condition") == "default" for cond in conditions)
                            if not has_default:
                                warnings.append(f"Endpoint {endpoint_idx}, Component {comp_idx}: Gateway has no default route - ensure all paths are covered")

    def _auto_fix_common_issues(self, json_data: Dict[str, Any], errors: List[str]) -> Optional[Dict[str, Any]]:
        """Attempt to automatically fix common JSON issues"""
        try:
            # Deep copy to avoid modifying original
            import copy
            fixed_json = copy.deepcopy(json_data)
            
            # Fix 1: Add missing sequence_flows if components exist but no flows
            for endpoint in fixed_json.get("endpoints", []):
                if "components" in endpoint and "sequence_flows" not in endpoint:
                    endpoint["sequence_flows"] = []
                    warnings.append("Added missing sequence_flows array")
                    
            # Fix 2: Ensure all components have config
            for endpoint in fixed_json.get("endpoints", []):
                for component in endpoint.get("components", []):
                    if "config" not in component:
                        component["config"] = {}
                        
            # Fix 3: Add standard start/end events if missing
            for endpoint in fixed_json.get("endpoints", []):
                components = endpoint.get("components", [])
                component_ids = {comp.get("id", "") for comp in components}
                
                # Add start event if not present
                if "StartEvent_2" not in component_ids:
                    start_event = {
                        "type": "start_event",
                        "id": "StartEvent_2",
                        "name": "Start"
                    }
                    components.insert(0, start_event)
                    
                # Add end event if not present
                if "EndEvent_2" not in component_ids:
                    end_event = {
                        "type": "end_event",
                        "id": "EndEvent_2",
                        "name": "End"
                    }
                    components.append(end_event)
                    
            return fixed_json
            
        except Exception as e:
            # If fixing fails, return None
            return None

    def get_schema_template(self) -> str:
        """Get a template JSON structure for guidance"""
        return """{
  "endpoints": [
    {
      "id": "flow_id",
      "name": "Flow Name",
      "description": "Flow Description",
      "components": [
        {
          "type": "content_modifier",
          "id": "set_headers",
          "name": "Set Headers",
          "config": {
            "headers": {
              "Content-Type": "application/json"
            }
          }
        }
      ],
      "sequence_flows": [
        {
          "id": "f1_start_to_header",
          "source_ref": "StartEvent_2",
          "target_ref": "set_headers"
        }
      ]
    }
  ]
}"""

    def get_component_examples(self) -> Dict[str, str]:
        """Get examples for each component type"""
        return {
            "content_modifier": """{
  "type": "content_modifier",
  "id": "set_headers",
  "name": "Set Headers",
  "config": {
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer ${property.token}"
    }
  }
}""",
            "gateway": """{
  "type": "gateway",
  "id": "route_message",
  "name": "Route Message",
  "config": {
    "routing_conditions": [
      {
        "condition": "${property.type} == 'order'",
        "target": "process_order"
      },
      {
        "condition": "default",
        "target": "default_handler"
      }
    ]
  }
}""",
            "script": """{
  "type": "script",
  "id": "validate_input",
  "name": "Validate Input",
  "config": {
    "script": "log.info('Processing message'); return message;"
  }
}"""
        }

def validate_iflow_json(json_data: Dict[str, Any]) -> ValidationResult:
    """
    Convenience function to validate iFlow JSON
    Usage: result = validate_iflow_json(json_data)
    """
    validator = SAPIFlowSchemaValidator()
    return validator.validate_json_schema(json_data)

def create_schema_aware_prompt(user_request: str) -> str:
    """
    Create a prompt that includes schema requirements
    Usage: prompt = create_schema_aware_prompt("Create an order processing flow")
    """
    validator = SAPIFlowSchemaValidator()
    
    return f"""Create a SAP Integration Suite iFlow JSON following this EXACT schema structure:

{validator.get_schema_template()}

VALID COMPONENT TYPES:
{', '.join(sorted(validator.valid_component_types))}

COMPONENT REQUIREMENTS:
- content_modifier: Must have 'config' with 'headers' (for headers) or 'body' (for body transformation)
- gateway: Must have 'config.routing_conditions' array with conditions and targets
- script: Must have 'config.script' with Groovy code
- subprocess: Must have 'config.components' array for nested components

SEQUENCE FLOWS:
- Must connect all components in logical order
- Use 'source_ref' and 'target_ref' to specify connections
- Include flows from StartEvent_2 to first component
- Include flows from last component to EndEvent_2

USER REQUEST: {user_request}

IMPORTANT: 
1. Follow the schema structure exactly
2. Use only documented component types
3. Ensure all components have required config fields
4. Create logical sequence flows between components
5. Include StartEvent_2 and EndEvent_2 if not specified

Generate ONLY the JSON, no explanations or markdown formatting."""

if __name__ == "__main__":
    # Test the validator
    test_json = {
        "endpoints": [
            {
                "id": "test_flow",
                "name": "Test Flow",
                "description": "Test flow for validation",
                "components": [
                    {
                        "type": "content_modifier",
                        "id": "set_header",
                        "name": "Set Header",
                        "config": {
                            "headers": {
                                "Content-Type": "application/json"
                            }
                        }
                    }
                ],
                "sequence_flows": [
                    {
                        "id": "f1_start_to_header",
                        "source_ref": "StartEvent_2",
                        "target_ref": "set_header"
                    }
                ]
            }
        ]
    }
    
    result = validate_iflow_json(test_json)
    print(f"Validation Result: {result.is_valid}")
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
