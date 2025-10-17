"""
Supabase Database Configuration and Connection Management
"""

import os
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseManager:
    """
    Manages Supabase database connections and operations
    """
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.url or not self.anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        # Create clients
        self.client: Client = create_client(self.url, self.anon_key)
        self.admin_client: Client = create_client(self.url, self.service_role_key) if self.service_role_key else None
        
        logger.info("Supabase clients initialized successfully")
    
    def test_connection(self) -> bool:
        """Test the Supabase connection"""
        try:
            # Test with a simple query
            result = self.client.table('jobs').select('id').limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False
    
    # Job Management
    def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job record"""
        try:
            job_data['created_at'] = datetime.utcnow().isoformat()
            job_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table('jobs').insert(job_data).execute()
            logger.info(f"Created job {job_data.get('id')} in Supabase")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Failed to create job: {str(e)}")
            raise
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a job by ID"""
        try:
            result = self.client.table('jobs').select('*').eq('id', job_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {str(e)}")
            return None
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update a job record"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.client.table('jobs').update(updates).eq('id', job_id).execute()
            logger.info(f"Updated job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {str(e)}")
            return False
    
    def get_jobs_by_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get jobs for a specific user"""
        try:
            result = self.client.table('jobs').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get jobs for user {user_id}: {str(e)}")
            return []
    
    # Document Management
    def create_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document record"""
        try:
            doc_data['created_at'] = datetime.utcnow().isoformat()
            result = self.client.table('documents').insert(doc_data).execute()
            logger.info(f"Created document {doc_data.get('filename')} in Supabase")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise
    
    def get_job_documents(self, job_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a job"""
        try:
            result = self.client.table('documents').select('*').eq('job_id', job_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get documents for job {job_id}: {str(e)}")
            return []
    
    # Feedback Management
    def create_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a feedback record"""
        try:
            feedback_data['created_at'] = datetime.utcnow().isoformat()
            result = self.client.table('user_feedback').insert(feedback_data).execute()
            logger.info(f"Created feedback for job {feedback_data.get('job_id')}")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Failed to create feedback: {str(e)}")
            raise
    
    def get_job_feedback(self, job_id: str) -> List[Dict[str, Any]]:
        """Get feedback for a specific job"""
        try:
            result = self.client.table('user_feedback').select('*').eq('job_id', job_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get feedback for job {job_id}: {str(e)}")
            return []
    
    # Analytics and Metrics
    def record_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Record a system metric"""
        try:
            metric_data['recorded_at'] = datetime.utcnow().isoformat()
            result = self.client.table('system_metrics').insert(metric_data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to record metric: {str(e)}")
            return False
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the last N days"""
        try:
            # Get job counts by status
            jobs_result = self.client.table('jobs').select('status').gte('created_at', 
                (datetime.utcnow() - timedelta(days=days)).isoformat()).execute()
            
            # Get feedback stats
            feedback_result = self.client.table('user_feedback').select('rating').gte('created_at',
                (datetime.utcnow() - timedelta(days=days)).isoformat()).execute()
            
            return {
                'total_jobs': len(jobs_result.data),
                'job_status_breakdown': self._count_by_field(jobs_result.data, 'status'),
                'average_rating': self._calculate_average_rating(feedback_result.data),
                'total_feedback': len(feedback_result.data)
            }
        except Exception as e:
            logger.error(f"Failed to get usage stats: {str(e)}")
            return {}
    
    def _count_by_field(self, data: List[Dict], field: str) -> Dict[str, int]:
        """Helper to count occurrences of field values"""
        counts = {}
        for item in data:
            value = item.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _calculate_average_rating(self, feedback_data: List[Dict]) -> float:
        """Helper to calculate average rating"""
        if not feedback_data:
            return 0.0
        
        ratings = [item.get('rating', 0) for item in feedback_data if item.get('rating')]
        return sum(ratings) / len(ratings) if ratings else 0.0

# Global instance
supabase_manager = SupabaseManager()
