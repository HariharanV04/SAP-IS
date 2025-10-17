"""
Integrated Database and Storage Manager
Combines Supabase database with S3 storage and vector search
"""

import os
import logging
from typing import Optional, Dict, Any, List, BinaryIO
from datetime import datetime
import uuid
import json

from .supabase_manager import supabase_manager
from .s3_manager import s3_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedManager:
    """
    Unified manager for database operations, file storage, and vector search
    """
    
    def __init__(self):
        self.db = supabase_manager
        self.storage = s3_manager
        logger.info("Integrated manager initialized")
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all service connections"""
        return {
            'database': self.db.test_connection(),
            'storage': self.storage.test_connection()
        }
    
    # ==========================================
    # ENHANCED JOB MANAGEMENT
    # ==========================================
    
    def create_job_with_file(self, job_data: Dict[str, Any], file_obj: Optional[BinaryIO] = None, filename: Optional[str] = None) -> Dict[str, Any]:
        """Create a job and optionally upload associated file"""
        try:
            job_id = job_data.get('id', str(uuid.uuid4()))
            job_data['id'] = job_id
            
            # Upload file if provided
            if file_obj and filename:
                file_key = f"jobs/{job_id}/uploads/{filename}"
                file_url = self.storage.upload_file(file_obj, file_key, {
                    'job_id': job_id,
                    'upload_type': 'original_document'
                })
                
                if file_url:
                    job_data['upload_path'] = file_url
                    
                    # Create document record
                    doc_data = {
                        'job_id': job_id,
                        'filename': filename,
                        'document_type': 'upload',
                        'file_path': file_url,
                        'file_size': getattr(file_obj, 'content_length', None)
                    }
                    self.db.create_document(doc_data)
            
            # Create job in database
            job = self.db.create_job(job_data)
            
            # Track user activity
            if job_data.get('user_id'):
                self.db.create_user_activity(
                    job_data['user_id'],
                    'job_created',
                    {'job_id': job_id, 'platform': job_data.get('platform')}
                )
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to create job with file: {str(e)}")
            raise
    
    def update_job_with_results(self, job_id: str, updates: Dict[str, Any], result_files: Optional[Dict[str, BinaryIO]] = None) -> bool:
        """Update job and upload result files"""
        try:
            # Upload result files if provided
            if result_files:
                result_paths = {}
                for file_type, file_obj in result_files.items():
                    file_key = f"jobs/{job_id}/results/{file_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                    file_url = self.storage.upload_file(file_obj, file_key, {
                        'job_id': job_id,
                        'file_type': file_type,
                        'upload_type': 'result'
                    })
                    
                    if file_url:
                        result_paths[file_type] = file_url
                        
                        # Create document record for result
                        doc_data = {
                            'job_id': job_id,
                            'filename': f"{file_type}_result",
                            'document_type': 'result',
                            'file_path': file_url
                        }
                        self.db.create_document(doc_data)
                
                updates['results_path'] = json.dumps(result_paths)
            
            # Update job
            return self.db.update_job(job_id, updates)
            
        except Exception as e:
            logger.error(f"Failed to update job with results: {str(e)}")
            return False
    
    def get_job_with_files(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job with associated files and documents"""
        try:
            job = self.db.get_job(job_id)
            if not job:
                return None
            
            # Get associated documents
            documents = self.db.get_job_documents(job_id)
            job['documents'] = documents
            
            # Get job history
            history = self.db.get_job_history(job_id)
            job['history'] = history
            
            # Get feedback
            feedback = self.db.get_job_feedback(job_id)
            job['feedback'] = feedback
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to get job with files: {str(e)}")
            return None
    
    # ==========================================
    # DOCUMENT MANAGEMENT WITH VECTOR SEARCH
    # ==========================================
    
    def create_document_with_embedding(self, doc_data: Dict[str, Any], content: str, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """Create document with vector embedding for similarity search"""
        try:
            # If no embedding provided, you could generate one here using OpenAI or other embedding service
            # For now, we'll store the document without embedding if not provided
            
            doc_data['content'] = content
            return self.db.create_document(doc_data, embedding)
            
        except Exception as e:
            logger.error(f"Failed to create document with embedding: {str(e)}")
            raise
    
    def search_similar_documents(self, query_text: str, query_embedding: Optional[List[float]] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity"""
        try:
            if not query_embedding:
                # If no embedding provided, you could generate one here
                # For now, return empty results
                logger.warning("No query embedding provided for similarity search")
                return []
            
            return self.db.search_similar_documents(query_embedding, limit)
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {str(e)}")
            return []
    
    # ==========================================
    # FILE MANAGEMENT
    # ==========================================
    
    def upload_job_file(self, job_id: str, file_obj: BinaryIO, filename: str, file_type: str = 'general') -> Optional[str]:
        """Upload a file associated with a job"""
        try:
            file_key = f"jobs/{job_id}/{file_type}/{filename}"
            file_url = self.storage.upload_file(file_obj, file_key, {
                'job_id': job_id,
                'file_type': file_type
            })
            
            if file_url:
                # Create document record
                doc_data = {
                    'job_id': job_id,
                    'filename': filename,
                    'document_type': file_type,
                    'file_path': file_url
                }
                self.db.create_document(doc_data)
            
            return file_url
            
        except Exception as e:
            logger.error(f"Failed to upload job file: {str(e)}")
            return None
    
    def download_job_file(self, job_id: str, filename: str) -> Optional[bytes]:
        """Download a file associated with a job"""
        try:
            # Find the document record
            documents = self.db.get_job_documents(job_id)
            target_doc = None
            
            for doc in documents:
                if doc['filename'] == filename:
                    target_doc = doc
                    break
            
            if not target_doc:
                logger.error(f"Document {filename} not found for job {job_id}")
                return None
            
            # Extract key from file path
            file_path = target_doc['file_path']
            if file_path.startswith('http'):
                # S3 URL - extract key
                file_key = file_path.split('/')[-1]  # Simplified - you might need more sophisticated parsing
            else:
                # Local path
                file_key = file_path
            
            return self.storage.download_file(file_key)
            
        except Exception as e:
            logger.error(f"Failed to download job file: {str(e)}")
            return None
    
    def get_file_download_url(self, job_id: str, filename: str, expiration: int = 3600) -> Optional[str]:
        """Get a presigned URL for file download"""
        try:
            documents = self.db.get_job_documents(job_id)
            target_doc = None
            
            for doc in documents:
                if doc['filename'] == filename:
                    target_doc = doc
                    break
            
            if not target_doc:
                return None
            
            file_path = target_doc['file_path']
            if file_path.startswith('http'):
                # S3 URL - generate presigned URL
                file_key = file_path.split('/')[-1]  # Simplified
                return self.storage.generate_presigned_url(file_key, expiration)
            else:
                # Local file - return path
                return file_path
                
        except Exception as e:
            logger.error(f"Failed to get file download URL: {str(e)}")
            return None
    
    # ==========================================
    # ANALYTICS AND REPORTING
    # ==========================================
    
    def get_comprehensive_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        try:
            # Get database stats
            db_stats = self.db.get_usage_stats(days)
            
            # Get storage stats
            storage_files = self.storage.list_files()
            total_storage_size = sum(f.get('size', 0) for f in storage_files)
            
            # Combine stats
            return {
                **db_stats,
                'storage': {
                    'total_files': len(storage_files),
                    'total_size_bytes': total_storage_size,
                    'total_size_mb': round(total_storage_size / (1024 * 1024), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive stats: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, int]:
        """Clean up old data from database and storage"""
        try:
            # This would implement cleanup logic
            # For now, return placeholder
            return {
                'jobs_deleted': 0,
                'files_deleted': 0,
                'storage_freed_mb': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {str(e)}")
            return {}

# Global instance
integrated_manager = IntegratedManager()
