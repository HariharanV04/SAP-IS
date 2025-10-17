import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
import markdown
from bs4 import BeautifulSoup
import json

# You may need to download NLTK resources
# nltk.download('punkt')
# nltk.download('stopwords')

def extract_terms_from_markdown(markdown_file):
    """
    Extract key terms from markdown file for search in SAP Integration Suite
    
    Args:
        markdown_file (str): Path to markdown file
        
    Returns:
        dict: Dictionary with categorized search terms
    """
    # Read markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content)
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize categories for terms
    terms = {
        'domain_terms': [],      # Financial Services, Wealth Management, etc.
        'technical_terms': [],   # API, REST, JSON, etc.
        'operation_terms': [],   # Create, Update, Delete, etc.
        'endpoint_paths': [],    # API paths
        'data_structures': [],   # JSON schemas
        'overview_terms': []     # Terms from API Overview section
    }
    
    # Extract API Overview section
    api_overview_section = extract_section_content(markdown_content, "API Overview", 1)
    if api_overview_section:
        # Extract key phrases and terms from the overview section
        overview_terms = extract_key_terms_from_text(api_overview_section)
        terms['overview_terms'] = overview_terms
        # Add overview terms to domain terms for better matching
        terms['domain_terms'].extend(overview_terms)
    
    # Extract headers (h1, h2, h3) for main concepts
    headers = []
    for h_tag in soup.find_all(['h1', 'h2', 'h3']):
        headers.append(h_tag.text.strip())
    
    # Extract API endpoints
    endpoint_patterns = re.findall(r'(GET|POST|PATCH|DELETE|PUT) (/\w+(?:/{\w+})?(?:/\w+)*)', markdown_content)
    endpoint_paths = [path for _, path in endpoint_patterns]
    terms['endpoint_paths'] = endpoint_paths
    
    # Extract JSON structures
    json_blocks = re.findall(r'```json\n([\s\S]*?)\n```', markdown_content)
    terms['data_structures'] = json_blocks
    
    # Extract domain-specific terms
    domain_specific_keywords = [
        'Financial Services', 'Wealth Management', 'Investment', 'Account', 
        'Beneficiary', 'Customer', 'Payment', 'Profile', 'Standing Order',
        'ACATS', 'RMD', 'Transaction', 'API', 'Investment Account'
    ]
    
    # Extract technical patterns
    technical_patterns = [
        'REST', 'API', 'JSON', 'ID Generation', 'Transformation', 'DataWeave',
        'HTTP', 'HTTPS', 'Authentication', 'Error Handling', 'Flow'
    ]
    
    # Extract operation terms
    operation_terms = [
        'Create', 'Read', 'Update', 'Delete', 'Initiate', 'Process', 'Retrieve',
        'Transfer', 'Cancel', 'GET', 'POST', 'PATCH', 'DELETE', 'PUT'
    ]
    
    # Process text content
    text_content = soup.get_text()
    
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text_content.lower())
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    # Count word frequency
    word_freq = Counter(filtered_tokens)
    
    # Extract ngrams (for multi-word terms)
    sentences = sent_tokenize(text_content)
    ngrams = []
    
    for sentence in sentences:
        words = word_tokenize(sentence)
        # Create bigrams and trigrams
        for i in range(len(words) - 1):
            ngrams.append(f"{words[i]} {words[i+1]}")
        for i in range(len(words) - 2):
            ngrams.append(f"{words[i]} {words[i+1]} {words[i+2]}")
    
    ngram_freq = Counter(ngrams)
    
    # Match domain keywords
    for keyword in domain_specific_keywords:
        keyword_lower = keyword.lower()
        # Check exact matches
        if keyword_lower in text_content.lower():
            terms['domain_terms'].append(keyword)
        # Check partial matches in ngrams
        else:
            for ngram, _ in ngram_freq.most_common(100):
                if keyword_lower in ngram.lower():
                    terms['domain_terms'].append(keyword)
                    break
    
    # Match technical patterns
    for pattern in technical_patterns:
        pattern_lower = pattern.lower()
        if pattern_lower in text_content.lower():
            terms['technical_terms'].append(pattern)
    
    # Match operation terms
    for op in operation_terms:
        op_lower = op.lower()
        if op_lower in text_content.lower():
            terms['operation_terms'].append(op)
    
    # Remove duplicates
    for category in terms:
        if isinstance(terms[category], list):
            terms[category] = list(set(terms[category]))
    
    # Extract sections with specific technical details
    mulesoft_sections = extract_sections(markdown_content, "Current MuleSoft Flow Logic", "Configuration")
    
    # Add technical implementation details
    if mulesoft_sections:
        technical_details = extract_technical_details(mulesoft_sections)
        terms['technical_details'] = technical_details
    
    # Add header-based terms
    terms['header_terms'] = headers
    
    return terms
def extract_section_content(markdown_content, section_name, level=2):
    """
    Extract content from a specific section in the markdown
    
    Args:
        markdown_content (str): The markdown content
        section_name (str): The name of the section to extract
        level (int): The heading level (1 for #, 2 for ##, etc.)
        
    Returns:
        str: The section content or None if not found
    """
    # Create the heading pattern based on level
    heading_marker = '#' * level
    pattern = f"{heading_marker} {section_name}([\\s\\S]*?)(?:{heading_marker} |$)"
    
    match = re.search(pattern, markdown_content)
    if match:
        return match.group(1).strip()
    return None

def extract_key_terms_from_text(text):
    """
    Extract important key terms from text
    
    Args:
        text (str): The text to analyze
        
    Returns:
        list: List of key terms
    """
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Extract noun phrases and important terms
    key_terms = []
    
    # Look for capitalized terms (often important concepts)
    capitalized_pattern = r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b'
    capitalized_terms = re.findall(capitalized_pattern, text)
    key_terms.extend(capitalized_terms)
    
    # Look for terms in bullet points
    bullet_pattern = r'[-*]\s+([^.\n]+)'
    bullet_points = re.findall(bullet_pattern, text)
    key_terms.extend(bullet_points)
    
    # Extract bigrams and trigrams that appear meaningful
    words = word_tokenize(text)
    bigrams = []
    trigrams = []
    
    for i in range(len(words) - 1):
        if words[i].isalnum() and words[i+1].isalnum():
            bigrams.append(f"{words[i]} {words[i+1]}")
    
    for i in range(len(words) - 2):
        if words[i].isalnum() and words[i+1].isalnum() and words[i+2].isalnum():
            trigrams.append(f"{words[i]} {words[i+1]} {words[i+2]}")
    
    # Add most common meaningful bigrams and trigrams
    bigram_counter = Counter(bigrams)
    trigram_counter = Counter(trigrams)
    
    key_terms.extend([b for b, c in bigram_counter.most_common(10) if not any(w in stop_words for w in b.split())])
    key_terms.extend([t for t, c in trigram_counter.most_common(5) if not any(w in stop_words for w in t.split())])
    
    # Remove duplicates and clean up
    cleaned_terms = []
    for term in key_terms:
        term = term.strip()
        if term and len(term) > 3:  # Only keep terms longer than 3 characters
            cleaned_terms.append(term)
    
    return list(set(cleaned_terms))

def extract_sections(markdown_content, start_header, end_header):
    """Extract a section from markdown between two headers"""
    pattern = f"# {start_header}([\\s\\S]*?)# {end_header}"
    match = re.search(pattern, markdown_content)
    if match:
        return match.group(1).strip()
    return None

def extract_technical_details(section_text):
    """Extract technical implementation details from section text"""
    # Look for flow identifiers
    flow_names = re.findall(r'\*\*Trigger\*\*: \w+ request to `([^`]+)`', section_text)
    
    # Look for transformation functions
    transformations = re.findall(r'`([^`]+\.dwl)`', section_text)
    
    # Look for processing steps
    processing_steps = []
    step_blocks = re.findall(r'\*\*Processing Steps\*\*:([\s\S]*?)(?:\n\n|$)', section_text)
    for block in step_blocks:
        steps = re.findall(r'\d+\.\s*(.*?)(?:\n|$)', block)
        processing_steps.extend(steps)
    
    return {
        'flow_names': flow_names,
        'transformations': transformations,
        'processing_steps': processing_steps
    }

def generate_search_terms(extracted_terms):
    """
    Generate weighted search terms from extracted terms
    
    Args:
        extracted_terms (dict): Dictionary with categorized terms
        
    Returns:
        dict: Dictionary with prioritized search terms
    """
    search_terms = {
        'primary': [],    # Most specific/important terms
        'secondary': [],  # Technical pattern terms
        'tertiary': []    # Business operation terms
    }
    
    # Process overview terms to create more effective search terms
    if 'overview_terms' in extracted_terms:
        for term in extracted_terms['overview_terms']:
            # Break down longer terms into smaller meaningful chunks
            if len(term.split()) > 2:
                # Extract meaningful phrases (2-3 words)
                words = term.split()
                for i in range(len(words)-1):
                    bigram = f"{words[i]} {words[i+1]}"
                    if len(bigram) > 5 and bigram not in search_terms['primary']:
                        search_terms['primary'].append(bigram)
                
                # Also add individual important words
                for word in words:
                    if len(word) > 4 and word not in ['with', 'that', 'this', 'from', 'into']:
                        if word not in search_terms['primary']:
                            search_terms['primary'].append(word)
            else:
                # Add shorter terms directly
                if term not in search_terms['primary']:
                    search_terms['primary'].append(term)
    
    # Process domain terms similarly
    for domain_term in extracted_terms['domain_terms']:
        # Break down longer domain terms
        if len(domain_term.split()) > 2:
            words = domain_term.split()
            for i in range(len(words)-1):
                bigram = f"{words[i]} {words[i+1]}"
                if len(bigram) > 5 and bigram not in search_terms['primary']:
                    search_terms['primary'].append(bigram)
            
            # Add individual words from domain terms
            for word in words:
                if len(word) > 4 and word not in ['with', 'that', 'this', 'from', 'into']:
                    if word not in search_terms['secondary']:
                        search_terms['secondary'].append(word)
        else:
            # Add shorter domain terms directly
            if domain_term not in search_terms['primary']:
                search_terms['primary'].append(domain_term)
    
    # Create combinations of technical and domain terms
    for tech_term in extracted_terms['technical_terms']:
        # Add technical terms directly to secondary
        if tech_term not in search_terms['secondary']:
            search_terms['secondary'].append(tech_term)
        
        # Create concise combinations with domain terms
        for domain_term in extracted_terms['domain_terms']:
            # Only use the last word of domain_term if it's a multi-word term
            domain_parts = domain_term.split()
            domain_part = domain_parts[-1] if len(domain_parts) > 1 else domain_term
            
            # Only create combination if both terms are reasonably short
            if len(tech_term) + len(domain_part) < 25:
                combined = f"{tech_term} {domain_part}"
                if combined not in search_terms['secondary']:
                    search_terms['secondary'].append(combined)
    
    # Add operation terms and combinations
    for op_term in extracted_terms['operation_terms']:
        if op_term not in search_terms['tertiary']:
            search_terms['tertiary'].append(op_term)
        
        # Create concise operation + domain combinations
        for domain_term in extracted_terms['domain_terms']:
            domain_parts = domain_term.split()
            domain_part = domain_parts[-1] if len(domain_parts) > 1 else domain_term
            
            if len(op_term) + len(domain_part) < 25:
                combined = f"{op_term} {domain_part}"
                if combined not in search_terms['tertiary']:
                    search_terms['tertiary'].append(combined)
    
    # Add technical implementation details if available
    if 'technical_details' in extracted_terms and 'flow_names' in extracted_terms['technical_details']:
        for flow_name in extracted_terms['technical_details']['flow_names']:
            # Extract endpoint part from flow name
            endpoint_match = re.search(r'`([^`]+)`', flow_name)
            if endpoint_match:
                endpoint = endpoint_match.group(1)
                parts = endpoint.split('/')
                for part in parts:
                    if len(part) > 3 and part not in ['{accountId}', '{customerId}']:
                        if part not in search_terms['primary']:
                            search_terms['primary'].append(part)
    
    # Limit to most relevant terms and ensure lowercase for case-insensitive matching
    search_terms['primary'] = [term.lower() for term in search_terms['primary'][:15]]
    search_terms['secondary'] = [term.lower() for term in search_terms['secondary'][:20]]
    search_terms['tertiary'] = [term.lower() for term in search_terms['tertiary'][:25]]
    
    return search_terms

# Example usage
if __name__ == "__main__":
    markdown_file = "mulesoft_documentation.md"
    extracted_terms = extract_terms_from_markdown(markdown_file)
    search_terms = generate_search_terms(extracted_terms)
    
    print("Extracted Terms:")
    print(json.dumps(extracted_terms, indent=2))
    
    print("\nGenerated Search Terms:")
    print(json.dumps(search_terms, indent=2))