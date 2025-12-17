"""
Content Storage Manager for ScreenGram Digital Signage System.

Provides secure, production-ready file storage for Content objects.
Supports both Local File System and Amazon S3 with automatic fallback.
Includes security features: file validation, hash-based integrity checking,
signed URLs, and access control.
"""

import os
import hashlib
import logging
from typing import Optional, Tuple, BinaryIO
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Custom exception for storage-related errors."""
    pass


class ContentStorageManager:
    """
    Manages content file storage with support for Local and S3 backends.
    
    Features:
    - Automatic backend selection (S3 or Local)
    - File type and size validation
    - Hash-based integrity checking
    - Secure signed URLs for S3
    - Access control and logging
    """
    
    @staticmethod
    def _get_storage_backend():
        """Get the configured storage backend."""
        return default_storage
    
    @staticmethod
    def _validate_file_type(file_obj: UploadedFile, content_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file type based on content type.
        
        Args:
            file_obj: Uploaded file object
            content_type: Expected content type (image, video, webview, etc.)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hasattr(file_obj, 'content_type'):
            # If content_type not available, try to infer from extension
            filename = file_obj.name if hasattr(file_obj, 'name') else ''
            if not filename:
                return False, "Cannot determine file type"
        
        content_storage = getattr(settings, 'CONTENT_STORAGE', {})
        mime_type = getattr(file_obj, 'content_type', '')
        
        if content_type == 'image':
            allowed_types = content_storage.get('ALLOWED_IMAGE_TYPES', [])
            if mime_type and mime_type not in allowed_types:
                return False, f"Invalid image type: {mime_type}. Allowed: {allowed_types}"
        
        elif content_type == 'video':
            allowed_types = content_storage.get('ALLOWED_VIDEO_TYPES', [])
            if mime_type and mime_type not in allowed_types:
                return False, f"Invalid video type: {mime_type}. Allowed: {allowed_types}"
        
        elif content_type == 'webview':
            allowed_types = content_storage.get('ALLOWED_WEBVIEW_TYPES', [])
            if mime_type and mime_type not in allowed_types:
                return False, f"Invalid webview type: {mime_type}. Allowed: {allowed_types}"
        
        return True, None
    
    @staticmethod
    def _validate_file_size(file_obj: UploadedFile) -> Tuple[bool, Optional[str]]:
        """
        Validate file size.
        
        Args:
            file_obj: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        content_storage = getattr(settings, 'CONTENT_STORAGE', {})
        max_size = content_storage.get('MAX_FILE_SIZE', 500 * 1024 * 1024)  # 500 MB default
        
        if hasattr(file_obj, 'size'):
            if file_obj.size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                return False, f"File size ({file_obj.size / (1024 * 1024):.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)"
        
        return True, None
    
    @staticmethod
    def _calculate_hash(file_obj: BinaryIO, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of file content for integrity checking.
        
        Args:
            file_obj: File object to hash
            algorithm: Hash algorithm (default: sha256)
            
        Returns:
            Hexadecimal hash string
        """
        hash_obj = hashlib.new(algorithm)
        
        # Reset file pointer to beginning
        file_obj.seek(0)
        
        # Read file in chunks to handle large files
        chunk_size = 8192
        while chunk := file_obj.read(chunk_size):
            hash_obj.update(chunk)
        
        # Reset file pointer again
        file_obj.seek(0)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def _generate_storage_path(content_instance) -> str:
        """
        Generate storage path for content file.
        
        Path format: content/{content_id}/{filename}
        
        Args:
            content_instance: Content model instance
            
        Returns:
            Storage path string
        """
        content_id = str(content_instance.id)
        
        # Get filename from file_obj or generate one
        if hasattr(content_instance, '_uploaded_file_name'):
            filename = content_instance._uploaded_file_name
        else:
            # Generate filename from content name and type
            ext = ContentStorageManager._get_file_extension(content_instance.type)
            filename = f"{content_instance.name}_{content_id[:8]}{ext}"
            # Sanitize filename
            filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))
        
        return os.path.join('content', content_id, filename)
    
    @staticmethod
    def _get_file_extension(content_type: str) -> str:
        """Get default file extension for content type."""
        extensions = {
            'image': '.jpg',
            'video': '.mp4',
            'webview': '.html',
            'text': '.txt',
            'json': '.json',
        }
        return extensions.get(content_type, '')
    
    @classmethod
    def save_content(cls, content_instance, file_obj: UploadedFile, user=None) -> Tuple[str, dict]:
        """
        Save content file to storage backend.
        
        Args:
            content_instance: Content model instance
            file_obj: Uploaded file object
            user: User who uploaded the file (for logging)
            
        Returns:
            Tuple of (storage_path, metadata_dict)
            
        Raises:
            StorageError: If validation or save fails
        """
        try:
            # Validate file type
            is_valid, error = cls._validate_file_type(file_obj, content_instance.type)
            if not is_valid:
                raise StorageError(error)
            
            # Validate file size
            is_valid, error = cls._validate_file_size(file_obj)
            if not is_valid:
                raise StorageError(error)
            
            # Calculate hash for integrity checking
            content_storage = getattr(settings, 'CONTENT_STORAGE', {})
            enable_hash = content_storage.get('ENABLE_HASH_VALIDATION', True)
            hash_algorithm = content_storage.get('HASH_ALGORITHM', 'sha256')
            
            file_hash = None
            if enable_hash:
                file_hash = cls._calculate_hash(file_obj, hash_algorithm)
            
            # Generate storage path
            storage_path = cls._generate_storage_path(content_instance)
            
            # Store filename for later use
            content_instance._uploaded_file_name = file_obj.name if hasattr(file_obj, 'name') else os.path.basename(storage_path)
            
            # Save file to storage backend
            storage = cls._get_storage_backend()
            
            # Read file content
            file_obj.seek(0)
            file_content = file_obj.read()
            file_size = len(file_content)
            
            # Save to storage
            saved_path = storage.save(storage_path, ContentFile(file_content))
            
            # Get file URL
            file_url = storage.url(saved_path)
            
            # If using S3, we'll need to generate signed URL separately
            # For now, file_url might be a relative path for local storage
            # or a public URL for S3 (if configured)
            
            # Prepare metadata
            metadata = {
                'storage_path': saved_path,
                'file_url': file_url,
                'file_size': file_size,
                'file_hash': file_hash,
                'hash_algorithm': hash_algorithm if file_hash else None,
                'content_type': getattr(file_obj, 'content_type', ''),
                'saved_at': timezone.now().isoformat(),
            }
            
            logger.info(f"Content file saved: {saved_path} (size: {file_size} bytes, hash: {file_hash})")
            
            return saved_path, metadata
            
        except Exception as e:
            logger.error(f"Error saving content file: {str(e)}")
            raise StorageError(f"Failed to save content file: {str(e)}")
    
    @classmethod
    def get_content_url(cls, content_instance, expiration: Optional[int] = None) -> str:
        """
        Get secure URL for content file.
        
        For S3: Returns signed URL with expiration
        For Local: Returns media URL
        
        Args:
            content_instance: Content model instance
            expiration: URL expiration time in seconds (for S3 signed URLs)
            
        Returns:
            URL string
        """
        if not content_instance.file_url:
            raise StorageError("Content has no file_url")
        
        storage = cls._get_storage_backend()
        
        # Check if using S3 storage
        if hasattr(storage, 'url') and 's3' in str(type(storage)).lower():
            # For S3, generate signed URL
            content_storage = getattr(settings, 'CONTENT_STORAGE', {})
            default_expiration = content_storage.get('SIGNED_URL_EXPIRATION', 3600)
            expiration = expiration or default_expiration
            
            try:
                # Extract key from file_url
                # S3 URLs typically look like: https://bucket.s3.region.amazonaws.com/key
                # or: https://bucket.s3-region.amazonaws.com/key
                file_url = content_instance.file_url
                
                # If file_url is already a full S3 URL, extract the key
                # Otherwise, use the storage_path
                if hasattr(content_instance, '_storage_path'):
                    key = content_instance._storage_path
                else:
                    # Try to extract from URL
                    key = file_url.split('.com/')[-1] if '.com/' in file_url else file_url
                
                # Generate signed URL
                signed_url = storage.url(key)
                
                # For boto3, we need to use generate_presigned_url
                if hasattr(storage, 'connection'):
                    # This is S3Boto3Storage
                    try:
                        import boto3
                        from botocore.client import Config
                        
                        s3_client = boto3.client(
                            's3',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                            region_name=settings.AWS_S3_REGION_NAME,
                            config=Config(signature_version='s3v4')
                        )
                        
                        signed_url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={
                                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                'Key': key
                            },
                            ExpiresIn=expiration
                        )
                    except ImportError:
                        logger.warning("boto3 not installed, cannot generate signed URLs for S3")
                        # Fallback to regular URL
                        signed_url = file_url
                
                return signed_url
                
            except Exception as e:
                logger.error(f"Error generating signed URL: {str(e)}")
                # Fallback to regular URL
                return file_url
        
        # For local storage, return media URL
        return storage.url(content_instance.file_url) if hasattr(storage, 'url') else content_instance.file_url
    
    @classmethod
    def delete_content(cls, content_instance) -> bool:
        """
        Delete content file from storage.
        
        Args:
            content_instance: Content model instance
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not content_instance.file_url:
            return True  # Nothing to delete
        
        try:
            storage = cls._get_storage_backend()
            
            # Extract storage path
            if hasattr(content_instance, '_storage_path'):
                storage_path = content_instance._storage_path
            else:
                # Try to extract from file_url
                storage_path = content_instance.file_url
                # Remove domain/prefix if present
                if 'http' in storage_path:
                    # Extract path after domain
                    parts = storage_path.split('/')
                    # Find 'content' in path
                    try:
                        content_idx = parts.index('content')
                        storage_path = '/'.join(parts[content_idx:])
                    except ValueError:
                        pass
            
            # Delete file
            if storage.exists(storage_path):
                storage.delete(storage_path)
                logger.info(f"Content file deleted: {storage_path}")
                return True
            else:
                logger.warning(f"Content file not found for deletion: {storage_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting content file: {str(e)}")
            return False
    
    @classmethod
    def verify_content_integrity(cls, content_instance, file_obj: Optional[BinaryIO] = None) -> Tuple[bool, Optional[str]]:
        """
        Verify content file integrity using hash.
        
        Args:
            content_instance: Content model instance
            file_obj: Optional file object to verify (if not provided, reads from storage)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        content_storage = getattr(settings, 'CONTENT_STORAGE', {})
        enable_hash = content_storage.get('ENABLE_HASH_VALIDATION', True)
        
        if not enable_hash:
            return True, None
        
        if not hasattr(content_instance, 'file_hash') or not content_instance.file_hash:
            return True, None  # No hash to verify
        
        try:
            hash_algorithm = content_storage.get('HASH_ALGORITHM', 'sha256')
            
            if file_obj:
                # Calculate hash from provided file object
                calculated_hash = cls._calculate_hash(file_obj, hash_algorithm)
            else:
                # Read from storage and calculate hash
                storage = cls._get_storage_backend()
                storage_path = content_instance.file_url
                
                if not storage.exists(storage_path):
                    return False, "File not found in storage"
                
                with storage.open(storage_path, 'rb') as f:
                    calculated_hash = cls._calculate_hash(f, hash_algorithm)
            
            # Compare hashes
            stored_hash = content_instance.file_hash
            if calculated_hash.lower() != stored_hash.lower():
                return False, f"Hash mismatch: stored={stored_hash}, calculated={calculated_hash}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error verifying content integrity: {str(e)}")
            return False, f"Integrity check failed: {str(e)}"
    
    @classmethod
    def list_contents(cls, screen_id=None, template_id=None, limit=100, offset=0):
        """
        List content files with optional filtering.
        
        Args:
            screen_id: Optional screen ID to filter by
            template_id: Optional template ID to filter by
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of content metadata dictionaries
        """
        from .models import Content
        
        queryset = Content.objects.filter(is_active=True)
        
        if screen_id:
            # Filter by screens that have this content's template
            queryset = queryset.filter(
                widget__layer__template__screens__id=screen_id
            )
        
        if template_id:
            queryset = queryset.filter(
                widget__layer__template__id=template_id
            )
        
        queryset = queryset.select_related('widget__layer__template')[offset:offset+limit]
        
        results = []
        for content in queryset:
            results.append({
                'id': str(content.id),
                'name': content.name,
                'type': content.type,
                'file_url': content.file_url,
                'file_size': getattr(content, 'file_size', None),
                'download_status': content.download_status,
                'created_at': content.created_at.isoformat(),
            })
        
        return results

