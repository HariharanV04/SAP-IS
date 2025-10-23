#!/usr/bin/env python3
"""
RAG-Based Similarity Search Integration
Replaces GitHub search with RAG-based semantic search for iFlows
Integrated into app directory for documentation generation workflow
"""
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# Ensure current directory is in path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from unified_semantic_search import UnifiedSemanticSearch
    RAG_AVAILABLE = True
    print("✅ RAG Search module loaded successfully")
except ImportError as e:
    print(f"⚠️  RAG Search not available: {e}")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Script directory: {Path(__file__).parent}")
    RAG_AVAILABLE = False

class RAGSimilaritySearch:
    """
    RAG-based similarity search for integration flows
    Integrates with IMigrate agent for intelligent iFlow discovery
    """
    
    def __init__(self):
        """Initialize the RAG similarity search"""
        self.search_system = None
        self.initialized = False
        
    def initialize(self):
        """Initialize the unified semantic search system"""
        if not RAG_AVAILABLE:
            print("❌ RAG system not available")
            return False
            
        try:
            print("🔧 Initializing RAG Similarity Search...")
            self.search_system = UnifiedSemanticSearch()
            self.search_system.initialize_clients()
            self.initialized = True
            print("✅ RAG Similarity Search initialized!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize RAG: {e}")
            return False
    
    def search_similar_flows(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """
        Search for similar integration flows using RAG
        
        Args:
            query_text: Description or requirements to search for
            top_k: Number of results to return
            
        Returns:
            List of similar iFlows with metadata and similarity scores
        """
        if not RAG_AVAILABLE:
            print("❌ RAG system not available")
            return []
            
        if not self.initialized:
            if not self.initialize():
                return []
        
        try:
            print(f"🔍 Searching for similar iFlows: '{query_text[:100]}...'")
            similar_flows = self.search_system.search_similar_flows(query_text, top_k)
            
            # Format results for agent usage
            formatted_results = []
            for flow in similar_flows:
                formatted_results.append({
                    'rank': flow['rank'],
                    'id': flow['id'],
                    'name': flow['name'],
                    'description': flow['description'],
                    'similarity_score': flow['similarity_score'],
                    'quality': self._determine_quality(flow['similarity_score']),
                    'type': 'SAP_Integration_Flow'
                })
            
            print(f"✅ Found {len(formatted_results)} similar iFlows")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching similar flows: {e}")
            return []
    
    def process_documentation(self, documentation_text: str, top_k: int = 10) -> Dict:
        """
        Process documentation and find similar iFlows
        
        Args:
            documentation_text: Generated documentation text
            top_k: Number of results to return
            
        Returns:
            Dictionary with search results and recommendations
        """
        if not self.initialized:
            if not self.initialize():
                return {'status': 'error', 'message': 'Failed to initialize RAG'}
        
        try:
            # Search for similar flows
            similar_flows = self.search_similar_flows(documentation_text, top_k)
            
            # Generate match report
            report = self.generate_match_report(similar_flows)
            
            return {
                'status': 'success',
                'similar_flows': similar_flows,
                'match_report': report,
                'total_found': len(similar_flows)
            }
            
        except Exception as e:
            print(f"❌ Error processing documentation: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_iflow_details(self, iflow_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific iFlow
        
        Args:
            iflow_id: iFlow ID to fetch
            
        Returns:
            iFlow details or None
        """
        if not self.initialized:
            if not self.initialize():
                return None
        
        try:
            result = self.search_system.supabase.table('integration_flows')\
                .select('*')\
                .eq('id', iflow_id)\
                .execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Error fetching iFlow details: {e}")
            return None
    
    def _determine_quality(self, similarity_score: float) -> str:
        """Determine match quality based on similarity score"""
        if similarity_score >= 0.8:
            return 'High'
        elif similarity_score >= 0.6:
            return 'Medium'
        else:
            return 'Low'
    
    def generate_match_report(self, search_results: List[Dict]) -> Dict:
        """
        Generate integration match report
        
        Args:
            search_results: List of search results
            
        Returns:
            Match report with statistics and recommendations
        """
        if not search_results:
            return {
                'total_results': 0,
                'high_quality_matches': 0,
                'medium_quality_matches': 0,
                'low_quality_matches': 0,
                'recommendations': [],
                'best_match': None
            }
        
        high_quality = [r for r in search_results if r['quality'] == 'High']
        medium_quality = [r for r in search_results if r['quality'] == 'Medium']
        low_quality = [r for r in search_results if r['quality'] == 'Low']
        
        recommendations = []
        best_match = search_results[0] if search_results else None
        
        if high_quality:
            recommendations.append({
                'type': 'high_confidence',
                'message': f"Found {len(high_quality)} high-confidence matches (>80% similarity)",
                'action': f"Top match: '{best_match['name']}' - Consider using as reference",
                'confidence': 'High'
            })
        
        if medium_quality:
            recommendations.append({
                'type': 'moderate_confidence',
                'message': f"Found {len(medium_quality)} moderate matches (60-80% similarity)",
                'action': "Review these matches for partial patterns you can adapt",
                'confidence': 'Medium'
            })
        
        if not high_quality and not medium_quality:
            recommendations.append({
                'type': 'low_confidence',
                'message': "No high-confidence matches found",
                'action': "Generate iFlow from scratch based on documentation",
                'confidence': 'Low'
            })
        
        return {
            'total_results': len(search_results),
            'high_quality_matches': len(high_quality),
            'medium_quality_matches': len(medium_quality),
            'low_quality_matches': len(low_quality),
            'recommendations': recommendations,
            'best_match': best_match,
            'avg_similarity': sum(r['similarity_score'] for r in search_results) / len(search_results) if search_results else 0
        }
    
    def format_results_for_agent(self, search_results: List[Dict]) -> str:
        """
        Format search results as context for the agent
        
        Args:
            search_results: List of search results
            
        Returns:
            Formatted string for agent context
        """
        if not search_results:
            return "No similar iFlows found in the knowledge base."
        
        context = "📚 **Similar Integration Flows Found:**\n\n"
        
        for result in search_results[:5]:  # Top 5 results
            context += f"**{result['rank']}. {result['name']}** (Similarity: {result['similarity_score']*100:.1f}%)\n"
            context += f"   Quality: {result['quality']}\n"
            context += f"   Description: {result['description'][:200]}...\n\n"
        
        return context

# Global instance
_rag_search = None

def get_rag_search() -> RAGSimilaritySearch:
    """Get or create the global RAG search instance"""
    global _rag_search
    if _rag_search is None:
        _rag_search = RAGSimilaritySearch()
        _rag_search.initialize()
    return _rag_search

def search_similar_iflows(documentation: str, top_k: int = 10) -> List[Dict]:
    """
    Convenience function to search for similar iFlows
    
    Args:
        documentation: Documentation text to search for
        top_k: Number of results
        
    Returns:
        List of similar iFlows
    """
    rag_search = get_rag_search()
    return rag_search.search_similar_flows(documentation, top_k)

if __name__ == "__main__":
    # Test the RAG similarity search
    print("="*60)
    print("🧪 Testing RAG Similarity Search")
    print("="*60)
    
    rag = RAGSimilaritySearch()
    if rag.initialize():
        # Test search
        test_query = "Integration flow that polls SFTP server every 5 minutes and posts data to SAP OData service"
        results = rag.search_similar_flows(test_query, top_k=5)
        
        if results:
            print(f"\n✅ Found {len(results)} similar iFlows:")
            for result in results:
                print(f"   {result['rank']}. {result['name']} ({result['similarity_score']*100:.1f}%)")
        else:
            print("\n⚠️  No results found")
    else:
        print("❌ Failed to initialize RAG search")

