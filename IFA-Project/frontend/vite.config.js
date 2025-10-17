import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import * as path from 'path';

// Load environment variables based on mode
export default ({ mode }) => {
  // Load env file based on `mode` in the current directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')

  // Get API URLs from environment variables or use defaults
  const SERVER_PATH = env.VITE_MAIN_API_PROTOCOL && env.VITE_MAIN_API_HOST
    ? `${env.VITE_MAIN_API_PROTOCOL}://${env.VITE_MAIN_API_HOST}/`
    : 'http://localhost:5000/'

  const IFLOW_SERVER_PATH = env.VITE_IFLOW_API_PROTOCOL && env.VITE_IFLOW_API_HOST
    ? `${env.VITE_IFLOW_API_PROTOCOL}://${env.VITE_IFLOW_API_HOST}/`
    : 'http://localhost:5003/'

  console.log('Using Main API Server:', SERVER_PATH)
  console.log('Using iFlow API Server:', IFLOW_SERVER_PATH)

  return defineConfig({
    plugins: [react()],
    build: {
      rollupOptions: {
        // Handle platform-specific dependencies gracefully
        external: (id) => {
          // Exclude all platform-specific rollup binaries
          return id.includes('@rollup/rollup-') && id.includes('-')
        },
        output: {
          // Ensure consistent builds across platforms
          manualChunks: undefined
        }
      },
      // Optimize for production deployment
      target: 'es2015',
      minify: process.env.NODE_ENV === 'production' ? 'terser' : 'esbuild',
      sourcemap: false,
      // Handle missing optional dependencies gracefully
      commonjsOptions: {
        ignoreDynamicRequires: true
      }
    },
    resolve: {
        alias: {
            '@pages': path.join(__dirname, 'src/pages'),
            '@layouts': path.join(__dirname, 'src/layouts'),
            '@assets': path.join(__dirname, 'src/assets'),
            '@styles': path.join(__dirname, 'src/styles'),
            '@components': path.join(__dirname, 'src/components'),
            '@contexts': path.join(__dirname, 'src/contexts'),
            '@hooks': path.join(__dirname, 'src/hooks'),
            '@services': path.join(__dirname, 'src/services'),
            '@utils': path.join(__dirname, 'src/utils'),
            '@': path.join(__dirname, 'src'),
        },
    },
    server: {
        proxy: {
            '/auth': {
                target: SERVER_PATH,
                changeOrigin: true,
                secure: false
            },
            '/attachments': {
                target: SERVER_PATH,
                changeOrigin: true,
                secure: false
            },
            '/api/generate-docs': {
                target: SERVER_PATH,
                changeOrigin: true,
                secure: false
            },
            // Main route for jobs - this will handle all job requests to the main API
            '/api/jobs': {
                target: SERVER_PATH,
                changeOrigin: true,
                secure: false
            },
            '/api/docs': {
                target: SERVER_PATH,
                changeOrigin: true,
                secure: false
            },
            // This route is no longer needed since we're using direct URLs
            // '/api/generate-iflow': {
            //     target: IFLOW_SERVER_PATH,
            //     changeOrigin: true,
            //     secure: false
            // },
            '/api/generate-iflow-match': {
                target: SERVER_PATH,  // This should go to port 5000
                changeOrigin: true,
                secure: false
            },
            '/api/iflow-match': {
                target: SERVER_PATH,
                changeOrigin: true,
                secure: false
            },
            '/api': {
                target: SERVER_PATH,
                changeOrigin: true,
                secure: false
            }
        }
    }
  })
}
