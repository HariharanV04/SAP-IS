# Demo_XML_Attributes_Elements

**Type**: sterling.process
**File**: xml-attributes-elements.bpml

## Description

Sterling B2B Business Process: Demo_XML_Attributes_Elements

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `LDAPAdapter/request/@scope`: subtree
  - `LDAPAdapter/request/@operation`: Read
  - `LDAPAdapter/request/@baseDN`: ou=Group,dc=test,dc=net
  - `LDAPAdapter/request/param.1`: (objectClass=groupOfNames)
  - `LDAPAdapter/request/param.1/@usage`: Search
  - `LDAPAdapter/request/param.2/@name`: cn
  - `LDAPAdapter/request/param.2/@usage`: Input
  - `LDAPAdapter/request/param.3/@name`: member
  - `LDAPAdapter/request/param.3/@usage`: Input

