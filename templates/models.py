import uuid
import os
import requests
import json
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError
from datetime import timedelta


def default_json_dict():
    """Return an empty dict for JSONField default values."""
    return {}


def template_thumbnail_upload_path(instance, filename):
    """
    Generate upload path for template thumbnails.
    Organizes files by template ID for better file management.
    """
    ext = filename.split('.')[-1]
    filename = f"{instance.id}.{ext}"
    return os.path.join('templates', 'thumbnails', filename)


class Template(models.Model):
    """
    Digital Signage Template model for managing display templates.
    
    Templates define the layout, content, and configuration for digital signage screens.
    Each template can contain multiple layers and widgets, and can be assigned to screens.
    """
    
    # Core Information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the template"
    )
    name = models.CharField(
        max_length=255,
        help_text="Display name for the template"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the template"
    )
    ORIENTATION_CHOICES = [
        ('landscape', 'Landscape'),
        ('portrait', 'Portrait'),
    ]
    orientation = models.CharField(
        max_length=20,
        choices=ORIENTATION_CHOICES,
        default='landscape',
        help_text="Template orientation"
    )
    width = models.PositiveIntegerField(
        default=1920,
        validators=[MinValueValidator(1)],
        help_text="Template width in pixels"
    )
    height = models.PositiveIntegerField(
        default=1080,
        validators=[MinValueValidator(1)],
        help_text="Template height in pixels"
    )
    thumbnail = models.ImageField(
        upload_to=template_thumbnail_upload_path,
        blank=True,
        null=True,
        help_text="Preview thumbnail image for the template"
    )
    
    # Relations
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_templates',
        help_text="User who created this template"
    )
    screens = models.ManyToManyField(
        'signage.Screen',
        blank=True,
        related_name='templates',
        help_text="Screens that have this template assigned"
    )
    assigned_schedules = models.ManyToManyField(
        'signage.Schedule',
        blank=True,
        related_name='templates',
        help_text="Schedules assigned to this template"
    )
    
    # Status & Control
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the template is currently active and available for use"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this template was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this template was last updated"
    )
    version = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Template version number"
    )
    
    # Dynamic Configuration
    config_json = models.JSONField(
        default=default_json_dict,
        help_text="Template configuration in JSON format (required)"
    )
    meta_data = models.JSONField(
        default=default_json_dict,
        blank=True,
        help_text="Additional metadata in JSON format (optional)"
    )
    
    class Meta:
        db_table = 'templates_template'
        verbose_name = 'Template'
        verbose_name_plural = 'Templates'
        ordering = ['-created_at', 'name']
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
            models.Index(fields=['created_by', 'is_active']),
            models.Index(fields=['orientation', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_layers(self):
        """
        Get all Layer objects associated with this template.
        
        Returns:
            QuerySet: All Layer objects related to this template
        """
        # This will work once the Layer model is created with a ForeignKey to Template
        try:
            return self.layers.all()
        except AttributeError:
            # Layer model doesn't exist yet, return empty queryset
            from django.db.models.query import EmptyQuerySet
            return EmptyQuerySet(model=None)
    
    def get_widgets(self):
        """
        Get all Widget objects across all layers of this template.
        
        This method will work once Layer and Widget models are created.
        Widget model should have a ForeignKey to Layer with related_name='widgets'.
        
        Returns:
            QuerySet: All Widget objects from all layers in this template
        """
        try:
            layers = self.get_layers()
            if not layers.exists():
                from django.db.models.query import EmptyQuerySet
                return EmptyQuerySet(model=None)
            
            # Collect widgets from all layers
            # This assumes Layer model has a ForeignKey to Widget with related_name='widgets'
            from django.apps import apps
            
            # Try to get Widget model dynamically
            try:
                Widget = apps.get_model('templates', 'Widget')
                Layer = apps.get_model('templates', 'Layer')
                
                # Get all layer IDs
                layer_ids = layers.values_list('id', flat=True)
                
                # Return widgets from all layers
                return Widget.objects.filter(layer_id__in=layer_ids)
            except (LookupError, AttributeError):
                # Models don't exist yet
                from django.db.models.query import EmptyQuerySet
                return EmptyQuerySet(model=None)
        except Exception:
            # Fallback if anything goes wrong
            from django.db.models.query import EmptyQuerySet
            return EmptyQuerySet(model=None)


class Layer(models.Model):
    """
    Digital Signage Layer model for managing template layers.
    
    Layers are positioned containers within a template that can hold widgets.
    Each layer has position, size, appearance properties, and can contain animations.
    """
    
    # Core Information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the layer"
    )
    name = models.CharField(
        max_length=255,
        help_text="Display name for the layer"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the layer"
    )
    
    # Position & Size
    x = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="X position (left) in pixels from template origin"
    )
    y = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Y position (top) in pixels from template origin"
    )
    width = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Layer width in pixels"
    )
    height = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Layer height in pixels"
    )
    z_index = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Z-index for display order (higher values appear on top)"
    )
    
    # Appearance & Animation
    background_color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Background color (hex code like #FFFFFF or color name)"
    )
    opacity = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Layer opacity (0.0 = transparent, 1.0 = opaque)"
    )
    ANIMATION_TYPE_CHOICES = [
        ('none', 'None'),
        ('fade', 'Fade'),
        ('slide', 'Slide'),
    ]
    animation_type = models.CharField(
        max_length=20,
        choices=ANIMATION_TYPE_CHOICES,
        default='none',
        help_text="Type of animation to apply to the layer"
    )
    animation_duration = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Animation duration in seconds"
    )
    
    # Relations
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name='layers',
        help_text="Template that this layer belongs to"
    )
    
    # Status & Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the layer is currently active and visible"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this layer was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this layer was last updated"
    )
    
    class Meta:
        db_table = 'templates_layer'
        verbose_name = 'Layer'
        verbose_name_plural = 'Layers'
        ordering = ['template', 'z_index', 'name']
        indexes = [
            models.Index(fields=['template', 'z_index']),
            models.Index(fields=['template', 'is_active']),
            models.Index(fields=['is_active', 'z_index']),
        ]
    
    def __str__(self):
        """Return string representation: '{template name} - {layer name}'"""
        return f"{self.template.name} - {self.name}"
    
    def get_widgets(self):
        """
        Get all Widget objects associated with this layer.
        
        Returns:
            QuerySet: All Widget objects related to this layer
        """
        return self.widgets.all()


class Widget(models.Model):
    """
    Digital Signage Widget model for managing content widgets within layers.
    
    Widgets are content elements (text, images, videos, etc.) that are positioned
    within layers. Each widget has its own position, size, and content configuration.
    """
    
    # Core Information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the widget"
    )
    name = models.CharField(
        max_length=255,
        help_text="Display name for the widget"
    )
    
    # Content Type & Configuration
    WIDGET_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('clock', 'Clock'),
        ('webview', 'Web View'),
        ('chart', 'Chart'),
    ]
    type = models.CharField(
        max_length=20,
        choices=WIDGET_TYPE_CHOICES,
        help_text="Type of widget content"
    )
    content_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL or file path for image/video/webview content"
    )
    content_json = models.JSONField(
        default=default_json_dict,
        blank=True,
        help_text="Dynamic or structured data for widget content"
    )
    font_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Font size in pixels (used for text widgets)"
    )
    color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Color (hex code or color name) for text or background"
    )
    ALIGNMENT_CHOICES = [
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ]
    alignment = models.CharField(
        max_length=10,
        choices=ALIGNMENT_CHOICES,
        blank=True,
        null=True,
        help_text="Text alignment (used for text widgets)"
    )
    autoplay = models.BooleanField(
        default=False,
        help_text="Whether to autoplay video or animated widgets"
    )
    
    # Position & Size
    x = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="X position (left) in pixels from layer origin"
    )
    y = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Y position (top) in pixels from layer origin"
    )
    width = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Widget width in pixels"
    )
    height = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Widget height in pixels"
    )
    z_index = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Z-index for display order within layer (higher values appear on top)"
    )
    
    # Relations
    layer = models.ForeignKey(
        Layer,
        on_delete=models.CASCADE,
        related_name='widgets',
        help_text="Layer that this widget belongs to"
    )
    
    # Status & Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the widget is currently active and visible"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this widget was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this widget was last updated"
    )
    
    class Meta:
        db_table = 'templates_widget'
        verbose_name = 'Widget'
        verbose_name_plural = 'Widgets'
        ordering = ['layer', 'z_index', 'name']
        indexes = [
            models.Index(fields=['layer', 'z_index']),
            models.Index(fields=['layer', 'is_active']),
            models.Index(fields=['type', 'is_active']),
            models.Index(fields=['is_active', 'z_index']),
        ]
    
    def __str__(self):
        """Return string representation: '{layer name} - {widget name}'"""
        return f"{self.layer.name} - {self.name}"


class Content(models.Model):
    """
    Digital Signage Content model for managing media and content items within widgets.
    
    Content represents individual media items (images, videos, text, etc.) that can be
    displayed within a widget. Supports multiple content items per widget for slideshows
    or playlists. Tracks download status for caching on screens.
    """
    
    # Core Information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the content"
    )
    name = models.CharField(
        max_length=255,
        help_text="Display name for the content"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the content"
    )
    
    # Content Type & File/Data
    CONTENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text'),
        ('webview', 'Web View'),
        ('chart', 'Chart'),
        ('json', 'JSON Data'),
    ]
    type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        help_text="Type of content"
    )
    file_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="URL or file path for local or remote files (image/video/webview)"
    )
    content_json = models.JSONField(
        default=default_json_dict,
        blank=True,
        help_text="Dynamic or structured data for content"
    )
    duration = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
        help_text="Display duration in seconds (for slideshows or videos)"
    )
    autoplay = models.BooleanField(
        default=False,
        help_text="Whether to autoplay video or animated content"
    )
    order = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Order of content in a widget (for playlists or slideshows)"
    )
    
    # Relations
    widget = models.ForeignKey(
        Widget,
        on_delete=models.CASCADE,
        related_name='contents',
        help_text="Widget that this content belongs to"
    )
    
    # Status & Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the content is currently active and visible"
    )
    downloaded = models.BooleanField(
        default=False,
        help_text="Whether content is cached locally on Screen"
    )
    DOWNLOAD_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    download_status = models.CharField(
        max_length=20,
        choices=DOWNLOAD_STATUS_CHOICES,
        default='pending',
        help_text="Status of content download to screen"
    )
    last_download_attempt = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time download was attempted"
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of download retry attempts"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this content was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this content was last updated"
    )
    
    class Meta:
        db_table = 'templates_content'
        verbose_name = 'Content'
        verbose_name_plural = 'Contents'
        ordering = ['widget', 'order', 'name']
        indexes = [
            models.Index(fields=['widget', 'order']),
            models.Index(fields=['widget', 'is_active']),
            models.Index(fields=['type', 'is_active']),
            models.Index(fields=['download_status', 'downloaded']),
            models.Index(fields=['widget', 'download_status']),
        ]
    
    def __str__(self):
        """Return string representation: '{widget name} - {content name}'"""
        return f"{self.widget.name} - {self.name}"
    
    # Helper Methods for Download Status
    def mark_downloaded(self):
        """
        Mark content as successfully downloaded.
        Updates downloaded flag and download_status.
        """
        self.downloaded = True
        self.download_status = 'success'
        self.last_download_attempt = timezone.now()
        self.save(update_fields=['downloaded', 'download_status', 'last_download_attempt'])
    
    def mark_failed(self):
        """
        Mark content download as failed.
        Updates download_status, increments retry_count, and updates last_download_attempt.
        """
        self.downloaded = False
        self.download_status = 'failed'
        self.retry_count += 1
        self.last_download_attempt = timezone.now()
        self.save(update_fields=['downloaded', 'download_status', 'retry_count', 'last_download_attempt'])
    
    def update_status(self, status, downloaded=None):
        """
        Update download status and optionally downloaded flag.
        
        Args:
            status: One of 'pending', 'success', 'failed'
            downloaded: Optional boolean to set downloaded flag
        """
        if status not in dict(self.DOWNLOAD_STATUS_CHOICES).keys():
            raise ValueError(f"Invalid status: {status}. Must be one of {list(dict(self.DOWNLOAD_STATUS_CHOICES).keys())}")
        
        self.download_status = status
        if downloaded is not None:
            self.downloaded = downloaded
        self.last_download_attempt = timezone.now()
        self.save(update_fields=['download_status', 'downloaded', 'last_download_attempt'])
    
    def reset_download_status(self):
        """
        Reset download status to pending.
        Useful when content is updated and needs to be re-downloaded.
        """
        self.downloaded = False
        self.download_status = 'pending'
        self.last_download_attempt = None
        self.save(update_fields=['downloaded', 'download_status', 'last_download_attempt'])
    
    # Property Methods
    @property
    def is_downloaded(self):
        """Check if content is successfully downloaded"""
        return self.downloaded and self.download_status == 'success'
    
    @property
    def needs_download(self):
        """Check if content needs to be downloaded"""
        return not self.downloaded or self.download_status in ['pending', 'failed']
    
    @property
    def file_extension(self):
        """Extract file extension from file_url if available"""
        if self.file_url:
            try:
                return os.path.splitext(self.file_url.split('?')[0])[1].lower()
            except (AttributeError, IndexError):
                return None
        return None
    
    @property
    def is_media_file(self):
        """Check if content is a media file (image or video)"""
        return self.type in ['image', 'video']
    
    @property
    def estimated_size_mb(self):
        """
        Estimate file size in MB based on type and duration.
        This is a rough estimate and can be overridden with actual file size.
        """
        if not self.is_media_file or not self.duration:
            return None
        
        # Rough estimates: 1MB per second for video, 0.1MB per image
        if self.type == 'video':
            return round(self.duration * 1.0, 2)
        elif self.type == 'image':
            return 0.1
        return None
    
    # Operational Methods for Content Delivery
    def download_to_screen(self, screen, max_retries=3, timeout=30):
        """
        Download content to a specific Screen instance.
        
        This method handles the actual download process:
        1. Validates content and screen
        2. Downloads file from file_url (if applicable)
        3. Stores content on screen's local storage
        4. Updates download status
        5. Handles exceptions and retries
        
        Args:
            screen: Screen instance to download content to
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 30)
            
        Returns:
            bool: True if download successful, False otherwise
            
        Raises:
            ValueError: If content type doesn't require file download
            ConnectionError: If network connection fails
        """
        # Validate content is active
        if not self.is_active:
            raise ValueError("Cannot download inactive content")
        
        # Validate screen is online
        if not screen.is_online:
            raise ValueError(f"Screen {screen.name} is not online")
        
        # Check if retry limit exceeded
        if self.retry_count >= max_retries:
            self.mark_failed()
            return False
        
        # For non-file content types, just mark as downloaded
        if self.type in ['text', 'json', 'chart']:
            # These don't require file download, just mark as ready
            self.mark_downloaded()
            return True
        
        # For file-based content, perform actual download
        if not self.file_url:
            raise ValueError(f"Content {self.name} requires file_url for download")
        
        try:
            # Validate URL
            URLValidator()(self.file_url)
            
            # Download file
            response = requests.get(
                self.file_url,
                timeout=timeout,
                stream=True,
                headers={'User-Agent': 'ScreenGram-DigitalSignage/1.0'}
            )
            response.raise_for_status()
            
            # Determine storage path on screen
            # This is a placeholder - actual implementation would use screen's storage path
            storage_path = self._get_screen_storage_path(screen)
            
            # Save file to screen storage
            # In production, this would use screen's API or file transfer mechanism
            file_saved = self._save_file_to_screen(response, screen, storage_path)
            
            if file_saved:
                # Mark as downloaded
                self.mark_downloaded()
                # Reset retry count on success
                self.retry_count = 0
                self.save(update_fields=['retry_count'])
                return True
            else:
                raise Exception("Failed to save file to screen storage")
                
        except requests.exceptions.RequestException as e:
            # Network or HTTP error
            self.mark_failed()
            raise ConnectionError(f"Download failed: {str(e)}")
        except Exception as e:
            # Other errors
            self.mark_failed()
            raise Exception(f"Download error: {str(e)}")
    
    def retry_download(self, screen, max_retries=3):
        """
        Retry downloading content to a screen if previous attempt failed.
        
        Args:
            screen: Screen instance to download content to
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            bool: True if retry successful, False otherwise
        """
        # Only retry if status is 'failed' or 'pending'
        if self.download_status not in ['failed', 'pending']:
            return False
        
        # Check retry limit
        if self.retry_count >= max_retries:
            self.update_status('failed')
            return False
        
        try:
            return self.download_to_screen(screen, max_retries=max_retries)
        except Exception as e:
            # Log error (in production, use proper logging)
            print(f"Retry download failed for content {self.name} to screen {screen.name}: {str(e)}")
            return False
    
    def _get_screen_storage_path(self, screen):
        """
        Get storage path for content on a specific screen.
        
        This is a helper method that generates the storage path.
        In production, this would integrate with screen's storage system.
        
        Args:
            screen: Screen instance
            
        Returns:
            str: Storage path for the content
        """
        # Generate path: screens/{screen_id}/content/{content_id}/{filename}
        screen_id = str(screen.id)
        content_id = str(self.id)
        
        # Get filename from URL or use content name
        if self.file_url:
            filename = os.path.basename(self.file_url.split('?')[0])
            if not filename:
                # Generate filename from type and id
                ext = self.file_extension or self._get_default_extension()
                filename = f"{self.name}_{content_id[:8]}{ext}"
        else:
            ext = self._get_default_extension()
            filename = f"{self.name}_{content_id[:8]}{ext}"
        
        return os.path.join('screens', screen_id, 'content', content_id, filename)
    
    def _get_default_extension(self):
        """Get default file extension based on content type"""
        extensions = {
            'image': '.jpg',
            'video': '.mp4',
            'webview': '.html',
        }
        return extensions.get(self.type, '')
    
    def _save_file_to_screen(self, response, screen, storage_path):
        """
        Save downloaded file to screen storage.
        
        This is a placeholder method. In production, this would:
        1. Use screen's API to transfer file
        2. Use FTP/SFTP for file transfer
        3. Use screen's local storage API
        
        Args:
            response: requests.Response object
            screen: Screen instance
            storage_path: Path where file should be saved
            
        Returns:
            bool: True if file saved successfully
        """
        # Placeholder implementation
        # In production, this would use actual file transfer mechanism
        
        # For now, just validate that we can read the file
        try:
            # Check if response has content
            if response.headers.get('content-length'):
                content_length = int(response.headers['content-length'])
                # Validate reasonable file size (e.g., max 500MB)
                if content_length > 500 * 1024 * 1024:
                    raise ValueError("File size exceeds maximum allowed size (500MB)")
            
            # In production, save to screen's storage
            # For now, return True to indicate "would be saved"
            return True
        except Exception as e:
            print(f"Error saving file to screen: {str(e)}")
            return False
    
    def validate_content(self):
        """
        Validate content data based on type.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Validate file_url for file-based content
        if self.type in ['image', 'video', 'webview']:
            if not self.file_url:
                return False, f"{self.type} content requires file_url"
            
            # Validate URL format
            try:
                URLValidator()(self.file_url)
            except ValidationError:
                return False, "Invalid file_url format"
        
        # Validate content_json for JSON content
        if self.type == 'json':
            if not self.content_json:
                return False, "JSON content requires content_json"
            try:
                json.dumps(self.content_json)  # Validate JSON is serializable
            except (TypeError, ValueError):
                return False, "Invalid JSON in content_json"
        
        # Validate duration for time-based content
        if self.duration is not None and self.duration <= 0:
            return False, "Duration must be positive"
        
        return True, None
    
    def clean(self):
        """Run validation on save"""
        super().clean()
        is_valid, error = self.validate_content()
        if not is_valid:
            raise ValidationError(error)


class Schedule(models.Model):
    """
    Digital Signage Schedule model for managing time-based template scheduling.
    
    Schedules define when and how templates should be displayed on screens.
    Supports one-time and recurring schedules with priority-based conflict resolution.
    """
    
    # Core Information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the schedule"
    )
    name = models.CharField(
        max_length=255,
        help_text="Display name for the schedule"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the schedule"
    )
    
    # Relations
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name='schedules',
        help_text="Template to be displayed in this schedule"
    )
    screens = models.ManyToManyField(
        'signage.Screen',
        blank=True,
        related_name='schedules',
        help_text="Screens where this schedule should run"
    )
    
    # Scheduling
    start_time = models.DateTimeField(
        help_text="Start time for the schedule"
    )
    end_time = models.DateTimeField(
        help_text="End time for the schedule"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the schedule is currently active"
    )
    REPEAT_TYPE_CHOICES = [
        ('none', 'None (One-time)'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    repeat_type = models.CharField(
        max_length=20,
        choices=REPEAT_TYPE_CHOICES,
        default='none',
        help_text="How often the schedule should repeat"
    )
    priority = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Priority level (higher values override lower ones in conflicts)"
    )
    
    # Status & Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this schedule was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this schedule was last updated"
    )
    last_executed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time this schedule was executed"
    )
    is_currently_running = models.BooleanField(
        default=False,
        help_text="Whether this schedule is currently active and running"
    )
    
    class Meta:
        db_table = 'templates_schedule'
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        ordering = ['-priority', 'start_time', 'name']
        indexes = [
            models.Index(fields=['template', 'is_active']),
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['is_active', 'start_time', 'end_time']),
            models.Index(fields=['repeat_type', 'is_active']),
            models.Index(fields=['priority', 'is_active']),
            models.Index(fields=['is_currently_running', 'start_time']),
        ]
    
    def __str__(self):
        """Return string representation: '{template name} - {name} ({start_time} to {end_time})'"""
        return f"{self.template.name} - {self.name} ({self.start_time} to {self.end_time})"
    
    def clean(self):
        """Validate that end_time is after start_time"""
        super().clean()
        if self.end_time and self.start_time:
            if self.end_time <= self.start_time:
                raise ValidationError({
                    'end_time': 'End time must be after start time.'
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    # Helper Methods
    def activate(self):
        """Activate the schedule"""
        self.is_active = True
        self.save(update_fields=['is_active'])
    
    def deactivate(self):
        """Deactivate the schedule"""
        self.is_active = False
        self.is_currently_running = False
        self.save(update_fields=['is_active', 'is_currently_running'])
    
    def is_conflicting(self, other_schedule):
        """
        Check if this schedule conflicts with another schedule.
        
        Two schedules conflict if:
        1. They share at least one screen
        2. Their time ranges overlap
        3. Both are active
        
        Args:
            other_schedule: Another Schedule instance to check against
            
        Returns:
            bool: True if schedules conflict, False otherwise
        """
        # Check if both are active
        if not (self.is_active and other_schedule.is_active):
            return False
        
        # Check if they share any screens
        shared_screens = self.screens.filter(id__in=other_schedule.screens.values_list('id', flat=True))
        if not shared_screens.exists():
            return False
        
        # Check if time ranges overlap
        # Overlap occurs if: start1 < end2 AND start2 < end1
        if self.start_time < other_schedule.end_time and other_schedule.start_time < self.end_time:
            return True
        
        # For recurring schedules, check if they would overlap in the future
        if self.repeat_type != 'none' or other_schedule.repeat_type != 'none':
            # This is a simplified check - full implementation would need to check
            # all future occurrences based on repeat_type
            if self.start_time < other_schedule.end_time and other_schedule.start_time < self.end_time:
                return True
        
        return False
    
    def next_run(self):
        """
        Calculate the next scheduled run time based on repeat_type.
        
        Returns:
            datetime: Next scheduled run time, or None if one-time and past
        """
        now = timezone.now()
        
        # If one-time schedule and already past, return None
        if self.repeat_type == 'none':
            if self.start_time > now:
                return self.start_time
            return None
        
        # If schedule hasn't started yet, return start_time
        if self.start_time > now:
            return self.start_time
        
        # Calculate next run based on repeat type
        if self.repeat_type == 'daily':
            # Find next occurrence today or tomorrow
            next_run = self.start_time
            while next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        
        elif self.repeat_type == 'weekly':
            # Find next occurrence (same day of week)
            next_run = self.start_time
            while next_run <= now:
                next_run += timedelta(weeks=1)
            return next_run
        
        elif self.repeat_type == 'monthly':
            # Find next occurrence (same day of month, approximate)
            next_run = self.start_time
            while next_run <= now:
                # Add approximately one month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
            return next_run
        
        return None
    
    def mark_executed(self):
        """Mark schedule as executed at current time"""
        self.last_executed_at = timezone.now()
        self.is_currently_running = True
        self.save(update_fields=['last_executed_at', 'is_currently_running'])
    
    def mark_completed(self):
        """Mark schedule as completed (no longer running)"""
        self.is_currently_running = False
        self.save(update_fields=['is_currently_running'])
    
    # Property Methods
    @property
    def duration(self):
        """Calculate duration of schedule in seconds"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
    @property
    def is_past(self):
        """Check if schedule has passed (for one-time schedules)"""
        if self.repeat_type == 'none':
            return timezone.now() > self.end_time
        return False
    
    @property
    def is_running_now(self):
        """Check if schedule should be running right now"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        
        # For one-time schedules
        if self.repeat_type == 'none':
            return self.start_time <= now <= self.end_time
        
        # For recurring schedules, check if current time falls within the time window
        # This is a simplified check - full implementation would need to check
        # if current time matches the repeat pattern
        start_time_today = self.start_time.time()
        end_time_today = self.end_time.time()
        current_time = now.time()
        
        if self.repeat_type == 'daily':
            return start_time_today <= current_time <= end_time_today
        
        elif self.repeat_type == 'weekly':
            # Check if same day of week
            if now.weekday() == self.start_time.weekday():
                return start_time_today <= current_time <= end_time_today
        
        elif self.repeat_type == 'monthly':
            # Check if same day of month
            if now.day == self.start_time.day:
                return start_time_today <= current_time <= end_time_today
        
        return False
    
    @property
    def screens_count(self):
        """Get count of screens assigned to this schedule"""
        return self.screens.count()
