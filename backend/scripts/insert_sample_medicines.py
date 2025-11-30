#!/usr/bin/env python
"""
Script to insert sample medicines for user dashboard
Based on Indian Medicine Dataset
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from database import init_db, execute_query
from database.models import Medicine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def insert_sample_medicines():
    """Insert 10 sample medicines from Indian dataset"""
    
    app = Flask(__name__)
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    try:
        init_db(app)
        print("✓ Database initialized successfully\n")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False
    
    # Sample medicines data - 10 medicines across 5 categories
    medicines_data = [
        # Fever (2)
        {
            'name': 'Crocin 500mg Tablet',
            'batch_no': 'CROC-2024-001',
            'mfg_date': '2024-01-15',
            'expiry_date': '2027-01-15',
            'dosage': 'Tablet',
            'strength': '500mg',
            'category': 'Fever',
            'description': 'Paracetamol based fever reducer - trusted by millions',
            'stock_quantity': 150,
            'delivery_status': 'in_stock',
        },
        {
            'name': 'Ibugesic 400mg Tablet',
            'batch_no': 'IBUG-2024-002',
            'mfg_date': '2024-02-10',
            'expiry_date': '2027-02-10',
            'dosage': 'Tablet',
            'strength': '400mg',
            'category': 'Fever',
            'description': 'Ibuprofen-based pain and fever relief',
            'stock_quantity': 200,
            'delivery_status': 'in_stock',
        },
        # Diabetes (2)
        {
            'name': 'Glycomet 500mg Tablet',
            'batch_no': 'GLYC-2024-003',
            'mfg_date': '2024-03-05',
            'expiry_date': '2027-03-05',
            'dosage': 'Tablet',
            'strength': '500mg',
            'category': 'Diabetes',
            'description': 'Metformin-based diabetes management - first-line therapy',
            'stock_quantity': 180,
            'delivery_status': 'in_stock',
        },
        {
            'name': 'Amaryl 2mg Tablet',
            'batch_no': 'AMAR-2024-004',
            'mfg_date': '2024-04-12',
            'expiry_date': '2027-04-12',
            'dosage': 'Tablet',
            'strength': '2mg',
            'category': 'Diabetes',
            'description': 'Glimepiride for type 2 diabetes blood sugar control',
            'stock_quantity': 120,
            'delivery_status': 'in_stock',
        },
        # Heart Disease (2)
        {
            'name': 'Aspirin 75mg Tablet',
            'batch_no': 'ASPR-2024-005',
            'mfg_date': '2024-05-20',
            'expiry_date': '2027-05-20',
            'dosage': 'Tablet',
            'strength': '75mg',
            'category': 'Heart Disease',
            'description': 'Acetylsalicylic acid for cardiac protection and blood thinning',
            'stock_quantity': 250,
            'delivery_status': 'in_stock',
        },
        {
            'name': 'Atorva 10mg Tablet',
            'batch_no': 'ATOR-2024-006',
            'mfg_date': '2024-06-08',
            'expiry_date': '2027-06-08',
            'dosage': 'Tablet',
            'strength': '10mg',
            'category': 'Heart Disease',
            'description': 'Atorvastatin for cholesterol management and heart health',
            'stock_quantity': 140,
            'delivery_status': 'in_stock',
        },
        # High Blood Pressure (2)
        {
            'name': 'Inderal LA 40mg Capsule',
            'batch_no': 'INDE-2024-007',
            'mfg_date': '2024-07-15',
            'expiry_date': '2027-07-15',
            'dosage': 'Capsule',
            'strength': '40mg',
            'category': 'High Blood Pressure',
            'description': 'Propranolol beta-blocker for hypertension control',
            'stock_quantity': 95,
            'delivery_status': 'in_stock',
        },
        {
            'name': 'Lisinopril 10mg Tablet',
            'batch_no': 'LISI-2024-008',
            'mfg_date': '2024-08-22',
            'expiry_date': '2027-08-22',
            'dosage': 'Tablet',
            'strength': '10mg',
            'category': 'High Blood Pressure',
            'description': 'ACE inhibitor for blood pressure and heart failure management',
            'stock_quantity': 165,
            'delivery_status': 'in_stock',
        },
        # Cough & Cold (2)
        {
            'name': 'Dolo 650mg Tablet',
            'batch_no': 'DOLO-2024-009',
            'mfg_date': '2024-09-10',
            'expiry_date': '2027-09-10',
            'dosage': 'Tablet',
            'strength': '650mg',
            'category': 'Cough & Cold',
            'description': 'Paracetamol for cold symptoms and body aches relief',
            'stock_quantity': 220,
            'delivery_status': 'in_stock',
        },
        {
            'name': 'Ciprocet C Cough Syrup',
            'batch_no': 'CIPR-2024-010',
            'mfg_date': '2024-10-05',
            'expiry_date': '2026-10-05',
            'dosage': 'Syrup',
            'strength': '100ml',
            'category': 'Cough & Cold',
            'description': 'Effective cough suppressant for dry and productive cough relief',
            'stock_quantity': 80,
            'delivery_status': 'in_stock',
        },
    ]
    
    # Get a seller to associate medicines with
    from database.models import Seller
    
    try:
        sellers = Seller.get_all_approved()
        if not sellers:
            print("✗ No approved sellers found in database")
            print("  Please run: CREATE_TEST_SELLER_PROFILE.sql first")
            return False
        
        seller_id = sellers[0]['id']
        print(f"✓ Using seller: {sellers[0]['company_name']} ({seller_id})\n")
    except Exception as e:
        print(f"✗ Error getting sellers: {e}")
        return False
    
    # Insert medicines
    inserted_count = 0
    skipped_count = 0
    
    print("Inserting sample medicines...\n")
    
    for med_data in medicines_data:
        try:
            # Check if medicine already exists
            query = "SELECT id FROM medicines WHERE name = %s"
            result = execute_query(query, (med_data['name'],), fetch_one=True)
            
            if result:
                print(f"  ⊘ {med_data['name']} (already exists)")
                skipped_count += 1
                continue
            
            # Create medicine
            medicine = Medicine.create(
                seller_id=seller_id,
                name=med_data['name'],
                batch_no=med_data['batch_no'],
                mfg_date=med_data['mfg_date'],
                expiry_date=med_data['expiry_date'],
                dosage=med_data['dosage'],
                strength=med_data['strength'],
                category=med_data['category'],
                description=med_data['description'],
                stock_quantity=med_data['stock_quantity'],
                delivery_status=med_data['delivery_status']
            )
            
            if medicine:
                # Approve the medicine
                approve_query = """
                    UPDATE medicines 
                    SET approval_status = 'approved', 
                        approved_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                execute_query(approve_query, (medicine['id'],))
                
                print(f"  ✓ {med_data['name']} ({med_data['category']})")
                inserted_count += 1
            else:
                print(f"  ✗ Failed to create {med_data['name']}")
                skipped_count += 1
                
        except Exception as e:
            print(f"  ✗ Error inserting {med_data['name']}: {e}")
            skipped_count += 1
    
    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  ✓ Inserted: {inserted_count} medicines")
    print(f"  ⊘ Skipped: {skipped_count} medicines")
    print(f"{'='*60}\n")
    
    # Show summary by category
    try:
        query = """
            SELECT category, COUNT(*) as count
            FROM medicines 
            WHERE category IN ('Fever', 'Diabetes', 'Heart Disease', 'High Blood Pressure', 'Cough & Cold')
            GROUP BY category
            ORDER BY category
        """
        results = execute_query(query, fetch_all=True)
        
        if results:
            print("Medicines by Category:")
            for row in results:
                print(f"  • {row['category']}: {row['count']} medicines")
            print()
    except Exception as e:
        print(f"Warning: Could not fetch summary: {e}\n")
    
    return True

if __name__ == '__main__':
    print("\n" + "="*60)
    print("INSERT SAMPLE MEDICINES FOR USER DASHBOARD")
    print("="*60 + "\n")
    
    success = insert_sample_medicines()
    
    if success:
        print("✓ Sample medicines inserted successfully!")
        print("\nYou can now:")
        print("  1. Login as a user")
        print("  2. Go to User Dashboard")
        print("  3. Browse medicines by category")
        print("  4. Search for medicines")
        sys.exit(0)
    else:
        print("✗ Failed to insert sample medicines")
        sys.exit(1)
