# API Overview
- This API provides product details from an SAP HANA database
- Base URL pattern: `/products`

# Endpoints

## GET /products
- **Purpose**: Retrieves product details based on a product identifier
- **Query Parameters**:
  - `productIdentifier` (required): The unique identifier of the product
- **Response Format**: JSON
- **Status Codes**:
  - 200: Success
  - 400: Bad Request
  - 404: Product Not Found
- **Response Body**: Product details including ProductId, Category, CategoryName, CurrencyCode, dimensions, descriptions, price, and other product attributes

# Current MuleSoft Flow Logic

## Flow: products-main
This is the main entry point for the API, triggered by an HTTP listener. It handles routing to the appropriate endpoints defined in the RAML specification.

1. **Trigger**: HTTP listener
2. **Processing**:
   - Sets response headers
   - Routes requests based on the API configuration
   - Handles errors with a dedicated error response handler
3. **Outcome**: Routes to the appropriate flow based on the endpoint requested

## Flow: products-console
This appears to be a console/logging version of the API, likely for debugging or monitoring purposes.

1. **Trigger**: HTTP listener
2. **Processing**:
   - Sets response headers
   - Outputs to console
   - Handles errors with a dedicated error response handler
3. **Outcome**: Logs API activity to the console

## Flow: get:\products:products-config
This flow handles GET requests to the `/products` endpoint.

1. **Trigger**: GET request to `/products`
2. **Processing**: Calls the `get-product-details-flow` subflow
3. **Outcome**: Returns product details or an error response

## Subflow: get-product-details-flow
This subflow retrieves product details from SAP HANA.

1. **Validation**: Checks if the provided product identifier is valid
   ```
   %dw 2.0
   output application/java
   var productidentifer=p('odata.productIdentifiers') splitBy(",")
   ---
   sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
   ```

2. **Conditional Processing**:
   - If product identifier is valid:
     - Logs the request
     - Makes an HTTP request to SAP HANA with OData query parameters:
       - `$filter`: `ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'`
       - `$select`: `ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit`
     - Transforms the response to JSON
   - If product identifier is invalid:
     - Logs the error
     - Returns an error response

3. **Error Handling**: Global error handler for API Kit errors (BAD_REQUEST, NOT_FOUND, etc.)

# DataWeave Transformations Explained

## Product Identifier Validation
```
%dw 2.0
output application/java
var productidentifer=p('odata.productIdentifiers') splitBy(",")
---
sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
```

This transformation:
1. Retrieves a comma-separated list of valid product identifiers from a property
2. Splits the string into an array
3. Filters the array to find matches with the requested product identifier
4. Returns true if at least one match is found (size > 0)

## OData Query Parameters Construction
```
#[output application/java
---
{
	"$filter" : "ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'",
	"$select" : "ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit"
}]
```

This transformation:
1. Creates a map with OData query parameters
2. Constructs a filter expression that matches the exact product identifier
3. Specifies which fields to select from the product data

## Response Payload Transformation
```
%dw 2.0
output application/json
---
payload
```

This simple transformation converts the response payload to JSON format without modifying its structure.

## Error Response Transformation
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

This transformation:
1. Creates a standardized error response structure
2. Includes the invalid product identifier in the error message
3. Sets a specific error code for product not found scenarios

# SAP Integration Suite Implementation

## Component Mapping

| MuleSoft Component | SAP Integration Suite Equivalent |
|--------------------|----------------------------------|
| HTTP Listener | HTTPS Adapter (Server) |
| HTTP Request | HTTPS Adapter (Client) |
| Router | Content Modifier + Router |
| Flow Reference | Process Call |
| Transform | Message Mapping |
| Logger | Write to Log |
| Choice/When/Otherwise | Router with multiple branches |
| Set Variable | Content Modifier (with header/property assignment) |
| Set Payload | Content Modifier (with body assignment) |
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
router1 --> response1[Response Handler]:::contentModifier
response1 --> headers1[Set Headers]:::contentModifier
response1 --> errorResponse[Error Response]:::exception

%% Error handling
errorResponse --> body1[Set Body]:::contentModifier
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
listener2 --> response2[Response Handler]:::contentModifier
response2 --> headers3[Set Headers]:::contentModifier
response2 --> errorResponse2[Error Response]:::exception
errorResponse2 --> body2[Set Body]:::contentModifier
body2 --> headers4[Set Headers]:::contentModifier
headers3 --> console[Console Output]:::contentModifier
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
start3((Start)) --> getProductsFlow[[get-product-details-flow]]:::processCall
getProductsFlow --> end3((End))
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
start4((Start)) --> transform1[Validate Product ID]:::mapping
transform1 --> setVar[Set Variable]:::contentModifier
setVar --> choice{Product Exists?}:::router
choice -->|Yes| logger1[Log Request]:::contentModifier
choice -->|No| logger2[Log Error]:::contentModifier
logger1 --> request[HTTP Request to SAP HANA]:::httpAdapter
request --> transform2[Transform to JSON]:::mapping
transform2 --> end4((End))
logger2 --> errorTransform[Create Error Response]:::mapping
errorTransform --> end4
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

%% Error Handling: Global_Error_Handler
start5((Error)) --> errorHandler[(Global Error Handler)]:::exception
errorHandler --> apiKitBadRequest[APIKIT:BAD_REQUEST]:::exception
errorHandler --> apiKitNotFound[APIKIT:NOT_FOUND]:::exception
errorHandler --> apiKitMethodNotAllowed[APIKIT:METHOD_NOT_ALLOWED]:::exception
errorHandler --> apiKitNotAcceptable[APIKIT:NOT_ACCEPTABLE]:::exception
errorHandler --> apiKitUnsupportedMediaType[APIKIT:UNSUPPORTED_MEDIA_TYPE]:::exception
errorHandler --> apiKitNotImplemented[APIKIT:NOT_IMPLEMENTED]:::exception
```

## Configuration Details

### HTTP Listener Configuration
- Component: HTTPS Adapter (Server)
- Parameters:
  - Name: HTTP_Listener_config
  - Port: [Configure based on deployment environment]
  - Host: [Configure based on deployment environment]
  - Path: /api/*

### HTTP Request Configuration
- Component: HTTPS Adapter (Client)
- Parameters:
  - Name: Hana_HTTP_Request_Configuration
  - Base URL: [SAP HANA OData service URL]
  - Authentication: [Configure based on SAP HANA requirements]

### Router Configuration
- Component: Router
- Routes defined in RAML specification (products.raml)
- Outbound Headers Map Name: outboundHeaders
- HTTP Status Variable Name: httpStatus

### OData Request Configuration
- Component: HTTPS Adapter (Client)
- Query Parameters:
  - $filter: ProductId eq '[productIdentifier]'
  - $select: ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit

# Configuration

## Important Configuration Parameters
- odata.productIdentifiers: Comma-separated list of valid product identifiers

## Environment Variables
- None explicitly mentioned in the source documentation

## Dependencies on External Systems
- SAP HANA database (accessed via HTTP/OData)

## Security Settings
- Authentication configuration for SAP HANA access (not explicitly defined in source)