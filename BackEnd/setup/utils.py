"""
Utility functions for setup/installation process.
"""
import os
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


def get_installed_lock_path():
    """Get the path to the installation lock file.
    
    Uses INSTALLATION_STATE_DIR (Docker volume mount) or BASE_DIR for local dev.
    """
    state_dir = getattr(settings, 'INSTALLATION_STATE_DIR', settings.BASE_DIR)
    return Path(state_dir) / 'installed.lock'


def is_installed():
    """
    Check if installation has been completed by checking for installed.lock file.
    
    Returns:
        bool: True if installed.lock exists and is a file, False otherwise
    """
    lock_path = get_installed_lock_path()
    return lock_path.is_file()


def mark_as_installed():
    """
    Mark installation as completed by creating the installed.lock file.
    
    Returns:
        bool: True if lock file was created successfully, False otherwise
    """
    try:
        lock_path = get_installed_lock_path()
        parent = lock_path.parent
        # Ensure parent directory exists (required for Docker volume mount)
        parent.mkdir(parents=True, exist_ok=True)
        lock_path.touch()
        if lock_path.is_file():
            logger.info("Installation lock file created at %s", lock_path)
            return True
        logger.error("Lock file creation failed: path exists but is not a file: %s", lock_path)
        return False
    except PermissionError as e:
        logger.error("Permission denied creating installed.lock at %s: %s", lock_path, e)
        return False
    except Exception as e:
        logger.exception("Failed to create installed.lock: %s", e)
        return False


def reset_installation():
    """
    Reset installation by removing the lock file (for testing/debugging).
    
    Returns:
        bool: True if lock file was removed successfully, False otherwise
    """
    try:
        lock_path = get_installed_lock_path()
        if lock_path.exists():
            lock_path.unlink()
        return not lock_path.exists()
    except Exception:
        return False
