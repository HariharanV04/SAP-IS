# ldapsync-create-group-restapi-xml

**Type**: sterling.process
**File**: create-partners-group-sfg-xml.bpml

## Description

Sterling B2B Business Process: ldapsync-create-group-restapi-xml

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': "DOMToDoc(/ProcessData/create,'PrimaryDocument')"}
  - `This/server`: http://127.0.0.1:5078
  - `This/api`: /B2BAPIs/svc/partnergroups/
  - `This/url`: {'from': 'concat(This/server/text(),This/api/text())'}
  - `This/auth`: admin:passw0rd
  - `create/@groupName`: Group01
  - `create/@groupMembers`: Sistema_100,Sistema_110

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

