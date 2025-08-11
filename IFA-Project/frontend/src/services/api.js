import api from "../utils/api"

// Use relative URL to leverage Vite's proxy
const API_URL = '/api'

// Add this test function to check connectivity with proper error handling
export const testBackendConnection = async () => {
    try {
        console.log("Testing connection to backend at:", API_URL)

        // Use our axios instance which has the proper baseURL configuration
        const response = await api.get("/health")

        console.log("Backend connection test successful:", response.status)
        return true
    } catch (error) {
        console.error("Backend connection test failed:", error)

        // Try a direct fetch with mode: 'no-cors' as a fallback
        try {
            console.log("Attempting fallback connection test...")
            const response = await fetch(`${API_URL}/health`, {
                method: "GET",
                mode: "no-cors" // This will prevent CORS errors but won't give us response data
            })

            // With 'no-cors', we can't check status, but at least we didn't get a network error
            console.log("Fallback connection completed without network errors")
            return true
        } catch (fallbackError) {
            console.error("Fallback connection test failed:", fallbackError)
            return false
        }
    }
}

// Upload documentation directly for iFlow generation
export const uploadDocumentation = async (file, platform = 'mulesoft', signal) => {
    try {
        const selectedProvider = getSelectedLLMProvider();
        console.log("Uploading documentation for direct iFlow generation")
        console.log("Platform selected:", platform)
        console.log("LLM Provider selected:", selectedProvider)
        console.log("File:", file.name, "Type:", file.type, "Size:", file.size)

        const formData = new FormData()
        formData.append("file", file)
        formData.append("platform", platform)
        formData.append("llm_provider", selectedProvider)

        const config = {
            headers: {
                "Content-Type": "multipart/form-data"
            },
            timeout: 120000 // 2 minutes timeout for document processing with LLM
        }

        if (signal) {
            config.signal = signal
        }

        const response = await api.post("/upload-documentation", formData, config)

        console.log("Documentation upload successful:", response.data)
        return response.data
    } catch (error) {
        console.error("Documentation upload failed:", error)

        if (error.name === 'AbortError') {
            throw new Error('Upload cancelled')
        }

        if (error.response) {
            const errorMessage = error.response.data?.error || 'Upload failed'
            const errorDetails = error.response.data?.details || ''
            const supportedFormats = error.response.data?.supported_formats || []

            let fullMessage = errorMessage
            if (errorDetails) {
                fullMessage += `: ${errorDetails}`
            }
            if (supportedFormats.length > 0) {
                fullMessage += `\n\nSupported formats: ${supportedFormats.join(', ')}`
            }

            throw new Error(fullMessage)
        }

        throw new Error('Network error occurred during upload')
    }
}

// Generate iFlow from uploaded documentation
export const generateIflowFromDocs = async (jobId, signal) => {
    try {
        const selectedProvider = getSelectedLLMProvider();
        console.log("Generating iFlow from uploaded documentation for job:", jobId, "using provider:", selectedProvider)

        const config = {
            timeout: 120000 // 2 minutes timeout for iFlow generation
        }

        if (signal) {
            config.signal = signal
        }

        // Send LLM provider information to Main API
        const requestData = {
            llm_provider: selectedProvider
        };

        const response = await api.post(`/generate-iflow-from-docs/${jobId}`, requestData, config)

        console.log("iFlow generation started:", response.data)
        return response.data
    } catch (error) {
        console.error("iFlow generation failed:", error)

        if (error.name === 'AbortError') {
            throw new Error('iFlow generation cancelled')
        }

        if (error.response) {
            const errorMessage = error.response.data?.error || 'iFlow generation failed'
            throw new Error(errorMessage)
        }

        throw new Error('Network error occurred during iFlow generation')
    }
}

// Modify generateDocs to use axios with platform support
export const generateDocs = async (formData, signal) => {
    try {
        console.log("Sending request to generate documentation")

        // Log the platform if it exists in formData
        if (formData.has('platform')) {
            console.log("Platform selected:", formData.get('platform'))
        }

        const config = {
            headers: {
                "Content-Type": "multipart/form-data"
            },
            signal
        }

        const response = await api.post("/generate-docs", formData, config)
        console.log("Response received:", response.data)
        return response.data
    } catch (error) {
        console.error("Error generating docs:", error)
        throw error
    }
}



// Update getJobStatus to use axios
export const getJobStatus = async (jobId, jobInfo = null) => {
    try {
        const response = await api.get(`/jobs/${jobId}`)
        return response.data
    } catch (error) {
        console.error("Error getting job status:", error)
        throw error
    }
}



// Update getAllJobs to use axios
export const getAllJobs = async () => {
    try {
        const response = await api.get("/jobs")
        return response.data
    } catch (error) {
        console.error("Error getting all jobs:", error)
        throw error
    }
}



// Delete a job and its associated files
export const deleteJob = async jobId => {
    try {
        const response = await api.delete(`/jobs/${jobId}`)
        return response.data
    } catch (error) {
        console.error("Error deleting job:", error)
        throw error
    }
}

// Update getDocumentation to use axios with responseType blob
export const getDocumentation = async (jobId, fileType) => {
    try {
        const response = await api.get(`/docs/${jobId}/${fileType}`, {
            responseType: "blob"
        })
        return response.data
    } catch (error) {
        console.error("Error getting documentation:", error)
        throw error
    }
}



// Generate iFlow match for a job
export const generateIflowMatch = async jobId => {
    try {
        console.log(`Generating iFlow match for job: ${jobId}`)
        // Fix: Remove the duplicate '/api' prefix since it's already in the baseURL
        const response = await api.post(`/generate-iflow-match/${jobId}`)
        console.log("iFlow match generation response:", response.data)
        return response.data
    } catch (error) {
        console.error("Error generating iFlow match:", error)
        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
        } else if (error.request) {
            console.error("No response received:", error.request)
        } else {
            console.error("Error message:", error.message)
        }
        throw error
    }
}



// Get iFlow match status
export const getIflowMatchStatus = async jobId => {
    try {
        console.log(`Getting iFlow match status for job: ${jobId}`)
        // Fix: Remove the duplicate '/api' prefix since it's already in the baseURL
        const response = await api.get(`/iflow-match/${jobId}`)
        console.log("iFlow match status response:", response.data)
        return response.data
    } catch (error) {
        console.error("Error getting iFlow match status:", error)
        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
        } else if (error.request) {
            console.error("No response received:", error.request)
        } else {
            console.error("Error message:", error.message)
        }
        throw error
    }
}



// Get iFlow match file
export const getIflowMatchFile = async (jobId, fileType) => {
    try {
        console.log(`Getting iFlow match file for job: ${jobId}, file type: ${fileType}`)
        // Fix: Remove the duplicate '/api' prefix since it's already in the baseURL
        const response = await api.get(`/iflow-match/${jobId}/${fileType}`, {
            responseType: "blob"
        })
        console.log(`iFlow match file response received, size: ${response.data.size} bytes`)
        return response.data
    } catch (error) {
        console.error("Error getting iFlow match file:", error)
        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
        } else if (error.request) {
            console.error("No response received:", error.request)
        } else {
            console.error("Error message:", error.message)
        }
        throw error
    }
}



// Create a dedicated API instance for the iFlow API
import axios from 'axios'

// Get environment variables
const ENV = import.meta.env.VITE_ENVIRONMENT || 'development';
const IFLOW_API_URL = import.meta.env.VITE_IFLOW_API_URL || 'http://localhost:5001/api';
const IFLOW_API_HOST = import.meta.env.VITE_IFLOW_API_HOST || 'localhost:5001';
const IFLOW_API_PROTOCOL = import.meta.env.VITE_IFLOW_API_PROTOCOL || 'http';

// Gemma3 API Configuration
const GEMMA3_API_URL = import.meta.env.VITE_GEMMA3_API_URL || 'http://localhost:5002/api';
const GEMMA3_API_HOST = import.meta.env.VITE_GEMMA3_API_HOST || 'localhost:5002';
const GEMMA3_API_PROTOCOL = import.meta.env.VITE_GEMMA3_API_PROTOCOL || 'http';

// BoomiToIS API Configuration
const BOOMI_API_URL = import.meta.env.VITE_BOOMI_API_URL || 'http://localhost:5003/api';
const BOOMI_API_HOST = import.meta.env.VITE_BOOMI_API_HOST || 'localhost:5003';
const BOOMI_API_PROTOCOL = import.meta.env.VITE_BOOMI_API_PROTOCOL || 'http';
const MAX_POLL_COUNT = parseInt(import.meta.env.VITE_MAX_POLL_COUNT || '60');
const POLL_INTERVAL_MS = parseInt(import.meta.env.VITE_POLL_INTERVAL_MS || '2000');
const MAX_FAILED_ATTEMPTS = parseInt(import.meta.env.VITE_MAX_FAILED_ATTEMPTS || '3');

console.log(`Environment: ${ENV}`);
console.log('Using iFlow API URL:', IFLOW_API_URL);
console.log('Using iFlow API Host:', IFLOW_API_HOST);
console.log('Using iFlow API Protocol:', IFLOW_API_PROTOCOL);
console.log('Using Gemma3 API URL:', GEMMA3_API_URL);
console.log('Using Boomi API URL:', BOOMI_API_URL);
console.log('Max Poll Count:', MAX_POLL_COUNT);
console.log('Poll Interval (ms):', POLL_INTERVAL_MS);
console.log('Max Failed Attempts:', MAX_FAILED_ATTEMPTS);

// Function to get selected LLM provider from localStorage
const getSelectedLLMProvider = () => {
  return localStorage.getItem('selectedLLMProvider') || 'anthropic';
};

// Function to get the appropriate API instance based on platform and LLM provider
const getIflowApiInstance = (platform = 'mulesoft') => {
  const provider = getSelectedLLMProvider();

  // If Gemma-3 is selected, always use Gemma-3 API regardless of platform
  if (provider === 'gemma3') {
    console.log(`Using Gemma-3 API for ${platform} platform`);
    return gemma3Api;
  }

  // For Anthropic provider, use platform-specific APIs
  if (platform === 'boomi') {
    console.log('Using BoomiToIS-API for Boomi platform with Anthropic');
    return boomiApi;
  }

  // Default to MuleSoft API for Anthropic
  console.log('Using MuleSoft API for Anthropic');
  return iflowApi;
};

// Create a separate instance for the iFlow API (Anthropic)
const iflowApi = axios.create({
  baseURL: IFLOW_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Set withCredentials based on environment
  // In production, we need to set this to true for Cloud Foundry
  withCredentials: ENV === 'production',
})

// Create a separate instance for the Gemma3 API
const gemma3Api = axios.create({
  baseURL: GEMMA3_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: ENV === 'production',
})

// Create a separate instance for the BoomiToIS API
const boomiApi = axios.create({
  baseURL: BOOMI_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: ENV === 'production',
})

// Add request interceptor for debugging
iflowApi.interceptors.request.use(
  (config) => {
    console.log(`iFlow API Request to: ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('iFlow API Request Error:', error);
    return Promise.reject(error);
  }
)

// Add response interceptor for debugging
iflowApi.interceptors.response.use(
  (response) => {
    console.log(`iFlow API Response from: ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('iFlow API Error Response:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('iFlow API No Response Error:', error.request);
    } else {
      console.error('iFlow API Request Setup Error:', error.message);
    }
    return Promise.reject(error);
  }
)

// Add interceptors for Gemma3 API
gemma3Api.interceptors.request.use(
  (config) => {
    console.log(`Gemma3 API Request to: ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('Gemma3 API Request Error:', error);
    return Promise.reject(error);
  }
)

gemma3Api.interceptors.response.use(
  (response) => {
    console.log(`Gemma3 API Response from: ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('Gemma3 API Error Response:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('Gemma3 API No Response Error:', error.request);
    } else {
      console.error('Gemma3 API Request Setup Error:', error.message);
    }
    return Promise.reject(error);
  }
)

// Helper function to try the markdown approach for iFlow generation
async function tryMarkdownApproach(jobId, platform) {
    console.log(`Fetching markdown content for job: ${jobId} using platform: ${platform}`);
    const markdownBlob = await getDocumentation(jobId, 'markdown');
    const markdownContent = await markdownBlob.text();
    console.log(`Markdown content fetched, length: ${markdownContent.length} characters`);

    // Now send the markdown content directly to the appropriate iFlow API based on platform
    const apiInstance = getIflowApiInstance(platform);
    const response = await apiInstance.post(`/generate-iflow`, {
        markdown: markdownContent,
        iflow_name: `IFlow_${jobId.substring(0, 8)}`
    }, {
        timeout: 30000 // 30 second timeout
    });

    console.log("iFlow generation response:", response.data);
    return response.data;
}

// Provider-aware markdown approach
async function tryMarkdownApproachWithProvider(jobId, provider, platform = 'mulesoft') {
    console.log(`Fetching markdown content for job: ${jobId} using ${provider} for platform: ${platform}`);
    const markdownBlob = await getDocumentation(jobId, 'markdown');
    const markdownContent = await markdownBlob.text();
    console.log(`Markdown content fetched, length: ${markdownContent.length} characters`);

    const apiInstance = getIflowApiInstance(platform);

    // Configure timeout based on provider and platform
    let timeout = 30000; // Default 30 seconds
    if (provider === 'gemma3') {
        timeout = 300000; // 5 minutes for Gemma3
    } else if (platform === 'boomi') {
        timeout = 120000; // 2 minutes for Boomi (more complex processing)
    }

    // Send the markdown content to the appropriate API
    const response = await apiInstance.post(`/generate-iflow`, {
        markdown: markdownContent,
        iflow_name: `IFlow_${jobId.substring(0, 8)}`,
        provider: provider,
        platform: platform
    }, {
        timeout: timeout
    });

    console.log(`${provider} iFlow generation response for ${platform}:`, response.data);
    return response.data;
}

// Generate iFlow from markdown
export const generateIflow = async (jobId, platform = 'mulesoft') => {
    try {
        const selectedProvider = getSelectedLLMProvider();
        console.log(`Generating iFlow for job: ${jobId} using ${selectedProvider} for platform: ${platform}`);
        console.log(`Environment: ${ENV}`);

        // Get the appropriate API instance based on platform
        const apiInstance = getIflowApiInstance(platform);

        // Use a consistent approach for both development and production
        // First try the markdown approach, then fall back to direct approach if needed
        try {
            console.log(`Trying markdown approach first with ${selectedProvider}...`);

            // Add a health check first to verify the API is accessible
            try {
                console.log(`Checking ${selectedProvider} API health first...`);
                const healthResponse = await apiInstance.get('/health');
                console.log(`${selectedProvider} API health check response:`, healthResponse.data);
            } catch (healthError) {
                console.error(`${selectedProvider} API health check failed:`, healthError);
                console.log("Continuing with iFlow generation despite health check failure");
            }

            // Try the markdown approach with selected provider and platform
            return await tryMarkdownApproachWithProvider(jobId, selectedProvider, platform);
        } catch (markdownError) {
            console.error("Markdown approach failed:", markdownError);

            if (markdownError.response) {
                console.error("Response status:", markdownError.response.status);
                console.error("Response data:", markdownError.response.data);
            } else if (markdownError.request) {
                console.error("No response received from server");
            } else {
                console.error("Error message:", markdownError.message);
            }

            // If markdown approach fails, try the direct approach
            console.log("Trying direct iFlow generation with job ID...");

            // Get the appropriate API instance based on platform
            const apiInstance = getIflowApiInstance(platform);
            const fullUrl = `${apiInstance.defaults.baseURL}/generate-iflow/${jobId}`;
            console.log(`Calling iFlow API directly with job ID: ${jobId} using platform: ${platform}`);
            console.log(`Full URL: ${fullUrl}`);

            // Log the baseURL to verify it's correct
            console.log(`iFlow API baseURL: ${apiInstance.defaults.baseURL}`);

            const directResponse = await apiInstance.post(`/generate-iflow/${jobId}`, {}, {
                timeout: 30000 // 30 second timeout
            });

            console.log("Direct iFlow generation response:", directResponse.data);
            return directResponse.data;
        }
    } catch (error) {
        console.error("Error generating iFlow:", error);

        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
            return {
                status: 'error',
                message: `Error: ${error.response.status} - ${error.response.data?.error || error.response.data?.message || 'Unknown error'}`,
                error: error.response.data
            };
        } else if (error.request) {
            console.error("No response received:", error.request)
            return {
                status: 'error',
                message: 'Error: Could not connect to the iFlow API server. Please make sure it is running.',
                error: 'CONNECTION_ERROR'
            };
        } else {
            console.error("Error message:", error.message)
            return {
                status: 'error',
                message: `Error: ${error.message}`,
                error: 'UNKNOWN_ERROR'
            };
        }
    }
}

// Get iFlow generation status
export const getIflowGenerationStatus = async (jobId, platform = 'mulesoft') => {
    try {
        const selectedProvider = getSelectedLLMProvider();
        console.log(`Getting iFlow generation status for job: ${jobId} using ${selectedProvider} for platform: ${platform}`);

        const apiInstance = getIflowApiInstance(platform);

        // Add a timeout to the request to prevent hanging
        const response = await apiInstance.get(`/jobs/${jobId}`, {
            timeout: 30000 // 30 second timeout for iFlow generation
        });

        console.log(`${selectedProvider} iFlow generation status response:`, response.data);
        return response.data;
    } catch (error) {
        console.error("Error getting iFlow generation status:", error)
        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
            // Return a formatted error object instead of throwing
            return {
                status: 'error',
                message: `Error: ${error.response.status} - ${error.response.data?.error || 'Unknown error'}`,
                error: error.response.data
            };
        } else if (error.request) {
            console.error("No response received:", error.request)
            // Return a formatted error object for connection issues
            return {
                status: 'error',
                message: 'Error: Could not connect to the iFlow API server. Please make sure it is running.',
                error: 'CONNECTION_ERROR'
            };
        } else {
            console.error("Error message:", error.message)
            // Return a formatted error object for other errors
            return {
                status: 'error',
                message: `Error: ${error.message}`,
                error: 'UNKNOWN_ERROR'
            };
        }
    }
}

// Download generated iFlow
export const downloadGeneratedIflow = async (jobId, platform = 'mulesoft') => {
    try {
        const selectedProvider = getSelectedLLMProvider();
        console.log(`Downloading generated iFlow for job: ${jobId} using ${selectedProvider} for platform: ${platform}`);

        const apiInstance = getIflowApiInstance(platform);

        // Use the appropriate API instance with blob response type
        const response = await apiInstance.get(`/jobs/${jobId}/download`, {
            responseType: 'blob'
        });

        console.log(`Downloaded iFlow blob from ${selectedProvider}, size: ${response.data.size} bytes`);
        return response.data;
    } catch (error) {
        console.error("Error downloading generated iFlow:", error)
        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
        } else if (error.request) {
            console.error("No response received:", error.request)
        } else {
            console.error("Error message:", error.message)
        }
        throw error
    }
}



// Download iFlow debug file
export const downloadIflowDebugFile = async (jobId, fileName, platform = 'mulesoft') => {
    try {
        console.log(`Downloading iFlow debug file for job: ${jobId}, file: ${fileName}, platform: ${platform}`);

        // Get the appropriate API instance based on platform
        const apiInstance = getIflowApiInstance(platform);
        const response = await apiInstance.get(`/jobs/${jobId}/debug/${fileName}`, {
            responseType: 'blob'
        });

        console.log(`Downloaded iFlow debug file blob, size: ${response.data.size} bytes`);
        return response.data;
    } catch (error) {
        console.error("Error downloading iFlow debug file:", error)
        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
        } else if (error.request) {
            console.error("No response received:", error.request)
        } else {
            console.error("Error message:", error.message)
        }
        throw error
    }
}



// Deploy iFlow to SAP Integration Suite
export const deployIflowToSap = async (jobId, packageId, description, platform = 'mulesoft') => {
    try {
        console.log(`Deploying iFlow for job: ${jobId} to SAP Integration Suite using platform: ${platform}`);

        // Get the appropriate API instance based on platform
        const apiInstance = getIflowApiInstance(platform);
        const response = await apiInstance.post(`/jobs/${jobId}/deploy`, {
            package_id: packageId,
            description: description
        });

        console.log("iFlow deployment response:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error deploying iFlow to SAP:", error)
        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
        } else if (error.request) {
            console.error("No response received:", error.request)
        } else {
            console.error("Error message:", error.message)
        }
        throw error
    }
}



// Deploy iFlow directly to SAP Integration Suite using the direct deployment approach
export const directDeployIflowToSap = async (jobId, packageId, iflowId, iflowName, platform = 'mulesoft') => {
    try {
        console.log(`Directly deploying iFlow for job: ${jobId} to SAP Integration Suite using platform: ${platform}`);
        console.log(`Parameters: packageId=${packageId}, iflowId=${iflowId}, iflowName=${iflowName}`);

        // Get the appropriate API instance based on platform
        const apiInstance = getIflowApiInstance(platform);
        const response = await apiInstance.post(`/jobs/${jobId}/direct-deploy`, {
            package_id: packageId,
            iflow_id: iflowId,
            iflow_name: iflowName
        });

        console.log("Direct iFlow deployment response:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error directly deploying iFlow to SAP:", error)
        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
        } else if (error.request) {
            console.error("No response received:", error.request)
        } else {
            console.error("Error message:", error.message)
        }
        throw error
    }
}



// Update deployment status in Main API
export const updateDeploymentStatus = async (jobId, deploymentStatus, deploymentMessage = '', deploymentDetails = {}) => {
    try {
        console.log(`Updating deployment status for job ${jobId}: ${deploymentStatus}`);

        const response = await api.post(`/jobs/${jobId}/update-deployment-status`, {
            deployment_status: deploymentStatus,
            deployment_message: deploymentMessage,
            deployment_details: deploymentDetails
        });

        console.log("Deployment status update response:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error updating deployment status:", error)
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
        }
        throw error
    }
}



// NEW: Unified Deploy iFlow - uses the WORKING direct deployment for both platforms
export const unifiedDeployIflowToSap = async (jobId, packageId, iflowId, iflowName, platform = 'mulesoft') => {
    try {
        console.log(`🚀 Unified deploying iFlow for job: ${jobId} to SAP Integration Suite using platform: ${platform}`);
        console.log(`Using DIRECT deployment method that works for both platforms`);
        console.log(`Parameters: packageId=${packageId}, iflowId=${iflowId}, iflowName=${iflowName}`);

        // First attempt: Use the proven direct-deploy endpoint
        const result = await directDeployIflowToSap(jobId, packageId, iflowId, iflowName, platform);
        
        console.log("✅ Unified iFlow deployment successful (direct method):", result);
        return result;
        
    } catch (error) {
        console.error("❌ Direct deployment failed:", error)
        
        // For MuleSoft platform, try additional fallback methods
        if (platform === 'mulesoft') {
            try {
                console.log("🔄 Fallback 1: Trying unified-deploy endpoint for MuleToIS...");
                const apiInstance = getIflowApiInstance(platform);
                const response = await apiInstance.post(`/jobs/${jobId}/unified-deploy`, {
                    package_id: packageId,
                    iflow_id: iflowId,
                    iflow_name: iflowName
                });
                
                console.log("✅ Fallback unified deployment successful:", response.data);
                return response.data;
                
            } catch (fallbackError1) {
                console.error("❌ Unified-deploy fallback failed:", fallbackError1);
                
                // Final fallback: Try deploy-latest-iflow endpoint
                try {
                    console.log("🔄 Fallback 2: Trying deploy-latest-iflow endpoint...");
                    const apiInstance = getIflowApiInstance(platform);
                    const response = await apiInstance.post('/deploy-latest-iflow', {
                        package_id: packageId
                    });
                    
                    console.log("✅ Latest iFlow deployment successful:", response.data);
                    return response.data;
                    
                } catch (fallbackError2) {
                    console.error("❌ All fallback methods failed:", fallbackError2);
                    throw new Error(`All deployment methods failed. Original error: ${error.message}`);
                }
            }
        }
        
        // For Boomi platform or if all MuleSoft fallbacks fail
        throw error;
    }
}

// NEW: Deploy Latest iFlow - deploys the most recent ZIP file found
export const deployLatestIflow = async (packageId, platform = 'mulesoft') => {
    try {
        console.log(`🚀 Deploying latest iFlow to SAP Integration Suite using platform: ${platform}`);
        console.log(`Package ID: ${packageId}`);

        // Get the appropriate API instance based on platform
        const apiInstance = getIflowApiInstance(platform);
        const response = await apiInstance.post('/deploy-latest-iflow', {
            package_id: packageId
        });

        console.log("Latest iFlow deployment response:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error deploying latest iFlow to SAP:", error)
        // Add more detailed error logging
        if (error.response) {
            console.error("Response error data:", error.response.data)
            console.error("Response error status:", error.response.status)
        } else if (error.request) {
            console.error("No response received:", error.request)
        } else {
            console.error("Error message:", error.message)
        }
        throw error
    }
}

