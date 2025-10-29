# HelloWorldJSON

**Type**: sterling.process
**File**: hello-world-json.bpml

## Description

Sterling B2B Business Process: HelloWorldJSON

## Operations

### 1. XmlJsonTransformer
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Input`: <book><title>The Lord of Rings</title><author>J.R.R. Tolkien</author></book>
  - `InputType`: XML
  - `OutputPath`: output.json
  - `.`: {'from': '*'}

### 2. SetContenType
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `DocumentContentType`: application
  - `DocumentContentSubType`: json
  - `updateMetaDataOnly`: true

### 3. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}

