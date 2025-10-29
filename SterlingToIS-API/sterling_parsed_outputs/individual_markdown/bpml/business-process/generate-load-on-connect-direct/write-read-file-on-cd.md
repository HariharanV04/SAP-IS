# WriteReadFileOnCD

**Type**: sterling.process
**File**: write-read-file-on-cd.bpml

## Description

Sterling B2B Business Process: WriteReadFileOnCD

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### FileCounterMaiorQueZero
- **Condition**: ``

### MailboxPathNotEmpty
- **Condition**: ``

## Operations

### 1. InformacoesConexao
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `This/LocalCDNodeName`: SINODE01
  - `This/LocalUserId`: demo_connectdirect
  - `This/RemoteCDNodeName`: CDNODE01
  - `This/RemotePasswd`: passw0rd
  - `This/RemoteUserId`: Administrator
  - `This/LocalPasswd`: passw0rd
  - `This/RemoteFilePrefix`: C:\Program Files\ibm\Connect Direct v6.0.0\Server\Download\
  - `This/MessageName`: ArquivoXPTO

### 2. CD Server Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `LocalCDNodeName`: {'from': '/ProcessData/This/LocalCDNodeName/text()'}
  - `LocalUserId`: {'from': '/ProcessData/This/LocalUserId/text()'}
  - `LocalPasswd`: {'from': '/ProcessData/This/LocalPasswd/text()'}
  - `RemoteCDNodeName`: {'from': '/ProcessData/This/RemoteCDNodeName/text()'}
  - `RemoteUserId`: {'from': '/ProcessData/This/RemoteUserId/text()'}
  - `RemotePasswd`: {'from': '/ProcessData/This/RemotePasswd/text()'}
  - `UsingObscuredPasswd`: NO

### 3. CD Server CopyTo Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': 'MessageName/text()'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 4. CD Server CopyFrom Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': 'concat(//This/RemoteFilePrefix/text(),//MessageName/text())'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 5. CD Server End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 6. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `TARGET`: PrimaryDocument

