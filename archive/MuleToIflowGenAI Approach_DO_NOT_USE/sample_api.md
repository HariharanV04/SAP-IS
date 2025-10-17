# Product API

This API provides access to product information.

## Endpoints

### GET /products

Retrieves a list of all products.

**Response:**
```json
{
  "products": [
    {
      "id": "123",
      "name": "Product 1",
      "description": "Description of product 1",
      "price": 19.99
    },
    {
      "id": "456",
      "name": "Product 2",
      "description": "Description of product 2",
      "price": 29.99
    }
  ]
}
```

### GET /products/{id}

Retrieves a specific product by ID.

**Parameters:**
- `id` (path): The ID of the product to retrieve

**Response:**
```json
{
  "id": "123",
  "name": "Product 1",
  "description": "Description of product 1",
  "price": 19.99
}
```

### POST /products

Creates a new product.

**Request Body:**
```json
{
  "name": "New Product",
  "description": "Description of new product",
  "price": 39.99
}
```

**Response:**
```json
{
  "id": "789",
  "name": "New Product",
  "description": "Description of new product",
  "price": 39.99
}
```

### PUT /products/{id}

Updates an existing product.

**Parameters:**
- `id` (path): The ID of the product to update

**Request Body:**
```json
{
  "name": "Updated Product",
  "description": "Updated description",
  "price": 49.99
}
```

**Response:**
```json
{
  "id": "123",
  "name": "Updated Product",
  "description": "Updated description",
  "price": 49.99
}
```

### DELETE /products/{id}

Deletes a product.

**Parameters:**
- `id` (path): The ID of the product to delete

**Response:**
```json
{
  "message": "Product deleted successfully"
}
```
