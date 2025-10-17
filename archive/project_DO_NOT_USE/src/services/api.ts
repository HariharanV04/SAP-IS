import { JobInfo } from '../types';
import api from '../utils/api';

// Use environment variable for API URL
const API_URL = import.meta.env.VITE_API_URL;

// Add this test function to check connectivity with proper error handling
export const testBackendConnection = async (): Promise<boolean> => {
  try {
    console.log('Testing connection to backend at:', API_URL);

    // Use our axios instance which has the proper baseURL configuration
    const response = await api.get('/health');

    console.log('Backend connection test successful:', response.status);
    return true;
  } catch (error) {
    console.error('Backend connection test failed:', error);

    // Try a direct fetch with mode: 'no-cors' as a fallback
    try {
      console.log('Attempting fallback connection test...');
      const response = await fetch(`${API_URL}/health`, {
        method: 'GET',
        mode: 'no-cors' // This will prevent CORS errors but won't give us response data
      });

      // With 'no-cors', we can't check status, but at least we didn't get a network error
      console.log('Fallback connection completed without network errors');
      return true;
    } catch (fallbackError) {
      console.error('Fallback connection test failed:', fallbackError);
      return false;
    }
  }
};

// Modify generateDocs to use axios
export const generateDocs = async (formData: FormData, signal?: AbortSignal): Promise<{ job_id: string; status: string; message: string } | null> => {
  try {
    console.log('Sending request to generate documentation');

    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      signal
    };

    const response = await api.post('/generate-docs', formData, config);
    console.log('Response received:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error generating docs:', error);
    throw error;
  }
};

// Update getJobStatus to use axios
export const getJobStatus = async (jobId: string): Promise<JobInfo | null> => {
  try {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting job status:', error);
    throw error;
  }
};

// Update getAllJobs to use axios
export const getAllJobs = async (): Promise<JobInfo[]> => {
  try {
    const response = await api.get('/jobs');
    return response.data;
  } catch (error) {
    console.error('Error getting all jobs:', error);
    throw error;
  }
};

// Update getDocumentation to use axios with responseType blob
export const getDocumentation = async (jobId: string, fileType: 'markdown' | 'html' | 'visualization'): Promise<Blob> => {
  try {
    const response = await api.get(`/docs/${jobId}/${fileType}`, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error('Error getting documentation:', error);
    throw error;
  }
};

// Generate iFlow match for a job
export const generateIflowMatch = async (jobId: string): Promise<{ status: string; message: string }> => {
  try {
    const response = await api.post(`/generate-iflow-match/${jobId}`);
    return response.data;
  } catch (error) {
    console.error('Error generating iFlow match:', error);
    throw error;
  }
};

// Get iFlow match status
export const getIflowMatchStatus = async (jobId: string): Promise<{
  status: string;
  message: string;
  result?: any;
  files?: Record<string, string>;
}> => {
  try {
    const response = await api.get(`/iflow-match/${jobId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting iFlow match status:', error);
    throw error;
  }
};

// Get iFlow match file
export const getIflowMatchFile = async (jobId: string, fileType: 'report' | 'summary'): Promise<Blob> => {
  try {
    const response = await api.get(`/iflow-match/${jobId}/${fileType}`, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error('Error getting iFlow match file:', error);
    throw error;
  }
};