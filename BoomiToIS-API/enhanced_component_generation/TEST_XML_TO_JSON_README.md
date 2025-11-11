# XML to JSON Converter Test Guide

## Overview

This guide explains how to test the XML to JSON converter component with the new `xmlJsonPathTable` array-to-HTML-table conversion feature.

## Test Files Created

### 1. **Test Metadata JSON**
- **Location:** `sample_metadata_jsons/test_xml_to_json_converter.json`
- **Purpose:** Complete test metadata for XML to JSON converter validation
- **Components:** 5 (Start → Content Modifier → XML to JSON → Script → End)

### 2. **Test Script**
- **Location:** `test_xml_to_json_generation.py` (in root BoomiToIS-API/)
- **Purpose:** Validates XML generation and property conversion

---

## Test Metadata Structure

### Flow Components

```
Start Event
    ↓
Content Modifier (Set XML Input)
    ↓
XML to JSON Converter ⭐ TEST FOCUS
    ↓
Groovy Script (Log Output)
    ↓
End Event
```

### XML to JSON Converter Configuration

The test metadata includes all new SAP IS properties:

```json
{
  "type": "xml_to_json_converter",
  "id": "xml_to_json_001",
  "name": "Convert XML to JSON",
  "config": {
    "componentVersion": "1.0",
    "cmdVariantUri": "ctype::FlowstepVariant/cname::XmlToJsonConverter/version::1.0.8",
    "activityType": "XmlToJsonConverter",
    "xmlJsonUseStreaming": "true",
    "xmlJsonSuppressRootElement": "false",
    "xmlJsonConvertAllElements": "specific",
    "xmlJsonPathTable": [
      "/Titles/Title/businessUnits",
      "/Titles/Title"
    ],
    "jsonOutputEncoding": "UTF-8",
    "jsonNamespaceMapping": "",
    "useNamespaces": "false",
    "jsonNamespaceSeparator": ":"
  }
}
```

### Key Test Points

1. **xmlJsonPathTable Array → HTML Table Conversion**
   - Input: `["/Titles/Title/businessUnits", "/Titles/Title"]`
   - Expected Output: `&lt;row&gt;&lt;cell&gt;/Titles/Title/businessUnits&lt;/cell&gt;&lt;cell&gt;&lt;/cell&gt;&lt;/row&gt;&lt;row&gt;&lt;cell&gt;/Titles/Title&lt;/cell&gt;&lt;cell&gt;&lt;/cell&gt;&lt;/row&gt;`

2. **All SAP IS Property Names**
   - Uses actual SAP IS names: `xmlJsonUseStreaming`, `xmlJsonSuppressRootElement`, etc.
   - NOT using metadata names like `streamJsonOutput`

3. **Sample XML Input**
   - Content Modifier sets XML body:
     ```xml
     <Titles>
       <Title>
         <businessUnits>Engineering</businessUnits>
         <name>Product Manager</name>
       </Title>
       <Title>
         <businessUnits>Sales</businessUnits>
         <name>Sales Director</name>
       </Title>
     </Titles>
     ```

---

## Running the Tests

### Test 1: Validate Component XML Generation

```bash
cd "C:\Users\ASUS\vs code projects\ITR\ImigrateAgent\BoomiToIS-API"
python test_xml_to_json_generation.py
```

**Expected Output:**
```
================================================================================
Testing XML to JSON Converter iFlow Generation
================================================================================

1. Loading metadata from: sample_metadata_jsons/test_xml_to_json_converter.json
   iFlow name: Test XML to JSON Converter Flow
   Components: 5

2. Testing XML to JSON Converter component:
   Component ID: xml_to_json_001
   Component Name: Convert XML to JSON

3. Generating component XML:
   [Shows generated XML snippet]

4. Validating output:
   [PASS] xmlJsonPathTable property
   [PASS] HTML-encoded table
   [PASS] XPath expressions
   [PASS] xmlJsonUseStreaming
   [PASS] xmlJsonSuppressRootElement

5. Examining xmlJsonPathTable value:
   Value length: 186 characters
   Contains &lt;: True
   Contains &gt;: True

================================================================================
SUCCESS: All validation checks passed!
================================================================================
```

### Test 2: Generate Complete iFlow ZIP (TODO)

**Note:** The full iFlow ZIP generation requires fixing the `enhanced_json_to_iflow_converter.py` file which is currently empty.

**Planned command:**
```bash
python -m enhanced_component_generation.enhanced_iflow_generator \
  --input_file sample_metadata_jsons/test_xml_to_json_converter.json \
  --output_dir output_test_xml_to_json \
  --iflow_name "TestXMLToJSONConverter"
```

**Expected Output:**
- ZIP file: `output_test_xml_to_json/TestXMLToJSONConverter.zip`
- Contains: `.iflw` file with all 5 components
- Ready for SAP IS import

---

## Validation Checklist

### ✅ JSON Metadata Validation
- [x] Valid JSON syntax
- [x] All required fields present
- [x] 5 components defined
- [x] 4 sequence flows connecting components
- [x] Correct component types and IDs

### ✅ XML Generation Validation
- [x] xmlJsonPathTable array converted to HTML-encoded table
- [x] HTML entities used: `&lt;` and `&gt;`
- [x] Both XPath expressions present in output
- [x] All SAP IS properties included
- [x] Correct property naming (xmlJsonXxx format)

### ⏳ Full iFlow Package Validation (Pending)
- [ ] Generate ZIP file successfully
- [ ] Extract and verify `.iflw` structure
- [ ] Verify BPMN `bpmn2:incoming/outgoing` elements
- [ ] Verify all components connected in diagram

### ⏳ SAP IS Import Validation (Manual)
- [ ] Import ZIP to SAP Integration Suite
- [ ] All components appear in diagram
- [ ] Components are properly connected
- [ ] XML to JSON converter properties match:
  - [ ] xmlJsonUseStreaming = true
  - [ ] xmlJsonSuppressRootElement = false
  - [ ] xmlJsonConvertAllElements = specific
  - [ ] xmlJsonPathTable = HTML-encoded table with both XPath expressions
  - [ ] jsonOutputEncoding = UTF-8
  - [ ] useNamespaces = false

### ⏳ Runtime Execution Validation (Manual)
- [ ] Deploy iFlow to SAP IS
- [ ] Execute test run
- [ ] Verify XML input is converted to JSON
- [ ] Check script logs JSON output in properties
- [ ] Verify XPath filtering works (only specified paths converted)

---

## Expected Results

### Generated xmlJsonPathTable Value

**Input (from JSON):**
```json
"xmlJsonPathTable": [
  "/Titles/Title/businessUnits",
  "/Titles/Title"
]
```

**Output (in .iflw XML):**
```xml
<ifl:property>
    <key>xmlJsonPathTable</key>
    <value>&lt;row&gt;&lt;cell&gt;/Titles/Title/businessUnits&lt;/cell&gt;&lt;cell&gt;&lt;/cell&gt;&lt;/row&gt;&lt;row&gt;&lt;cell&gt;/Titles/Title&lt;/cell&gt;&lt;cell&gt;&lt;/cell&gt;&lt;/row&gt;</value>
</ifl:property>
```

### Expected JSON Output (after conversion)

When the iFlow executes with the sample XML input, the expected JSON output should include only the specified XPath elements:

```json
{
  "businessUnits": ["Engineering", "Sales"],
  "Title": [
    {
      "businessUnits": "Engineering",
      "name": "Product Manager"
    },
    {
      "businessUnits": "Sales",
      "name": "Sales Director"
    }
  ]
}
```

---

## Troubleshooting

### Issue: "ImportError: cannot import name 'EnhancedJSONToIFlowConverter'"

**Cause:** The `enhanced_json_to_iflow_converter.py` file in the `enhanced_component_generation/` folder is empty.

**Solution:** Use the component-level test script (`test_xml_to_json_generation.py`) which directly tests the template generation without requiring the full converter.

### Issue: "xmlJsonPathTable not HTML-encoded"

**Cause:** The property might be getting double-escaped by `_format_property_value()`.

**Solution:** Already fixed! The code now skips the `_format_property_value()` call for `xmlJsonPathTable` since it's already HTML-encoded by `_create_xpath_path_table_xml()`.

### Issue: "XPath expressions missing from output"

**Cause:** Array might be empty or not being passed correctly.

**Solution:** Verify the JSON metadata has the `xmlJsonPathTable` array populated with at least one XPath expression.

---

## Implementation Details

### Files Modified/Created

1. **metadata_template/components.json** (Updated)
   - Lines 594-612: xml_to_json_converter definition
   - Updated all property names to match SAP IS (xmlJsonXxx format)
   - Added xmlJsonPathTable as array type

2. **enhanced_component_generation/enhanced_component_templates.py** (Updated)
   - Lines 306-354: `_create_xpath_path_table_xml()` helper method
   - Lines 187-200: Updated `_generate_property_xml()` to handle xmlJsonPathTable
   - Lines 203-207: Skip double-encoding for xmlJsonPathTable

3. **sample_metadata_jsons/test_xml_to_json_converter.json** (Created)
   - Complete test metadata with 5 components
   - XML to JSON converter with all new properties
   - Sample XML input for testing

4. **test_xml_to_json_generation.py** (Created)
   - Validation script for component XML generation
   - Tests xmlJsonPathTable conversion
   - Verifies HTML encoding

5. **enhanced_component_generation/test_xml_to_json.py** (Created earlier)
   - Unit tests for `_create_xpath_path_table_xml()` method
   - Tests all edge cases

---

## Next Steps

### Immediate
1. ✅ Create test metadata JSON
2. ✅ Validate JSON structure
3. ✅ Test component XML generation
4. ✅ Verify xmlJsonPathTable conversion

### Short-term
1. ⏳ Fix `enhanced_json_to_iflow_converter.py` (currently empty)
2. ⏳ Generate complete iFlow ZIP package
3. ⏳ Validate ZIP structure and contents

### Long-term
1. ⏳ Import to SAP Integration Suite
2. ⏳ Execute runtime test
3. ⏳ Verify JSON conversion output
4. ⏳ Document any SAP IS-specific requirements

---

## Summary

✅ **Component Template** - Working correctly with dynamic property generation

✅ **xmlJsonPathTable Conversion** - Array → HTML-encoded table conversion validated

✅ **Test Metadata** - Complete test file created with all new properties

✅ **Validation** - All component-level tests passing

⏳ **Full Integration** - Pending converter fix for complete ZIP generation

---

**Last Updated:** 2025-11-04
**Test Status:** Component-level validation complete, full integration pending
