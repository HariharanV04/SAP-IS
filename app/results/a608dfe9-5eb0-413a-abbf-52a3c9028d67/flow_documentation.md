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

## API Overview
This API provides access to product information stored in an SAP HANA database through OData services. The integration retrieves detailed product information based on a product identifier provided as a query parameter. The API validates the product identifier against a configured list of valid identifiers before making the request to the backend SAP system.

- **Base URL**: Determined by the HTTP_Listener_config
- **Authentication**: Not explicitly defined in the source documentation
- **Rate Limiting**: Not specified in the source documentation
- **General Response Format**: JSON

## Endpoints

### GET /products
Retrieves detailed product information based on a product identifier.

- **HTTP Method**: GET
- **Path**: /products
- **Purpose**: Fetch product details from SAP HANA database using OData services

**Request Parameters**:
- **Query Parameters**:
  - `productIdentifier` (required): The unique identifier of the product to retrieve

**Response Format**:
- **Success Response (200 OK)**:
  - Content-Type: application/json
  - Body: JSON object containing product details

**Error Responses**:
- **400 Bad Request**:
  - When the product identifier is invalid or not found
  - Content-Type: application/json
  - Body:
    ```json
    {
      "status": "error",
      "message": "The product identifier {identifier} was not found.",
      "errorCode": "PRODUCT_NOT_FOUND"
    }
    ```

**Example Request**:
```
GET /products?productIdentifier=HT-1000
```

**Example Response**:
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
  "PictureUrl": "/images/HT-1000.jpg",
  "Price": 956.00,
  "QuantityUnit": "EA",
  "ShortDescription": "Notebook Basic 15 with 2,80 GHz quad core, 15\" LCD, 4 GB DDR3 RAM, 500 GB Hard Disc",
  "SupplierId": "0100000046",
  "Weight": 4.2,
  "WeightUnit": "KG"
}
```

## Current MuleSoft Flow Logic

### products-main Flow
1. **Trigger**: HTTP listener configured with products-config
2. **Processing**:
   - Sets response headers
   - Routes requests to appropriate handlers
   - Handles errors with error-response component
3. **Outcome**: Routes API requests to the appropriate endpoint handlers

### products-console Flow
1. **Trigger**: HTTP listener
2. **Processing**:
   - Sets response headers
   - Logs information to the console
   - Handles errors with error-response component
3. **Outcome**: Provides console logging functionality for debugging

### get:\products:products-config Flow
1. **Trigger**: GET request to /products endpoint
2. **Processing**:
   - References the get-product-details-flow subflow
3. **Outcome**: Delegates processing to the get-product-details-flow subflow

### get-product-details-flow Subflow
1. **Trigger**: Flow reference from get:\products:products-config
2. **Processing Steps**:
   - Validates if the product identifier exists in the configured list
   - If valid:
     - Logs the request with product identifier
     - Constructs OData query parameters for filtering and selecting fields
     - Makes HTTP request to SAP HANA backend
     - Transforms the response to JSON
   - If invalid:
     - Logs the error
     - Returns an error response
3. **Data Transformations**:
   - Validates product identifier against configured list
   - Constructs OData query parameters
   - Transforms backend response to JSON
   - Constructs error response if needed
4. **Error Scenarios**:
   - Invalid or missing product identifier
   - Backend service errors

## DataWeave Transformations Explained

### Product Identifier Validation
This transformation checks if the provided product identifier exists in a configured list of valid identifiers.

**Input**: Product identifier from query parameters
**Output**: Boolean value indicating if the product identifier is valid

```dw
%dw 2.0
output application/java
var productidentifer=p('odata.productIdentifiers') splitBy(",")
---
sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
```

**Explanation**:
1. Retrieves the list of valid product identifiers from a property `odata.productIdentifiers`
2. Splits the comma-separated list into an array
3. Filters the array to find matches with the provided product identifier
4. Returns true if at least one match is found (size > 0)

### OData Query Parameters Construction
This transformation constructs the OData query parameters for filtering and selecting fields.

**Input**: Product identifier from query parameters
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
2. Uses string concatenation (`++`) to insert the product identifier into the filter expression
3. Uses the `default` operator to provide an empty string if the product identifier is null

### Response Payload Transformation
This transformation passes through the response from the backend service.

**Input**: Response from SAP HANA OData service
**Output**: JSON response

```dw
%dw 2.0
output application/json
---
payload
```

**Explanation**:
1. Simply outputs the payload as JSON without any transformation
2. Maintains the structure and data from the backend response

### Error Response Transformation
This transformation constructs an error response when the product identifier is invalid.

**Input**: Product identifier from query parameters
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
2. Uses string concatenation (`++`) to insert the product identifier into the error message

## SAP Integration Suite Implementation

### Component Mapping

| MuleSoft Component | SAP Integration Suite Equivalent | Notes |
|--------------------|----------------------------------|-------|
| HTTP Listener | HTTPS Adapter (Receiver) | Configure with the same path and method |
| Flow Reference | Process Call | References another integration flow |
| DataWeave Transform | Content Modifier with Script | Use Groovy or JavaScript for similar logic |
| Logger | Write to Message Log | Configure with the same message content |
| HTTP Request | OData Adapter (Sender) | Configure with the same OData parameters |
| Choice/When/Otherwise | Router | Use Content-Based Router with the same conditions |
| Set Variable | Content Modifier | Set properties with the same values |
| Set Payload | Content Modifier | Set message body with the same content |
| Error Handler | Exception Subprocess | Configure with similar error handling logic |

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
    ((Start)) --> [HTTP_Endpoint_products]:::httpAdapter
    [HTTP_Endpoint_products] --> [[get-product-details-flow]]:::processCall
    
    %% get-product-details-flow Subflow
    subgraph get-product-details-flow
        ((Start_Subflow)) --> [ValidateProductIdentifier]:::mapping
        [ValidateProductIdentifier] --> {Is Product Valid?}:::router
        {Is Product Valid?} -->|Yes| [LogValidRequest]:::contentModifier
        {Is Product Valid?} -->|No| [LogInvalidRequest]:::contentModifier
        
        [LogValidRequest] --> [ConstructODataQuery]:::mapping
        [ConstructODataQuery] --> [ODataRequest]:::httpAdapter
        [ODataRequest] --> [TransformResponse]:::mapping
        
        [LogInvalidRequest] --> [ConstructErrorResponse]:::mapping
    end
    
    %% Error Handling
    [HTTP_Endpoint_products] -.-> [(GlobalErrorHandler)]:::exception
    [(GlobalErrorHandler)] -.-> [SetErrorResponse]:::contentModifier
    
    %% End points
    [TransformResponse] --> ((End_Success))
    [ConstructErrorResponse] --> ((End_Error))
    [SetErrorResponse] --> ((End_Error))
```

### Configuration Details

#### HTTP Endpoint Configuration
- **Adapter Type**: HTTPS Adapter (Receiver)
- **Path**: /products
- **Method**: GET
- **Authentication**: To be determined based on requirements

#### OData Request Configuration
- **Adapter Type**: OData Adapter (Sender)
- **Service URL**: To be configured based on SAP HANA endpoint
- **Query Parameters**:
  - **$filter**: ProductId eq '{productIdentifier}'
  - **$select**: ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit

#### Content Modifier - ValidateProductIdentifier
- **Type**: Content Modifier with Script
- **Script Type**: Groovy
- **Script**:
  ```groovy
  def productIdentifiers = property.get("odata.productIdentifiers").split(",")
  def requestedIdentifier = message.getProperty("productIdentifier")
  def isValid = productIdentifiers.find { it == requestedIdentifier } != null
  message.setProperty("isExistProduct", isValid)
  return message
  ```

#### Router - Is Product Valid?
- **Type**: Content-Based Router
- **Condition 1**: ${property.isExistProduct} == true
- **Condition 2**: Default (otherwise)

#### Content Modifier - LogValidRequest
- **Type**: Write to Message Log
- **Log Level**: INFO
- **Message**: The request is processed and sent downstream with the product identifier (${property.productIdentifier}).

#### Content Modifier - LogInvalidRequest
- **Type**: Write to Message Log
- **Log Level**: WARN
- **Message**: The product identifier (${property.productIdentifier}) was not passed in the request or was passed incorrectly.

#### Content Modifier - ConstructErrorResponse
- **Type**: Content Modifier
- **Message Body**:
  ```json
  {
    "status": "error",
    "message": "The product identifier ${property.productIdentifier} was not found.",
    "errorCode": "PRODUCT_NOT_FOUND"
  }
  ```
- **Content Type**: application/json

## Environment Configuration

### Important Configuration Parameters
- **odata.productIdentifiers**: Comma-separated list of valid product identifiers
- **HTTP_Listener_config**: HTTP listener configuration for the API endpoints
- **Hana_HTTP_Request_Configuration**: HTTP request configuration for connecting to SAP HANA

### Environment Variables
- **odata.productIdentifiers**: List of valid product identifiers (e.g., "HT-1000,HT-1001,HT-1002")
- **http.port**: Port for the HTTP listener (e.g., 8081)
- **hana.host**: Hostname for the SAP HANA instance
- **hana.port**: Port for the SAP HANA instance
- **hana.path**: Path to the OData service

### Dependencies on External Systems
- **SAP HANA**: The application depends on an SAP HANA instance with OData services enabled
- **OData Service**: The application requires an OData service that provides product information

### Security Settings
- **Authentication**: The source documentation does not specify authentication mechanisms, but typical options include:
  - Basic Authentication
  - OAuth 2.0
  - API Keys
- **TLS/SSL**: HTTPS should be used for secure communication

### Deployment Considerations
- Ensure network connectivity between the integration platform and SAP HANA
- Configure appropriate timeouts for HTTP requests
- Implement proper error handling and monitoring
- Consider implementing caching for frequently accessed products

### Required Resources
- **Memory**: Minimum 1GB recommended
- **CPU**: 1 vCPU minimum
- **Disk Space**: 500MB minimum for logs and temporary files

## API Reference

### Complete List of Endpoints

#### GET /products
Retrieves detailed product information based on a product identifier.

**Request**:
- **Method**: GET
- **Path**: /products
- **Query Parameters**:
  - `productIdentifier` (required): The unique identifier of the product to retrieve

**Response**:
- **Status Code**: 200 OK
- **Content-Type**: application/json
- **Body**: JSON object containing product details

**Error Responses**:
- **Status Code**: 400 Bad Request
  - When the product identifier is invalid or not found
  - **Content-Type**: application/json
  - **Body**:
    ```json
    {
      "status": "error",
      "message": "The product identifier {identifier} was not found.",
      "errorCode": "PRODUCT_NOT_FOUND"
    }
    ```

### Authentication Requirements
Authentication requirements are not explicitly defined in the source documentation. Typical options include:
- Basic Authentication
- OAuth 2.0
- API Keys

### Error Codes
- **PRODUCT_NOT_FOUND**: The specified product identifier was not found or is invalid

### Rate Limiting
Rate limiting information is not specified in the source documentation.

### Pagination
Pagination details are not applicable for this API as it retrieves a single product by identifier.

### Versioning Information
Versioning information is not specified in the source documentation.