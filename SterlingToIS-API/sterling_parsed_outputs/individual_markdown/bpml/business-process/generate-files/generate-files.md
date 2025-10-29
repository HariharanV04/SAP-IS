# GenerateFiles

**Type**: sterling.process
**File**: generate-files.bpml

## Description

Sterling B2B Business Process: GenerateFiles

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### This/FileCounter
- **Condition**: ``

## Operations

### 1. Get_Current_Time
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `action`: {'from': "'current_time'"}
  - `format`: 'D'yyyyMMdd.'S'HHmm

### 2. Document Keyword Replace
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `literal_bufferSize`: 102400
  - `literal_mode`: true
  - `literal_readAheadSize`: 8192
  - `keyword1`: {'from': 'string(\'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\')'}
  - `keywordtype1`: string
  - `replace1`: {'from': "string('')"}
  - `keyword2`: {'from': "string('<ProcessData/>')"}
  - `keywordtype2`: string
  - `replace2`: {'from': "string('')"}
  - `keyword3`: X
  - `keywordtype3`: string
  - `replace3`: {'from': "string('')"}
  - `.`: {'from': '*'}

### 3. Get Document Information Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 4. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: {'from': '/ProcessData/This/MailboxPath'}

