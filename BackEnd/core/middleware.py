"""
JSON Error Response Middleware

Ensures all API errors return JSON responses instead of HTML.
This is critical for enterprise-grade error handling.
"""
import json
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class JSONErrorResponseMiddleware(MiddlewareMixin):
    """
    Middleware to ensure all API errors return JSON responses.
    
    This middleware catches exceptions and converts them to JSON responses
    with a consistent format:
    {
        "error": "error_code",
        "message": "Human-readable message",
        "details": {}
    }
    """
    
    def process_exception(self, request, exception):
        """
        Process exceptions and return JSON responses for API requests.
        """
        # Only handle API requests (those starting with /api/)
        if not request.path.startswith('/api/'):
            return None  # Let Django handle non-API errors normally
        
        # Handle DRF exceptions
        if isinstance(exception, APIException):
            return JsonResponse({
                'error': exception.get_codes() if hasattr(exception, 'get_codes') else 'api_error',
                'message': str(exception.detail) if hasattr(exception, 'detail') else str(exception),
                'details': exception.detail if isinstance(exception.detail, dict) else {}
            }, status=exception.status_code)
        
        # Handle other exceptions
        error_code = type(exception).__name__
        error_message = str(exception)
        
        # Log the error with context
        logger.error(
            f"API Error: {error_code} - {error_message}",
            exc_info=True,
            extra={
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
                'endpoint': request.path,
                'method': request.method,
                'organization': getattr(request.user, 'organization', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
                'action_type': 'api_error',
            }
        )
        
        # Return JSON error response
        return JsonResponse({
            'error': error_code.lower().replace('exception', ''),
            'message': error_message or 'An unexpected error occurred',
            'details': {}
        }, status=500)


def drf_exception_handler(exc, context):
    """
    Custom DRF exception handler that ensures JSON responses.
    
    This is used by DRF's EXCEPTION_HANDLER setting.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Ensure response is JSON
        if hasattr(response, 'data'):
            # Format the response data
            custom_response_data = {
                'error': response.data.get('error', 'api_error'),
                'message': response.data.get('detail') or response.data.get('message') or 'An error occurred',
                'details': response.data
            }
            response.data = custom_response_data
    
    return response

