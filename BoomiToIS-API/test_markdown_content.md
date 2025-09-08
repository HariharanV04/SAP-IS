# Enhanced Complete Package Test

Test the enhanced template-based approach for complete SAP package

## Endpoints

### Test Endpoint

**ID:** test_endpoint

**Components:**

- **Set Properties**
  - Type: enricher
  - ID: enricher_1
  - Configuration:
    - headers:
      - Content-Type: application/json

- **Validate Input**
  - Type: script
  - ID: script_1
  - Configuration:
    - script: log.info('Script executed'); return message;

- **Call External API**
  - Type: request_reply
  - ID: request_reply_1
  - Configuration:
    - endpoint_path: /api/external

