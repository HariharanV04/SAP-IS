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
This API provides access to product information stored in an SAP HANA database through OData services. It allows clients to retrieve detailed product information by providing a product identifier as a query parameter. The API validates the product identifier against a configured list of valid identifiers before making the request to the backend SAP system.

- **Base URL**: Determined by the HTTP_Listener_config
- **Authentication**: Not explicitly defined in the source documentation
- **Rate Limiting**: Not specified in the source documentation
- **General Response Format**: JSON

The API serves as a middleware layer between client applications and the SAP backend system, providing a simplified interface for retrieving product information while implementing validation and error handling.

## Endpoints

### GET /products
Retrieves detailed product information based on a provided product identifier.

- **HTTP Method**: GET
- **Path**: /products
- **Purpose**: Fetch detailed product information from SAP HANA

**Request Parameters**:
- **Query Parameters**:
  - `productIdentifier` (required): The unique identifier of the product to retrieve

**Response Format**:
- **Success Response (200 OK)**:
  - Content-Type: application/json
  - Body: JSON object containing product details from SAP HANA

- **Error Response (400 Bad Request)**:
  - Content-Type: application/json
  - Body: JSON object with error details
    ```json
    {
      "status": "error",
      "message": "The product identifier [identifier] was not found.",
      "errorCode": "PRODUCT_NOT_FOUND"
    }
    ```

**Error Handling**:
- If the product identifier is not provided or is invalid, returns a 400 Bad Request with a PRODUCT_NOT_FOUND error
- API-specific errors (BAD_REQUEST, NOT_FOUND, etc.) are handled by the global error handler

## Current MuleSoft Flow Logic

### products-main Flow
1. **Trigger**: HTTP listener configured with HTTP_Listener_config
2. **Processing**:
   - Sets response headers
   - Routes requests based on API configuration
   - Handles errors with a dedicated error response component
3. **Outcome**: Routes API requests to the appropriate flow based on the endpoint and method

### products-console Flow
1. **Trigger**: HTTP listener configured with HTTP_Listener_config
2. **Processing**:
   - Sets response headers
   - Logs information to the console
   - Handles errors with a dedicated error response component
3. **Outcome**: Provides console logging functionality for the API

### get:\products:products-config Flow
1. **Trigger**: GET request to the /products endpoint
2. **Processing**:
   - References the get-product-details-flow subflow
3. **Outcome**: Delegates processing to the get-product-details-flow subflow

### get-product-details-flow Subflow
1. **Trigger**: Flow reference from get:\products:products-config
2. **Processing Steps**:
   - Validates the product identifier against a configured list
   - Sets variables for processing
   - Logs the request details
   - If product identifier is valid:
     - Constructs OData query parameters for the SAP HANA request
     - Makes HTTP request to SAP HANA with specific OData parameters
     - Transforms the response to JSON
   - If product identifier is invalid:
     - Logs the error
     - Creates an error response
3. **Data Transformations**:
   - Validates product identifier against configured list
   - Constructs OData query parameters
   - Transforms SAP HANA response to JSON
   - Creates error response for invalid product identifiers
4. **Expected Outcomes**:
   - Success: Returns product details from SAP HANA
   - Error: Returns error response for invalid product identifier

**Key Technical Details**:
- OData query parameters:
  - `$filter`: `ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'`
  - `$select`: `ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit`

## DataWeave Transformations Explained

### Product Identifier Validation
This transformation validates if the provided product identifier exists in the configured list of valid product identifiers.

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
This transformation constructs the OData query parameters for the SAP HANA request.

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
1. Creates a Java map with OData query parameters
2. Sets the `$filter` parameter to filter by the provided product identifier
3. Sets the `$select` parameter to specify which fields to retrieve
4. Uses the `default ''` operator to handle cases where the product identifier is not provided

### Response Payload Transformation
This transformation passes through the SAP HANA response as JSON.

**Input**: SAP HANA response
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
This transformation creates an error response for invalid product identifiers.

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
2. Sets the status to "error"
3. Constructs an error message that includes the invalid product identifier
4. Sets the error code to "PRODUCT_NOT_FOUND"

## SAP Integration Suite Implementation

### Component Mapping

| MuleSoft Component | SAP Integration Suite Equivalent | Notes |
|--------------------|----------------------------------|-------|
| HTTP Listener | HTTPS Adapter (Receiver) | Configure with the same path and method settings |
| Flow Reference | Process Call | Used to call the product details subflow |
| DataWeave Transform | Content Modifier + Groovy Script | For complex transformations, use Groovy Script; for simple mappings, use Content Modifier |
| Logger | Write to Message Log | Configure with the same log message |
| HTTP Request | OData Adapter (Sender) | Configure with the same OData query parameters |
| Choice Router | Router | Configure with the same condition |
| Set Variable | Content Modifier (with property setting) | Use to set exchange properties |
| Set Payload | Content Modifier | Use to set the message body |
| Error Handler | Exception Subprocess | Configure with the same error handling logic |

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
    [HTTP_Endpoint_products] --> [[Get_Product_Details]]:::processCall
    [[Get_Product_Details]] --> ((End))

    %% Get Product Details Subflow
    subgraph Get_Product_Details_Flow
        ((SubflowStart)) --> [ValidateProductID]:::mapping
        [ValidateProductID] --> [SetIsExistProductVar]:::contentModifier
        [SetIsExistProductVar] --> {IsProductValid}:::router
        {IsProductValid} -->|Yes| [LogValidRequest]:::contentModifier
        {IsProductValid} -->|No| [LogInvalidRequest]:::contentModifier
        
        [LogValidRequest] --> [ConstructODataQuery]:::mapping
        [ConstructODataQuery] --> [SAP_OData_Request]:::httpAdapter
        [SAP_OData_Request] --> [TransformResponse]:::mapping
        [TransformResponse] --> ((SubflowEnd))
        
        [LogInvalidRequest] --> [CreateErrorResponse]:::mapping
        [CreateErrorResponse] --> ((SubflowEnd))
    end

    %% Error Handling
    [HTTP_Endpoint_products] -.-> [(GlobalErrorHandler)]:::exception
    [(GlobalErrorHandler)] -.-> [SetErrorResponse]:::contentModifier
    [SetErrorResponse] -.-> ((ErrorEnd))
```

### Configuration Details

#### HTTP Endpoint Configuration
- **Adapter Type**: HTTPS Adapter (Receiver)
- **Path**: /products
- **Method**: GET
- **Authentication**: To be determined based on security requirements

#### OData Adapter Configuration
- **Adapter Type**: OData Adapter (Sender)
- **Connection**: SAP HANA Connection
- **Service Path**: To be determined based on SAP HANA OData service
- **Query Parameters**:
  - `$filter`: ProductId eq '{productIdentifier}'
  - `$select`: ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit

#### Content Modifiers
1. **ValidateProductID**:
   - Type: Groovy Script
   - Script:
     ```groovy
     import com.sap.gateway.ip.core.customdev.util.Message;
     
     def Message processData(Message message) {
         def productIdentifier = message.getProperty("productIdentifier");
         def validIdentifiers = message.getProperty("odata.productIdentifiers").split(",");
         
         boolean isValid = false;
         for (String id : validIdentifiers) {
             if (id.trim().equals(productIdentifier)) {
                 isValid = true;
                 break;
             }
         }
         
         message.setProperty("isExistProduct", isValid);
         return message;
     }
     ```

2. **SetIsExistProductVar**:
   - Type: Content Modifier
   - Action: Set Property
   - Property Name: isExistProduct
   - Property Value: ${isExistProduct}

3. **LogValidRequest**:
   - Type: Write to Message Log
   - Log Level: INFO
   - Message: The request is processed and sent downstream with the product identifier (${property.productIdentifier}).

4. **LogInvalidRequest**:
   - Type: Write to Message Log
   - Log Level: WARN
   - Message: The product identifier (${property.productIdentifier}) was not passed in the request or was passed incorrectly.

5. **ConstructODataQuery**:
   - Type: Content Modifier
   - Action: Set Property
   - Property Name: filter
   - Property Value: ProductId eq '${property.productIdentifier}'
   - Property Name: select
   - Property Value: ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit

6. **TransformResponse**:
   - Type: Content Modifier
   - Action: Set Body
   - Body: ${body}
   - Content Type: application/json

7. **CreateErrorResponse**:
   - Type: Content Modifier
   - Action: Set Body
   - Body:
     ```json
     {
       "status": "error",
       "message": "The product identifier ${property.productIdentifier} was not found.",
       "errorCode": "PRODUCT_NOT_FOUND"
     }
     ```
   - Content Type: application/json

#### Router Configuration
- **IsProductValid**:
  - Condition 1: ${property.isExistProduct} == true
  - Default Route: No route (to LogInvalidRequest)

## Environment Configuration

### Important Configuration Parameters
- **HTTP Listener Configuration**:
  - Name: HTTP_Listener_config
  - Host and port settings to be determined based on deployment environment

- **HANA HTTP Request Configuration**:
  - Name: Hana_HTTP_Request_Configuration
  - Base URL to be determined based on SAP HANA environment

- **API Configuration**:
  - Name: products-config
  - RAML file: products.raml
  - Outbound headers map name: outboundHeaders
  - HTTP status variable name: httpStatus

### Environment Variables
- **odata.productIdentifiers**: Comma-separated list of valid product identifiers
  - Example value: "PR001,PR002,PR003,PR004,PR005"

### Dependencies on External Systems
- **SAP HANA**: The API depends on an SAP HANA OData service for retrieving product information
  - Connection details to be determined based on the SAP HANA environment

### Security Settings
- Authentication mechanism not explicitly defined in the source documentation
- Recommended to implement appropriate authentication based on security requirements:
  - OAuth 2.0
  - Basic Authentication
  - API Key
  - Client Certificates

### Deployment Considerations
- Ensure proper network connectivity between the integration platform and SAP HANA
- Configure appropriate timeouts for HTTP requests to SAP HANA
- Implement monitoring and alerting for API availability and performance
- Consider implementing caching for frequently accessed products to improve performance

### Required Resources
- Memory and CPU requirements to be determined based on expected load
- Disk space requirements minimal (primarily for logging)
- Network bandwidth to handle expected request volume

## API Reference

### Complete List of Endpoints

| HTTP Method | Endpoint | Description |
|-------------|----------|-------------|
| GET | /products | Retrieve product information by product identifier |

### Request and Response Schemas

#### GET /products

**Request Parameters**:
- **Query Parameters**:
  - `productIdentifier` (string, required): The unique identifier of the product to retrieve

**Response Schema**:
- **Success Response (200 OK)**:
  ```json
  {
    "ProductId": "string",
    "Category": "string",
    "CategoryName": "string",
    "CurrencyCode": "string",
    "DimensionDepth": "number",
    "DimensionHeight": "number",
    "DimensionUnit": "string",
    "DimensionWidth": "number",
    "LongDescription": "string",
    "Name": "string",
    "PictureUrl": "string",
    "Price": "number",
    "QuantityUnit": "string",
    "ShortDescription": "string",
    "SupplierId": "string",
    "Weight": "number",
    "WeightUnit": "string"
  }
  ```

- **Error Response (400 Bad Request)**:
  ```json
  {
    "status": "error",
    "message": "The product identifier [identifier] was not found.",
    "errorCode": "PRODUCT_NOT_FOUND"
  }
  ```

### Error Codes

| Error Code | Description |
|------------|-------------|
| PRODUCT_NOT_FOUND | The provided product identifier is not valid or not found |
| APIKIT:BAD_REQUEST | The request is malformed or missing required parameters |
| APIKIT:NOT_FOUND | The requested resource does not exist |
| APIKIT:METHOD_NOT_ALLOWED | The HTTP method is not supported for the requested resource |
| APIKIT:NOT_ACCEPTABLE | The server cannot produce a response matching the list of acceptable values |
| APIKIT:UNSUPPORTED_MEDIA_TYPE | The request entity has a media type which the server does not support |
| APIKIT:NOT_IMPLEMENTED | The server does not support the functionality required to fulfill the request |

### Authentication Requirements
Authentication requirements are not explicitly defined in the source documentation. Implementation should be based on security requirements for the specific deployment environment.

### Rate Limiting Information
Rate limiting information is not specified in the source documentation. Implementation should be based on performance requirements and resource constraints for the specific deployment environment.

### Pagination Details
Pagination is not implemented in the current API design. All product details are returned in a single response.

### Versioning Information
Versioning information is not explicitly defined in the source documentation. The API is defined in a RAML file named "products.raml", which may contain versioning information.