# Comprehensive File Validation

This module provides enterprise-grade file validation for ScreenGram's Content upload system.

## Features

### Security Validation
- **MIME Type Verification**: Uses `python-magic` to verify actual file content (magic numbers), not just file extensions
- **File Signature Detection**: Detects executable files (ELF, PE, Mach-O) and dangerous file types
- **Script Injection Detection**: Scans text/HTML files for XSS and script injection patterns
- **Path Traversal Prevention**: Validates and sanitizes filenames

### Hardware Compatibility
- **File Size Limits**: Enforces maximum file sizes per content type (500MB for videos, 50MB for images)
- **Video Resolution Checking**: Uses `ffprobe` to verify video resolution doesn't exceed 4K (3840x2160)
- **Codec Validation**: Checks for supported video codecs (H.264, H.265, VP8, VP9)

### Format Validation
- **Image Format**: Validates image format, dimensions, and integrity using Pillow
- **Video Format**: Validates video format and extracts metadata (duration, resolution, codec)
- **Text/JSON**: Validates text encoding and JSON structure

## Requirements

### Python Dependencies
- `python-magic` or `python-magic-bin` (Windows): For MIME type detection
- `Pillow`: For image validation
- `ffmpeg` (system dependency): For video resolution checking via `ffprobe`

### Installing ffmpeg

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract and add to PATH
3. Or use: `choco install ffmpeg` (if Chocolatey is installed)

**Linux:**
```bash
sudo apt-get install ffmpeg  # Debian/Ubuntu
sudo yum install ffmpeg       # CentOS/RHEL
```

**macOS:**
```bash
brew install ffmpeg
```

## Usage

The validator is automatically used when uploading content through the Content upload endpoint.

### Backend Validation

```python
from content_validation.validators import ContentValidator

result = ContentValidator.validate_content(
    file_obj=uploaded_file,
    content_type='image',  # or 'video', 'text', etc.
    filename='image.jpg'
)
```

### Frontend Validation

The `FileUploader` component automatically:
- Reads image dimensions and checks aspect ratio
- Reads video duration and resolution
- Validates before upload
- Shows warnings for aspect ratio mismatches

## Error Messages

The validator provides detailed, user-friendly error messages:

- **MIME Type Mismatch**: "The file 'video.mp4' is a fake JPG and has been rejected for security reasons"
- **Resolution Exceeded**: "Video resolution (4096x2160) exceeds maximum allowed (3840x2160)"
- **File Size**: "File size (600.50 MB) exceeds maximum allowed size (500.00 MB)"
- **Security Violation**: "ELF executable detected (Linux/Unix executable)"

## Configuration

Validation limits can be configured in `content_validation/settings.py`:

```python
MAX_FILE_SIZES = {
    'image': 50 * 1024 * 1024,   # 50 MB
    'video': 500 * 1024 * 1024,  # 500 MB
}

MAX_VIDEO_RESOLUTION = {
    'width': 3840,
    'height': 2160
}
```

