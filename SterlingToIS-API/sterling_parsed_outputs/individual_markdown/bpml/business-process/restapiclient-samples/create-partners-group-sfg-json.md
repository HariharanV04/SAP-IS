# REST_CreatePartnerGroups

**Type**: sterling.process
**File**: create-partners-group-sfg-json.bpml

## Description

Sterling B2B Business Process: REST_CreatePartnerGroups

## Operations

### 1. Request
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `url`: http:/127.0.0.1:5078/B2BAPIs/svc/partnergroups/
  - `restoperation`: POST
  - `auth`: admin:passw0rd
  - `Authorization`: Basic
  - `Content-type`: Application/json
  - `Accept`: Application/json
  - `isProxy`: false
  - `jsoninput1`: "groupName": "GrupoTest02", "groupMembers": "Sistema_100,Sistema_110"
  - `.`: {'from': '*'}

