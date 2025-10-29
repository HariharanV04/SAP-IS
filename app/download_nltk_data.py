"""
Script to download required NLTK data.
Run this script once to download the necessary NLTK data files.
"""

import nltk
import os
import sys

def download_nltk_data():
    """Download required NLTK data files"""
    print("Downloading NLTK data files...")
    
    # Create nltk_data directory in the app folder
    nltk_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    # Set NLTK data path
    nltk.data.path.append(nltk_data_dir)
    
    # Download required data
    nltk.download('punkt', download_dir=nltk_data_dir)
    nltk.download('stopwords', download_dir=nltk_data_dir)
    nltk.download('wordnet', download_dir=nltk_data_dir)
    nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir)
    
    print(f"NLTK data downloaded to: {nltk_data_dir}")
    print("NLTK data paths:")
    for path in nltk.data.path:
        print(f"- {path}")

if __name__ == "__main__":
    download_nltk_data()
