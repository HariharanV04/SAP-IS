# Demo_BP_Append_List

**Type**: sterling.process
**File**: bp-append-list-02.bpml

## Description

Sterling B2B Business Process: Demo_BP_Append_List

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### has_next
- **Condition**: ``

### skip_item
- **Condition**: ``

## Operations

### 1. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `TARGET`: /ProcessData/List/Item[1]
  - `.`: {'from': '*'}

