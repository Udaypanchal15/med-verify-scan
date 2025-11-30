"""
Script to create an admin user
Usage: python scripts/create_admin.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from database import init_db
from database.models import User
from services.auth import hash_password
from flask import Flask

# Load environment variables
load_dotenv()

def create_admin_user(email: str, password: str):
    """Create an admin user"""
    # Create a minimal Flask app for database initialization
    app = Flask(__name__)
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    # Initialize database
    try:
        init_db(app)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    
    # Check if user already exists
    existing_user = User.get_by_email(email)
    if existing_user:
        print(f"User with email {email} already exists")
        # Update role to admin if not already admin
        if existing_user.get('role') != 'admin':
            print(f"Updating user role to admin...")
            # Note: We would need an update method in User model
            # For now, we'll just inform the user
            print("Please update the user role manually in the database")
        else:
            print("User is already an admin")
        return False
    
    # Create admin user
    password_hash = hash_password(password)
    user = User.create(email, password_hash, role='admin', timezone='UTC')
    
    if user:
        print(f"Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Role: admin")
        print(f"User ID: {user['id']}")
        return True
    else:
        print("Failed to create admin user")
        return False

if __name__ == '__main__':
    import getpass
    
    print("=" * 50)
    print("Create Admin User")
    print("=" * 50)
    
    email = input("Enter admin email: ").strip().lower()
    if not email:
        print("Email is required")
        sys.exit(1)
    
    password = getpass.getpass("Enter admin password: ")
    if not password:
        print("Password is required")
        sys.exit(1)
    
    confirm_password = getpass.getpass("Confirm admin password: ")
    if password != confirm_password:
        print("Passwords do not match")
        sys.exit(1)
    
    if len(password) < 8:
        print("Password must be at least 8 characters long")
        sys.exit(1)
    
    success = create_admin_user(email, password)
    if success:
        print("\nAdmin user created successfully!")
        print("You can now log in with these credentials.")
    else:
        print("\nFailed to create admin user")
        sys.exit(1)



