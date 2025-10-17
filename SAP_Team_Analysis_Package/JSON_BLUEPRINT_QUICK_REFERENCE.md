# JSON Blueprint Quick Reference Guide

## Component Types Quick Reference

### 1. Enricher
```json
{
  "type": "enricher",
  "id": "enricher_1",
  "name": "Component Name",
  "config": {
    "headers": {"Header-Name": "value"},
    "properties": "prop1=value1,prop2=value2",
    "file_operations": "generate_csv,apply_pgp_encryption"
  }
}
```

### 2. Script
```json
{
  "type": "script",
  "id": "script_1",
  "name": "Script Name",
  "config": {
    "script_content": "// Groovy script content",
    "input_variables": ["var1", "var2"],
    "output_variables": ["result1", "result2"]
  }
}
```

### 3. Request-Reply
```json
{
  "type": "request_reply",
  "id": "request_reply_1",
  "name": "API Call Name",
  "config": {
    "endpoint_path": "/api/endpoint",
    "method": "GET|POST|PUT|DELETE",
    "url": "https://example.com/api/endpoint",
    "headers": "Content-Type=application/json,Authorization=Bearer token"
  }
}
```

### 4. SFTP
```json
{
  "type": "sftp",
  "id": "sftp_1",
  "name": "SFTP Upload",
  "config": {
    "host": "sftp.example.com",
    "port": "22",
    "path": "/uploads/",
    "username": "sftp_user",
    "password": "sftp_password"
  }
}
```

### 5. Gateway
```json
{
  "type": "gateway",
  "id": "gateway_1",
  "name": "Decision Gateway",
  "config": {
    "gateway_type": "exclusive|parallel|inclusive",
    "routing_conditions": [
      {
        "condition": "${message.status == 'success'}",
        "target": "success_path"
      }
    ]
  }
}
```

### 6. OData
```json
{
  "type": "odata",
  "id": "odata_1",
  "name": "OData Query",
  "config": {
    "service_url": "https://example.com/odata/service",
    "entity_set": "EntityName",
    "operation": "GET|POST|PUT|DELETE",
    "query_options": "$select=field1,field2&$filter=condition"
  }
}
```

### 7. Message Mapping
```json
{
  "type": "message_mapping",
  "id": "mapping_1",
  "name": "Data Mapping",
  "config": {
    "mapping_name": "MappingName",
    "source_schema": "source.xsd",
    "target_schema": "target.xsd",
    "mapping_rules": {
      "source_field": "target_field"
    }
  }
}
```

## Error Handling Patterns

### Exception Subprocess
```json
{
  "type": "exception_subprocess",
  "id": "exception_1",
  "name": "Handle Errors",
  "config": {
    "error_type": "All|Timeout|Validation|Connection",
    "components": [
      {
        "type": "enricher",
        "name": "Log Error",
        "config": {
          "error_logging": "detailed",
          "error_properties": "error_message,stack_trace"
        }
      }
    ]
  }
}
```

### Retry Policy
```json
{
  "retry_policy": {
    "max_retries": 3,
    "retry_delay": "5000",
    "backoff_multiplier": 2,
    "retry_conditions": ["timeout", "connection_error"]
  }
}
```

## Flow Control Patterns

### Linear Flow
```json
{
  "flow": [
    "enricher_1",
    "script_1",
    "request_reply_1",
    "sftp_1"
  ]
}
```

### Conditional Flow
```json
{
  "branching": {
    "type": "exclusive",
    "branches": [
      {
        "condition": "success",
        "components": ["success_component_1", "success_component_2"]
      },
      {
        "condition": "error",
        "components": ["error_component_1", "error_component_2"]
      }
    ]
  }
}
```

### Parallel Flow
```json
{
  "branching": {
    "type": "parallel",
    "branches": [
      {
        "condition": "process_data",
        "components": ["component_1", "component_2"],
        "parallel_execution": true
      }
    ]
  }
}
```

## Common Configuration Patterns

### Environment Variables
```json
{
  "url": "https://{{BASE_URL}}/api/endpoint",
  "headers": "Authorization=Bearer {{ACCESS_TOKEN}}",
  "username": "{{SFTP_USERNAME}}",
  "password": "{{SFTP_PASSWORD}}"
}
```

### Dynamic Properties
```json
{
  "properties": "process_id={{uuid}},timestamp=now(),date={{date}}"
}
```

### File Operations
```json
{
  "file_operations": "generate_csv,apply_pgp_encryption,compress_file",
  "output_filename": "data_{{timestamp}}.csv",
  "encryption_key": "{{PGP_PUBLIC_KEY}}"
}
```

## Validation Checklist

- [ ] All component IDs are unique within each endpoint
- [ ] All flow references point to existing components
- [ ] All sequence flows reference existing components
- [ ] Configuration objects match component type requirements
- [ ] Error handling is comprehensive
- [ ] Environment variables use {{VARIABLE_NAME}} format
- [ ] Script content is valid and complete
- [ ] Authentication credentials are properly configured

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| Component ID conflict | Duplicate component IDs | Ensure unique IDs within endpoint |
| Missing flow reference | Component in flow doesn't exist | Verify component exists in components array |
| Invalid configuration | Config doesn't match component type | Check component type requirements |
| Missing environment variable | {{VARIABLE}} not defined | Define variable in environment or config |
| Script syntax error | Invalid Groovy syntax | Validate script content |

## Performance Tips

1. **Use parallel processing** for independent operations
2. **Implement caching** for frequently accessed data
3. **Set appropriate timeouts** for external calls
4. **Batch process** multiple records when possible
5. **Monitor resource usage** and optimize accordingly

## Security Best Practices

1. **Use secure authentication** methods (OAuth2, API keys)
2. **Encrypt sensitive data** in transit and at rest
3. **Implement access controls** for different user roles
4. **Audit all operations** for security compliance
5. **Use environment variables** for sensitive configuration

## Troubleshooting Steps

1. **Check component IDs** for uniqueness
2. **Validate JSON syntax** using a JSON validator
3. **Verify flow references** point to existing components
4. **Test components individually** before testing full flow
5. **Check environment variables** are properly defined
6. **Review error logs** for detailed error information
7. **Validate script content** for syntax errors
8. **Test with sample data** to verify functionality

This quick reference guide provides essential information for creating and troubleshooting JSON blueprints efficiently.
