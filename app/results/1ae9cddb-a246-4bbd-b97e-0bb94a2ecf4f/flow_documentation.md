# MuleSoft Application Documentation

## Overview

This document provides a comprehensive overview of the MuleSoft application's flows, subflows, configurations, and error handling strategies.

# Flows

## Flow: products-main

This flow performs the following operations:

<ol>
  <li><strong>products-main</strong> (flow)

    Executes `flow` component.
  </li>
  <li>listener

    Executes `listener` component.
  </li>
  <li>response

    Executes `response` component.
  </li>
  <li>headers

    Executes `headers` component.
  </li>
  <li>error-response

    Executes `error-response` component.
  </li>
  <li>body

    Executes `body` component.
  </li>
  <li>headers

    Executes `headers` component.
  </li>
  <li>router

    Executes `router` component.
  </li>
</ol>


## Flow: products-console

This flow performs the following operations:

<ol>
  <li><strong>products-console</strong> (flow)

    Executes `flow` component.
  </li>
  <li>listener

    Executes `listener` component.
  </li>
  <li>response

    Executes `response` component.
  </li>
  <li>headers

    Executes `headers` component.
  </li>
  <li>error-response

    Executes `error-response` component.
  </li>
  <li>body

    Executes `body` component.
  </li>
  <li>headers

    Executes `headers` component.
  </li>
  <li>console

    Executes `console` component.
  </li>
</ol>


## Flow: get:\products:products-config

This flow performs the following operations:

<ol>
  <li><strong>get:\products:products-config</strong> (flow)

    Executes `flow` component.
  </li>
  <li><strong>get-product-details-flow</strong> (flow-ref)

    Executes `flow-ref` component.
  </li>
</ol>


# Subflows

## Flow: get-product-details-flow

This flow performs the following operations:

<ol>
  <li><strong>get-product-details-flow</strong> (sub-flow)

    Executes `sub-flow` component.
  </li>
  <li>transform

    • Set `isExistProduct` =

      ```
      %dw 2.0
output application/java
var productidentifer=p('odata.productIdentifiers') splitBy(",")
---
sizeOf(productidentifer filter ($ == attributes.queryParams.productIdentifier))>0
      ```
  </li>
  <li>message

    Executes `message` component.
  </li>
  <li>variables

    Executes `variables` component.
  </li>
  <li>set-variable

    Executes `set-variable` component.
  </li>
  <li>choice

    **Conditions:**
      - `#[vars.isExistProduct]`
  </li>
  <li>when

    Executes `when` component.
  </li>
  <li>logger

    • Log message: "The request is processed and sent downstream with the product identifier (#[attributes.queryParams.productIdentifier])."
  </li>
  <li>request

    **Query parameters (raw):**

    ```
#[output application/java
---
{
	"$filter" : "ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'",
	"$select" : "ProductId,Category,CategoryName,CurrencyCode,DimensionDepth,DimensionHeight,DimensionUnit,DimensionWidth,LongDescription,Name,PictureUrl,Price,QuantityUnit,ShortDescription,SupplierId,Weight,WeightUnit"
}]
    ```

    • OData `$filter`: `ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'`

    • OData `$select`: `ProductId`

    • All OData parameters:
      - **$filter**: `ProductId eq '" ++ (attributes.queryParams.productIdentifier default '') ++ "'`
      - **$select**: `ProductId`
  </li>
  <li>query-params

    Executes `query-params` component.
  </li>
  <li>transform

    **Transform payload:**

    ```
%dw 2.0
output application/json
---
payload
    ```
  </li>
  <li>message

    Executes `message` component.
  </li>
  <li>set-payload

    Executes `set-payload` component.
  </li>
  <li>otherwise

    Executes `otherwise` component.
  </li>
  <li>logger

    • Log message: "The product identifier (#[attributes.queryParams.productIdentifier]) was not passed in the request or was passed incorrectly."
  </li>
  <li>transform

    **Transform payload:**

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
  </li>
  <li>message

    Executes `message` component.
  </li>
  <li>set-payload

    Executes `set-payload` component.
  </li>
</ol>


## Configurations

The application uses the following configurations:

### HTTP_Listener_config
Type: listener-config
Configuration details:
- name: HTTP_Listener_config

### Hana_HTTP_Request_Configuration
Type: request-config
Configuration details:
- name: Hana_HTTP_Request_Configuration

### products-config
Type: config
Configuration details:
- name: products-config
- api: products.raml
- outboundHeadersMapName: outboundHeaders
- httpStatusVarName: httpStatus

## Error Handling

The application implements the following error handling strategies:

### Gobal_Error_Handler
- Handles APIKIT:BAD_REQUEST errors using on-error-propagate
- Handles APIKIT:NOT_FOUND errors using on-error-propagate
- Handles APIKIT:METHOD_NOT_ALLOWED errors using on-error-propagate
- Handles APIKIT:NOT_ACCEPTABLE errors using on-error-propagate
- Handles APIKIT:UNSUPPORTED_MEDIA_TYPE errors using on-error-propagate
- Handles APIKIT:NOT_IMPLEMENTED errors using on-error-propagate



# Additional Resources

This section contains documentation for additional resources used in the Mule application.



## Error Adding Additional Resources

An error occurred while adding additional resources to the documentation: sequence item 0: expected str instance, int found
