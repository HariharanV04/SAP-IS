# SAP Integration Suite Documentation for Product API

# Table of Contents
- [API Overview](#api-overview)
- [Endpoints](#endpoints)
  - [GET /products](#get-products)
- [Current MuleSoft Flow Logic](#current-mulesoft-flow-logic)
  - [products-main Flow](#products-main-flow)
  - [products-console Flow](#products-console-flow)
  - [get:\products:products-config Flow](#getproductsproducts-config-flow)
  - [get-product-details-flow Subflow](#get-product-details-flow-subflow)
- [DataWeave Transformations Explained](#dataweave-transformations-explained)
  - [Product Identifier Validation](#product-identifier-validation)
  - [OData Query Parameters](#odata-query-parameters)
  - [Response Payload Transformation](#response-payload-transformation)
  - [Error Response Transformation](#error-response-transformation)
- [SAP Integration Suite Implementation](#sap-integration-suite-implementation)
  - [Component Mapping](#component-mapping)
  - [Integration Flow Visualization](#integration-flow-visualization)
- [Configuration Details](#configuration-details)
  - [HTTP Adapter Configuration](#http-adapter-configuration)
  - [OData Adapter Configuration](#odata-adapter-configuration)
  - [Content Modifier Configuration](#content-modifier-configuration)
  - [Router Configuration](#router-configuration)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [External Dependencies](#external-dependencies)

# API Overview

This API provides access to product information from an SAP HANA backend system. It allows clients to retrieve product details by specifying a product identifier as a query parameter. The API validates the product identifier against a configured list of valid identifiers before retrieving the data from the backend system.

**Base URL**: `/api/v1`

# Endpoints

## GET /products

This endpoint retrieves product details based on the provided product identifier.

**Query Parameters**:
- `productIdentifier` (required): The unique identifier of the product to retrieve

**Response Codes**:
- 200: Success - Returns product details
- 400: Bad Request - Invalid input parameters
- 404: Not Found - Product identifier not found
- 500: Internal Server Error - Server-side error

**Response Format**: JSON

**Example Request**:
```
GET /api/v1/products?productIdentifier=HT-2000
```

**Example Response**:
```json
{
  "ProductId": "HT-2000",
  "Category": "Notebooks",
  "CategoryName": "Notebooks",
  "CurrencyCode": "USD",
  "DimensionDepth": 30,
  "DimensionHeight": 3,
  "DimensionUnit": "cm",
  "DimensionWidth": 40,
  "LongDescription": "Notebook Basic 17 with 2,80 GHz quad core, 17\" LCD, 4 GB DDR3 RAM, 500 GB Hard Disc, Windows 8 Pro",
  "Name": "Notebook Basic 17",
  "PictureUrl": "/sap/public/bc/NWDEMO_MODEL/IMAGES/HT-2000.jpg",
  "Price": 1249,
  "QuantityUnit": "EA",
  "ShortDescription": "Notebook Basic 17 with 2,80 GHz quad core, 17\" LCD, 4 GB DDR3 RAM, 500 GB Hard Disc",
  "SupplierId": "0100000046",
  "Weight": 4.5,
  "WeightUnit": "KG"
}
```

# Current MuleSoft Flow Logic

## products-main Flow

This is the main entry point for the API. It:
1. Listens for incoming HTTP requests
2. Routes the request to the appropriate flow based on the endpoint
3. Handles responses and errors

## products-console Flow

This flow is used for logging and debugging purposes. It:
1. Listens for incoming HTTP requests
2. Logs the request details to the console
3. Returns a response

## get:\products:products-config Flow

This flow handles the GET /products endpoint. It:
1. Receives the request from the products-main flow
2. Calls the get-product-details-flow subflow to process the request

## get-product-details-flow Subflow

This subflow processes the product details request:

1. **Validate Product Identifier**: Checks if the provided productIdentifier query parameter is in the list of valid product identifiers
   
2. **Process Valid Product Request**:
   - If the product identifier is valid, logs the request
   - Constructs an OData query with specific filter and select parameters
   - Sends the request to the SAP HANA backend
   - Returns the response payload as JSON

3. **Handle Invalid Product Request**:
   - If the product identifier is invalid, logs an error message
   - Returns a custom error response with status "error" and error code "PRODUCT_NOT_FOUND"

# DataWeave Transformations Explained

## Product Identifier Validation

This transformation checks if the provided product identifier is in the list of valid product identifiers configured in the application.

**Input**: Query parameter `productIdentifier` from the HTTP request
**Output**: Boolean value indicating if the product identifier is valid

```dw
%dw 2.0
output application/java
var productidentifer=p('odata.productIdentifiers') splitBy(",")
---
sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
```

**Explanation**:
1. Retrieves the list of valid product identifiers from the configuration property `odata.productIdentifiers`
2. Splits the comma-separated list into an array
3. Filters the array to find elements matching the provided product identifier
4. Checks if the size of the filtered array is greater than 0 (indicating a match was found)

## OData Query Parameters

This transformation constructs the OData query parameters for the backend request.

**Input**: Query parameter `productIdentifier` from the HTTP request
**Output**: OData query parameters as a Java map

```dw
#[output application/java
---
{
	"$filter" : "ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'",
	"$select" : "ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit"
}]
```

**Explanation**:
1. Creates a map with two OData query parameters:
   - `$filter`: Filters products where ProductId equals the provided product identifier
   - `$select`: Specifies which fields to include in the response

## Response Payload Transformation

This transformation passes through the response payload from the backend system.

**Input**: Response from the SAP HANA backend
**Output**: JSON response

```dw
%dw 2.0
output application/json
---
payload
```

**Explanation**:
- Simply converts the payload to JSON format without any modifications

## Error Response Transformation

This transformation creates a custom error response when the product identifier is invalid.

**Input**: Query parameter `productIdentifier` from the HTTP request
**Output**: JSON error response

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

**Explanation**:
1. Creates a JSON object with three fields:
   - `status`: Set to "error"
   - `message`: Dynamic error message including the invalid product identifier
   - `errorCode`: Set to "PRODUCT_NOT_FOUND"

# SAP Integration Suite Implementation

## Component Mapping

| MuleSoft Component | SAP Integration Suite Equivalent | Notes |
|--------------------|----------------------------------|-------|
| HTTP Listener | HTTP Adapter (Receiver) | Configure with the same port and path from the MuleSoft configuration |
| Router | Router | Used to route requests based on endpoint path |
| Flow Reference | Process Call | Used to call subflows |
| Transform Message | Content Modifier with Script | Implement DataWeave logic using Groovy or JavaScript |
| Logger | Content Modifier with Logging | Configure to log the same messages |
| HTTP Request | OData Adapter (Sender) | Configure with the same URL, path, and query parameters |
| Set Variable | Content Modifier | Used to set variables in the message processing |
| Choice/When/Otherwise | Router with multiple branches | Implement the same conditional logic |
| Error Handler | Exception Subprocess | Configure to handle the same error scenarios |

## Integration Flow Visualization

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
start((Start)):::httpAdapter --> httpReceiver[HTTP Receiver]:::httpAdapter
httpReceiver --> router{Route by Path}:::router
router -->|"/products"| getProductsFlow[[get-products-flow]]:::processCall
router -->|other paths| notFound[Not Found Response]:::contentModifier
notFound --> end((End)):::httpAdapter

%% get-products-flow
getProductsFlow --> getProductDetailsFlow[[get-product-details-flow]]:::processCall
getProductDetailsFlow --> end

%% get-product-details-flow
subgraph getProductDetailsSubflow[get-product-details-flow]
    detailsStart((Start)) --> validateProduct[Validate Product ID]:::mapping
    validateProduct --> isValidProduct{Is Valid Product?}:::router
    
    isValidProduct -->|Yes| logValidRequest[Log Valid Request]:::contentModifier
    logValidRequest --> constructODataQuery[Construct OData Query]:::mapping
    constructODataQuery --> sendODataRequest[OData Request]:::httpAdapter
    sendODataRequest --> transformResponse[Transform Response]:::mapping
    transformResponse --> detailsEnd((End))
    
    isValidProduct -->|No| logInvalidRequest[Log Invalid Request]:::contentModifier
    logInvalidRequest --> createErrorResponse[Create Error Response]:::mapping
    createErrorResponse --> detailsEnd
end

%% Error Handling
httpReceiver -.-> errorHandler[(Global Error Handler)]:::exception
errorHandler -.-> badRequestError[Bad Request Error]:::contentModifier
errorHandler -.-> notFoundError[Not Found Error]:::contentModifier
errorHandler -.-> methodNotAllowedError[Method Not Allowed Error]:::contentModifier
errorHandler -.-> notAcceptableError[Not Acceptable Error]:::contentModifier
errorHandler -.-> unsupportedMediaTypeError[Unsupported Media Type Error]:::contentModifier
errorHandler -.-> notImplementedError[Not Implemented Error]:::contentModifier
badRequestError & notFoundError & methodNotAllowedError & notAcceptableError & unsupportedMediaTypeError & notImplementedError -.-> end
```

# Configuration Details

## HTTP Adapter Configuration

**HTTP Receiver Adapter**:
- Protocol: HTTPS
- Address: `/api/v1/*`
- Port: 8081 (from configuration)
- Authentication: None (based on source documentation)
- CSRF Protection: Disabled (based on source documentation)

**OData Sender Adapter**:
- Protocol: HTTPS
- Address: `refapp-espm-ui-cf.cfapps.eu10.hana.ondemand.com`
- Port: 443
- Path: `/espm-cloud-web/espm.svc/Products`
- Authentication: None (based on source documentation)

## OData Adapter Configuration

**OData Query Parameters**:
- $filter: `ProductId eq '{productIdentifier}'`
- $select: `ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit`

## Content Modifier Configuration

**Validate Product ID**:
- Script Type: Groovy
- Script:
```groovy
def productIdentifiers = properties.get("odata.productIdentifiers").split(",")
def requestedProductId = message.getHeaders().get("productIdentifier")
def isValid = productIdentifiers.any { it == requestedProductId }
message.setProperty("isExistProduct", isValid)
return message
```

**Log Valid Request**:
- Log Level: INFO
- Log Message: `The request is processed and sent downstream with the product identifier (${header.productIdentifier}).`

**Log Invalid Request**:
- Log Level: WARN
- Log Message: `The product identifier (${header.productIdentifier}) was not passed in the request or was passed incorrectly.`

**Create Error Response**:
- Content Type: application/json
- Content:
```json
{
  "status": "error",
  "message": "The product identifier ${header.productIdentifier} was not found.",
  "errorCode": "PRODUCT_NOT_FOUND"
}
```

## Router Configuration

**Route by Path**:
- Default Route: Not Found Response
- Condition 1: 
  - Condition Type: XPath
  - Expression: `$header.path = '/products'`
  - Route To: get-products-flow

**Is Valid Product?**:
- Default Route: Log Invalid Request
- Condition 1:
  - Condition Type: Property
  - Expression: `${property.isExistProduct} = true`
  - Route To: Log Valid Request

# Configuration

## Environment Variables

The following environment variables are required for the integration:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| api.listener.port | HTTP listener port | 8081 |
| api.listener.path | Base path for the API | /api/v1/* |
| hana.espm.url | URL of the SAP HANA backend | refapp-espm-ui-cf.cfapps.eu10.hana.ondemand.com |
| hana.espm.port | Port of the SAP HANA backend | 443 |
| hana.espm.path | Path to the Products service | /espm-cloud-web/espm.svc/Products |
| odata.productIdentifiers | Comma-separated list of valid product identifiers | HT-2000,HT-2001 |

## External Dependencies

The integration depends on the following external systems:

1. **SAP HANA ESPM Service**:
   - URL: refapp-espm-ui-cf.cfapps.eu10.hana.ondemand.com
   - Port: 443
   - Path: /espm-cloud-web/espm.svc/Products
   - Protocol: HTTPS
   - Authentication: None specified in source documentation