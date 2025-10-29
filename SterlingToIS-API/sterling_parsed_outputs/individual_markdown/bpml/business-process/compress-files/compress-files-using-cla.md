# Demo_BP_CompressFilesUsingCLA

**Type**: sterling.process
**File**: compress-files-using-cla.bpml

## Description

Sterling B2B Business Process: Demo_BP_CompressFilesUsingCLA

## Operations

### 1. Command Line Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `cmdLine`: /usr/bin/zip ZippedFiles.zip testdata1.csv testadata.csv
  - `workingDir`: /tmp/files2compress
  - `useOutput`: YES

### 2. SetContentType
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `DocumentContentType`: application
  - `DocumentContentSubType`: x-compressed

