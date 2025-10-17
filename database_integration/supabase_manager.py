"""
Supabase Database Manager with Vector Search and History Tables
"""

import os
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from datetime import datetime, timedelta
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseManager:
    """
    Manages Supabase database with vector search and history tracking
    """

    def __init__(self, schema_name: str = 'is_migration'):
        self.url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.schema_name = schema_name

        # For testing/development, allow dummy values
        if not self.url or not self.anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")

        # Check for dummy/test configuration
        if self.url == 'https://dummy.supabase.co' or self.anon_key == 'dummy_key':
            logger.warning("Using dummy Supabase configuration - database features disabled")
            self.client = None
            self.admin_client = None
            return

        # Create clients
        self.client: Client = create_client(self.url, self.anon_key)
        self.admin_client: Client = create_client(self.url, self.service_role_key) if self.service_role_key else None

        logger.info(f"Supabase manager initialized successfully with schema: {self.schema_name}")

    def _get_table(self, table_name: str):
        """Get table reference - use public schema due to PostgREST limitations"""
        # Temporary workaround: Use existing tables in public schema
        return self.client.table(table_name)

    def test_connection(self) -> bool:
        """Test the Supabase connection"""
        try:
            # Test by trying to access the jobs table directly
            # This will work if the schema is properly set up
            result = self._get_table('jobs').select('*').limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")

            # Try a basic connection test to see if Supabase is reachable
            try:
                # Test basic connectivity - this should work even without our schema
                result = self.client.table('auth.users').select('id').limit(0).execute()
                logger.warning("Basic Supabase connection works, but is_migration schema may not be set up properly")
                logger.warning("Please ensure you've run the is_migration_schema.sql script in Supabase SQL Editor")
                return False
            except Exception as e2:
                logger.error(f"Complete Supabase connection failure: {str(e2)}")
                return False
    
    # ==========================================
    # JOB MANAGEMENT
    # ==========================================
    
    def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job record"""
        try:
            job_data['id'] = job_data.get('id', str(uuid.uuid4()))
            job_data['created_at'] = datetime.utcnow().isoformat()
            job_data['updated_at'] = datetime.utcnow().isoformat()
            job_data['status'] = job_data.get('status', 'pending')
            
            result = self._get_table('jobs').insert(job_data).execute()
            logger.info(f"Created job {job_data['id']} in Supabase")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Failed to create job: {str(e)}")
            raise
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a job by ID"""
        try:
            result = self._get_table('jobs').select('*').eq('id', job_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {str(e)}")
            return None
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update a job record and create history entry"""
        try:
            # Get current job data for history
            current_job = self.get_job(job_id)
            if current_job:
                # Create history entry
                self.create_job_history(job_id, current_job, updates)
            
            # Update job
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self._get_table('jobs').update(updates).eq('id', job_id).execute()
            logger.info(f"Updated job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {str(e)}")
            return False

    def get_user_jobs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get jobs for a specific user"""
        try:
            result = self._get_table('jobs').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get jobs for user {user_id}: {str(e)}")
            return []
    
    # ==========================================
    # DOCUMENT MANAGEMENT WITH VECTORS
    # ==========================================
    
    def create_document(self, doc_data: Dict[str, Any], embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """Create a document record with optional vector embedding"""
        try:
            doc_data['id'] = doc_data.get('id', str(uuid.uuid4()))
            doc_data['created_at'] = datetime.utcnow().isoformat()
            
            if embedding:
                doc_data['embedding'] = embedding
            
            result = self._get_table('documents').insert(doc_data).execute()
            logger.info(f"Created document {doc_data.get('filename')} in Supabase")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise

    def search_similar_documents(self, query_embedding: List[float], limit: int = 10, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity"""
        try:
            # Use Supabase's vector similarity search
            result = self.client.rpc('search_documents', {
                'query_embedding': query_embedding,
                'match_threshold': similarity_threshold,
                'match_count': limit
            }).execute()

            return result.data or []
        except Exception as e:
            logger.error(f"Failed to search similar documents: {str(e)}")
            return []

    def get_job_documents(self, job_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a job"""
        try:
            result = self._get_table('documents').select('*').eq('job_id', job_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get documents for job {job_id}: {str(e)}")
            return []
    
    # ==========================================
    # HISTORY TRACKING
    # ==========================================
    
    def create_job_history(self, job_id: str, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """Create a job history entry"""
        try:
            history_data = {
                'id': str(uuid.uuid4()),
                'job_id': job_id,
                'old_data': old_data,
                'new_data': new_data,
                'changed_fields': list(new_data.keys()),
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self._get_table('job_history').insert(history_data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to create job history: {str(e)}")
            return False

    def get_job_history(self, job_id: str) -> List[Dict[str, Any]]:
        """Get history for a specific job"""
        try:
            result = self._get_table('job_history').select('*').eq('job_id', job_id).order('created_at', desc=True).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get job history for {job_id}: {str(e)}")
            return []
    
    def create_user_activity(self, user_id: str, activity_type: str, activity_data: Dict[str, Any]) -> bool:
        """Track user activity"""
        try:
            activity = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'activity_type': activity_type,
                'activity_data': activity_data,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self._get_table('user_activity').insert(activity).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to create user activity: {str(e)}")
            return False

    def get_user_activity(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user activity history"""
        try:
            result = self._get_table('user_activity').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get user activity for {user_id}: {str(e)}")
            return []
    
    # ==========================================
    # FEEDBACK SYSTEM
    # ==========================================
    
    def create_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a feedback record"""
        try:
            feedback_data['id'] = feedback_data.get('id', str(uuid.uuid4()))
            feedback_data['created_at'] = datetime.utcnow().isoformat()
            
            result = self._get_table('user_feedback').insert(feedback_data).execute()
            logger.info(f"Created feedback for job {feedback_data.get('job_id')}")
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Failed to create feedback: {str(e)}")
            raise

    def get_job_feedback(self, job_id: str) -> List[Dict[str, Any]]:
        """Get feedback for a specific job"""
        try:
            result = self._get_table('user_feedback').select('*').eq('job_id', job_id).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get feedback for job {job_id}: {str(e)}")
            return []
    
    # ==========================================
    # ANALYTICS AND METRICS
    # ==========================================
    
    def record_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Record a system metric"""
        try:
            metric_data['id'] = str(uuid.uuid4())
            metric_data['recorded_at'] = datetime.utcnow().isoformat()
            
            result = self._get_table('system_metrics').insert(metric_data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to record metric: {str(e)}")
            return False

    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the last N days"""
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            # Get job counts
            jobs_result = self._get_table('jobs').select('status').gte('created_at', cutoff_date).execute()

            # Get feedback stats
            feedback_result = self._get_table('user_feedback').select('rating').gte('created_at', cutoff_date).execute()
            
            return {
                'total_jobs': len(jobs_result.data),
                'job_status_breakdown': self._count_by_field(jobs_result.data, 'status'),
                'average_rating': self._calculate_average_rating(feedback_result.data),
                'total_feedback': len(feedback_result.data),
                'period_days': days
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
