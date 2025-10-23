#!/usr/bin/env python3
"""
Unified Semantic Search System for IMigrate
Handles document and metadata upload with RAG-based similarity search
"""
import json
import openai
from supabase import create_client, Client
from bs4 import BeautifulSoup
import sys
import os

# Add agentic-rag-IMigrate directory to path for config import
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agentic-rag-IMigrate')
if config_path not in sys.path:
    sys.path.insert(0, config_path)

try:
    from config import SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY
except ImportError as e:
    # Fallback to environment variables
    print(f"⚠️  Could not import config: {e}")
    print(f"   Using environment variables instead")
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
from pathlib import Path
import hashlib
from typing import List, Dict, Optional

# Embedding model - text-embedding-ada-002 (1536 dimensions)
EMBEDDING_MODEL = "text-embedding-ada-002"

class UnifiedSemanticSearch:
    def __init__(self):
        """Initialize the unified semantic search system"""
        self.supabase: Client = None
        self.uploaded_documents = {}  # Temporary memory for documents
        self.uploaded_metadata = {}   # Temporary memory for metadata
        
    def initialize_clients(self):
        """Initialize OpenAI and Supabase clients"""
        print("🔧 Initializing RAG search clients...")
        openai.api_key = OPENAI_API_KEY
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ RAG search clients initialized!")
    
    def extract_text_from_html(self, html_content: str) -> str:
        """Extract text content from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file types"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Handle different file types
            if file_path.suffix.lower() == '.html':
                return self.extract_text_from_html(content)
            else:
                return content
                
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
    
    def extract_overview_sections(self, text: str, max_words: int = 250) -> str:
        """Extract overview sections from text"""
        # Look for common overview patterns
        overview_patterns = [
            "API Overview", "Overview", "Introduction", "Summary", 
            "Process Flow Overview", "Integration Overview", "System Overview"
        ]
        
        overview_text = ""
        lines = text.split('\n')
        
        # Find overview sections
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            for pattern in overview_patterns:
                if pattern.lower() in line_lower:
                    # Extract content after the overview heading
                    overview_content = []
                    for j in range(i + 1, min(i + 20, len(lines))):
                        content_line = lines[j].strip()
                        if content_line and not content_line.lower().startswith(('##', '###', '**', '*', '-')):
                            overview_content.append(content_line)
                    
                    overview_text = ' '.join(overview_content)
                    break
            
            if overview_text:
                break
        
        # If no specific overview found, use first part of text
        if not overview_text:
            overview_text = text[:2000]
        
        # Limit to max_words
        words = overview_text.split()
        if len(words) > max_words:
            overview_text = ' '.join(words[:max_words]) + '...'
        
        return overview_text.strip()
    
    def extract_metadata_from_json(self, json_content: str) -> Dict:
        """Extract metadata from JSON blueprint file"""
        try:
            data = json.loads(json_content)
            metadata = {}
            
            if 'blueprint' in data:
                blueprint = data.get('blueprint', {})
                metadata = {
                    'id': blueprint.get('id', ''),
                    'name': blueprint.get('name', ''),
                    'description': blueprint.get('description', ''),
                    'components': blueprint.get('components', [])
                }
            elif 'endpoints' in data:
                endpoints = data.get('endpoints', [])
                if endpoints:
                    endpoint = endpoints[0]
                    metadata = {
                        'id': endpoint.get('id', ''),
                        'name': endpoint.get('name', ''),
                        'description': endpoint.get('description', ''),
                        'components': endpoint.get('components', [])
                    }
            elif 'id' in data or 'name' in data:
                metadata = {
                    'id': data.get('id', ''),
                    'name': data.get('name', ''),
                    'description': data.get('description', ''),
                    'components': data.get('components', [])
                }
            
            if not metadata:
                metadata = {'id': '', 'name': '', 'description': '', 'components': []}
            
            return metadata
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error extracting metadata: {e}")
    
    def create_metadata_description(self, metadata: Dict) -> str:
        """Create a comprehensive description from metadata, limited to 250 words"""
        id_text = metadata.get('id', '')
        name_text = metadata.get('name', '')
        desc_text = metadata.get('description', '')
        components = metadata.get('components', [])
        
        description_parts = []
        if name_text:
            description_parts.append(f"Integration: {name_text}")
        if desc_text:
            description_parts.append(f"Description: {desc_text}")
        if components:
            component_names = [comp.get('name', '') for comp in components if comp.get('name')]
            if component_names:
                description_parts.append(f"Components: {', '.join(component_names)}")
        if id_text:
            description_parts.append(f"ID: {id_text}")
        
        full_description = ' '.join(description_parts) if description_parts else "Integration flow metadata"
        if not full_description.strip():
            full_description = "Integration flow with metadata"
        
        words = full_description.split()
        if len(words) > 250:
            full_description = ' '.join(words[:250]) + '...'
        
        return full_description.strip()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI text-embedding-ada-002 (1536 dimensions)"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=[text]
                # Note: text-embedding-ada-002 always returns 1536 dimensions (no dimensions parameter)
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            raise
    
    def search_similar_flows(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """
        Search for similar integration flows using RAG
        Uses existing integration_flows table and search_similar_flows() function
        
        Args:
            query_text: Text to search for
            top_k: Number of results to return
            
        Returns:
            List of similar iFlows with similarity scores
        """
        print(f"🔍 RAG Search: '{query_text[:100]}...'")
        
        # Generate embedding for query
        try:
            query_embedding = self.generate_embedding(query_text)
        except Exception as e:
            print(f"❌ Error generating query embedding: {e}")
            raise
        
        # Search integration flows using existing Supabase RPC function
        # Table: integration_flows (id, name, description, embedding)
        try:
            iflow_results = self.supabase.rpc(
                'search_similar_flows',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': 0.1,  # Lowered from 0.3 to get more results
                    'match_count': top_k
                }
            ).execute()
            
            print(f"🔍 RPC Response: {type(iflow_results.data)} with {len(iflow_results.data) if iflow_results.data else 0} items")
            if iflow_results.data:
                print(f"   Sample result keys: {list(iflow_results.data[0].keys()) if len(iflow_results.data) > 0 else 'None'}")
            
            similar_flows = []
            for row in iflow_results.data if iflow_results.data else []:
                similar_flows.append({
                    'rank': len(similar_flows) + 1,
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'similarity_score': round(row['similarity'], 4)
                })
            
            print(f"✅ Found {len(similar_flows)} similar iFlows")
            return similar_flows
            
        except Exception as e:
            print(f"❌ Error searching integration flows: {e}")
            raise
    
    def upload_document(self, file_path: str, custom_name: Optional[str] = None) -> Dict:
        """Upload and process a document (stored in memory)"""
        print(f"📄 Processing document: {file_path}")
        
        # Extract text content
        try:
            text_content = self.extract_text_from_file(file_path)
            print(f"   Extracted {len(text_content)} characters")
        except Exception as e:
            raise Exception(f"Error extracting text: {e}")
        
        # Extract overview sections
        try:
            overview_text = self.extract_overview_sections(text_content)
            print(f"   Overview: {len(overview_text)} characters")
        except Exception as e:
            raise Exception(f"Error extracting overview: {e}")
        
        # Generate embedding
        try:
            embedding = self.generate_embedding(overview_text)
            print("   ✅ Generated embedding")
        except Exception as e:
            raise Exception(f"Error generating embedding: {e}")
        
        # Store in memory
        original_filename = Path(file_path).name
        filename_hash = hashlib.md5(original_filename.encode()).hexdigest()
        custom_name = custom_name or original_filename
        
        document_data = {
            'filename': filename_hash,
            'original_filename': original_filename,
            'custom_name': custom_name,
            'overview_text': overview_text,
            'embedding': embedding,
            'file_size': len(text_content)
        }
        
        self.uploaded_documents[filename_hash] = document_data
        
        # Search for similar flows
        try:
            similar_flows = self.search_similar_flows(overview_text)
        except Exception as e:
            raise Exception(f"Error searching similar flows: {e}")
        
        return {
            'document_id': filename_hash,
            'document': document_data,
            'similar_flows': similar_flows
        }
    
    def upload_metadata(self, file_path: str, custom_name: Optional[str] = None) -> Dict:
        """Upload and process metadata (stored in memory)"""
        print(f"📋 Processing metadata: {file_path}")
        
        # Extract metadata from JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_content = f.read()
            
            metadata = self.extract_metadata_from_json(json_content)
            print(f"   Metadata: {metadata.get('name', 'N/A')}")
        except Exception as e:
            raise Exception(f"Error extracting metadata: {e}")
        
        # Create description from metadata
        try:
            description_text = self.create_metadata_description(metadata)
            print(f"   Description: {len(description_text)} characters")
        except Exception as e:
            raise Exception(f"Error creating description: {e}")
        
        # Generate embedding
        try:
            embedding = self.generate_embedding(description_text)
            print("   ✅ Generated embedding")
        except Exception as e:
            raise Exception(f"Error generating embedding: {e}")
        
        # Store in memory
        original_filename = Path(file_path).name
        filename_hash = hashlib.md5(original_filename.encode()).hexdigest()
        custom_name = custom_name or original_filename
        
        metadata_data = {
            'filename': filename_hash,
            'original_filename': original_filename,
            'custom_name': custom_name,
            'metadata': metadata,
            'description_text': description_text,
            'embedding': embedding,
            'file_size': len(json_content)
        }
        
        self.uploaded_metadata[filename_hash] = metadata_data
        
        # Search for similar flows
        try:
            similar_flows = self.search_similar_flows(description_text)
        except Exception as e:
            raise Exception(f"Error searching similar flows: {e}")
        
        return {
            'metadata_id': filename_hash,
            'metadata_data': metadata_data,
            'similar_flows': similar_flows
        }
    
    def list_uploaded_content(self):
        """List all uploaded content in memory"""
        print("\n=== Uploaded Content in Memory ===")
        
        print(f"\nDocuments ({len(self.uploaded_documents)}):")
        for doc_id, doc in self.uploaded_documents.items():
            print(f"  - {doc['custom_name']} (ID: {doc_id[:8]}...)")
        
        print(f"\nMetadata ({len(self.uploaded_metadata)}):")
        for meta_id, meta in self.uploaded_metadata.items():
            print(f"  - {meta['custom_name']} (ID: {meta_id[:8]}...)")
    
    def clear_memory(self):
        """Clear all uploaded content from memory"""
        self.uploaded_documents.clear()
        self.uploaded_metadata.clear()
        print("✅ Memory cleared!")

