# CodeListEditorWeb

**Type**: sterling.process
**File**: code-list-editor-web.bpml

## Description

Sterling B2B Business Process: CodeListEditorWeb

## Integration Patterns

- Conditional Logic

## Business Rules

### list_name
- **Condition**: ``

### http_method_post
- **Condition**: ``

### http_method_get
- **Condition**: ``

### no_parameters
- **Condition**: ``

### is_new_page
- **Condition**: ``

### search_has_results
- **Condition**: ``

### update_has_results
- **Condition**: ``

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `/ProcessData/ResponseData/searchpage`: Search Page
  - `This/sqlMain`: {'from': 'concat("SELECT * FROM CODELIST_XREF_ITEM WHERE CODELIST_XREF_ITEM.LIST_NAME = \'",/ProcessData/sLN/text(),"\' AND CODELIST_XREF_ITEM.LIST_VERSION = (SELECT DEFAULT_VERSION FROM CODELIST_XREF_VERS WHERE CODELIST_XREF_VERS.LIST_NAME = \'",/ProcessData/sLN/text(),"\')")'}
  - `This/sqlSender`: {'from': 'if (string-length(/ProcessData/sSIt) > 0,concat(" AND SENDER_ITEM like \'%",/ProcessData/sSIt/text(),"%\'"),"")'}
  - `This/sqlReceiver`: {'from': 'if (string-length(/ProcessData/sRIt) > 0,concat(" AND RECEIVER_ITEM like \'%",/ProcessData/sRIt/text(),"%\'"),"")'}
  - `This/sqlSelect`: {'from': 'concat(This/sqlMain,This/sqlSender,This/sqlReceiver)'}

### 2. Lightweight JDBC Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `pool`: {'from': '/ProcessData/This/databasePool/text()'}
  - `query_type`: SELECT
  - `result_name`: Result1
  - `row_name`: Row1
  - `sql`: {'from': '/ProcessData/This/sqlSelect/text()'}

### 3. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `/ProcessData/ResponseData/updatepage`: Update Page
  - `This/P1`: UPDATE CODELIST_XREF_ITEM SET
  - `This/F1`: {'from': 'concat(" SENDER_ITEM = \'",/ProcessData/HttpURLDecodedValues/mSIt/text(),"\',")'}
  - `This/F2`: {'from': 'concat(" RECEIVER_ITEM = \'",/ProcessData/HttpURLDecodedValues/mRIt/text(),"\',")'}
  - `This/F3`: {'from': 'concat(" DESCRIPTION = \'",/ProcessData/HttpURLDecodedValues/mDesc/text(),"\',")'}
  - `This/F4`: {'from': 'concat(" TEXT1 = \'",/ProcessData/HttpURLDecodedValues/mT1/text(),"\',")'}
  - `This/F5`: {'from': 'concat(" TEXT2 = \'",/ProcessData/HttpURLDecodedValues/mT2/text(),"\',")'}
  - `This/F6`: {'from': 'concat(" TEXT3 = \'",/ProcessData/HttpURLDecodedValues/mT3/text(),"\'")'}
  - `This/W1`: {'from': 'concat(" WHERE LIST_NAME = \'",/ProcessData/HttpURLDecodedValues/LN,"\'")'}
  - `This/W2`: {'from': 'concat(" AND LIST_VERSION = \'",/ProcessData/HttpURLDecodedValues/LV,"\'")'}
  - `This/W3`:  AND SENDER_ID IS NULL AND RECEIVER_ID IS NULL
  - `This/W4`: {'from': 'concat(" AND SENDER_ITEM = \'",/ProcessData/HttpURLDecodedValues/SIt,"\'")'}
  - `This/W5`: {'from': 'concat(" AND RECEIVER_ITEM = \'",/ProcessData/HttpURLDecodedValues/RIt,"\'")'}
  - `This/sqlUpdate`: {'from': 'concat(This/P1,This/F1,This/F2,This/F3,This/F4,This/F5,This/F6,This/W1,This/W2,This/W3,This/W4,This/W5)'}

### 4. Lightweight JDBC Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `pool`: {'from': '/ProcessData/This/databasePool/text()'}
  - `query_type`: UPDATE
  - `result_name`: Result1
  - `row_name`: Row1
  - `sql`: {'from': '/ProcessData/This/sqlUpdate/text()'}

### 5. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/ResponseData
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: CodeListEditorWeb
  - `.`: {'from': '*'}

### 6. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}

