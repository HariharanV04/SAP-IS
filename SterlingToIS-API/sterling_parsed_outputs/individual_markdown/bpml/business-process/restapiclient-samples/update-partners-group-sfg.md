# update-partners-group-sfgs

**Type**: sterling.process
**File**: update-partners-group-sfg.bpml

## Description

Sterling B2B Business Process: update-partners-group-sfgs

## Operations

### 1. Request
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `url`: http://127.0.0.1:5078/B2BAPIs/svc/partnergroups/Group01
  - `restoperation`: PUT
  - `auth`: admin:passw0rd
  - `Authorization`: Basic
  - `Content-type`: Application/json
  - `Accept`: Application/json
  - `isProxy`: false
  - `jsoninput1`: "addOrRemove": "add","partners": "Sistema_120"
  - `.`: {'from': '*'}

