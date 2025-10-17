"""
MuleSoft to SAP Integration Suite iFlow Generator API - Gemma3 Version

This Flask application provides an API for generating SAP Integration Suite iFlow packages
from MuleSoft documentation using Gemma3 LLM via RunPod. It includes token management
and response resumption strategies for handling large responses.
"""

import os
import time
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS
CORS(app, origins=[
    "http://localhost:5173",
    "https://ifa-frontend.cfapps.us10-001.hana.ondemand.com",
    "https://boomi-frontend.cfapps.us10-001.hana.ondemand.com"
], supports_credentials=True)

# Configuration
RUNPOD_API_KEY = os.getenv('RUNPOD_API_KEY')
RUNPOD_ENDPOINT_ID = os.getenv('RUNPOD_ENDPOINT_ID', 's5unaaduyy7otl')
RUNPOD_RUN_URL = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/run"
RUNPOD_STATUS_URL = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/status"

# Token limits and chunking configuration
MAX_INPUT_TOKENS = int(os.getenv('GEMMA3_MAX_INPUT_TOKENS', '8192'))
MAX_OUTPUT_TOKENS = int(os.getenv('GEMMA3_MAX_OUTPUT_TOKENS', '2048'))
CHUNK_OVERLAP = int(os.getenv('GEMMA3_CHUNK_OVERLAP', '200'))
MAX_WAIT_TIME = int(os.getenv('GEMMA3_MAX_WAIT_TIME', '300'))

# In-memory storage for jobs (in production, use Redis or database)
jobs = {}

class GemmaJobManager:
    """Manages Gemma3 job execution with token management and resumption"""
    
    def __init__(self):
        self.jobs = {}
    
    def create_job(self, job_id, markdown_content, iflow_name):
        """Create a new job for iFlow generation"""
        self.jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'created': datetime.now().isoformat(),
            'markdown_content': markdown_content,
            'iflow_name': iflow_name,
            'chunks': [],
            'current_chunk': 0,
            'partial_responses': [],
            'final_response': None,
            'error': None,
            'runpod_jobs': []
        }
        return self.jobs[job_id]
    
    def get_job(self, job_id):
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def update_job_status(self, job_id, status, **kwargs):
        """Update job status and other fields"""
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = status
            self.jobs[job_id]['last_updated'] = datetime.now().isoformat()
            for key, value in kwargs.items():
                self.jobs[job_id][key] = value

job_manager = GemmaJobManager()

def estimate_tokens(text):
    """Rough estimation of tokens (1 token ≈ 4 characters for English)"""
    return len(text) // 4

def chunk_text(text, max_tokens, overlap=200):
    """Split text into chunks that fit within token limits"""
    max_chars = max_tokens * 4  # Rough conversion
    overlap_chars = overlap * 4
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chars
        
        if end >= len(text):
            # Last chunk
            chunks.append(text[start:])
            break
        
        # Try to find a good breaking point (sentence or paragraph)
        break_point = end
        for i in range(end - 100, end):
            if i < len(text) and text[i] in '.!?\n':
                break_point = i + 1
                break
        
        chunks.append(text[start:break_point])
        start = break_point - overlap_chars
        
        if start < 0:
            start = 0
    
    return chunks

def call_runpod_api(prompt, max_wait_time=300):
    """Call RunPod API with Gemma3"""
    if not RUNPOD_API_KEY:
        raise Exception("RUNPOD_API_KEY not configured")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {RUNPOD_API_KEY}'
    }
    
    data = {
        "input": {
            "prompt": prompt,
            "max_tokens": MAX_OUTPUT_TOKENS,
            "temperature": 0.7
        }
    }
    
    try:
        # Submit job
        logger.info("Submitting job to RunPod...")
        response = requests.post(RUNPOD_RUN_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        job_data = response.json()
        job_id = job_data.get('id')
        
        if not job_id:
            raise Exception("No job ID received from RunPod")
        
        logger.info(f"Job submitted successfully. Job ID: {job_id}")
        
        # Poll for results
        start_time = time.time()
        check_interval = 10
        
        while time.time() - start_time < max_wait_time:
            status_response = requests.get(
                f"{RUNPOD_STATUS_URL}/{job_id}",
                headers=headers,
                timeout=30
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            
            job_status = status_data.get('status')
            elapsed_time = int(time.time() - start_time)
            
            logger.info(f"RunPod Status: {job_status} (Elapsed: {elapsed_time}s)")
            
            if job_status == 'COMPLETED':
                logger.info(f"RunPod job completed successfully: {job_id}")
                logger.debug(f"Full response: {status_data}")
                return status_data
            elif job_status == 'FAILED':
                logger.error(f"RunPod job failed: {status_data}")
                raise Exception(f"RunPod job failed: {status_data}")
            elif job_status in ['IN_PROGRESS', 'IN_QUEUE']:
                time.sleep(check_interval)
            else:
                logger.warning(f"Unknown RunPod status: {job_status}")
                time.sleep(check_interval)
        
        raise Exception(f"Timeout reached after {max_wait_time} seconds")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making RunPod API call: {e}")
        raise Exception(f"RunPod API error: {e}")

def extract_output(result_data):
    """Extract the actual output from the RunPod API response"""
    if not result_data:
        return None

    try:
        # Handle the nested RunPod response structure
        if 'output' in result_data:
            output = result_data['output']

            # Check if output is a list (as in the example)
            if isinstance(output, list) and len(output) > 0:
                first_output = output[0]

                # Check for choices structure
                if isinstance(first_output, dict) and 'choices' in first_output:
                    choices = first_output['choices']
                    if isinstance(choices, list) and len(choices) > 0:
                        choice = choices[0]

                        # Extract tokens if available
                        if isinstance(choice, dict) and 'tokens' in choice:
                            tokens = choice['tokens']
                            if isinstance(tokens, list) and len(tokens) > 0:
                                # Join all tokens into a single string
                                return ''.join(tokens)

                        # Fallback to text field if available
                        if isinstance(choice, dict) and 'text' in choice:
                            return choice['text']

                # Direct text in first output
                if isinstance(first_output, dict) and 'text' in first_output:
                    return first_output['text']

                # If first output is a string
                if isinstance(first_output, str):
                    return first_output

            # Handle direct output formats
            elif isinstance(output, dict):
                if 'text' in output:
                    return output['text']
                elif 'choices' in output:
                    choices = output['choices']
                    if isinstance(choices, list) and len(choices) > 0:
                        choice = choices[0]
                        if isinstance(choice, dict) and 'text' in choice:
                            return choice['text']

            elif isinstance(output, str):
                return output

        # Fallback to result field
        elif 'result' in result_data:
            return str(result_data['result'])

        # Last resort - convert entire response to string
        logger.warning(f"Unexpected response format: {result_data}")
        return str(result_data)

    except Exception as e:
        logger.error(f"Error extracting output from response: {e}")
        logger.error(f"Response data: {result_data}")
        return str(result_data)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MuleToIS-API-Gemma3',
        'timestamp': datetime.now().isoformat(),
        'runpod_configured': bool(RUNPOD_API_KEY),
        'max_input_tokens': MAX_INPUT_TOKENS,
        'max_output_tokens': MAX_OUTPUT_TOKENS
    })

@app.route('/api/test-extract', methods=['POST'])
def test_extract():
    """Test endpoint for response extraction"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Test the extract_output function with provided data
        extracted = extract_output(data)

        return jsonify({
            'original': data,
            'extracted': extracted,
            'extraction_successful': bool(extracted)
        })

    except Exception as e:
        logger.error(f"Error in test extract: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-iflow', methods=['POST'])
def generate_iflow():
    """Generate iFlow from markdown content using Gemma3"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        markdown_content = data.get('markdown')
        iflow_name = data.get('iflow_name', f'GeneratedIFlow_{int(time.time())}')
        
        if not markdown_content:
            return jsonify({'error': 'No markdown content provided'}), 400
        
        # Create job
        job_id = str(uuid.uuid4())
        job_manager.create_job(job_id, markdown_content, iflow_name)
        
        # Start processing in background (for now, process synchronously)
        try:
            process_iflow_generation(job_id)
        except Exception as e:
            logger.error(f"Error processing iFlow generation: {e}")
            job_manager.update_job_status(job_id, 'failed', error=str(e))
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'iFlow generation started'
        })
        
    except Exception as e:
        logger.error(f"Error in generate_iflow: {e}")
        return jsonify({'error': str(e)}), 500

def process_iflow_generation(job_id):
    """Process iFlow generation with chunking and resumption"""
    job = job_manager.get_job(job_id)
    if not job:
        raise Exception(f"Job {job_id} not found")
    
    try:
        job_manager.update_job_status(job_id, 'processing')
        
        markdown_content = job['markdown_content']
        iflow_name = job['iflow_name']
        
        # Estimate tokens and determine if chunking is needed
        estimated_tokens = estimate_tokens(markdown_content)
        logger.info(f"Estimated tokens for job {job_id}: {estimated_tokens}")
        
        if estimated_tokens > MAX_INPUT_TOKENS:
            # Need to chunk the input
            logger.info(f"Input too large, chunking into smaller pieces...")
            chunks = chunk_text(markdown_content, MAX_INPUT_TOKENS - 1000, CHUNK_OVERLAP)  # Reserve 1000 tokens for prompt
            job_manager.update_job_status(job_id, 'processing', chunks=chunks)
            
            # Process each chunk
            partial_responses = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)} for job {job_id}")
                
                prompt = create_chunked_prompt(chunk, i, len(chunks), iflow_name)
                response = call_runpod_api(prompt, MAX_WAIT_TIME)
                output = extract_output(response)
                
                if output:
                    partial_responses.append(output)
                    job_manager.update_job_status(
                        job_id, 'processing', 
                        current_chunk=i+1, 
                        partial_responses=partial_responses
                    )
            
            # Combine responses
            final_response = combine_chunked_responses(partial_responses, iflow_name)
            
        else:
            # Single request
            logger.info(f"Processing single request for job {job_id}")
            prompt = create_iflow_prompt(markdown_content, iflow_name)
            response = call_runpod_api(prompt, MAX_WAIT_TIME)
            final_response = extract_output(response)
        
        if final_response:
            job_manager.update_job_status(
                job_id, 'completed', 
                final_response=final_response
            )
            logger.info(f"Job {job_id} completed successfully")
        else:
            raise Exception("No response generated")
            
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        job_manager.update_job_status(job_id, 'failed', error=str(e))

def create_iflow_prompt(markdown_content, iflow_name):
    """Create prompt for iFlow generation"""
    return f"""You are an expert SAP Integration Suite developer. Generate a complete iFlow project structure based on the following MuleSoft documentation.

An iFlow project has the following folder structure:
- src/main/resources/scenarioflows/integrationflow/[iflow_name].iflw (Main iFlow XML file)
- src/main/resources/parameters.prop (Parameters properties file)
- src/main/resources/parameters.propdef (Parameters property definitions)
- src/main/resources/script/ (Directory for Groovy scripts)
- META-INF/MANIFEST.MF (Manifest file with bundle information)
- .project (Project file)
- metainfo.prop (Metadata properties)

Requirements:
1. Create a complete SAP Integration Suite iFlow project structure
2. Generate the main iFlow XML file ({iflow_name}.iflw)
3. Include all necessary components (sender, receiver, message mapping, etc.)
4. Follow SAP Integration Suite best practices
5. Include proper error handling and parameters
6. Provide all required project files

MuleSoft Documentation:
{markdown_content}

Generate the complete iFlow project with all files:"""

def create_chunked_prompt(chunk, chunk_index, total_chunks, iflow_name):
    """Create prompt for chunked processing"""
    if chunk_index == 0:
        return f"""You are an expert SAP Integration Suite developer. I will provide you with MuleSoft documentation in {total_chunks} parts. This is part {chunk_index + 1}/{total_chunks}.

An iFlow project has the following folder structure:
- src/main/resources/scenarioflows/integrationflow/{iflow_name}.iflw (Main iFlow XML file)
- src/main/resources/parameters.prop (Parameters properties file)
- src/main/resources/parameters.propdef (Parameters property definitions)
- src/main/resources/script/ (Directory for Groovy scripts)
- META-INF/MANIFEST.MF (Manifest file with bundle information)
- .project (Project file)
- metainfo.prop (Metadata properties)

For this first part, analyze the content and start generating the SAP Integration Suite iFlow project structure. Focus on the main flow structure and initial components.

iFlow name: {iflow_name}

Part {chunk_index + 1}/{total_chunks} of MuleSoft Documentation:
{chunk}

Generate the beginning of the iFlow project structure:"""

    elif chunk_index == total_chunks - 1:
        return f"""This is the final part {chunk_index + 1}/{total_chunks} of the MuleSoft documentation. Complete the SAP Integration Suite iFlow project definition.

Final part of MuleSoft Documentation:
{chunk}

Complete the iFlow project with all remaining files and proper structure:"""

    else:
        return f"""This is part {chunk_index + 1}/{total_chunks} of the MuleSoft documentation. Continue building the SAP Integration Suite iFlow project based on this content.

Part {chunk_index + 1}/{total_chunks} of MuleSoft Documentation:
{chunk}

Continue the iFlow project definition:"""

def combine_chunked_responses(partial_responses, iflow_name):
    """Combine multiple partial responses into a complete iFlow"""
    if not partial_responses:
        return None
    
    if len(partial_responses) == 1:
        return partial_responses[0]
    
    # Simple combination strategy - in production, you might want more sophisticated merging
    combined = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated iFlow: {iflow_name} -->
<!-- Combined from {len(partial_responses)} parts -->

"""
    
    for i, response in enumerate(partial_responses):
        combined += f"\n<!-- Part {i+1} -->\n"
        # Remove XML declarations from subsequent parts
        if i > 0 and response.startswith('<?xml'):
            lines = response.split('\n')
            response = '\n'.join(lines[1:])
        combined += response + "\n"
    
    return combined

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    job = job_manager.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    response_data = {
        'id': job['id'],
        'status': job['status'],
        'created': job['created'],
        'last_updated': job.get('last_updated'),
        'message': f"Job is {job['status']}"
    }
    
    if job['status'] == 'processing' and job.get('chunks'):
        response_data['progress'] = {
            'current_chunk': job.get('current_chunk', 0),
            'total_chunks': len(job['chunks']),
            'percentage': int((job.get('current_chunk', 0) / len(job['chunks'])) * 100)
        }
    
    if job['status'] == 'failed':
        response_data['error'] = job.get('error')
    
    return jsonify(response_data)

@app.route('/api/jobs/<job_id>/download', methods=['GET'])
def download_iflow(job_id):
    """Download generated iFlow"""
    job = job_manager.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    if not job.get('final_response'):
        return jsonify({'error': 'No iFlow generated'}), 404
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(job['final_response'])
            temp_path = f.name
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"{job['iflow_name']}.xml",
            mimetype='application/xml'
        )
        
    except Exception as e:
        logger.error(f"Error downloading iFlow: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting MuleToIS-API-Gemma3 on {host}:{port}")
    logger.info(f"RunPod configured: {bool(RUNPOD_API_KEY)}")
    
    app.run(host=host, port=port, debug=debug)
