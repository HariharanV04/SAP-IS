"""
S3 Storage Manager for File Storage
Ready for configuration when S3 details are provided
"""

import os
import logging
from typing import Optional, Dict, Any, List, BinaryIO
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime, timedelta
import uuid
import mimetypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3Manager:
    """
    Manages S3 file storage operations
    """
    
    def __init__(self):
        # S3 Configuration (supports both AWS S3 and CF ObjectStore)
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.endpoint_url = os.getenv('S3_ENDPOINT_URL')  # For CF ObjectStore

        # Initialize S3 client if credentials are available
        self.s3_client = None
        self.s3_enabled = False

        if self.aws_access_key_id and self.aws_secret_access_key and self.bucket_name:
            try:
                # Configure S3 client (works with both AWS S3 and CF ObjectStore)
                client_config = {
                    'aws_access_key_id': self.aws_access_key_id,
                    'aws_secret_access_key': self.aws_secret_access_key,
                    'region_name': self.aws_region
                }

                # Add endpoint URL for CF ObjectStore
                if self.endpoint_url:
                    client_config['endpoint_url'] = f"https://{self.endpoint_url}"
                    logger.info(f"Using custom S3 endpoint: {self.endpoint_url}")

                self.s3_client = boto3.client('s3', **client_config)
                self.s3_enabled = True
                logger.info("S3 client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {str(e)}")
        else:
            logger.info("S3 credentials not provided - using local storage fallback")
    
    def test_connection(self) -> bool:
        """Test S3 connection and bucket access"""
        if not self.s3_enabled:
            return False
        
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info("S3 connection test successful")
            return True
        except Exception as e:
            logger.error(f"S3 connection test failed: {str(e)}")
            return False
    
    def upload_file(self, file_obj: BinaryIO, key: str, metadata: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Upload a file to S3 or local storage
        Returns the file URL/path
        """
        if self.s3_enabled:
            return self._upload_to_s3(file_obj, key, metadata)
        else:
            return self._upload_to_local(file_obj, key, metadata)
    
    def _upload_to_s3(self, file_obj: BinaryIO, key: str, metadata: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Upload file to S3"""
        try:
            # Determine content type
            content_type, _ = mimetypes.guess_type(key)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': key,
                'Body': file_obj,
                'ContentType': content_type
            }
            
            if metadata:
                upload_params['Metadata'] = metadata
            
            # Upload file
            self.s3_client.upload_fileobj(**upload_params)
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{key}"
            logger.info(f"File uploaded to S3: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            return None
    
    def _upload_to_local(self, file_obj: BinaryIO, key: str, metadata: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Upload file to local storage as fallback"""
        try:
            # Create local storage directory
            local_storage_path = os.getenv('LOCAL_STORAGE_PATH', 'storage')
            os.makedirs(local_storage_path, exist_ok=True)
            
            # Create full file path
            file_path = os.path.join(local_storage_path, key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_obj.read())
            
            logger.info(f"File uploaded to local storage: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to upload file to local storage: {str(e)}")
            return None
    
    def download_file(self, key: str) -> Optional[bytes]:
        """Download a file from S3 or local storage"""
        if self.s3_enabled:
            return self._download_from_s3(key)
        else:
            return self._download_from_local(key)
    
    def _download_from_s3(self, key: str) -> Optional[bytes]:
        """Download file from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Failed to download file from S3: {str(e)}")
            return None
    
    def _download_from_local(self, key: str) -> Optional[bytes]:
        """Download file from local storage"""
        try:
            local_storage_path = os.getenv('LOCAL_STORAGE_PATH', 'storage')
            file_path = os.path.join(local_storage_path, key)
            
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to download file from local storage: {str(e)}")
            return None
    
    def delete_file(self, key: str) -> bool:
        """Delete a file from S3 or local storage"""
        if self.s3_enabled:
            return self._delete_from_s3(key)
        else:
            return self._delete_from_local(key)
    
    def _delete_from_s3(self, key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"File deleted from S3: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            return False
    
    def _delete_from_local(self, key: str) -> bool:
        """Delete file from local storage"""
        try:
            local_storage_path = os.getenv('LOCAL_STORAGE_PATH', 'storage')
            file_path = os.path.join(local_storage_path, key)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted from local storage: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file from local storage: {str(e)}")
            return False
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """Generate a presigned URL for file access"""
        if not self.s3_enabled:
            # For local storage, return the file path
            local_storage_path = os.getenv('LOCAL_STORAGE_PATH', 'storage')
            return os.path.join(local_storage_path, key)
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None
    
    def list_files(self, prefix: str = '') -> List[Dict[str, Any]]:
        """List files in S3 bucket or local storage"""
        if self.s3_enabled:
            return self._list_s3_files(prefix)
        else:
            return self._list_local_files(prefix)
    
    def _list_s3_files(self, prefix: str) -> List[Dict[str, Any]]:
        """List files in S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag']
                })
            
            return files
        except Exception as e:
            logger.error(f"Failed to list S3 files: {str(e)}")
            return []
    
    def _list_local_files(self, prefix: str) -> List[Dict[str, Any]]:
        """List files in local storage"""
        try:
            local_storage_path = os.getenv('LOCAL_STORAGE_PATH', 'storage')
            search_path = os.path.join(local_storage_path, prefix)
            
            files = []
            if os.path.exists(search_path):
                for root, dirs, filenames in os.walk(search_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(file_path, local_storage_path)
                        stat = os.stat(file_path)
                        
                        files.append({
                            'key': relative_path.replace('\\', '/'),  # Normalize path separators
                            'size': stat.st_size,
                            'last_modified': datetime.fromtimestamp(stat.st_mtime),
                            'path': file_path
                        })
            
            return files
        except Exception as e:
            logger.error(f"Failed to list local files: {str(e)}")
            return []
    
    def get_file_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        if self.s3_enabled:
            return self._get_s3_file_info(key)
        else:
            return self._get_local_file_info(key)
    
    def _get_s3_file_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get S3 file metadata"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return {
                'key': key,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response['ContentType'],
                'metadata': response.get('Metadata', {})
            }
        except Exception as e:
            logger.error(f"Failed to get S3 file info: {str(e)}")
            return None
    
    def _get_local_file_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get local file metadata"""
        try:
            local_storage_path = os.getenv('LOCAL_STORAGE_PATH', 'storage')
            file_path = os.path.join(local_storage_path, key)
            
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                content_type, _ = mimetypes.guess_type(file_path)
                
                return {
                    'key': key,
                    'size': stat.st_size,
                    'last_modified': datetime.fromtimestamp(stat.st_mtime),
                    'content_type': content_type or 'application/octet-stream',
                    'path': file_path
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get local file info: {str(e)}")
            return None

# Global instance
s3_manager = S3Manager()
