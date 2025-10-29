# ColetaArquivoViaCDstoreMbx

**Type**: sterling.process
**File**: collect-file-on-cd-store-mbx.bpml

## Description

Sterling B2B Business Process: ColetaArquivoViaCDstoreMbx

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
  - `This/RemoteFileName`: C:\MyTempDir\myfile.dat
  - `This/MailboxPath`: /Demo_ConnectDirect/Inbox
  - `This/MessageName`: myfile.dat

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

### 3. CD Server CopyFrom Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/This/RemoteFileName/text()'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 4. CD Server End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 5. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `ExtractableCount`: 1
  - `MailboxPath`: {'from': '/ProcessData/This/MailboxPath/text()'}
  - `MessageName`: {'from': '/ProcessData/This/MessageName/text()'}

