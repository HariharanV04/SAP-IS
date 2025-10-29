# SFGAdvancedSearchWeb

**Type**: sterling.process
**File**: sfg-advanced-search-web.bpml

## Description

Sterling B2B Business Process: SFGAdvancedSearchWeb

## Integration Patterns

- Conditional Logic

## Business Rules

### partner_name
- **Condition**: ``

### partner_code
- **Condition**: ``

### login_id
- **Condition**: ``

### first_name
- **Condition**: ``

### last_name
- **Condition**: ``

### first_name_last_name
- **Condition**: ``

### no_parameters
- **Condition**: ``

### is_new_page
- **Condition**: ``

### has_results
- **Condition**: ``

## Operations

### 1. Lightweight JDBC Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `pool`: db2Pool
  - `query_type`: SELECT
  - `result_name`: Result1
  - `row_name`: Row1
  - `sql`: {'from': '/ProcessData/This/sql/text()'}

### 2. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/ResponseData
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: SFGAdvancedSearch
  - `.`: {'from': '*'}

### 3. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}

