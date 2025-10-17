"""
Script to set up dependencies for the MuleToIS-API.
This script copies the necessary files from the MuleToIflowGenAI Approach folder.
"""

import os
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_dependencies():
    """Copy necessary files from MuleToIflowGenAI Approach folder"""
    # Get the path to the MuleToIflowGenAI Approach folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    source_dir = os.path.join(parent_dir, "MuleToIflowGenAI Approach")
    
    # Check if the source directory exists
    if not os.path.exists(source_dir):
        logger.error(f"Source directory not found: {source_dir}")
        return False
    
    # List of files to copy
    files_to_copy = [
        "enhanced_genai_iflow_generator.py",
        "enhanced_iflow_templates.py",
        "enhanced_prompt_generator.py",
        "json_to_iflow_converter.py",
        "bpmn_templates.py",
        ".env"
    ]
    
    # Copy each file
    for file_name in files_to_copy:
        source_file = os.path.join(source_dir, file_name)
        dest_file = os.path.join(current_dir, file_name)
        
        if os.path.exists(source_file):
            try:
                shutil.copy2(source_file, dest_file)
                logger.info(f"Copied {file_name} to {current_dir}")
            except Exception as e:
                logger.error(f"Error copying {file_name}: {str(e)}")
        else:
            logger.warning(f"Source file not found: {source_file}")
    
    # Create directories if they don't exist
    dirs_to_create = ["genai_debug", "genai_output"]
    for dir_name in dirs_to_create:
        dir_path = os.path.join(current_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")
    
    logger.info("Dependencies setup completed")
    return True

if __name__ == "__main__":
    if setup_dependencies():
        print("\nDependencies setup completed successfully.")
        print("You can now run the API with: python app.py")
    else:
        print("\nError setting up dependencies. Please check the logs.")
        sys.exit(1)
