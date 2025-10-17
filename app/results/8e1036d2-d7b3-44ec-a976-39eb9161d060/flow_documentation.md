# SAP OData Product Information API Integration

## Table of Contents
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
  - [OData Query Parameters Construction](#odata-query-parameters-construction)
  - [Response Payload Transformation](#response-payload-transformation)
  - [Error Response Transformation](#error-response-transformation)
- [SAP Integration Suite Implementation](#sap-integration-suite-implementation)
  - [Component Mapping](#component-mapping)
  - [Integration Flow Visualization](#integration-flow-visualization)
  - [Configuration Details](#configuration-details)
- [Environment Configuration](#environment-configuration)
- [API Reference](#api-reference)
  - [GET /products](#get-products-1)
  - [Error Codes](#error-codes)

## API Overview
This API provides access to product information stored in an SAP HANA database through OData services. The integration allows clients to retrieve detailed product information by providing a product identifier as a query parameter. The API validates the product identifier against a configured list of valid identifiers before forwarding the request to the backend SAP system.

- **Base URL**: Determined by the HTTP_Listener_config
- **Authentication**: Not explicitly defined in the source documentation
- **Rate Limiting**: Not specified in the source documentation
- **General Response Format**: JSON

The API serves as a facade for the underlying SAP OData service, providing a simplified interface for product information retrieval while handling validation and error scenarios.

## Endpoints

### GET /products
Retrieves detailed product information based on a provided product identifier.

- **HTTP Method**: GET
- **Path**: /products
- **Purpose**: Fetch product details from SAP HANA database via OData service

**Request Parameters**:
- **Query Parameters**:
  - `productIdentifier` (required): The unique identifier of the product to retrieve

**Response Format**:
- **Success Response (200 OK)**:
  - Content-Type: application/json
  - Body: Product details from the SAP system

- **Error Response (400 Bad Request)**:
  - Content-Type: application/json
  - Body: Error details with status, message, and errorCode

**Example Error Response**:
```json
{
  "status": "error",
  "message": "The product identifier ABC123 was not found.",
  "errorCode": "PRODUCT_NOT_FOUND"
}
```

**Error Handling**:
- If the product identifier is not provided or is invalid, returns a PRODUCT_NOT_FOUND error
- APIKIT errors (BAD_REQUEST, NOT_FOUND, etc.) are handled by the global error handler

## Current MuleSoft Flow Logic

### products-main Flow
1. **Trigger**: HTTP listener configured with products-config
2. **Processing**:
   - Sets response headers
   - Routes requests based on API configuration
   - Handles errors with a dedicated error response component
3. **Outcome**: Routes API requests to the appropriate handler flow based on the endpoint and method

### products-console Flow
1. **Trigger**: HTTP listener
2. **Processing**:
   - Sets response headers
   - Logs information to the console
   - Handles errors with a dedicated error response component
3. **Outcome**: Provides console logging functionality for the API

### get:\products:products-config Flow
1. **Trigger**: GET request to /products endpoint
2. **Processing**:
   - References the get-product-details-flow subflow
3. **Outcome**: Delegates processing to the get-product-details-flow subflow

### get-product-details-flow Subflow
1. **Trigger**: Flow reference from get:\products:products-config
2. **Processing Steps**:
   - Validates if the provided product identifier exists in the configured list
   - Sets variables for processing
   - Branches based on validation result:
     - If valid: Logs the request, constructs OData query, and sends request to SAP
     - If invalid: Logs the error and constructs an error response
3. **Data Transformations**:
   - Validates product identifier against configured list
   - Constructs OData query parameters with $filter and $select
   - Transforms SAP response to JSON
   - Constructs error response for invalid product identifiers
4. **Expected Outcomes**:
   - Success: Returns product details from SAP
   - Error: Returns error response with PRODUCT_NOT_FOUND code

**Key Technical Details**:
- OData query parameters:
  - `$filter`: `ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'`
  - `$select`: `ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit`

## DataWeave Transformations Explained

### Product Identifier Validation
This transformation validates if the provided product identifier exists in the configured list of valid identifiers.

**Input**: Query parameters from the HTTP request
**Output**: Boolean value indicating if the product identifier is valid

```dw
%dw 2.0
output application/java
var productidentifer=p('odata.productIdentifiers') splitBy(",")
---
sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
```

**Explanation**:
1. Retrieves the configured list of valid product identifiers from a property
2. Splits the comma-separated list into an array
3. Filters the array to find matches with the provided product identifier
4. Returns true if at least one match is found (size > 0)

### OData Query Parameters Construction
This transformation constructs the OData query parameters for the SAP request.

**Input**: HTTP request attributes
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
1. Creates a map with OData query parameters
2. Constructs a $filter parameter that filters products by the provided product identifier
3. Specifies the fields to retrieve using the $select parameter
4. Uses the default operator to handle cases where productIdentifier is not provided

### Response Payload Transformation
This transformation passes through the SAP response as JSON.

**Input**: SAP OData response
**Output**: JSON response

```dw
%dw 2.0
output application/json
---
payload
```

**Explanation**:
1. Sets the output MIME type to application/json
2. Passes through the payload without modification

### Error Response Transformation
This transformation constructs an error response for invalid product identifiers.

**Input**: HTTP request attributes
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
1. Creates a JSON object with error details
2. Includes the invalid product identifier in the error message
3. Sets a specific error code for product not found scenarios

## SAP Integration Suite Implementation

### Component Mapping

| MuleSoft Component | SAP Integration Suite Equivalent | Notes |
|--------------------|----------------------------------|-------|
| HTTP Listener | HTTPS Adapter (Receiver) | Configure with the same path and method |
| Router | Content Modifier + Router | Use Content Modifier to set properties and Router for conditional paths |
| Flow Reference | Process Call | References another integration flow |
| Transform (DataWeave) | Groovy Script or Message Mapping | Convert DataWeave scripts to equivalent Groovy or Message Mapping |
| Logger | Content Modifier with Write to Log option | Set log level and message content |
| HTTP Request | HTTPS Adapter (Sender) or OData Adapter | Use OData Adapter for SAP OData services |
| Set Variable | Content Modifier | Set exchange properties |
| Choice/When/Otherwise | Router | Configure with the same conditions |
| Error Handler | Exception Subprocess | Handle errors with the same logic |

### Integration Flow Visualization

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
    ((Start)) --> HttpReceiver[HTTP Receiver: /products]:::httpAdapter
    HttpReceiver --> ProductsRouter{Route by endpoint}:::router
    ProductsRouter -->|GET /products| [[GetProductDetailsFlow]]:::processCall
    
    %% Get Product Details Flow
    subgraph GetProductDetailsFlow
        ((StartSubflow)) --> ValidateProduct[Validate Product Identifier]:::mapping
        ValidateProduct --> SetVars[Set Variables]:::contentModifier
        SetVars --> ProductRouter{Is Valid Product?}:::router
        
        ProductRouter -->|Yes| LogValidRequest[Log Valid Request]:::contentModifier
        LogValidRequest --> BuildODataQuery[Build OData Query Parameters]:::contentModifier
        BuildODataQuery --> ODataRequest[OData Request to SAP]:::httpAdapter
        ODataRequest --> TransformResponse[Transform Response]:::mapping
        
        ProductRouter -->|No| LogInvalidRequest[Log Invalid Request]:::contentModifier
        LogInvalidRequest --> BuildErrorResponse[Build Error Response]:::mapping
    end
    
    %% Error Handling
    HttpReceiver -.-> [(Global Error Handler)]:::exception
    [(Global Error Handler)] -.-> BuildApiErrorResponse[Build API Error Response]:::mapping
    
    %% End points
    TransformResponse --> ((End Success))
    BuildErrorResponse --> ((End Error))
    BuildApiErrorResponse -.-> ((End API Error))
```

### Configuration Details

#### HTTP Receiver Adapter
- **Path**: /products
- **Method**: GET
- **Authentication**: To be determined based on security requirements

#### Content Modifier: Validate Product Identifier
- **Script Type**: Groovy
- **Script Content**:
```groovy
def productIdentifiers = property.get("odata.productIdentifiers").split(",")
def requestedProductId = message.getHeaders().get("productIdentifier")
def isValidProduct = productIdentifiers.any { it == requestedProductId }
message.setProperty("isExistProduct", isValidProduct)
return message
```

#### Router: Is Valid Product?
- **Condition 1**: ${property.isExistProduct} == true
- **Condition 2**: ${property.isExistProduct} == false

#### Content Modifier: Log Valid Request
- **Log Level**: INFO
- **Message**: "The request is processed and sent downstream with the product identifier (${header.productIdentifier})."

#### Content Modifier: Build OData Query Parameters
- **Header Name**: SAP_OData_Filter
- **Header Value**: ProductId eq '${header.productIdentifier}'
- **Header Name**: SAP_OData_Select
- **Header Value**: ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit

#### OData Adapter: OData Request to SAP
- **Connection**: SAP HANA OData Service
- **Entity Set**: Products
- **Query Options**:
  - $filter: ${header.SAP_OData_Filter}
  - $select: ${header.SAP_OData_Select}

#### Content Modifier: Log Invalid Request
- **Log Level**: WARN
- **Message**: "The product identifier (${header.productIdentifier}) was not passed in the request or was passed incorrectly."

#### Message Mapping: Build Error Response
- **Target Structure**: JSON
- **Mapping**:
```json
{
  "status": "error",
  "message": "The product identifier ${header.productIdentifier} was not found.",
  "errorCode": "PRODUCT_NOT_FOUND"
}
```

#### Exception Subprocess: Global Error Handler
- **Error Types**: All API errors
- **Response Code**: Based on error type
- **Response Format**: JSON error response

## Environment Configuration

### Important Configuration Parameters
- **odata.productIdentifiers**: Comma-separated list of valid product identifiers

### Environment Variables
- **HTTP_LISTENER_HOST**: Host for the HTTP listener (e.g., "0.0.0.0")
- **HTTP_LISTENER_PORT**: Port for the HTTP listener (e.g., "8081")
- **SAP_HANA_HOST**: Host for the SAP HANA system
- **SAP_HANA_PORT**: Port for the SAP HANA system
- **SAP_HANA_PATH**: Path to the OData service
- **SAP_HANA_USERNAME**: Username for SAP HANA authentication
- **SAP_HANA_PASSWORD**: Password for SAP HANA authentication

### Dependencies on External Systems
- **SAP HANA**: The integration depends on an SAP HANA system with OData services enabled
- **OData Service**: The SAP system must expose product information via OData

### Security Settings
- **Authentication**: Configuration required for SAP HANA authentication
- **TLS/SSL**: Configuration required for secure communication with SAP HANA

### Deployment Considerations
- Ensure network connectivity between the integration platform and SAP HANA
- Configure appropriate timeouts for SAP HANA requests
- Set up monitoring for integration health and performance

### Required Resources
- **Memory**: Minimum 1GB recommended
- **CPU**: 1 CPU core minimum
- **Disk Space**: 500MB minimum for logs and temporary files

## API Reference

### GET /products
Retrieves detailed product information from SAP HANA.

**Request**:
- **Method**: GET
- **Path**: /products
- **Query Parameters**:
  - `productIdentifier` (required): The unique identifier of the product to retrieve

**Response**:
- **Success Response (200 OK)**:
  - Content-Type: application/json
  - Body: Product details from SAP HANA
  ```json
  {
    "ProductId": "HT-1000",
    "Category": "Laptops",
    "CategoryName": "Laptops",
    "CurrencyCode": "USD",
    "DimensionDepth": 30,
    "DimensionHeight": 3,
    "DimensionUnit": "cm",
    "DimensionWidth": 40,
    "LongDescription": "Notebook Basic 15 with 2,80 GHz quad core, 15\" LCD, 4 GB DDR3 RAM, 500 GB Hard Disc, Windows 8 Pro",
    "Name": "Notebook Basic 15",
    "PictureUrl": "/sap/public/bc/NWDEMO_MODEL/IMAGES/HT-1000.jpg",
    "Price": 956,
    "QuantityUnit": "EA",
    "ShortDescription": "Notebook Basic 15 with 2,80 GHz quad core, 15\" LCD, 4 GB DDR3 RAM, 500 GB Hard Disc",
    "SupplierId": "0100000046",
    "Weight": 4.2,
    "WeightUnit": "kg"
  }
  ```

- **Error Response (400 Bad Request)**:
  - Content-Type: application/json
  - Body: Error details
  ```json
  {
    "status": "error",
    "message": "The product identifier ABC123 was not found.",
    "errorCode": "PRODUCT_NOT_FOUND"
  }
  ```

### Error Codes

| Error Code | Description | HTTP Status Code |
|------------|-------------|------------------|
| PRODUCT_NOT_FOUND | The requested product identifier was not found or is invalid | 400 |
| APIKIT:BAD_REQUEST | The request was malformed | 400 |
| APIKIT:NOT_FOUND | The requested resource was not found | 404 |
| APIKIT:METHOD_NOT_ALLOWED | The HTTP method is not allowed for the requested resource | 405 |
| APIKIT:NOT_ACCEPTABLE | The server cannot produce a response matching the list of acceptable values | 406 |
| APIKIT:UNSUPPORTED_MEDIA_TYPE | The media type of the request is not supported | 415 |
| APIKIT:NOT_IMPLEMENTED | The requested functionality is not implemented | 501 |