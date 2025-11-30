import os
import sys
sys.path.insert(0, os.getcwd())

os.environ['DATABASE_URL'] = 'dbname=medverify user=postgres password=Uday@2005 host=127.0.0.1 port=5432 sslmode=disable'

from database import execute_query

print("=" * 70)
print("DATABASE MIGRATION: Add Missing Seller Columns")
print("=" * 70 + "\n")

try:
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
    print("Checking for duplicate emails...")
    print("=" * 70 + "\n")
    
    query = """
        SELECT LOWER(email), COUNT(*) as count
        FROM users
        GROUP BY LOWER(email)
        HAVING COUNT(*) > 1
    """
    
    result = execute_query(query, fetch_all=True)
    
    if result:
        print(f"⚠ Found {len(result)} duplicate email(s):\n")
        for row in result:
            email = row[0]
            count = row[1]
            print(f"  • {email}: {count} accounts")
        print("\nFix: Delete the older duplicate accounts\n")
    else:
        print("✓ No duplicate emails found\n")
    
    print("=" * 70)
    print("✓ MIGRATION COMPLETE!")
    print("=" * 70)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
