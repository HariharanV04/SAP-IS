# Sterling B2B Integration Documentation

Generated: 2025-10-22 20:23:04

## Overview

This documentation covers 74 Sterling B2B components:
- BPML Processes: 72
- MXL Maps: 4

## Business Processes (BPML)

### XAPI_CreateUser_Example01

# XAPI_CreateUser_Example01

**Type**: sterling.process
**File**: XAPI_CreateUser.bpml

## Description

Sterling B2B Business Process: XAPI_CreateUser_Example01

## Operations

### 1. XAPI Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `api`: createUserHierarchy


---

### XAPI_CreateRoutingChannel

# XAPI_CreateRoutingChannel

**Type**: sterling.process
**File**: XAPI_CreateRoutingChannel.bpml

## Description

Sterling B2B Business Process: XAPI_CreateRoutingChannel

## Operations

### 1. XAPI Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `api`: createFgTemplatedRoutingChannel
  - `UserId`: admin


---

### DEMO_AsyncChildBP

# DEMO_AsyncChildBP

**Type**: sterling.process
**File**: bp-async-child.bpml

## Description

Sterling B2B Business Process: DEMO_AsyncChildBP


---

### DEMO_AsyncParentBP_PrimaryDoc

# DEMO_AsyncParentBP_PrimaryDoc

**Type**: sterling.process
**File**: bp-async-parent-primarydoc.bpml

## Description

Sterling B2B Business Process: DEMO_AsyncParentBP_PrimaryDoc

## Operations

### 1. 
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `WFD_NAME`: DEMO_AsyncChildBP
  - `INVOKE_MODE`: ASYNC


---

### DEMO_Async_ParentBP

# DEMO_Async_ParentBP

**Type**: sterling.process
**File**: bp-async-parent.bpml

## Description

Sterling B2B Business Process: DEMO_Async_ParentBP

## Operations

### 1. CallSubProcessService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `INVOKE_MODE`: ASYNC
  - `WFD_NAME`: DEMO_AsyncChildBP
  - `NOTIFY_PARENT_ON_ERROR`: ALL


---

### Demo_BP_Convert_Json2Xml_input

# Demo_BP_Convert_Json2Xml_input

**Type**: sterling.process
**File**: convert-json2xml-file.bpml

## Description

Sterling B2B Business Process: Demo_BP_Convert_Json2Xml_input

## Operations

### 1. Request
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `InputType`: JSON
  - `OutputPath`: output.xml


---

### Demo_BP_Convert_Json2Xml_input

# Demo_BP_Convert_Json2Xml_input

**Type**: sterling.process
**File**: convert-json2xml-input.bpml

## Description

Sterling B2B Business Process: Demo_BP_Convert_Json2Xml_input

## Operations

### 1. Request
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input`: {"student":{"name":"Anakin Skywalker","age":"22"}}
  - `InputType`: JSON
  - `OutputPath`: output.xml
  - `.`: {'from': '*'}


---

### Demo_BP_Convert_Json2Xml_input

# Demo_BP_Convert_Json2Xml_input

**Type**: sterling.process
**File**: convert-xml2json-file.bpml

## Description

Sterling B2B Business Process: Demo_BP_Convert_Json2Xml_input

## Operations

### 1. Request
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `InputType`: XML
  - `OutputPath`: output.json


---

### Demo_BP_Convert_Xml2Json_input

# Demo_BP_Convert_Xml2Json_input

**Type**: sterling.process
**File**: convert-xml2json-input.bpml

## Description

Sterling B2B Business Process: Demo_BP_Convert_Xml2Json_input

## Operations

### 1. Request
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input`: <message>Hello World!</message>
  - `InputType`: XML
  - `OutputPath`: output.json
  - `.`: {'from': '*'}


---

### JavaTaskCheckSum

# JavaTaskCheckSum

**Type**: sterling.process
**File**: check-sum-java-task.bpml

## Description

Sterling B2B Business Process: JavaTaskCheckSum

## Operations

### 1. JavaTaskSample
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `srcLocationMode`: inline
  - `javaSrc`: 
import com.sterlingcommerce.woodstock.workflow.Document;
import com.sterlingcommerce.woodstock.workflow.WFCBase;
import java.io.InputStream;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import org.apache.commons.codec.digest.DigestUtils;

String digest = null;
Document document = new Document();
Document srcDoc = wfc.getPrimaryDocument();
InputStream is = srcDoc.getInputStream();

try {
  digest = DigestUtils.md5Hex(is);
  wfc.setBasicStatus(WFCBase.SUCCESS);
  wfc.addWFContent("CheckSum", digest.toString());
} catch (Exception ex) {
  wfc.setBasicStatus(WFCBase.ERROR);
  wfc.addWFContent("CheckSumError", ex.getMessage());
}
return "000";
				
  - `.`: {'from': '*'}


---

### Demo_BP_CLA_Example_01

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


---

### CodeListEditorWeb

# CodeListEditorWeb

**Type**: sterling.process
**File**: code-list-editor-web.bpml

## Description

Sterling B2B Business Process: CodeListEditorWeb

## Integration Patterns

- Conditional Logic

## Business Rules

### list_name
- **Condition**: ``

### http_method_post
- **Condition**: ``

### http_method_get
- **Condition**: ``

### no_parameters
- **Condition**: ``

### is_new_page
- **Condition**: ``

### search_has_results
- **Condition**: ``

### update_has_results
- **Condition**: ``

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `/ProcessData/ResponseData/searchpage`: Search Page
  - `This/sqlMain`: {'from': 'concat("SELECT * FROM CODELIST_XREF_ITEM WHERE CODELIST_XREF_ITEM.LIST_NAME = \'",/ProcessData/sLN/text(),"\' AND CODELIST_XREF_ITEM.LIST_VERSION = (SELECT DEFAULT_VERSION FROM CODELIST_XREF_VERS WHERE CODELIST_XREF_VERS.LIST_NAME = \'",/ProcessData/sLN/text(),"\')")'}
  - `This/sqlSender`: {'from': 'if (string-length(/ProcessData/sSIt) > 0,concat(" AND SENDER_ITEM like \'%",/ProcessData/sSIt/text(),"%\'"),"")'}
  - `This/sqlReceiver`: {'from': 'if (string-length(/ProcessData/sRIt) > 0,concat(" AND RECEIVER_ITEM like \'%",/ProcessData/sRIt/text(),"%\'"),"")'}
  - `This/sqlSelect`: {'from': 'concat(This/sqlMain,This/sqlSender,This/sqlReceiver)'}

### 2. Lightweight JDBC Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `pool`: {'from': '/ProcessData/This/databasePool/text()'}
  - `query_type`: SELECT
  - `result_name`: Result1
  - `row_name`: Row1
  - `sql`: {'from': '/ProcessData/This/sqlSelect/text()'}

### 3. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `/ProcessData/ResponseData/updatepage`: Update Page
  - `This/P1`: UPDATE CODELIST_XREF_ITEM SET
  - `This/F1`: {'from': 'concat(" SENDER_ITEM = \'",/ProcessData/HttpURLDecodedValues/mSIt/text(),"\',")'}
  - `This/F2`: {'from': 'concat(" RECEIVER_ITEM = \'",/ProcessData/HttpURLDecodedValues/mRIt/text(),"\',")'}
  - `This/F3`: {'from': 'concat(" DESCRIPTION = \'",/ProcessData/HttpURLDecodedValues/mDesc/text(),"\',")'}
  - `This/F4`: {'from': 'concat(" TEXT1 = \'",/ProcessData/HttpURLDecodedValues/mT1/text(),"\',")'}
  - `This/F5`: {'from': 'concat(" TEXT2 = \'",/ProcessData/HttpURLDecodedValues/mT2/text(),"\',")'}
  - `This/F6`: {'from': 'concat(" TEXT3 = \'",/ProcessData/HttpURLDecodedValues/mT3/text(),"\'")'}
  - `This/W1`: {'from': 'concat(" WHERE LIST_NAME = \'",/ProcessData/HttpURLDecodedValues/LN,"\'")'}
  - `This/W2`: {'from': 'concat(" AND LIST_VERSION = \'",/ProcessData/HttpURLDecodedValues/LV,"\'")'}
  - `This/W3`:  AND SENDER_ID IS NULL AND RECEIVER_ID IS NULL
  - `This/W4`: {'from': 'concat(" AND SENDER_ITEM = \'",/ProcessData/HttpURLDecodedValues/SIt,"\'")'}
  - `This/W5`: {'from': 'concat(" AND RECEIVER_ITEM = \'",/ProcessData/HttpURLDecodedValues/RIt,"\'")'}
  - `This/sqlUpdate`: {'from': 'concat(This/P1,This/F1,This/F2,This/F3,This/F4,This/F5,This/F6,This/W1,This/W2,This/W3,This/W4,This/W5)'}

### 4. Lightweight JDBC Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `pool`: {'from': '/ProcessData/This/databasePool/text()'}
  - `query_type`: UPDATE
  - `result_name`: Result1
  - `row_name`: Row1
  - `sql`: {'from': '/ProcessData/This/sqlUpdate/text()'}

### 5. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/ResponseData
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: CodeListEditorWeb
  - `.`: {'from': '*'}

### 6. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}


---

### Demo_BP_CompressFilesFromFS

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


---

### Demo_BP_CompressFilesUsingCLA

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


---

### Demo_BP_CopyFileFromFSA2MBX

# Demo_BP_CopyFileFromFSA2MBX

**Type**: sterling.process
**File**: copy-file-from-fsa-to-mbx.bpml

## Description

Sterling B2B Business Process: Demo_BP_CopyFileFromFSA2MBX

## Operations

### 1. File System Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `Action`: FS_COLLECT
  - `collectionFolder`: C:\Temp\
  - `collectMultiple`: false
  - `deleteAfterCollect`: false
  - `filter`: *.txt

### 2. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: {'from': '/Inbox'}


---

### Demo_BP_CopyMultipleFilesFromFSA2MBX

# Demo_BP_CopyMultipleFilesFromFSA2MBX

**Type**: sterling.process
**File**: copy-multiplefiles-fsa-to-mbx.bpml

## Description

Sterling B2B Business Process: Demo_BP_CopyMultipleFilesFromFSA2MBX

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### more_docs
- **Condition**: ``

## Operations

### 1. File System Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `Action`: FS_COLLECT
  - `collectionFolder`: C:\Temp\
  - `collectMultiple`: true
  - `deleteAfterCollect`: false
  - `filter`: *.txt
  - `noFilesSetSuccess`: true

### 2. For Each Document
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `DOCUMENT_KEY_PREFIX`: FSA_Document
  - `ITERATOR_NAME`: FSADoc

### 3. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: /Inbox


---

### Demo_BP_LineFolding

# Demo_BP_LineFolding

**Type**: sterling.process
**File**: file-folding.bpml

## Description

Sterling B2B Business Process: Demo_BP_LineFolding

## Operations

### 1. FileFolding
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `srcLocationMode`: inline
  - `javaSrc`: import java.io.BufferedReader; 
import java.io.InputStreamReader; 
import java.io.PrintStream; 
import com.sterlingcommerce.woodstock.workflow.WorkFlowContext; 
import com.sterlingcommerce.woodstock.workflow.WorkFlowException; 
import com.sterlingcommerce.woodstock.workflow.Document; 
 
String strFoldLen = wfc.getParm("LineFoldLength"); 
int foldLen = new Integer(strFoldLen).intValue(); 

Document srcDoc = wfc.getPrimaryDocument(); 
Document foldDoc = wfc.newDocument(); 
 
BufferedReader reader = new BufferedReader(new InputStreamReader(srcDoc.getInputStream())); 
PrintStream writer = new PrintStream(foldDoc.getOutputStream()); 
 
String line = ""; 
while ((line = reader.readLine()) != null) { 
    String foldStr = line.replaceAll("(.{" + foldLen + "})", "$1\n"); 
    writer.println(foldStr); 
} 
 
writer.close(); 
reader.close(); 
 
wfc.putPrimaryDocument(foldDoc); 
return "OK"; 
  - `.`: {'from': '*'}


---

### Demo_BP_FTPGetMultipleFiles

# Demo_BP_FTPGetMultipleFiles

**Type**: sterling.process
**File**: ftp-get-multiple-files.bpml

## Description

Sterling B2B Business Process: Demo_BP_FTPGetMultipleFiles

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### FileCounter
- **Condition**: ``

### DELETE_FILES?
- **Condition**: ``

### MOVE_FILES?
- **Condition**: ``

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `REMOTE_HOST`: localhost
  - `REMOTE_PORT`: 21
  - `FTP_CLIENT_ADAPTER`: FTPClientAdapter
  - `REMOTE_USER`: sistema_ftp
  - `REMOTE_PASSWORD`: passw0rd
  - `REMOTE_DIRECTORY`: /home/sistema_ftp
  - `REMOTE_FILENAME`: *.txt
  - `MAILBOX_PATH`: /Sistema_ftp/Inbox

### 2. FTP Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RemoteHost`: {'from': '//REMOTE_HOST/text()'}
  - `FTPClientAdapter`: {'from': '//FTP_CLIENT_ADAPTER/text()'}
  - `UsingRevealedPasswd`: True
  - `RemotePasswd`: {'from': '//REMOTE_PASSWORD/text()'}
  - `RemoteUserId`: {'from': '//REMOTE_USER/text()'}
  - `RemotePort`: {'from': '//REMOTE_PORT/text()'}
  - `.`: {'from': '*'}

### 3. FTP CD SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}
  - `Directory`: {'from': '//REMOTE_DIRECTORY/text()'}

### 4. FTP Client LIST Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `NamesOnly`: YES
  - `RemoteFileName`: {'from': '//REMOTE_FILENAME/text()'}
  - `ResponseTimeout`: 60
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}

### 5. FTP Client GET Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RemoteFileName`: {'from': '//ListNames/Name[1]/text()'}
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}
  - `ConnectionType`: PASSIVE

### 6. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Extractable`: YES
  - `MailboxPath`: {'from': '//MAILBOX_PATH/text()'}
  - `MessageName`: {'from': '//ListNames/Name[1]/text()'}
  - `.`: {'from': '*'}

### 7. FTP Client MOVE Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/ListNames/Name[1]/text()'}
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}

### 8. FTP Client DELETE Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/ListNames/Name[1]/text()'}
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}

### 9. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `TARGET`: /ProcessData/PrimaryDocument | /ProcessData/DocumentList/DocumentId[1] | /ProcessData/ListNames/Name[1] | /ProcessData/MailboxAddResults
  - `.`: {'from': '*'}

### 10. FTP Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FTPClientBeginSessionServiceResults/SessionToken/text()'}
  - `.`: {'from': '*'}


---

### GenerateFiles

# GenerateFiles

**Type**: sterling.process
**File**: generate-files.bpml

## Description

Sterling B2B Business Process: GenerateFiles

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### This/FileCounter
- **Condition**: ``

## Operations

### 1. Get_Current_Time
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `action`: {'from': "'current_time'"}
  - `format`: 'D'yyyyMMdd.'S'HHmm

### 2. Document Keyword Replace
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `literal_bufferSize`: 102400
  - `literal_mode`: true
  - `literal_readAheadSize`: 8192
  - `keyword1`: {'from': 'string(\'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\')'}
  - `keywordtype1`: string
  - `replace1`: {'from': "string('')"}
  - `keyword2`: {'from': "string('<ProcessData/>')"}
  - `keywordtype2`: string
  - `replace2`: {'from': "string('')"}
  - `keyword3`: X
  - `keywordtype3`: string
  - `replace3`: {'from': "string('')"}
  - `.`: {'from': '*'}

### 3. Get Document Information Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 4. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: {'from': '/ProcessData/This/MailboxPath'}


---

### ColetaArquivoViaCDstoreMbx

# ColetaArquivoViaCDstoreMbx

**Type**: sterling.process
**File**: collect-file-on-cd-store-mbx.bpml

## Description

Sterling B2B Business Process: ColetaArquivoViaCDstoreMbx

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### FileCounterMaiorQueZero
- **Condition**: ``

### MailboxPathNotEmpty
- **Condition**: ``

## Operations

### 1. InformacoesConexao
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `This/LocalCDNodeName`: SINODE01
  - `This/LocalUserId`: demo_connectdirect
  - `This/RemoteCDNodeName`: CDNODE01
  - `This/RemotePasswd`: passw0rd
  - `This/RemoteUserId`: Administrator
  - `This/LocalPasswd`: passw0rd
  - `This/RemoteFileName`: C:\MyTempDir\myfile.dat
  - `This/MailboxPath`: /Demo_ConnectDirect/Inbox
  - `This/MessageName`: myfile.dat

### 2. CD Server Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `LocalCDNodeName`: {'from': '/ProcessData/This/LocalCDNodeName/text()'}
  - `LocalUserId`: {'from': '/ProcessData/This/LocalUserId/text()'}
  - `LocalPasswd`: {'from': '/ProcessData/This/LocalPasswd/text()'}
  - `RemoteCDNodeName`: {'from': '/ProcessData/This/RemoteCDNodeName/text()'}
  - `RemoteUserId`: {'from': '/ProcessData/This/RemoteUserId/text()'}
  - `RemotePasswd`: {'from': '/ProcessData/This/RemotePasswd/text()'}
  - `UsingObscuredPasswd`: NO

### 3. CD Server CopyFrom Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/This/RemoteFileName/text()'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 4. CD Server End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 5. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `ExtractableCount`: 1
  - `MailboxPath`: {'from': '/ProcessData/This/MailboxPath/text()'}
  - `MessageName`: {'from': '/ProcessData/This/MessageName/text()'}


---

### ColetaArquivoViaCD

# ColetaArquivoViaCD

**Type**: sterling.process
**File**: collect-file-on-cd.bpml

## Description

Sterling B2B Business Process: ColetaArquivoViaCD

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### FileCounterMaiorQueZero
- **Condition**: ``

### MailboxPathNotEmpty
- **Condition**: ``

## Operations

### 1. InformacoesConexao
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `This/LocalCDNodeName`: SINODE01
  - `This/LocalUserId`: demo_connectdirect
  - `This/RemoteCDNodeName`: CDNODE01
  - `This/RemotePasswd`: passw0rd
  - `This/RemoteUserId`: Administrator
  - `This/LocalPasswd`: passw0rd
  - `This/RemoteFileName`: C:\MyTempDir\myfile.dat
  - `This/MessageName`: myfile.dat

### 2. CD Server Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `LocalCDNodeName`: {'from': '/ProcessData/This/LocalCDNodeName/text()'}
  - `LocalUserId`: {'from': '/ProcessData/This/LocalUserId/text()'}
  - `LocalPasswd`: {'from': '/ProcessData/This/LocalPasswd/text()'}
  - `RemoteCDNodeName`: {'from': '/ProcessData/This/RemoteCDNodeName/text()'}
  - `RemoteUserId`: {'from': '/ProcessData/This/RemoteUserId/text()'}
  - `RemotePasswd`: {'from': '/ProcessData/This/RemotePasswd/text()'}
  - `UsingObscuredPasswd`: NO

### 3. CD Server CopyFrom Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/This/RemoteFileName/text()'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 4. CD Server End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 5. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `TARGET`: PrimaryDocument


---

### WriteReadFileOnCD

# WriteReadFileOnCD

**Type**: sterling.process
**File**: write-read-file-on-cd.bpml

## Description

Sterling B2B Business Process: WriteReadFileOnCD

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### FileCounterMaiorQueZero
- **Condition**: ``

### MailboxPathNotEmpty
- **Condition**: ``

## Operations

### 1. InformacoesConexao
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `This/LocalCDNodeName`: SINODE01
  - `This/LocalUserId`: demo_connectdirect
  - `This/RemoteCDNodeName`: CDNODE01
  - `This/RemotePasswd`: passw0rd
  - `This/RemoteUserId`: Administrator
  - `This/LocalPasswd`: passw0rd
  - `This/RemoteFilePrefix`: C:\Program Files\ibm\Connect Direct v6.0.0\Server\Download\
  - `This/MessageName`: ArquivoXPTO

### 2. CD Server Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `LocalCDNodeName`: {'from': '/ProcessData/This/LocalCDNodeName/text()'}
  - `LocalUserId`: {'from': '/ProcessData/This/LocalUserId/text()'}
  - `LocalPasswd`: {'from': '/ProcessData/This/LocalPasswd/text()'}
  - `RemoteCDNodeName`: {'from': '/ProcessData/This/RemoteCDNodeName/text()'}
  - `RemoteUserId`: {'from': '/ProcessData/This/RemoteUserId/text()'}
  - `RemotePasswd`: {'from': '/ProcessData/This/RemotePasswd/text()'}
  - `UsingObscuredPasswd`: NO

### 3. CD Server CopyTo Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': 'MessageName/text()'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 4. CD Server CopyFrom Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': 'concat(//This/RemoteFilePrefix/text(),//MessageName/text())'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 5. CD Server End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `SessionToken`: {'from': '//BeginSessionResults/SessionToken/node()'}

### 6. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `TARGET`: PrimaryDocument


---

### JavaTaskGzipCompress

# JavaTaskGzipCompress

**Type**: sterling.process
**File**: gzip-compress-java-task.bpml

## Description

Sterling B2B Business Process: JavaTaskGzipCompress

## Operations

### 1. GzipCompress
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `srcLocationMode`: inline
  - `javaSrc`: 
import com.sterlingcommerce.woodstock.workflow.Document;
import java.io.*;
import java.util.zip.GZIPOutputStream;

try {
    String fileName = "myfilename.gz";

    Document doc = wfc.getPrimaryDocument();
    String bodyNameInput = doc.getBodyName();
    wfc.addWFContent("DocumentNameInput",bodyNameInput); 

    // Open the file for reading
    InputStream is = doc.getBodyInputStream();
    BufferedInputStream bis = new BufferedInputStream(is);


    // Open the gzip file for writing
    Document newDoc = new Document();
    OutputStream os = newDoc.getOutputStream();

    //FileOutputStream fos = new FileOutputStream(fileName + ".gz");
    //GZIPOutputStream gzos = new GZIPOutputStream(fos, 9);
    GZIPOutputStream gzos = new GZIPOutputStream(os, 9);
    BufferedOutputStream bos = new BufferedOutputStream(gzos);

    // Write the compressed data
    byte[] buffer = new byte[1024];
    int bytesRead;
    while ((bytesRead = bis.read(buffer)) != -1) {
    bos.write(buffer, 0, bytesRead);
    }

    // Close the streams
    bos.close();
    bis.close();

    //String newContent = "This is the content of the new Primary Document";
    //Document newDoc = new Document();
    //OutputStream os = newDoc.getOutputStream();
    //os.write(newContent.getBytes());
    os.flush();
    os.close();
    wfc.putPrimaryDocument(newDoc);
    wfc.addWFContent("DocumentNameOutput",fileName); 
} catch (IOException e) {
    log.log("Error: " + e.getMessage());
}
return "OK";
    
  - `.`: {'from': '*'}


---

### HelloWorldJSON

# HelloWorldJSON

**Type**: sterling.process
**File**: hello-world-json.bpml

## Description

Sterling B2B Business Process: HelloWorldJSON

## Operations

### 1. XmlJsonTransformer
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Input`: <book><title>The Lord of Rings</title><author>J.R.R. Tolkien</author></book>
  - `InputType`: XML
  - `OutputPath`: output.json
  - `.`: {'from': '*'}

### 2. SetContenType
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `DocumentContentType`: application
  - `DocumentContentSubType`: json
  - `updateMetaDataOnly`: true

### 3. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}


---

### RESTAPIClientJSON

# RESTAPIClientJSON

**Type**: sterling.process
**File**: restapi-client-json.bpml

## Description

Sterling B2B Business Process: RESTAPIClientJSON

## Operations

### 1. Request
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `url`: http://localhost:5033/helloworldjson
  - `restoperation`: GET
  - `Content-type`: Application/json
  - `Accept`: Application/json
  - `isProxy`: false
  - `proxyHost`: 127.0.0.1
  - `proxyPort`: 8080
  - `isProxyAuth`: false
  - `.`: {'from': '*'}


---

### HelloWorldXML

# HelloWorldXML

**Type**: sterling.process
**File**: hello-world-xml.bpml

## Description

Sterling B2B Business Process: HelloWorldXML

## Operations

### 1. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/ResponseData
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: HelloWorldXML
  - `.`: {'from': '*'}

### 2. SetContenType
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `DocumentContentType`: application
  - `DocumentContentSubType`: xml
  - `updateMetaDataOnly`: true

### 3. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}


---

### RESTAPIClientXML

# RESTAPIClientXML

**Type**: sterling.process
**File**: restapi-client-xml.bpml

## Description

Sterling B2B Business Process: RESTAPIClientXML

## Operations

### 1. Request
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `url`: http://localhost:5033/helloworldxml
  - `restoperation`: GET
  - `Content-type`: Application/xml
  - `Accept`: Application/xml
  - `isProxy`: false
  - `proxyHost`: 127.0.0.1
  - `proxyPort`: 8080
  - `isProxyAuth`: false
  - `.`: {'from': '*'}


---

### HttpPostToMailbox

# HttpPostToMailbox

**Type**: sterling.process
**File**: http-post-to-mailbox.bpml

## Description

Sterling B2B Business Process: HttpPostToMailbox

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `MAILBOX_PATH`: /Sistema_ftp/Inbox

### 2. set user token
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `USER_TOKEN`: admin
  - `.`: {'from': '*'}

### 3. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `Extractable`: Yes
  - `DocumentId`: {'from': '/PrimaryDocument/@SCIObjectID'}
  - `MailboxPath`: {'from': '//MAILBOX_PATH/text()'}

### 4. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}


---

### Demo_LDAPAdapter

# Demo_LDAPAdapter

**Type**: sterling.process
**File**: demo-ldap-01.bpml

## Description

Sterling B2B Business Process: Demo_LDAPAdapter

## Operations

### 1. LDAP
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### Demo_LDAPExtraction

# Demo_LDAPExtraction

**Type**: sterling.process
**File**: demo-ldap-02.bpml

## Description

Sterling B2B Business Process: Demo_LDAPExtraction

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

### 2. LDAP
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### Demo_BP_RenameRegexJavaTask

# Demo_BP_RenameRegexJavaTask

**Type**: sterling.process
**File**: demo-rename-regex-java-task.bpml

## Description

Sterling B2B Business Process: Demo_BP_RenameRegexJavaTask

## Operations

### 1. RegexMapTest
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `srcLocationMode`: inline
  - `javaSrc`: 
  import java.util.regex.Matcher;
  import java.util.regex.Pattern;

	String fileName = (String)wfc.getWFContent("fileName");
	String matchPattern = (String)wfc.getWFContent("matchPattern");
	String replacePattern = (String)wfc.getWFContent("replacePattern");

  Pattern p1 = Pattern.compile(matchPattern);
  Matcher m1 = p1.matcher(fileName);

  if (m1.find( )) {
    String output = m1.replaceFirst(replacePattern);
    wfc.addWFContent("resultFilename", output);
  } else {
    wfc.addWFContent("resultFilename", fileName);
    wfc.addWFContent("nomatch", "true");
  }

	return "OK";
  - `.`: {'from': '*'}


---

### REST_CreatePartnerGroups

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


---

### ldapsync-create-group-restapi-xml

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


---

### create-user-restapi-json

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


---

### create-user-restapi-xml

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


---

### update-partners-group-sfgs

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


---

### Demo_BP_test_smtp

# Demo_BP_test_smtp

**Type**: sterling.process
**File**: bp-send-smtp-mail.bpml

## Description

Sterling B2B Business Process: Demo_BP_test_smtp

## Operations

### 1. Send
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `xport-smtp-mailhost`: {'from': '//mailhost/text()'}
  - `xport-smtp-mailport`: 25
  - `xport-smtp-mailfrom`: a@company.com
  - `xport-smtp-mailto`: b@company.com
  - `xport-smtp-mailCC`: c@company.com
  - `xport-smtp-mailsubject`: {'from': '//MAIL_SUBJECT/text()'}


---

### Demo_BP_SFTPGetMultipleFiles

# Demo_BP_SFTPGetMultipleFiles

**Type**: sterling.process
**File**: sftp-get-multiple-files.bpml

## Description

Sterling B2B Business Process: Demo_BP_SFTPGetMultipleFiles

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### FileCounter
- **Condition**: ``

### DELETE_FILES?
- **Condition**: ``

### MOVE_FILES?
- **Condition**: ``

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SFTP_CLIENT_ADAPTER`: SFTPClientAdapter
  - `SSH_PROFILEID`: 2356001890249e5e3node1
  - `REMOTE_DIRECTORY`: /home/sistema_sftp
  - `REMOTE_FILENAME`: *.txt
  - `MAILBOX_PATH`: /Parceiro_SFTP/Inbox

### 2. SFTP Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `SFTPClientAdapter`: {'from': '//SFTP_CLIENT_ADAPTER/text()'}
  - `ProfileId`: {'from': '/ProcessData/SSH_PROFILEID/text()'}

### 3. SFTP CD SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Directory`: {'from': '//REMOTE_DIRECTORY/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 4. SFTP Client LIST Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '//REMOTE_FILENAME/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 5. SFTP Client GET Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/SFTPClientListResults/Files/File[1]/Name/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 6. Mailbox Add Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `DocumentId`: {'from': '/ProcessData/DocumentList/DocumentId[1]/text()'}
  - `Extractable`: YES
  - `MailboxPath`: {'from': '//MAILBOX_PATH/text()'}
  - `.`: {'from': '*'}

### 7. SFTP Client MOVE Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/SFTPClientListResults/Files/File[1]/Name/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 8. SFTP Client DELETE Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `RemoteFileName`: {'from': '/ProcessData/SFTPClientListResults/Files/File[1]/Name/text()'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}

### 9. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `TARGET`: /ProcessData/DocumentList/DocumentId[1] | /ProcessData/SFTPClientListResults/Files/File[1] | /ProcessData/MailboxAdd
  - `.`: {'from': '*'}

### 10. SFTP Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `SessionToken`: {'from': '/ProcessData/SFTPClientBeginSessionServiceResults/SessionToken/text()'}


---

### Demo_Kafka_Consumer

# Demo_Kafka_Consumer

**Type**: sterling.process
**File**: demo-kafka-consumer.bpml

## Description

Sterling B2B Business Process: Demo_Kafka_Consumer

## Operations

### 1. Kafka Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Action`: get
  - `BootStrapServers`: localhost:29092
  - `KafkaClientAdapter`: KafkaClientAdapter
  - `SecurityAction`: PLAINTEXT
  - `GroupId`: demo-sfg-consumer-0001
  - `.`: {'from': 'PrimaryDocument'}

### 2. Kafka Client Consumer Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Topic`: sb2b-kfk-inbound

### 3. Kafka Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Action`: get


---

### Demo_Kafka_Producer

# Demo_Kafka_Producer

**Type**: sterling.process
**File**: demo-kafka-producer.bpml

## Description

Sterling B2B Business Process: Demo_Kafka_Producer

## Operations

### 1. Kafka Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Action`: put
  - `BootStrapServers`: localhost:29092
  - `KafkaClientAdapter`: KafkaClientAdapter
  - `SecurityAction`: PLAINTEXT
  - `ProducerConfig`: buffer.memory=102400;compression.type=gzip
  - `.`: {'from': 'PrimaryDocument'}

### 2. Kafka Client Producer Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Topic`: sb2b-kfk-outbound
  - `.`: {'from': 'PrimaryDocument'}

### 3. Kafka Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Action`: put


---

### Demo_BP_Append_List

# Demo_BP_Append_List

**Type**: sterling.process
**File**: bp-append-list-01.bpml

## Description

Sterling B2B Business Process: Demo_BP_Append_List

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### has_next
- **Condition**: ``

## Operations

### 1. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `TARGET`: /ProcessData/List/Item[1]
  - `.`: {'from': '*'}


---

### Demo_BP_Append_List

# Demo_BP_Append_List

**Type**: sterling.process
**File**: bp-append-list-02.bpml

## Description

Sterling B2B Business Process: Demo_BP_Append_List

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### has_next
- **Condition**: ``

### skip_item
- **Condition**: ``

## Operations

### 1. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `TARGET`: /ProcessData/List/Item[1]
  - `.`: {'from': '*'}


---

### Demo_BP_Append_List

# Demo_BP_Append_List

**Type**: sterling.process
**File**: bp-append-list-loop-counter.bpml

## Description

Sterling B2B Business Process: Demo_BP_Append_List

## Integration Patterns

- Batch Processing
- Conditional Logic

## Business Rules

### moreItens
- **Condition**: ``


---

### Demo_ListHandling

# Demo_ListHandling

**Type**: sterling.process
**File**: bp-work-with-lists-01.bpml

## Description

Sterling B2B Business Process: Demo_ListHandling


---

### Demo_ListHandling

# Demo_ListHandling

**Type**: sterling.process
**File**: bp-work-with-lists-01.bpml

## Description

Sterling B2B Business Process: Demo_ListHandling


---

### Demo_XML_Attributes_Elements

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


---

### MAILBOX_DELETE_FILE_RUNTASK

# MAILBOX_DELETE_FILE_RUNTASK

**Type**: sterling.process
**File**: mailbox-delete-file-runtask.bpml

## Description

Sterling B2B Business Process: MAILBOX_DELETE_FILE_RUNTASK

## Integration Patterns

- Conditional Logic

## Business Rules

### DelMsgCntGreaterZero
- **Condition**: ``

## Operations

### 1. Mailbox Delete Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: {'from': 'string(/ProcessData/This/MailboxPath)'}
  - `MessageNamePattern`: {'from': 'string(/ProcessData/This/MessageNamePattern)'}
  - `MailboxSelection`: choose
  - `MessageExtractable`: ALL

### 2. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 3. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### MAILBOX_GET_INDEX_CDP

# MAILBOX_GET_INDEX_CDP

**Type**: sterling.process
**File**: mailbox-get-index-cdp.bpml

## Description

Sterling B2B Business Process: MAILBOX_GET_INDEX_CDP

## Operations

### 1. Mailbox Query Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: /Inbox
  - `MessageExtractable`: YES
  - `MessageNamePattern`: *
  - `OrderBy`: MessageId

### 2. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/PullList
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: PullListCDP
  - `.`: {'from': '*'}

### 3. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 4. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### MAILBOX_GET_INDEX_TXT

# MAILBOX_GET_INDEX_TXT

**Type**: sterling.process
**File**: mailbox-get-index-txt.bpml

## Description

Sterling B2B Business Process: MAILBOX_GET_INDEX_TXT

## Operations

### 1. Mailbox Query Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: /Inbox
  - `MessageExtractable`: YES
  - `MessageNamePattern`: *
  - `OrderBy`: MessageId

### 2. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/PullList
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: PullListTXT
  - `.`: {'from': '*'}

### 3. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### MAILBOX_GET_INDEX_XML

# MAILBOX_GET_INDEX_XML

**Type**: sterling.process
**File**: mailbox-get-index-xml.bpml

## Description

Sterling B2B Business Process: MAILBOX_GET_INDEX_XML

## Operations

### 1. Mailbox Query Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: /Inbox
  - `MessageExtractable`: YES
  - `MessageNamePattern`: *
  - `OrderBy`: MessageId

### 2. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### MAILBOX_DELETE_FILE_RUNTASK

# MAILBOX_DELETE_FILE_RUNTASK

**Type**: sterling.process
**File**: mailbox-delete-file-runtask.bpml

## Description

Sterling B2B Business Process: MAILBOX_DELETE_FILE_RUNTASK

## Integration Patterns

- Conditional Logic

## Business Rules

### DelMsgCntGreaterZero
- **Condition**: ``

### has_mailboxpath
- **Condition**: ``

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `This/ReturnCode`: 0
  - `This/MailboxPath`: /Inbox

### 2. Mailbox Delete Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: {'from': 'string(/ProcessData/This/MailboxPath)'}
  - `MessageNamePattern`: {'from': 'string(/ProcessData/This/MessageNamePattern)'}
  - `MailboxSelection`: choose
  - `MessageExtractable`: ALL

### 3. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 4. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### MAILBOX_GET_INDEX_CDP_ADV

# MAILBOX_GET_INDEX_CDP_ADV

**Type**: sterling.process
**File**: mailbox-get-index-cdp-adv.bpml

## Description

Sterling B2B Business Process: MAILBOX_GET_INDEX_CDP_ADV

## Integration Patterns

- Conditional Logic

## Business Rules

### os_windows
- **Condition**: ``

### os_unix
- **Condition**: ``

### os_other
- **Condition**: ``

### has_filter
- **Condition**: ``

### has_mailboxpath
- **Condition**: ``

## Operations

### 1. AssignService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `This/SlashType`: \
  - `This/Dummy`: /* Dummy Comment */
  - `This/MailboxPath`: /Inbox
  - `This/MessageNamePattern`: *

### 2. Mailbox Query Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `MailboxPath`: {'from': 'This/MailboxPath/text()'}
  - `MessageExtractable`: YES
  - `MessageNamePattern`: {'from': 'This/MessageNamePattern/text()'}
  - `OrderBy`: MessageId

### 3. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/This
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: PullListCdpAdv
  - `.`: {'from': '*'}

### 4. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 5. CD Server BP Response Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### Demo_BP_Content_Based_Routing

# Demo_BP_Content_Based_Routing

**Type**: sterling.process
**File**: content-based-routing-01.bpml

## Description

Sterling B2B Business Process: Demo_BP_Content_Based_Routing

## Operations

### 1. Translation
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `map_name`: {'from': "'Demo_Map_Content_Based_Routing'"}
  - `validate_input`: NO
  - `.`: {'from': '*'}


---

### Demo_BP_Content_Based_Routing_XML

# Demo_BP_Content_Based_Routing_XML

**Type**: sterling.process
**File**: content-based-routing-02.bpml

## Description

Sterling B2B Business Process: Demo_BP_Content_Based_Routing_XML


---

### Demo_BP_CustomLayer_Consumer

# Demo_BP_CustomLayer_Consumer

**Type**: sterling.process
**File**: demo-bp-customlayer-consumer.bpml

## Description

Sterling B2B Business Process: Demo_BP_CustomLayer_Consumer

## Operations

### 1. Get Document Information Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### Demo_BP_CustomLayer_Producer

# Demo_BP_CustomLayer_Producer

**Type**: sterling.process
**File**: demo-bp-customlayer-producer.bpml

## Description

Sterling B2B Business Process: Demo_BP_CustomLayer_Producer

## Operations

### 1. Get Document Information Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### FGCustomLayer_ExecuteProcess

# FGCustomLayer_ExecuteProcess

**Type**: sterling.process
**File**: fgcustomlayer-executeprocess.bpml

## Description

Sterling B2B Business Process: FGCustomLayer_ExecuteProcess

## Operations

### 1. Invoke Sub-Process
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `INVOKE_MODE`: INLINE
  - `WFD_NAME`: {'from': '/ProcessData/BP_TO_RUN/text()'}
  - `.`: {'from': '*'}

### 2. Release Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `TARGET`: /ProcessData/DocumentId
  - `.`: {'from': '*'}

### 3. Get Document Information Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}


---

### FileGatewayCustomLayerXAPI

# FileGatewayCustomLayerXAPI

**Type**: sterling.process
**File**: xapi-import-bp.bpml

## Description

Sterling B2B Business Process: FileGatewayCustomLayerXAPI

## Operations

### 1. XAPI Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `api`: multiApi


---

### FGCustomLayer_Translation

# FGCustomLayer_Translation

**Type**: sterling.process
**File**: fgcustomlayer-translation.bpml

## Description

Sterling B2B Business Process: FGCustomLayer_Translation

## Operations

### 1. Translation
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `map_name`: {'from': '/ProcessData/Map_Name/text()'}

### 2. FileGatewayRouteEventServiceType
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteDataflowId'}
  - `EventCode`: CUST_0002
  - `ExceptionLevel`: Normal
  - `EventAttributes/Map_Name`: {'from': '/ProcessData/Map_Name/text()'}

### 3. FileGatewayRouteEventServiceType
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteDataflowId'}
  - `EventCode`: CUST_0052
  - `ExceptionLevel`: Normal
  - `EventAttributes/Map_Name`: {'from': '/ProcessData/Map_Name/text()'}


---

### FileGatewayCustomLayerXAPI

# FileGatewayCustomLayerXAPI

**Type**: sterling.process
**File**: xapi-import-bp.bpml

## Description

Sterling B2B Business Process: FileGatewayCustomLayerXAPI

## Operations

### 1. XAPI Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `api`: multiApi


---

### Demo_BP_Dynamic_ConsumerName

# Demo_BP_Dynamic_ConsumerName

**Type**: sterling.process
**File**: dynamic-consumername.bpml

## Description

Sterling B2B Business Process: Demo_BP_Dynamic_ConsumerName


---

### SFGAdvancedSearchWeb

# SFGAdvancedSearchWeb

**Type**: sterling.process
**File**: sfg-advanced-search-web.bpml

## Description

Sterling B2B Business Process: SFGAdvancedSearchWeb

## Integration Patterns

- Conditional Logic

## Business Rules

### partner_name
- **Condition**: ``

### partner_code
- **Condition**: ``

### login_id
- **Condition**: ``

### first_name
- **Condition**: ``

### last_name
- **Condition**: ``

### first_name_last_name
- **Condition**: ``

### no_parameters
- **Condition**: ``

### is_new_page
- **Condition**: ``

### has_results
- **Condition**: ``

## Operations

### 1. Lightweight JDBC Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}
  - `pool`: db2Pool
  - `query_type`: SELECT
  - `result_name`: Result1
  - `row_name`: Row1
  - `sql`: {'from': '/ProcessData/This/sql/text()'}

### 2. XSLT Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `input_pd_xpath`: /ProcessData/ResponseData
  - `xml_input_from`: ProcData
  - `xml_input_validation`: NO
  - `xslt_name`: SFGAdvancedSearch
  - `.`: {'from': '*'}

### 3. HttpRespond
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `doc-has-headers`: false
  - `.`: {'from': '*'}


---

### Demo_BP_Consumer_Broadcast_List

# Demo_BP_Consumer_Broadcast_List

**Type**: sterling.process
**File**: consumers-broadcast-list.bpml

## Description

Sterling B2B Business Process: Demo_BP_Consumer_Broadcast_List


---

### Demo_BP_RouteViaCustomFTP

# Demo_BP_RouteViaCustomFTP

**Type**: sterling.process
**File**: route-via-custom-ftp.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaCustomFTP

## Integration Patterns

- Conditional Logic

## Business Rules

### renameFile?
- **Condition**: ``

### changeDirectory?
- **Condition**: ``

## Operations

### 1. Obscure Password
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': '*'}

### 2. FTP BEGIN SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `FTPClientAdapter`: FTPClientAdapter
  - `RemoteHost`: {'from': '/ProcessData/customftp_RemoteHost/text()'}
  - `RemotePort`: {'from': '/ProcessData/customftp_RemotePort/text()'}
  - `RemoteUserId`: {'from': '/ProcessData/customftp_RemoteUserId/text()'}
  - `RemotePasswd`: {'from': 'revealObscured(/ProcessData/Demo_Remote_FTP)'}
  - `UsingRevealedPasswd`: true
  - `ConnectionRetries`: {'from': '/ProcessData/customftp_NoOfRetries/text()'}
  - `RetryDelay`: {'from': '/ProcessData/customftp_RetriesInterval/text()'}
  - `ResponseTimeout`: {'from': '/ProcessData/ResponseTimeout/text()'}
  - `ClearControlChannel`: {'from': '/ProcessData/ClearControlChannel/text()'}
  - `.`: {'from': '*'}

### 3. changeDir
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}
  - `Directory`: {'from': '/ProcessData/FtpBeginSessionServiceResults/TPProfile/Directory/text()'}

### 4. FTP PUT SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RepresentationType`: BINARY
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}
  - `.`: {'from': '*'}

### 5. moveFile
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RemoteFromFileName`: {'from': 'string(RemoteFileName)'}
  - `RemoteToFileName`: {'from': 'substring-after(string(RemoteFileName),string(TempPrefix))'}
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}

### 6. FTP END SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}

### 7. FTP END SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/FtpBeginSessionServiceResults/SessionToken/text()'}

### 8. generateException
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `exceptionCode`: Error, FTP PUT
  - `.`: {'from': '*'}


---

### Demo_BP_RouteViaCustomProtocol

# Demo_BP_RouteViaCustomProtocol

**Type**: sterling.process
**File**: route-via-custom-protocol.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaCustomProtocol

## Operations

### 1. Get_Current_Time
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `action`: {'from': "'current_time'"}
  - `format`: yyyy-MM-dd.HH-mm-ss-SSS

### 2. File System Adapter
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `extractionFolder`: /home/siuser/CustomProtocol
  - `assignFilename`: true
  - `assignedFilename`: {'from': 'DestinationMessageName/text()'}
  - `Action`: FS_EXTRACT
  - `.`: {'from': '*'}

### 3. FileGatewayRouteEventService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteMetadata'}
  - `EventCode`: CUST_0003
  - `ExceptionLevel`: Normal
  - `EventAttributes/ProducerName`: {'from': 'ProducerName/text()'}
  - `EventAttributes/ConsumerFilename`: {'from': 'DestinationMessageName/text()'}

### 4. FileGatewayRouteEventService
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `.`: {'from': 'RouteMetadata'}
  - `EventCode`: CUST_0053
  - `ExceptionLevel`: Normal
  - `EventAttributes/ProducerName`: {'from': 'ProducerName/text()'}
  - `EventAttributes/ConsumerFilename`: {'from': 'DestinationMessageName/text()'}


---

### Demo_BP_RouteViaCustomSFTP

# Demo_BP_RouteViaCustomSFTP

**Type**: sterling.process
**File**: route-via-custom-sftp.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaCustomSFTP

## Integration Patterns

- Conditional Logic

## Business Rules

### changeDirectory?
- **Condition**: ``

## Operations

### 1. SFTP BEGIN SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SFTPClientAdapter`: {'from': '/ProcessData/customsftp_SFTPClientAdapter/text()'}
  - `ProfileId`: {'from': '/ProcessData/customsftp_ProfileId/text()'}
  - `.`: {'from': '*'}

### 2. changeDir
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '/ProcessData/SftpBeginSessionServiceResults/SessionToken/text()'}
  - `Directory`: {'from': '/ProcessData/SftpBeginSessionServiceResults/TPProfile/Directory/text()'}

### 3. SFTP PUT SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': 'SftpBeginSessionServiceResults/SessionToken/text()'}
  - `RemoteFileName`: {'from': 'DestinationMessageName/text()'}
  - `.`: {'from': '*'}

### 4. SFTP END SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': 'SftpBeginSessionServiceResults/SessionToken/text()'}

### 5. SFTP END SESSION SERVICE
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': 'SftpBeginSessionServiceResults/SessionToken/text()'}
  - `.`: {'from': 'ResponseTimeout'}

### 6. generateException
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `exceptionCode`: Error, SFTP PUT
  - `.`: {'from': '*'}


---

### Demo_BP_RouteViaFileSystem

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


---

### Demo_BP_RouteViaHttpPost

# Demo_BP_RouteViaHttpPost

**Type**: sterling.process
**File**: route-via-http-post.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaHttpPost

## Operations

### 1. HTTP Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `HTTPClientAdapter`: HTTPClientAdapter
  - `RemoteHost`: {'from': 'customhttp_RemoteHost/text()'}
  - `RemotePort`: {'from': 'customhttp_RemotePort/text()'}
  - `SSL`: Must
  - `CACertificateId`: {'from': 'customhttp_CertID/text()'}
  - `CipherStrength`: All
  - `.`: {'from': '*'}

### 2. HTTP Client POST Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `RawRequest`: false
  - `RawResponse`: false
  - `ResponseTimeout`: 1500
  - `SessionToken`: {'from': '//SessionToken/text()'}
  - `ShowResponseCode`: true
  - `URI`: {'from': 'customhttp_URI/text()'}
  - `.`: {'from': '*'}

### 3. HTTP Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionToken`: {'from': '//SessionToken/text()'}
  - `.`: {'from': '*'}


---

### Demo_BP_RouteViaKafka

# Demo_BP_RouteViaKafka

**Type**: sterling.process
**File**: route-via-kafka.bpml

## Description

Sterling B2B Business Process: Demo_BP_RouteViaKafka

## Operations

### 1. Kafka Client Begin Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `Action`: put
  - `BootStrapServers`: {'from': '//customkafka_BootStrapServers/text()'}
  - `KafkaClientAdapter`: {'from': '//customkafka_KafkaClientAdapter/text()'}
  - `SecurityAction`: {'from': '//customkafka_SecurityAction/text()'}
  - `ProducerConfig`: {'from': '//customkafka_ProducerConfig/text()'}
  - `.`: {'from': 'PrimaryDocument'}

### 2. Kafka Client Producer Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Topic`: {'from': '//customkafka_Topic/text()'}
  - `.`: {'from': 'PrimaryDocument'}

### 3. Kafka Client End Session Service
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `SessionID`: {'from': '//KafkaBeginSessionServiceResults/SessionID/text()'}
  - `KafkaClientAdapter`: {'from': '//KafkaBeginSessionServiceResults/KafkaClientAdapter/text()'}
  - `Action`: put


---

### Demo_BP_Content_Based_Routing

# Demo_BP_Content_Based_Routing

**Type**: sterling.process
**File**: content-based-routing-01.bpml

## Description

Sterling B2B Business Process: Demo_BP_Content_Based_Routing

## Operations

### 1. Translation
- **Participant**: 
- **Type**: service
- **Configuration**:
  - `map_name`: {'from': "'Demo_Map_Content_Based_Routing'"}
  - `validate_input`: NO
  - `.`: {'from': '*'}


---

## Data Maps (MXL)

### Demo_Map_Content_Based_Routing

# Demo_Map_Content_Based_Routing

**Type**: sterling.map
**File**: Demo_Map_Content_Based_Routing.mxl
**Author**: 

## Description




---

### Demo_Map_TranslationLayer

# Demo_Map_TranslationLayer

**Type**: sterling.map
**File**: Demo_Map_TranslationLayer.mxl
**Author**: 

## Description




---

### Demo_Map_Content_Based_Routing

# Demo_Map_Content_Based_Routing

**Type**: sterling.map
**File**: Demo_Map_Content_Based_Routing.mxl
**Author**: 

## Description




---

### MapPos2CsvSample01

# MapPos2CsvSample01

**Type**: sterling.map
**File**: MapPos2CsvSample01.mxl
**Author**: 

## Description




---

