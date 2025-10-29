"""
Supabase Vector Store implementation for SAP iFlow RAG system.
Works with the 4-table iFlow vector database schema.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os
import numpy as np
import json

from supabase import create_client, Client

# Import CodeBERT for embeddings
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SupabaseVectorStore:
    """Vector store for SAP iFlow embeddings using Supabase API."""
    
    def __init__(self, supabase_url: str, supabase_key: str, embedding_model=None, use_codebert: bool = True):
        """
        Initialize Supabase vector store.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key (preferably service role key)
            embedding_model: Optional embedding model for query encoding
            use_codebert: Whether to initialize CodeBERT for embedding queries
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.embedding_model = embedding_model
        
        # Create Supabase client
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # iFlow database table schema
        self.tables = {
            'assets': 'iflow_assets',
            'components': 'iflow_components', 
            'flows': 'iflow_flows',
            'packages': 'iflow_packages'
        }
        
        # Initialize CodeBERT for query encoding
        self.codebert_model = None
        self.codebert_tokenizer = None
        
        if use_codebert and TRANSFORMERS_AVAILABLE:
            try:
                print("Loading CodeBERT model for query encoding...")
                self.codebert_tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
                self.codebert_model = AutoModel.from_pretrained("microsoft/codebert-base")
                self.codebert_model.eval()  # Set to evaluation mode
                print("CodeBERT loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load CodeBERT: {e}")
                print(f"CodeBERT loading failed: {e}")
        elif use_codebert:
            print("Transformers not available - install with: pip install transformers torch")
        
        logger.info(f"Initialized SupabaseVectorStore with URL: {supabase_url}")
    
    def _encode_query(self, query: str) -> Optional[List[float]]:
        """
        Encode query text to embedding vector using CodeBERT.
        
        Args:
            query: Text query to encode
            
        Returns:
            List of floats representing the embedding, or None if encoding fails
        """
        # Try custom embedding model first
        if self.embedding_model:
            try:
                if hasattr(self.embedding_model, 'encode'):
                    return self.embedding_model.encode([query])[0].tolist()
            except Exception as e:
                logger.warning(f"Failed to encode query with custom model: {e}")
        
        # Try CodeBERT
        if self.codebert_model and self.codebert_tokenizer:
            try:
                # Tokenize and encode
                inputs = self.codebert_tokenizer(query, return_tensors='pt', 
                                               truncation=True, max_length=512, padding=True)
                
                with torch.no_grad():
                    outputs = self.codebert_model(**inputs)
                    # Use mean pooling of last hidden states
                    embeddings = outputs.last_hidden_state.mean(dim=1)
                    return embeddings[0].tolist()
                    
            except Exception as e:
                logger.warning(f"Failed to encode query with CodeBERT: {e}")
        
        # Return None to indicate text-based search fallback
        return None
    
    async def search_similar(self, query: str, limit: int = 5, chunk_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar content across all iFlow tables.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            chunk_types: Optional filter by content types
            
        Returns:
            List of matching documents with metadata
        """
        logger.info(f"Searching for: '{query}' (limit: {limit})")
        
        all_results = []
        
        try:
            # Search across all 4 tables
            search_results = await self._search_all_tables(query, limit)
            
            # Convert results to standardized format
            for result in search_results:
                doc = self._format_document(result)
                if doc:
                    all_results.append(doc)
            
            # Sort by relevance score if available
            all_results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
            
            # Limit results
            final_results = all_results[:limit]
            
            logger.info(f"Found {len(final_results)} matching documents")
            return final_results
            
        except Exception as e:
            logger.error(f"Error in search_similar: {e}")
            return []
    
    async def _search_all_tables(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search across all iFlow tables for relevant content."""
        all_matches = []
        
        # Define search strategies for each table
        search_strategies = {
            'iflow_assets': {
                'text_columns': ['description', 'content', 'file_name'],
                'embedding_columns': ['description_embedding', 'content_embedding'],
                'metadata_columns': ['id', 'package_id', 'file_type', 'created_at']
            },
            'iflow_components': {
                'text_columns': ['description', 'activity_type', 'complete_bpmn_xml'],
                'embedding_columns': ['description_embedding', 'code_embedding', 'activity_type_embedding'],
                'metadata_columns': ['id', 'package_id', 'component_id', 'activity_type', 'properties', 'created_at']
            },
            'iflow_flows': {
                'text_columns': ['description', 'content', 'flow_type'],
                'embedding_columns': ['description_embedding', 'flow_embedding'],
                'metadata_columns': ['id', 'package_id', 'source_component_id', 'target_component_id', 'created_at']
            },
            'iflow_packages': {
                'text_columns': ['description', 'package_name', 'iflw_xml'],
                'embedding_columns': ['description_embedding'],
                'metadata_columns': ['id', 'version', 'created_at']
            }
        }
        
        # Search each table sequentially (prevents concurrent load)
        for table_name, strategy in search_strategies.items():
            try:
                matches = await self._search_table(table_name, query, strategy, limit)
                for match in matches:
                    match['source_table'] = table_name
                    all_matches.append(match)
            except Exception as e:
                error_msg = str(e)
                if 'statement timeout' in error_msg or '57014' in error_msg:
                    logger.error(f"Error searching table {table_name}: {error_msg}")
                    # Continue with other tables even if one times out
                else:
                    logger.warning(f"Error searching table {table_name}: {e}")
                continue
        
        return all_matches
    
    async def _search_table(self, table_name: str, query: str, strategy: Dict, limit: int) -> List[Dict[str, Any]]:
        """Search a specific table using text matching and metadata filtering."""
        
        try:
            # Build query with text search across relevant columns
            query_lower = query.lower()
            
            # Optimize query: select only necessary columns and limit rows
            # This prevents statement timeouts by reducing data transfer
            columns_to_select = strategy['text_columns'] + strategy['metadata_columns']
            select_clause = ','.join(columns_to_select)
            
            # Limit to 100 rows per table to prevent timeouts
            # This is sufficient for RAG retrieval
            try:
                result = self.supabase.table(table_name).select(select_clause).limit(100).execute()
            except Exception as query_error:
                error_msg = str(query_error)
                if 'statement timeout' in error_msg or '57014' in error_msg:
                    logger.warning(f"Timeout for {table_name}, trying with reduced limit...")
                    # Retry with smaller limit
                    try:
                        result = self.supabase.table(table_name).select(select_clause).limit(20).execute()
                    except:
                        logger.error(f"Failed even with reduced limit for {table_name}")
                        return []
                else:
                    raise
            
            if not result.data:
                return []
            
            # Score and filter results
            scored_results = []
            
            for row in result.data:
                score = self._calculate_text_relevance(row, query_lower, strategy['text_columns'])
                
                if score > 0:  # Only include if there's some relevance
                    scored_results.append({
                        **row,
                        'relevance_score': score,
                        'table_source': table_name
                    })
            
            # Sort by relevance and return top results
            scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return scored_results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching table {table_name}: {e}")
            return []
    
    def _calculate_text_relevance(self, row: Dict, query_lower: str, text_columns: List[str]) -> float:
        """Calculate relevance score based on text matching."""
        total_score = 0.0
        query_terms = set(query_lower.split())
        
        for column in text_columns:
            if column not in row or not row[column]:
                continue
                
            text = str(row[column]).lower()
            
            # Exact phrase match (highest score)
            if query_lower in text:
                total_score += 10.0
            
            # Individual term matches
            text_terms = set(text.split())
            matching_terms = query_terms.intersection(text_terms)
            
            if matching_terms:
                # Score based on percentage of query terms found
                term_score = len(matching_terms) / len(query_terms) * 5.0
                total_score += term_score
            
            # Partial word matches
            for term in query_terms:
                if len(term) > 3 and term in text:
                    total_score += 1.0
        
        return total_score
    
    def _format_document(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw database result into standardized document format."""
        
        table_source = raw_result.get('source_table', raw_result.get('table_source', 'unknown'))
        
        # Extract content based on table type
        if table_source == 'iflow_assets':
            content = raw_result.get('content', '')
            title = raw_result.get('file_name', 'Unnamed Asset')
            description = raw_result.get('description', '')
            doc_type = 'asset'
            
        elif table_source == 'iflow_components':
            content = raw_result.get('complete_bpmn_xml', '')
            title = f"Component: {raw_result.get('component_id', 'Unknown')}"
            description = raw_result.get('description', '')
            doc_type = 'component'
            
        elif table_source == 'iflow_flows':
            content = raw_result.get('content', '')
            title = f"Flow: {raw_result.get('source_component_id', '')} → {raw_result.get('target_component_id', '')}"
            description = raw_result.get('description', '')
            doc_type = 'flow'
            
        elif table_source == 'iflow_packages':
            content = raw_result.get('iflw_xml', '')
            title = raw_result.get('package_name', 'Unnamed Package')
            description = raw_result.get('description', '')
            doc_type = 'package'
            
        else:
            content = str(raw_result)
            title = 'Unknown Document'
            description = ''
            doc_type = 'unknown'
        
        # Scale similarity score to be out of 10 (from ~0-30 range)
        raw_score = raw_result.get('relevance_score', raw_result.get('similarity_score', 0.0))
        scaled_score = min(raw_score / 3.0, 10.0)  # Scale to 0-10 range
        
        # Create standardized document format
        formatted_doc = {
            'id': raw_result.get('id', 'unknown'),
            'document_name': title,
            'content': content[:2000] if content else '',  # Limit content length
            'description': description[:500] if description else '',  # Limit description length
            'document_type': doc_type,
            'source_table': table_source,
            'similarity_score': round(scaled_score, 1),
            'metadata': {
                'package_id': raw_result.get('package_id'),
                'created_at': raw_result.get('created_at'),
                'file_type': raw_result.get('file_type'),
                'activity_type': raw_result.get('activity_type'),
                'flow_type': raw_result.get('flow_type'),
                'version': raw_result.get('version'),
                'properties': raw_result.get('properties'),  # Include properties JSON field
            },
            'chunk_type': doc_type,
            'confidence': min(raw_result.get('relevance_score', 0.0) / 10.0, 1.0)  # Normalize to 0-1
        }
        
        # Remove None values from metadata
        formatted_doc['metadata'] = {k: v for k, v in formatted_doc['metadata'].items() if v is not None}
        
        return formatted_doc
    
    async def get_document_by_id(self, doc_id: str, table_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document by ID."""
        
        # If table is specified, search only that table
        if table_name and table_name in self.tables.values():
            try:
                result = self.supabase.table(table_name).select("*").eq("id", doc_id).execute()
                if result.data:
                    doc = result.data[0]
                    doc['source_table'] = table_name
                    return self._format_document(doc)
            except Exception as e:
                logger.error(f"Error getting document from {table_name}: {e}")
        
        # Search all tables
        for table_name in self.tables.values():
            try:
                result = self.supabase.table(table_name).select("*").eq("id", doc_id).execute()
                if result.data:
                    doc = result.data[0]
                    doc['source_table'] = table_name
                    return self._format_document(doc)
            except Exception as e:
                logger.warning(f"Error searching {table_name} for ID {doc_id}: {e}")
                continue
        
        return None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {
            'total_documents': 0,
            'tables': {}
        }
        
        for table_key, table_name in self.tables.items():
            try:
                result = self.supabase.table(table_name).select("*", count="exact").limit(1).execute()
                count = result.count if hasattr(result, 'count') else 0
                stats['tables'][table_key] = {
                    'name': table_name,
                    'count': count
                }
                stats['total_documents'] += count
            except Exception as e:
                logger.error(f"Error getting stats for {table_name}: {e}")
                stats['tables'][table_key] = {
                    'name': table_name,
                    'count': 0,
                    'error': str(e)
                }
        
        return stats


def create_supabase_vector_store(config_module=None, use_codebert: bool = True) -> SupabaseVectorStore:
    """
    Factory function to create SupabaseVectorStore from config.
    
    Args:
        config_module: Configuration module with SUPABASE_URL and SUPABASE_KEY
    
    Returns:
        Configured SupabaseVectorStore instance
    """
    
    # Try to get credentials from config
    if config_module:
        url = getattr(config_module, 'SUPABASE_URL', None)
        key = getattr(config_module, 'SUPABASE_KEY', None)
    else:
        # Try importing config
        try:
            import config
            url = getattr(config, 'SUPABASE_URL', None)
            key = getattr(config, 'SUPABASE_KEY', None)
        except ImportError:
            url = None
            key = None
    
    # Fallback to environment variables
    if not url or not key:
        url = os.getenv('SUPABASE_URL', 'https://dbtkffmwrjqmmevlhddk.supabase.co')
        key = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRidGtmZm13cmpxbW1ldmxoZGRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTY5MjE2OSwiZXhwIjoyMDcxMjY4MTY5fQ.MWljK5mWGq4uJvwz1qqNp5kLdRmDFuwsUphvT4lezbs')
    
    if not url or not key:
        raise ValueError("Supabase URL and key are required. Set SUPABASE_URL and SUPABASE_KEY in config or environment.")
    
    return SupabaseVectorStore(url, key, use_codebert=use_codebert)
