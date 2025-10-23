"""
Flask API for the BoomiToIS iFlow Generator.
This module provides a REST API for generating iFlows from Dell Boomi process documentation.
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
    from utils.nltk_setup import setup_nltk
    setup_nltk()
    logging.info("NLTK setup completed")
except Exception as e:
    logging.warning(f"Warning: NLTK setup failed: {str(e)}")

# Run startup checks
try:
    from utils.cf_startup_check import check_imports
    if check_imports():
        logging.info("Startup checks completed successfully!")
    else:
        logging.warning("WARNING: Startup checks failed!")
except Exception as e:
    logging.error(f"Error running startup checks: {str(e)}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DEBUG: Log current working directory and Python path
logger.info("=" * 80)
logger.info("DEBUG: Application startup information")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
logger.info("=" * 80)

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

# Import feedback API
from feedback_api import feedback_bp

# SAP BTP Integration configuration
SAP_BTP_TENANT_URL = os.getenv('SAP_BTP_TENANT_URL')
SAP_BTP_CLIENT_ID = os.getenv('SAP_BTP_CLIENT_ID')
SAP_BTP_CLIENT_SECRET = os.getenv('SAP_BTP_CLIENT_SECRET')
SAP_BTP_OAUTH_URL = os.getenv('SAP_BTP_OAUTH_URL')
SAP_BTP_DEFAULT_PACKAGE = os.getenv('SAP_BTP_DEFAULT_PACKAGE')

# RAG API Integration configuration
USE_RAG_GENERATION = os.getenv('USE_RAG_GENERATION', 'true').lower() == 'true'
RAG_API_URL = os.getenv('RAG_API_URL', 'http://localhost:5010')
RAG_API_TIMEOUT = int(os.getenv('RAG_API_TIMEOUT', '300'))  # 5 minutes default

# Log RAG configuration
logger.info(f"RAG Generation Enabled: {USE_RAG_GENERATION}")
if USE_RAG_GENERATION:
    logger.info(f"RAG API URL: {RAG_API_URL}")
    logger.info(f"RAG API Timeout: {RAG_API_TIMEOUT} seconds")

# Create the Flask application
app = Flask(__name__)

# Get the appropriate CORS origin
cors_origin = get_cors_origin()
logger.info(f"Using CORS origin: {cors_origin}")

# Enable CORS for all routes with additional options
CORS(app, resources={r"/*": {"origins": cors_origin, "supports_credentials": True}})

# Register feedback blueprint
app.register_blueprint(feedback_bp)

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
        jobs_file_path = app.config['JOBS_FILE']
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(jobs_file_path), exist_ok=True)
        
        # Write to a temporary file first, then rename (atomic operation)
        temp_file = jobs_file_path + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_dict, f, indent=2, default=str)
        
        # Rename temp file to actual file (atomic on most systems)
        if os.path.exists(jobs_file_path):
            os.remove(jobs_file_path)
        os.rename(temp_file, jobs_file_path)
    except Exception as e:
        logging.error(f"Error saving jobs file to '{app.config.get('JOBS_FILE', 'unknown')}': {str(e)}")
        import traceback
        logging.error(traceback.format_exc())

# In-memory job storage (initialized from file and periodically saved to file)
jobs = load_jobs()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    response = jsonify({
        'status': 'ok',
        'message': 'BoomiToIS API is running',
        'platform': 'Dell Boomi',
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

        # Get markdown from request body first (prioritize direct markdown over fetching)
        data = request.json
        
        # DEBUG: Log incoming request details
        logger.info(f"📥 Incoming request to generate-iflow:")
        logger.info(f"   URL job_id parameter: {job_id}")
        logger.info(f"   Request body keys: {list(data.keys()) if data else 'None'}")
        if data:
            logger.info(f"   Body has job_id: {'job_id' in data}")
            if 'job_id' in data:
                logger.info(f"   Body job_id value: {data['job_id']}")

        # Check if markdown is provided in request body
        if data and 'markdown' in data:
            # Use markdown from request body (for document upload jobs)
            markdown_content = data['markdown']
            logger.info(f"Using markdown from request body, length: {len(markdown_content)} characters")

            # CRITICAL: Extract job_id from request body if not in URL
            if not job_id and 'job_id' in data:
                job_id = data['job_id']
                logger.info(f"📌 Using job_id from request body: {job_id}")
            elif job_id:
                logger.info(f"📌 Using job_id from URL parameter: {job_id}")
            else:
                logger.warning(f"⚠️ No job_id found in URL or request body!")

            iflow_name = data.get('iflow_name', f"IFlow_{job_id[:8] if job_id else 'Generated'}")
            source_type = data.get('source_type', 'unknown')
            logger.info(f"Using iFlow name: {iflow_name}, source type: {source_type}")

        elif job_id:
            # Fallback: fetch markdown from main API (for traditional XML processing jobs)
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
                logger.info(f"Received markdown content from API, length: {len(markdown_content)} characters")
                iflow_name = f"IFlow_{job_id[:8]}"
                source_type = "xml_processing"

            except Exception as e:
                logger.error(f"Error fetching markdown for job {job_id}: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'Error fetching markdown for job {job_id}: {str(e)}'
                }), 500
        else:
            # No markdown in request body and no job_id
            logger.error("Missing required parameter: markdown")
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameter: markdown'
            }), 400
        # Generate a new job ID for iFlow generation
        iflow_job_id = str(uuid.uuid4())

        # PERSISTENT MAPPING: Store job_id mapping even if None
        # This creates a retrievable relationship for status updates later
        job_mapping_file = os.path.join(app.config['RESULTS_FOLDER'], 'job_mappings.json')
        try:
            if os.path.exists(job_mapping_file):
                with open(job_mapping_file, 'r') as f:
                    job_mappings = json.load(f)
            else:
                job_mappings = {}
        except:
            job_mappings = {}
        
        # Store bidirectional mapping
        if job_id:
            job_mappings[iflow_job_id] = job_id  # BoomiToIS → Main API
            job_mappings[job_id] = iflow_job_id  # Main API → BoomiToIS
            logger.info(f"💾 Saved job mapping: {iflow_job_id} ↔ {job_id}")
        else:
            # Even if job_id is None, store the BoomiToIS job_id for future lookup
            job_mappings[iflow_job_id] = None
            logger.warning(f"💾 Saved BoomiToIS job without Main API job_id: {iflow_job_id}")
        
        # Save mappings to file
        os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
        with open(job_mapping_file, 'w') as f:
            json.dump(job_mappings, f, indent=2)

        # Create job record
        jobs[iflow_job_id] = {
            'id': iflow_job_id,
            'original_job_id': job_id,  # Keep reference to original job if provided
            'status': 'queued',
            'created': str(uuid.uuid1()),
            'message': 'Job queued. Starting iFlow generation...',
            'source_type': source_type
        }
        save_jobs(jobs)  # Save job data to file

        # Start processing in background
        thread = threading.Thread(
            target=process_iflow_generation,
            args=(iflow_job_id, markdown_content, iflow_name)
        )
        thread.daemon = True
        thread.start()

        response = jsonify({
            'status': 'queued',
            'message': 'iFlow generation started',
            'job_id': iflow_job_id
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

    Args:
        job_id: Job ID to identify the job
        markdown_content: Markdown content to process
        iflow_name: Name of the iFlow (optional)
    """
    try:
        # Create output directory in the job results folder
        job_result_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
        os.makedirs(job_result_dir, exist_ok=True)

        # Update job status
        jobs[job_id].update({
            'status': 'processing',
            'message': 'Initializing iFlow generator...'
        })
        save_jobs(jobs)  # Save job data to file

        # Update job status
        jobs[job_id].update({
            'status': 'processing',
            'message': 'Analyzing markdown and generating iFlow...'
        })
        save_jobs(jobs)  # Save job data to file

        # Generate the iFlow
        if iflow_name is None:
            iflow_name = f"GeneratedIFlow_{job_id[:8]}"

        # Check if RAG generation is enabled
        if USE_RAG_GENERATION:
            logger.info(f"🤖 Using RAG API for iFlow generation: {RAG_API_URL}")

            try:
                import requests

                # Update job status
                jobs[job_id].update({
                    'status': 'processing',
                    'message': 'Generating iFlow using RAG AI system...'
                })
                save_jobs(jobs)

                # Get the original main job ID (not the BoomiToIS job ID)
                main_job_id = jobs[job_id].get('original_job_id', job_id)

                # Call RAG API
                logger.info(f"📡 Sending request to RAG API: {RAG_API_URL}/api/generate-iflow-from-markdown")
                logger.info(f"   iFlow Name: {iflow_name}")
                logger.info(f"   Main Job ID: {main_job_id} (BoomiToIS Job ID: {job_id})")

                rag_response = requests.post(
                    f"{RAG_API_URL}/api/generate-iflow-from-markdown",
                    json={
                        'markdown_content': markdown_content,
                        'iflow_name': iflow_name,
                        'job_id': main_job_id,  # Pass the MAIN job ID, not BoomiToIS job ID
                        'output_dir': job_result_dir
                    },
                    timeout=RAG_API_TIMEOUT
                )

                if rag_response.status_code == 200:
                    result = rag_response.json()
                    logger.info(f"✅ RAG API returned 200 status")
                    logger.info(f"   Generation method: {result.get('generation_method', 'RAG Agent')}")
                    logger.info(f"   Components: {len(result.get('components', []))}")
                    
                    # Validate RAG response has valid package path
                    package_path = result.get('files', {}).get('zip', '')
                    if not package_path or package_path.strip() == '':
                        logger.error(f"❌ RAG API returned empty package_path")
                        logger.warning("⚠️ Falling back to template-based generation")
                        
                        # Fallback to template-based generation
                        result = generate_iflow_from_markdown(
                            markdown_content=markdown_content,
                            api_key=ANTHROPIC_API_KEY,
                            output_dir=job_result_dir,
                            iflow_name=iflow_name,
                            job_id=job_id,
                            use_converter=False
                        )
                        result['generation_method'] = 'Template-based (RAG empty path fallback)'
                    else:
                        logger.info(f"   Package path: {package_path}")
                else:
                    logger.error(f"❌ RAG API error: {rag_response.status_code} - {rag_response.text}")
                    logger.warning("⚠️ Falling back to template-based generation")

                    # Fallback to template-based generation
                    result = generate_iflow_from_markdown(
                        markdown_content=markdown_content,
                        api_key=ANTHROPIC_API_KEY,
                        output_dir=job_result_dir,
                        iflow_name=iflow_name,
                        job_id=job_id,
                        use_converter=False
                    )
                    result['generation_method'] = 'Template-based (RAG fallback)'

            except requests.exceptions.Timeout:
                logger.error(f"❌ RAG API timeout after {RAG_API_TIMEOUT} seconds")
                logger.warning("⚠️ Falling back to template-based generation")

                # Fallback to template-based generation
                result = generate_iflow_from_markdown(
                    markdown_content=markdown_content,
                    api_key=ANTHROPIC_API_KEY,
                    output_dir=job_result_dir,
                    iflow_name=iflow_name,
                    job_id=job_id,
                    use_converter=False
                )
                result['generation_method'] = 'Template-based (RAG timeout fallback)'

            except Exception as e:
                logger.error(f"❌ Error calling RAG API: {str(e)}")
                logger.warning("⚠️ Falling back to template-based generation")

                # Fallback to template-based generation
                result = generate_iflow_from_markdown(
                    markdown_content=markdown_content,
                    api_key=ANTHROPIC_API_KEY,
                    output_dir=job_result_dir,
                    iflow_name=iflow_name,
                    job_id=job_id,
                    use_converter=False
                )
                result['generation_method'] = 'Template-based (RAG error fallback)'
        else:
            # Use original template-based generation
            logger.info("📝 Using template-based iFlow generation (RAG disabled)")
            result = generate_iflow_from_markdown(
                markdown_content=markdown_content,
                api_key=ANTHROPIC_API_KEY,
                output_dir=job_result_dir,
                iflow_name=iflow_name,
                job_id=job_id,
                use_converter=False  # Use template-based approach for proper SAP Integration Suite XML
            )
            result['generation_method'] = 'Template-based'

        if result["status"] == "success":
            # Update job with file paths
            zip_path = result["files"]["zip"]
            
            # Validate zip_path before using it
            if not zip_path or not isinstance(zip_path, str) or zip_path.strip() == '':
                raise ValueError(f"Invalid zip_path received: '{zip_path}'")
            
            # Resolve the absolute path - RAG API returns path relative to its directory
            # Convert to absolute path by checking multiple possible locations
            if not os.path.isabs(zip_path):
                # Try RAG API directory first (most common)
                rag_api_base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agentic-rag-IMigrate')
                absolute_zip_path = os.path.join(rag_api_base, zip_path)
                
                if not os.path.exists(absolute_zip_path):
                    # Try BoomiToIS-API directory as fallback
                    absolute_zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), zip_path)
                    
                    if not os.path.exists(absolute_zip_path):
                        # Try current working directory
                        absolute_zip_path = os.path.abspath(zip_path)
                        
                        if not os.path.exists(absolute_zip_path):
                            logger.error(f"❌ ZIP file not found in any expected location:")
                            logger.error(f"   1. RAG API dir: {os.path.join(rag_api_base, zip_path)}")
                            logger.error(f"   2. BoomiToIS dir: {os.path.join(os.path.dirname(os.path.abspath(__file__)), zip_path)}")
                            logger.error(f"   3. Current dir: {os.path.abspath(zip_path)}")
                            raise ValueError(f"Generated ZIP file not found: {zip_path}")
                
                zip_path = absolute_zip_path
            else:
                # Already absolute path, just verify it exists
                if not os.path.exists(zip_path):
                    logger.warning(f"⚠️ ZIP file not found at absolute path: {zip_path}")
                    raise ValueError(f"Generated ZIP file not found: {zip_path}")
            
            # Retry mechanism: Check for ZIP file existence with retries (handles file system delays, network drives, antivirus scanning)
            import time
            max_retries = 10
            retry_interval = 10  # seconds
            
            for attempt in range(1, max_retries + 1):
                if os.path.exists(zip_path):
                    logger.info(f"✅ Verified ZIP file exists (attempt {attempt}/{max_retries}): {zip_path}")
                    break
                else:
                    if attempt < max_retries:
                        logger.warning(f"⚠️ ZIP file not found yet (attempt {attempt}/{max_retries}), retrying in {retry_interval} seconds...")
                        logger.warning(f"   Path checked: {zip_path}")
                        time.sleep(retry_interval)
                    else:
                        # Final attempt failed
                        logger.error(f"❌ ZIP file not found after {max_retries} attempts ({max_retries * retry_interval} seconds)")
                        logger.error(f"   Path: {zip_path}")
                        raise ValueError(f"Generated ZIP file not found after {max_retries} retries: {zip_path}")
            relative_zip_path = os.path.relpath(zip_path, os.path.dirname(os.path.abspath(__file__)))

            # Add debug files if they exist
            debug_files = {}
            for debug_file, debug_path in result["files"]["debug"].items():
                relative_debug_path = os.path.relpath(debug_path, os.path.dirname(os.path.abspath(__file__)))
                debug_files[debug_file] = relative_debug_path

            # Only mark as completed after all verification is done
            jobs[job_id].update({
                'status': 'completed',
                'message': 'iFlow generation completed successfully!',
                'files': {
                    'zip': relative_zip_path,
                    'debug': debug_files
                },
                'iflow_name': iflow_name
            })
            save_jobs(jobs)  # Save job data to file
            logger.info(f"✅ Job {job_id} marked as completed and saved")
            
            # Update Main API with completion status
            try:
                main_job_id = jobs[job_id].get('original_job_id')
                
                # FALLBACK: If not in job record, try to retrieve from persistent mapping
                if not main_job_id:
                    logger.warning(f"⚠️ No original_job_id in job record, checking persistent mapping...")
                    job_mapping_file = os.path.join(app.config['RESULTS_FOLDER'], 'job_mappings.json')
                    try:
                        if os.path.exists(job_mapping_file):
                            with open(job_mapping_file, 'r') as f:
                                job_mappings = json.load(f)
                            main_job_id = job_mappings.get(job_id)
                            if main_job_id:
                                logger.info(f"✅ Retrieved main_job_id from persistent mapping: {main_job_id}")
                    except Exception as e:
                        logger.error(f"❌ Error reading job mappings: {e}")
                
                if main_job_id:
                    logger.info(f"📡 Updating Main API job {main_job_id} to 'completed' status")
                    
                    # Get Main API URL
                    MAIN_API_URL = os.getenv('MAIN_API_URL', 'http://localhost:5000')
                    MAIN_API_HOST = os.getenv('MAIN_API_HOST', 'localhost')
                    MAIN_API_PORT = os.getenv('MAIN_API_PORT', '5000')
                    MAIN_API_PROTOCOL = os.getenv('MAIN_API_PROTOCOL', 'http')
                    
                    if not MAIN_API_URL or MAIN_API_URL == 'http://localhost:5000':
                        MAIN_API_URL = f"{MAIN_API_PROTOCOL}://{MAIN_API_HOST}"
                        if MAIN_API_PORT and MAIN_API_PORT not in ['80', '443']:
                            MAIN_API_URL += f":{MAIN_API_PORT}"
                    
                    # Update Main API job status
                    import requests
                    update_response = requests.post(
                        f"{MAIN_API_URL}/api/jobs/{main_job_id}/update",
                        json={
                            'status': 'completed',
                            'processing_message': 'iFlow generation completed successfully!',
                            'iflow_package_path': zip_path,
                            'package_path': zip_path,
                            'iflow_name': iflow_name
                        },
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        logger.info(f"✅ Successfully updated Main API job {main_job_id}")
                    else:
                        logger.warning(f"⚠️ Main API update returned {update_response.status_code}: {update_response.text}")
                else:
                    logger.warning(f"⚠️ No original_job_id found for BoomiToIS job {job_id}, skipping Main API update")
                    
            except Exception as update_error:
                logger.error(f"❌ Error updating Main API: {str(update_error)}")
                # Don't fail the whole job if Main API update fails
        else:
            jobs[job_id].update({
                'status': 'failed',
                'message': result["message"]
            })
            save_jobs(jobs)  # Save job data to file
            
            # Update Main API with failure status
            try:
                main_job_id = jobs[job_id].get('original_job_id')
                
                # FALLBACK: Check persistent mapping
                if not main_job_id:
                    job_mapping_file = os.path.join(app.config['RESULTS_FOLDER'], 'job_mappings.json')
                    try:
                        if os.path.exists(job_mapping_file):
                            with open(job_mapping_file, 'r') as f:
                                job_mappings = json.load(f)
                            main_job_id = job_mappings.get(job_id)
                    except:
                        pass
                
                if main_job_id:
                    logger.info(f"📡 Updating Main API job {main_job_id} to 'failed' status")
                    
                    MAIN_API_URL = os.getenv('MAIN_API_URL', 'http://localhost:5000')
                    MAIN_API_HOST = os.getenv('MAIN_API_HOST', 'localhost')
                    MAIN_API_PORT = os.getenv('MAIN_API_PORT', '5000')
                    MAIN_API_PROTOCOL = os.getenv('MAIN_API_PROTOCOL', 'http')
                    
                    if not MAIN_API_URL or MAIN_API_URL == 'http://localhost:5000':
                        MAIN_API_URL = f"{MAIN_API_PROTOCOL}://{MAIN_API_HOST}"
                        if MAIN_API_PORT and MAIN_API_PORT not in ['80', '443']:
                            MAIN_API_URL += f":{MAIN_API_PORT}"
                    
                    import requests
                    requests.post(
                        f"{MAIN_API_URL}/api/jobs/{main_job_id}/update",
                        json={
                            'status': 'failed',
                            'processing_message': result["message"],
                            'error': result["message"]
                        },
                        timeout=10
                    )
            except Exception as update_error:
                logger.error(f"❌ Error updating Main API: {str(update_error)}")

    except Exception as e:
        logger.error(f"Error generating iFlow: {str(e)}")
        jobs[job_id].update({
            'status': 'failed',
            'message': f'Error generating iFlow: {str(e)}'
        })
        save_jobs(jobs)  # Save job data to file
        
        # Update Main API with exception status
        try:
            main_job_id = jobs[job_id].get('original_job_id')
            
            # FALLBACK: Check persistent mapping
            if not main_job_id:
                job_mapping_file = os.path.join(app.config['RESULTS_FOLDER'], 'job_mappings.json')
                try:
                    if os.path.exists(job_mapping_file):
                        with open(job_mapping_file, 'r') as f:
                            job_mappings = json.load(f)
                        main_job_id = job_mappings.get(job_id)
                except:
                    pass
            
            if main_job_id:
                logger.info(f"📡 Updating Main API job {main_job_id} to 'failed' status (exception)")
                
                MAIN_API_URL = os.getenv('MAIN_API_URL', 'http://localhost:5000')
                MAIN_API_HOST = os.getenv('MAIN_API_HOST', 'localhost')
                MAIN_API_PORT = os.getenv('MAIN_API_PORT', '5000')
                MAIN_API_PROTOCOL = os.getenv('MAIN_API_PROTOCOL', 'http')
                
                if not MAIN_API_URL or MAIN_API_URL == 'http://localhost:5000':
                    MAIN_API_URL = f"{MAIN_API_PROTOCOL}://{MAIN_API_HOST}"
                    if MAIN_API_PORT and MAIN_API_PORT not in ['80', '443']:
                        MAIN_API_URL += f":{MAIN_API_PORT}"
                
                import requests
                requests.post(
                    f"{MAIN_API_URL}/api/jobs/{main_job_id}/update",
                    json={
                        'status': 'failed',
                        'processing_message': f'Error generating iFlow: {str(e)}',
                        'error': str(e)
                    },
                    timeout=10
                )
        except Exception as update_error:
            logger.error(f"❌ Error updating Main API: {str(update_error)}")

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
        generator_api = IFlowGeneratorAPI(api_key=ANTHROPIC_API_KEY, use_converter=False)

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
            stored_path = job['files']['zip']
            
            # Extract just the filename from the stored path
            zip_filename = os.path.basename(stored_path)
            
            # ALWAYS look in agentic-rag-IMigrate/generated_packages/
            imigrate_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            zip_path = os.path.join(imigrate_root, 'agentic-rag-IMigrate', 'generated_packages', zip_filename)
            
            if os.path.exists(zip_path):
                logger.info(f"Found ZIP file at: {zip_path}")
            else:
                logger.warning(f"ZIP file not found at expected location: {zip_path}")
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

        # Deploy the iFlow using direct deployment (original working method)
        logger.info(f"Deploying iFlow using direct deployment: {zip_path}")
        logger.info(f"Using SAP BTP tenant: {SAP_BTP_TENANT_URL}")
        logger.info(f"Using OAuth URL: {SAP_BTP_OAUTH_URL}")
        logger.info(f"Using package: {package_id}")
        
        # Use the original working deployment method with new credentials
        deployment_result = deploy_iflow(
            iflow_path=zip_path,
            iflow_id=iflow_id,
            iflow_name=iflow_name,
            package_id=package_id,
            client_id=SAP_BTP_CLIENT_ID,
            client_secret=SAP_BTP_CLIENT_SECRET,
            token_url=SAP_BTP_OAUTH_URL,
            base_url=SAP_BTP_TENANT_URL
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))

    # Disable auto-reload to prevent interruptions during long-running AI analysis
    # The debug mode was causing restarts every time a ZIP file was generated
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
