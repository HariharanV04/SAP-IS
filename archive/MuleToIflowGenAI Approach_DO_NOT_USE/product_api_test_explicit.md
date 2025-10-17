# Product Information API

## Overview
This API provides access to product information stored in a backend system. It allows clients to retrieve product details, search for products, and update product information. All endpoints follow a request-reply pattern.

## Endpoints

### GET /products
Retrieves a list of all products with basic information. This endpoint implements a request-reply pattern.

**Request:**
- Headers:
  - Authorization: Bearer token
  - Accept: application/json

**Response:**
- Status: 200 OK
- Body:
```json
{
  "products": [
    {
      "id": "P001",
      "name": "Laptop Pro",
      "category": "Electronics",
      "price": 1299.99,
      "inStock": true
    },
    {
      "id": "P002",
      "name": "Wireless Headphones",
      "category": "Audio",
      "price": 199.99,
      "inStock": true
    }
  ],
  "totalCount": 2
}
```

**Processing Steps (Request-Reply Flow):**
1. Validate the authorization token
2. Log the incoming request details
3. Call OData service to retrieve product list from backend system
4. Transform the backend response to the API format
5. Set appropriate response headers
6. Return the response

### GET /products/{id}
Retrieves detailed information about a specific product. This endpoint implements a request-reply pattern.

**Path Parameters:**
- id: Product identifier

**Request:**
- Headers:
  - Authorization: Bearer token
  - Accept: application/json

**Response:**
- Status: 200 OK
- Body:
```json
{
  "id": "P001",
  "name": "Laptop Pro",
  "description": "High-performance laptop with 16GB RAM and 512GB SSD",
  "category": "Electronics",
  "price": 1299.99,
  "specifications": {
    "processor": "Intel Core i7",
    "memory": "16GB",
    "storage": "512GB SSD",
    "display": "15.6 inch 4K"
  },
  "inStock": true,
  "availableQuantity": 45,
  "ratings": {
    "average": 4.7,
    "count": 128
  }
}
```

**Error Responses:**
- 404 Not Found: If the product doesn't exist
- 401 Unauthorized: If the authorization token is invalid
- 500 Internal Server Error: For server-side issues

**Processing Steps (Request-Reply Flow):**
1. Validate the authorization token
2. Extract product ID from the path
3. Log the incoming request with product ID
4. Call OData service with the product ID parameter
5. Check if product exists
   - If not, return 404 error
6. Transform the backend response to the API format
7. Set appropriate response headers
8. Return the response

### POST /products/search
Searches for products based on various criteria. This endpoint implements a request-reply pattern.

**Request:**
- Headers:
  - Authorization: Bearer token
  - Content-Type: application/json
- Body:
```json
{
  "keywords": "wireless headphones",
  "category": "Audio",
  "priceRange": {
    "min": 50,
    "max": 300
  },
  "inStockOnly": true,
  "sortBy": "price",
  "sortOrder": "asc",
  "page": 1,
  "pageSize": 10
}
```

**Response:**
- Status: 200 OK
- Body:
```json
{
  "products": [
    {
      "id": "P002",
      "name": "Wireless Headphones",
      "category": "Audio",
      "price": 199.99,
      "inStock": true
    }
  ],
  "totalCount": 1,
  "page": 1,
  "pageSize": 10,
  "totalPages": 1
}
```

**Processing Steps (Request-Reply Flow):**
1. Validate the authorization token
2. Validate the search criteria
3. Log the search request
4. Transform search criteria to OData query parameters
5. Call OData service with search parameters
6. Transform the backend response to the API format
7. Add pagination information
8. Set appropriate response headers
9. Return the response

## Backend Integration Details

### OData Service
- Service URL: https://backend-system.example.com/odata/Products
- Authentication: OAuth 2.0
- Operations:
  - GET /Products - Retrieve all products
  - GET /Products('{id}') - Retrieve a specific product
  - GET /Products/Search - Search for products with query parameters

### Error Handling
- All errors should be logged with correlation IDs
- Backend timeouts should be handled gracefully
- Authentication failures should return appropriate error messages

## Performance Requirements
- API should respond within 500ms for GET requests
- Search operations should complete within 1 second
- Connection pooling should be used for backend calls

## Security Requirements
- All requests must include a valid JWT token
- Sensitive data should be masked in logs
- Rate limiting should be applied (max 100 requests per minute per client)
