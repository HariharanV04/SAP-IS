import re
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ContentSimilarityScorer:
    """
    Score and rank integration content based on similarity to Mulesoft implementation
    """
    
    def __init__(self, extracted_terms):
        """
        Initialize with extracted terms from Mulesoft documentation
        
        Args:
            extracted_terms (dict): Dictionary with categorized terms from Mulesoft documentation
        """
        self.extracted_terms = extracted_terms
        
        # Combine all relevant terms for matching
        self.all_terms = []
        for category in ['domain_terms', 'technical_terms', 'operation_terms']:
            if category in extracted_terms:
                self.all_terms.extend(extracted_terms[category])
        
        # Create a "document" from the Mulesoft terms for similarity comparison
        self.mulesoft_document = ' '.join(self.all_terms)
        
        # Create a list of important endpoint patterns
        self.endpoint_patterns = []
        if 'endpoint_paths' in extracted_terms:
            for path in extracted_terms['endpoint_paths']:
                # Replace path parameters with wildcards
                pattern = re.sub(r'{[^}]+}', '.*', path)
                self.endpoint_patterns.append(pattern)
        
        # Prepare TF-IDF vectorizer for content similarity
        self.vectorizer = None
    
    def preprocess_text(self, text):
        """Preprocess text for similarity comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
        
        return ' '.join(filtered_tokens)
    
    def calculate_term_match_score(self, item):
        """
        Calculate score based on term matches in different fields
        
        Args:
            item (dict): Discovery content item
            
        Returns:
            float: Term match score
        """
        score = 0
        
        # Extract text from relevant fields
        name = item.get('Name', '')
        description = item.get('Description', '')
        categories = item.get('Categories', [])
        tags = item.get('Tags', [])
        
        # Convert lists to strings
        categories_text = ' '.join(categories) if isinstance(categories, list) else str(categories)
        tags_text = ' '.join(tags) if isinstance(tags, list) else str(tags)
        
        # Combine all text
        all_text = f"{name} {description} {categories_text} {tags_text}".lower()
        
        # Score term matches with different weights
        for term in self.all_terms:
            term_lower = term.lower()
            
            # Exact match in name (highest weight)
            if term_lower in name.lower():
                score += 10
            
            # Exact match in description
            if term_lower in description.lower():
                score += 5
            
            # Match in categories or tags
            if term_lower in categories_text.lower() or term_lower in tags_text.lower():
                score += 3
            
            # Partial match anywhere
            if term_lower in all_text:
                score += 1
        
        return score
    
    def calculate_endpoint_match_score(self, item):
        """
        Calculate score based on API endpoint pattern matches
        
        Args:
            item (dict): Discovery content item
            
        Returns:
            float: Endpoint match score
        """
        score = 0
        
        # Check if this is an API/integration flow
        content_type = item.get('ContentType', '')
        if 'flow' not in content_type.lower() and 'api' not in content_type.lower():
            return score
        
        # Extract API information from description or other fields
        description = item.get('Description', '')
        
        # Look for endpoint patterns
        for pattern in self.endpoint_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                score += 5
                
        return score
    
    def calculate_content_similarity_score(self, items):
        """
        Calculate similarity scores based on TF-IDF and cosine similarity
        
        Args:
            items (list): List of Discovery content items
            
        Returns:
            dict: Dictionary mapping item IDs to similarity scores
        """
        if not items:
            return {}
        
        # Prepare corpus for TF-IDF
        corpus = [self.mulesoft_document]  # Start with Mulesoft document
        
        # Add content items to corpus
        for item in items:
            name = item.get('Name', '')
            description = item.get('Description', '')
            text = f"{name} {description}"
            preprocessed = self.preprocess_text(text)
            corpus.append(preprocessed)
        
        # Create and fit TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer()
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        
        # Calculate cosine similarity between Mulesoft doc and each item
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Map similarity scores to item IDs
        similarity_scores = {}
        for i, item in enumerate(items):
            item_id = item.get('Id')
            if item_id:
                similarity_scores[item_id] = float(cosine_similarities[i])
        
        return similarity_scores
    
    def score_and_rank_results(self, search_results, search_sources=None):
        """
        Score and rank search results based on similarity to Mulesoft implementation
        
        Args:
            search_results (list): List of search results from Discovery API
            search_sources (dict, optional): Dictionary mapping content IDs to search source info
            
        Returns:
            list: Sorted list of results with similarity scores
        """
        if not search_results:
            return []
        
        # Calculate different components of the score
        scored_results = []
        
        # Get content similarity scores (TF-IDF based)
        similarity_scores = self.calculate_content_similarity_score(search_results)
        
        for item in search_results:
            item_id = item.get('Id')
            
            # Calculate individual score components
            term_match_score = self.calculate_term_match_score(item)
            endpoint_match_score = self.calculate_endpoint_match_score(item)
            content_similarity = similarity_scores.get(item_id, 0)
            
            # Calculate search priority score
            search_priority_score = 0
            if search_sources and item_id in search_sources:
                source_info = search_sources[item_id]
                priority = source_info.get('priority')
                if priority == 'primary':
                    search_priority_score = 10
                elif priority == 'secondary':
                    search_priority_score = 5
                elif priority == 'tertiary':
                    search_priority_score = 2
            
            # Combine scores with weights
            combined_score = (
                term_match_score * 0.35 +
                endpoint_match_score * 0.25 +
                content_similarity * 0.25 +
                search_priority_score * 0.15
            )
            
            # Add scores to item
            result_with_scores = item.copy()
            result_with_scores['_scores'] = {
                'term_match': term_match_score,
                'endpoint_match': endpoint_match_score,
                'content_similarity': content_similarity,
                'search_priority': search_priority_score,
                'combined_score': combined_score
            }
            
            scored_results.append(result_with_scores)
        
        # Sort by combined score (descending)
        scored_results.sort(key=lambda x: x['_scores']['combined_score'], reverse=True)
        
        return scored_results
    
    def explain_match(self, item):
        """
        Generate an explanation of why an item matched
        
        Args:
            item (dict): Discovery content item with score information
            
        Returns:
            dict: Explanation of the match
        """
        if not item or '_scores' not in item:
            return {"explanation": "No score information available"}
        
        # Extract item details
        name = item.get('Name', '')
        description = item.get('Description', '')
        scores = item.get('_scores', {})
        
        # Find matching terms
        matching_terms = []
        for term in self.all_terms:
            term_lower = term.lower()
            if term_lower in (name + ' ' + description).lower():
                matching_terms.append(term)
        
        # Limit to top terms
        matching_terms = matching_terms[:5]
        
        # Generate explanation
        explanation = {
            "matching_terms": matching_terms,
            "score_breakdown": scores,
            "relevance": "High" if scores.get('combined_score', 0) > 20 else 
                        ("Medium" if scores.get('combined_score', 0) > 10 else "Low"),
            "explanation": self.generate_explanation_text(item, matching_terms, scores)
        }
        
        return explanation
    
    def generate_explanation_text(self, item, matching_terms, scores):
        """Generate a human-readable explanation text"""
        name = item.get('Name', '')
        content_type = item.get('ContentType', '')
        
        explanation = f"The {content_type} '{name}' matched "
        
        if matching_terms:
            explanation += f"based on these key terms: {', '.join(matching_terms)}. "
        else:
            explanation += "based on content similarity. "
        
        # Add score explanation
        combined_score = scores.get('combined_score', 0)
        if combined_score > 20:
            explanation += "This is a strong match with your Mulesoft implementation."
        elif combined_score > 10:
            explanation += "This is a moderate match that shares some similarities with your implementation."
        else:
            explanation += "This is a weaker match but may still contain useful patterns."
            
        return explanation


# Example usage
if __name__ == "__main__":
    # Example extracted terms (would come from Step 1)
    extracted_terms = {
        'domain_terms': ['Financial Services', 'Wealth Management', 'Investment Account'],
        'technical_terms': ['REST API', 'JSON', 'Transformation'],
        'operation_terms': ['Create', 'Update', 'Delete', 'Retrieve'],
        'endpoint_paths': ['/InvestmentAccounts/Initiate', '/InvestmentAccounts/Update']
    }
    
    # Example search results (would come from Step 2)
    search_results = [
        {
            'Id': 'package1',
            'Name': 'Financial Services API',
            'Description': 'REST API for wealth management and investment accounts',
            'ContentType': 'IntegrationPackage',
            'Categories': ['Financial', 'Banking']
        },
        {
            'Id': 'package2',
            'Name': 'Customer Profile Service',
            'Description': 'Update and manage customer profiles with REST endpoints',
            'ContentType': 'IntegrationFlow',
            'Categories': ['Customer', 'Profile']
        }
    ]
    
    # Example search sources (would come from Step 2)
    search_sources = {
        'package1': {'term': 'Financial Services API', 'priority': 'primary'},
        'package2': {'term': 'Profile management', 'priority': 'secondary'}
    }
    
    # Initialize scorer
    scorer = ContentSimilarityScorer(extracted_terms)
    
    # Score and rank results
    scored_results = scorer.score_and_rank_results(search_results, search_sources)
    
    # Print ranked results
    for i, result in enumerate(scored_results):
        scores = result.get('_scores', {})
        print(f"{i+1}. {result.get('Name')} - Score: {scores.get('combined_score', 0):.2f}")
        
        # Get explanation
        explanation = scorer.explain_match(result)
        print(f"   Explanation: {explanation.get('explanation')}")
        print(f"   Matching terms: {', '.join(explanation.get('matching_terms', []))}")
        print()