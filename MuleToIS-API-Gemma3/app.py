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
import threading
import zipfile
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
RUNPOD_ENDPOINT_ID = os.getenv('RUNPOD_ENDPOINT_ID', 'yap1wc04ci8b5d')
# Use OpenAI-compatible endpoint (same as working test script)
RUNPOD_BASE_URL = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/openai/v1"
RUNPOD_CHAT_URL = f"{RUNPOD_BASE_URL}/chat/completions"

# Token limits and chunking configuration for Gemma 3n E4B IT
MAX_INPUT_TOKENS = int(os.getenv('GEMMA3_MAX_INPUT_TOKENS', '24576'))  # 24K for input (leaving 8K for output)
MAX_OUTPUT_TOKENS = int(os.getenv('GEMMA3_MAX_OUTPUT_TOKENS', '16384'))  # 16K for complete iFlows
CHUNK_OVERLAP = int(os.getenv('GEMMA3_CHUNK_OVERLAP', '500'))  # Larger overlap for better context
MAX_WAIT_TIME = int(os.getenv('GEMMA3_MAX_WAIT_TIME', '1200'))  # 20 minutes for cold starts
TEMPERATURE = float(os.getenv('GEMMA3_TEMPERATURE', '0.3'))  # Lower for more deterministic output
TOP_P = float(os.getenv('GEMMA3_TOP_P', '0.9'))  # Nucleus sampling

# In-memory storage for jobs (in production, use Redis or database)
jobs = {}

class GemmaJobManager:
    """Manages Gemma3 job execution with token management and resumption"""
    
    def __init__(self):
        self.jobs = {}
    
    def create_job(self, job_id, markdown_content, iflow_name, platform='mulesoft'):
        """Create a new job for iFlow generation"""
        self.jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'created': datetime.now().isoformat(),
            'markdown_content': markdown_content,
            'iflow_name': iflow_name,
            'platform': platform,
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
        """Update job status and other fields with protection against regression"""
        if job_id in self.jobs:
            current_status = self.jobs[job_id].get('status')

            # PREVENT STATUS REGRESSION: Don't update to processing if already completed
            if current_status == 'completed' and status in ['processing', 'queued', 'generating_iflow']:
                print(f"🚫 Gemma3-API: PREVENTING STATUS REGRESSION for job {job_id[:8]}")
                print(f"🚫 Current: {current_status}, Attempted: {status} - BLOCKED")
                return  # Don't update the status

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

def call_runpod_api(prompt, max_wait_time=1200):
    """Call RunPod API with Gemma3 using OpenAI-compatible format"""
    if not RUNPOD_API_KEY:
        raise Exception("RUNPOD_API_KEY not configured")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {RUNPOD_API_KEY}'
    }

    # Use OpenAI-compatible format (same as working test script)
    data = {
        "model": "google/gemma-3-4b-it",  # Use the working model name
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "stream": False
    }

    logger.info(f"RunPod API call - Prompt length: {len(prompt)} chars, Max wait: {max_wait_time}s")
    logger.info(f"RunPod API parameters: max_tokens={MAX_OUTPUT_TOKENS}, temperature={TEMPERATURE}, top_p={TOP_P}")
    logger.info(f"Token limits: MAX_INPUT_TOKENS={MAX_INPUT_TOKENS}, MAX_OUTPUT_TOKENS={MAX_OUTPUT_TOKENS}")
    logger.info(f"Using OpenAI-compatible endpoint: {RUNPOD_CHAT_URL}")

    try:
        # Call OpenAI-compatible endpoint (same as working test)
        logger.info("Calling RunPod OpenAI-compatible endpoint...")
        response = requests.post(RUNPOD_CHAT_URL, headers=headers, json=data, timeout=max_wait_time)
        response.raise_for_status()

        # OpenAI-compatible format response (same as working test script)
        response_data = response.json()
        logger.info(f"RunPod OpenAI response received successfully")
        logger.info(f"Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")

        # Extract content from OpenAI format
        if isinstance(response_data, dict) and 'choices' in response_data:
            choices = response_data['choices']
            if isinstance(choices, list) and len(choices) > 0:
                choice = choices[0]
                if isinstance(choice, dict) and 'message' in choice:
                    message = choice['message']
                    if isinstance(message, dict) and 'content' in message:
                        content = message['content']
                        if content:
                            logger.info(f"Response content length: {len(content)} characters")
                            # Return in format expected by extract_output function
                            return {
                                'choices': [{'message': {'content': content}}],
                                'usage': response_data.get('usage', {})
                            }
                        else:
                            logger.warning("Empty content in response")
                    else:
                        logger.warning("No content in message")
                else:
                    logger.warning("No message in choice")
            else:
                logger.warning("No choices in response")
        else:
            logger.warning(f"Unexpected response format: {response_data}")

        return response_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making RunPod API call: {e}")
        raise Exception(f"RunPod API error: {e}")

def extract_output(result_data):
    """Extract the actual output from the RunPod API response (OpenAI format)"""
    if not result_data:
        return None

    try:
        # Handle OpenAI-compatible format (same as working test script)
        if 'choices' in result_data:
            choices = result_data['choices']
            if isinstance(choices, list) and len(choices) > 0:
                choice = choices[0]
                if isinstance(choice, dict) and 'message' in choice:
                    message = choice['message']
                    if isinstance(message, dict) and 'content' in message:
                        content = message['content']
                        logger.info(f"Successfully extracted content: {len(content)} characters")
                        return content
                # Fallback to text field
                elif isinstance(choice, dict) and 'text' in choice:
                    return choice['text']

        # Handle legacy RunPod format (for backward compatibility)
        elif 'output' in result_data:
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
@app.route('/api/health', methods=['GET'])
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

@app.route('/api/debug/jobs', methods=['GET'])
def debug_jobs():
    """Debug endpoint to see all jobs"""
    try:
        all_jobs = {}
        for job_id, job_data in job_manager.jobs.items():
            all_jobs[job_id] = {
                'id': job_data['id'],
                'status': job_data['status'],
                'created': job_data['created'],
                'iflow_name': job_data['iflow_name'],
                'has_final_response': bool(job_data.get('final_response')),
                'final_response_length': len(job_data.get('final_response', '')) if job_data.get('final_response') else 0,
                'error': job_data.get('error')
            }

        return jsonify({
            'total_jobs': len(all_jobs),
            'jobs': all_jobs
        })

    except Exception as e:
        logger.error(f"Error in debug jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-iflow/<job_id>', methods=['POST', 'OPTIONS'])
@app.route('/api/generate-iflow', methods=['POST', 'OPTIONS'])
def generate_iflow(job_id=None):
    """Generate iFlow from markdown content using Gemma3"""

    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 200

    try:
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

                # Generate a job ID for the iFlow generation
                iflow_job_id = str(uuid.uuid4())
                iflow_name = f"IFlow_{job_id[:8]}"

                # Create job
                job_manager.create_job(iflow_job_id, markdown_content, iflow_name)

                # Start processing in background thread
                thread = threading.Thread(
                    target=process_iflow_generation,
                    args=(iflow_job_id,)
                )
                thread.daemon = True
                thread.start()
                logger.info(f"Started background processing for job {iflow_job_id}")

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
                logger.error(f"Error fetching markdown for job {job_id}: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'Error fetching markdown for job {job_id}: {str(e)}'
                }), 500

        # If no job_id, get markdown from request body
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        markdown_content = data.get('markdown')
        iflow_name = data.get('iflow_name', f'GeneratedIFlow_{int(time.time())}')
        platform = data.get('platform', 'mulesoft')  # Default to mulesoft

        # Use job ID from Main API if provided, otherwise generate new one
        job_id = data.get('job_id', str(uuid.uuid4()))

        print(f"DEBUG: Gemma-3 API received job_id: {job_id}")

        if not markdown_content:
            return jsonify({'error': 'No markdown content provided'}), 400
        job_manager.create_job(job_id, markdown_content, iflow_name, platform)
        
        # Start processing in background thread
        thread = threading.Thread(
            target=process_iflow_generation,
            args=(job_id,)
        )
        thread.daemon = True
        thread.start()
        logger.info(f"Started background processing for job {job_id}")
        
        response = jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'iFlow generation started'
        })
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 202

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
        platform = job.get('platform', 'mulesoft')

        # Estimate tokens and determine if chunking is needed
        estimated_tokens = estimate_tokens(markdown_content)
        logger.info(f"Estimated tokens for job {job_id}: {estimated_tokens}")

        if estimated_tokens > MAX_INPUT_TOKENS:
            # Need to chunk the input
            logger.info(f"Input too large, chunking into smaller pieces...")
            chunks = chunk_text(markdown_content, MAX_INPUT_TOKENS - 1000, CHUNK_OVERLAP)
            job_manager.update_job_status(job_id, 'processing', chunks=chunks)

            # Process each chunk
            partial_responses = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)} for job {job_id}")

                prompt = create_chunked_prompt(chunk, i, len(chunks), iflow_name, platform)
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
            prompt = create_iflow_prompt(markdown_content, iflow_name, platform)
            logger.info(f"Prompt length: {len(prompt)} characters")

            response = call_runpod_api(prompt, MAX_WAIT_TIME)
            logger.info(f"RunPod response received: {type(response)}")

            # DETAILED DEBUG: Log the complete raw response structure
            logger.info(f"RAW RunPod Response Keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict) and 'output' in response:
                output = response['output']
                logger.info(f"Output type: {type(output)}")
                if isinstance(output, list) and len(output) > 0:
                    logger.info(f"Output[0] type: {type(output[0])}")
                    logger.info(f"Output[0] keys: {list(output[0].keys()) if isinstance(output[0], dict) else 'Not a dict'}")
                    if isinstance(output[0], dict):
                        # Log the actual content length before extraction
                        for key, value in output[0].items():
                            if isinstance(value, str):
                                logger.info(f"Output[0]['{key}'] length: {len(value)} chars")
                            elif isinstance(value, list):
                                logger.info(f"Output[0]['{key}'] is list with {len(value)} items")

            logger.debug(f"Full RunPod response: {response}")

            final_response = extract_output(response)
            logger.info(f"Extracted response length: {len(final_response) if final_response else 0} characters")

            # Debug: Show first 500 chars of response to check for truncation
            if final_response:
                logger.info(f"Response preview (first 500 chars): {final_response[:500]}...")
                if len(final_response) < 1000:
                    logger.warning(f"Response seems too short for a complete iFlow! Full response: {final_response}")
            else:
                logger.error("No final response extracted from RunPod!")

        if final_response:
            job_manager.update_job_status(
                job_id, 'completed',
                final_response=final_response
            )
            logger.info(f"Job {job_id} completed successfully with response length: {len(final_response)}")
        else:
            logger.error(f"No response generated for job {job_id}")
            logger.error(f"RunPod response was: {response}")
            raise Exception("No response generated from RunPod")

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        job_manager.update_job_status(job_id, 'failed', error=str(e))

def create_iflow_prompt(markdown_content, iflow_name, platform='mulesoft'):
    """Create prompt for iFlow generation with structured output optimized for Gemma 3n"""
    platform_text = "MuleSoft" if platform == 'mulesoft' else "Dell Boomi"

    # Use Gemma 3n chat template format for better instruction following
    return f"""<start_of_turn>user
You are an expert SAP Integration Suite developer with deep knowledge of BPMN2 XML structure and SAP Cloud Integration patterns.

Task: Generate a complete SAP Integration Suite iFlow project structure based on the following {platform_text} documentation.

Requirements:
1. Create a fully functional iFlow with proper BPMN2 XML structure
2. Include all necessary adapters, message mappings, and sequence flows
3. Generate complete project files including MANIFEST.MF, .project, and metainfo.prop
4. Ensure proper error handling and logging components
5. Use appropriate SAP Integration Suite components and patterns

{platform_text} Documentation:
{markdown_content}

Generate a complete iFlow project for: {iflow_name}
<end_of_turn>
<start_of_turn>model

IMPORTANT: Structure your response EXACTLY as shown below with clear file separators:

=== FILE: src/main/resources/scenarioflows/integrationflow/{iflow_name}.iflw ===
[Generate the main iFlow XML content here - complete BPMN2 XML with collaboration, participants, message flows, and process definitions]

=== FILE: META-INF/MANIFEST.MF ===
[Generate the manifest file content here]

=== FILE: .project ===
[Generate the Eclipse project file content here]

=== FILE: metainfo.prop ===
[Generate the metadata properties file content here]

=== FILE: src/main/resources/parameters.prop ===
[Generate the parameters properties file content here]

=== FILE: src/main/resources/parameters.propdef ===
[Generate the parameter definitions file content here]

=== END FILES ===

Requirements for the main iFlow XML:
1. Complete BPMN2 XML structure with proper namespaces
2. Collaboration section with participants and message flows
3. Process section with start event, components, and end event
4. HTTP sender adapter configuration
5. Message mapping and transformation components
6. Error handling components
7. Proper sequence flows connecting all components

Requirements for other files:
1. MANIFEST.MF: Standard OSGi bundle manifest
2. .project: Eclipse project configuration
3. metainfo.prop: iFlow metadata and description
4. parameters.prop: Runtime parameters
5. parameters.propdef: Parameter type definitions

{platform_text} Documentation:
{markdown_content}

Generate the complete structured response with all files:"""

def create_chunked_prompt(chunk, chunk_index, total_chunks, iflow_name, platform='mulesoft'):
    """Create prompt for chunked processing with structured output optimized for Gemma 3n"""
    platform_text = "MuleSoft" if platform == 'mulesoft' else "Dell Boomi"
    if chunk_index == 0:
        return f"""<start_of_turn>user
You are an expert SAP Integration Suite developer. I will provide you with {platform_text} documentation in {total_chunks} parts. This is part {chunk_index + 1}/{total_chunks}.

For this first part, start generating the SAP Integration Suite iFlow project structure. Focus on the main flow structure and initial components.

IMPORTANT: Structure your response EXACTLY as shown below with clear file separators:

=== FILE: src/main/resources/scenarioflows/integrationflow/{iflow_name}.iflw ===
[Start generating the main iFlow XML content here - begin with XML declaration and root elements]

=== FILE: META-INF/MANIFEST.MF ===
[Generate the manifest file content here]

=== PARTIAL RESPONSE ===
[This is part {chunk_index + 1} of {total_chunks}]

iFlow name: {iflow_name}

Part {chunk_index + 1}/{total_chunks} of MuleSoft Documentation:
{chunk}

Generate the beginning of the structured iFlow project:"""

    elif chunk_index == total_chunks - 1:
        return f"""This is the final part {chunk_index + 1}/{total_chunks} of the MuleSoft documentation. Complete the SAP Integration Suite iFlow project definition.

IMPORTANT: Complete all remaining files with proper structure:

=== CONTINUE FILE: src/main/resources/scenarioflows/integrationflow/{iflow_name}.iflw ===
[Complete the main iFlow XML content here]

=== FILE: .project ===
[Generate the Eclipse project file content here]

=== FILE: metainfo.prop ===
[Generate the metadata properties file content here]

=== FILE: src/main/resources/parameters.prop ===
[Generate the parameters properties file content here]

=== FILE: src/main/resources/parameters.propdef ===
[Generate the parameter definitions file content here]

=== END FILES ===

Final part of MuleSoft Documentation:
{chunk}

Complete the iFlow project with all remaining files:"""

    else:
        return f"""This is part {chunk_index + 1}/{total_chunks} of the MuleSoft documentation. Continue building the SAP Integration Suite iFlow project based on this content.

=== CONTINUE FILE: src/main/resources/scenarioflows/integrationflow/{iflow_name}.iflw ===
[Continue the main iFlow XML content here]

=== PARTIAL RESPONSE ===
[This is part {chunk_index + 1} of {total_chunks}]

Part {chunk_index + 1}/{total_chunks} of MuleSoft Documentation:
{chunk}

Continue the iFlow project definition:"""

def parse_structured_response(response_text):
    """Parse structured response into multiple files"""
    files = {}

    if not response_text:
        return files

    # Split by file markers
    file_sections = response_text.split('=== FILE: ')

    for section in file_sections[1:]:  # Skip the first empty section
        if '===' not in section:
            continue

        # Extract file path and content
        lines = section.split('\n')
        if not lines:
            continue

        # First line contains the file path and closing ===
        header_line = lines[0]
        file_path = header_line.split(' ===')[0].strip()

        # Find the content (everything until next file marker or end)
        content_lines = []
        for line in lines[1:]:
            if line.strip().startswith('=== FILE:') or line.strip() == '=== END FILES ===':
                break
            content_lines.append(line)

        # Join content and clean up
        content = '\n'.join(content_lines).strip()

        if file_path and content:
            files[file_path] = content
            logger.info(f"Parsed file: {file_path} ({len(content)} characters)")

    return files

def combine_chunked_responses(partial_responses, iflow_name):
    """Combine multiple partial responses into a complete iFlow"""
    if not partial_responses:
        return None

    if len(partial_responses) == 1:
        return partial_responses[0]

    # For chunked responses, combine them and then parse
    combined = f"""# Generated iFlow Project: {iflow_name}
# Combined from {len(partial_responses)} parts

"""

    for i, response in enumerate(partial_responses):
        combined += f"\n## Part {i+1}\n"
        combined += response + "\n"

    return combined

@app.route('/api/jobs/<job_id>', methods=['GET', 'OPTIONS'])
def get_job_status(job_id):
    """Get job status"""

    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response, 200

    job = job_manager.get_job(job_id)
    if not job:
        response = jsonify({'error': 'Job not found'})
        response.headers.set('Access-Control-Allow-Origin', '*')
        return response, 404

    response_data = {
        'id': job['id'],
        'status': job['status'],
        'created': job['created'],
        'last_updated': job.get('last_updated'),
        'message': f"Job is {job['status']}",
        'iflow_name': job.get('iflow_name', 'GeneratedIFlow')
    }

    if job['status'] == 'processing' and job.get('chunks'):
        response_data['progress'] = {
            'current_chunk': job.get('current_chunk', 0),
            'total_chunks': len(job['chunks']),
            'percentage': int((job.get('current_chunk', 0) / len(job['chunks'])) * 100)
        }

    if job['status'] == 'failed':
        response_data['error'] = job.get('error')

    response = jsonify(response_data)
    response.headers.set('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/jobs/<job_id>/download', methods=['GET'])
def download_iflow(job_id):
    """Download generated iFlow"""
    logger.info(f"Download request for job: {job_id}")

    job = job_manager.get_job(job_id)
    if not job:
        logger.error(f"Job not found: {job_id}")
        return jsonify({'error': 'Job not found'}), 404

    logger.info(f"Job status: {job['status']}")

    if job['status'] != 'completed':
        logger.error(f"Job not completed. Status: {job['status']}")
        return jsonify({
            'error': 'Job not completed',
            'status': job['status'],
            'message': job.get('error', 'Job still processing')
        }), 400

    if not job.get('final_response'):
        logger.error(f"No final response in job: {job_id}")
        logger.error(f"Job data: {job}")
        return jsonify({'error': 'No iFlow generated'}), 404

    try:
        logger.info(f"Creating iFlow ZIP package for job: {job_id}")
        logger.info(f"Response length: {len(job['final_response'])} characters")

        # Log first 100 characters to debug content
        logger.debug(f"Response preview: {job['final_response'][:100]}...")

        # Create temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        temp_zip.close()

        try:
            # Parse the structured response into multiple files
            parsed_files = parse_structured_response(job['final_response'])

            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                if parsed_files:
                    # Use parsed files from Gemma3 response
                    logger.info(f"Using parsed files from Gemma3 response: {list(parsed_files.keys())}")

                    for file_path, content in parsed_files.items():
                        zip_file.writestr(file_path, content, compress_type=zipfile.ZIP_DEFLATED)
                        logger.info(f"Added parsed file: {file_path} ({len(content)} chars)")

                    # Ensure we have the script directory
                    if not any(path.startswith("src/main/resources/script/") for path in parsed_files.keys()):
                        zip_file.writestr("src/main/resources/script/.gitkeep", "")

                else:
                    # Fallback: treat the entire response as the main iFlow XML
                    logger.warning("No structured files found, using fallback approach")

                    # Create the main iFlow XML file
                    iflow_xml_path = f"src/main/resources/scenarioflows/integrationflow/{job['iflow_name']}.iflw"
                    zip_file.writestr(iflow_xml_path, job['final_response'], compress_type=zipfile.ZIP_DEFLATED)

                    # Create basic project structure files
                    # META-INF/MANIFEST.MF
                    manifest_content = f"""Manifest-Version: 1.0
Created-By: SAP Integration Suite (Gemma3)
Bundle-Name: {job['iflow_name']}
Bundle-SymbolicName: com.sap.{job['iflow_name'].lower()}
Bundle-Version: 1.0.0
"""
                    zip_file.writestr("META-INF/MANIFEST.MF", manifest_content)

                    # .project file
                    project_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>{job['iflow_name']}</name>
    <comment>Generated iFlow project</comment>
    <projects></projects>
    <buildSpec>
        <buildCommand>
            <name>org.eclipse.jdt.core.javabuilder</name>
            <arguments></arguments>
        </buildCommand>
    </buildSpec>
    <natures>
        <nature>org.eclipse.jdt.core.javanature</nature>
    </natures>
</projectDescription>"""
                    zip_file.writestr(".project", project_content)

                    # metainfo.prop
                    metainfo_content = """adapter.type=scenario
adapter.version=1.0
"""
                    zip_file.writestr("metainfo.prop", metainfo_content)

                    # parameters.prop (empty for now)
                    zip_file.writestr("src/main/resources/parameters.prop", "# iFlow parameters\n")

                    # parameters.propdef (empty for now)
                    zip_file.writestr("src/main/resources/parameters.propdef", "# Parameter definitions\n")

                    # Create empty script directory
                    zip_file.writestr("src/main/resources/script/.gitkeep", "")

            logger.info(f"ZIP file created successfully: {temp_zip.name}")

        except Exception as zip_error:
            logger.error(f"Error creating ZIP file: {zip_error}")
            # Fallback to XML file if ZIP creation fails
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
                f.write(job['final_response'])
                temp_path = f.name
            logger.info(f"Fallback: Created XML file instead: {temp_path}")
            return send_file(
                temp_path,
                as_attachment=True,
                download_name=f"{job['iflow_name']}.xml",
                mimetype='application/xml'
            )

        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name=f"{job['iflow_name']}.zip",
            mimetype='application/zip'
        )

    except Exception as e:
        logger.error(f"Error downloading iFlow for job {job_id}: {e}")
        logger.error(f"Job data keys: {list(job.keys()) if job else 'None'}")
        logger.error(f"Final response type: {type(job.get('final_response', 'None'))}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting MuleToIS-API-Gemma3 on {host}:{port}")
    logger.info(f"RunPod configured: {bool(RUNPOD_API_KEY)}")

    app.run(host=host, port=port, debug=debug, use_reloader=False)
