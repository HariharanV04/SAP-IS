# SAP Integration Suite iFlow JSON Component Schema

## Standard JSON Format for iFlow Components

### Root Structure
```json
{
    "endpoints": [
        {
            "id": "endpoint_id",
            "name": "Endpoint Name",
            "components": [...],
            "flow": [...] // Optional: explicit flow sequence
        }
    ]
}
```

### Component Types and Their Configurations

#### 1. Enricher Component
```json
{
    "type": "enricher",
    "id": "enricher_1",
    "name": "Set Properties",
    "config": {
        "headers": {
            "Content-Type": "application/json",
            "X-Custom-Header": "value"
        },
        "properties": {
            "property.name": "property.value",
            "another.property": "another.value"
        }
    }
}
```

#### 2. Script Component
```json
{
    "type": "script",
    "id": "script_1",
    "name": "Process Data",
    "config": {
        "script_file": "script_name.groovy",
        "script_content": "// Groovy script content\nlog.info('Processing data');\nreturn message;"
    }
}
```

#### 3. Request-Reply Component
```json
{
    "type": "request_reply",
    "id": "request_reply_1",
    "name": "Call External Service",
    "config": {
        "endpoint_path": "/api/endpoint",
        "method": "GET|POST|PUT|DELETE",
        "url": "https://example.com/api/endpoint"
    }
}
```

#### 4. SFTP Component
```json
{
    "type": "sftp",
    "id": "sftp_1",
    "name": "Upload File",
    "config": {
        "host": "sftp.example.com",
        "port": 22,
        "path": "/remote/path",
        "username": "sftp_user",
        "password": "sftp_password"
    }
}
```

#### 5. OData Component
```json
{
    "type": "odata",
    "id": "ODataCall_1",
    "name": "Query Data",
    "config": {
        "service_url": "https://example.com/api/service",
        "entity_set": "EntitySetName",
        "operation": "GET|POST|PUT|DELETE"
    }
}
```

#### 6. Local Integration Process (LIP)
```json
{
    "type": "lip",
    "id": "lip_1",
    "name": "Process Data",
    "config": {
        "process_id": "Process_Data_Processing",
        "process_name": "Data Processing LIP",
        "script_name": "data_processing.groovy",
        "activity_type": "DataProcessing"
    }
}
```

### Flow Array (Optional)
```json
{
    "flow": [
        "enricher_1",
        "script_1",
        "request_reply_1",
        "sftp_1",
        "ODataCall_1"
    ]
}
```

## Key Rules

1. **Component IDs**: Must be unique within the endpoint
2. **Script Files**: Use `script_file` for file path and `script_content` for inline content
3. **Flow Array**: If provided, defines the sequence of component execution
4. **Config Objects**: Each component type has specific required config fields
5. **Naming**: Use descriptive names for components and IDs

## Common Issues to Avoid

1. **Script Configuration**: Don't mix script content with file paths
2. **Missing Flow**: Include flow array for explicit sequence control
3. **Invalid IDs**: Ensure all component IDs in flow array exist in components
4. **Config Structure**: Follow the exact config structure for each component type





