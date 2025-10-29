# Demo_BP_RouteViaCustomProtocol

**Type**: sterling.process
**File**: route-via-custom-protocol.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaCustomProtocol

## Operations

### 1. Get_Current_Time
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `action`: {'from': "'current_time'"}
  - `format`: yyyy-MM-dd.HH-mm-ss-SSS

### 2. File System Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `extractionFolder`: /home/siuser/CustomProtocol
  - `assignFilename`: true
  - `assignedFilename`: {'from': 'DestinationMessageName/text()'}
  - `Action`: FS_EXTRACT
  - `.`: {'from': '*'}

### 3. FileGatewayRouteEventService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteMetadata'}
  - `EventCode`: CUST_0003
  - `ExceptionLevel`: Normal
  - `EventAttributes/ProducerName`: {'from': 'ProducerName/text()'}
  - `EventAttributes/ConsumerFilename`: {'from': 'DestinationMessageName/text()'}

### 4. FileGatewayRouteEventService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteMetadata'}
  - `EventCode`: CUST_0053
  - `ExceptionLevel`: Normal
  - `EventAttributes/ProducerName`: {'from': 'ProducerName/text()'}
  - `EventAttributes/ConsumerFilename`: {'from': 'DestinationMessageName/text()'}

