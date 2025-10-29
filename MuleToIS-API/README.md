# MuleToIS API for iFlow Generation

This API provides a REST interface for generating SAP Integration Suite iFlows from markdown documentation. It leverages the MuleToIFlow GenAI approach to analyze markdown content and generate iFlow XML files.

## Features

- REST API for generating iFlows from markdown content
- Asynchronous job processing
- Job status tracking
- Download generated iFlow ZIP files
- Access to debug files for troubleshooting

## Prerequisites

- Python 3.8 or higher
- Claude API key (set in `.env` file)
- Access to the MuleToIFlow GenAI Approach code

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Claude API key:
   ```
   CLAUDE_API_KEY=your_api_key_here
   ```

## Usage

### Starting the API Server

```bash
python app.py
```

The server will start on port 5000 by default. You can change the port by setting the `PORT` environment variable.

### API Endpoints

#### Generate iFlow

```
POST /api/generate-iflow
```

Request body:
```json
{
  "markdown": "# API Documentation...",
  "iflow_name": "MyIFlow" (optional)
}
```

Response:
```json
{
  "status": "queued",
  "message": "iFlow generation started",
  "job_id": "12345678-1234-5678-1234-567812345678"
}
```

#### Get Job Status

```
GET /api/jobs/{job_id}
```

Response:
```json
{
  "id": "12345678-1234-5678-1234-567812345678",
  "status": "completed",
  "created": "2025-05-15T10:30:00.000Z",
  "message": "iFlow generation completed successfully!",
  "files": {
    "zip": "results/12345678-1234-5678-1234-567812345678/GeneratedIFlow_12345678.zip",
    "debug": {
      "raw_analysis_response.txt": "genai_debug/raw_analysis_response.txt",
      "final_iflow_GeneratedIFlow_12345678.xml": "genai_debug/final_iflow_GeneratedIFlow_12345678.xml"
    }
  },
  "iflow_name": "GeneratedIFlow_12345678"
}
```

#### Download Generated iFlow

```
GET /api/jobs/{job_id}/download
```

Returns the generated iFlow ZIP file.

#### Download Debug File

```
GET /api/jobs/{job_id}/debug/{file_name}
```

Returns the specified debug file.

### Health Check

```
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "message": "MuleToIS API is running",
  "api_key_configured": true
}
```

## Integration with Frontend

To integrate with the frontend "Generate iFlow" button:

1. Update the frontend API service to call the new endpoints:

```javascript
// Generate iFlow from markdown documentation
export const generateIflow = async (markdown, iflowName = null) => {
  try {
    const response = await api.post('/api/generate-iflow', {
      markdown,
      iflow_name: iflowName
    });
    return response.data;
  } catch (error) {
    console.error("Error generating iFlow:", error);
    throw error;
  }
};

// Get iFlow generation status
export const getIflowGenerationStatus = async (jobId) => {
  try {
    const response = await api.get(`/api/jobs/${jobId}`);
    return response.data;
  } catch (error) {
    console.error("Error getting iFlow generation status:", error);
    throw error;
  }
};

// Download generated iFlow
export const downloadGeneratedIflow = async (jobId) => {
  try {
    const response = await api.get(`/api/jobs/${jobId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error("Error downloading generated iFlow:", error);
    throw error;
  }
};
```

2. Update the "Generate iFlow" button handler to use the new API:

```javascript
const handleGenerateIflow = async () => {
  try {
    setIsGeneratingIflow(true);
    
    // Get the markdown content from the job
    const markdownContent = await getDocumentation(jobInfo.id, 'markdown');
    const markdownText = await markdownContent.text();
    
    // Call the API to generate the iFlow
    const result = await generateIflow(markdownText);
    
    // Start polling for status
    const statusInterval = setInterval(async () => {
      try {
        const statusResult = await getIflowGenerationStatus(result.job_id);
        
        if (statusResult.status === "completed") {
          setIsGeneratingIflow(false);
          setIsIflowGenerated(true);
          setIflowJobId(result.job_id);
          toast.success("iFlow generated successfully!");
          clearInterval(statusInterval);
        } else if (statusResult.status === "failed") {
          setIsGeneratingIflow(false);
          toast.error(`iFlow generation failed: ${statusResult.message}`);
          clearInterval(statusInterval);
        }
      } catch (error) {
        console.error("Error checking iFlow generation status:", error);
      }
    }, 2000);
    
  } catch (error) {
    setIsGeneratingIflow(false);
    toast.error("Failed to generate iFlow");
    console.error("Error generating iFlow:", error);
  }
};
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
