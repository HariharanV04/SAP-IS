# DEMO_Async_ParentBP

**Type**: sterling.process
**File**: bp-async-parent.bpml

## Description

Sterling B2B Business Process: DEMO_Async_ParentBP

## Operations

### 1. CallSubProcessService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `INVOKE_MODE`: ASYNC
  - `WFD_NAME`: DEMO_AsyncChildBP
  - `NOTIFY_PARENT_ON_ERROR`: ALL

