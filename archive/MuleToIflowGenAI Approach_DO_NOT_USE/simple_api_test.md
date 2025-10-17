# Simple Product API

## Overview
This API provides access to product information.

## Base URL
`https://example.com/api`

## Endpoints

### Get Products
Retrieves a list of all products.

**Method**: GET  
**Path**: `/products`  
**Response**: JSON array of product objects

**Process Flow**:
1. Prepare request headers
2. Log the request
3. Call OData Products service
4. Set response headers
5. Transform response to required format

### Get Product Details
Retrieves details for a specific product.

**Method**: GET  
**Path**: `/products/{id}`  
**Parameters**: 
- `id` (path parameter): The product ID

**Response**: JSON object with product details

**Process Flow**:
1. Extract product ID from request
2. Log the request with product ID
3. Call OData Product Detail service
4. Set response headers
5. Transform product detail to required format
