"""
Security middleware for rate limiting, input validation, and security headers
"""
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import hashlib
import re

# Simple in-memory rate limiting (use Redis in production)
rate_limit_store = {}

def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    Rate limiting decorator
    max_requests: Maximum number of requests
    window_seconds: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            client_id = get_client_id()
            
            # Check rate limit
            key = f"{request.endpoint}:{client_id}"
            now = datetime.now()
            
            if key in rate_limit_store:
                requests, window_start = rate_limit_store[key]
                
                # Reset window if expired
                if (now - window_start).seconds > window_seconds:
                    rate_limit_store[key] = ([], now)
                    requests = []
                else:
                    requests = [r for r in requests if (now - r).seconds < window_seconds]
            else:
                requests = []
                window_start = now
                rate_limit_store[key] = (requests, window_start)
            
            # Check if limit exceeded
            if len(requests) >= max_requests:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {max_requests} requests per {window_seconds} seconds"
                }), 429
            
            # Add current request
            requests.append(now)
            rate_limit_store[key] = (requests, window_start)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_client_id():
    """Get client identifier for rate limiting"""
    # Use IP address and User-Agent
    ip = request.remote_addr or 'unknown'
    user_agent = request.headers.get('User-Agent', 'unknown')
    return hashlib.md5(f"{ip}:{user_agent}".encode()).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    return text.strip()

def validate_json_schema(data: dict, schema: dict) -> tuple[bool, str]:
    """
    Validate JSON data against schema
    Returns (is_valid, error_message)
    """
    for field, rules in schema.items():
        required = rules.get('required', False)
        field_type = rules.get('type')
        min_length = rules.get('min_length')
        max_length = rules.get('max_length')
        pattern = rules.get('pattern')
        
        # Check required fields
        if required and field not in data:
            return False, f"Field '{field}' is required"
        
        if field in data:
            value = data[field]
            
            # Check type
            if field_type and not isinstance(value, field_type):
                return False, f"Field '{field}' must be of type {field_type.__name__}"
            
            # Check string length
            if isinstance(value, str):
                if min_length and len(value) < min_length:
                    return False, f"Field '{field}' must be at least {min_length} characters"
                if max_length and len(value) > max_length:
                    return False, f"Field '{field}' must be at most {max_length} characters"
                
                # Check pattern
                if pattern and not re.match(pattern, value):
                    return False, f"Field '{field}' does not match required pattern"
    
    return True, ""

def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

def validate_request_size(max_size: int = 10 * 1024 * 1024):
    """Validate request size"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.content_length and request.content_length > max_size:
                return jsonify({
                    "error": "Request too large",
                    "message": f"Maximum size is {max_size / 1024 / 1024}MB"
                }), 413
            return f(*args, **kwargs)
        return decorated_function
    return decorator



