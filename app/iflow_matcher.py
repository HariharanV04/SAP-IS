"""
Comprehensive iFlow matcher module for finding SAP Integration Suite equivalents.
This module extracts key terms from MuleSoft documentation and matches them with
appropriate SAP Integration Suite components.
"""

import os
import json
import logging
import markdown
from bs4 import BeautifulSoup
import re
import requests
from datetime import datetime
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import random  # For generating random scores in demo mode

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants for SAP Integration Suite components
SAP_COMPONENTS = [
    {
        "name": "SAP API Management",
        "description": "SAP API Management provides a comprehensive solution for API-based integration scenarios, including API creation, publishing, and monitoring.",
        "url": "https://help.sap.com/docs/SAP_CLOUD_PLATFORM_API_MANAGEMENT",
        "keywords": ["api", "rest", "http", "gateway", "management", "proxy", "security", "oauth"]
    },
    {
        "name": "SAP Cloud Integration",
        "description": "SAP Cloud Integration enables enterprise-wide integration of processes and data across cloud and on-premise systems.",
        "url": "https://help.sap.com/docs/CLOUD_INTEGRATION",
        "keywords": ["integration", "flow", "message", "transform", "mapping", "xml", "json", "protocol"]
    },
    {
        "name": "SAP Integration Suite - API Management",
        "description": "API Management capabilities within SAP Integration Suite for creating, publishing, and managing APIs.",
        "url": "https://help.sap.com/docs/SAP_INTEGRATION_SUITE",
        "keywords": ["api", "management", "gateway", "developer", "portal", "catalog", "lifecycle"]
    },
    {
        "name": "SAP Open Connectors",
        "description": "Pre-built connectors for integrating with third-party applications and services.",
        "url": "https://help.sap.com/docs/SAP_CLOUD_PLATFORM_INTEGRATION_FOR_OPEN_CONNECTORS",
        "keywords": ["connector", "third-party", "saas", "connection", "adapter"]
    },
    {
        "name": "SAP Integration Advisor",
        "description": "AI-powered tool for creating integration content and mappings.",
        "url": "https://help.sap.com/docs/SAP_CLOUD_PLATFORM_INTEGRATION_ADVISOR",
        "keywords": ["mapping", "b2b", "edi", "xml", "schema", "transformation"]
    },
    {
        "name": "SAP Process Orchestration",
        "description": "On-premise integration platform for process integration, business process management, and more.",
        "url": "https://help.sap.com/docs/SAP_PROCESS_ORCHESTRATION",
        "keywords": ["process", "orchestration", "workflow", "business", "rule", "bpm"]
    },
    {
        "name": "SAP Event Mesh",
        "description": "Event-driven architecture service for building loosely coupled integrations.",
        "url": "https://help.sap.com/docs/SAP_ENTERPRISE_MESSAGING",
        "keywords": ["event", "messaging", "queue", "publish", "subscribe", "asynchronous"]
    }
]

# Try to download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("Downloaded NLTK data")
    except Exception as e:
        logger.warning(f"Could not download NLTK data: {str(e)}")

# Try to get stopwords, with fallback
try:
    from nltk.corpus import stopwords
    STOPWORDS = set(stopwords.words('english'))
except:
    # Fallback stopwords if NLTK data is not available
    STOPWORDS = set([
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
        'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
        'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
        'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
        'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
        'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
    ])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_terms_from_markdown(markdown_file_path):
    """
    Extract key terms and information from a markdown file.

    Args:
        markdown_file_path (str): Path to the markdown file

    Returns:
        dict: Dictionary containing extracted information
    """
    # Read markdown file
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content)

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract text content
    text_content = soup.get_text()

    # Extract headers
    headers = []
    for h_tag in soup.find_all(['h1', 'h2', 'h3']):
        headers.append(h_tag.text.strip())

    # Extract API endpoints
    endpoint_patterns = re.findall(r'(GET|POST|PATCH|DELETE|PUT) (/\w+(?:/{\w+})?(?:/\w+)*)', markdown_content)
    endpoint_paths = [path for _, path in endpoint_patterns]

    # Extract URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    urls = re.findall(url_pattern, markdown_content)

    # Extract code blocks
    code_blocks = []
    for code_tag in soup.find_all('code'):
        code_blocks.append(code_tag.text.strip())

    # Extract technical terms using NLP
    try:
        # Tokenize text
        words = word_tokenize(text_content.lower())

        # Remove stopwords and punctuation
        words = [word for word in words if word.isalnum() and word not in STOPWORDS]

        # Count word frequencies
        word_freq = Counter(words)

        # Get most common words
        common_words = word_freq.most_common(30)

        # Extract sentences containing technical terms
        sentences = sent_tokenize(text_content)
        technical_sentences = []

        # Technical terms to look for
        technical_terms = [
            "REST", "API", "JSON", "HTTP", "HTTPS", "Authentication", "Flow",
            "Integration", "Connector", "Endpoint", "Payload", "Transform",
            "Mapping", "Protocol", "Service", "Message", "Queue", "Event",
            "Synchronous", "Asynchronous", "XML", "SOAP", "Gateway", "Proxy"
        ]

        # Find sentences containing technical terms
        for sentence in sentences:
            for term in technical_terms:
                if term.lower() in sentence.lower():
                    technical_sentences.append(sentence)
                    break

        # Find technical terms in the text
        found_technical_terms = []
        for term in technical_terms:
            if term.lower() in text_content.lower():
                found_technical_terms.append(term)
    except Exception as e:
        logger.warning(f"Error in NLP processing: {str(e)}")
        common_words = []
        technical_sentences = []
        found_technical_terms = ["REST", "API", "Integration"]  # Fallback

    # Extract integration patterns
    integration_patterns = []
    pattern_keywords = {
        "Request-Response": ["request", "response", "synchronous"],
        "Publish-Subscribe": ["publish", "subscribe", "event", "topic"],
        "Message Queue": ["queue", "message", "jms", "amqp"],
        "File Transfer": ["file", "transfer", "ftp", "sftp"],
        "Database Integration": ["database", "sql", "jdbc", "query"],
        "API-Led": ["api", "experience", "process", "system"],
        "Event-Driven": ["event", "trigger", "notification"],
        "Batch Processing": ["batch", "bulk", "scheduled"]
    }

    for pattern, keywords in pattern_keywords.items():
        for keyword in keywords:
            if keyword in text_content.lower():
                integration_patterns.append(pattern)
                break

    # Return extracted terms
    return {
        "headers": headers,
        "endpoints": endpoint_paths,
        "urls": urls,
        "code_blocks": code_blocks,
        "common_words": [word for word, count in common_words],
        "technical_terms": found_technical_terms,
        "technical_sentences": technical_sentences[:5],  # Limit to 5 sentences
        "integration_patterns": list(set(integration_patterns)),  # Remove duplicates
        "text_content": text_content[:1000]  # First 1000 chars for summary
    }

def calculate_component_scores(extracted_terms):
    """
    Calculate match scores for SAP components based on extracted terms.

    Args:
        extracted_terms (dict): Dictionary of extracted terms from markdown

    Returns:
        list: List of components with match scores
    """
    scored_components = []

    # Combine all relevant terms for matching
    all_terms = " ".join([
        " ".join(extracted_terms.get("headers", [])),
        " ".join(extracted_terms.get("endpoints", [])),
        " ".join(extracted_terms.get("technical_terms", [])),
        " ".join(extracted_terms.get("integration_patterns", [])),
        " ".join(extracted_terms.get("common_words", [])),
        " ".join(extracted_terms.get("technical_sentences", []))
    ]).lower()

    # Calculate score for each component
    for component in SAP_COMPONENTS:
        score = 0
        matches = []

        # Check for keyword matches
        for keyword in component["keywords"]:
            if keyword in all_terms:
                score += 10
                matches.append(keyword)

        # Check for name match
        if component["name"].lower() in all_terms:
            score += 15
            matches.append(component["name"])

        # Check for integration patterns
        for pattern in extracted_terms.get("integration_patterns", []):
            if pattern == "API-Led" and "API" in component["name"]:
                score += 20
                matches.append("API-Led Integration")
            elif pattern == "Event-Driven" and "Event" in component["name"]:
                score += 20
                matches.append("Event-Driven Architecture")
            elif pattern == "Message Queue" and any(k in component["keywords"] for k in ["queue", "messaging"]):
                score += 15
                matches.append("Message Queuing")

        # Check for API endpoints
        if len(extracted_terms.get("endpoints", [])) > 0 and "API" in component["name"]:
            score += 15
            matches.append("API Endpoints")

        # Normalize score to 0-100 range
        normalized_score = min(100, score)

        # Add component with score to results
        scored_components.append({
            "name": component["name"],
            "description": component["description"],
            "url": component["url"],
            "score": normalized_score,
            "matches": matches
        })

    # Sort by score (descending)
    scored_components.sort(key=lambda x: x["score"], reverse=True)

    return scored_components

def process_markdown_for_iflow(markdown_file_path, output_dir=None, github_token=None):
    """
    Process a markdown file to find SAP Integration Suite (iFlow) equivalents.

    Args:
        markdown_file_path (str): Path to the markdown file with MuleSoft documentation
        output_dir (str, optional): Directory to save output files. If None, uses the current directory.
        github_token (str, optional): GitHub token for API access.

    Returns:
        dict: Dictionary with paths to generated files and other information
    """
    logger.info(f"Processing markdown file: {markdown_file_path}")

    try:
        # Import the main processing function from the main module
        # Use a safer import approach to avoid reloading issues
        import sys
        import importlib.util

        # Get the path to the main.py file
        # Try both possible locations for main.py
        main_path_in_getiflow = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "GetIflowEquivalent", "main.py")
        main_path_in_app = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

        # Check which path exists
        if os.path.exists(main_path_in_getiflow):
            main_path = main_path_in_getiflow
            logger.info(f"Found main.py in GetIflowEquivalent directory")
        elif os.path.exists(main_path_in_app):
            main_path = main_path_in_app
            logger.info(f"Found main.py in app directory")
        else:
            # Default to the app directory path for error reporting
            main_path = main_path_in_app

        # Check if the file exists
        logger.info(f"Looking for main module at: {main_path}")
        if not os.path.exists(main_path):
            logger.error(f"Main module not found at: {main_path}")

            # List files in the directory to help diagnose the issue
            parent_dir = os.path.dirname(main_path)
            if os.path.exists(parent_dir):
                logger.info(f"Contents of {parent_dir}:")
                for file in os.listdir(parent_dir):
                    logger.info(f"  - {file}")
            else:
                logger.error(f"Parent directory does not exist: {parent_dir}")

            return {
                "status": "failed",
                "message": f"Main module not found at: {main_path}"
            }

        # Import the module using importlib
        spec = importlib.util.spec_from_file_location("iflow_main", main_path)
        iflow_main = importlib.util.module_from_spec(spec)

        # Add the directory containing the module to sys.path temporarily
        # This helps with relative imports within the module
        module_dir = os.path.dirname(main_path)
        original_sys_path = sys.path.copy()
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)

        try:
            # Execute the module
            spec.loader.exec_module(iflow_main)

            # Call the main processing function
            result = iflow_main.process_markdown_for_iflow(
                markdown_file_path=markdown_file_path,
                output_dir=output_dir,
                github_token=github_token
            )
        finally:
            # Restore the original sys.path
            sys.path = original_sys_path

        return result

    except Exception as e:
        logger.error(f"Error importing or calling main module: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            "status": "failed",
            "message": f"Error processing markdown: {str(e)}"
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = process_markdown_for_iflow(sys.argv[1])
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        if result["status"] == "success":
            print(f"Report: {result['files']['report']}")
            print(f"Summary: {result['files']['summary']}")
    else:
        print("Please provide a markdown file path")
