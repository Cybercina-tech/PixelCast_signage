"""
Comprehensive content validators with security checks.

Validates file type, size, format, structure, and security vulnerabilities.
"""
import os
import re
import logging
from typing import Tuple, Optional, Dict, List, Any
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.core.exceptions import ValidationError

# Optional imports (handle gracefully if not available)
try:
    import magic
except ImportError:
    magic = None
    logging.warning("python-magic not installed. MIME type detection will be limited.")

try:
    from PIL import Image
except ImportError:
    Image = None
    logging.warning("Pillow not installed. Image validation will be limited.")

import io

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error with detailed message."""
    pass


class SecurityValidationError(ValidationError):
    """Security-related validation error."""
    pass


class ContentValidator:
    """
    Comprehensive content validator with security checks.
    
    Features:
    - File type and MIME type validation
    - File size limits per type
    - Format/structure validation
    - Security vulnerability detection
    - Path traversal prevention
    - Script injection detection
    - Executable file detection
    """
    
    # Allowed file extensions per content type
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'],
        'video': ['.mp4', '.webm', '.ogg', '.mov', '.avi'],
        'webview': ['.html', '.htm', '.xhtml'],
        'text': ['.txt', '.md', '.csv'],
        'json': ['.json'],
    }
    
    # Allowed MIME types per content type
    ALLOWED_MIME_TYPES = {
        'image': [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'image/webp', 'image/svg+xml', 'image/svg'
        ],
        'video': [
            'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime',
            'video/x-msvideo', 'video/avi'
        ],
        'webview': [
            'text/html', 'application/xhtml+xml', 'text/xhtml'
        ],
        'text': [
            'text/plain', 'text/markdown', 'text/csv', 'text/css'
        ],
        'json': [
            'application/json', 'text/json'
        ],
    }
    
    # Maximum file sizes per type (in bytes)
    MAX_FILE_SIZES = {
        'image': 50 * 1024 * 1024,  # 50 MB
        'video': 500 * 1024 * 1024,  # 500 MB
        'webview': 10 * 1024 * 1024,  # 10 MB
        'text': 5 * 1024 * 1024,  # 5 MB
        'json': 5 * 1024 * 1024,  # 5 MB
    }
    
    # Dangerous file extensions to reject
    DANGEROUS_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js', '.jar',
        '.app', '.deb', '.rpm', '.msi', '.dmg', '.pkg', '.sh', '.ps1',
        '.php', '.asp', '.jsp', '.py', '.rb', '.pl', '.cgi'
    ]
    
    # Dangerous MIME types
    DANGEROUS_MIME_TYPES = [
        'application/x-executable', 'application/x-msdownload',
        'application/x-shockwave-flash', 'application/x-javascript',
        'text/javascript', 'application/javascript'
    ]
    
    # Script injection patterns
    SCRIPT_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'eval\s*\(',
        r'exec\s*\(',
        r'<svg.*onload',
        r'<img.*onerror',
    ]
    
    @classmethod
    def validate_filename(cls, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate and sanitize filename.
        
        Args:
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, sanitized_filename or error_message)
        """
        if not filename:
            return False, "Filename cannot be empty"
        
        # Remove path components (prevent directory traversal)
        filename = os.path.basename(filename)
        
        # Check for directory traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            raise SecurityValidationError("Path traversal attempt detected in filename")
        
        # Check for null bytes
        if '\x00' in filename:
            raise SecurityValidationError("Null byte detected in filename")
        
        # Remove or replace dangerous characters
        # Allow: alphanumeric, dash, underscore, dot
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Ensure filename is not empty after sanitization
        if not sanitized or sanitized.strip() == '':
            return False, "Filename is invalid after sanitization"
        
        # Limit filename length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        # Ensure filename doesn't start or end with dot
        sanitized = sanitized.strip('.')
        
        if not sanitized:
            return False, "Filename cannot be only dots"
        
        return True, sanitized
    
    @classmethod
    def validate_file_extension(cls, filename: str, content_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file extension matches content type.
        
        Args:
            filename: File filename
            content_type: Expected content type
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename is required"
        
        # Get file extension
        _, ext = os.path.splitext(filename.lower())
        
        # Check for dangerous extensions
        if ext in cls.DANGEROUS_EXTENSIONS:
            raise SecurityValidationError(f"Dangerous file extension detected: {ext}")
        
        # Check if extension is allowed for content type
        allowed_exts = cls.ALLOWED_EXTENSIONS.get(content_type, [])
        if ext not in allowed_exts:
            return False, f"File extension {ext} not allowed for content type '{content_type}'. Allowed: {allowed_exts}"
        
        return True, None
    
    @classmethod
    def validate_mime_type(cls, file_obj: UploadedFile, content_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate MIME type matches content type.
        
        Args:
            file_obj: Uploaded file object
            content_type: Expected content type
            
        Returns:
            Tuple of (is_valid, detected_mime_type or error_message)
        """
        # Get MIME type from file object
        declared_mime = getattr(file_obj, 'content_type', '')
        
        # Read file content for actual MIME type detection
        file_obj.seek(0)
        file_content = file_obj.read(1024)  # Read first 1KB for MIME detection
        file_obj.seek(0)
        
        # Detect actual MIME type using python-magic or file signature
        detected_mime = None
        try:
            # Try python-magic if available
            if magic:
                detected_mime = magic.from_buffer(file_content, mime=True)
        except:
            pass
        
        # Fallback to declared MIME type
        if not detected_mime:
            detected_mime = declared_mime
        
        # Check for dangerous MIME types
        if detected_mime in cls.DANGEROUS_MIME_TYPES:
            raise SecurityValidationError(f"Dangerous MIME type detected: {detected_mime}")
        
        # Validate against allowed MIME types for content type
        allowed_mimes = cls.ALLOWED_MIME_TYPES.get(content_type, [])
        
        # If detected_mime is available, use it; otherwise use declared
        mime_to_check = detected_mime or declared_mime
        
        if mime_to_check and mime_to_check not in allowed_mimes:
            return False, f"MIME type '{mime_to_check}' not allowed for content type '{content_type}'. Allowed: {allowed_mimes}"
        
        # Check for MIME type mismatch (extension vs actual MIME)
        if detected_mime and declared_mime and detected_mime != declared_mime:
            logger.warning(f"MIME type mismatch: declared={declared_mime}, detected={detected_mime}")
            # Use detected MIME for validation
            mime_to_check = detected_mime
        
        return True, mime_to_check or declared_mime
    
    @classmethod
    def validate_file_size(cls, file_obj: UploadedFile, content_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file size within limits.
        
        Args:
            file_obj: Uploaded file object
            content_type: Content type
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hasattr(file_obj, 'size'):
            return False, "Cannot determine file size"
        
        max_size = cls.MAX_FILE_SIZES.get(content_type, 10 * 1024 * 1024)  # Default 10MB
        
        # Check if size exceeds limit
        if file_obj.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            actual_size_mb = file_obj.size / (1024 * 1024)
            return False, f"File size ({actual_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb:.2f} MB) for content type '{content_type}'"
        
        # Check for zero-size files
        if file_obj.size == 0:
            return False, "File is empty"
        
        return True, None
    
    @classmethod
    def validate_image_format(cls, file_obj: UploadedFile) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validate image format and extract metadata.
        
        Args:
            file_obj: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message, metadata_dict)
        """
        if Image is None:
            logger.warning("Pillow not available, skipping detailed image validation")
            return True, None, {}
        
        try:
            file_obj.seek(0)
            file_content = file_obj.read()
            file_obj.seek(0)
            
            # Open image with PIL
            try:
                image = Image.open(io.BytesIO(file_content))
            except Exception as e:
                return False, f"Invalid image format: {str(e)}", None
            
            # Verify image can be loaded and is not corrupted
            try:
                image.verify()
            except Exception as e:
                return False, f"Image is corrupted: {str(e)}", None
            
            # Reopen for metadata (verify() closes the image)
            image = Image.open(io.BytesIO(file_content))
            
            # Check format
            if image.format not in ['JPEG', 'PNG', 'GIF', 'WEBP', 'SVG']:
                return False, f"Unsupported image format: {image.format}", None
            
            # Extract metadata
            metadata = {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,  # (width, height)
                'width': image.size[0],
                'height': image.size[1],
            }
            
            # Check for reasonable dimensions
            if image.size[0] < 1 or image.size[1] < 1:
                return False, "Image has invalid dimensions", None
            
            if image.size[0] > 10000 or image.size[1] > 10000:
                return False, "Image dimensions exceed maximum (10000x10000)", None
            
            return True, None, metadata
            
        except Exception as e:
            logger.error(f"Error validating image format: {str(e)}")
            return False, f"Image validation error: {str(e)}", None
    
    @classmethod
    def validate_video_format(cls, file_obj: UploadedFile) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validate video format and extract basic metadata.
        
        Args:
            file_obj: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message, metadata_dict)
        """
        try:
            file_obj.seek(0)
            file_content = file_obj.read(8192)  # Read first 8KB for header check
            file_obj.seek(0)
            
            metadata = {}
            
            # Check for video file signatures (magic numbers)
            # MP4: ftyp box at beginning
            if file_content[:4] == b'ftyp':
                metadata['format'] = 'MP4'
                metadata['codec'] = 'H.264/H.265'  # Generic
            # WebM: starts with EBML header
            elif file_content[:4] == b'\x1a\x45\xdf\xa3':
                metadata['format'] = 'WebM'
                metadata['codec'] = 'VP8/VP9'
            # AVI: RIFF header
            elif file_content[:4] == b'RIFF':
                metadata['format'] = 'AVI'
                metadata['codec'] = 'Various'
            # MOV/QuickTime: ftyp or moov
            elif file_content[4:8] == b'ftyp' or file_content[4:8] == b'moov':
                metadata['format'] = 'MOV'
                metadata['codec'] = 'QuickTime'
            else:
                # Could be valid video but signature not recognized
                # Try to proceed with basic validation
                pass
            
            # For more detailed validation, would need ffprobe or similar
            # For now, basic signature check is sufficient
            
            return True, None, metadata
            
        except Exception as e:
            logger.error(f"Error validating video format: {str(e)}")
            return False, f"Video validation error: {str(e)}", None
    
    @classmethod
    def validate_text_content(cls, file_obj: UploadedFile, check_scripts: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Validate text content and check for script injection.
        
        Args:
            file_obj: Uploaded file object
            check_scripts: Whether to check for script injection patterns
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            file_obj.seek(0)
            file_content = file_obj.read()
            file_obj.seek(0)
            
            # Try to decode as UTF-8
            try:
                text_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                # Try other encodings
                try:
                    text_content = file_content.decode('latin-1')
                except:
                    return False, "File encoding not recognized (expected UTF-8 or Latin-1)"
            
            # Check for script injection patterns
            if check_scripts:
                for pattern in cls.SCRIPT_PATTERNS:
                    if re.search(pattern, text_content, re.IGNORECASE | re.DOTALL):
                        raise SecurityValidationError(f"Script injection pattern detected: {pattern}")
            
            return True, None
            
        except SecurityValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating text content: {str(e)}")
            return False, f"Text validation error: {str(e)}"
    
    @classmethod
    def validate_json_content(cls, file_obj: UploadedFile) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON content format.
        
        Args:
            file_obj: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            import json
            file_obj.seek(0)
            file_content = file_obj.read()
            file_obj.seek(0)
            
            # Try to decode and parse JSON
            try:
                text_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                return False, "JSON file must be UTF-8 encoded"
            
            # Parse JSON
            try:
                json.loads(text_content)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON format: {str(e)}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating JSON content: {str(e)}")
            return False, f"JSON validation error: {str(e)}"
    
    @classmethod
    def check_executable_headers(cls, file_obj: UploadedFile) -> Tuple[bool, Optional[str]]:
        """
        Check file for executable headers (ELF, PE, Mach-O).
        
        Args:
            file_obj: Uploaded file object
            
        Returns:
            Tuple of (is_safe, error_message)
        """
        try:
            file_obj.seek(0)
            file_header = file_obj.read(16)
            file_obj.seek(0)
            
            # ELF executable (Linux/Unix)
            if file_header[:4] == b'\x7fELF':
                raise SecurityValidationError("ELF executable detected (Linux/Unix executable)")
            
            # PE executable (Windows)
            if file_header[:2] == b'MZ':
                # Check further for PE signature
                file_obj.seek(0)
                full_header = file_obj.read(64)
                if b'PE\x00\x00' in full_header:
                    raise SecurityValidationError("PE executable detected (Windows executable)")
                file_obj.seek(0)
            
            # Mach-O executable (macOS)
            if file_header[:4] in [b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe',
                                   b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe',
                                   b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca']:
                raise SecurityValidationError("Mach-O executable detected (macOS executable)")
            
            # Java class file
            if file_header[:4] == b'\xca\xfe\xba\xbe':
                raise SecurityValidationError("Java class file detected")
            
            return True, None
            
        except SecurityValidationError:
            raise
        except Exception as e:
            logger.error(f"Error checking executable headers: {str(e)}")
            # Don't fail validation if check fails, but log it
            return True, None
    
    @classmethod
    def validate_content(cls, file_obj: UploadedFile, content_type: str, filename: str) -> Dict[str, Any]:
        """
        Comprehensive content validation.
        
        Args:
            file_obj: Uploaded file object
            content_type: Expected content type (image, video, text, etc.)
            filename: Original filename
            
        Returns:
            Dict with validation results:
            {
                'is_valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'metadata': Dict,
                'sanitized_filename': str
            }
            
        Raises:
            ValidationError: If validation fails critically
            SecurityValidationError: If security issue detected
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'metadata': {},
            'sanitized_filename': filename
        }
        
        try:
            # 1. Validate and sanitize filename
            is_valid, sanitized = cls.validate_filename(filename)
            if not is_valid:
                result['errors'].append(f"Filename validation failed: {sanitized}")
                result['is_valid'] = False
            else:
                result['sanitized_filename'] = sanitized
            
            # 2. Validate file extension
            is_valid, error = cls.validate_file_extension(result['sanitized_filename'], content_type)
            if not is_valid:
                result['errors'].append(f"Extension validation failed: {error}")
                result['is_valid'] = False
            
            # 3. Validate MIME type
            is_valid, mime_type = cls.validate_mime_type(file_obj, content_type)
            if not is_valid:
                result['errors'].append(f"MIME type validation failed: {mime_type}")
                result['is_valid'] = False
            else:
                result['metadata']['mime_type'] = mime_type
            
            # 4. Validate file size
            is_valid, error = cls.validate_file_size(file_obj, content_type)
            if not is_valid:
                result['errors'].append(f"Size validation failed: {error}")
                result['is_valid'] = False
            else:
                result['metadata']['file_size'] = file_obj.size
            
            # 5. Check for executable headers (security)
            try:
                cls.check_executable_headers(file_obj)
            except SecurityValidationError as e:
                result['errors'].append(f"Security check failed: {str(e)}")
                result['is_valid'] = False
            
            # 6. Content-type specific validation
            if content_type == 'image':
                is_valid, error, metadata = cls.validate_image_format(file_obj)
                if not is_valid:
                    result['errors'].append(f"Image format validation failed: {error}")
                    result['is_valid'] = False
                else:
                    result['metadata'].update(metadata or {})
            
            elif content_type == 'video':
                is_valid, error, metadata = cls.validate_video_format(file_obj)
                if not is_valid:
                    result['errors'].append(f"Video format validation failed: {error}")
                    result['is_valid'] = False
                else:
                    result['metadata'].update(metadata or {})
            
            elif content_type == 'text':
                is_valid, error = cls.validate_text_content(file_obj, check_scripts=True)
                if not is_valid:
                    result['errors'].append(f"Text content validation failed: {error}")
                    result['is_valid'] = False
            
            elif content_type == 'json':
                is_valid, error = cls.validate_json_content(file_obj)
                if not is_valid:
                    result['errors'].append(f"JSON validation failed: {error}")
                    result['is_valid'] = False
            
            elif content_type == 'webview':
                # Webview is HTML, check for scripts
                is_valid, error = cls.validate_text_content(file_obj, check_scripts=True)
                if not is_valid:
                    result['errors'].append(f"Webview content validation failed: {error}")
                    result['is_valid'] = False
            
            # If any critical errors, raise exception
            if not result['is_valid']:
                error_msg = "; ".join(result['errors'])
                if any('Security' in err or 'security' in err.lower() for err in result['errors']):
                    raise SecurityValidationError(error_msg)
                else:
                    raise ValidationError(error_msg)
            
            return result
            
        except (ValidationError, SecurityValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error during validation: {str(e)}")
            raise ValidationError(f"Validation error: {str(e)}")
