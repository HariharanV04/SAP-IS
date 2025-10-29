# Demo_BP_RouteViaCustomSFTP

**Type**: sterling.process
**File**: route-via-custom-sftp.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaCustomSFTP

## Integration Patterns

- Conditional Logic

## Business Rules

### changeDirectory?
- **Condition**: ``

## Operations

### 1. SFTP BEGIN SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SFTPClientAdapter`: {'from': '/ProcessData/customsftp_SFTPClientAdapter/text()'}
  - `ProfileId`: {'from': '/ProcessData/customsftp_ProfileId/text()'}
  - `.`: {'from': '*'}

### 2. changeDir
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/SftpBeginSessionServiceResults/SessionToken/text()'}
  - `Directory`: {'from': '/ProcessData/SftpBeginSessionServiceResults/TPProfile/Directory/text()'}

### 3. SFTP PUT SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': 'SftpBeginSessionServiceResults/SessionToken/text()'}
  - `RemoteFileName`: {'from': 'DestinationMessageName/text()'}
  - `.`: {'from': '*'}

### 4. SFTP END SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': 'SftpBeginSessionServiceResults/SessionToken/text()'}

### 5. SFTP END SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': 'SftpBeginSessionServiceResults/SessionToken/text()'}
  - `.`: {'from': 'ResponseTimeout'}

### 6. generateException
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `exceptionCode`: Error, SFTP PUT
  - `.`: {'from': '*'}

