# MAILBOX_DELETE_FILE_RUNTASK

**Type**: sterling.process
**File**: mailbox-delete-file-runtask.bpml

## Description

Sterling B2B Business Process: MAILBOX_DELETE_FILE_RUNTASK

## Integration Patterns

- Conditional Logic

## Business Rules

### DelMsgCntGreaterZero
- **Condition**: ``

### has_mailboxpath
- **Condition**: ``

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `This/ReturnCode`: 0
  - `This/MailboxPath`: /Inbox

### 2. Mailbox Delete Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: {'from': 'string(/ProcessData/This/MailboxPath)'}
  - `MessageNamePattern`: {'from': 'string(/ProcessData/This/MessageNamePattern)'}
  - `MailboxSelection`: choose
  - `MessageExtractable`: ALL

### 3. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 4. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

