"""
Quick migration script to add missing seller columns
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate():
    from dotenv import load_dotenv
    import psycopg2
    
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        return False
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("Adding missing columns to sellers table...")
        
        columns = [
            "license_type VARCHAR(100)",
            "license_expiry DATE",
            "gstin VARCHAR(50)",
            "address TEXT",
            "authorized_person VARCHAR(255)",
            "authorized_person_contact VARCHAR(20)",
            "company_website TEXT",
            "documents JSONB",
            "document_checksums JSONB",
            "submission_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "viewed_at TIMESTAMP WITH TIME ZONE",
            "verifying_at TIMESTAMP WITH TIME ZONE",
            "rejected_at TIMESTAMP WITH TIME ZONE",
            "admin_remarks TEXT",
            "required_changes TEXT",
        ]
        
        for col_def in columns:
            col_name = col_def.split()[0]
            try:
                cur.execute(f"ALTER TABLE sellers ADD COLUMN IF NOT EXISTS {col_def}")
                print(f"  ✓ {col_name}")
            except Exception as e:
                print(f"  ! {col_name}: {e}")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
        # Check for duplicate emails
        cur.execute("""
            SELECT LOWER(email), COUNT(*) 
            FROM users 
            GROUP BY LOWER(email) 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cur.fetchall()
        if duplicates:
            print(f"\n⚠ WARNING: Found {len(duplicates)} duplicate email(s):")
            for email, count in duplicates:
                print(f"  - {email}: {count} accounts")
            print("\nThis causes 'email already exists' errors on registration.")
        else:
            print("\n✓ No duplicate emails found")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
