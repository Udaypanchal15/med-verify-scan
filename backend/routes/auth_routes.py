"""
Authentication routes: registration, login, token refresh
"""
from flask import Blueprint, request, jsonify
from services.auth import register_user, login_user, refresh_access_token, get_user_by_id
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware.auth import login_required
import re
import os

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str):
    """
    Validate password strength
    Returns (is_valid, error_message)

    Policy can be relaxed for development by setting the environment
    variable `ENFORCE_PASSWORD_POLICY=false`. When relaxed, only a
    minimum length (6) is required. When enforced (default), require
    at least 8 chars, one uppercase, one lowercase and one digit.
    """
    enforce = os.getenv('ENFORCE_PASSWORD_POLICY', 'True').lower() in ('1', 'true', 'yes')

    if not password:
        return False, "Password is required"

    if not enforce:
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        return True, ""

    # Strict policy
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        role = data.get('role', 'user').lower()
        timezone = data.get('timezone', 'UTC')
        
        # Validate email
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password
        if not password:
            return jsonify({"error": "Password is required"}), 400
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Validate role
        if role not in ['user', 'seller', 'admin']:
            return jsonify({"error": "Invalid role. Must be 'user', 'seller', or 'admin'"}), 400
        
        # Only allow 'user' and 'seller' roles for registration
        # Admin users should be created by existing admins
        if role == 'admin':
            return jsonify({"error": "Admin role cannot be self-assigned"}), 403
        
        # Register user
        result = register_user(email, password, role, timezone)
        
        if result is None:
            return jsonify({"error": "User with this email already exists"}), 409
        
        # If seller role, create seller profile only if full KYC data is provided
        if role == 'seller':
            from database.models import Seller
            company_name = data.get('company_name', '').strip()
            license_number = data.get('license_number', '').strip()

            # Only create seller profile if both company_name and license_number are provided
            # Note: Due to database schema limitations, only core fields are stored
            if company_name and license_number:
                seller = Seller.create(
                    user_id=result['user']['id'],
                    company_name=company_name,
                    license_number=license_number
                )
                if seller:
                    result['seller'] = seller
        
        return jsonify({
            "message": "User registered successfully",
            "data": result
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Authenticate user
        result = login_user(email, password)
        
        if result is None:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check seller approval status
        if result['user']['role'] == 'seller':
            from database.models import Seller
            seller = Seller.get_by_user_id(result['user']['id'])
            
            if not seller:
                # Seller doesn't have a profile yet - they need to complete KYC
                return jsonify({
                    "message": "Login successful",
                    "data": result,
                    "seller_status": "no_application"
                }), 200
            
            # Seller has a profile - check their application status
            if seller.get('status') == 'pending':
                result['seller_status'] = 'pending_verification'
            elif seller.get('status') == 'approved':
                result['seller_status'] = 'approved'
            elif seller.get('status') == 'rejected':
                result['seller_status'] = 'rejected'
            elif seller.get('status') == 'changes_required':
                result['seller_status'] = 'changes_required'
            else:
                result['seller_status'] = seller.get('status', 'unknown')
            
            if seller.get('status') == 'rejected':
                return jsonify({
                    "error": "Your seller application has been rejected. Please contact support.",
                    "status": "rejected",
                    "seller_status": seller.get('status')
                }), 403
            
            if seller.get('status') == 'revoked':
                return jsonify({
                    "error": "Your seller account has been revoked. Please contact support.",
                    "status": "revoked",
                    "seller_status": seller.get('status')
                }), 403
        
        return jsonify({
            "message": "Login successful",
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        user_id = get_jwt_identity()
        result = refresh_access_token(user_id)
        
        if result is None:
            return jsonify({"error": "User not found or inactive"}), 401
        
        return jsonify({
            "message": "Token refreshed successfully",
            "data": result
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user_info(current_user, user_id):
    """Get current user information"""
    try:
        # Remove sensitive data
        user_data = {
            "id": str(current_user['id']),
            "email": current_user['email'],
            "role": current_user['role'],
            "timezone": current_user.get('timezone', 'UTC'),
            "created_at": current_user.get('created_at').isoformat() if current_user.get('created_at') else None,
            "last_login": current_user.get('last_login').isoformat() if current_user.get('last_login') else None
        }
        
        return jsonify({
            "message": "User information retrieved successfully",
            "data": user_data
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client-side token removal)
    For server-side token blacklisting, you would need to implement a token blacklist
    """
    return jsonify({
        "message": "Logged out successfully. Please remove tokens on client side."
    }), 200

