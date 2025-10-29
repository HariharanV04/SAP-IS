# Sterling B2B XML Processor

## 📋 Overview

This processor extracts integration logic from Sterling B2B files (BPML and MXL) and generates structured JSON + Markdown outputs. **It follows the exact same structure as BoomiXMLProcessor** for consistency.

## 🚀 Quick Start

```bash
cd SterlingToIS-API

# Process all files
python sterling_xml_processor.py

# Clean old outputs first
python sterling_xml_processor.py --clean

# Custom directories
python sterling_xml_processor.py --source my-samples --output my-outputs
```

## 📁 Output Structure

After running, you'll get:

```
sterling_parsed_outputs/
├── combined_documentation.md          # All 76 files in one document
├── all_components.json                # All components in structured JSON
├── summary_report.txt                 # Statistics and overview
│
├── individual_markdown/               # One MD per file
│   ├── bpml/
│   │   ├── business-process/
│   │   │   ├── ftp-get-multiple-files.md
│   │   │   └── ... (72 files)
│   │   ├── apis/
│   │   └── filegateway-scenarios/
│   └── mxl/
│       └── map-editor/
│           └── ... (4 files)
│
└── json/                              # One JSON per file
    ├── bpml/
    │   └── ... (72 JSON files)
    └── mxl/
        └── ... (4 JSON files)
```

## 🔍 Component JSON Structure

### BPML Components (Business Processes)

```json
{
  "id": "ftp-get-multiple-files",
  "name": "Demo_BP_FTPGetMultipleFiles",
  "type": "sterling.process",
  "subtype": "bpml",
  "description": "Sterling B2B Business Process: Demo_BP_FTPGetMultipleFiles",
  "file_path": "...",
  "rules": [
    {
      "name": "FileCounter",
      "condition": "/ProcessData/FileCounter/text()>0",
      "type": "business_rule"
    }
  ],
  "operations": [
    {
      "name": "AssignService",
      "participant": "AssignService",
      "type": "content_modifier",
      "config": {
        "REMOTE_HOST": "localhost",
        "REMOTE_PORT": "21",
        "REMOTE_USER": "sistema_ftp",
        "REMOTE_DIRECTORY": "/home/sistema_ftp",
        "REMOTE_FILENAME": "*.txt"
      }
    },
    {
      "name": "FTP Client Begin Session Service",
      "participant": "FTPClientBeginSession",
      "type": "ftp_adapter",
      "config": {
        "RemoteHost": {"from": "//REMOTE_HOST/text()"},
        "RemotePort": {"from": "//REMOTE_PORT/text()"}
      }
    }
  ],
  "assignments": [],
  "sequences": [],
  "patterns": [
    "ftp_file_transfer",
    "batch_processing",
    "conditional_logic"
  ],
  "raw_content": "<?xml version=\"1.0\"?>..."
}
```

### MXL Components (Data Maps)

```json
{
  "id": "MapPos2CsvSample01",
  "name": "MapPos2CsvSample01",
  "type": "sterling.map",
  "subtype": "mxl",
  "description": "Test",
  "author": "Administrator",
  "file_path": "...",
  "mappings": [
    {
      "from_key": "22",
      "from_field": "NAME1",
      "from_type": "field",
      "to_key": "17",
      "to_field": "FULL_NAME",
      "to_type": "string",
      "mapping_type": "direct"
    },
    {
      "from_key": "explicit_rule",
      "from_type": "transformation",
      "to_key": "17",
      "to_field": "FULL_NAME",
      "to_type": "string",
      "mapping_type": "transformation",
      "transformation": "#FULL_NAME = #NAME1 + \" \" + #NAME2 ;"
    }
  ],
  "functions": [
    {
      "name": "Transform_FULL_NAME",
      "type": "transformation",
      "category": "explicit_rule",
      "target_field": "FULL_NAME",
      "expression": "#FULL_NAME = #NAME1 + \" \" + #NAME2 ;",
      "language": "sterling_rule"
    }
  ],
  "input_fields": [
    {
      "id": "22",
      "name": "NAME1",
      "type": "string",
      "length": "7",
      "start_pos": "3",
      "format": "X",
      "direction": "input"
    }
  ],
  "output_fields": [
    {
      "id": "17",
      "name": "FULL_NAME",
      "type": "string",
      "format": "X",
      "direction": "output"
    }
  ],
  "raw_content": "<?xml version=\"1.0\"?>..."
}
```

## 📊 Operation Types (Sterling → SAP Mapping)

The processor automatically maps Sterling services to SAP Integration Suite component types:

| Sterling Service | Operation Type | SAP Component |
|-----------------|---------------|---------------|
| FTPClient* | `ftp_adapter` | FTP Adapter |
| SFTPClient* | `sftp_adapter` | SFTP Adapter |
| RESTAPIClient | `rest_adapter` | REST Adapter |
| HTTPClient | `http_adapter` | HTTP Adapter |
| HttpRespond | `http_adapter` | HTTP Response |
| MailboxAdd/Get | `message_queue` | JMS/Queue |
| Translation | `message_mapping` | Message Mapping |
| XAPIService | `soap_adapter` | SOAP Adapter |
| AssignService | `content_modifier` | Content Modifier |
| xmljsontransformer | `json_xml_converter` | JSON/XML Converter |

## ✅ Validation Checklist

### 1. Quick Validation (`combined_documentation.md`)
- ✅ Open and search for specific processes
- ✅ Check if FTP hosts, ports, paths are captured
- ✅ Verify operations are listed with actual values
- ✅ Confirm patterns are identified

### 2. Component Structure (`all_components.json`)
- ✅ Open in JSON editor
- ✅ Verify `components[]` array exists
- ✅ Check each component has: `id`, `name`, `type`, `subtype`
- ✅ For BPML: verify `operations[]` array with `config` objects
- ✅ For MXL: verify `mappings[]` and `functions[]` arrays

### 3. Individual Files (`json/bpml/` and `json/mxl/`)
- ✅ Pick a BPML file you know well
- ✅ Open its JSON counterpart
- ✅ Verify all operations are captured
- ✅ Check all assignment values are present
- ✅ Confirm config objects have actual values (not placeholders)

### 4. Field Mappings (`json/mxl/`)
- ✅ Open an MXL JSON file
- ✅ Check `mappings[]` array
- ✅ Verify `from_field` and `to_field` have actual names
- ✅ Check `transformation` field has actual expressions
- ✅ Verify `functions[]` array has transformation details

### 5. Summary Report (`summary_report.txt`)
- ✅ Verify counts: 72 BPML + 4 MXL = 76 total
- ✅ Check success rate (should be 100%)
- ✅ Review integration patterns found

## 🎯 Key Fields to Validate

### BPML Files - Check These:
```json
{
  "operations": [
    {
      "config": {
        "REMOTE_HOST": "localhost",        // ✅ Actual value
        "REMOTE_PORT": "21",               // ✅ Actual value
        "REMOTE_USER": "sistema_ftp",      // ✅ Actual value
        "REMOTE_DIRECTORY": "/home/..."    // ✅ Actual path
      }
    }
  ]
}
```

### MXL Files - Check These:
```json
{
  "mappings": [
    {
      "from_field": "NAME1",               // ✅ Actual field name
      "to_field": "FULL_NAME",             // ✅ Actual field name
      "transformation": "#FULL_NAME = ..." // ✅ Actual expression
    }
  ],
  "input_fields": [
    {
      "name": "NAME1",                     // ✅ Actual name
      "type": "string",                    // ✅ Actual type
      "length": "7",                       // ✅ Actual length
      "start_pos": "3"                     // ✅ Actual position
    }
  ]
}
```



## 📝 Files Generated

After processing 76 files, you get:

- **1** combined markdown (all files)
- **1** all_components.json (structured data)
- **1** summary report
- **76** individual markdown files
- **76** individual JSON files
- **Total: 155 output files**

## 🎉 Success Indicators

✅ **100% success rate** in summary_report.txt
✅ **All 76 files** listed in combined_documentation.md
✅ **Actual values** in JSON files (no "placeholder" or "dummy")
✅ **Complete config objects** in operations
✅ **Field mappings with real names** in MXL files
✅ **Transformation expressions** captured in functions

## 🚨 Common Issues

### Issue: Config objects are empty
**Fix:** Check if BPML has `<output>` message with `<assign>` elements

### Issue: Mappings array is empty
**Fix:** Check if MXL has `<Link>` or `<ExplicitRule>` elements

### Issue: Operation type is "unknown"
**Fix:** Check participant name mapping in `_identify_operation_type()`

## 📞 Next Steps

After validating the outputs:

1. ✅ Review `all_components.json` structure
2. ✅ Spot-check individual JSON files for completeness
3. ✅ Verify actual values (not placeholders) in config objects
4. ✅ Confirm field mappings have real field names
5. ✅ Check transformation expressions are captured

Once validated, this can be integrated with the Flask API for iFlow generation!





