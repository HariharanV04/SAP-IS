"""
NLTK setup script to download required data.
This script is imported by app.py during startup.
"""

import os
import nltk
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_nltk():
    """Download required NLTK data packages"""
    try:
        # Set NLTK data path
        nltk_data_dir = os.environ.get('NLTK_DATA', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data'))
        os.makedirs(nltk_data_dir, exist_ok=True)
        nltk.data.path.append(nltk_data_dir)
        
        logger.info(f"NLTK data directory: {nltk_data_dir}")
        
        # List of required NLTK data packages
        required_packages = [
            'punkt',
            'stopwords',
            'wordnet',
            'averaged_perceptron_tagger'
        ]
        
        # Download each package
        for package in required_packages:
            try:
                logger.info(f"Downloading NLTK package: {package}")
                nltk.download(package, download_dir=nltk_data_dir, quiet=True)
                logger.info(f"Successfully downloaded NLTK package: {package}")
            except Exception as e:
                logger.warning(f"Error downloading NLTK package {package}: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Error setting up NLTK: {str(e)}")
        return False

# Run setup when imported
setup_result = setup_nltk()
logger.info(f"NLTK setup completed with result: {setup_result}")
