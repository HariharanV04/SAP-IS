# SAP Integration Suite Implementation for Product API

# Table of Contents
- [API Overview](#api-overview)
- [Endpoints](#endpoints)
- [Current MuleSoft Flow Logic](#current-mulesoft-flow-logic)
- [DataWeave Transformations Explained](#dataweave-transformations-explained)
- [SAP Integration Suite Implementation](#sap-integration-suite-implementation)
  - [Component Mapping](#component-mapping)
  - [Integration Flow Visualization](#integration-flow-visualization)
- [Configuration Details](#configuration-details)
- [Configuration](#configuration)

# API Overview
This API provides access to product information from an SAP HANA backend system. It allows clients to retrieve product details by specifying a product identifier. The API validates the product identifier against a configured list of valid identifiers before retrieving the data from the SAP HANA system.

**Base URL**: `http://localhost:8081/api/v1`

# Endpoints

## GET /products
**Purpose**: Retrieves product details based on the provided product identifier.

**Request Parameters**:
- **Query Parameters**:
  - `productIdentifier` (required): The identifier of the product to retrieve

**Response Format**:
- **200 OK**: Successfully retrieved product details
  - Content-Type: application/json
  - Body: Product details JSON object
- **400 Bad Request**: Invalid request
- **404 Not Found**: Product not found
- **500 Internal Server Error**: Server error

**Error Response Example**:
```json
{
  "status": "error",
  "message": "The product identifier HT-9999 was not found.",
  "errorCode": "PRODUCT_NOT_FOUND"
}
```

# Current MuleSoft Flow Logic

## products-main Flow
**Trigger**: HTTP listener configured at `/api/v1/*`
**Purpose**: Main entry point for the API that handles routing to appropriate endpoints

1. Receives HTTP requests via the listener
2. Sets response headers
3. Routes requests to appropriate flows based on the path
4. Handles errors and formats error responses

## products-console Flow
**Trigger**: HTTP listener
**Purpose**: Provides console logging for API requests

1. Receives HTTP requests
2. Sets response headers
3. Logs request details to the console
4. Handles errors

## get:\products:products-config Flow
**Trigger**: HTTP GET request to `/products`
**Purpose**: Handles GET requests to the products endpoint

1. Receives the GET request to `/products`
2. Calls the `get-product-details-flow` subflow to process the request

## get-product-details-flow Subflow
**Purpose**: Validates the product identifier and retrieves product details

1. Validates if the provided product identifier exists in the configured list:
   ```
   %dw 2.0
   output application/java
   var productidentifer=p('odata.productIdentifiers') splitBy(",")
   ---
   sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
   ```

2. Sets a variable `isExistProduct` with the validation result

3. Conditional processing based on validation:
   - If `isExistProduct` is true:
     - Logs: "The request is processed and sent downstream with the product identifier (#[attributes.queryParams.productIdentifier])."
     - Makes an HTTP request to the SAP HANA backend with the following query parameters:
       ```
       #[output application/java
       ---
       {
         "$filter" : "ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'",
         "$select" : "ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit"
       }]
       ```
     - Transforms the response payload:
       ```
       %dw 2.0
       output application/json
       ---
       payload
       ```

   - If `isExistProduct` is false:
     - Logs: "The product identifier (#[attributes.queryParams.productIdentifier]) was not passed in the request or was passed incorrectly."
     - Transforms the payload to an error response:
       ```
       %dw 2.0
       output application/json
       ---
       {
         status: "error",
         message: "The product identifier " ++ attributes.queryParams.productIdentifier ++ " was not found.",
         errorCode: "PRODUCT_NOT_FOUND"
       }
       ```

# DataWeave Transformations Explained

## Product Identifier Validation Transformation
**Purpose**: Validates if the provided product identifier exists in the configured list of valid identifiers

**Input**: Query parameter `productIdentifier` from the HTTP request
**Output**: Boolean value indicating if the product identifier is valid

**Logic**:
1. Retrieves the configured list of product identifiers from the property `odata.productIdentifiers`
2. Splits the comma-separated list into an array
3. Filters the array to find matches with the provided product identifier
4. Returns true if at least one match is found (size > 0)

```dw
%dw 2.0
output application/java
var productidentifer=p('odata.productIdentifiers') splitBy(",")
---
sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
```

## OData Query Parameters Transformation
**Purpose**: Constructs the OData query parameters for the HTTP request to the SAP HANA backend

**Input**: Query parameter `productIdentifier` from the HTTP request
**Output**: OData query parameters object with `$filter` and `$select` parameters

**Logic**:
1. Constructs a `$filter` parameter to filter products by the provided product identifier
2. Specifies the fields to retrieve using the `$select` parameter

```dw
#[output application/java
---
{
  "$filter" : "ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'",
  "$select" : "ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit"
}]
```

## Response Payload Transformation
**Purpose**: Passes through the response payload from the SAP HANA backend

**Input**: Response payload from the HTTP request to the SAP HANA backend
**Output**: JSON representation of the response payload

```dw
%dw 2.0
output application/json
---
payload
```

## Error Response Transformation
**Purpose**: Constructs an error response when the product identifier is invalid

**Input**: Query parameter `productIdentifier` from the HTTP request
**Output**: JSON error response object

**Logic**:
1. Creates a JSON object with error status, message, and error code
2. Includes the invalid product identifier in the error message

```dw
%dw 2.0
output application/json
---
{
  status: "error",
  message: "The product identifier " ++ attributes.queryParams.productIdentifier ++ " was not found.",
  errorCode: "PRODUCT_NOT_FOUND"
}
```

# SAP Integration Suite Implementation

## Component Mapping

| MuleSoft Component | SAP Integration Suite Equivalent | Notes |
|--------------------|----------------------------------|-------|
| HTTP Listener | HTTPS Adapter (Receiver) | Configure with the same path and port |
| Router | Content Modifier + Router | Use a Content Modifier to set routing conditions and a Router to direct the flow |
| Flow Reference | Process Call | Use a Process Call to invoke another integration flow |
| Transform | Groovy Script or Message Mapping | Use Groovy Script for complex transformations and Message Mapping for simpler ones |
| Logger | Write to Message Headers | Use a Content Modifier to write log messages to message headers |
| HTTP Request | OData Adapter (Sender) | Configure with the same OData query parameters |
| Set Variable | Content Modifier | Use a Content Modifier to set variables |
| Choice/When/Otherwise | Router | Use a Router with multiple conditions |
| Set Payload | Content Modifier | Use a Content Modifier to set the message body |
| Error Handler | Exception Subprocess | Create an Exception Subprocess for error handling |

## REST API Integration Flow: GET /products

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Main Flow
start((Start)):::httpAdapter --> httpListener[HTTP Listener]:::httpAdapter
httpListener --> router{Router}:::router
router -->|/products| getProducts[[get:\products:products-config]]:::processCall
router -->|Other paths| notFound[Not Found Response]:::contentModifier
notFound --> end((End)):::httpAdapter

%% get:\products:products-config Flow
getProducts --> getProductDetailsFlow[[get-product-details-flow]]:::processCall
getProductDetailsFlow --> end

%% get-product-details-flow Subflow
subgraph getProductDetailsSubflow[get-product-details-flow]
    subflowStart((Start)) --> validateProductId[Validate Product ID]:::mapping
    validateProductId --> setIsExistProduct[Set isExistProduct Variable]:::contentModifier
    setIsExistProduct --> productIdCheck{isExistProduct?}:::router
    
    productIdCheck -->|Yes| logValidProduct[Log Valid Product]:::contentModifier
    logValidProduct --> constructODataQuery[Construct OData Query]:::mapping
    constructODataQuery --> oDataRequest[OData Request to SAP HANA]:::httpAdapter
    oDataRequest --> transformResponse[Transform Response]:::mapping
    transformResponse --> subflowEndSuccess((End))
    
    productIdCheck -->|No| logInvalidProduct[Log Invalid Product]:::contentModifier
    logInvalidProduct --> constructErrorResponse[Construct Error Response]:::mapping
    constructErrorResponse --> subflowEndError((End))
end

%% Error Handling
httpListener --> errorHandler[(Global Error Handler)]:::exception
errorHandler -->|APIKIT:BAD_REQUEST| badRequestResponse[Bad Request Response]:::contentModifier
errorHandler -->|APIKIT:NOT_FOUND| notFoundResponse[Not Found Response]:::contentModifier
errorHandler -->|APIKIT:METHOD_NOT_ALLOWED| methodNotAllowedResponse[Method Not Allowed Response]:::contentModifier
errorHandler -->|APIKIT:NOT_ACCEPTABLE| notAcceptableResponse[Not Acceptable Response]:::contentModifier
errorHandler -->|APIKIT:UNSUPPORTED_MEDIA_TYPE| unsupportedMediaTypeResponse[Unsupported Media Type Response]:::contentModifier
errorHandler -->|APIKIT:NOT_IMPLEMENTED| notImplementedResponse[Not Implemented Response]:::contentModifier
badRequestResponse --> end
notFoundResponse --> end
methodNotAllowedResponse --> end
notAcceptableResponse --> end
unsupportedMediaTypeResponse --> end
notImplementedResponse --> end
```

# Configuration Details

## HTTP Listener (HTTPS Adapter - Receiver)
- **Address**: `/api/v1/*`
- **Port**: `8081` (from configuration)
- **Authentication**: None (or as required)

## Router
- **Condition 1**: `/products` - Route to get-products flow
- **Default**: Route to not found response

## OData Request (OData Adapter - Sender)
- **URL**: `refapp-espm-ui-cf.cfapps.eu10.hana.ondemand.com:443/espm-cloud-web/espm.svc/Products`
- **Query Parameters**:
  - **$filter**: `ProductId eq '{productIdentifier}'`
  - **$select**: `ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit`

## Validate Product ID (Groovy Script)
- **Script**:
```groovy
import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;

def Message processData(Message message) {
    def map = message.getProperties();
    def productIdentifier = message.getProperty("productIdentifier");
    def validProductIds = map.get("odata.productIdentifiers").split(",");
    
    boolean isExistProduct = false;
    for (String id : validProductIds) {
        if (id.trim().equals(productIdentifier)) {
            isExistProduct = true;
            break;
        }
    }
    
    message.setProperty("isExistProduct", isExistProduct);
    return message;
}
```

## Product ID Check Router
- **Condition 1**: `${property.isExistProduct} == true` - Route to valid product flow
- **Default**: Route to invalid product flow

## Construct Error Response (Content Modifier)
- **Message Body**:
```json
{
  "status": "error",
  "message": "The product identifier ${property.productIdentifier} was not found.",
  "errorCode": "PRODUCT_NOT_FOUND"
}
```
- **Content Type**: `application/json`

# Configuration

## Environment Variables
From the `dev.yaml` file:

```yaml
api:
  listener:
    port: "8081"
    path: /api/v1/*
    
hana:
  espm:
    url: refapp-espm-ui-cf.cfapps.eu10.hana.ondemand.com
    port: "443"
    path: /espm-cloud-web/espm.svc/Products
    
odata:
  productIdentifiers: "HT-2000,HT-2001"
```

## External System Dependencies
- **SAP HANA Backend**: The integration relies on an SAP HANA backend system accessible at `refapp-espm-ui-cf.cfapps.eu10.hana.ondemand.com:443/espm-cloud-web/espm.svc/Products`

## Security Settings
- The original MuleSoft application does not specify security settings, but in SAP Integration Suite, you would typically configure:
  - **Basic Authentication** or **OAuth** for the OData connection to SAP HANA
  - **HTTPS** for all external connections
  - **API Management** policies for the exposed API endpoint

## Error Handling
The integration should implement error handling for:
- APIKIT:BAD_REQUEST
- APIKIT:NOT_FOUND
- APIKIT:METHOD_NOT_ALLOWED
- APIKIT:NOT_ACCEPTABLE
- APIKIT:UNSUPPORTED_MEDIA_TYPE
- APIKIT:NOT_IMPLEMENTED

Each error should return an appropriate HTTP status code and error message.