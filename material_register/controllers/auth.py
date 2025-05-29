from odoo import http
from odoo.http import request, Response
import json
import base64
import werkzeug.wrappers
import logging
from functools import wraps

_logger = logging.getLogger(__name__)


def invalid_response(message, status=400, code=None):
    """
    Return invalid response for JSON routes
    """
    response_data = {
        'success': False,
        'error': {
            'message': message,
            'code': code or str(status)
        }
    }
    
    # For JSON routes, we return the Python dict directly
    return response_data


def valid_response(data, status=200, message=None, meta=None):
    """
    Return valid response for JSON routes
    """
    response_data = {
        'success': True,
        'data': data
    }
    
    if message:
        response_data['message'] = message
        
    if meta:
        response_data['meta'] = meta
        
    # For JSON routes, we return the Python dict directly
    return response_data


def authenticate_api(func):
    """
    Decorator to authenticate API requests
    Supports both token-based (Bearer) and Basic authentication
    """
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header:
            return invalid_response('Missing authorization header', 401)
        
        # Handle Bearer token (API Key) authentication
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # First try with our custom API key field
            
                
            # Then try with Odoo's built-in API key system
            try:
                # Odoo 14 requires a non-empty scope parameter
                user_id = request.env['res.users.apikeys'].sudo()._check_credentials(scope='material_register_api', key=token)
                if user_id:
                    user = request.env['res.users'].sudo().browse(user_id)
                    request.env.user = user
                    request.uid = user.id
                    return func(self, *args, **kwargs)
            except Exception as e:
                _logger.warning(f"API key authentication error: {str(e)}")
                
            return invalid_response('Invalid API key', 401)
        
        # Handle Basic authentication (username/password)
        elif auth_header.startswith('Basic '):
            auth_decoded = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
            username, password = auth_decoded.split(':')
            
            try:
                uid = request.session.authenticate(request.session.db, username, password)
                if not uid:
                    return invalid_response('Authentication failed: Invalid username or password', 401)
                
                return func(self, *args, **kwargs)
            except Exception as e:
                _logger.exception("Authentication error")
                return invalid_response(f'Authentication error: {str(e)}', 401)
        
        else:
            return invalid_response('Unsupported authorization method', 401)
    
    return wrapped