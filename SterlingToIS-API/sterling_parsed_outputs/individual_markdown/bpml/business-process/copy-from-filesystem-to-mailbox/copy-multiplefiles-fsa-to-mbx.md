# Demo_BP_CopyMultipleFilesFromFSA2MBX

**Type**: sterling.process
**File**: copy-multiplefiles-fsa-to-mbx.bpml

## Description

Sterling B2B Business Process: Demo_BP_CopyMultipleFilesFromFSA2MBX

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### more_docs
- **Condition**: ``

## Operations

### 1. File System Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `Action`: FS_COLLECT
  - `collectionFolder`: C:\Temp\
  - `collectMultiple`: true
  - `deleteAfterCollect`: false
  - `filter`: *.txt
  - `noFilesSetSuccess`: true

### 2. For Each Document
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `DOCUMENT_KEY_PREFIX`: FSA_Document
  - `ITERATOR_NAME`: FSADoc

### 3. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: /Inbox

