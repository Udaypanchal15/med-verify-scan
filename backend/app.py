from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Import database initialization
from database import init_db, close_pool

# Import blueprints
from routes.auth_routes import auth_bp
from routes.scan_routes import scan_bp
from routes.medicine_routes import medicine_bp
from routes.reminder_routes import reminder_bp
# from routes.blockchain_routes import blockchain_bp
from routes.seller_routes import seller_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 86400))
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

# CORS Configuration
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
CORS(app, origins=cors_origins, supports_credentials=True)

# Initialize JWT
jwt = JWTManager(app)

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": "Token has expired",
        "message": "Please refresh your token or log in again"
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "error": "Invalid token",
        "message": "Please provide a valid token"
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "error": "Authorization required",
        "message": "Please provide a valid token"
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": "Fresh token required",
        "message": "Please refresh your token"
    }), 401

# Initialize Database
try:
    init_db(app)
    app.logger.info("Database initialized successfully")
except Exception as e:
    app.logger.error(f"Failed to initialize database: {e}")
    # Continue without database for development (will fail on DB operations)

# Setup Logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Medicine Verification System startup')

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(scan_bp)
app.register_blueprint(medicine_bp)
app.register_blueprint(reminder_bp)
# app.register_blueprint(blockchain_bp)
app.register_blueprint(seller_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def home():
    return {"message": "Medicine Scanner Backend Running ✅", "version": "1.0.0"}

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}

@app.after_request
def after_request(response):
    """Add security headers to all responses"""
    from middleware.security import add_security_headers
    return add_security_headers(response)

@app.teardown_appcontext
def close_db(error):
    """Close database connections on app teardown"""
    # Connection pool handles cleanup automatically
    pass

# Start reminder worker if enabled
if os.getenv('ENABLE_REMINDER_WORKER', 'False').lower() == 'true':
    try:
        from services.reminder_worker import start_reminder_worker
        scheduler = start_reminder_worker()
        if scheduler:
            app.logger.info("Reminder worker started")
    except Exception as e:
        app.logger.error(f"Failed to start reminder worker: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
