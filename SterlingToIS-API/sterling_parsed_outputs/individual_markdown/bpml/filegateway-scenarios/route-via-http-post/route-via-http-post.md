# Demo_BP_RouteViaHttpPost

**Type**: sterling.process
**File**: route-via-http-post.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaHttpPost

## Operations

### 1. HTTP Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `HTTPClientAdapter`: HTTPClientAdapter
  - `RemoteHost`: {'from': 'customhttp_RemoteHost/text()'}
  - `RemotePort`: {'from': 'customhttp_RemotePort/text()'}
  - `SSL`: Must
  - `CACertificateId`: {'from': 'customhttp_CertID/text()'}
  - `CipherStrength`: All
  - `.`: {'from': '*'}

### 2. HTTP Client POST Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RawRequest`: false
  - `RawResponse`: false
  - `ResponseTimeout`: 1500
  - `SessionToken`: {'from': '//SessionToken/text()'}
  - `ShowResponseCode`: true
  - `URI`: {'from': 'customhttp_URI/text()'}
  - `.`: {'from': '*'}

### 3. HTTP Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '//SessionToken/text()'}
  - `.`: {'from': '*'}

