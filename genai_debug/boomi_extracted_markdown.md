# Boomi Process: Subscription Completed JSON to SF Opportunity CREATE Request XML + SF Opportunity CREATE Operation

## Process Overview

This Boomi integration process contains 2 components:

1. **Subscription Completed JSON to SF Opportunity CREATE Request XML** (transform.map)
2. **SF Opportunity CREATE Operation** (connector-action)

## Component 1: Subscription Completed JSON to SF Opportunity CREATE Request XML

**Type**: transform.map
**Description**: For more details, see here: https://community.boomi.com/s/article/Create-Salesforce-Opportunities-from-Stripe-Subscriptions

### Data Mappings

- **Opportunity/Description**: Mapped from function
- **Opportunity/Name**: Mapped from function
- **Opportunity/CloseDate**: Mapped from function

### Functions

- **Get Document Property** (DocumentPropertyGet)
  - Property: Dynamic Document Property - DDP_SalesforceDescription
- **Get Document Property** (DocumentPropertyGet)
  - Property: Dynamic Document Property - DDP_CustomerName
- **Get Document Property** (DocumentPropertyGet)
  - Property: Dynamic Document Property - DDP_CloseDate

### XML Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?><Component xmlns:bns="http://api.platform.boomi.com/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" branchId="Qjo1MDE0MTU" branchName="main" componentId="cbb5a23f-5904-4fb9-a7dc-9e7062d2b268" copiedFromComponentId="ea5bc16f-15e4-405b-95a4-9c147d310910" copiedFromComponentVersion="8" createdBy="deepan@itresonance.com" createdDate="2025-06-05T11:22:10Z" currentVersion="true" deleted="false" folderFullPath="IT Resonance/Create Salesforce Opportunities from Stripe Subscriptions_2025-06-05-11:22:02" folderId="Rjo3NzA2ODk1" folderName="Create Salesforce Opportunities from Stripe Subscriptions_2025-06-05-11:22:02" modifiedBy="deepan@itresonance.com" modifiedDate="2025-06-05T11:22:10Z" name="Subscription Completed JSON to SF Opportunity CREATE Request XML" type="transform.map" version="1">
  <bns:encryptedValues/>
  <bns:description>For more details, see here: https://community.boomi.com/s/article/Create-Salesforce-Opportunities-from-Stripe-Subscriptions</bns:description>
  <bns:object>
    <Map fromProfile="6e791dfd-6dad-469a-9bd7-5339e240cca2" toProfile="efd69737-e49c-4a38-bb32-abb39383ed5f">
      <Mappings>
        <Mapping fromFunction="2" fromKey="3" fromType="function" toKey="5" toKeyPath="*[@key='1']/*[@key='5']" toNamePath="Opportunity/Description" toType="profile"/>
        <Mapping fromFunction="3" fromKey="3" fromType="function" toKey="4" toKeyPath="*[@key='1']/*[@key='4']" toNamePath="Opportunity/Name" toType="profile"/>
        <Mapping fromFunction="4" fromKey="3" fromType="function" toKey="10" toKeyPath="*[@key='1']/*[@key='10']" toNamePath="Opportunity/CloseDate" toType="profile"/>
      </Mappings>
      <Functions optimizeExecutionOrder="true">
        <FunctionStep cacheEnabled="true" category="ProcessProperty" key="2" name="Get Document Property" position="2" sumEnabled="false" type="DocumentPropertyGet" x="10.0" y="10.0">
          <Inputs/>
          <Outputs>
            <Output key="3" name="Dynamic Docu
<!-- Content truncated for brevity -->

```

## Component 2: SF Opportunity CREATE Operation

**Type**: connector-action
**Subtype**: salesforce
**Description**: For more details, see here: https://community.boomi.com/s/article/Create-Salesforce-Opportunities-from-Stripe-Subscriptions

### Operations

**Salesforce CREATE Operation**

- **Object**: Opportunity
- **Action**: create
- **Batch Size**: 10

**Fields** (21 total):
- AccountId (reference)
- IsPrivate (boolean)
- Name (character)
- Description (character)
- StageName (character)
- Amount (number)
- Probability (number)
- TotalOpportunityQuantity (number)
- CloseDate (date)
- Type (character)
- ... and 11 more fields

### XML Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?><Component xmlns:bns="http://api.platform.boomi.com/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" branchId="Qjo1MDE0MTU" branchName="main" componentId="22d84e3e-6a7f-4c9d-9757-67177bc97a19" copiedFromComponentId="4672357a-1565-4100-85a0-3496ea1cb3da" copiedFromComponentVersion="6" createdBy="deepan@itresonance.com" createdDate="2025-06-05T11:22:11Z" currentVersion="true" deleted="false" folderFullPath="IT Resonance/Create Salesforce Opportunities from Stripe Subscriptions_2025-06-05-11:22:02" folderId="Rjo3NzA2ODk1" folderName="Create Salesforce Opportunities from Stripe Subscriptions_2025-06-05-11:22:02" modifiedBy="deepan@itresonance.com" modifiedDate="2025-06-05T11:22:11Z" name="SF Opportunity CREATE Operation" subType="salesforce" type="connector-action" version="1">
  <bns:encryptedValues/>
  <bns:description>For more details, see here: https://community.boomi.com/s/article/Create-Salesforce-Opportunities-from-Stripe-Subscriptions</bns:description>
  <bns:object>
    <Operation>
      <Archiving directory="" enabled="false"/>
      <Configuration>
        <SalesforceSendAction batchCount="200" batchSize="10" bulkAPIVersion="None" objectAction="create" objectName="Opportunity" requestProfile="efd69737-e49c-4a38-bb32-abb39383ed5f" returnApplicationErrors="false" useBulkAPI="false">
          <Options>
            <Fields>
              <SalesforceObject checkable="false" externalIdField="Choose..." import="true" level="0" name="Opportunity" objectAction="create" objectType="Opportunity">
                <FieldList name="FieldList">
                  <SalesforceField custom="false" dataType="reference" fEnabled="true" name="AccountId" nillable="true">
                    <references relationshipName="Account" useExternalId="false">
                      <referenceTo objectType="Account">
                        <referenceField custom="false" dataType="character" name="Id"/>
                      </referenceTo>
      
<!-- Content truncated for brevity -->

```

