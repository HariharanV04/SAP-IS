# SAP OData Product Details API Integration

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
This API provides access to product details from an SAP HANA database through OData services. The integration retrieves product information based on a product identifier provided as a query parameter. The API validates the product identifier against a configured list of valid identifiers before making the request to the backend system.

- **Base URL**: Determined by the HTTP_Listener_config
- **Authentication**: Not explicitly defined in the source documentation
- **Rate Limiting**: Not specified in the source documentation
- **General Response Format**: JSON

The API serves as a facade to simplify access to product data stored in SAP systems, providing a RESTful interface that handles validation, error responses, and data transformation.

## Endpoints

### GET /products
Retrieves detailed information about a specific product based on the provided product identifier.

- **HTTP Method**: GET
- **Path**: /products
- **Purpose**: Fetch detailed product information from SAP HANA

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

## Current MuleSoft Flow Logic

The application consists of several flows and subflows that work together to process API requests:

### products-main Flow
1. **Trigger**: HTTP listener configured with products-config
2. **Processing**:
   - Sets response headers
   - Handles error responses
   - Routes requests to appropriate handlers based on the API specification

### products-console Flow
1. **Trigger**: HTTP listener
2. **Processing**:
   - Sets response headers
   - Handles error responses
   - Logs information to the console

### get:\products:products-config Flow
1. **Trigger**: HTTP GET request to /products endpoint
2. **Processing**:
   - Calls the get-product-details-flow subflow to handle the request

### get-product-details-flow Subflow
1. **Validation**:
   - Transforms the request to validate if the product identifier exists in the configured list
   ```
   %dw 2.0
   output application/java
   var productidentifer=p('odata.productIdentifiers') splitBy(",")
   ---
   sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
   ```
   - Sets the validation result to a variable `isExistProduct`

2. **Conditional Processing**:
   - If `vars.isExistProduct` is true:
     - Logs that the request is being processed
     - Makes an HTTP request to the SAP HANA backend with OData query parameters:
       ```
       #[output application/java
       ---
       {
         "$filter" : "ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'",
         "$select" : "ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit"
       }]
       ```
     - Transforms the response payload to JSON format
   - Otherwise (if validation fails):
     - Logs that the product identifier was not passed or was incorrect
     - Returns an error response with status "error", appropriate message, and error code "PRODUCT_NOT_FOUND"

## DataWeave Transformations Explained

### Product Identifier Validation
This transformation validates if the provided product identifier exists in a configured list of valid identifiers.

**Input**: Query parameters from the HTTP request
**Output**: Boolean value indicating if the product identifier is valid

```dw
%dw 2.0
output application/java
var productidentifer=p('odata.productIdentifiers') splitBy(",")
---
sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
```

The transformation:
1. Retrieves a comma-separated list of valid product identifiers from a property
2. Splits the string into an array using the comma as a delimiter
3. Filters the array to find elements matching the provided product identifier
4. Returns true if at least one match is found (size > 0), false otherwise

### OData Query Parameters Construction
This transformation constructs the OData query parameters for filtering and selecting specific product fields.

**Input**: Query parameters from the HTTP request
**Output**: OData query parameters as a Java map

```dw
#[output application/java
---
{
	"$filter" : "ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'",
	"$select" : "ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit"
}]
```

The transformation:
1. Creates a map with two OData query parameters:
   - `$filter`: Constructs a filter expression that matches the ProductId with the provided identifier
   - `$select`: Specifies the fields to retrieve from the product data

### Response Payload Transformation
This simple transformation passes through the payload from the HTTP response.

**Input**: Response from the SAP HANA backend
**Output**: JSON representation of the response

```dw
%dw 2.0
output application/json
---
payload
```

### Error Response Transformation
This transformation constructs an error response when the product identifier validation fails.

**Input**: Query parameters from the HTTP request
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

The transformation:
1. Creates a JSON object with three fields:
   - `status`: Set to "error"
   - `message`: A descriptive message including the invalid product identifier
   - `errorCode`: Set to "PRODUCT_NOT_FOUND"

## SAP Integration Suite Implementation

### Component Mapping

| MuleSoft Component | SAP Integration Suite Equivalent | Notes |
|--------------------|----------------------------------|-------|
| HTTP Listener | HTTPS Adapter (Receiver) | Configure with the same path and method |
| Flow Reference | Process Call | Used to call subflows |
| DataWeave Transform | Content Modifier with Script | Use Groovy or JavaScript for similar logic |
| Logger | Write to Message Headers | Log messages can be stored in message headers |
| HTTP Request | OData Adapter (Sender) | Configure with the same OData query parameters |
| Set Variable | Content Modifier | Used to set variables in the message exchange |
| Choice/When/Otherwise | Router | Implement conditional logic |
| Set Payload | Content Modifier | Set the message body |
| Error Handler | Exception Subprocess | Handle errors with appropriate responses |

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
start((Start)) --> httpListener[HTTP Listener<br>/products]:::httpAdapter
httpListener --> getProductsFlow[[get:\products:products-config]]:::processCall
getProductsFlow --> response[HTTP Response]:::httpAdapter
response --> end((End))

%% get:\products:products-config Flow
getProductsFlowStart((Start)) --> productDetailsFlow[[get-product-details-flow]]:::processCall
productDetailsFlow --> getProductsFlowEnd((End))

%% get-product-details-flow Subflow
subflowStart((Start)) --> validateProduct[Validate Product Identifier]:::mapping
validateProduct --> setIsExistProduct[Set isExistProduct Variable]:::contentModifier
setIsExistProduct --> isProductValid{Is Product Valid?}:::router
isProductValid -->|Yes| logSuccess[Log Success Message]:::contentModifier
logSuccess --> constructODataQuery[Construct OData Query]:::mapping
constructODataQuery --> oDataRequest[OData Request to SAP HANA]:::httpAdapter
oDataRequest --> transformResponse[Transform Response to JSON]:::mapping
transformResponse --> successEnd((End))

isProductValid -->|No| logError[Log Error Message]:::contentModifier
logError --> constructErrorResponse[Construct Error Response]:::mapping
constructErrorResponse --> errorEnd((End))

%% Error Handling
httpListener --> errorHandler[(Global Error Handler)]:::exception
errorHandler --> apiKitErrors{API Kit Errors}:::router
apiKitErrors -->|BAD_REQUEST| badRequestResponse[Set Bad Request Response]:::contentModifier
apiKitErrors -->|NOT_FOUND| notFoundResponse[Set Not Found Response]:::contentModifier
apiKitErrors -->|METHOD_NOT_ALLOWED| methodNotAllowedResponse[Set Method Not Allowed Response]:::contentModifier
apiKitErrors -->|NOT_ACCEPTABLE| notAcceptableResponse[Set Not Acceptable Response]:::contentModifier
apiKitErrors -->|UNSUPPORTED_MEDIA_TYPE| unsupportedMediaTypeResponse[Set Unsupported Media Type Response]:::contentModifier
apiKitErrors -->|NOT_IMPLEMENTED| notImplementedResponse[Set Not Implemented Response]:::contentModifier
```

### Configuration Details

#### HTTP Adapter (Receiver)
- **Address**: `/products`
- **Method**: GET
- **Authentication**: To be determined based on security requirements
- **CSRF Protection**: Disabled

#### OData Adapter (Sender)
- **Connection**: SAP HANA OData Service
- **Service Path**: To be determined based on SAP HANA configuration
- **Query Options**:
  - **$filter**: `ProductId eq '{productIdentifier}'`
  - **$select**: `ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit`
- **Authentication**: To be determined based on SAP HANA configuration

#### Content Modifier (Validate Product Identifier)
- **Script Type**: Groovy
- **Script**:
  ```groovy
  def productIdentifiers = properties.get("odata.productIdentifiers").split(",")
  def requestedIdentifier = message.getProperty("productIdentifier")
  def isValid = productIdentifiers.any { it == requestedIdentifier }
  message.setProperty("isExistProduct", isValid)
  return message
  ```

#### Router (Product Validation)
- **Condition 1**: `${property.isExistProduct} == true`
- **Condition 2**: `${property.isExistProduct} != true`

#### Content Modifier (Error Response)
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

### Environment Variables
- **HTTP_LISTENER_HOST**: Host for the HTTP listener
- **HTTP_LISTENER_PORT**: Port for the HTTP listener
- **HANA_HTTP_BASE_URL**: Base URL for the SAP HANA HTTP requests
- **PRODUCT_IDENTIFIERS**: Comma-separated list of valid product identifiers

### Dependencies on External Systems
- **SAP HANA**: The integration depends on an SAP HANA system with OData services enabled
- **OData Service**: The OData service must support the query parameters used in the integration

### Security Settings
- **Authentication**: The integration should implement appropriate authentication mechanisms for both the API and the SAP HANA connection
- **HTTPS**: All connections should use HTTPS for secure communication

### Deployment Considerations
- **Connectivity**: Ensure network connectivity between the integration platform and SAP HANA
- **Firewall Rules**: Configure firewall rules to allow communication between systems
- **Certificate Management**: Manage certificates for secure HTTPS connections

### Required Resources
- **Memory**: Minimum 1GB recommended
- **CPU**: 1 vCPU minimum recommended
- **Disk Space**: 500MB minimum for logs and temporary files

## API Reference

### GET /products
Retrieves detailed information about a specific product.

**Request**:
- **Method**: GET
- **Path**: /products
- **Query Parameters**:
  - `productIdentifier` (required): The unique identifier of the product to retrieve

**Response**:
- **Status Code**: 200 OK
- **Content-Type**: application/json
- **Body**: JSON object containing product details with the following fields:
  - ProductId
  - Category
  - CategoryName
  - CurrencyCode
  - DimensionDepth
  - DimensionHeight
  - DimensionUnit
  - DimensionWidth
  - LongDescription
  - Name
  - PictureUrl
  - Price
  - QuantityUnit
  - ShortDescription
  - SupplierId
  - Weight
  - WeightUnit

### Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| PRODUCT_NOT_FOUND | 400 | The requested product identifier was not found or is invalid |
| APIKIT:BAD_REQUEST | 400 | The request was malformed or contained invalid parameters |
| APIKIT:NOT_FOUND | 404 | The requested resource was not found |
| APIKIT:METHOD_NOT_ALLOWED | 405 | The HTTP method is not supported for the requested resource |
| APIKIT:NOT_ACCEPTABLE | 406 | The server cannot produce a response matching the list of acceptable values |
| APIKIT:UNSUPPORTED_MEDIA_TYPE | 415 | The media type of the request is not supported |
| APIKIT:NOT_IMPLEMENTED | 501 | The requested functionality is not implemented |