# Byterover Knowledge Entry: Verified Metadata Format for SAP IS iFlow Generation

## Title
Verified JSON Metadata Format for BoomiToIS-API iFlow Generation

## Category
Architecture Pattern / API Contract / Verified Format

## Summary
Complete verified format for JSON metadata that successfully generates SAP Integration Suite iFlows. This format has been tested and confirmed working with EnhancedJSONToIFlowConverter and EnhancedIFlowGenerator. Critical rule: Start/End events are AUTO-GENERATED and must NOT be included in components array.

## Key Points

### 1. CRITICAL RULE: Start/End Event Handling

**DO NOT include `start_event` or `end_event` in components array!**

The converter automatically creates:
- `StartEvent_2` - Auto-generated start event (created in `_generate_process_section()`)
- `EndEvent_2` - Auto-generated end event (created in `_generate_process_section()`)

**Why this matters:**
- The converter checks for `component_type == "startEvent"` (camelCase) to skip them
- Including them as components with snake_case (`start_event`) will cause processing errors
- The auto-generated events are already properly configured with all required SAP IS properties

**Correct Format:**
```json
{
  "components": [
    // Only include actual flow components
    {
      "type": "content_modifier",
      "id": "content_modifier_001",
      "name": "Set XML Content",
      "sap_activity_type": "Enricher",
      "config": { ... }
    },
    {
      "type": "xml_to_json_converter",
      "id": "xml_to_json_001",
      "name": "Convert to JSON",
      "sap_activity_type": "XmlToJsonConverter",
      "config": { ... }
    }
  ],
  "flow": [
    "content_modifier_001",
    "xml_to_json_001"
  ],
  "sequence_flows": [
    {
      "id": "flow_001",
      "source": "StartEvent_2",  // Reference auto-generated start
      "target": "content_modifier_001"
    },
    {
      "id": "flow_002",
      "source": "content_modifier_001",
      "target": "xml_to_json_001"
    },
    {
      "id": "flow_003",
      "source": "xml_to_json_001",
      "target": "EndEvent_2"  // Reference auto-generated end
    }
  ]
}
```

### 2. Complete Metadata Structure

**Required Top-Level Fields:**
```json
{
  "metadata_version": "1.0.0",
  "iflow_info": {
    "id": "unique_iflow_id",
    "name": "iFlow Display Name",
    "description": "Optional description",
    "version": "1.0.0"
  },
  "endpoints": [
    {
      "id": "endpoint_id",
      "name": "Endpoint Name",
      "components": [ ... ],
      "flow": [ ... ],
      "sequence_flows": [ ... ]
    }
  ]
}
```

### 3. Component Structure Requirements

Each component must have:
```json
{
  "type": "component_type",           // MUST use snake_case
  "id": "unique_component_id",        // Must be unique
  "name": "Display Name",
  "sap_activity_type": "SAPType",     // MUST use PascalCase
  "config": {
    "componentVersion": "1.0",
    "cmdVariantUri": "ctype::FlowstepVariant/cname::ComponentName/version::1.0.x",
    "activityType": "ActivityType",
    // ... all component-specific properties
  }
}
```

**Component Type Naming:**
- ✅ Use snake_case: `content_modifier`, `xml_to_json_converter`, `groovy_script`
- ❌ Do NOT use camelCase: `contentModifier`, `xmlToJsonConverter`

**SAP Activity Type Naming:**
- ✅ Use PascalCase: `Enricher`, `XmlToJsonConverter`, `JsonToXmlConverter`
- ❌ Do NOT use snake_case or lowercase

### 4. Verified Working Components

**Tested and Confirmed Working:**
- ✅ `content_modifier` (with headers array support)
- ✅ `xml_to_json_converter` (with xmlJsonPathTable array support)
- ✅ Auto-generated `StartEvent_2` and `EndEvent_2`

**Component Properties:**
- All components must have `componentVersion`, `cmdVariantUri`, and `activityType` in config
- Special properties like `xmlJsonPathTable` are automatically converted (array → HTML table)
- Headers and properties arrays are automatically converted to XML tables

### 5. Sequence Flow Rules

**Format:**
```json
{
  "sequence_flows": [
    {
      "id": "unique_flow_id",
      "source": "source_component_id",  // Must exist in components or be StartEvent_2
      "target": "target_component_id"   // Must exist in components or be EndEvent_2
    }
  ]
}
```

**Rules:**
- First flow MUST have `"source": "StartEvent_2"`
- Last flow MUST have `"target": "EndEvent_2"`
- All component IDs referenced must exist in `components` array
- Every component must have at least one incoming and one outgoing flow

### 6. Special Property Handling

**XML to JSON Converter - xmlJsonPathTable:**
- Input: JSON array of XPath strings
- Output: Automatically converted to HTML-encoded XML table
- Example:
```json
{
  "xmlJsonPathTable": [
    "/Products/Product/Id",
    "/Products/Product/Name",
    "/Products/Product"
  ]
}
```
- Converts to: `&lt;row&gt;&lt;cell&gt;/Products/Product/Id&lt;/cell&gt;&lt;cell&gt;&lt;/cell&gt;&lt;/row&gt;...`

**Content Modifier - Headers/Properties:**
- Format as arrays of objects with Action, Type, Name, Value, DataType
- Automatically converted to XML tables (`headerTable`, `propertyTable`)

## Reference Files

**Primary Reference:**
- `BoomiToIS-API/sample_metadata_jsons/sample_simple_xml_to_json_flow.json` ⭐
  - ✅ Verified working format
  - Complete example with all correct patterns

**Documentation:**
- `BoomiToIS-API/sample_metadata_jsons/README.md` - Complete format guide
- `BoomiToIS-API/TECHNICAL_SUMMARY_METADATA_TO_IFLOW.md` - Technical details

**Code Locations:**
- Converter: `BoomiToIS-API/enhanced_component_generation/enhanced_json_to_iflow_converter.py`
- Templates: `BoomiToIS-API/enhanced_component_generation/enhanced_component_templates.py`
- Generator: `BoomiToIS-API/enhanced_component_generation/enhanced_iflow_generator.py`

## Common Mistakes to Avoid

1. ❌ Including `start_event` or `end_event` in components array
2. ❌ Using camelCase for component types (`contentModifier` instead of `content_modifier`)
3. ❌ Missing required properties in config (`componentVersion`, `cmdVariantUri`, `activityType`)
4. ❌ Referencing non-existent component IDs in sequence_flows
5. ❌ Using wrong property names (e.g., `streamJsonOutput` instead of `xmlJsonUseStreaming`)

## Validation Checklist

Before generating iFlow, verify:
- [ ] `iflow_info` has `id` and `name`
- [ ] `endpoints` is array with at least one endpoint
- [ ] Each endpoint has `components`, `flow`, and `sequence_flows`
- [ ] NO `start_event` or `end_event` in `components` array
- [ ] All component types use snake_case
- [ ] All components have `config` with required properties
- [ ] All component IDs are unique
- [ ] `flow` array lists components in order
- [ ] First sequence_flow has `source: "StartEvent_2"`
- [ ] Last sequence_flow has `target: "EndEvent_2"`
- [ ] All referenced component IDs exist

## When to Use This Knowledge

- When creating new metadata JSON files for iFlow generation
- When debugging iFlow generation errors
- When validating metadata format
- When explaining the conversion process to others
- When troubleshooting component generation issues

## Related Patterns

- SAP Integration Suite BPMN 2.0 structure
- Component template generation
- Dynamic property mapping from JSON to SAP IS XML
- Sequence flow generation and flow reference tracking

## Last Updated
2025-01-04

## Verification Status
✅ Tested and confirmed working with real iFlow generation


