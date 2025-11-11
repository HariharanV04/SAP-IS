# Filter Component Creation Guide

Complete documentation for creating Filter components in SAP Integration Suite iFlow based on the enhanced component generation system.

## Table of Contents

1. [Overview](#overview)
2. [Component Detection Logic](#component-detection-logic)
3. [Creation Flow](#creation-flow)
4. [Template Method](#template-method)
5. [Property Generation Logic](#property-generation-logic)
6. [Filter Component Properties](#filter-component-properties)
7. [Sample Configurations](#sample-configurations)
8. [XPath Expression Handling](#xpath-expression-handling)
9. [Generated XML Structure](#generated-xml-structure)
10. [Best Practices](#best-practices)

---

## Overview

The Filter component is used to filter messages based on XPath expressions, JavaScript, or Groovy expressions. It evaluates conditions and determines whether to continue processing the message.

**SAP Activity Type**: `Filter`  
**BPMN Element**: `bpmn2:callActivity`  
**Component Version**: `1.0` (default) or `1.1`

---

## Component Detection Logic

### Entry Point

When processing components in the JSON blueprint, the converter checks the `type` field:

**File**: `enhanced_component_generation/enhanced_json_to_iflow_converter.py`

```python
# Line 500-501
elif component_type == "filter":
    return self._create_filter(component_id, component_name, config, position, incoming_flows, outgoing_flows)
```

**Trigger**: Component with `"type": "filter"` in the JSON metadata

---

## Creation Flow

### Step 1: Component Detection

The converter processes each component in the endpoint's `components` array:

```python
# In _process_endpoint_components()
for component in components:
    component_type = component.get("type", "")
    if component_type == "filter":
        # Call filter creation method
```

### Step 2: Filter Creation Method

**File**: `enhanced_component_generation/enhanced_json_to_iflow_converter.py`  
**Method**: `_create_filter()` (Lines 658-685)

```python
def _create_filter(self, id: str, name: str, config: Dict[str, Any], position: Dict[str, int],
                   incoming_flows: Optional[List[str]] = None,
                   outgoing_flows: Optional[List[str]] = None) -> str:
    """
    Create a filter component using the enhanced template.
    
    This method uses the EnhancedComponentTemplates.filter_template()
    which supports dynamic property generation including xpathType and wrapContent.
    
    Args:
        id: Component ID
        name: Component name
        config: Configuration dictionary with all filter properties
        position: Position dict (not used by template but kept for consistency)
        incoming_flows: List of incoming sequence flow IDs
        outgoing_flows: List of outgoing sequence flow IDs
    
    Returns:
        Generated BPMN XML for the filter component
    """
    return self.templates.filter_template(
        id=id,
        name=name,
        config=config,
        incoming_flows=incoming_flows,
        outgoing_flows=outgoing_flows
    )
```

**Key Points**:
- Extracts `id`, `name`, and `config` from component JSON
- Retrieves `incoming_flows` and `outgoing_flows` from flow references
- Delegates to the template system for XML generation

### Step 3: Template Method

**File**: `enhanced_component_generation/enhanced_component_templates.py`  
**Method**: `filter_template()` (Lines 1693-1695)

```python
def filter_template(self, id: str, name: str, config: Dict[str, Any], 
                   incoming_flows: Optional[List[str]] = None, 
                   outgoing_flows: Optional[List[str]] = None):
    """Template for Filter component"""
    return self.generic_component_template(id, name, "Filter", config, 
                                         incoming_flows=incoming_flows, 
                                         outgoing_flows=outgoing_flows)
```

**Key Points**:
- Uses `generic_component_template()` with `sap_activity_type="Filter"`
- All filter-specific logic is handled by the generic template
- Properties are dynamically generated from the config dictionary

### Step 4: Generic Component Template

**File**: `enhanced_component_generation/enhanced_component_templates.py`  
**Method**: `generic_component_template()` (Lines 947-1017)

This method:
1. Generates required properties (componentVersion, activityType, cmdVariantUri)
2. Generates all other properties from config using `_generate_property_xml()`
3. Creates incoming/outgoing flow references
4. Wraps everything in BPMN2 XML structure

**Required Properties** (auto-generated if not in config):
- `componentVersion`: Defaults to `"1.0"` or from config
- `activityType`: Defaults to `"Filter"` or from config
- `cmdVariantUri`: Auto-generated as `"ctype::FlowstepVariant/cname::Filter/version::{componentVersion}"`

**BPMN Element**: Creates `<bpmn2:callActivity>` element

---

## Property Generation Logic

### Dynamic Property Generation

**File**: `enhanced_component_generation/enhanced_component_templates.py`  
**Method**: `_generate_property_xml()` (Lines 135-230)

This method processes all properties from the config dictionary:

1. **Flattening Nested Objects**: Nested dictionaries are flattened using key mappings
2. **Array Handling**: Arrays are converted to comma-separated strings or XML tables
3. **Value Formatting**: All values are XML-escaped via `_escape_xml()`
4. **Empty Value Handling**: Empty values are skipped (unless `skip_empty=False`)

### XML Escaping

**File**: `enhanced_component_generation/enhanced_component_templates.py`  
**Method**: `_escape_xml()` (Lines 28-34)

```python
def _escape_xml(self, value: Any) -> str:
    """Escape XML special characters in property values"""
    if value is None:
        return ""
    value_str = str(value)
    # Escape XML entities
    return xml.sax.saxutils.escape(value_str, {"'": "&apos;", '"': "&quot;"})
```

**Escaped Characters**: `&`, `<`, `>`, `'`, `"`

### Property Value Formatting

**File**: `enhanced_component_generation/enhanced_component_templates.py`  
**Method**: `_format_property_value()` (Lines 36-45)

```python
def _format_property_value(self, value: Any) -> str:
    """Format property value for XML - handle empty values"""
    if value is None:
        return ""
    if isinstance(value, str):
        if not value or value == "<placeholder>" or value.startswith("<") and value.endswith(">"):
            return ""
        return self._escape_xml(value)
    # Convert non-string types to string
    return self._escape_xml(str(value))
```

**Key Points**:
- None values → empty string
- Placeholder values → skipped
- All other values → XML-escaped strings

---

## Filter Component Properties

### Required Properties (Auto-Generated)

These properties are automatically generated if not provided in the config:

| Property | Default Value | Description |
|----------|--------------|-------------|
| `componentVersion` | `"1.0"` | Component version number |
| `activityType` | `"Filter"` | SAP activity type |
| `cmdVariantUri` | `"ctype::FlowstepVariant/cname::Filter/version::1.0"` | Command variant URI |

### Optional Properties (From Config)

All properties below are optional and can be included in the `config` dictionary:

#### Expression Properties

| Property | Type | Description | Example Values |
|----------|------|-------------|----------------|
| `expressionType` | string | Type of expression language | `"XPath"`, `"JavaScript"`, `"Groovy"` |
| `expression` | string | The filter expression to evaluate | `"/root/status = 'active'"` |
| `valueType` | string | Expected return type of expression | `"boolean"`, `"string"`, `"integer"`, `"node"`, `"nodelist"` |
| `xpathType` | string | XPath type (for XPath expressions) | `"Integer"`, `"String"`, `"Boolean"` |
| `wrapContent` | string | XPath expression for content wrapping/filtering | `"//Customers[Status = '${property.CustomerStatus}']"` |

#### Configuration Properties

| Property | Type | Description | Example Values |
|----------|------|-------------|----------------|
| `description` | string | Human-readable description | `"Filter active records only"` |
| `throwExceptionOnFail` | string | Throw exception if filter fails | `"true"`, `"false"` |
| `enabled` | string | Whether component is enabled | `"true"`, `"false"` |
| `namespaceContext` | string | XML namespace context for XPath expressions | `""` (empty) or namespace mapping |
| `logEvaluation` | string | Log expression evaluation | `"true"`, `"false"` |

### Property Metadata Reference

**File**: `metadata_template/components.json` (Lines 792-809)

```json
{
  "<filter_step_id>": {
    "type": "filter",
    "id": "<filter_step_id>",
    "name": "<filter_step_name>",
    "sap_activity_type": "Filter",
    "config": {
      "componentVersion": "1.0",
      "cmdVariantUri": "ctype::FlowstepVariant/cname::Filter/version::1.0",
      "expressionType": "<XPath|JavaScript|Groovy>",
      "expression": "<expression_content>",
      "valueType": "<boolean|string|integer|node|nodelist>",
      "description": "<description_text>",
      "throwExceptionOnFail": "<true|false>",
      "enabled": "<true|false>",
      "namespaceContext": "<xml_namespace_context>",
      "logEvaluation": "<true|false>"
    }
  }
}
```

---

## Sample Configurations

### Sample 1: XPath Filter with Property Reference

**Source**: `sample_metadata_jsons/sample_filter_flow.json` (Lines 51-63)

```json
{
  "type": "filter",
  "id": "filter_001",
  "name": "Filter_1",
  "sap_activity_type": "Filter",
  "config": {
    "xpathType": "Integer",
    "wrapContent": "//Customers[Status = '${property.CustomerStatus}']",
    "componentVersion": "1.1",
    "activityType": "Filter",
    "cmdVariantUri": "ctype::FlowstepVariant/cname::Filter/version::1.1.0"
  }
}
```

**Use Case**: Filter XML content using XPath expression with property reference

### Sample 2: Complete Filter Configuration

**Source**: `sample_metadata_jsons/test_4_components.json` (Lines 73-90)

```json
{
  "type": "filter",
  "id": "filter_001",
  "name": "Filter Component - XPath Expression",
  "sap_activity_type": "Filter",
  "config": {
    "componentVersion": "1.0",
    "cmdVariantUri": "ctype::FlowstepVariant/cname::Filter/version::1.0",
    "expressionType": "XPath",
    "expression": "/root/status = 'active'",
    "valueType": "boolean",
    "description": "Filter active records only",
    "throwExceptionOnFail": "true",
    "enabled": "true",
    "namespaceContext": "",
    "logEvaluation": "true"
  }
}
```

**Use Case**: Full filter configuration with all properties

### Sample 3: Minimal Filter Configuration

```json
{
  "type": "filter",
  "id": "filter_001",
  "name": "Simple Filter",
  "config": {
    "expression": "/root/status = 'active'",
    "expressionType": "XPath"
  }
}
```

**Use Case**: Minimal configuration - required properties auto-generated

---

## XPath Expression Handling

### How XPath Expressions Are Processed

Filter component XPath expressions are handled as **regular string properties** with standard XML escaping:

1. **No Special Parsing**: XPath expressions are NOT parsed or validated
2. **Standard Escaping**: XML special characters are escaped (`&`, `<`, `>`, `'`, `"`)
3. **No CDATA Wrapping**: XPath expressions are NOT wrapped in CDATA (unlike script content)
4. **Property Reference Support**: Property references like `${property.CustomerStatus}` are preserved

### XPath Expression Examples

#### Example 1: Simple XPath Expression

```json
{
  "expression": "/root/status = 'active'",
  "expressionType": "XPath"
}
```

**Generated XML**:
```xml
<ifl:property>
    <key>expression</key>
    <value>/root/status = 'active'</value>
</ifl:property>
```

#### Example 2: XPath with Property Reference

```json
{
  "wrapContent": "//Customers[Status = '${property.CustomerStatus}']",
  "xpathType": "Integer"
}
```

**Generated XML**:
```xml
<ifl:property>
    <key>wrapContent</key>
    <value>//Customers[Status = '${property.CustomerStatus}']</value>
</ifl:property>
<ifl:property>
    <key>xpathType</key>
    <value>Integer</value>
</ifl:property>
```

#### Example 3: Complex XPath Expression

```json
{
  "expression": "/root/customers/customer[@status='active' and @type='premium']",
  "expressionType": "XPath",
  "namespaceContext": "ns1=http://example.com/ns1;ns2=http://example.com/ns2"
}
```

**Generated XML**:
```xml
<ifl:property>
    <key>expression</key>
    <value>/root/customers/customer[@status='active' and @type='premium']</value>
</ifl:property>
<ifl:property>
    <key>expressionType</key>
    <value>XPath</value>
</ifl:property>
<ifl:property>
    <key>namespaceContext</key>
    <value>ns1=http://example.com/ns1;ns2=http://example.com/ns2</value>
</ifl:property>
```

### Special Handling for namespaceContext

The `namespaceContext` property is allowed to be empty (not skipped), even when `skip_empty=True`:

```python
# In _generate_property_xml(), line 185
if value == "" and key not in ["namespaceContext", "bodyNamespaceMapping"]:
    continue
```

This allows explicit empty namespace context to be included in the generated XML.

---

## Generated XML Structure

### Complete Filter Component XML

A filter component generates the following BPMN2 XML structure:

```xml
<bpmn2:callActivity id="filter_001" name="Filter_1">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Filter</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Filter/version::1.0</value>
        </ifl:property>
        <!-- All other properties from config -->
        <ifl:property>
            <key>expressionType</key>
            <value>XPath</value>
        </ifl:property>
        <ifl:property>
            <key>expression</key>
            <value>/root/status = 'active'</value>
        </ifl:property>
        <!-- ... more properties ... -->
    </bpmn2:extensionElements>
    <!-- Incoming flows -->
    <bpmn2:incoming>flow_001</bpmn2:incoming>
    <!-- Outgoing flows -->
    <bpmn2:outgoing>flow_002</bpmn2:outgoing>
</bpmn2:callActivity>
```

### Flow References

Flow references are automatically generated based on sequence flows defined in the JSON:

- **Incoming flows**: Sequence flows where this component is the target
- **Outgoing flows**: Sequence flows where this component is the source

**Flow Reference Generation**:
- File: `enhanced_component_generation/enhanced_json_to_iflow_converter.py`
- Method: `_add_flow_references_to_components()` (Lines 1061-1086)

---

## Best Practices

### 1. Always Include Required Properties Explicitly

While required properties are auto-generated, it's best practice to include them explicitly:

```json
{
  "config": {
    "componentVersion": "1.0",
    "activityType": "Filter",
    "cmdVariantUri": "ctype::FlowstepVariant/cname::Filter/version::1.0",
    "expression": "...",
    "expressionType": "XPath"
  }
}
```

### 2. Use Descriptive Names and Descriptions

```json
{
  "name": "Filter Active Customers",
  "config": {
    "description": "Filter customers with status='active' and type='premium'",
    "expression": "/root/customers/customer[@status='active' and @type='premium']"
  }
}
```

### 3. Enable Logging for Debugging

```json
{
  "config": {
    "logEvaluation": "true",
    "description": "Filter description for troubleshooting"
  }
}
```

### 4. Handle Exceptions Appropriately

```json
{
  "config": {
    "throwExceptionOnFail": "true",  // or "false" for graceful failure
    "enabled": "true"
  }
}
```

### 5. Use Namespace Context for Complex XML

```json
{
  "config": {
    "expressionType": "XPath",
    "namespaceContext": "ns1=http://example.com/ns1;ns2=http://example.com/ns2",
    "expression": "/ns1:root/ns2:customers/ns1:customer"
  }
}
```

### 6. Property Reference in XPath Expressions

Use property references for dynamic filtering:

```json
{
  "config": {
    "wrapContent": "//Customers[Status = '${property.CustomerStatus}']",
    "expressionType": "XPath"
  }
}
```

### 7. Validate Expression Types

Ensure `expressionType` matches the `expression` syntax:
- `"XPath"` → XPath 2.0 expressions
- `"JavaScript"` → JavaScript expressions
- `"Groovy"` → Groovy script expressions

---

## Code Reference Summary

### Key Files

1. **Converter**: `enhanced_component_generation/enhanced_json_to_iflow_converter.py`
   - Line 500-501: Component type detection
   - Line 658-685: `_create_filter()` method

2. **Templates**: `enhanced_component_generation/enhanced_component_templates.py`
   - Line 1693-1695: `filter_template()` method
   - Line 947-1017: `generic_component_template()` method
   - Line 135-230: `_generate_property_xml()` method
   - Line 28-34: `_escape_xml()` method
   - Line 36-45: `_format_property_value()` method

3. **Metadata**: `metadata_template/components.json`
   - Line 792-809: Filter component metadata template

4. **Samples**: 
   - `sample_metadata_jsons/sample_filter_flow.json` (Lines 51-63)
   - `sample_metadata_jsons/test_4_components.json` (Lines 73-90)

---

## Common Issues and Solutions

### Issue 1: Expression Not Evaluating

**Problem**: Filter expression not working as expected

**Solution**: 
- Verify `expressionType` matches expression syntax
- Check `namespaceContext` if using namespaced XML
- Enable `logEvaluation: "true"` for debugging

### Issue 2: Property References Not Resolved

**Problem**: `${property.PropertyName}` not resolving

**Solution**:
- Ensure property is set in a previous component (e.g., Content Modifier)
- Verify property name spelling matches exactly
- Check property scope (message properties vs exchange properties)

### Issue 3: Empty namespaceContext

**Problem**: Empty namespace context causing XPath failures

**Solution**:
- Include explicit `namespaceContext: ""` if no namespaces needed
- Or provide proper namespace mapping: `"ns1=http://example.com/ns1"`

---

## Conclusion

The Filter component creation follows a straightforward flow:

1. **Detection**: Component with `"type": "filter"` triggers filter creation
2. **Template**: Uses `filter_template()` → `generic_component_template()` with `"Filter"` activity type
3. **Properties**: All properties dynamically generated from config dictionary
4. **XML Generation**: Creates `<bpmn2:callActivity>` with extension elements containing all properties
5. **Flow References**: Incoming/outgoing flows automatically added based on sequence flows

The system is designed to be flexible - any property in the config is automatically converted to `<ifl:property>` elements, making it easy to add new filter properties without code changes.

