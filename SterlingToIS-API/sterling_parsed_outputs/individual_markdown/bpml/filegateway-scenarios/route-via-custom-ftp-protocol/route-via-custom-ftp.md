# Demo_BP_RouteViaCustomFTP

**Type**: sterling.process
**File**: route-via-custom-ftp.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaCustomFTP

## Integration Patterns

- Conditional Logic

## Business Rules

### renameFile?
- **Condition**: ``

### changeDirectory?
- **Condition**: ``

## Operations

### 1. Obscure Password
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 2. FTP BEGIN SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `FTPClientAdapter`: FTPClientAdapter
  - `RemoteHost`: {'from': '/ProcessData/customftp_RemoteHost/text()'}
  - `RemotePort`: {'from': '/ProcessData/customftp_RemotePort/text()'}
  - `RemoteUserId`: {'from': '/ProcessData/customftp_RemoteUserId/text()'}
  - `RemotePasswd`: {'from': 'revealObscured(/ProcessData/Demo_Remote_FTP)'}
  - `UsingRevealedPasswd`: true
  - `ConnectionRetries`: {'from': '/ProcessData/customftp_NoOfRetries/text()'}
  - `RetryDelay`: {'from': '/ProcessData/customftp_RetriesInterval/text()'}
  - `ResponseTimeout`: {'from': '/ProcessData/ResponseTimeout/text()'}
  - `ClearControlChannel`: {'from': '/ProcessData/ClearControlChannel/text()'}
  - `.`: {'from': '*'}

### 3. changeDir
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}
  - `Directory`: {'from': '/ProcessData/FtpBeginSessionServiceResults/TPProfile/Directory/text()'}

### 4. FTP PUT SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RepresentationType`: BINARY
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}
  - `.`: {'from': '*'}

### 5. moveFile
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RemoteFromFileName`: {'from': 'string(RemoteFileName)'}
  - `RemoteToFileName`: {'from': 'substring-after(string(RemoteFileName),string(TempPrefix))'}
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}

### 6. FTP END SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}

### 7. FTP END SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}

### 8. generateException
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `exceptionCode`: Error, FTP PUT
  - `.`: {'from': '*'}

