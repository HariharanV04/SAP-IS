# Demo_BP_CLA_Example_01

**Type**: sterling.process
**File**: cmd-line-example-01.bpml

## Description

Sterling B2B Business Process: Demo_BP_CLA_Example_01

## Operations

### 1. Command Line 2 Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `cmdLine`: /home/siuser/myscript.sh $0 $1 $2 $Outputs
  - `parm0`: CLA2
  - `parm1`: Hello
  - `parm2`: World!
  - `useOutput`: true
  - `workingDir`: /home/siuser/

