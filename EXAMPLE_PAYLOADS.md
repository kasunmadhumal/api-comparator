# Example Payloads for Testing

This file contains sample payloads for common API testing scenarios.

## Example 1: Flight API

### Test Case 1: Valid Flight Number
```json
{
  "flightNumber": "AA123",
  "date": "2025-11-12",
  "origin": "JFK",
  "destination": "LAX"
}
```

### Test Case 2: International Flight
```json
{
  "flightNumber": "BA456",
  "date": "2025-11-15",
  "origin": "LHR",
  "destination": "JFK"
}
```

### Test Case 3: Invalid Flight Number
```json
{
  "flightNumber": "INVALID",
  "date": "2025-11-12",
  "origin": "JFK",
  "destination": "LAX"
}
```

## Example 2: User API

### Test Case 1: Get User by ID
```json
{
  "userId": "12345",
  "includeDetails": true
}
```

### Test Case 2: Search Users
```json
{
  "query": "john@example.com",
  "filters": {
    "status": "active",
    "role": "admin"
  }
}
```

## Example 3: E-commerce API

### Test Case 1: Get Product Details
```json
{
  "productId": "PROD-001",
  "includeInventory": true,
  "includeReviews": true
}
```

### Test Case 2: Search Products
```json
{
  "searchTerm": "laptop",
  "category": "electronics",
  "priceRange": {
    "min": 500,
    "max": 2000
  },
  "sortBy": "price_asc"
}
```

## Example 4: Weather API (GET with Query Params)

Query params format: `city=London&units=metric&days=7`

## Tips for Creating Test Cases

1. **Positive Test Cases**: Valid inputs that should succeed
2. **Negative Test Cases**: Invalid inputs to test error handling
3. **Edge Cases**: Boundary values, empty strings, null values
4. **Performance Tests**: Large datasets, concurrent requests
5. **Security Tests**: SQL injection, XSS attempts (in safe environment)

## Best Practices

- Use descriptive test case names
- Test the same scenarios on both API versions
- Include edge cases and error scenarios
- Document expected results
- Keep payloads organized by feature/module
