"""
Diagnose test@test.com account and show what should happen
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

from database.models import User, Seller

def diagnose():
    """Diagnose test@test.com account"""

    print("="*70)
    print("DIAGNOSTIC REPORT FOR test@test.com")
    print("="*70)

    # Check user
    user = User.get_by_email('test@test.com')

    if not user:
        print("\n❌ ISSUE FOUND: User does not exist")
        print("\n🔧 FIX:")
        print("   1. Go to http://localhost:5173/register")
        print("   2. Register with:")
        print("      Email: test@test.com")
        print("      Password: Test1234")
        print("      Role: Seller")
        return

    print("\n✅ USER ACCOUNT EXISTS")
    print(f"   Email: {user['email']}")
    print(f"   Role: {user['role']}")
    print(f"   User ID: {user['id']}")

    if user['role'] != 'seller':
        print(f"\n⚠️  WARNING: User role is '{user['role']}', not 'seller'")
        print("   The seller verification workflow only applies to users with role='seller'")

    # Check seller profile
    seller = Seller.get_by_user_id(user['id'])

    if not seller:
        print("\n❌ SELLER PROFILE NOT FOUND")
        print("\n📋 EXPECTED BEHAVIOR:")
        print("   ✓ Login redirects to: /seller/apply")
        print("   ✓ User must submit KYC application")
        print("   ✓ Cannot access /seller/dashboard")
        print("\n🔧 FIX:")
        print("   1. Login as test@test.com")
        print("   2. Fill out the KYC application form at /seller/apply")
        print("   3. Submit with required documents")
        return

    print("\n✅ SELLER PROFILE EXISTS")
    print(f"   Seller ID: {seller['id']}")
    print(f"   Company: {seller.get('company_name', 'N/A')}")
    print(f"   License: {seller.get('license_number', 'N/A')}")
    print(f"   Status: {seller['status']}")
    print(f"   Created: {seller.get('created_at')}")

    # Show status-specific behavior
    status = seller['status']
    print("\n" + "="*70)
    print(f"CURRENT STATUS: {status.upper()}")
    print("="*70)

    if status == 'pending':
        print("\n📋 EXPECTED BEHAVIOR:")
        print("   ✓ Login redirects to: /seller/status")
        print("   ✓ Shows: Application pending review")
        print("   ✓ Dashboard access: BLOCKED")
        print("   ✓ Can create medicines: NO")
        print("   ✓ Can generate QR codes: NO")
        print("\n👨‍💼 ADMIN ACTIONS AVAILABLE:")
        print("   • Mark as Viewed")
        print("   • Start Verification Process")
        print("   • Approve")
        print("   • Reject")

    elif status == 'viewed':
        print("\n📋 EXPECTED BEHAVIOR:")
        print("   ✓ Login redirects to: /seller/status")
        print("   ✓ Shows: Application viewed by admin")
        print("   ✓ Dashboard access: BLOCKED")
        print("   ✓ Can create medicines: NO")
        print("   ✓ Can generate QR codes: NO")
        print("\n👨‍💼 ADMIN ACTIONS AVAILABLE:")
        print("   • Start Verification Process")
        print("   • Approve")
        print("   • Reject")

    elif status == 'verifying':
        print("\n📋 EXPECTED BEHAVIOR:")
        print("   ✓ Login redirects to: /seller/status")
        print("   ✓ Shows: Application being verified")
        print("   ✓ Dashboard access: BLOCKED")
        print("   ✓ Can create medicines: NO")
        print("   ✓ Can generate QR codes: NO")
        print("\n👨‍💼 ADMIN ACTIONS AVAILABLE:")
        print("   • Approve")
        print("   • Reject")

    elif status == 'approved':
        print("\n📋 EXPECTED BEHAVIOR:")
        print("   ✓ Login redirects to: /seller/dashboard")
        print("   ✓ Shows: Full dashboard access")
        print("   ✓ Dashboard access: ALLOWED ✅")
        print("   ✓ Can create medicines: YES (after generating keys)")
        print("   ✓ Can generate QR codes: YES (after generating keys)")
        print(f"\n   Has public key: {'YES ✅' if seller.get('public_key') else 'NO - Need to generate keys'}")

        if not seller.get('public_key'):
            print("\n🔧 TO GENERATE KEYS:")
            print("   1. Access /seller/dashboard")
            print("   2. Look for 'Generate Keys' button")
            print("   3. Click to generate ECDSA key pair")

        print("\n⚠️  THIS IS CORRECT BEHAVIOR!")
        print("   If the seller is approved, they SHOULD have full access.")
        print("\n   If you want to TEST the verification workflow:")
        print("   Run: python scripts/reset_test_seller_status.py")

    elif status == 'rejected':
        print("\n📋 EXPECTED BEHAVIOR:")
        print("   ✓ Login: BLOCKED with error message")
        print("   ✓ Shows: Application rejected")
        print("   ✓ Dashboard access: BLOCKED")
        print("   ✓ Can create medicines: NO")
        print("   ✓ Can generate QR codes: NO")
        print("\n   User must contact support")

    elif status == 'revoked':
        print("\n📋 EXPECTED BEHAVIOR:")
        print("   ✓ Login: BLOCKED with error message")
        print("   ✓ Shows: Account revoked")
        print("   ✓ Dashboard access: BLOCKED")
        print("   ✓ Can create medicines: NO")
        print("   ✓ Can generate QR codes: NO")
        print("\n   User must contact support")

    else:
        print(f"\n⚠️  UNKNOWN STATUS: {status}")

    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)

    if status == 'approved':
        print("\n✅ Everything is working correctly!")
        print("   The seller is approved and has full access.")
        print("\n   To test the verification workflow from scratch:")
        print("   1. Run: python scripts/reset_test_seller_status.py")
        print("   2. This will set status back to 'pending'")
        print("   3. Then test the admin approval process")

    elif status in ['pending', 'viewed', 'verifying']:
        print("\n✅ Protection is working!")
        print("   Seller cannot access dashboard until approved.")
        print("\n   To approve this seller:")
        print("   1. Login as admin")
        print("   2. Go to /admin/sellers")
        print(f"   3. Find '{seller.get('company_name')}' in Pending tab")
        print("   4. Click 'Approve'")

    elif status in ['rejected', 'revoked']:
        print("\n   To allow this seller to try again:")
        print("   Run: python scripts/reset_test_seller_status.py")

    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        init_standalone_db()
        print()
        diagnose()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
