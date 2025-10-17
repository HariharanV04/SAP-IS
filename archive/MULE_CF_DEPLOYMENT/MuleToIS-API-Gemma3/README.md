# MuleToIS-API-Gemma3

SAP Integration Suite iFlow Generator API using Gemma3 LLM via RunPod.

## Overview

This Flask application provides an API for generating SAP Integration Suite iFlow packages from MuleSoft documentation using the open-source Gemma3 LLM hosted on RunPod. It includes intelligent token management and response resumption strategies for handling large documents.

## Features

- **Gemma3 LLM Integration**: Uses open-source Gemma3 model via RunPod
- **Token Management**: Automatic chunking for inputs exceeding 8K token limit
- **Response Resumption**: Handles token limits with progressive response combination
- **Smart Chunking**: Breaks text at sentence/paragraph boundaries with overlap
- **Error Recovery**: Robust error handling and retry mechanisms
- **Progress Tracking**: Real-time status updates for multi-chunk processing

## API Endpoints

### Health Check
```
GET /health
```
Returns service status and configuration.

### Generate iFlow
```
POST /api/generate-iflow
```
Generate iFlow from markdown content.

**Request Body:**
```json
{
  "markdown": "MuleSoft documentation content...",
  "iflow_name": "MyIFlow",
  "provider": "gemma3"
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "queued",
  "message": "iFlow generation started"
}
```

### Job Status
```
GET /api/jobs/{job_id}
```
Get job status and progress.

**Response:**
```json
{
  "id": "job-id",
  "status": "processing|completed|failed",
  "progress": {
    "current_chunk": 2,
    "total_chunks": 5,
    "percentage": 40
  }
}
```

### Download iFlow
```
GET /api/jobs/{job_id}/download
```
Download generated iFlow XML file.

### Test Response Parsing
```
POST /api/test-extract
```
Test endpoint for RunPod response extraction.

## Environment Variables

### Required
- `RUNPOD_API_KEY`: Your RunPod API key
- `RUNPOD_ENDPOINT_ID`: RunPod endpoint ID (default: s5unaaduyy7otl)

### Optional
- `GEMMA3_MAX_INPUT_TOKENS`: Maximum input tokens (default: 8192)
- `GEMMA3_MAX_OUTPUT_TOKENS`: Maximum output tokens (default: 2048)
- `GEMMA3_CHUNK_OVERLAP`: Token overlap between chunks (default: 200)
- `GEMMA3_MAX_WAIT_TIME`: Maximum wait time in seconds (default: 300)
- `PORT`: Server port (default: 5001)
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Debug mode (default: False)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your RunPod credentials
```

### 3. Run Development Server
```bash
python app.py
```
or
```bash
./start-development.bat
```

### 4. Test Response Parsing
```bash
python test_response_parsing.py
```

## Token Management

### Chunking Strategy
1. **Token Estimation**: Rough estimation (1 token ≈ 4 characters)
2. **Smart Splitting**: Breaks at sentence/paragraph boundaries
3. **Context Preservation**: 200-token overlap between chunks
4. **Progressive Processing**: Sequential chunk processing
5. **Response Combination**: Merges partial responses

### Example Flow
```
Large Document (12K tokens)
    ↓
Split into 2 chunks (6K + 6K with 200 overlap)
    ↓
Process Chunk 1 → Partial Response 1
    ↓
Process Chunk 2 → Partial Response 2
    ↓
Combine Responses → Complete iFlow
```

## RunPod Response Format

The service handles RunPod's nested response structure:

```json
{
  "output": [
    {
      "choices": [
        {
          "tokens": ["Generated", " text", " content..."]
        }
      ],
      "usage": {
        "input": 139,
        "output": 2000
      }
    }
  ],
  "status": "COMPLETED"
}
```

## Cloud Foundry Deployment

### 1. Set Environment Variables
```bash
cf set-env mulesoft-iflow-api-gemma3 RUNPOD_API_KEY your_api_key
cf set-env mulesoft-iflow-api-gemma3 RUNPOD_ENDPOINT_ID your_endpoint_id
```

### 2. Deploy
```bash
cf push
```

### 3. Production URL
```
https://mulesoft-iflow-api-gemma3.cfapps.us10-001.hana.ondemand.com
```

## Error Handling

- **Connection Errors**: Automatic retry with exponential backoff
- **Token Limit Exceeded**: Automatic chunking and resumption
- **RunPod Failures**: Detailed error logging and user feedback
- **Timeout Handling**: Configurable timeouts for long-running jobs

## Monitoring

- **Health Checks**: `/health` endpoint for service monitoring
- **Detailed Logging**: Comprehensive logging for debugging
- **Progress Tracking**: Real-time job progress updates
- **Error Reporting**: Structured error responses

## Comparison with Anthropic

| Feature | Anthropic Claude | Gemma3 (This Service) |
|---------|------------------|----------------------|
| Max Tokens | 200K | 8K |
| Speed | Fast (30s) | Moderate (5min) |
| Quality | Excellent | Good |
| Cost | Premium | Low |
| Chunking | Not needed | Automatic |
| Open Source | No | Yes |

## Development

### Project Structure
```
MuleToIS-API-Gemma3/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── manifest.yml               # Cloud Foundry manifest
├── Procfile                   # Process configuration
├── .env.example              # Environment template
├── start-development.bat     # Development startup script
├── test_response_parsing.py  # Response parsing test
└── README.md                 # This file
```

### Testing
```bash
# Test response parsing
python test_response_parsing.py

# Test API endpoints
curl -X GET http://localhost:5002/health
curl -X POST http://localhost:5002/api/test-extract -H "Content-Type: application/json" -d '{"test": "data"}'
```

## Troubleshooting

### Common Issues

1. **RunPod Connection Failed**
   - Check RUNPOD_API_KEY is set correctly
   - Verify endpoint ID is valid
   - Check network connectivity

2. **Token Limit Errors**
   - Service automatically handles chunking
   - Check GEMMA3_MAX_INPUT_TOKENS setting
   - Monitor chunk processing logs

3. **Response Parsing Errors**
   - Use test_response_parsing.py to debug
   - Check RunPod response format changes
   - Review extraction logs

4. **Timeout Issues**
   - Increase GEMMA3_MAX_WAIT_TIME
   - Check RunPod endpoint performance
   - Monitor job processing times

### Logs
```bash
# View application logs
cf logs mulesoft-iflow-api-gemma3 --recent

# Stream live logs
cf logs mulesoft-iflow-api-gemma3
```

## Support

For issues and questions:
1. Check the logs for detailed error messages
2. Test with the `/api/test-extract` endpoint
3. Verify RunPod credentials and endpoint status
4. Review token limits and chunking behavior
