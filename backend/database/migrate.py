"""
Migration: Add missing seller columns using app context
"""
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migration():
    # Load environment
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
    
    # Import after loading env
    from flask import Flask
    from database import init_db, execute_query
    
    app = Flask(__name__)
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    print("=" * 70)
    print("DATABASE MIGRATION: Add Missing Seller Columns")
    print("=" * 70)
    
    try:
        init_db(app)
        print("✓ Connected to database\n")
        
        # Add columns
        columns = {
            "license_type": "VARCHAR(100)",
            "license_expiry": "DATE",
            "gstin": "VARCHAR(50)",
            "address": "TEXT",
            "authorized_person": "VARCHAR(255)",
            "authorized_person_contact": "VARCHAR(20)",
            "company_website": "TEXT",
            "documents": "JSONB",
            "document_checksums": "JSONB",
            "submission_date": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "viewed_at": "TIMESTAMP WITH TIME ZONE",
            "verifying_at": "TIMESTAMP WITH TIME ZONE",
            "rejected_at": "TIMESTAMP WITH TIME ZONE",
            "admin_remarks": "TEXT",
            "required_changes": "TEXT",
        }
        
        print("Adding columns to sellers table...")
        for col_name, col_type in columns.items():
            sql = f"ALTER TABLE sellers ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
            try:
                execute_query(sql)
                print(f"  ✓ {col_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"  ✓ {col_name} (already exists)")
                else:
                    print(f"  ! {col_name}: {str(e)[:60]}")
        
        print("\n" + "=" * 70)
        print("Checking for duplicate emails in users table...")
        print("=" * 70 + "\n")
        
        # Check for duplicates
        query = """
            SELECT LOWER(email), COUNT(*) as count
            FROM users
            GROUP BY LOWER(email)
            HAVING COUNT(*) > 1
        """
        
        result = execute_query(query, fetch_all=True)
        
        if result:
            print(f"⚠ WARNING: Found {len(result)} email(s) with duplicate accounts:\n")
            for row in result:
                email = row[0]
                count = row[1]
                print(f"  • {email}: {count} accounts")
            
            print("\n" + "=" * 70)
            print("ISSUE: These duplicate emails will cause registration to fail!")
            print("=" * 70)
            print("\nTo fix, you need to delete duplicate accounts manually.")
            print("For each duplicate, find and delete the older account(s).\n")
            
            return False
        else:
            print("✓ No duplicate emails found\n")
        
        print("=" * 70)
        print("✓ MIGRATION SUCCESSFUL!")
        print("=" * 70)
        print("\nYou can now:")
        print("  1. Register new sellers without column errors")
        print("  2. Register with any fresh email address")
        print("  3. Submit KYC applications with all fields\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    success = run_migration()
    sys.exit(0 if success else 1)
