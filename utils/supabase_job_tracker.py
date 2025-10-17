"""
Supabase Job Tracker
Utility for tracking iFlow generation jobs in Supabase database
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)


class SupabaseJobTracker:
    """
    Track iFlow generation jobs in Supabase database
    Provides real-time job status updates for UI
    """

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize Supabase client

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service role key
        """
        # Use provided credentials or fall back to environment variables
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key are required")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase Job Tracker initialized")

    # ========================================================================
    # JOB CRUD OPERATIONS
    # ========================================================================

    def create_job(
        self,
        job_id: str,
        platform: str,
        source_file_name: str,
        source_file_size: int = None,
        user_id: str = None,
        llm_provider: str = 'anthropic',
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Create a new iFlow generation job

        Args:
            job_id: Unique job identifier (UUID)
            platform: Platform type ('boomi', 'mulesoft', 'generic')
            source_file_name: Name of uploaded file
            source_file_size: Size of uploaded file in bytes
            user_id: User who created the job
            llm_provider: LLM provider used ('anthropic', 'openai', 'gemini')
            metadata: Additional metadata

        Returns:
            Created job data
        """
        try:
            job_data = {
                'job_id': job_id,
                'platform': platform,
                'source_file_name': source_file_name,
                'source_file_size': source_file_size,
                'user_id': user_id,
                'llm_provider': llm_provider,
                'status': 'pending',
                'progress': 0,
                'current_step': 'upload',
                'metadata': metadata or {}
            }

            result = self.client.table('iflow_jobs').insert(job_data).execute()
            logger.info(f"Created job {job_id}")
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error creating job {job_id}: {e}")
            raise

    def update_job_status(
        self,
        job_id: str,
        status: str,
        progress: int = None,
        current_step: str = None,
        error_message: str = None
    ) -> Dict[str, Any]:
        """
        Update job status and progress

        Args:
            job_id: Job identifier
            status: New status ('pending', 'processing', 'analyzing', 'generating', 'completed', 'failed')
            progress: Progress percentage (0-100)
            current_step: Current step name
            error_message: Error message if failed

        Returns:
            Updated job data
        """
        try:
            update_data = {'status': status}

            if progress is not None:
                update_data['progress'] = progress
            if current_step:
                update_data['current_step'] = current_step
            if error_message:
                update_data['error_message'] = error_message

            # Set timestamps based on status
            if status == 'processing' or status == 'analyzing':
                update_data['started_at'] = datetime.utcnow().isoformat()
            elif status in ['completed', 'failed', 'cancelled']:
                update_data['completed_at'] = datetime.utcnow().isoformat()

            result = self.client.table('iflow_jobs').update(update_data).eq('job_id', job_id).execute()
            logger.info(f"Updated job {job_id} status to {status}")
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error updating job {job_id}: {e}")
            raise

    def update_job_documentation(
        self,
        job_id: str,
        documentation_text: str,
        documentation_html: str = None
    ) -> Dict[str, Any]:
        """
        Update job with generated documentation

        Args:
            job_id: Job identifier
            documentation_text: Markdown documentation
            documentation_html: HTML documentation

        Returns:
            Updated job data
        """
        try:
            update_data = {
                'generated_documentation': documentation_text,
                'documentation_html': documentation_html,
                'status': 'documentation_ready',
                'progress': 40
            }

            result = self.client.table('iflow_jobs').update(update_data).eq('job_id', job_id).execute()
            logger.info(f"Updated job {job_id} with documentation")
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error updating job documentation {job_id}: {e}")
            raise

    def update_job_iflow(
        self,
        job_id: str,
        iflow_name: str,
        iflow_description: str,
        generation_method: str,
        iflow_zip_url: str = None,
        components: List[Dict] = None,
        rag_stats: Dict = None
    ) -> Dict[str, Any]:
        """
        Update job with iFlow generation results

        Args:
            job_id: Job identifier
            iflow_name: Name of generated iFlow
            iflow_description: Description
            generation_method: 'template', 'rag', or 'hybrid'
            iflow_zip_url: URL to download ZIP file
            components: List of component details
            rag_stats: RAG statistics (retrievals_count, sources_used)

        Returns:
            Updated job data
        """
        try:
            update_data = {
                'iflow_name': iflow_name,
                'iflow_description': iflow_description,
                'generation_method': generation_method,
                'iflow_zip_url': iflow_zip_url,
                'components_json': components,
                'total_components': len(components) if components else 0,
                'status': 'completed',
                'progress': 100
            }

            if rag_stats:
                update_data['rag_retrievals_count'] = rag_stats.get('retrievals_count', 0)
                update_data['rag_sources_used'] = rag_stats.get('sources_used', 0)

            result = self.client.table('iflow_jobs').update(update_data).eq('job_id', job_id).execute()
            logger.info(f"Updated job {job_id} with iFlow results")
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error updating job iFlow {job_id}: {e}")
            raise

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job details

        Args:
            job_id: Job identifier

        Returns:
            Job data or None
        """
        try:
            result = self.client.table('iflow_jobs').select('*').eq('job_id', job_id).execute()
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error getting job {job_id}: {e}")
            return None

    def get_recent_jobs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent jobs

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of job data
        """
        try:
            result = self.client.table('iflow_jobs')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error getting recent jobs: {e}")
            return []

    # ========================================================================
    # COMPONENT TRACKING
    # ========================================================================

    def add_component(
        self,
        job_id: str,
        component_type: str,
        component_name: str,
        component_order: int,
        source: str = 'template',
        rag_similarity_score: float = None,
        rag_document_name: str = None,
        configuration: Dict = None,
        xml_content: str = None
    ) -> Dict[str, Any]:
        """
        Add a component to the job

        Args:
            job_id: Job identifier
            component_type: Type of component
            component_name: Component name
            component_order: Order in iFlow (1, 2, 3, ...)
            source: 'template', 'rag', 'authoritative', 'user_specified'
            rag_similarity_score: Similarity score if from RAG (0.0-1.0)
            rag_document_name: Source document name from RAG
            configuration: Component configuration
            xml_content: Component XML

        Returns:
            Created component data
        """
        try:
            component_data = {
                'job_id': job_id,
                'component_type': component_type,
                'component_name': component_name,
                'component_order': component_order,
                'source': source,
                'rag_similarity_score': rag_similarity_score,
                'rag_document_name': rag_document_name,
                'configuration': configuration,
                'xml_content': xml_content
            }

            result = self.client.table('iflow_components').insert(component_data).execute()
            logger.debug(f"Added component {component_name} to job {job_id}")
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error adding component to job {job_id}: {e}")
            raise

    def get_job_components(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Get all components for a job

        Args:
            job_id: Job identifier

        Returns:
            List of components
        """
        try:
            result = self.client.table('iflow_components')\
                .select('*')\
                .eq('job_id', job_id)\
                .order('component_order')\
                .execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error getting components for job {job_id}: {e}")
            return []

    # ========================================================================
    # RAG RETRIEVAL TRACKING
    # ========================================================================

    def log_rag_retrieval(
        self,
        job_id: str,
        retrieval_type: str,
        search_query: str,
        results: List[Dict],
        retrieval_location: str = None,
        component_type_searched: str = None,
        retrieval_time_ms: int = None
    ) -> Dict[str, Any]:
        """
        Log a RAG retrieval operation

        Args:
            job_id: Job identifier
            retrieval_type: 'vector_search', 'pattern_search', 'graph_query', 'hybrid'
            search_query: Search query used
            results: List of retrieved documents
            retrieval_location: Code location where retrieval happened
            component_type_searched: Component type being searched for
            retrieval_time_ms: Retrieval time in milliseconds

        Returns:
            Created retrieval log data
        """
        try:
            retrieval_data = {
                'job_id': job_id,
                'retrieval_type': retrieval_type,
                'search_query': search_query,
                'results_count': len(results),
                'results': results,
                'retrieval_location': retrieval_location,
                'component_type_searched': component_type_searched,
                'retrieval_time_ms': retrieval_time_ms
            }

            result = self.client.table('rag_retrievals').insert(retrieval_data).execute()
            logger.debug(f"Logged RAG retrieval for job {job_id}")
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error logging RAG retrieval for job {job_id}: {e}")
            raise

    def get_job_retrievals(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Get all RAG retrievals for a job

        Args:
            job_id: Job identifier

        Returns:
            List of retrieval logs
        """
        try:
            result = self.client.table('rag_retrievals')\
                .select('*')\
                .eq('job_id', job_id)\
                .order('created_at')\
                .execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error getting retrievals for job {job_id}: {e}")
            return []

    # ========================================================================
    # LOGGING
    # ========================================================================

    def add_log(
        self,
        job_id: str,
        log_level: str,
        log_message: str,
        log_category: str = None,
        step_name: str = None,
        details: Dict = None
    ) -> Dict[str, Any]:
        """
        Add a log entry for a job

        Args:
            job_id: Job identifier
            log_level: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
            log_message: Log message
            log_category: Category (e.g., 'parsing', 'generation', 'rag_retrieval')
            step_name: Step name
            details: Additional details

        Returns:
            Created log entry
        """
        try:
            log_data = {
                'job_id': job_id,
                'log_level': log_level,
                'log_message': log_message,
                'log_category': log_category,
                'step_name': step_name,
                'details': details
            }

            result = self.client.table('iflow_generation_logs').insert(log_data).execute()
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error adding log for job {job_id}: {e}")
            raise

    def get_job_logs(self, job_id: str, log_level: str = None) -> List[Dict[str, Any]]:
        """
        Get logs for a job

        Args:
            job_id: Job identifier
            log_level: Optional filter by log level

        Returns:
            List of log entries
        """
        try:
            query = self.client.table('iflow_generation_logs').select('*').eq('job_id', job_id)

            if log_level:
                query = query.eq('log_level', log_level)

            result = query.order('created_at').execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error getting logs for job {job_id}: {e}")
            return []

    # ========================================================================
    # STATISTICS & ANALYTICS
    # ========================================================================

    def get_job_summary(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete job summary with all related data

        Args:
            job_id: Job identifier

        Returns:
            Complete job summary
        """
        try:
            # Get job details
            job = self.get_job(job_id)
            if not job:
                return None

            # Get components
            components = self.get_job_components(job_id)

            # Get retrievals
            retrievals = self.get_job_retrievals(job_id)

            # Get error logs
            error_logs = self.get_job_logs(job_id, log_level='ERROR')

            return {
                'job': job,
                'components': components,
                'retrievals': retrievals,
                'error_logs': error_logs,
                'statistics': {
                    'total_components': len(components),
                    'total_retrievals': len(retrievals),
                    'error_count': len(error_logs),
                    'rag_components': len([c for c in components if c.get('source') == 'rag']),
                    'template_components': len([c for c in components if c.get('source') == 'template'])
                }
            }

        except Exception as e:
            logger.error(f"Error getting job summary for {job_id}: {e}")
            return None


# Singleton instance
_job_tracker_instance: Optional[SupabaseJobTracker] = None


def get_job_tracker(supabase_url: str = None, supabase_key: str = None) -> SupabaseJobTracker:
    """
    Get or create SupabaseJobTracker singleton instance

    Args:
        supabase_url: Supabase project URL
        supabase_key: Supabase service role key

    Returns:
        SupabaseJobTracker instance
    """
    global _job_tracker_instance

    if _job_tracker_instance is None:
        _job_tracker_instance = SupabaseJobTracker(supabase_url, supabase_key)

    return _job_tracker_instance
