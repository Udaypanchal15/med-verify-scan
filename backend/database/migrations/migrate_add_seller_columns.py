"""
Database migration: Add missing columns to sellers table
Run this if sellers table doesn't have license_type and other columns
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from database import get_db, execute_query
from flask import Flask

# Load environment variables
load_dotenv()

def migrate_add_seller_columns():
    """Add missing columns to sellers table"""
    
    # Create a minimal Flask app for database initialization
    app = Flask(__name__)
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    print("=" * 60)
    print("Sellers Table Migration")
    print("Adding missing columns if they don't exist")
    print("=" * 60)
    
    try:
        # Get database connection
        from database import init_db
        init_db(app)
        print("\n✓ Database connection established")
        
        # Add missing columns
        migrations = [
            ("license_type", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS license_type VARCHAR(100)"),
            ("license_expiry", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS license_expiry DATE"),
            ("gstin", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS gstin VARCHAR(50)"),
            ("address", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS address TEXT"),
            ("authorized_person", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS authorized_person VARCHAR(255)"),
            ("authorized_person_contact", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS authorized_person_contact VARCHAR(20)"),
            ("company_website", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS company_website TEXT"),
            ("documents", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS documents JSONB"),
            ("document_checksums", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS document_checksums JSONB"),
            ("submission_date", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS submission_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
            ("viewed_at", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS viewed_at TIMESTAMP WITH TIME ZONE"),
            ("verifying_at", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS verifying_at TIMESTAMP WITH TIME ZONE"),
            ("rejected_at", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMP WITH TIME ZONE"),
            ("admin_remarks", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS admin_remarks TEXT"),
            ("required_changes", "ALTER TABLE sellers ADD COLUMN IF NOT EXISTS required_changes TEXT"),
        ]
        
        print("\nAdding columns to sellers table:")
        for col_name, migration_sql in migrations:
            try:
                execute_query(migration_sql)
                print(f"  ✓ Added/verified column: {col_name}")
            except Exception as e:
                print(f"  ! {col_name}: {str(e)}")
        
        # Check for duplicate emails in users table
        print("\n" + "=" * 60)
        print("Checking for duplicate emails in users table...")
        print("=" * 60)
        
        query = """
            SELECT LOWER(email), COUNT(*) as count
            FROM users
            GROUP BY LOWER(email)
            HAVING COUNT(*) > 1
        """
        result = execute_query(query, fetch_all=True)
        
        if result:
            print(f"\n⚠ Found {len(result)} duplicate email(s):")
            for row in result:
                email, count = row[0], row[1]
                print(f"  - {email}: {count} accounts")
            
            print("\nThese duplicates will cause 'email already exists' errors.")
            print("You may need to manually delete duplicate accounts.")
            return False
        else:
            print("✓ No duplicate emails found")
        
        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Register new sellers with all required fields")
        print("2. Try registering with a fresh email again")
        print("3. Submit seller KYC applications without errors")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_add_seller_columns()
    sys.exit(0 if success else 1)
