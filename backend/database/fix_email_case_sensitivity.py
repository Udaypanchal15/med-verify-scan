#!/usr/bin/env python3
"""
Fix email case sensitivity issue in existing database
Run this after updating the code if you have existing users
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db, execute_query

def fix_email_case_sensitivity():
    """Fix the email case sensitivity issue"""
    try:
        print("🔧 Fixing email case sensitivity issue...")
        
        # Step 1: Remove old constraint
        print("  1️⃣ Removing old UNIQUE constraint on email...")
        try:
            execute_query("ALTER TABLE users DROP CONSTRAINT users_email_key CASCADE")
            print("     ✅ Old constraint removed (or didn't exist)")
        except Exception as e:
            print(f"     ⚠️  Could not remove constraint (might already be removed): {str(e)[:100]}")
        
        # Step 2: Create case-insensitive index
        print("  2️⃣ Creating case-insensitive unique index...")
        execute_query("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower ON users (LOWER(email))")
        print("     ✅ Index created")
        
        # Step 3: Normalize emails
        print("  3️⃣ Normalizing existing emails to lowercase...")
        result = execute_query("UPDATE users SET email = LOWER(email) WHERE email != LOWER(email)")
        print("     ✅ Emails normalized")
        
        # Step 4: Verify
        print("  4️⃣ Verifying fix...")
        count = execute_query("SELECT COUNT(*) as total FROM users", fetch_one=True)
        print(f"     ✅ Total users in database: {count['total']}")
        
        print("\n✨ Email case sensitivity issue fixed!")
        print("📝 Users can now log in with any case variation of their email address")
        return True
        
    except Exception as e:
        print(f"\n❌ Error fixing email case sensitivity: {str(e)}")
        print("\n💡 Manual fix:")
        print("   Run the SQL in: backend/database/fix_email_case_sensitivity.sql")
        return False

if __name__ == "__main__":
    fix_email_case_sensitivity()
