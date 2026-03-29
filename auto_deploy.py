#!/usr/bin/env python3
"""
Automated Deployment Script for PixelCast Signage

This script handles automated deployments from GitHub:
1. Pulls latest code from main branch
2. Rebuilds and restarts Docker containers
3. Logs all output to deploy_log.txt

Usage:
    python auto_deploy.py [--branch main] [--no-build]

Security:
    This script should be run with appropriate permissions and should only
    be triggered by authenticated webhook requests.
"""

import os
import sys
import subprocess
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Configure logging
LOG_FILE = Path(__file__).parent / 'deploy_log.txt'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class DeploymentError(Exception):
    """Custom exception for deployment errors."""
    pass


def run_command(command, cwd=None, check=True):
    """
    Run a shell command and log the output.
    
    Args:
        command: Command to run (list or string)
        cwd: Working directory (default: project root)
        check: If True, raise exception on non-zero exit code
    
    Returns:
        CompletedProcess object
    """
    if cwd is None:
        cwd = Path(__file__).parent
    
    logger.info(f"Executing: {' '.join(command) if isinstance(command, list) else command}")
    logger.info(f"Working directory: {cwd}")
    
    try:
        if isinstance(command, str):
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                check=check,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
        else:
            result = subprocess.run(
                command,
                cwd=cwd,
                check=check,
                capture_output=True,
                text=True,
                timeout=600
            )
        
        if result.stdout:
            logger.info(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"STDERR:\n{result.stderr}")
        
        return result
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after 600 seconds: {command}")
        raise DeploymentError(f"Command timed out: {command}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}: {command}")
        logger.error(f"Error output: {e.stderr}")
        raise DeploymentError(f"Command failed: {command}")


def check_prerequisites():
    """Check if required tools are available."""
    logger.info("Checking prerequisites...")
    
    # Check git
    try:
        result = run_command(['git', '--version'], check=True)
        logger.info(f"Git version: {result.stdout.strip()}")
    except (DeploymentError, FileNotFoundError):
        raise DeploymentError("Git is not installed or not in PATH")
    
    # Check docker-compose
    try:
        result = run_command(['docker-compose', '--version'], check=True)
        logger.info(f"Docker Compose version: {result.stdout.strip()}")
    except (DeploymentError, FileNotFoundError):
        # Try docker compose (v2)
        try:
            result = run_command(['docker', 'compose', 'version'], check=True)
            logger.info(f"Docker Compose version: {result.stdout.strip()}")
            return 'docker compose'  # Return command format
        except (DeploymentError, FileNotFoundError):
            raise DeploymentError("Docker Compose is not installed or not in PATH")
    
    return 'docker-compose'


def git_pull(branch='main'):
    """Pull latest code from GitHub."""
    logger.info(f"Pulling latest code from branch: {branch}")
    
    try:
        # Fetch latest changes
        run_command(['git', 'fetch', 'origin', branch])
        
        # Check if there are changes
        result = run_command(['git', 'rev-list', '--count', f'HEAD..origin/{branch}'], check=False)
        commits_behind = int(result.stdout.strip()) if result.stdout.strip() else 0
        
        if commits_behind == 0:
            logger.info("Already up to date. No new commits to pull.")
            return False
        
        logger.info(f"Found {commits_behind} new commit(s). Pulling...")
        
        # Pull changes
        run_command(['git', 'pull', 'origin', branch])
        
        # Get latest commit info
        result = run_command(['git', 'log', '-1', '--pretty=format:%h - %s (%an)'])
        logger.info(f"Latest commit: {result.stdout.strip()}")
        
        return True
    except DeploymentError as e:
        logger.error(f"Git pull failed: {e}")
        raise


def docker_compose_up(docker_compose_cmd, build=True):
    """Rebuild and restart Docker containers."""
    logger.info("Starting Docker containers...")
    
    try:
        if build:
            logger.info("Building images and starting containers...")
            if docker_compose_cmd == 'docker compose':
                run_command(['docker', 'compose', 'up', '--build', '-d'])
            else:
                run_command(['docker-compose', 'up', '--build', '-d'])
        else:
            logger.info("Starting containers (no build)...")
            if docker_compose_cmd == 'docker compose':
                run_command(['docker', 'compose', 'up', '-d'])
            else:
                run_command(['docker-compose', 'up', '-d'])
        
        # Check container status
        logger.info("Checking container status...")
        if docker_compose_cmd == 'docker compose':
            result = run_command(['docker', 'compose', 'ps'], check=False)
        else:
            result = run_command(['docker-compose', 'ps'], check=False)
        
        logger.info(f"Container status:\n{result.stdout}")
        
        return True
    except DeploymentError as e:
        logger.error(f"Docker Compose failed: {e}")
        raise


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description='Automated deployment script for PixelCast Signage')
    parser.add_argument('--branch', default='main', help='Git branch to pull from (default: main)')
    parser.add_argument('--no-build', action='store_true', help='Skip Docker image rebuild')
    parser.add_argument('--force', action='store_true', help='Force deployment even if no new commits')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("PixelCast Signage Automated Deployment Started")
    logger.info(f"Timestamp: {datetime.now().strftime(DATE_FORMAT)}")
    logger.info(f"Branch: {args.branch}")
    logger.info(f"Build: {not args.no_build}")
    logger.info("=" * 60)
    
    try:
        # Check prerequisites
        docker_compose_cmd = check_prerequisites()
        
        # Pull latest code
        has_changes = git_pull(args.branch)
        
        if not has_changes and not args.force:
            logger.info("No changes detected. Deployment skipped.")
            logger.info("Use --force to deploy anyway.")
            return 0
        
        # Rebuild and restart containers
        docker_compose_up(docker_compose_cmd, build=not args.no_build)
        
        logger.info("=" * 60)
        logger.info("Deployment completed successfully!")
        logger.info("=" * 60)
        
        return 0
        
    except DeploymentError as e:
        logger.error("=" * 60)
        logger.error(f"Deployment failed: {e}")
        logger.error("=" * 60)
        return 1
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"Unexpected error during deployment: {e}", exc_info=True)
        logger.error("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())

