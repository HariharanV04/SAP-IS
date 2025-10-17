// api.js - Helper for API calls
import axios from 'axios';

// Use environment variable for API URL, with fallback to local development
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

console.log(`API configured with baseURL: ${baseURL}`);

// Create an axios instance with the base URL and CORS configuration
const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  // Required for CORS requests from different origins
  withCredentials: false,
  // Longer timeout for API requests (especially for file uploads)
  timeout: 60000
});

// Add request interceptor for debugging
api.interceptors.request.use(config => {
  console.log(`Making API request to: ${config.baseURL}${config.url}`);
  return config;
});

// Add response interceptor for handling errors
api.interceptors.response.use(
  response => {
    // Successful response
    console.log(`Received successful response from ${response.config.url} (${response.status})`);
    return response;
  },
  error => {
    // Error response
    if (error.response) {
      // Server responded with non-2xx status
      console.error(`API Error: ${error.response.status} - ${error.response.statusText}`);
      console.error('Error data:', error.response.data);
    } else if (error.request) {
      // Request was made but no response received (network error)
      console.error('Network Error: No response received from server');
      console.error('Request details:', error.request);
    } else {
      // Error in setting up the request
      console.error('Request Error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default api;
