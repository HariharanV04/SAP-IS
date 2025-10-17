// debug-env.js - Debug utility to log environment variables

// Function to log all environment variables
export function logEnvironmentVariables() {
  console.log('===== Environment Variables =====');
  
  // Log Vite environment variables
  console.log('Vite Environment Variables:');
  for (const key in import.meta.env) {
    console.log(`${key}: ${import.meta.env[key]}`);
  }
  
  // Log specific API URL variables
  console.log('\nAPI URL Variables:');
  console.log(`VITE_API_URL: ${import.meta.env.VITE_API_URL}`);
  console.log(`import.meta.env.VITE_API_URL: ${import.meta.env.VITE_API_URL}`);
  console.log(`process.env.REACT_APP_API_URL: ${process.env?.REACT_APP_API_URL}`);
  
  // Log baseURL from API configuration
  console.log('\nAPI Configuration:');
  console.log(`baseURL from api.js: ${import.meta.env.VITE_API_URL || 'http://localhost:8080/api'}`);
  
  console.log('================================');
}

// Export a default function that does nothing
export default function debugEnv() {
  // This function is just a placeholder
  return null;
}
