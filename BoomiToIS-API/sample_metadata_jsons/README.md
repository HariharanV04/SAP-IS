# Sample Metadata JSON Files

This directory contains sample metadata JSON files that demonstrate the correct format for generating SAP Integration Suite iFlows.

## ✅ Verified Working Samples

### `sample_simple_xml_to_json_flow.json` ⭐ **REFERENCE FORMAT**

**Status:** ✅ Verified working with EnhancedJSONToIFlowConverter and EnhancedIFlowGenerator

**Flow:** Start → Content Modifier → XML to JSON Converter → End

**Key Features:**
- ✅ Correct start/end event handling (auto-generated, not in components)
- ✅ Proper component type naming (snake_case)
- ✅ Valid sequence_flows referencing StartEvent_2 and EndEvent_2
- ✅ Complete SAP IS properties for all components
- ✅ xmlJsonPathTable array format (will be converted to HTML table)

**Use this as a reference for:**
- Correct metadata structure
- Start/end event handling
- Component configuration
- Sequence flow definition
- Property naming conventions

---

## Metadata Format Rules

### 1. Structure Requirements

**Required Top-Level Fields:**
```json
{
  "metadata_version": "1.0.0",
  "iflow_info": { ... },
  "endpoints": [ ... ]
}
```

**Required iflow_info Fields:**
- `id` - Unique identifier
- `name` - Display name
- `description` - Optional description
- `version` - Version number

**Optional iflow_info Fields:**
- `script_files` - Dictionary of script filenames to content (for Groovy scripts)
- `mapping_files` - Dictionary of mapping file paths to content (for message mappings, XSLT)
- `schema_files` - Dictionary of schema filenames to content (for XSD files)
- `wsd_files` - Dictionary of WSD filenames to content (for WSDL files)

**Required endpoint Fields:**
- `id` - Endpoint identifier
- `name` - Endpoint name
- `components` - Array of components
- `flow` - Array of component IDs (order matters)
- `sequence_flows` - Array of flow connections

### 2. Component Structure

Each component must have:
```json
{
  "type": "component_type",           // snake_case
  "id": "unique_component_id",
  "name": "Display Name",
  "sap_activity_type": "SAPType",     // PascalCase
  "config": {
    "componentVersion": "1.0",
    "cmdVariantUri": "ctype::...",
    "activityType": "ActivityType",
    // ... component-specific properties
  }
}
```

### 3. ⚠️ CRITICAL: Start/End Event Handling

**DO NOT include start_event or end_event in components array!**

❌ **WRONG:**
```json
{
  "components": [
    {
      "type": "start_event",  // DON'T DO THIS!
      "id": "start_001",
      ...
    },
    { ... other components ... },
    {
      "type": "end_event",  // DON'T DO THIS!
      "id": "end_001",
      ...
    }
  ]
}
```

✅ **CORRECT:**
```json
{
  "components": [
    // Only include actual flow components
    {
      "type": "content_modifier",
      "id": "content_modifier_001",
      ...
    },
    {
      "type": "xml_to_json_converter",
      "id": "xml_to_json_001",
      ...
    }
  ],
  "flow": [
    "content_modifier_001",
    "xml_to_json_001"
  ],
  "sequence_flows": [
    {
      "id": "flow_001",
      "source": "StartEvent_2",  // Auto-generated
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
      "target": "EndEvent_2"  // Auto-generated
    }
  ]
}
```

**Why:**
- The converter automatically creates `StartEvent_2` and `EndEvent_2`
- These are properly configured with all SAP IS requirements
- Including them as components causes duplicates or processing errors

### 4. Component Type Naming

**Use snake_case for component types:**
- ✅ `content_modifier`
- ✅ `xml_to_json_converter`
- ✅ `json_to_xml_converter`
- ✅ `groovy_script`
- ❌ `contentModifier` (wrong)
- ❌ `xmlToJsonConverter` (wrong)

**Use PascalCase for sap_activity_type:**
- ✅ `Enricher`
- ✅ `XmlToJsonConverter`
- ✅ `JsonToXmlConverter`
- ✅ `Script`

### 5. Required Component Properties

**All components MUST have:**
```json
{
  "config": {
    "componentVersion": "1.0",
    "cmdVariantUri": "ctype::FlowstepVariant/cname::ComponentName/version::1.0.x",
    "activityType": "ActivityType"
  }
}
```

### 6. Sequence Flows

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
- Every component must have at least one incoming and one outgoing flow
- First flow should have `"source": "StartEvent_2"`
- Last flow should have `"target": "EndEvent_2"`
- All component IDs referenced must exist

### 7. Special Property Handling

#### XML to JSON Converter - xmlJsonPathTable

**Input (JSON array):**
```json
{
  "xmlJsonPathTable": [
    "/Products/Product/Id",
    "/Products/Product/Name",
    "/Products/Product"
  ]
}
```

**Output (HTML-encoded table in SAP IS XML):**
```xml
<ifl:property>
    <key>xmlJsonPathTable</key>
    <value>&lt;row&gt;&lt;cell&gt;/Products/Product/Id&lt;/cell&gt;&lt;cell&gt;&lt;/cell&gt;&lt;/row&gt;...&lt;/value&gt;
</ifl:property>
```

The converter automatically handles this conversion.

#### Content Modifier - Headers and Properties

**Format as arrays of objects:**
```json
{
  "headers": [
    {
      "Action": "Create",
      "Type": "constant",
      "Name": "Content-Type",
      "Value": "application/xml",
      "DataType": "java.lang.String"
    }
  ],
  "properties": [
    {
      "Action": "Create",
      "Type": "expression",
      "Name": "myProperty",
      "Value": "${header.someHeader}",
      "DataType": "java.lang.String"
    }
  ]
}
```

These are automatically converted to XML tables (`headerTable`, `propertyTable`).

#### WSD (Web Service Definition) Files

**WSD files are stored in `src/main/resources/wsd/*.wsdl` folder in the generated ZIP.**

**Format 1: Direct WSD files in iflow_info:**
```json
{
  "iflow_info": {
    "id": "my_iflow",
    "name": "My iFlow",
    "wsd_files": {
      "MyService.wsdl": "<?xml version=\"1.0\"?>...<wsdl:definitions>...</wsdl:definitions>",
      "AnotherService.wsdl": "..."
    }
  }
}
```

**Format 2: WSD files referenced in SOAP adapter components:**
```json
{
  "components": [
    {
      "type": "soap_receiver",
      "id": "soap_receiver_001",
      "name": "SOAP Receiver",
      "config": {
        "wsdlContent": "<?xml version=\"1.0\"?>...<wsdl:definitions>...</wsdl:definitions>",
        "wsdlFilename": "MyService.wsdl",
        "location_id": "wsd/MyService.wsdl",
        // ... other SOAP adapter properties
      }
    }
  ]
}
```

**Supported WSD file properties:**
- `wsdlContent` - Full WSDL XML content (required)
- `wsdlFilename` - WSDL filename (required, will be used as filename in wsd folder)
- `location_id` - Alternative property name for WSDL file location/path
- `wsdlFile` - Alternative property name for WSDL filename

**Note:** WSD files are automatically extracted from:
1. `iflow_info.wsd_files` dictionary (direct file definitions)
2. SOAP adapter component configs (`wsdlContent` + `wsdlFilename`)
3. Sender/receiver adapter configs (if they contain WSDL references)

---

## Testing Your Metadata

### Validation Checklist

Before generating an iFlow, verify:

- [ ] `iflow_info` has `id` and `name`
- [ ] `endpoints` is an array with at least one endpoint
- [ ] Each endpoint has `components`, `flow`, and `sequence_flows`
- [ ] NO `start_event` or `end_event` in `components` array
- [ ] All component types use snake_case
- [ ] All components have `config` with required properties
- [ ] All component IDs are unique
- [ ] `flow` array lists components in order
- [ ] First sequence_flow has `source: "StartEvent_2"`
- [ ] Last sequence_flow has `target: "EndEvent_2"`
- [ ] All referenced component IDs exist

### Running the Converter

```bash
# From BoomiToIS-API directory
python -m enhanced_component_generation.enhanced_iflow_generator \
  sample_metadata_jsons/your_metadata.json \
  output/ \
  "Your iFlow Name"
```

---

## Common Issues and Solutions

### Issue: "Component not found" error

**Cause:** Component ID in `sequence_flows` doesn't exist in `components`

**Solution:** Check all IDs match exactly

### Issue: Duplicate start/end events

**Cause:** Including `start_event` or `end_event` in components

**Solution:** Remove them, use auto-generated `StartEvent_2` and `EndEvent_2`

### Issue: Missing flow references

**Cause:** Component has no incoming or outgoing flows

**Solution:** Ensure all components are included in `sequence_flows`

### Issue: Invalid property names

**Cause:** Using wrong property names (e.g., `streamJsonOutput` instead of `xmlJsonUseStreaming`)

**Solution:** Check `metadata_template/components.json` for correct property names

---

## File Descriptions

### Working Samples

- **`sample_simple_xml_to_json_flow.json`** ⭐
  - **Status:** ✅ Verified
  - **Flow:** Start → Content Modifier → XML to JSON → End
  - **Use as:** Primary reference for correct format

### Test Samples

- **`test_xml_to_json_converter.json`**
  - **Purpose:** Testing XML to JSON converter with xmlJsonPathTable
  - **Components:** 5 (Start, Content Modifier, XML to JSON, Script, End)

- **`test_4_components.json`**
  - **Purpose:** Testing multiple component flow
  - **Components:** 4 components with various types

### Example Samples

- **`api_gateway_rate_limiting.json`**
  - **Purpose:** Example of API gateway with rate limiting
  - **Features:** Multiple components, complex routing

- **`test.json`**
  - **Purpose:** General testing

---

## Additional Resources

- **Components Template:** `../metadata_template/components.json` - Complete reference for all 76+ component types
- **Technical Summary:** `../TECHNICAL_SUMMARY_METADATA_TO_IFLOW.md` - Detailed technical documentation
- **Converter Code:** `../enhanced_component_generation/enhanced_json_to_iflow_converter.py`

---

**Last Updated:** 2025-01-04
**Verified Working:** ✅ sample_simple_xml_to_json_flow.json


