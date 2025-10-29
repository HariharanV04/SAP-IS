# MAILBOX_GET_INDEX_CDP

**Type**: sterling.process
**File**: mailbox-get-index-cdp.bpml

## Description

Sterling B2B Business Process: MAILBOX_GET_INDEX_CDP

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

### 2. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/PullList
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: PullListCDP
  - `.`: {'from': '*'}

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

