# Demo_BP_CompressFilesFromFS

**Type**: sterling.process
**File**: compress-files-from-filesystem.bpml

## Description

Sterling B2B Business Process: Demo_BP_CompressFilesFromFS

## Operations

### 1. FileSystem
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Action`: FS_COLLECT
  - `collectionFolder`: c:\tmp\files2compress
  - `filter`: *.csv
  - `collectMultiple`: true
  - `.`: {'from': '*'}

### 2. Compress
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `compression_action`: compress
  - `compressed_filename`: ZippedFiles.zip
  - `compression_level`: 9
  - `compression_type`: Deflate

### 3. FileSystem
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Action`: FS_EXTRACT
  - `extractionFolder`: c:\tmp\compressedFiles
  - `.`: {'from': '*'}

