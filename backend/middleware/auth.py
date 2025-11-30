"""
Authentication middleware and decorators for role-based access control
"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from database.models import User
from typing import Callable, List

def role_required(*allowed_roles: str):
    """
    Decorator to require specific roles for a route
    Usage: @role_required('admin', 'seller')
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip auth for OPTIONS requests (CORS preflight)
            if request.method == 'OPTIONS':
                return f(*args, **kwargs)

            # Verify JWT token
            verify_jwt_in_request()

            # Get user identity and claims
            user_id = get_jwt_identity()
            claims = get_jwt()
            user_role = claims.get('role')

            # Check if user role is allowed
            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Insufficient permissions",
                    "message": f"Required roles: {', '.join(allowed_roles)}"
                }), 403

            # Get user from database to ensure they exist and are active
            user = User.get_by_id(user_id)
            if not user or not user.get('is_active', True):
                return jsonify({
                    "error": "User not found or inactive"
                }), 401

            # Add user to kwargs for route handlers
            kwargs['current_user'] = user
            kwargs['user_id'] = user_id

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f: Callable) -> Callable:
    """Decorator to require admin role"""
    return role_required('admin')(f)

def seller_required(f: Callable) -> Callable:
    """Decorator to require seller role"""
    return role_required('seller')(f)

def admin_or_seller_required(f: Callable) -> Callable:
    """Decorator to require admin or seller role"""
    return role_required('admin', 'seller')(f)

def login_required(f: Callable) -> Callable:
    """
    Decorator to require authentication (any logged-in user)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verify JWT token
        verify_jwt_in_request()
        
        # Get user identity
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Get user from database
        user = User.get_by_id(user_id)
        if not user or not user.get('is_active', True):
            return jsonify({
                "error": "User not found or inactive"
            }), 401
        
        # Add user to kwargs
        kwargs['current_user'] = user
        kwargs['user_id'] = user_id
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """
    Get current user from JWT token (for use in route handlers)
    Returns user dict or None
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        return user if user and user.get('is_active', True) else None
    except Exception:
        return None



