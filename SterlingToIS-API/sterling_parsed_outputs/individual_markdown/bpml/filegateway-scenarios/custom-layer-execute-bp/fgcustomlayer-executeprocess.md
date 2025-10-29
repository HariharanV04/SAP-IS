# FGCustomLayer_ExecuteProcess

**Type**: sterling.process
**File**: fgcustomlayer-executeprocess.bpml

## Description

Sterling B2B Business Process: FGCustomLayer_ExecuteProcess

## Operations

### 1. Invoke Sub-Process
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `INVOKE_MODE`: INLINE
  - `WFD_NAME`: {'from': '/ProcessData/BP_TO_RUN/text()'}
  - `.`: {'from': '*'}

### 2. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `TARGET`: /ProcessData/DocumentId
  - `.`: {'from': '*'}

### 3. Get Document Information Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

