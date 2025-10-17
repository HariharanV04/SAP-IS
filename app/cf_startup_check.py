"""
Cloud Foundry startup check script.
This script is run when the application starts in Cloud Foundry to verify that all required modules can be imported.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_imports():
    """Check that all required modules can be imported"""
    logger.info("Starting import checks...")
    
    # Check working directory and Python path
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    # List files in current directory
    try:
        files = os.listdir(".")
        logger.info(f"Files in current directory: {files}")
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
    
    # Check if iflow_matcher.py exists
    if "iflow_matcher.py" in files:
        logger.info("iflow_matcher.py found in current directory")
    else:
        logger.error("iflow_matcher.py NOT found in current directory")
    
    # Try to import iflow_matcher
    try:
        logger.info("Trying to import iflow_matcher...")
        import iflow_matcher
        logger.info("Successfully imported iflow_matcher module")
        logger.info(f"Module file: {iflow_matcher.__file__}")
        
        # Try to import process_markdown_for_iflow
        try:
            logger.info("Trying to import process_markdown_for_iflow from iflow_matcher...")
            from iflow_matcher import process_markdown_for_iflow
            logger.info("Successfully imported process_markdown_for_iflow function")
            logger.info("Import checks completed successfully!")
            return True
        except ImportError as e:
            logger.error(f"Error importing process_markdown_for_iflow: {str(e)}")
            return False
    except ImportError as e:
        logger.error(f"Error importing iflow_matcher: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during import check: {str(e)}")
        return False

if __name__ == "__main__":
    check_imports()
