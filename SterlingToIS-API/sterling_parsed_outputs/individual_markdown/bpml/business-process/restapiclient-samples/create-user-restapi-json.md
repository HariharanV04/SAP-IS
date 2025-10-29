# create-user-restapi-json

**Type**: sterling.process
**File**: create-user-restapi-json.bpml

## Description

Sterling B2B Business Process: create-user-restapi-json

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': "DOMToDoc(/ProcessData/Partner,'PrimaryDocument')"}
  - `This/server`: http://127.0.0.1:5078
  - `This/url`: {'from': "concat(This/server/text(),'/B2BAPIs/svc/tradingpartners/')"}
  - `This/auth`: admin:passw0rd
  - `This/emailAddress`: kk@ibm.com
  - `Partner/username`: demopartner01
  - `Partner/partnerName`: demopartner01
  - `Partner/givenName`: demo
  - `Partner/surname`: demopartner01
  - `Partner/authenticationType`: Local
  - `Partner/community`: Demo_Community
  - `Partner/emailAddress`: kk@ibm.com
  - `Partner/password`: passw0rd
  - `Partner/postalCode`: 12345-678
  - `Partner/isInitiatingConsumer`: True
  - `Partner/isInitiatingProducer`: True
  - `Partner/isListeningConsumer`: False
  - `Partner/isListeningProducer`: False
  - `Partner/doesUseSSH`: true
  - `Partner/phone`: 555-5555

### 2. Convert to Json
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `InputType`: XML
  - `OutputPath`: output.json

### 3. Create Partner
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `url`: {'from': 'This/url/text()'}
  - `restoperation`: POST
  - `auth`: {'from': 'This/auth/text()'}
  - `Authorization`: Basic
  - `Content-type`: Application/json
  - `Accept`: Application/json
  - `isProxy`: false
  - `jsoninput1`: false
  - `.`: {'from': '*'}

