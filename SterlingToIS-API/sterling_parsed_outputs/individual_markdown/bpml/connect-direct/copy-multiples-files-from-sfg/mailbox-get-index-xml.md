# MAILBOX_GET_INDEX_XML

**Type**: sterling.process
**File**: mailbox-get-index-xml.bpml

## Description

Sterling B2B Business Process: MAILBOX_GET_INDEX_XML

## Operations

### 1. Mailbox Query Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: /Inbox
  - `MessageExtractable`: YES
  - `MessageNamePattern`: *
  - `OrderBy`: MessageId

### 2. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

