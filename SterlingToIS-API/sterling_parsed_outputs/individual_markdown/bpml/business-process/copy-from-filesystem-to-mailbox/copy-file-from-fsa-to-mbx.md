# Demo_BP_CopyFileFromFSA2MBX

**Type**: sterling.process
**File**: copy-file-from-fsa-to-mbx.bpml

## Description

Sterling B2B Business Process: Demo_BP_CopyFileFromFSA2MBX

## Operations

### 1. File System Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `Action`: FS_COLLECT
  - `collectionFolder`: C:\Temp\
  - `collectMultiple`: false
  - `deleteAfterCollect`: false
  - `filter`: *.txt

### 2. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: {'from': '/Inbox'}

