# create-user-restapi-xml

**Type**: sterling.process
**File**: create-user-restapi-xml.bpml

## Description

Sterling B2B Business Process: create-user-restapi-xml

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': "DOMToDoc(/ProcessData/create,'PrimaryDocument')"}
  - `This/server`: http://127.0.0.1:5078
  - `This/url`: {'from': "concat(This/server/text(),'/B2BAPIs/svc/tradingpartners/')"}
  - `This/auth`: admin:passw0rd
  - `create/@username`: demopartner01
  - `create/@partnerName`: demopartner01
  - `create/@givenName`: demo
  - `create/@surname`: demopartner01
  - `create/@authenticationType`: Local
  - `create/@community`: Demo_Community
  - `create/@emailAddress`: kk@ibm.com
  - `create/@password`: passw0rd
  - `create/@postalCode`: 12345-678
  - `create/@isInitiatingConsumer`: true
  - `create/@isInitiatingProducer`: true
  - `create/@isListeningConsumer`: false
  - `create/@isListeningProducer`: false
  - `create/@doesUseSSH`: true
  - `create/@phone`: 555-5555
  - `create/@timeZone`: -031
  - `create/@countryOrRegion`: BR

### 2. Create Partner
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `url`: {'from': 'This/url/text()'}
  - `restoperation`: POST
  - `auth`: {'from': 'This/auth/text()'}
  - `Authorization`: Basic
  - `Content-type`: Application/XML
  - `Accept`: Application/XML
  - `isProxy`: false
  - `jsoninput1`: false
  - `.`: {'from': '*'}

