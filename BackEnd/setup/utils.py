"""
Utility functions for setup/installation process.
"""
import os
from pathlib import Path
from django.conf import settings


def get_installed_lock_path():
    """Get the path to the installation lock file."""
    return Path(settings.BASE_DIR) / 'installed.lock'


def is_installed():
    """
    Check if installation has been completed by checking for installed.lock file.
    
    Returns:
        bool: True if installed.lock exists, False otherwise
    """
    lock_path = get_installed_lock_path()
    return lock_path.exists()


def mark_as_installed():
    """
    Mark installation as completed by creating the installed.lock file.
    
    Returns:
        bool: True if lock file was created successfully, False otherwise
    """
    try:
        lock_path = get_installed_lock_path()
        lock_path.touch()
        return lock_path.exists()
    except Exception:
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
