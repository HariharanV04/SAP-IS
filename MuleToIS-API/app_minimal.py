"""
Minimal Flask API for testing Cloud Foundry deployment.
This is a simplified version of the MuleToIS API for testing deployment.
"""

import os
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'MuleToIS API (minimal version) is running'
    })

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'MuleToIS API (minimal version) is running',
        'endpoints': [
            '/api/health',
            '/'
        ]
    })

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8080))
    
    logger.info(f"Starting minimal MuleToIS API server on port {port}...")
    app.run(host='0.0.0.0', port=port)
