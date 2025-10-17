# API Overview
- This API provides product details from an SAP HANA database
- Base URL pattern: `/products`

# Endpoints

## GET /products
- **Purpose**: Retrieves product details based on a product identifier
- **Query Parameters**: 
  - `productIdentifier` (required): The unique identifier for the product
- **Response Format**: JSON
- **Status Codes**:
  - 200: Success
  - 400: Bad Request
  - 404: Product Not Found
- **Response Body**: Product details including ProductId, Category, CategoryName, CurrencyCode, dimensions, descriptions, price, and other product attributes

# Current MuleSoft Flow Logic

## Flow: products-main
This is the main entry point for the API that handles HTTP requests.
1. **Trigger**: HTTP listener
2. **Processing**: Routes requests to appropriate handlers
3. **Response**: Returns HTTP response with appropriate headers
4. **Error Handling**: Provides error responses with appropriate status codes

## Flow: products-console
This flow appears to be a console-based entry point, possibly for testing or monitoring.
1. **Trigger**: HTTP listener
2. **Processing**: Outputs to console
3. **Response**: Returns HTTP response with appropriate headers
4. **Error Handling**: Provides error responses

## Flow: get:\products:products-config
This flow handles GET requests to the `/products` endpoint.
1. **Trigger**: HTTP GET request to `/products`
2. **Processing**: References the `get-product-details-flow` subflow

## Subflow: get-product-details-flow
This subflow retrieves product details from SAP HANA.
1. **Validation**: Checks if the provided product identifier is valid
2. **Processing**:
   - If valid: Makes an HTTP request to SAP HANA OData service
   - If invalid: Returns an error message
3. **Data Transformation**: Transforms the response to the required format
4. **Technical Details**:
   - OData query parameters:
     - `$filter`: `ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'`
     - `$select`: `ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit`

# DataWeave Transformations Explained

## Product Identifier Validation Transformation
This transformation checks if the provided product identifier is in the list of allowed product identifiers.

- **Input**: Query parameters from the HTTP request
- **Output**: Boolean value indicating if the product identifier is valid
- **Key Operations**: 
  - `splitBy` to convert a comma-separated string to an array
  - `filter` to check if the product identifier is in the array
  - `sizeOf` to determine if any matches were found

```dw
%dw 2.0
output application/java
var productidentifer=p('odata.productIdentifiers') splitBy(",")
---
sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
```

## OData Query Parameters Transformation
This transformation constructs the OData query parameters for the SAP HANA request.

- **Input**: Query parameters from the HTTP request
- **Output**: OData query parameters
- **Key Operations**: String concatenation to build the filter expression

```dw
#[output application/java
---
{
	"$filter" : "ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'",
	"$select" : "ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit"
}]
```

## Response Payload Transformation (Success)
This transformation passes through the payload from the SAP HANA response.

- **Input**: JSON response from SAP HANA
- **Output**: JSON response to the client
- **Key Operations**: Simple pass-through

```dw
%dw 2.0
output application/json
---
payload
```

## Error Response Transformation
This transformation creates an error response when the product identifier is not valid.

- **Input**: Query parameters from the HTTP request
- **Output**: JSON error response
- **Key Operations**: String concatenation to build the error message

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

| MuleSoft Component | SAP Integration Suite Equivalent |
|--------------------|----------------------------------|
| HTTP Listener | HTTPS Adapter (Server) |
| HTTP Request | HTTP Adapter (Client) |
| Router | Router |
| DataWeave Transform | Content Modifier with Script |
| Logger | Write to Log |
| Flow Reference | Process Call |
| Set Variable | Content Modifier |
| Choice/When/Otherwise | Router with multiple branches |
| Error Handler | Exception Subprocess |

## Integration Flow Visualization

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Flow: products-main
start1((Start)) --> listener1[HTTP Listener]:::httpAdapter
listener1 --> router1{Router}:::router
router1 --> response1[HTTP Response]:::httpAdapter
response1 --> headers1[Set Headers]:::contentModifier
router1 --> errorResponse1[Error Response]:::httpAdapter
errorResponse1 --> body1[Set Body]:::contentModifier
body1 --> headers2[Set Headers]:::contentModifier
```

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Flow: products-console
start2((Start)) --> listener2[HTTP Listener]:::httpAdapter
listener2 --> response2[HTTP Response]:::httpAdapter
response2 --> headers3[Set Headers]:::contentModifier
listener2 --> errorResponse2[Error Response]:::httpAdapter
errorResponse2 --> body2[Set Body]:::contentModifier
body2 --> headers4[Set Headers]:::contentModifier
headers4 --> console1[Write to Log]:::contentModifier
```

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Flow: get:\products:products-config
start3((Start)) --> getProductDetailsFlow[[get-product-details-flow]]:::processCall
```

```mermaid
flowchart TD
%% Define node styles
classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
classDef router fill:#FFB6C1,stroke:#333,stroke-width:2px
classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
classDef exception fill:#FFA07A,stroke:#333,stroke-width:2px
classDef processCall fill:#F0E68C,stroke:#333,stroke-width:2px

%% Subflow: get-product-details-flow
start4((Start)) --> transform1[Transform]:::mapping
transform1 --> message1[Message]:::contentModifier
message1 --> variables1[Variables]:::contentModifier
variables1 --> setVariable1[Set Variable]:::contentModifier
setVariable1 --> choice1{Choice}:::router
choice1 -->|isExistProduct| when1[When]:::router
when1 --> logger1[Write to Log]:::contentModifier
logger1 --> request1[HTTP Request]:::httpAdapter
request1 --> queryParams1[Query Params]:::contentModifier
queryParams1 --> transform2[Transform]:::mapping
transform2 --> message2[Message]:::contentModifier
message2 --> setPayload1[Set Payload]:::contentModifier
choice1 -->|otherwise| otherwise1[Otherwise]:::router
otherwise1 --> logger2[Write to Log]:::contentModifier
logger2 --> transform3[Transform]:::mapping
transform3 --> message3[Message]:::contentModifier
message3 --> setPayload2[Set Payload]:::contentModifier
```

## Configuration Details

### HTTP Listener Configuration
- **Component**: HTTPS Adapter (Server)
- **Parameters**:
  - Name: HTTP_Listener_config
  - Port: [To be configured]
  - Host: [To be configured]
  - Path: /products

### HTTP Request Configuration
- **Component**: HTTP Adapter (Client)
- **Parameters**:
  - Name: Hana_HTTP_Request_Configuration
  - URL: [SAP HANA OData service URL to be configured]
  - Method: GET
  - Authentication: [To be configured based on SAP HANA requirements]

### Transform Components
- **Component**: Content Modifier with Script
- **Parameters**:
  - Script language: Groovy or JavaScript (SAP Integration Suite equivalent to DataWeave)
  - Script content: Equivalent logic to the DataWeave transformations

### Router Component
- **Component**: Router
- **Parameters**:
  - Condition: ${property.isExistProduct} (equivalent to vars.isExistProduct in MuleSoft)

### Logger Components
- **Component**: Write to Log
- **Parameters**:
  - Log Level: INFO
  - Log Messages:
    - "The request is processed and sent downstream with the product identifier (${property.productIdentifier})."
    - "The product identifier (${property.productIdentifier}) was not passed in the request or was passed incorrectly."

# Configuration

## Important Configuration Parameters
- **odata.productIdentifiers**: Comma-separated list of valid product identifiers (from properties file)

## Environment Variables
- No explicit environment variables mentioned in the source documentation

## Dependencies on External Systems
- SAP HANA OData service for product data retrieval

## Security Settings
- Authentication configuration for SAP HANA HTTP Request (not explicitly defined in source)
- HTTPS configuration for API endpoints (not explicitly defined in source)