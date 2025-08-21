# Boomi Process: EC372 - EC to NAVEX (OB) + Sub: Extract Data

## Process Overview

This Boomi integration process contains 3 components:

1. **EC372 - EC to NAVEX (OB)** (process) - Version 75
   - Location: PepsiCo/2.0 Development/2.1 Global Integrations/EC372 - EC to NAVEX (OB)
2. **Sub: Extract Data** (process) - Version 83
   - Location: PepsiCo/2.0 Development/2.1 Global Integrations/EC372 - EC to NAVEX (OB)
3. **Sub: SFTP to Pepsi and NAVEX** (process) - Version 4
   - Location: PepsiCo/2.0 Development/2.1 Global Integrations/EC372 - EC to NAVEX (OB)

## 🔧 Process Properties Configuration

These properties control the business logic and behavior of the integration:

### Archive path on SFTP server
- **Description**: Path for archiving processed files on SFTP server
- **Property Key**: `6c4f4625-a39d-4368-b986-85499c5dd7d2`

### Employee Status
- **Description**: Filter for employee status (Active, Terminated, etc.)
- **Property Key**: `6236f705-e6ba-4f9c-8dcf-bacffe65d640`
- **Overrideable**: true

### Encrypt Archive File
- **Description**: Controls PGP encryption of archived files
- **Property Key**: `60304a50-7a2a-412a-932c-db44d28dbdc4`

### FileType
- **Description**: Type of file processing (Delta, Full, etc.)
- **Property Key**: `d0c9f73d-8faa-47c1-adda-3abd94033ac9`

### Filter_EmployeeClass
- **Description**: Employee class filter for role-based data extraction
- **Property Key**: `5373d17c-a180-4aab-bc91-e91f8689b86c`
- **Overrideable**: true

### Filter_GPID
- **Description**: Global Person ID filter for employee identification
- **Property Key**: `c7175bc9-9ed8-4da3-97ad-e2147208110f`
- **Overrideable**: true

### Filter_LSRD
- **Description**: Filter for Last Successful Run Date - controls delta vs full extraction
- **Property Key**: `bdf17f77-c75b-4777-bc49-2ce59e2286d9`

### Filter_LegalEntity
- **Description**: Legal entity filter for organizational data separation
- **Property Key**: `8caddbc7-67c5-41dc-afb1-ce06fa7d9e8e`
- **Overrideable**: true

### Filter_company_territory_code
- **Description**: Territory code filter for geographical data filtering
- **Property Key**: `a92b59a7-bbfb-4ee5-8a4c-e32d7727fbb4`
- **Overrideable**: true

### Full File Start Date
- **Description**: Start date for full file extraction mode
- **Property Key**: `2d3d973b-7bee-4b79-9512-f52a5021a00e`
- **Overrideable**: true

### NAVEXSFTPDirectory
- **Description**: Target directory path for NAVEX SFTP delivery
- **Property Key**: `729bf863-ed8a-4863-85e7-f6a69f337c8b`

### Send Output To Vendor ?
- **Description**: Controls whether output files are sent to external vendor
- **Property Key**: `9649296e-66e0-4bf8-9041-cd438ad4167b`

### SendFilesToPepsoSFTP
- **Description**: Controls whether files are archived to PepsiCo SFTP
- **Property Key**: `b2157951-1c8b-4e53-96fe-70de4e1be1b3`

### fromEmailAddressForErrors
- **Description**: Source email address for error notifications
- **Property Key**: `a6b2e057-49d9-4cbc-9c94-16fe27cf011b`

### fromEmailAddressForSuccess
- **Description**: Source email address for success notifications
- **Property Key**: `9a653915-1d4f-464a-b613-f20c8958f652`

### toEmailAddressForErrors
- **Description**: Destination email address for error notifications
- **Property Key**: `630bd0e1-a257-4ac9-b3c6-b4213140f7ff`

### toEmailAddressForSuccess
- **Description**: Destination email address for success notifications
- **Property Key**: `e6c11e22-d87f-4570-975b-f39b8012be6e`

## 🔐 Security Configuration

Encryption and security settings:

### PGP Keys (EC372 - EC to NAVEX (OB))
- **PGP Public Key- EC-372 NAVEX**
  - Purpose: NAVEX vendor encryption key for secure file delivery
  - Overrideable: true
- **SF Integrations - Pepsi (QA Pub Key)**
  - Purpose: PepsiCo internal encryption key for QA environment
  - Overrideable: true

### PGP Encryption (Sub: SFTP to Pepsi and NAVEX)
- **Purpose**: PGP encryption for sensitive data protection
- **Encryption Alias**: `d0c6be56-2fd3-454e-8aa0-22fa190c97a9`
- **Clear Sign**: true

## 🔄 Process Flow Details

Business logic and decision points:

### Decision Points
- **Filter LSRD is NULL **
  - Logic: equals comparison
  - Purpose: Business decision: Filter LSRD is NULL 

- **Delta Run?**
  - Logic: equals comparison
  - Purpose: Determines extraction type - incremental vs full data pull

- **end_date_check**
  - Logic: equals comparison
  - Purpose: Business decision: end_date_check

- **Send Files to Vendor?**
  - Logic: equals comparison
  - Purpose: Business decision: Send Files to Vendor?

- **Send Files to Pepsico SFTP?**
  - Logic: equals comparison
  - Purpose: Business decision: Send Files to Pepsico SFTP?

- **Encrypt Archive File**
  - Logic: equals comparison
  - Purpose: Business decision: Encrypt Archive File

### Parallel Processing
- ****
  - Branches: 5 parallel paths
  - Purpose: Parallel processing with 5 branches

- ****
  - Branches: 2 parallel paths
  - Purpose: Parallel processing with 2 branches

- ****
  - Branches: 2 parallel paths
  - Purpose: Parallel processing with 2 branches

- ****
  - Branches: 2 parallel paths
  - Purpose: Parallel processing with 2 branches

- ****
  - Branches: 2 parallel paths
  - Purpose: Parallel processing with 2 branches

- ****
  - Branches: 2 parallel paths
  - Purpose: Parallel processing with 2 branches

- ****
  - Branches: 2 parallel paths
  - Purpose: Parallel processing with 2 branches

### Document Properties
- **SetLastSuccessRunDate**
  - Properties Set: 5 dynamic properties
    - Dynamic Process Property - SDATE
    - Dynamic Process Property - EDATE
    - Dynamic Process Property - LSRD
    - ... and 2 more properties

- **SetLastSuccessRunDate**
  - Properties Set: 5 dynamic properties
    - Dynamic Process Property - SDATE
    - Dynamic Process Property - EDATE
    - Dynamic Process Property - LSRD
    - ... and 2 more properties

- **Set SFTP fileName**
  - Properties Set: 2 dynamic properties
    - SFTP - File Name
    - Dynamic Process Property - DPP_FileName

- **Set extensions**
  - Properties Set: 3 dynamic properties
    - Dynamic Process Property - EDATE
    - Dynamic Process Property - DemographicTotalCount
    - Dynamic Process Property - DemographicErrorCount

- **Error Message Details**
  - Properties Set: 9 dynamic properties
    - Mail - File Name
    - Mail - Subject
    - Mail - From Address
    - ... and 6 more properties

- **Set Error Record Count Property**
  - Properties Set: 4 dynamic properties
    - Dynamic Process Property - RPT_ERR_PRCSS_NAME
    - Dynamic Process Property - RPT_ERR_CPNT_TYPE
    - Dynamic Process Property - RPT_ERR_FILE_NAME
    - ... and 1 more properties

- **Set Error Message Properties**
  - Properties Set: 5 dynamic properties
    - Dynamic Process Property - RPT_ERR_MSG_FRGMNT_FLAG
    - Dynamic Process Property - RPT_ERR_MSG_BRULE_PROF_TYPE
    - Dynamic Process Property - RPT_ERR_MSG_BRULE_KEY_DATA_DELIM
    - ... and 2 more properties

- **Set Success Counts PCR**
  - Properties Set: 4 dynamic properties
    - Dynamic Process Property - RPT_SUC_PRCSS_NAME
    - Dynamic Process Property - RPT_SUC_FILE_NAME
    - Dynamic Process Property - RPT_SUC_REC_TYPE
    - ... and 1 more properties

- **Set FileName**
  - Properties Set: 1 dynamic properties
    - Dynamic Process Property - File_Name

- **Set NAVEX Directory**
  - Properties Set: 1 dynamic properties
    - SFTP - Remote Directory

- **Set Remote Directory for Archive file**
  - Properties Set: 1 dynamic properties
    - SFTP - Remote Directory

- **Set Mail Properties for successful file transfer**
  - Properties Set: 4 dynamic properties
    - Mail - From Address
    - Mail - To Address
    - Mail - Subject
    - ... and 1 more properties


## Component 1: EC372 - EC to NAVEX (OB)

**Type**: process

### XML Configuration

```xml
<?xml version="1.0" ?>
<bns:Component xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bns="http://api.platform.boomi.com/" folderFullPath="PepsiCo/2.0 Development/2.1 Global Integrations/EC372 - EC to NAVEX (OB)" componentId="3c0b145b-dd1a-45f4-9289-9aaf7d592a9a" version="75" name="EC372 - EC to NAVEX (OB)" type="process" createdDate="2018-04-11T03:58:42Z" createdBy="Deep.Singh.Chauhan@accenture.com" modifiedDate="2022-02-16T13:41:22Z" modifiedBy="Geetanjali.Kumari.Contractor@pepsico.com" deleted="false" currentVersion="true" folderName="EC372 - EC to NAVEX (OB)" folderId="RjoxOTM3OTEx" branchName="main" branchId="QjoyOTk5NDY">
  <bns:encryptedValues/>
  <bns:description/>
  <bns:object>
    <process xmlns="" allowSimultaneous="false" enableUserLog="false" processLogOnErrorOnly="false" purgeDataImmediately="false" updateRunDates="true" workload="general">
      <shapes>
        <shape image="start" name="shape1" shapetype="start" userlabel="" x="16.0" y="400.0">
          <configuration>
            <noaction/>
          </configuration>
          <dragpoints>
            <dragpoint name="shape1.dragpoint1" toShape="shape15" x="96.0" y="409.0">
              <linesegment length="0" name="shape1.dragpoint1.lineseg1" orient="horizontal" x="50.0" y="415.0"/>
              <linesegment length="0" name="shape1.dragpoint1.lineseg2" orient="vertical" x="50.0" y="415.0"/>
              <linesegment length="31" name="shape1.dragpoint1.lineseg3" orient="horizontal" x="50.0" y="415.0"/>
              <linesegment length="0" name="shape1.dragpoint1.lineseg4" orient="vertical" x="81.0" y="415.0"/>
              <linesegment length="15" name="shape1.dragpoint1.lineseg5" orient="horizontal" x="81.0" y="415.0"/>
            </dragpoint>
          </dragpoints>
        </shape>
        <shape image="decision_icon" name="shape3" shapetype="decision" userlabel="Filter LSRD is NULL " x="256.0" y="304.0">
          <configuration>
            <decision comparison="equals" na
<!-- Content truncated for brevity -->

```

## Component 2: Sub: Extract Data

**Type**: process

### XML Configuration

```xml
<?xml version="1.0" ?>
<bns:Component xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bns="http://api.platform.boomi.com/" folderFullPath="PepsiCo/2.0 Development/2.1 Global Integrations/EC372 - EC to NAVEX (OB)" componentId="4fef22a1-66b8-4874-bab0-74afe13bed36" version="83" name="Sub: Extract Data" type="process" createdDate="2018-04-11T09:20:21Z" createdBy="Deep.Singh.Chauhan@accenture.com" modifiedDate="2024-08-29T11:10:08Z" modifiedBy="bittu.kumar.contractor@pepsico.com" deleted="false" currentVersion="true" folderName="EC372 - EC to NAVEX (OB)" folderId="RjoxOTM3OTEx" branchName="main" branchId="QjoyOTk5NDY">
  <bns:encryptedValues/>
  <bns:description/>
  <bns:object>
    <process xmlns="" allowSimultaneous="false" enableUserLog="false" processLogOnErrorOnly="false" purgeDataImmediately="false" updateRunDates="false" workload="general">
      <shapes>
        <shape image="start" name="shape1" shapetype="start" userlabel="Start" x="64.0" y="240.0">
          <configuration>
            <passthroughaction/>
          </configuration>
          <dragpoints>
            <dragpoint name="shape1.dragpoint1" toShape="shape3" x="160.0" y="248.0"/>
          </dragpoints>
        </shape>
        <shape image="connectoraction_icon" name="shape2" shapetype="connectoraction" userlabel="" x="319.0" y="240.0">
          <configuration>
            <connectoraction actionType="QUERY" connectionId="8748a325-5df6-46f4-a828-4f9e1d5e4398" connectorType="successfactorsmaster-Q2Q93V-SFSF-priv_prod" hideSettings="false" operationId="7d3dbaf9-b9f0-4700-810f-df85841cb4b6" parameter-profile="EMBEDDED|genericparameterchooser|7d3dbaf9-b9f0-4700-810f-df85841cb4b6">
              <parameters/>
            </connectoraction>
          </configuration>
          <dragpoints>
            <dragpoint name="shape2.dragpoint1" toShape="shape5" x="511.0" y="248.0"/>
          </dragpoints>
        </shape>
        <shape image="branch_icon" name="shape3" shapetype="branch" userlabe
<!-- Content truncated for brevity -->

```

## Component 3: Sub: SFTP to Pepsi and NAVEX

**Type**: process

### XML Configuration

```xml
<?xml version="1.0" ?>
<bns:Component xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bns="http://api.platform.boomi.com/" folderFullPath="PepsiCo/2.0 Development/2.1 Global Integrations/EC372 - EC to NAVEX (OB)" componentId="31a87c8f-19d7-4288-a6c7-929e94724a6a" version="4" name="Sub: SFTP to Pepsi and NAVEX" type="process" createdDate="2018-04-25T10:42:51Z" createdBy="Deep.Singh.Chauhan@accenture.com" modifiedDate="2018-05-03T07:40:06Z" modifiedBy="Deep.Singh.Chauhan@accenture.com" deleted="false" currentVersion="true" folderName="EC372 - EC to NAVEX (OB)" folderId="RjoxOTM3OTEx" branchName="main" branchId="QjoyOTk5NDY">
  <bns:encryptedValues/>
  <bns:description/>
  <bns:object>
    <process xmlns="" allowSimultaneous="false" enableUserLog="false" processLogOnErrorOnly="false" purgeDataImmediately="false" updateRunDates="false" workload="general">
      <shapes>
        <shape image="start" name="shape1" shapetype="start" userlabel="Start" x="80.0" y="176.0">
          <configuration>
            <passthroughaction/>
          </configuration>
          <dragpoints>
            <dragpoint name="shape1.dragpoint1" toShape="shape7" x="224.0" y="184.0">
              <linesegment length="0" name="shape1.dragpoint1.lineseg1" orient="horizontal" x="113.0" y="190.0"/>
              <linesegment length="0" name="shape1.dragpoint1.lineseg2" orient="vertical" x="113.0" y="190.0"/>
              <linesegment length="63" name="shape1.dragpoint1.lineseg3" orient="horizontal" x="113.0" y="190.0"/>
              <linesegment length="0" name="shape1.dragpoint1.lineseg4" orient="vertical" x="176.0" y="190.0"/>
              <linesegment length="48" name="shape1.dragpoint1.lineseg5" orient="horizontal" x="176.0" y="190.0"/>
            </dragpoint>
          </dragpoints>
        </shape>
        <shape image="catcherrors_icon" name="shape5" shapetype="catcherrors" userlabel="" x="832.0" y="480.0">
          <configuration>
            <catcherrors catchAll="true" re
<!-- Content truncated for brevity -->

```

