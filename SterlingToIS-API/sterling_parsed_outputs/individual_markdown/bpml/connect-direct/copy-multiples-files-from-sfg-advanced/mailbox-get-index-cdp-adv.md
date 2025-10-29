# MAILBOX_GET_INDEX_CDP_ADV

**Type**: sterling.process
**File**: mailbox-get-index-cdp-adv.bpml

## Description

Sterling B2B Business Process: MAILBOX_GET_INDEX_CDP_ADV

## Integration Patterns

- Conditional Logic

## Business Rules

### os_windows
- **Condition**: ``

### os_unix
- **Condition**: ``

### os_other
- **Condition**: ``

### has_filter
- **Condition**: ``

### has_mailboxpath
- **Condition**: ``

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `This/SlashType`: \
  - `This/Dummy`: /* Dummy Comment */
  - `This/MailboxPath`: /Inbox
  - `This/MessageNamePattern`: *

### 2. Mailbox Query Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: {'from': 'This/MailboxPath/text()'}
  - `MessageExtractable`: YES
  - `MessageNamePattern`: {'from': 'This/MessageNamePattern/text()'}
  - `OrderBy`: MessageId

### 3. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/This
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: PullListCdpAdv
  - `.`: {'from': '*'}

### 4. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 5. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

