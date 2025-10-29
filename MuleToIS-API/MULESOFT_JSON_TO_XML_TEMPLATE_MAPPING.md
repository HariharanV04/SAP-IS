# MuleSoft JSON to XML Template Mapping Reference

## 🎯 **Complete Developer Guide: MuleSoft JSON Components → SAP Integration Suite XML Templates**

This document provides a comprehensive mapping of MuleSoft JSON component structures to their corresponding XML templates in the SAP Integration Suite iFlow generation system, specifically optimized for MuleSoft migrations.

**📅 Last Updated:** Based on MuleSoft-specific template implementation  
**🔧 Status:** All templates updated for MuleSoft to SAP Integration Suite migrations  
**✅ Verified:** Templates generate components that are visible and functional after SAP Integration Suite import  

---

## 📋 **MuleSoft Component JSON Structure**

### **Standard MuleSoft Component JSON Format**
```json
{
  "type": "mulesoft_component_type",
  "name": "Component_Name",
  "id": "component_id",
  "config": {
    "property1": "value1",
    "property2": "value2"
  },
  "mulesoft_origin": "original_mulesoft_component"
}
```

---

## 🔄 **Core MuleSoft Component Mappings**

### **1. HTTP Listener Component**

#### **JSON Input:**
```json
{
  "type": "https_sender",
  "name": "Customer_API_Listener",
  "id": "http_listener_1",
  "config": {
    "url_path": "/api/customers",
    "sender_auth": "RoleBased",
    "user_role": "ESBMessaging.send",
    "enable_cors": "true"
  },
  "mulesoft_origin": "http:listener"
}
```

#### **Generated XML:**
```xml
<bpmn2:messageFlow id="http_listener_1" name="HTTP Listener" sourceRef="Participant_1" targetRef="StartEvent_2">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ComponentType</key>
            <value>HTTP</value>
        </ifl:property>
        <ifl:property>
            <key>Description</key>
            <value>MuleSoft HTTP Listener equivalent - Customer_API_Listener</value>
        </ifl:property>
        <ifl:property>
            <key>address</key>
            <value>/api/customers</value>
        </ifl:property>
        <ifl:property>
            <key>allowedMethods</key>
            <value>GET</value>
        </ifl:property>
        <ifl:property>
            <key>corsEnabled</key>
            <value>true</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>
```

### **2. HTTP Request Component**

#### **JSON Input:**
```json
{
  "type": "http_receiver",
  "name": "External_API_Call",
  "id": "http_request_1",
  "config": {
    "address": "https://api.external.com/data",
    "http_method": "GET",
    "timeout": "30000",
    "auth_method": "OAuth"
  },
  "mulesoft_origin": "http:request"
}
```

#### **Generated XML:**
```xml
<bpmn2:messageFlow id="http_request_1" name="HTTP Request" sourceRef="ServiceTask_1" targetRef="Participant_External">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ComponentType</key>
            <value>HTTP</value>
        </ifl:property>
        <ifl:property>
            <key>Description</key>
            <value>MuleSoft HTTP Request equivalent - External_API_Call</value>
        </ifl:property>
        <ifl:property>
            <key>address</key>
            <value>https://api.external.com/data</value>
        </ifl:property>
        <ifl:property>
            <key>httpMethod</key>
            <value>GET</value>
        </ifl:property>
        <ifl:property>
            <key>httpRequestTimeout</key>
            <value>30000</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>
```

### **3. Transform Message Component**

#### **JSON Input:**
```json
{
  "type": "groovy_script",
  "name": "Customer_Data_Transform",
  "id": "transform_1",
  "config": {
    "script_function": "processData",
    "script_content": "// MuleSoft Transform Message equivalent\ndef json = new groovy.json.JsonSlurper().parseText(message.getBody(String))\ndef result = [\n    customerId: json.id,\n    customerName: json.name\n]\nmessage.setBody(new groovy.json.JsonBuilder(result).toString())\nreturn message",
    "output_format": "application/json"
  },
  "mulesoft_origin": "transform"
}
```

#### **Generated XML:**
```xml
<bpmn2:callActivity id="transform_1" name="Customer_Data_Transform">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>scriptFunction</key>
            <value>processData</value>
        </ifl:property>
        <ifl:property>
            <key>script</key>
            <value>// MuleSoft Transform Message equivalent
def json = new groovy.json.JsonSlurper().parseText(message.getBody(String))
def result = [
    customerId: json.id,
    customerName: json.name
]
message.setBody(new groovy.json.JsonBuilder(result).toString())
return message</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Script</value>
        </ifl:property>
        <ifl:property>
            <key>outputFormat</key>
            <value>application/json</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>SequenceFlow_In</bpmn2:incoming>
    <bpmn2:outgoing>SequenceFlow_Out</bpmn2:outgoing>
</bpmn2:callActivity>
```

### **4. Choice Router Component**

#### **JSON Input:**
```json
{
  "type": "router",
  "name": "Customer_Type_Router",
  "id": "choice_1",
  "config": {
    "conditions": [
      {
        "expression": "${property.customerType} = 'premium'",
        "flow": "premium_route"
      },
      {
        "expression": "true",
        "flow": "standard_route"
      }
    ]
  },
  "mulesoft_origin": "choice"
}
```

#### **Generated XML:**
```xml
<bpmn2:exclusiveGateway id="choice_1" name="Customer_Type_Router">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>activityType</key>
            <value>Router</value>
        </ifl:property>
        <ifl:property>
            <key>condition_0</key>
            <value>${property.customerType} = 'premium'</value>
        </ifl:property>
        <ifl:property>
            <key>route_0</key>
            <value>premium_route</value>
        </ifl:property>
        <ifl:property>
            <key>condition_1</key>
            <value>true</value>
        </ifl:property>
        <ifl:property>
            <key>route_1</key>
            <value>standard_route</value>
        </ifl:property>
        <ifl:property>
            <key>otherwiseRoute</key>
            <value>standard_route</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>SequenceFlow_In</bpmn2:incoming>
    <bpmn2:outgoing>SequenceFlow_Premium</bpmn2:outgoing>
    <bpmn2:outgoing>SequenceFlow_Standard</bpmn2:outgoing>
</bpmn2:exclusiveGateway>
```

### **5. Salesforce Connector Component**

#### **JSON Input:**
```json
{
  "type": "request_reply",
  "name": "Salesforce_Account_Query",
  "id": "sf_query_1",
  "receiver_adapter": {
    "type": "odata_adapter",
    "operation": "Query(GET)",
    "service_url": "https://your-instance.salesforce.com/services/data/v52.0",
    "entity_set": "Account",
    "resource_path": "sobjects/Account"
  },
  "config": {
    "auth_method": "OAuth",
    "credential_name": "Salesforce_Credentials"
  },
  "mulesoft_origin": "salesforce:query"
}
```

#### **Generated XML Components:**

**Service Task:**
```xml
<bpmn2:serviceTask id="sf_query_1" name="Salesforce_Account_Query">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>activityType</key>
            <value>ExternalCall</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>SequenceFlow_In</bpmn2:incoming>
    <bpmn2:outgoing>SequenceFlow_Out</bpmn2:outgoing>
</bpmn2:serviceTask>
```

**Participant:**
```xml
<bpmn2:participant id="Participant_Salesforce" ifl:type="EndpointRecevier" name="Salesforce_Account_Query">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointRecevier</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>
```

**Message Flow:**
```xml
<bpmn2:messageFlow id="MessageFlow_Salesforce" name="Salesforce OData" sourceRef="sf_query_1" targetRef="Participant_Salesforce">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ComponentType</key>
            <value>HCIOData</value>
        </ifl:property>
        <ifl:property>
            <key>address</key>
            <value>https://your-instance.salesforce.com/services/data/v52.0</value>
        </ifl:property>
        <ifl:property>
            <key>resourcePath</key>
            <value>sobjects/Account</value>
        </ifl:property>
        <ifl:property>
            <key>operation</key>
            <value>Query(GET)</value>
        </ifl:property>
        <ifl:property>
            <key>authenticationMethod</key>
            <value>OAuth</value>
        </ifl:property>
        <ifl:property>
            <key>credentialName</key>
            <value>Salesforce_Credentials</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>
```

---

## 🛠 **Template Method Mapping**

| JSON Component Type | Template Method | Generated XML Type |
|-------------------|-----------------|-------------------|
| `https_sender` | `mulesoft_http_listener_template()` | `<bpmn2:messageFlow ComponentType="HTTP">` |
| `http_receiver` | `mulesoft_http_request_template()` | `<bpmn2:messageFlow ComponentType="HTTP">` |
| `groovy_script` | `mulesoft_transform_message_template()` | `<bpmn2:callActivity activityType="Script">` |
| `router` | `mulesoft_choice_router_template()` | `<bpmn2:exclusiveGateway activityType="Router">` |
| `request_reply` | `odata_request_reply_pattern()` | Multiple components (ServiceTask + MessageFlow + Participant) |
| `enricher` | `content_enricher_template()` | `<bpmn2:callActivity activityType="Enricher">` |
| `json_to_xml` | `json_to_xml_converter_template()` | `<bpmn2:callActivity activityType="JsonToXmlConverter">` |
| `xml_to_json` | `xml_to_json_converter_template()` | `<bpmn2:callActivity activityType="XmlToJsonConverter">` |

---

## 🚀 **Complete MuleSoft Flow Example**

### **Input JSON:**
```json
{
  "process_name": "Customer Data Integration",
  "endpoints": [
    {
      "method": "POST",
      "path": "/api/customers",
      "components": [
        {
          "type": "https_sender",
          "name": "Customer_API_Listener",
          "config": {
            "url_path": "/api/customers",
            "sender_auth": "RoleBased"
          },
          "mulesoft_origin": "http:listener"
        },
        {
          "type": "groovy_script",
          "name": "Validate_Customer_Data",
          "config": {
            "script_content": "// Validation logic here"
          },
          "mulesoft_origin": "validation"
        },
        {
          "type": "request_reply",
          "name": "Query_Salesforce_Account",
          "receiver_adapter": {
            "type": "odata_adapter",
            "operation": "Query(GET)",
            "service_url": "https://your-instance.salesforce.com/services/data/v52.0",
            "entity_set": "Account"
          },
          "mulesoft_origin": "salesforce:query"
        }
      ]
    }
  ]
}
```

### **Generated XML Structure:**
- **Collaboration Section**: Contains participants and message flows
- **Process Section**: Contains service tasks, gateways, and sequence flows  
- **Diagram Section**: Contains visual layout information

---

## ⚠️ **Migration Guidelines**

### **✅ Best Practices:**
1. **Always specify `mulesoft_origin`** to track original component types
2. **Use proper receiver adapters** for request-reply patterns
3. **Include authentication configuration** for external service calls
4. **Preserve error handling logic** through exception subprocesses
5. **Map DataWeave transformations** to equivalent Groovy scripts

### **❌ Common Pitfalls:**
1. **Missing receiver adapters** in request-reply components
2. **Incorrect component types** that don't map to SAP Integration Suite
3. **Missing authentication configuration** for secure endpoints
4. **Incomplete transformation logic** when converting DataWeave to Groovy

---

*This documentation is maintained as part of the MuleToIS API migration system. For implementation details, refer to enhanced_iflow_templates.py.*
