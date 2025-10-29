# HelloWorldXML

**Type**: sterling.process
**File**: hello-world-xml.bpml

## Description

Sterling B2B Business Process: HelloWorldXML

## Operations

### 1. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/ResponseData
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: HelloWorldXML
  - `.`: {'from': '*'}

### 2. SetContenType
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `DocumentContentType`: application
  - `DocumentContentSubType`: xml
  - `updateMetaDataOnly`: true

### 3. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}

