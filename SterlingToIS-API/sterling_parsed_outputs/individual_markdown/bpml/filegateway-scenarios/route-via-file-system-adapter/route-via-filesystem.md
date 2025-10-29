# Demo_BP_RouteViaFileSystem

**Type**: sterling.process
**File**: route-via-filesystem.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaFileSystem

## Operations

### 1. File System Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `extractionFolder`: {'from': 'fsa_RemoteFileSystem/text()'}
  - `assignFilename`: true
  - `assignedFilename`: {'from': 'DestinationMessageName/text()'}
  - `Action`: FS_EXTRACT
  - `.`: {'from': '*'}

### 2. FileGatewayRouteEventService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteMetadata'}
  - `EventCode`: CUST_0003
  - `ExceptionLevel`: Normal
  - `EventAttributes/ProducerName`: {'from': 'ProducerName/text()'}
  - `EventAttributes/ConsumerFilename`: {'from': 'DestinationMessageName/text()'}

### 3. FileGatewayRouteEventService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteMetadata'}
  - `EventCode`: CUST_0053
  - `ExceptionLevel`: Normal
  - `EventAttributes/ProducerName`: {'from': 'ProducerName/text()'}
  - `EventAttributes/ConsumerFilename`: {'from': 'DestinationMessageName/text()'}

