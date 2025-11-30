"""
Reset test@test.com seller to PENDING status
Use this to test the verification workflow from the beginning
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize database pool for standalone script
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv
import database

# Load environment variables
load_dotenv()

def init_standalone_db():
    """Initialize database connection pool for standalone scripts"""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("\n🔧 FIX:")
        print("   1. Make sure backend/.env file exists")
        print("   2. Check that it contains DATABASE_URL=...")
        print("   3. Example: DATABASE_URL=postgresql://user:pass@localhost/dbname")
        sys.exit(1)

    try:
        database._pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=database_url
        )
        print("✅ Database connection initialized")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

from database import execute_query
from database.models import User, Seller
from datetime import datetime, timezone

def reset_test_seller():
    """Reset test@test.com seller to pending status"""

    # Get user
    user = User.get_by_email('test@test.com')

    if not user:
        print("❌ User test@test.com not found!")
        print("   Please register this account first.")
        return

    print(f"✅ Found user: {user['email']} (Role: {user['role']})")
    print(f"   User ID: {user['id']}")

    # Get seller
    seller = Seller.get_by_user_id(user['id'])

    if not seller:
        print("\n❌ No seller profile found for test@test.com")
        print("   This seller needs to submit a KYC application first.")
        print("\n   Steps to fix:")
        print("   1. Login as test@test.com")
        print("   2. You'll be redirected to /seller/apply")
        print("   3. Fill in and submit the KYC application")
        return

    print(f"\n✅ Found seller profile:")
    print(f"   Seller ID: {seller['id']}")
    print(f"   Company: {seller.get('company_name', 'N/A')}")
    print(f"   Current Status: {seller['status']}")

    if seller['status'] == 'pending':
        print("\n⚠️  Seller is already PENDING")
        print("   No changes needed. The verification workflow should work correctly.")
        return

    # Reset to pending
    print(f"\n🔄 Resetting seller status from '{seller['status']}' to 'pending'...")

    query = """
        UPDATE sellers
        SET
            status = 'pending',
            viewed_at = NULL,
            verifying_at = NULL,
            approved_at = NULL,
            rejected_at = NULL,
            approved_by = NULL,
            admin_remarks = NULL,
            required_changes = NULL
        WHERE id = %s
        RETURNING id, status
    """

    result = execute_query(query, (seller['id'],), fetch_one=True)

    if result:
        print(f"✅ SUCCESS! Seller reset to PENDING status")
        print(f"\n📋 What to test now:")
        print(f"   1. Login as test@test.com")
        print(f"      → Should redirect to /seller/status")
        print(f"      → Status should show PENDING")
        print(f"   2. Try to access /seller/dashboard")
        print(f"      → Should be BLOCKED by SellerDashboardGuard")
        print(f"      → Should redirect to /seller/status")
        print(f"   3. Login as Admin")
        print(f"      → Go to /admin/sellers")
        print(f"      → Find '{seller.get('company_name')}' in Pending tab")
        print(f"      → Click to review")
        print(f"      → Mark as Viewed → Verifying → Approve")
        print(f"   4. Seller can now access dashboard!")
    else:
        print("❌ Failed to update seller status")

if __name__ == "__main__":
    print("="*60)
    print("Reset test@test.com Seller to PENDING Status")
    print("="*60)

    try:
        init_standalone_db()
        print()
        reset_test_seller()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
