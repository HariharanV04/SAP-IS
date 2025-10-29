# Demo_BP_SFTPGetMultipleFiles

**Type**: sterling.process
**File**: sftp-get-multiple-files.bpml

## Description

Sterling B2B Business Process: Demo_BP_SFTPGetMultipleFiles

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### FileCounter
- **Condition**: ``

### DELETE_FILES?
- **Condition**: ``

### MOVE_FILES?
- **Condition**: ``

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SFTP_CLIENT_ADAPTER`: SFTPClientAdapter
  - `SSH_PROFILEID`: 2356001890249e5e3node1
  - `REMOTE_DIRECTORY`: /home/sistema_sftp
  - `REMOTE_FILENAME`: *.txt
  - `MAILBOX_PATH`: /Parceiro_SFTP/Inbox

### 2. SFTP Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `SFTPClientAdapter`: {'from': '//SFTP_CLIENT_ADAPTER/text()'}
  - `ProfileId`: {'from': '/ProcessData/SSH_PROFILEID/text()'}

### 3. SFTP CD SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Directory`: {'from': '//REMOTE_DIRECTORY/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 4. SFTP Client LIST Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '//REMOTE_FILENAME/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 5. SFTP Client GET Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/SFTPClientListResults/Files/File[1]/Name/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 6. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `DocumentId`: {'from': '/ProcessData/DocumentList/DocumentId[1]/text()'}
  - `Extractable`: YES
  - `MailboxPath`: {'from': '//MAILBOX_PATH/text()'}
  - `.`: {'from': '*'}

### 7. SFTP Client MOVE Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/SFTPClientListResults/Files/File[1]/Name/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 8. SFTP Client DELETE Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/SFTPClientListResults/Files/File[1]/Name/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 9. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `TARGET`: /ProcessData/DocumentList/DocumentId[1] | /ProcessData/SFTPClientListResults/Files/File[1] | /ProcessData/MailboxAdd
  - `.`: {'from': '*'}

### 10. SFTP Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

