# JSON Blueprint Scenarios - Real-World Examples

## Table of Contents
1. [E-Commerce Integration](#e-commerce-integration)
2. [HR Data Synchronization](#hr-data-synchronization)
3. [Financial Data Processing](#financial-data-processing)
4. [IoT Data Collection](#iot-data-collection)
5. [API Gateway Patterns](#api-gateway-patterns)
6. [Batch Processing](#batch-processing)
7. [Event-Driven Architecture](#event-driven-architecture)
8. [Microservices Integration](#microservices-integration)

## E-Commerce Integration

### Scenario: Multi-Channel Order Processing

```json
{
  "process_name": "Multi-Channel E-Commerce Order Processing",
  "description": "Process orders from multiple channels (web, mobile, marketplace) and synchronize with backend systems",
  "endpoints": [
    {
      "id": "order_processing_main",
      "name": "Main Order Processing",
      "method": "POST",
      "path": "/orders/process",
      "purpose": "Process incoming orders from all channels",
      "components": [
        {
          "type": "enricher",
          "name": "Set Order Context",
          "id": "enricher_1",
          "config": {
            "properties": "order_id={{uuid}},processing_timestamp=now(),channel={{order_channel}},priority={{order_priority}}"
          }
        },
        {
          "type": "script",
          "name": "Validate Order Data",
          "id": "script_1",
          "config": {
            "script_content": "// Order validation logic\ndef order = new JsonSlurper().parseText(message)\n\n// Validate required fields\nif (!order.customerId || !order.items || order.items.isEmpty()) {\n    throw new Exception('Invalid order data')\n}\n\n// Validate item availability\norder.items.each { item ->\n    if (!item.sku || !item.quantity || item.quantity <= 0) {\n        throw new Exception('Invalid item data')\n    }\n}\n\nreturn message"
          }
        },
        {
          "type": "request_reply",
          "name": "Check Inventory",
          "id": "request_reply_1",
          "config": {
            "endpoint_path": "/api/inventory/check",
            "method": "POST",
            "url": "{{INVENTORY_SERVICE_URL}}/api/inventory/check",
            "headers": "Content-Type=application/json,Authorization=Bearer {{INVENTORY_TOKEN}}"
          }
        },
        {
          "type": "gateway",
          "name": "Inventory Available?",
          "id": "gateway_1",
          "config": {
            "gateway_type": "exclusive",
            "routing_conditions": [
              {
                "condition": "${message.inventory_available == true}",
                "target": "process_order"
              },
              {
                "condition": "${message.inventory_available == false}",
                "target": "handle_backorder"
              }
            ]
          }
        },
        {
          "type": "request_reply",
          "name": "Create Order in ERP",
          "id": "request_reply_2",
          "config": {
            "endpoint_path": "/api/orders",
            "method": "POST",
            "url": "{{ERP_BASE_URL}}/api/orders",
            "headers": "Content-Type=application/json,Authorization=Bearer {{ERP_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Update Customer Profile",
          "id": "request_reply_3",
          "config": {
            "endpoint_path": "/api/customers/update",
            "method": "PUT",
            "url": "{{CRM_BASE_URL}}/api/customers/update",
            "headers": "Content-Type=application/json,Authorization=Bearer {{CRM_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Send Order Confirmation",
          "id": "request_reply_4",
          "config": {
            "endpoint_path": "/send-confirmation",
            "method": "POST",
            "url": "{{NOTIFICATION_SERVICE_URL}}/send-confirmation",
            "headers": "Content-Type=application/json"
          }
        }
      ],
      "error_handling": {
        "exception_subprocess": [
          {
            "type": "enricher",
            "name": "Log Order Error",
            "id": "error_enricher_1",
            "trigger": "any_error",
            "config": {
              "error_logging": "detailed",
              "error_properties": "order_id,error_message,stack_trace,component_name,timestamp"
            }
          },
          {
            "type": "request_reply",
            "name": "Send Error Notification",
            "id": "error_request_reply_1",
            "trigger": "any_error",
            "config": {
              "endpoint_path": "/send-error-alert",
              "method": "POST",
              "url": "{{ALERT_SERVICE_URL}}/send-error-alert"
            }
          }
        ]
      },
      "flow": [
        "enricher_1",
        "script_1",
        "request_reply_1",
        "gateway_1",
        "request_reply_2",
        "request_reply_3",
        "request_reply_4"
      ]
    }
  ]
}
```

## HR Data Synchronization

### Scenario: Employee Onboarding Integration

```json
{
  "process_name": "Employee Onboarding Integration",
  "description": "Automate employee onboarding process across HR systems",
  "endpoints": [
    {
      "id": "employee_onboarding",
      "name": "Employee Onboarding",
      "method": "POST",
      "path": "/onboarding/process",
      "purpose": "Process new employee onboarding across all systems",
      "components": [
        {
          "type": "enricher",
          "name": "Set Onboarding Context",
          "id": "enricher_1",
          "config": {
            "properties": "onboarding_id={{uuid}},start_date={{hire_date}},department={{department}},manager={{manager_id}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Create Employee in HRIS",
          "id": "request_reply_1",
          "config": {
            "endpoint_path": "/api/employees",
            "method": "POST",
            "url": "{{HRIS_BASE_URL}}/api/employees",
            "headers": "Content-Type=application/json,Authorization=Bearer {{HRIS_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Create IT Account",
          "id": "request_reply_2",
          "config": {
            "endpoint_path": "/api/accounts/create",
            "method": "POST",
            "url": "{{IT_SERVICE_URL}}/api/accounts/create",
            "headers": "Content-Type=application/json,Authorization=Bearer {{IT_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Assign Equipment",
          "id": "request_reply_3",
          "config": {
            "endpoint_path": "/api/equipment/assign",
            "method": "POST",
            "url": "{{EQUIPMENT_SERVICE_URL}}/api/equipment/assign",
            "headers": "Content-Type=application/json,Authorization=Bearer {{EQUIPMENT_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Schedule Training",
          "id": "request_reply_4",
          "config": {
            "endpoint_path": "/api/training/schedule",
            "method": "POST",
            "url": "{{TRAINING_SERVICE_URL}}/api/training/schedule",
            "headers": "Content-Type=application/json,Authorization=Bearer {{TRAINING_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Send Welcome Email",
          "id": "request_reply_5",
          "config": {
            "endpoint_path": "/send-welcome-email",
            "method": "POST",
            "url": "{{EMAIL_SERVICE_URL}}/send-welcome-email",
            "headers": "Content-Type=application/json"
          }
        }
      ],
      "flow": [
        "enricher_1",
        "request_reply_1",
        "request_reply_2",
        "request_reply_3",
        "request_reply_4",
        "request_reply_5"
      ]
    }
  ]
}
```

## Financial Data Processing

### Scenario: Invoice Processing and Payment

```json
{
  "process_name": "Invoice Processing and Payment Integration",
  "description": "Process invoices, validate payments, and update financial systems",
  "endpoints": [
    {
      "id": "invoice_processing",
      "name": "Invoice Processing",
      "method": "POST",
      "path": "/invoices/process",
      "purpose": "Process incoming invoices and handle payments",
      "components": [
        {
          "type": "enricher",
          "name": "Set Invoice Context",
          "id": "enricher_1",
          "config": {
            "properties": "invoice_id={{uuid}},processing_date=now(),currency={{currency}},amount={{total_amount}}"
          }
        },
        {
          "type": "script",
          "name": "Validate Invoice Data",
          "id": "script_1",
          "config": {
            "script_content": "// Invoice validation logic\ndef invoice = new JsonSlurper().parseText(message)\n\n// Validate required fields\nif (!invoice.vendorId || !invoice.invoiceNumber || !invoice.totalAmount) {\n    throw new Exception('Invalid invoice data')\n}\n\n// Validate amount\nif (invoice.totalAmount <= 0) {\n    throw new Exception('Invalid invoice amount')\n}\n\n// Validate currency\nif (!['USD', 'EUR', 'GBP'].contains(invoice.currency)) {\n    throw new Exception('Unsupported currency')\n}\n\nreturn message"
          }
        },
        {
          "type": "request_reply",
          "name": "Validate Vendor",
          "id": "request_reply_1",
          "config": {
            "endpoint_path": "/api/vendors/validate",
            "method": "GET",
            "url": "{{VENDOR_SERVICE_URL}}/api/vendors/validate",
            "headers": "Content-Type=application/json,Authorization=Bearer {{VENDOR_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Check Budget Availability",
          "id": "request_reply_2",
          "config": {
            "endpoint_path": "/api/budget/check",
            "method": "POST",
            "url": "{{BUDGET_SERVICE_URL}}/api/budget/check",
            "headers": "Content-Type=application/json,Authorization=Bearer {{BUDGET_TOKEN}}"
          }
        },
        {
          "type": "gateway",
          "name": "Approval Required?",
          "id": "gateway_1",
          "config": {
            "gateway_type": "exclusive",
            "routing_conditions": [
              {
                "condition": "${message.amount > 10000}",
                "target": "require_approval"
              },
              {
                "condition": "${message.amount <= 10000}",
                "target": "auto_approve"
              }
            ]
          }
        },
        {
          "type": "request_reply",
          "name": "Process Payment",
          "id": "request_reply_3",
          "config": {
            "endpoint_path": "/api/payments/process",
            "method": "POST",
            "url": "{{PAYMENT_SERVICE_URL}}/api/payments/process",
            "headers": "Content-Type=application/json,Authorization=Bearer {{PAYMENT_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Update General Ledger",
          "id": "request_reply_4",
          "config": {
            "endpoint_path": "/api/gl/update",
            "method": "POST",
            "url": "{{GL_SERVICE_URL}}/api/gl/update",
            "headers": "Content-Type=application/json,Authorization=Bearer {{GL_TOKEN}}"
          }
        }
      ],
      "flow": [
        "enricher_1",
        "script_1",
        "request_reply_1",
        "request_reply_2",
        "gateway_1",
        "request_reply_3",
        "request_reply_4"
      ]
    }
  ]
}
```

## IoT Data Collection

### Scenario: Sensor Data Processing

```json
{
  "process_name": "IoT Sensor Data Processing",
  "description": "Collect, process, and analyze data from IoT sensors",
  "endpoints": [
    {
      "id": "sensor_data_processing",
      "name": "Sensor Data Processing",
      "method": "POST",
      "path": "/sensors/data",
      "purpose": "Process incoming sensor data and trigger actions",
      "components": [
        {
          "type": "enricher",
          "name": "Set Sensor Context",
          "id": "enricher_1",
          "config": {
            "properties": "sensor_id={{sensor_id}},timestamp=now(),location={{location}},device_type={{device_type}}"
          }
        },
        {
          "type": "script",
          "name": "Validate Sensor Data",
          "id": "script_1",
          "config": {
            "script_content": "// Sensor data validation\ndef sensorData = new JsonSlurper().parseText(message)\n\n// Validate sensor ID\nif (!sensorData.sensorId) {\n    throw new Exception('Missing sensor ID')\n}\n\n// Validate data values\nif (!sensorData.values || sensorData.values.isEmpty()) {\n    throw new Exception('No sensor values provided')\n}\n\n// Check for data anomalies\nsensorData.values.each { value ->\n    if (value < -100 || value > 100) {\n        throw new Exception('Sensor value out of range')\n    }\n}\n\nreturn message"
          }
        },
        {
          "type": "script",
          "name": "Analyze Data Patterns",
          "id": "script_2",
          "config": {
            "script_content": "// Data pattern analysis\ndef sensorData = new JsonSlurper().parseText(message)\ndef analysis = [:]\n\n// Calculate average\nanalysis.average = sensorData.values.sum() / sensorData.values.size()\n\n// Calculate min/max\nanalysis.min = sensorData.values.min()\nanalysis.max = sensorData.values.max()\n\n// Detect anomalies\nanalysis.anomalies = sensorData.values.findAll { value ->\n    Math.abs(value - analysis.average) > (analysis.average * 0.2)\n}\n\n// Set analysis results\nmessage.setProperty('data_analysis', new JsonBuilder(analysis).toString())\nreturn message"
          }
        },
        {
          "type": "gateway",
          "name": "Anomaly Detected?",
          "id": "gateway_1",
          "config": {
            "gateway_type": "exclusive",
            "routing_conditions": [
              {
                "condition": "${message.anomalies.size() > 0}",
                "target": "handle_anomaly"
              },
              {
                "condition": "${message.anomalies.size() == 0}",
                "target": "normal_processing"
              }
            ]
          }
        },
        {
          "type": "request_reply",
          "name": "Store Data in Database",
          "id": "request_reply_1",
          "config": {
            "endpoint_path": "/api/sensor-data/store",
            "method": "POST",
            "url": "{{DATABASE_SERVICE_URL}}/api/sensor-data/store",
            "headers": "Content-Type=application/json,Authorization=Bearer {{DB_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Send Alert",
          "id": "request_reply_2",
          "config": {
            "endpoint_path": "/send-alert",
            "method": "POST",
            "url": "{{ALERT_SERVICE_URL}}/send-alert",
            "headers": "Content-Type=application/json"
          }
        }
      ],
      "flow": [
        "enricher_1",
        "script_1",
        "script_2",
        "gateway_1",
        "request_reply_1",
        "request_reply_2"
      ]
    }
  ]
}
```

## API Gateway Patterns

### Scenario: API Gateway with Rate Limiting and Authentication

```json
{
  "process_name": "API Gateway with Rate Limiting",
  "description": "API gateway that handles authentication, rate limiting, and routing",
  "endpoints": [
    {
      "id": "api_gateway",
      "name": "API Gateway",
      "method": "ANY",
      "path": "/api/*",
      "purpose": "Route API requests with authentication and rate limiting",
      "components": [
        {
          "type": "enricher",
          "name": "Set Request Context",
          "id": "enricher_1",
          "config": {
            "properties": "request_id={{uuid}},timestamp=now(),client_ip={{client_ip}},user_agent={{user_agent}}"
          }
        },
        {
          "type": "script",
          "name": "Validate API Key",
          "id": "script_1",
          "config": {
            "script_content": "// API key validation\ndef headers = message.getHeaders()\ndef apiKey = headers.get('X-API-Key')\n\nif (!apiKey) {\n    throw new Exception('Missing API key')\n}\n\n// Validate API key format\nif (!apiKey.matches('[a-zA-Z0-9]{32}')) {\n    throw new Exception('Invalid API key format')\n}\n\n// Set validated API key\nmessage.setProperty('validated_api_key', apiKey)\nreturn message"
          }
        },
        {
          "type": "request_reply",
          "name": "Check Rate Limit",
          "id": "request_reply_1",
          "config": {
            "endpoint_path": "/api/rate-limit/check",
            "method": "POST",
            "url": "{{RATE_LIMIT_SERVICE_URL}}/api/rate-limit/check",
            "headers": "Content-Type=application/json,Authorization=Bearer {{RATE_LIMIT_TOKEN}}"
          }
        },
        {
          "type": "gateway",
          "name": "Rate Limit Exceeded?",
          "id": "gateway_1",
          "config": {
            "gateway_type": "exclusive",
            "routing_conditions": [
              {
                "condition": "${message.rate_limit_exceeded == true}",
                "target": "rate_limit_exceeded"
              },
              {
                "condition": "${message.rate_limit_exceeded == false}",
                "target": "route_request"
              }
            ]
          }
        },
        {
          "type": "script",
          "name": "Route Request",
          "id": "script_2",
          "config": {
            "script_content": "// Request routing logic\ndef path = message.getProperty('path')\ndef method = message.getProperty('method')\n\ndef targetUrl = ''\n\n// Route based on path\nif (path.startsWith('/api/users')) {\n    targetUrl = '{{USER_SERVICE_URL}}' + path\n} else if (path.startsWith('/api/orders')) {\n    targetUrl = '{{ORDER_SERVICE_URL}}' + path\n} else if (path.startsWith('/api/products')) {\n    targetUrl = '{{PRODUCT_SERVICE_URL}}' + path\n} else {\n    throw new Exception('Unknown API endpoint')\n}\n\nmessage.setProperty('target_url', targetUrl)\nreturn message"
          }
        },
        {
          "type": "request_reply",
          "name": "Forward Request",
          "id": "request_reply_2",
          "config": {
            "endpoint_path": "{{target_url}}",
            "method": "{{method}}",
            "url": "{{target_url}}",
            "headers": "Content-Type=application/json,Authorization=Bearer {{SERVICE_TOKEN}}"
          }
        }
      ],
      "flow": [
        "enricher_1",
        "script_1",
        "request_reply_1",
        "gateway_1",
        "script_2",
        "request_reply_2"
      ]
    }
  ]
}
```

## Batch Processing

### Scenario: Daily Data Synchronization

```json
{
  "process_name": "Daily Data Synchronization",
  "description": "Synchronize data between systems on a daily basis",
  "endpoints": [
    {
      "id": "daily_sync",
      "name": "Daily Data Sync",
      "method": "POST",
      "path": "/sync/daily",
      "purpose": "Synchronize data between systems daily",
      "components": [
        {
          "type": "enricher",
          "name": "Set Sync Context",
          "id": "enricher_1",
          "config": {
            "properties": "sync_date={{date}},sync_type=daily,batch_id={{uuid}}"
          }
        },
        {
          "type": "script",
          "name": "Extract Changed Data",
          "id": "script_1",
          "config": {
            "script_content": "// Extract changed data since last sync\ndef lastSyncDate = message.getProperty('last_sync_date')\ndef currentDate = new Date().format('yyyy-MM-dd')\n\n// Query for changed records\nmessage.setProperty('query_date', lastSyncDate)\nmessage.setProperty('current_date', currentDate)\n\nreturn message"
          }
        },
        {
          "type": "request_reply",
          "name": "Get Source Data",
          "id": "request_reply_1",
          "config": {
            "endpoint_path": "/api/data/changes",
            "method": "GET",
            "url": "{{SOURCE_SYSTEM_URL}}/api/data/changes",
            "headers": "Content-Type=application/json,Authorization=Bearer {{SOURCE_TOKEN}}"
          }
        },
        {
          "type": "script",
          "name": "Transform Data",
          "id": "script_2",
          "config": {
            "script_content": "// Transform data for target system\ndef sourceData = new JsonSlurper().parseText(message)\ndef transformedData = []\n\nsourceData.records.each { record ->\n    def transformed = [:]\n    transformed.id = record.id\n    transformed.name = record.name\n    transformed.email = record.email\n    transformed.updated_at = new Date().format('yyyy-MM-dd HH:mm:ss')\n    transformedData.add(transformed)\n}\n\nmessage.setBody(new JsonBuilder(transformedData).toString())\nreturn message"
          }
        },
        {
          "type": "request_reply",
          "name": "Update Target System",
          "id": "request_reply_2",
          "config": {
            "endpoint_path": "/api/data/bulk-update",
            "method": "POST",
            "url": "{{TARGET_SYSTEM_URL}}/api/data/bulk-update",
            "headers": "Content-Type=application/json,Authorization=Bearer {{TARGET_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Update Sync Status",
          "id": "request_reply_3",
          "config": {
            "endpoint_path": "/api/sync/update-status",
            "method": "POST",
            "url": "{{SYNC_SERVICE_URL}}/api/sync/update-status",
            "headers": "Content-Type=application/json,Authorization=Bearer {{SYNC_TOKEN}}"
          }
        }
      ],
      "flow": [
        "enricher_1",
        "script_1",
        "request_reply_1",
        "script_2",
        "request_reply_2",
        "request_reply_3"
      ]
    }
  ]
}
```

## Event-Driven Architecture

### Scenario: Event Processing and Notification

```json
{
  "process_name": "Event Processing and Notification",
  "description": "Process business events and send notifications",
  "endpoints": [
    {
      "id": "event_processing",
      "name": "Event Processing",
      "method": "POST",
      "path": "/events/process",
      "purpose": "Process business events and trigger notifications",
      "components": [
        {
          "type": "enricher",
          "name": "Set Event Context",
          "id": "enricher_1",
          "config": {
            "properties": "event_id={{uuid}},event_type={{event_type}},timestamp=now(),source={{source_system}}"
          }
        },
        {
          "type": "script",
          "name": "Process Event",
          "id": "script_1",
          "config": {
            "script_content": "// Event processing logic\ndef event = new JsonSlurper().parseText(message)\n\ndef eventType = event.type\ndef eventData = event.data\n\ndef processingResult = [:]\n\nswitch (eventType) {\n    case 'user_registration':\n        processingResult.action = 'send_welcome_email'\n        processingResult.priority = 'high'\n        break\n    case 'order_placed':\n        processingResult.action = 'update_inventory'\n        processingResult.priority = 'medium'\n        break\n    case 'payment_failed':\n        processingResult.action = 'send_payment_reminder'\n        processingResult.priority = 'high'\n        break\n    default:\n        processingResult.action = 'log_event'\n        processingResult.priority = 'low'\n}\n\nmessage.setProperty('processing_result', new JsonBuilder(processingResult).toString())\nreturn message"
          }
        },
        {
          "type": "gateway",
          "name": "Route by Event Type",
          "id": "gateway_1",
          "config": {
            "gateway_type": "exclusive",
            "routing_conditions": [
              {
                "condition": "${message.event_type == 'user_registration'}",
                "target": "handle_registration"
              },
              {
                "condition": "${message.event_type == 'order_placed'}",
                "target": "handle_order"
              },
              {
                "condition": "${message.event_type == 'payment_failed'}",
                "target": "handle_payment_failure"
              }
            ]
          }
        },
        {
          "type": "request_reply",
          "name": "Send Notification",
          "id": "request_reply_1",
          "config": {
            "endpoint_path": "/send-notification",
            "method": "POST",
            "url": "{{NOTIFICATION_SERVICE_URL}}/send-notification",
            "headers": "Content-Type=application/json,Authorization=Bearer {{NOTIFICATION_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Update Database",
          "id": "request_reply_2",
          "config": {
            "endpoint_path": "/api/events/update",
            "method": "POST",
            "url": "{{DATABASE_SERVICE_URL}}/api/events/update",
            "headers": "Content-Type=application/json,Authorization=Bearer {{DB_TOKEN}}"
          }
        }
      ],
      "flow": [
        "enricher_1",
        "script_1",
        "gateway_1",
        "request_reply_1",
        "request_reply_2"
      ]
    }
  ]
}
```

## Microservices Integration

### Scenario: Microservices Orchestration

```json
{
  "process_name": "Microservices Orchestration",
  "description": "Orchestrate multiple microservices to complete a business process",
  "endpoints": [
    {
      "id": "microservices_orchestration",
      "name": "Microservices Orchestration",
      "method": "POST",
      "path": "/orchestrate",
      "purpose": "Orchestrate multiple microservices for business process",
      "components": [
        {
          "type": "enricher",
          "name": "Set Orchestration Context",
          "id": "enricher_1",
          "config": {
            "properties": "orchestration_id={{uuid}},process_type={{process_type}},timestamp=now()"
          }
        },
        {
          "type": "request_reply",
          "name": "Call User Service",
          "id": "request_reply_1",
          "config": {
            "endpoint_path": "/api/users/validate",
            "method": "POST",
            "url": "{{USER_SERVICE_URL}}/api/users/validate",
            "headers": "Content-Type=application/json,Authorization=Bearer {{USER_SERVICE_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Call Product Service",
          "id": "request_reply_2",
          "config": {
            "endpoint_path": "/api/products/check",
            "method": "POST",
            "url": "{{PRODUCT_SERVICE_URL}}/api/products/check",
            "headers": "Content-Type=application/json,Authorization=Bearer {{PRODUCT_SERVICE_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Call Inventory Service",
          "id": "request_reply_3",
          "config": {
            "endpoint_path": "/api/inventory/reserve",
            "method": "POST",
            "url": "{{INVENTORY_SERVICE_URL}}/api/inventory/reserve",
            "headers": "Content-Type=application/json,Authorization=Bearer {{INVENTORY_SERVICE_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Call Payment Service",
          "id": "request_reply_4",
          "config": {
            "endpoint_path": "/api/payments/process",
            "method": "POST",
            "url": "{{PAYMENT_SERVICE_URL}}/api/payments/process",
            "headers": "Content-Type=application/json,Authorization=Bearer {{PAYMENT_SERVICE_TOKEN}}"
          }
        },
        {
          "type": "request_reply",
          "name": "Call Notification Service",
          "id": "request_reply_5",
          "config": {
            "endpoint_path": "/api/notifications/send",
            "method": "POST",
            "url": "{{NOTIFICATION_SERVICE_URL}}/api/notifications/send",
            "headers": "Content-Type=application/json,Authorization=Bearer {{NOTIFICATION_SERVICE_TOKEN}}"
          }
        }
      ],
      "flow": [
        "enricher_1",
        "request_reply_1",
        "request_reply_2",
        "request_reply_3",
        "request_reply_4",
        "request_reply_5"
      ]
    }
  ]
}
```

## Best Practices for Scenario Design

### 1. Error Handling
- Always include comprehensive error handling
- Use exception subprocesses for error scenarios
- Implement retry logic for transient failures
- Log errors with sufficient detail for debugging

### 2. Performance Optimization
- Use parallel processing where possible
- Implement caching for frequently accessed data
- Set appropriate timeouts for external calls
- Monitor and optimize processing times

### 3. Security Considerations
- Use secure authentication methods
- Encrypt sensitive data in transit and at rest
- Implement proper access controls
- Audit all security-relevant events

### 4. Monitoring and Logging
- Include detailed logging for debugging
- Monitor processing times and resource usage
- Track success and failure rates
- Implement alerting for critical failures

### 5. Maintainability
- Use descriptive names for components
- Document complex logic
- Follow consistent patterns
- Version control your blueprints

This comprehensive set of scenarios provides real-world examples that can be adapted for various integration needs. Each scenario demonstrates different patterns and best practices that can be combined and customized for specific requirements.
