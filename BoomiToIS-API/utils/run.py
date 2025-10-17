"""
Local development server for the MuleToIS API.
This script runs the Flask application using the Waitress WSGI server.
"""

import os
from waitress import serve
from app import app

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    
    print(f"Starting MuleToIS API server on port {port}...")
    print(f"API will be available at: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    # Run the application using Waitress
    serve(app, host="0.0.0.0", port=port)
