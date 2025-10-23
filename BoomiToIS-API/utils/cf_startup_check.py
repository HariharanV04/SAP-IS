"""
Cloud Foundry startup check script for BoomiToIS-API.
This script is run when the application starts to verify that all required modules can be imported.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_imports():
    """Check that all required modules can be imported"""
    logger.info("Starting import checks for BoomiToIS-API...")
    
    # Check working directory and Python path
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python version: {sys.version}")
    
    # List files in current directory
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        files = os.listdir(current_dir)
        logger.info(f"Files in BoomiToIS-API directory: {files}")
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return False
    
    # Check for required files
    required_files = [
        "enhanced_genai_iflow_generator.py",
        "enhanced_iflow_templates.py", 
        "boomi_xml_processor.py",
        "iflow_generator_api.py"
    ]
    
    missing_files = []
    for file in required_files:
        if file not in files:
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing required files: {missing_files}")
        return False
    
    logger.info("All required files found")
    
    # Try to import key modules
    try:
        logger.info("Trying to import enhanced_genai_iflow_generator...")
        from enhanced_genai_iflow_generator import EnhancedGenAIIFlowGenerator
        logger.info("Successfully imported EnhancedGenAIIFlowGenerator")
        logger.info(f"Module file: {EnhancedGenAIIFlowGenerator.__file__}")
        
        # Check if it's the correct version
        if hasattr(EnhancedGenAIIFlowGenerator, 'VERSION_ID'):
            logger.info(f"Version ID: {EnhancedGenAIIFlowGenerator.VERSION_ID}")
            if 'BoomiTOIS-API' in EnhancedGenAIIFlowGenerator.VERSION_ID:
                logger.info("✅ Correct version imported - BoomiTOIS-API")
            else:
                logger.warning("⚠️ Wrong version imported - not BoomiTOIS-API")
        
        logger.info("Import checks completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"Error importing enhanced_genai_iflow_generator: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during import check: {str(e)}")
        return False

if __name__ == "__main__":
    check_imports()













