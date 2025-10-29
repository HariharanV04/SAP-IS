# FGCustomLayer_Translation

**Type**: sterling.process
**File**: fgcustomlayer-translation.bpml

## Description

Sterling B2B Business Process: FGCustomLayer_Translation

## Operations

### 1. Translation
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `map_name`: {'from': '/ProcessData/Map_Name/text()'}

### 2. FileGatewayRouteEventServiceType
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteDataflowId'}
  - `EventCode`: CUST_0002
  - `ExceptionLevel`: Normal
  - `EventAttributes/Map_Name`: {'from': '/ProcessData/Map_Name/text()'}

### 3. FileGatewayRouteEventServiceType
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteDataflowId'}
  - `EventCode`: CUST_0052
  - `ExceptionLevel`: Normal
  - `EventAttributes/Map_Name`: {'from': '/ProcessData/Map_Name/text()'}

