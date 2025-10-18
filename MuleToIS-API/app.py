"""
Flask API for the MuleToIS iFlow Generator.
This module provides a REST API for generating iFlows from markdown content.
"""

import os
import sys
import logging
import tempfile
import json
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import threading

# Import CORS configuration
from cors_config import get_cors_origin

# Set up NLTK data
try:
    import nltk_setup
    logging.info("NLTK setup completed")
except Exception as e:
    logging.warning(f"Warning: NLTK setup failed: {str(e)}")

# Run startup checks
try:
    import cf_startup_check
    if cf_startup_check.check_imports():
        logging.info("Startup checks completed successfully!")
    else:
        logging.warning("WARNING: Startup checks failed!")
except Exception as e:
    logging.error(f"Error running startup checks: {str(e)}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    # First, try to load environment-specific .env file
    env = os.getenv('FLASK_ENV', 'development')
    env_file = f".env.{env}"
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), env_file)

    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from: {env_path} ({env} environment)")
    else:
        # Fall back to default .env file
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"Loaded environment variables from: {env_path} (default)")
        else:
            logger.warning("No .env file found at expected locations")

    # Log environment configuration
    logger.info(f"Environment: {env}")
    logger.info(f"API Port: {os.getenv('PORT', '5001')}")
    logger.info(f"Main API URL: {os.getenv('MAIN_API_URL', 'http://localhost:5000')}")

except Exception as e:
    logger.error(f"Error loading environment variables: {str(e)}")

# Import the iFlow generator API
from iflow_generator_api import generate_iflow_from_markdown, IFlowGeneratorAPI

# Import the SAP BTP integration module
from sap_btp_integration import SapBtpIntegration

# Import the direct iFlow deployment module
from direct_iflow_deployment import DirectIflowDeployment, deploy_iflow

# SAP BTP Integration configuration
SAP_BTP_TENANT_URL = os.getenv('SAP_BTP_TENANT_URL')
SAP_BTP_CLIENT_ID = os.getenv('SAP_BTP_CLIENT_ID')
SAP_BTP_CLIENT_SECRET = os.getenv('SAP_BTP_CLIENT_SECRET')
SAP_BTP_OAUTH_URL = os.getenv('SAP_BTP_OAUTH_URL')
SAP_BTP_DEFAULT_PACKAGE = os.getenv('SAP_BTP_DEFAULT_PACKAGE')

# Create the Flask application
app = Flask(__name__)

# Get the appropriate CORS origin
cors_origin = get_cors_origin()
logger.info(f"Using CORS origin: {cors_origin}")

# Enable CORS for all routes with additional options
CORS(app, resources={r"/*": {"origins": cors_origin, "supports_credentials": True}})

# Add a global CORS handler
@app.after_request
def after_request(response):
    # Get the origin from the request
    origin = request.headers.get('Origin')

    # If cors_origin contains multiple origins (comma-separated)
    if ',' in cors_origin:
        # Parse the origins
        allowed_origins = [o.strip() for o in cors_origin.split(',')]

        # If the request origin is in the allowed list, use it
        if origin and origin in allowed_origins:
            response.headers.set('Access-Control-Allow-Origin', origin)
        # Otherwise use the first one
        elif allowed_origins:
            response.headers.set('Access-Control-Allow-Origin', allowed_origins[0])
        # Fallback
        else:
            response.headers.set('Access-Control-Allow-Origin', cors_origin)
    else:
        # Use the single origin
        response.headers.set('Access-Control-Allow-Origin', cors_origin)

    response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    # Set Access-Control-Allow-Credentials to true for credential requests
    response.headers.set('Access-Control-Allow-Credentials', 'true')
    return response

# Get the Anthropic API key from the .env file
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    logger.warning("No Anthropic API key found in .env file. API will not work without it.")

# RAG API Integration configuration
USE_RAG_GENERATION = os.getenv('USE_RAG_GENERATION', 'true').lower() == 'true'
RAG_API_URL = os.getenv('RAG_API_URL', 'http://localhost:5010')
RAG_API_TIMEOUT = int(os.getenv('RAG_API_TIMEOUT', '300'))  # 5 minutes default

# Log RAG configuration
logger.info(f"RAG Generation Enabled: {USE_RAG_GENERATION}")
if USE_RAG_GENERATION:
    logger.info(f"RAG API URL: {RAG_API_URL}")
    logger.info(f"RAG API Timeout: {RAG_API_TIMEOUT} seconds")

# Configure Flask app
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['RESULTS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
app.config['JOBS_FILE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jobs.json')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Function to load jobs from JSON file
def load_jobs():
    if os.path.exists(app.config['JOBS_FILE']):
        try:
            with open(app.config['JOBS_FILE'], 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("Error loading jobs file. Starting with empty jobs dictionary.")
    return {}

# Function to save jobs to JSON file
def save_jobs(jobs_dict):
    try:
        with open(app.config['JOBS_FILE'], 'w') as f:
            json.dump(jobs_dict, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving jobs file: {str(e)}")

# Protected job update function
def update_job_protected(job_id, updates):
    """Update job with protection against status regression"""
    if job_id in jobs:
        current_job = jobs[job_id]
        current_status = current_job.get('status')

        # If job is completed, protect against status regression
        if current_status == 'completed':
            protected_updates = {}

            for key, value in updates.items():
                if key == 'status' and value != 'completed':
                    print(f"🛡️ MuleToIS-API PROTECTION: Preventing status regression for job {job_id}: {current_status} → {value}")
                    continue  # Skip this update
                elif key == 'message' and 'processing' in str(value).lower():
                    print(f"🛡️ MuleToIS-API PROTECTION: Preventing message regression for job {job_id}")
                    continue  # Skip this update
                else:
                    protected_updates[key] = value

            if protected_updates:
                jobs[job_id].update(protected_updates)
                save_jobs(jobs)
            else:
                print(f"🛡️ MuleToIS-API PROTECTION: All updates blocked for completed job {job_id}")
        else:
            # Normal update for non-completed jobs
            jobs[job_id].update(updates)
            save_jobs(jobs)

# In-memory job storage (initialized from file and periodically saved to file)
jobs = load_jobs()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    response = jsonify({
        'status': 'ok',
        'message': 'MuleToIS API is running',
        'api_key_configured': bool(ANTHROPIC_API_KEY)
    })
    # Add CORS headers
    response.headers.set('Access-Control-Allow-Origin', cors_origin)
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.set('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/api/generate-iflow/<job_id>', methods=['POST', 'OPTIONS'])
@app.route('/api/generate-iflow', methods=['POST', 'OPTIONS'])
def generate_iflow(job_id=None):
    """
    Generate an iFlow from markdown content

    Request body:
    {
        "markdown": "# API Documentation...",
        "iflow_name": "MyIFlow" (optional)
    }

    Or if job_id is provided, it will fetch the markdown from the job.
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.set('Access-Control-Allow-Origin', cors_origin)
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 200

    try:
        # Check if API key is configured
        if not ANTHROPIC_API_KEY:
            return jsonify({
                'status': 'error',
                'message': 'Anthropic API key not configured. Please set ANTHROPIC_API_KEY in .env file.'
            }), 500

        # If job_id is provided, fetch the markdown from the main API
        if job_id:
            try:
                import requests

                # Get the main API URL from environment variables
                MAIN_API_URL = os.getenv('MAIN_API_URL', 'http://localhost:5000')
                MAIN_API_HOST = os.getenv('MAIN_API_HOST', 'localhost')
                MAIN_API_PORT = os.getenv('MAIN_API_PORT', '5000')
                MAIN_API_PROTOCOL = os.getenv('MAIN_API_PROTOCOL', 'http')

                # Construct the URL if not provided directly
                if not MAIN_API_URL:
                    MAIN_API_URL = f"{MAIN_API_PROTOCOL}://{MAIN_API_HOST}"
                    if MAIN_API_PORT and MAIN_API_PORT != '80' and MAIN_API_PORT != '443':
                        MAIN_API_URL += f":{MAIN_API_PORT}"

                # Fetch the markdown content from the main API
                logger.info(f"Fetching markdown content for job {job_id} from {MAIN_API_URL}")
                response = requests.get(f"{MAIN_API_URL}/api/docs/{job_id}/markdown")

                if response.status_code != 200:
                    logger.error(f"Error fetching markdown for job {job_id}: {response.status_code} {response.text}")
                    return jsonify({
                        'status': 'error',
                        'message': f'Error fetching markdown for job {job_id}: {response.status_code} {response.text}'
                    }), 500

                # Get the markdown content from the response
                markdown_content = response.text
                logger.info(f"Received markdown content length: {len(markdown_content)} characters")

                # Generate a job ID
                iflow_job_id = str(uuid.uuid4())

                # Create job record
                jobs[iflow_job_id] = {
                    'id': iflow_job_id,
                    'original_job_id': job_id,
                    'status': 'queued',
                    'created': str(uuid.uuid1()),
                    'message': 'Job queued. Starting iFlow generation...'
                }
                save_jobs(jobs)  # Save job data to file

                # Start processing in background
                thread = threading.Thread(
                    target=process_iflow_generation,
                    args=(iflow_job_id, markdown_content, f"IFlow_{job_id[:8]}")
                )
                thread.daemon = True
                thread.start()

                return jsonify({
                    'status': 'queued',
                    'message': 'iFlow generation started',
                    'job_id': iflow_job_id
                }), 202
            except Exception as e:
                logger.error(f"Error fetching markdown for job {job_id}: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'Error fetching markdown for job {job_id}: {str(e)}'
                }), 500

        # If no job_id, get markdown from request body
        data = request.json
        logger.info(f"Received request data: {data}")

        if not data or 'markdown' not in data:
            logger.error("Missing required parameter: markdown")
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameter: markdown'
            }), 400

        markdown_content = data['markdown']
        logger.info(f"Received markdown content length: {len(markdown_content)} characters")

        iflow_name = data.get('iflow_name')
        logger.info(f"Using iFlow name: {iflow_name}")

        # Generate a job ID
        job_id = str(uuid.uuid4())

        # Create job record
        jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'created': str(uuid.uuid1()),
            'message': 'Job queued. Starting iFlow generation...'
        }
        save_jobs(jobs)  # Save job data to file

        # Start processing in background
        thread = threading.Thread(
            target=process_iflow_generation,
            args=(job_id, markdown_content, iflow_name)
        )
        thread.daemon = True
        thread.start()

        response = jsonify({
            'status': 'queued',
            'message': 'iFlow generation started',
            'job_id': job_id
        })
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 202

    except Exception as e:
        logger.error(f"Error starting iFlow generation: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error starting iFlow generation: {str(e)}'
        }), 500

def process_iflow_generation(job_id, markdown_content, iflow_name=None):
    """
    Process the markdown content to generate an iFlow in a background thread

    Integration Strategy:
    1. Try RAG API if enabled (USE_RAG_GENERATION=true)
    2. Fallback to template-based generation if RAG fails or disabled

    Args:
        job_id: Job ID to identify the job
        markdown_content: Markdown content to process
        iflow_name: Name of the iFlow (optional)
    """
    try:
        # Create output directory in the job results folder
        job_result_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
        os.makedirs(job_result_dir, exist_ok=True)

        # Generate iFlow name if not provided
        if iflow_name is None:
            iflow_name = f"GeneratedIFlow_{job_id[:8]}"

        # Check if RAG generation is enabled
        if USE_RAG_GENERATION:
            logger.info(f"🤖 Using RAG API for iFlow generation: {RAG_API_URL}")

            try:
                import requests

                # Update job status
                update_job_protected(job_id, {
                    'status': 'processing',
                    'message': 'Generating iFlow using RAG AI system...'
                })

                # Get the original main job ID (not the MuleToIS job ID)
                main_job_id = jobs[job_id].get('original_job_id', job_id)

                # Call RAG API
                logger.info(f"📡 Sending request to RAG API: {RAG_API_URL}/api/generate-iflow-from-markdown")
                logger.info(f"   iFlow Name: {iflow_name}")
                logger.info(f"   Markdown Length: {len(markdown_content)} chars")
                logger.info(f"   Main Job ID: {main_job_id} (MuleToIS Job ID: {job_id})")

                rag_response = requests.post(
                    f"{RAG_API_URL}/api/generate-iflow-from-markdown",
                    json={
                        'markdown_content': markdown_content,
                        'iflow_name': iflow_name,
                        'job_id': main_job_id,  # Pass the MAIN job ID, not MuleToIS job ID
                        'output_dir': job_result_dir
                    },
                    timeout=RAG_API_TIMEOUT
                )

                # Check RAG API response
                if rag_response.status_code == 200:
                    rag_result = rag_response.json()

                    if rag_result.get('status') == 'success':
                        logger.info(f"✅ RAG API generated iFlow successfully")
                        logger.info(f"   Generation method: {rag_result.get('generation_method', 'RAG Agent')}")
                        logger.info(f"   Components: {len(rag_result.get('components', []))}")

                        # Get package path from RAG response
                        package_path = rag_result.get('files', {}).get('zip', '')

                        if package_path:
                            # Convert to relative path
                            relative_zip_path = os.path.relpath(package_path, os.path.dirname(os.path.abspath(__file__)))

                            # Update job with success status
                            update_job_protected(job_id, {
                                'status': 'completed',
                                'message': 'iFlow generation completed successfully using RAG AI!',
                                'files': {
                                    'zip': relative_zip_path,
                                    'debug': rag_result.get('files', {}).get('debug', {})
                                },
                                'iflow_name': iflow_name,
                                'components': rag_result.get('components', []),
                                'generation_method': 'RAG Agent (Dynamic)',
                                'metadata_path': rag_result.get('metadata_path', '')
                            })

                            logger.info(f"📦 iFlow package saved: {relative_zip_path}")
                            return  # Success - exit function
                        else:
                            logger.warning("⚠️ RAG API response missing package path")
                            raise ValueError("RAG API returned success but no package path")
                    else:
                        logger.warning(f"⚠️ RAG API returned non-success status: {rag_result.get('message')}")
                        raise ValueError(f"RAG API error: {rag_result.get('message')}")
                else:
                    logger.warning(f"⚠️ RAG API HTTP error: {rag_response.status_code}")
                    logger.warning(f"   Response: {rag_response.text[:500]}")
                    raise ValueError(f"RAG API returned status {rag_response.status_code}")

            except requests.exceptions.Timeout:
                logger.error(f"❌ RAG API timeout after {RAG_API_TIMEOUT} seconds")
                logger.info(f"⤵️ Falling back to template-based generation")
                # Continue to fallback below

            except requests.exceptions.RequestException as req_err:
                logger.error(f"❌ RAG API request failed: {str(req_err)}")
                logger.info(f"⤵️ Falling back to template-based generation")
                # Continue to fallback below

            except Exception as rag_err:
                logger.error(f"❌ RAG API error: {str(rag_err)}")
                logger.info(f"⤵️ Falling back to template-based generation")
                # Continue to fallback below
        else:
            logger.info(f"📝 RAG generation disabled - using template-based generation")

        # ═════════════════════════════════════════════════════════════════
        # FALLBACK: Template-based generation (original logic)
        # ═════════════════════════════════════════════════════════════════

        logger.info(f"🔧 Starting template-based iFlow generation")

        # Update job status
        update_job_protected(job_id, {
            'status': 'processing',
            'message': 'Analyzing markdown and generating iFlow...'
        })

        # Generate the iFlow using original template-based method
        result = generate_iflow_from_markdown(
            markdown_content=markdown_content,
            api_key=ANTHROPIC_API_KEY,
            output_dir=job_result_dir,
            iflow_name=iflow_name,
            job_id=job_id  # Pass job_id for real-time status updates
        )

        if result["status"] == "success":
            # Update job with file paths
            zip_path = result["files"]["zip"]
            relative_zip_path = os.path.relpath(zip_path, os.path.dirname(os.path.abspath(__file__)))

            # Add debug files if they exist
            debug_files = {}
            for debug_file, debug_path in result["files"]["debug"].items():
                relative_debug_path = os.path.relpath(debug_path, os.path.dirname(os.path.abspath(__file__)))
                debug_files[debug_file] = relative_debug_path

            update_job_protected(job_id, {
                'status': 'completed',
                'message': 'iFlow generation completed successfully!',
                'files': {
                    'zip': relative_zip_path,
                    'debug': debug_files
                },
                'iflow_name': iflow_name,
                'generation_method': 'Template-based (Fallback)'
            })

            logger.info(f"✅ Template-based generation completed successfully")
        else:
            update_job_protected(job_id, {
                'status': 'failed',
                'message': result["message"]
            })
            logger.error(f"❌ Template-based generation failed: {result['message']}")

    except Exception as e:
        logger.error(f"❌ Error generating iFlow: {str(e)}")
        update_job_protected(job_id, {
            'status': 'failed',
            'message': f'Error generating iFlow: {str(e)}'
        })

@app.route('/api/jobs/<job_id>', methods=['GET', 'OPTIONS'])
@app.route('/api/iflow-generation/<job_id>', methods=['GET', 'OPTIONS'])
def get_job_status(job_id):
    """Get the status of a job"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.set('Access-Control-Allow-Origin', cors_origin)
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 200

    if job_id not in jobs:
        # Check if the job has completed and the result file exists
        job_result_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
        if os.path.exists(job_result_dir):
            # Look for zip files in the result directory
            zip_files = []
            for root, dirs, files in os.walk(job_result_dir):
                for file in files:
                    if file.endswith('.zip'):
                        rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(os.path.abspath(__file__)))
                        zip_files.append(rel_path)

            if zip_files:
                # Job has completed and result file exists
                # Create a job record with completed status
                iflow_name = f"GeneratedIFlow_{job_id[:8]}"
                job_info = {
                    'id': job_id,
                    'status': 'completed',
                    'created': str(uuid.uuid1()),
                    'last_updated': str(uuid.uuid1()),
                    'message': 'iFlow generation completed successfully',
                    'files': {
                        'zip': zip_files[0],  # Use the first zip file
                        'debug': {}  # No debug files available
                    },
                    'iflow_name': iflow_name
                }
                # Store the job info for future requests
                jobs[job_id] = job_info
                save_jobs(jobs)  # Save job data to file

                # Return the job info
                response = jsonify(job_info)
                response.headers.set('Access-Control-Allow-Origin', cors_origin)
                response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
                response.headers.set('Access-Control-Allow-Credentials', 'true')
                return response, 200

        # If we get here, the job doesn't exist
        response = jsonify({'error': 'Job not found'})
        response.headers.set('Access-Control-Allow-Origin', cors_origin)
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 404

    response = jsonify(jobs[job_id])
    response.headers.set('Access-Control-Allow-Origin', cors_origin)
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.set('Access-Control-Allow-Credentials', 'true')
    return response, 200

@app.route('/api/jobs/<job_id>/download', methods=['GET'])
@app.route('/api/iflow-generation/<job_id>/download', methods=['GET'])
def download_iflow(job_id):
    """Download the generated iFlow ZIP file"""
    # First check if the job is in our jobs dictionary
    if job_id in jobs:
        job = jobs[job_id]

        # Check if job is completed
        if job['status'] != 'completed':
            return jsonify({
                'error': 'iFlow generation not completed',
                'status': job['status']
            }), 400

        # Check if ZIP file exists
        if 'files' not in job or 'zip' not in job['files']:
            return jsonify({'error': 'iFlow ZIP file not available'}), 404

        zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), job['files']['zip'])

        if not os.path.exists(zip_path):
            return jsonify({'error': 'iFlow ZIP file not found on server'}), 404

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{job.get('iflow_name', f'GeneratedIFlow_{job_id[:8]}')}.zip",
            mimetype='application/zip'
        )

    # If the job is not in our jobs dictionary, check if the result file exists directly
    job_result_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
    if os.path.exists(job_result_dir):
        # Look for zip files in the result directory
        for root, _, files in os.walk(job_result_dir):
            for file in files:
                if file.endswith('.zip'):
                    zip_path = os.path.join(root, file)
                    if os.path.exists(zip_path):
                        # Found a zip file, return it
                        return send_file(
                            zip_path,
                            as_attachment=True,
                            download_name=f"GeneratedIFlow_{job_id[:8]}.zip",
                            mimetype='application/zip'
                        )

    # If we get here, the job or zip file doesn't exist
    return jsonify({'error': 'iFlow ZIP file not found'}), 404

@app.route('/api/jobs/<job_id>/debug/<file_name>', methods=['GET'])
@app.route('/api/iflow-generation/<job_id>/debug/<file_name>', methods=['GET'])
def download_debug_file(job_id, file_name):
    """Download a debug file"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = jobs[job_id]

    # Check if job is completed
    if job['status'] != 'completed':
        return jsonify({
            'error': 'iFlow generation not completed',
            'status': job['status']
        }), 400

    # Check if debug file exists
    if ('files' not in job or
        'debug' not in job['files'] or
        file_name not in job['files']['debug']):
        return jsonify({'error': 'Debug file not available'}), 404

    debug_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), job['files']['debug'][file_name])

    if not os.path.exists(debug_path):
        return jsonify({'error': 'Debug file not found on server'}), 404

    return send_file(
        debug_path,
        as_attachment=True,
        download_name=file_name,
        mimetype='text/plain'
    )

@app.route('/api/jobs/<job_id>/deploy', methods=['POST', 'OPTIONS'])
@app.route('/api/iflow-generation/<job_id>/deploy', methods=['POST', 'OPTIONS'])
def deploy_to_sap(job_id):
    """
    Deploy the generated iFlow to SAP Integration Suite

    Request body:
    {
        "package_id": "MyPackage", // Optional, will use default if not provided
        "description": "My iFlow description" // Optional
    }
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.set('Access-Control-Allow-Origin', cors_origin)
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 200

    try:
        # Check if SAP BTP integration is configured
        if not all([SAP_BTP_TENANT_URL, SAP_BTP_CLIENT_ID, SAP_BTP_CLIENT_SECRET]):
            return jsonify({
                'status': 'error',
                'message': 'SAP BTP integration not configured. Please set SAP_BTP_* environment variables.'
            }), 500

        # First, check if this is a documentation job ID that was used to generate an iFlow
        iflow_job_id = None
        for jid, job_data in jobs.items():
            if job_data.get('original_job_id') == job_id:
                # Found an iFlow job that was generated from this documentation job
                iflow_job_id = jid
                logger.info(f"Found iFlow job {iflow_job_id} that was generated from documentation job {job_id}")
                break

        # If we found an iFlow job ID, use that instead
        if iflow_job_id:
            logger.info(f"Using iFlow job ID {iflow_job_id} instead of documentation job ID {job_id}")
            job_id = iflow_job_id

        # Check if job exists
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404

        job = jobs[job_id]

        # Check if job is completed
        if job['status'] != 'completed':
            return jsonify({
                'error': 'iFlow generation not completed',
                'status': job['status']
            }), 400

        # Check if ZIP file exists
        if 'files' not in job or 'zip' not in job['files']:
            return jsonify({'error': 'iFlow ZIP file not available'}), 404

        zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), job['files']['zip'])

        if not os.path.exists(zip_path):
            return jsonify({'error': 'iFlow ZIP file not found on server'}), 404

        # Get request data
        data = request.json or {}

        # Get package ID from request or use default
        package_id = data.get('package_id') or SAP_BTP_DEFAULT_PACKAGE
        if not package_id:
            return jsonify({
                'status': 'error',
                'message': 'No package ID provided and no default package configured'
            }), 400

        # Get description from request or use default
        description = data.get('description')

        # Get iFlow name from job
        iflow_name = job.get('iflow_name', f"GeneratedIFlow_{job_id[:8]}")

        # Update job status
        jobs[job_id].update({
            'deployment_status': 'deploying',
            'deployment_message': 'Deploying to SAP Integration Suite...'
        })
        save_jobs(jobs)  # Save job data to file

        # Initialize SAP BTP integration client
        sap_client = SapBtpIntegration(
            tenant_url=SAP_BTP_TENANT_URL,
            client_id=SAP_BTP_CLIENT_ID,
            client_secret=SAP_BTP_CLIENT_SECRET,
            oauth_url=SAP_BTP_OAUTH_URL
        )

        # Deploy the iFlow
        result = sap_client.deploy_integration_flow(
            package_id=package_id,
            iflow_name=iflow_name,
            iflow_zip_path=zip_path,
            description=description
        )

        # Update job status
        jobs[job_id].update({
            'deployment_status': 'completed',
            'deployment_message': 'Deployment completed successfully',
            'deployment_details': result,
            'iflow_name': iflow_name  # Preserve the iflow_name after deployment
        })
        save_jobs(jobs)  # Save job data to file

        return jsonify({
            'status': 'success',
            'message': 'iFlow deployed successfully',
            'details': result
        }), 200

    except Exception as e:
        logger.error(f"Error deploying iFlow: {str(e)}")

        # Update job status
        if job_id in jobs:
            jobs[job_id].update({
                'deployment_status': 'failed',
                'deployment_message': f'Error deploying iFlow: {str(e)}',
                'iflow_name': iflow_name  # Preserve the iflow_name even on failure
            })
            save_jobs(jobs)  # Save job data to file

        return jsonify({
            'status': 'error',
            'message': f'Error deploying iFlow: {str(e)}'
        }), 500

@app.route('/api/fix-iflow', methods=['POST', 'OPTIONS'])
def fix_iflow():
    """
    Fix an existing iFlow file to ensure compatibility with SAP Integration Suite

    Request body:
    {
        "file_path": "/path/to/iflow.iflw",  # Path to the iFlow file to fix
        "create_backup": true                # Whether to create a backup of the original file (optional, default: true)
    }

    Returns:
    {
        "status": "success" | "warning" | "error",
        "message": "Description of the result",
        "file_path": "/path/to/fixed/iflow.iflw"  # Path to the fixed iFlow file
    }
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.set('Access-Control-Allow-Origin', cors_origin)
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 200

    try:
        # Get request data
        data = request.json
        logger.info(f"Received fix-iflow request: {data}")

        if not data or 'file_path' not in data:
            logger.error("Missing required parameter: file_path")
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameter: file_path'
            }), 400

        file_path = data['file_path']
        create_backup = data.get('create_backup', True)

        # Initialize the iFlow generator API
        generator_api = IFlowGeneratorAPI(api_key=ANTHROPIC_API_KEY)

        # Fix the iFlow file
        result = generator_api.fix_iflow_file(file_path, create_backup)

        # Return the result
        return jsonify(result), 200 if result['status'] != 'error' else 500

    except Exception as e:
        logger.error(f"Error fixing iFlow file: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error fixing iFlow file: {str(e)}'
        }), 500

@app.route('/api/jobs/<job_id>/direct-deploy', methods=['POST', 'OPTIONS'])
@app.route('/api/iflow-generation/<job_id>/direct-deploy', methods=['POST', 'OPTIONS'])
def direct_deploy_to_sap(job_id):
    """
    Deploy the generated iFlow directly to SAP Integration Suite using the direct deployment approach

    Request body:
    {
        "package_id": "MyPackage", // Optional, will use default if not provided
        "iflow_id": "MyIFlowId",   // Optional, will use filename without extension if not provided
        "iflow_name": "My iFlow"   // Optional, will use filename without extension if not provided
    }

    Returns:
    {
        "status": "success" | "error",
        "message": "Description of the result",
        "iflow_id": "MyIFlowId",
        "package_id": "MyPackage",
        "iflow_name": "My iFlow"
    }
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.set('Access-Control-Allow-Origin', cors_origin)
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 200

    try:
        # Get request data
        data = request.json or {}

        # Get parameters from request or use defaults
        package_id = data.get('package_id', 'WithRequestReply')
        iflow_id = data.get('iflow_id')
        iflow_name = data.get('iflow_name')

        # First, check if this is a documentation job ID that was used to generate an iFlow
        iflow_job_id = None
        for jid, job_data in jobs.items():
            if job_data.get('original_job_id') == job_id:
                # Found an iFlow job that was generated from this documentation job
                iflow_job_id = jid
                logger.info(f"Found iFlow job {iflow_job_id} that was generated from documentation job {job_id}")
                break

        # If we found an iFlow job ID, use that instead
        if iflow_job_id:
            logger.info(f"Using iFlow job ID {iflow_job_id} instead of documentation job ID {job_id}")
            job_id = iflow_job_id

        # Check if job exists
        if job_id not in jobs:
            logger.warning(f"Job not found directly: {job_id}")

            # Try to find the job by searching for the iFlow file in the results directory
            results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
            found_job_id = None
            found_zip_path = None

            # Look for the iFlow file in all job directories
            for job_dir in os.listdir(results_dir):
                job_path = os.path.join(results_dir, job_dir)
                if os.path.isdir(job_path):
                    # Look for zip files that match the pattern
                    for file in os.listdir(job_path):
                        if file.endswith('.zip') and ('IFlow_' + job_id[:8]) in file:
                            found_job_id = job_dir
                            found_zip_path = os.path.join(job_path, file)
                            logger.info(f"Found matching iFlow file: {found_zip_path} for job ID prefix: {job_id[:8]}")
                            break

                    if found_job_id:
                        break

            if found_job_id:
                logger.info(f"Using alternative job ID: {found_job_id} instead of {job_id}")
                job_id = found_job_id
            else:
                logger.error(f"Job not found and no matching iFlow file found: {job_id}")
                return jsonify({
                    'status': 'error',
                    'message': f'Job not found: {job_id}'
                }), 404

        # Get job data
        job = jobs[job_id]

        # Check if job is completed
        if job['status'] != 'completed':
            logger.error(f"Job not completed: {job_id}")
            return jsonify({
                'status': 'error',
                'message': f'iFlow generation not completed. Current status: {job["status"]}'
            }), 400

        # Check if ZIP file exists
        zip_path = None

        # First check if the ZIP file is in the job data
        if 'files' in job and 'zip' in job['files']:
            zip_path = job['files']['zip']
            if os.path.exists(zip_path):
                logger.info(f"Found ZIP file in job data: {zip_path}")
            else:
                logger.warning(f"ZIP file in job data does not exist: {zip_path}")
                zip_path = None

        # If ZIP file not found in job data, search for it in the results directory
        if not zip_path:
            logger.info(f"Searching for ZIP file in results directory for job: {job_id}")
            job_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', job_id)

            if os.path.exists(job_dir):
                for file in os.listdir(job_dir):
                    if file.endswith('.zip'):
                        zip_path = os.path.join(job_dir, file)
                        logger.info(f"Found ZIP file: {zip_path}")
                        break

        # If still not found, try looking for a file with the iFlow ID in the name
        if not zip_path and iflow_id:
            logger.info(f"Searching for ZIP file with iFlow ID: {iflow_id}")
            job_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', job_id)

            if os.path.exists(job_dir):
                for file in os.listdir(job_dir):
                    if file.endswith('.zip') and iflow_id in file:
                        zip_path = os.path.join(job_dir, file)
                        logger.info(f"Found ZIP file with iFlow ID: {zip_path}")
                        break

        # If still not found, return error
        if not zip_path:
            logger.error(f"ZIP file not found for job: {job_id}")
            return jsonify({
                'status': 'error',
                'message': 'iFlow ZIP file not available'
            }), 404

        # Update job status
        jobs[job_id].update({
            'deployment_status': 'deploying',
            'deployment_message': 'Deploying to SAP Integration Suite using direct deployment...'
        })
        save_jobs(jobs)  # Save job data to file

        # Deploy the iFlow using direct deployment
        logger.info(f"Deploying iFlow using direct deployment: {zip_path}")
        deployment_result = deploy_iflow(
            iflow_path=zip_path,
            iflow_id=iflow_id,
            iflow_name=iflow_name,
            package_id=package_id
        )

        # Update job status based on deployment result
        if deployment_result['status'] == 'success':
            jobs[job_id].update({
                'deployment_status': 'completed',
                'deployment_message': 'iFlow deployed successfully',
                'deployment_details': deployment_result,
                'iflow_name': iflow_name  # Preserve the iflow_name after successful deployment
            })
            save_jobs(jobs)  # Save job data to file
        else:
            jobs[job_id].update({
                'deployment_status': 'failed',
                'deployment_message': f'Deployment failed: {deployment_result["message"]}',
                'deployment_details': deployment_result,
                'iflow_name': iflow_name  # Preserve the iflow_name even on failure
            })
            save_jobs(jobs)  # Save job data to file

        # Return the deployment result
        return jsonify(deployment_result), 200 if deployment_result['status'] == 'success' else 500

    except Exception as e:
        logger.error(f"Error deploying iFlow: {str(e)}")

        # Update job status
        if job_id in jobs:
            jobs[job_id].update({
                'deployment_status': 'failed',
                'deployment_message': f'Deployment failed: {str(e)}',
                'iflow_name': iflow_name  # Preserve the iflow_name even on exception
            })
            save_jobs(jobs)  # Save job data to file

        return jsonify({
            'status': 'error',
            'message': f'Error deploying iFlow: {str(e)}'
        }), 500

@app.route('/api/jobs/<job_id>/unified-deploy', methods=['POST', 'OPTIONS'])
@app.route('/api/iflow-generation/<job_id>/unified-deploy', methods=['POST', 'OPTIONS'])
def unified_deploy_to_sap(job_id):
    """
    Deploy the generated iFlow using unified deployment logic that handles job ID mapping issues
    This endpoint uses the robust file finding logic from BoomiToIS to solve deployment problems
    
    Request body:
    {
        "package_id": "MyPackage", // Optional, will use default if not provided
        "iflow_id": "MyIFlowId",   // Optional, will use auto-generated ID if not provided
        "iflow_name": "My iFlow"   // Optional, will use filename if not provided
    }

    Returns:
    {
        "status": "success" | "error",
        "message": "Description of the result",
        "iflow_id": "MyIFlowId",
        "package_id": "MyPackage",
        "iflow_name": "My iFlow",
        "file_deployed": "filename.zip"
    }
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.set('Access-Control-Allow-Origin', cors_origin)
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 200

    try:
        # Import the unified deployment module
        from unified_deployment import UnifiedIflowDeployment
        
        # Get request data
        data = request.json or {}
        
        # Get parameters from request or use defaults
        package_id = data.get('package_id', 'ConversionPackages')
        iflow_id = data.get('iflow_id')
        iflow_name = data.get('iflow_name')
        
        logger.info(f"🚀 Starting unified deployment for job {job_id}")
        logger.info(f"Parameters: package_id={package_id}, iflow_id={iflow_id}, iflow_name={iflow_name}")
        
        # Initialize unified deployment
        unified_deployment = UnifiedIflowDeployment()
        
        # Deploy using unified logic - this handles job ID mapping issues automatically
        result = unified_deployment.deploy_any_available_iflow(
            job_id=job_id,
            package_id=package_id,
            iflow_id=iflow_id,
            iflow_name=iflow_name
        )
        
        logger.info(f"Unified deployment result: {result}")
        
        if result['status'] == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in unified deployment: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error in unified deployment: {str(e)}'
        }), 500

@app.route('/api/deploy-latest-iflow', methods=['POST', 'OPTIONS'])
def deploy_latest_iflow_endpoint():
    """
    Deploy the most recent iFlow file found - simplest deployment option
    This endpoint doesn't require a job ID and just deploys whatever is the newest ZIP file
    
    Request body:
    {
        "package_id": "MyPackage"  // Optional, will use default if not provided
    }
    """
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.set('Access-Control-Allow-Origin', cors_origin)
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 200

    try:
        # Import the unified deployment module
        from unified_deployment import deploy_latest_iflow
        
        # Get request data
        data = request.json or {}
        package_id = data.get('package_id', 'ConversionPackages')
        
        logger.info(f"🚀 Deploying latest iFlow to package: {package_id}")
        
        # Deploy the latest iFlow
        result = deploy_latest_iflow(package_id=package_id)
        
        logger.info(f"Latest iFlow deployment result: {result}")
        
        if result['status'] == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error deploying latest iFlow: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error deploying latest iFlow: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # MuleToIS API runs on port 5001
    app.run(host='0.0.0.0', port=port, debug=True)
