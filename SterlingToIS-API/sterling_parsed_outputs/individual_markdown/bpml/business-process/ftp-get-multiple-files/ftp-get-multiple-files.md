# Demo_BP_FTPGetMultipleFiles

**Type**: sterling.process
**File**: ftp-get-multiple-files.bpml

## Description

Sterling B2B Business Process: Demo_BP_FTPGetMultipleFiles

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
  - `REMOTE_HOST`: localhost
  - `REMOTE_PORT`: 21
  - `FTP_CLIENT_ADAPTER`: FTPClientAdapter
  - `REMOTE_USER`: sistema_ftp
  - `REMOTE_PASSWORD`: passw0rd
  - `REMOTE_DIRECTORY`: /home/sistema_ftp
  - `REMOTE_FILENAME`: *.txt
  - `MAILBOX_PATH`: /Sistema_ftp/Inbox

### 2. FTP Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RemoteHost`: {'from': '//REMOTE_HOST/text()'}
  - `FTPClientAdapter`: {'from': '//FTP_CLIENT_ADAPTER/text()'}
  - `UsingRevealedPasswd`: True
  - `RemotePasswd`: {'from': '//REMOTE_PASSWORD/text()'}
  - `RemoteUserId`: {'from': '//REMOTE_USER/text()'}
  - `RemotePort`: {'from': '//REMOTE_PORT/text()'}
  - `.`: {'from': '*'}

### 3. FTP CD SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}
  - `Directory`: {'from': '//REMOTE_DIRECTORY/text()'}

### 4. FTP Client LIST Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `NamesOnly`: YES
  - `RemoteFileName`: {'from': '//REMOTE_FILENAME/text()'}
  - `ResponseTimeout`: 60
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}

### 5. FTP Client GET Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RemoteFileName`: {'from': '//ListNames/Name[1]/text()'}
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}
  - `ConnectionType`: PASSIVE

### 6. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Extractable`: YES
  - `MailboxPath`: {'from': '//MAILBOX_PATH/text()'}
  - `MessageName`: {'from': '//ListNames/Name[1]/text()'}
  - `.`: {'from': '*'}

### 7. FTP Client MOVE Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/ListNames/Name[1]/text()'}
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}

### 8. FTP Client DELETE Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/ListNames/Name[1]/text()'}
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}

### 9. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `TARGET`: /ProcessData/PrimaryDocument | /ProcessData/DocumentList/DocumentId[1] | /ProcessData/ListNames/Name[1] | /ProcessData/MailboxAddResults
  - `.`: {'from': '*'}

### 10. FTP Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}
  - `.`: {'from': '*'}

