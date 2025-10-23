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
    Process a markdown file to find SAP Integration Suite (iFlow) equivalents using RAG search.
    
    *** USES RAG SEARCH - No GitHub Token Needed ***

    Args:
        markdown_file_path (str): Path to the markdown file with MuleSoft documentation
        output_dir (str, optional): Directory to save output files. If None, uses the current directory.
        github_token (str, optional): DEPRECATED - Not used. Kept for backwards compatibility.

    Returns:
        dict: Dictionary with paths to generated files and other information
    """
    logger.info(f"🔍 Processing markdown file with RAG search: {markdown_file_path}")

    try:
        # Import RAG search module
        from rag_similarity_search import get_rag_search
        
        # Read markdown file
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        logger.info(f"📄 Read {len(markdown_content)} characters from markdown file")
        
        # Initialize RAG search
        rag_search = get_rag_search()
        
        # Search for similar iFlows using RAG
        logger.info("🔍 Searching for similar iFlows using RAG...")
        similar_iflows = rag_search.search_similar_flows(markdown_content, top_k=10)
        
        if not similar_iflows:
            logger.warning("⚠️ No similar iFlows found")
            similar_iflows = []
        else:
            logger.info(f"✅ Found {len(similar_iflows)} similar iFlows")
        
        # Generate match report
        match_report = rag_search.generate_match_report(similar_iflows)
        
        # Set up output directory
        if output_dir is None:
            output_dir = os.path.dirname(markdown_file_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate report HTML
        report_html_path = os.path.join(output_dir, "iflow_similarity_report.html")
        _generate_rag_report_html(similar_iflows, match_report, report_html_path)
        
        # Generate summary JSON
        summary_json_path = os.path.join(output_dir, "iflow_similarity_summary.json")
        _generate_rag_summary_json(similar_iflows, match_report, summary_json_path)
        
        logger.info(f"✅ RAG search completed successfully!")
        logger.info(f"   Report: {report_html_path}")
        logger.info(f"   Summary: {summary_json_path}")
        
        # Get top 5 matches for frontend display
        top_matches = similar_iflows[:5] if len(similar_iflows) > 0 else []
        
        return {
            "status": "success",
            "message": f"Found {len(similar_iflows)} similar iFlows using RAG search",
            "files": {
                "report": report_html_path,
                "summary": summary_json_path
            },
            "iflow_count": len(similar_iflows),
            "top_match": similar_iflows[0] if similar_iflows else None,
            "top_matches": top_matches  # Top 5 for frontend preview
        }

    except Exception as e:
        logger.error(f"❌ Error in RAG search: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            "status": "failed",
            "message": f"Error processing markdown with RAG: {str(e)}"
        }

def _generate_rag_report_html(similar_iflows, match_report, output_path):
    """Generate professional HTML report for RAG search results"""
    
    from datetime import datetime
    
    avg_sim = match_report.get('avg_similarity', 0) * 100 if match_report.get('avg_similarity') else 0
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    # Medal emojis for top 3
    def get_rank_badge(rank):
        if rank == 1:
            return '<span class="rank-badge gold">🥇 #1</span>'
        elif rank == 2:
            return '<span class="rank-badge silver">🥈 #2</span>'
        elif rank == 3:
            return '<span class="rank-badge bronze">🥉 #3</span>'
        else:
            return f'<span class="rank-badge default">#{rank}</span>'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAP Integration Flow Similarity Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        
        .header .timestamp {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 15px;
            font-style: italic;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8fafc;
            border-bottom: 3px solid #e2e8f0;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #1e3c72;
            margin: 10px 0;
        }}
        
        .summary-card .label {{
            font-size: 0.9em;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .summary-card.high .value {{ color: #10b981; }}
        .summary-card.medium .value {{ color: #f59e0b; }}
        .summary-card.low .value {{ color: #6b7280; }}
        
        .content {{
            padding: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #1e293b;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #e2e8f0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .iflow-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-bottom: 20px;
        }}
        
        .iflow-table thead {{
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
        }}
        
        .iflow-table th {{
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}
        
        .iflow-table th:first-child {{ text-align: center; width: 80px; }}
        .iflow-table th:nth-child(3) {{ text-align: center; width: 120px; }}
        .iflow-table th:nth-child(4) {{ text-align: center; width: 150px; }}
        
        .iflow-table tbody tr {{
            border-bottom: 1px solid #e2e8f0;
            transition: all 0.2s;
        }}
        
        .iflow-table tbody tr:hover {{
            background: #f8fafc;
            transform: scale(1.01);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .iflow-table td {{
            padding: 20px 15px;
            vertical-align: top;
        }}
        
        .rank-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .rank-badge.gold {{
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(251, 191, 36, 0.4);
        }}
        
        .rank-badge.silver {{
            background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(156, 163, 175, 0.4);
        }}
        
        .rank-badge.bronze {{
            background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(251, 146, 60, 0.4);
        }}
        
        .rank-badge.default {{
            background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
            color: white;
        }}
        
        .iflow-name {{
            font-size: 1.1em;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 8px;
        }}
        
        .iflow-description {{
            font-size: 0.9em;
            color: #64748b;
            line-height: 1.6;
        }}
        
        .quality-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }}
        
        .quality-badge.high {{
            background: #d1fae5;
            color: #065f46;
            border: 2px solid #10b981;
        }}
        
        .quality-badge.medium {{
            background: #fef3c7;
            color: #92400e;
            border: 2px solid #f59e0b;
        }}
        
        .quality-badge.low {{
            background: #f3f4f6;
            color: #374151;
            border: 2px solid #9ca3af;
        }}
        
        .score-container {{
            text-align: center;
        }}
        
        .score-value {{
            font-size: 2em;
            font-weight: bold;
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 12px;
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 8px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }}
        
        .progress-fill.high {{
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        }}
        
        .progress-fill.medium {{
            background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
        }}
        
        .progress-fill.low {{
            background: linear-gradient(90deg, #9ca3af 0%, #6b7280 100%);
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 30px;
            background: #f8fafc;
            border-radius: 12px;
            margin-top: 30px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.9em;
            color: #64748b;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            background: #1e293b;
            color: white;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SAP Integration Flow Similarity Report</h1>
            <div class="subtitle">RAG-Based Semantic Search Results</div>
            <div class="timestamp">Generated on {current_time}</div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="label">Total Matches</div>
                <div class="value">{match_report.get('total_results', 0)}</div>
            </div>
            <div class="summary-card high">
                <div class="label">High Quality</div>
                <div class="value">{match_report.get('high_quality_matches', 0)}</div>
                <div class="label" style="font-size: 0.75em; margin-top: 5px;">&gt;80% Similarity</div>
            </div>
            <div class="summary-card medium">
                <div class="label">Medium Quality</div>
                <div class="value">{match_report.get('medium_quality_matches', 0)}</div>
                <div class="label" style="font-size: 0.75em; margin-top: 5px;">60-80% Similarity</div>
            </div>
            <div class="summary-card">
                <div class="label">Average Score</div>
                <div class="value">{avg_sim:.1f}%</div>
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Similar Integration Flows
            </h2>
            
            <table class="iflow-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Integration Flow</th>
                        <th>Quality</th>
                        <th>Similarity Score</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for iflow in similar_iflows:
        quality_class = iflow['quality'].lower()
        score = iflow['similarity_score'] * 100
        
        html += f"""
                    <tr>
                        <td style="text-align: center;">
                            {get_rank_badge(iflow['rank'])}
                        </td>
                        <td>
                            <div class="iflow-name">{iflow['name']}</div>
                            <div class="iflow-description">{iflow['description']}</div>
                        </td>
                        <td style="text-align: center;">
                            <span class="quality-badge {quality_class}">
                                {'✓ ' if quality_class == 'high' else ''}{iflow['quality']}
                            </span>
                        </td>
                        <td>
                            <div class="score-container">
                                <div class="score-value">{score:.1f}%</div>
                                <div class="progress-bar">
                                    <div class="progress-fill {quality_class}" style="width: {score}%"></div>
                                </div>
                            </div>
                        </td>
                    </tr>
        """
    
    html += f"""
                </tbody>
            </table>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(135deg, #10b981, #059669);"></div>
                    <span>High Quality (&gt;80%)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(135deg, #f59e0b, #d97706);"></div>
                    <span>Medium Quality (60-80%)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(135deg, #9ca3af, #6b7280);"></div>
                    <span>Low Quality (&lt;60%)</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated using RAG (Retrieval Augmented Generation) with OpenAI text-embedding-ada-002</p>
            <p style="margin-top: 10px; font-size: 0.85em; opacity: 0.8;">
                Semantic search powered by Supabase vector database • {len(similar_iflows)} results shown
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

def _generate_rag_summary_json(similar_iflows, match_report, output_path):
    """Generate JSON summary for RAG search results"""
    
    summary = {
        "search_method": "RAG (Retrieval Augmented Generation)",
        "total_results": len(similar_iflows),
        "match_report": match_report,
        "similar_iflows": similar_iflows
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

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
