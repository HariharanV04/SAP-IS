"""
API wrapper for the MuleToIFlow GenAI approach.
This module provides functions to generate iFlow from markdown content.
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
import shutil
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the generator
import_successful = False
try:
    # Try to import from the current directory first
    from enhanced_genai_iflow_generator import EnhancedGenAIIFlowGenerator
    logger.info("Successfully imported EnhancedGenAIIFlowGenerator from local directory")
    import_successful = True
except ImportError as e:
    logger.warning(f"Could not import from local directory: {str(e)}")

# Only try fallback import if the first import failed
if not import_successful:
    try:
        # Add MuleToIFlow GenAI Approach directory to path
        MULE_TO_IFLOW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MuleToIflowGenAI Approach")
        sys.path.append(MULE_TO_IFLOW_DIR)

        # Import the module
        from enhanced_genai_iflow_generator import EnhancedGenAIIFlowGenerator
        logger.info("Successfully imported EnhancedGenAIIFlowGenerator from MuleToIflowGenAI Approach directory")
    except ImportError as e:
        logger.error(f"Error importing EnhancedGenAIIFlowGenerator: {str(e)}")
        raise ImportError(f"Could not import EnhancedGenAIIFlowGenerator: {str(e)}")

class IFlowGeneratorAPI:
    """API wrapper for the MuleToIFlow GenAI approach"""

    def __init__(self, api_key=None, model="claude-sonnet-4-20250514", provider="claude"):
        """
        Initialize the iFlow generator API

        Args:
            api_key (str): API key for the LLM service (optional)
            model (str): Model to use for the LLM service
            provider (str): AI provider to use ('openai', 'claude', or 'local')
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider

        # Initialize the generator
        self.generator = EnhancedGenAIIFlowGenerator(
            api_key=self.api_key,
            model=self.model,
            provider=self.provider
        )

        logger.info(f"Initialized IFlowGeneratorAPI with {provider} provider and {model} model")

    def generate_from_markdown(self, markdown_content, output_dir=None, iflow_name=None, job_id=None):
        """
        Generate an iFlow from markdown content

        Args:
            markdown_content (str): The markdown content to analyze
            output_dir (str, optional): Directory to save the generated iFlow. If None, uses a temporary directory.
            iflow_name (str, optional): Name of the iFlow. If None, generates a name based on UUID.
            job_id (str, optional): Job ID for progress tracking

        Returns:
            dict: Dictionary with paths to generated files and other information
        """
        try:
            # Create a temporary directory if output_dir is not provided
            temp_dir = None
            if output_dir is None:
                temp_dir = tempfile.mkdtemp(prefix="iflow_gen_")
                output_dir = temp_dir
                logger.info(f"Created temporary directory for output: {output_dir}")
            else:
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Using provided output directory: {output_dir}")

            # Generate a name if not provided
            if iflow_name is None:
                iflow_name = f"GeneratedIFlow_{uuid.uuid4().hex[:8]}"
                logger.info(f"Generated iFlow name: {iflow_name}")

            # Generate the iFlow
            logger.info(f"Generating iFlow '{iflow_name}' using {self.provider} provider")
            zip_path = self.generator.generate_iflow(markdown_content, output_dir, iflow_name, job_id)

            # Get debug files if they exist
            debug_files = {}
            debug_dir = os.path.join(os.getcwd(), "genai_debug")
            if os.path.exists(debug_dir):
                for file in os.listdir(debug_dir):
                    if file.startswith(f"final_iflow_{iflow_name}") or file.startswith("raw_analysis_response"):
                        debug_files[file] = os.path.join(debug_dir, file)

            # Return the result
            result = {
                "status": "success",
                "message": f"Generated iFlow: {zip_path}",
                "files": {
                    "zip": zip_path,
                    "debug": debug_files
                },
                "iflow_name": iflow_name,
                "temp_dir": temp_dir  # Include the temp_dir so it can be cleaned up later if needed
            }

            logger.info(f"Successfully generated iFlow: {zip_path}")
            return result

        except Exception as e:
            logger.error(f"Error generating iFlow: {str(e)}")
            return {
                "status": "error",
                "message": f"Error generating iFlow: {str(e)}",
                "temp_dir": temp_dir  # Include the temp_dir so it can be cleaned up if needed
            }

    def cleanup(self, temp_dir):
        """
        Clean up temporary directories

        Args:
            temp_dir (str): Path to the temporary directory to clean up
        """
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
                return True
            except Exception as e:
                logger.error(f"Error cleaning up temporary directory: {str(e)}")
                return False
        return False

    def fix_iflow_file(self, iflow_path, create_backup=True):
        """
        Fix an existing iFlow file to ensure compatibility with SAP Integration Suite

        Args:
            iflow_path (str): Path to the iFlow file to fix
            create_backup (bool): Whether to create a backup of the original file

        Returns:
            dict: Dictionary with status and message
        """
        try:
            # Import the iflow_fixer module
            try:
                from iflow_fixer import fix_iflow_file
            except ImportError:
                logger.error("Could not import iflow_fixer module")
                return {
                    "status": "error",
                    "message": "Could not import iflow_fixer module"
                }

            # Check if the file exists
            if not os.path.exists(iflow_path):
                logger.error(f"iFlow file not found: {iflow_path}")
                return {
                    "status": "error",
                    "message": f"iFlow file not found: {iflow_path}"
                }

            # Fix the iFlow file
            logger.info(f"Fixing iFlow file: {iflow_path}")
            success, message = fix_iflow_file(iflow_path, create_backup)

            if success:
                logger.info(f"Successfully fixed iFlow file: {iflow_path}")
                return {
                    "status": "success",
                    "message": message,
                    "file_path": iflow_path
                }
            else:
                logger.warning(f"Could not fix iFlow file: {message}")
                return {
                    "status": "warning",
                    "message": message,
                    "file_path": iflow_path
                }

        except Exception as e:
            logger.error(f"Error fixing iFlow file: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fixing iFlow file: {str(e)}"
            }

# Function to generate iFlow from markdown content
def generate_iflow_from_markdown(markdown_content, api_key, output_dir=None, iflow_name=None, model="claude-sonnet-4-20250514", provider="claude", job_id=None):
    """
    Generate an iFlow from markdown content

    Args:
        markdown_content (str): The markdown content to analyze
        api_key (str): API key for the LLM service
        output_dir (str, optional): Directory to save the generated iFlow. If None, uses a temporary directory.
        iflow_name (str, optional): Name of the iFlow. If None, generates a name based on UUID.
        model (str, optional): Model to use for the LLM service
        provider (str, optional): AI provider to use ('openai', 'claude', or 'local')
        job_id (str, optional): Job ID for progress tracking

    Returns:
        dict: Dictionary with paths to generated files and other information
    """
    generator_api = IFlowGeneratorAPI(api_key=api_key, model=model, provider=provider, use_converter=True)
    return generator_api.generate_from_markdown(markdown_content, output_dir, iflow_name, job_id)

# Test function
def test_generate_iflow():
    """Test the iFlow generator API"""
    import os
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    # Get the Claude API key from the .env file
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        logger.error("No Claude API key found in .env file")
        return

    # Test markdown content
    markdown_content = """
    # Simple Product API

    ## Overview
    This API provides access to product information.

    ## Base URL
    `https://example.com/api`

    ## Endpoints

    ### Get Products
    Retrieves a list of all products.

    **Method**: GET
    **Path**: `/products`
    **Response**: JSON array of product objects

    **Process Flow**:
    1. Prepare request headers
    2. Log the request
    3. Call OData Products service
    4. Set response headers
    5. Transform response to required format
    """

    # Generate the iFlow
    result = generate_iflow_from_markdown(
        markdown_content=markdown_content,
        api_key=api_key,
        output_dir="test_output",
        iflow_name="TestProductAPI"
    )

    # Print the result
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if result["status"] == "success":
        print(f"ZIP file: {result['files']['zip']}")
        for debug_file, debug_path in result['files']['debug'].items():
            print(f"Debug file: {debug_file} - {debug_path}")

if __name__ == "__main__":
    test_generate_iflow()
