"""
Cloud Foundry startup check script.
This script verifies that all required dependencies are properly installed.
"""

import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_imports():
    """Check that all required packages can be imported"""
    required_packages = [
        'flask',
        'flask_cors',
        'dotenv',
        'anthropic',
        'requests',
        'werkzeug',
        'waitress',
        'tabulate',
        'bs4',  # beautifulsoup4
        'markdown',
        'nltk',
        'sklearn',  # scikit-learn
        'numpy',
        'matplotlib',
        'termcolor'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"Successfully imported {package}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"Failed to import {package}")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        return False
    
    # Check NLTK data
    try:
        import nltk
        nltk_data_dir = os.environ.get('NLTK_DATA', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data'))
        nltk.data.path.append(nltk_data_dir)
        
        # Try to load a tokenizer to verify NLTK data is available
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        logger.info("Successfully loaded NLTK data")
    except Exception as e:
        logger.error(f"Failed to load NLTK data: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_imports()
    if success:
        logger.info("All imports successful!")
        sys.exit(0)
    else:
        logger.error("Some imports failed!")
        sys.exit(1)
