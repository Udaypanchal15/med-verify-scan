"""
Authentication service with password hashing and JWT token management
"""
import bcrypt
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token, create_refresh_token
from database.models import User
from typing import Optional, Dict, Any

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def register_user(email: str, password: str, role: str = 'user', timezone: str = 'UTC') -> Dict[str, Any]:
    """
    Register a new user
    Returns user data and tokens if successful, None if user already exists
    """
    # Check if user already exists
    existing_user = User.get_by_email(email)
    if existing_user:
        return None
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    user = User.create(email, password_hash, role, timezone)
    if not user:
        return None
    
    # Generate tokens
    access_token = create_access_token(
        identity=str(user['id']),
        additional_claims={"role": user['role'], "email": user['email']}
    )
    refresh_token = create_refresh_token(
        identity=str(user['id']),
        additional_claims={"role": user['role'], "email": user['email']}
    )
    
    return {
        "user": {
            "id": str(user['id']),
            "email": user['email'],
            "role": user['role'],
            "timezone": user['timezone'],
            "created_at": user['created_at'].isoformat() if user.get('created_at') else None
        },
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def login_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user and return tokens
    Returns user data and tokens if successful, None if authentication fails
    """
    # Get user by email
    user = User.get_by_email(email)
    if not user:
        return None
    
    # Check if user is active
    if not user.get('is_active', True):
        return None
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        return None
    
    # Update last login
    User.update_last_login(str(user['id']))
    
    # Generate tokens
    access_token = create_access_token(
        identity=str(user['id']),
        additional_claims={"role": user['role'], "email": user['email']}
    )
    refresh_token = create_refresh_token(
        identity=str(user['id']),
        additional_claims={"role": user['role'], "email": user['email']}
    )
    
    return {
        "user": {
            "id": str(user['id']),
            "email": user['email'],
            "role": user['role'],
            "timezone": user['timezone'],
            "last_login": user.get('last_login').isoformat() if user.get('last_login') else None
        },
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def refresh_access_token(user_id: str) -> Dict[str, Any]:
    """
    Create a new access token from a refresh token
    """
    user = User.get_by_id(user_id)
    if not user or not user.get('is_active', True):
        return None
    
    access_token = create_access_token(
        identity=user_id,
        additional_claims={"role": user['role'], "email": user['email']}
    )
    
    return {
        "access_token": access_token
    }

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID (for protected routes)"""
    user = User.get_by_id(user_id)
    if not user:
        return None
    
    # Remove sensitive data
    user_dict = dict(user)
    user_dict.pop('password_hash', None)
    user_dict['id'] = str(user_dict['id'])
    
    return user_dict



