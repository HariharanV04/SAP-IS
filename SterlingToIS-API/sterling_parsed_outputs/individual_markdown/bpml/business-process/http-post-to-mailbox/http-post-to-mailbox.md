# HttpPostToMailbox

**Type**: sterling.process
**File**: http-post-to-mailbox.bpml

## Description

Sterling B2B Business Process: HttpPostToMailbox

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `MAILBOX_PATH`: /Sistema_ftp/Inbox

### 2. set user token
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `USER_TOKEN`: admin
  - `.`: {'from': '*'}

### 3. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `Extractable`: Yes
  - `DocumentId`: {'from': '/PrimaryDocument/@SCIObjectID'}
  - `MailboxPath`: {'from': '//MAILBOX_PATH/text()'}

### 4. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}

