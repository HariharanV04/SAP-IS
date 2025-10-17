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

#### 1. Enricher Component (Content Modifier)
```json
{
    "type": "enricher",
    "id": "enricher_1",
    "name": "Set Properties",
    "activity_type": "Enricher",
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

#### 2. Script Component (Groovy Script)
```json
{
    "type": "script",
    "id": "script_1",
    "name": "Process Data",
    "activity_type": "Script",
    "config": {
        "script_file": "script_name.groovy",
        "script_content": "// Groovy script content\nlog.info('Processing data');\nreturn message;"
    }
}
```

#### 3. Request-Reply Component (RequestReply)
```json
{
    "type": "request_reply",
    "id": "request_reply_1",
    "name": "Call External Service",
    "activity_type": "RequestReply",
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
    "activity_type": "SFTP",
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
    "activity_type": "OData",
    "config": {
        "service_url": "https://example.com/api/service",
        "entity_set": "EntitySetName",
        "operation": "GET|POST|PUT|DELETE"
    }
}
```

#### 6. Router Component (Exclusive Gateway)
```json
{
    "type": "router",
    "id": "router_1",
    "name": "Decision Router",
    "activity_type": "exclusiveGateway",
    "config": {
        "gateway_type": "exclusive",
        "routing_conditions": [
            {
                "condition": "${message.status == 'success'}",
                "target": "success_path"
            },
            {
                "condition": "${message.status == 'error'}",
                "target": "error_path"
            }
        ],
        "default_flow": "default_path"
    }
}
```

#### 7. Endpoint Sender Component
```json
{
    "type": "endpoint_sender",
    "id": "sender_1",
    "name": "HTTPS Sender",
    "activity_type": "participant",
    "config": {
        "protocol": "HTTPS",
        "url_path": "/api/endpoint",
        "authentication": "Basic",
        "timeout": "60000"
    }
}
```

#### 8. Endpoint Receiver Component
```json
{
    "type": "endpoint_receiver",
    "id": "receiver_1",
    "name": "HTTP Receiver",
    "activity_type": "participant",
    "config": {
        "protocol": "HTTP",
        "url_path": "/receive",
        "method": "POST",
        "timeout": "60000"
    }
}
```

#### 9. Start Event Component
```json
{
    "type": "start_event",
    "id": "start_1",
    "name": "Start",
    "activity_type": "startEvent",
    "config": {
        "event_type": "message",
        "trigger": "incoming_message"
    }
}
```

#### 10. End Event Component
```json
{
    "type": "end_event",
    "id": "end_1",
    "name": "End",
    "activity_type": "endEvent",
    "config": {
        "event_type": "message",
        "completion": "success"
    }
}
```

#### 11. Local Integration Process (LIP)
```json
{
    "type": "lip",
    "id": "lip_1",
    "name": "Process Data",
    "activity_type": "DataProcessing",
    "config": {
        "process_id": "Process_Data_Processing",
        "process_name": "Data Processing LIP",
        "script_name": "data_processing.groovy"
    }
}
```

### Flow Array (Optional)
```json
{
    "flow": [
        "start_1",
        "enricher_1",
        "script_1",
        "request_reply_1",
        "router_1",
        "sftp_1",
        "ODataCall_1",
        "end_1"
    ]
}
```

## Key Rules

1. **Component IDs**: Must be unique within the endpoint
2. **Activity Types**: Each component must have the correct `activity_type` field
3. **Script Files**: Use `script_file` for file path and `script_content` for inline content
4. **Flow Array**: If provided, defines the sequence of component execution
5. **Config Objects**: Each component type has specific required config fields
6. **Naming**: Use descriptive names for components and IDs

## Activity Type Mappings

| Component Type | Activity Type | Description |
|----------------|---------------|-------------|
| Content Modifier | Enricher | Enriches message content |
| Groovy Script | Script | Executes Groovy script logic |
| Request-Reply | RequestReply | Synchronous request-response invocation |
| Router | exclusiveGateway | Conditional routing decisions |
| Endpoint Sender | participant | Outgoing message sender |
| Endpoint Receiver | participant | Incoming message receiver |
| Start Event | startEvent | Process initiation point |
| End Event | endEvent | Process completion point |
| SFTP | SFTP | File transfer operations |
| OData | OData | OData service calls |

## Common Issues to Avoid

1. **Script Configuration**: Don't mix script content with file paths
2. **Missing Flow**: Include flow array for explicit sequence control
3. **Invalid IDs**: Ensure all component IDs in flow array exist in components
4. **Config Structure**: Follow the exact config structure for each component type





