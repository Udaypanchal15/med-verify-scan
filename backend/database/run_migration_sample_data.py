#!/usr/bin/env python3
"""Migration script to add email column to sellers and insert sample medicines"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()
db_url = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(db_url)

def run_migration():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Add email column to sellers table
        print("Adding email column to sellers table...")
        cursor.execute('''
            ALTER TABLE sellers
            ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE;
        ''')
        
        # Create unique index for case-insensitive email lookup
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_sellers_email_lower 
            ON sellers (LOWER(email));
        ''')
        
        print("✓ Email column added to sellers table")
        
        # 2. Get approved seller ID (should be test@test.com)
        cursor.execute('''
            SELECT id FROM sellers 
            WHERE status = 'approved' 
            LIMIT 1;
        ''')
        
        seller_result = cursor.fetchone()
        if not seller_result:
            print("✗ No approved seller found! Creating test seller...")
            # We'll use a test seller ID or prompt
            seller_id = None
        else:
            seller_id = seller_result[0]
            print(f"✓ Found approved seller: {seller_id}")
        
        if seller_id:
            # 3. Insert sample medicines (10 total, 2 each for 5 categories)
            print("\nInserting sample medicines...")
            
            sample_medicines = [
                # Fever (2)
                (seller_id, 'Aspirin', 'ASP001', '2024-01-01', '2026-01-01', 'Tablet', '500mg', 'Fever', 100, 'in_stock'),
                (seller_id, 'Paracetamol', 'PAR001', '2024-01-01', '2026-01-01', 'Tablet', '500mg', 'Fever', 150, 'in_stock'),
                
                # Diabetes (2)
                (seller_id, 'Metformin', 'MET001', '2024-01-01', '2026-01-01', 'Tablet', '500mg', 'Diabetes', 80, 'in_stock'),
                (seller_id, 'Glipizide', 'GLI001', '2024-01-01', '2026-01-01', 'Tablet', '10mg', 'Diabetes', 60, 'in_stock'),
                
                # Heart Disease (2)
                (seller_id, 'Aspirin Cardio', 'ASC001', '2024-01-01', '2026-01-01', 'Tablet', '75mg', 'Heart Disease', 120, 'in_stock'),
                (seller_id, 'Atorvastatin', 'ATO001', '2024-01-01', '2026-01-01', 'Tablet', '20mg', 'Heart Disease', 90, 'in_stock'),
                
                # High Blood Pressure (2)
                (seller_id, 'Amlodipine', 'AML001', '2024-01-01', '2026-01-01', 'Tablet', '5mg', 'High Blood Pressure', 110, 'in_stock'),
                (seller_id, 'Lisinopril', 'LIS001', '2024-01-01', '2026-01-01', 'Tablet', '10mg', 'High Blood Pressure', 95, 'in_stock'),
                
                # Cough & Cold (2)
                (seller_id, 'Cough Syrup DM', 'COU001', '2024-01-01', '2026-01-01', 'Syrup', '10mg/5ml', 'Cough & Cold', 70, 'in_stock'),
                (seller_id, 'Cetirizine', 'CET001', '2024-01-01', '2026-01-01', 'Tablet', '10mg', 'Cough & Cold', 140, 'in_stock'),
            ]
            
            insert_query = '''
                INSERT INTO medicines 
                (seller_id, name, batch_no, mfg_date, expiry_date, dosage, strength, category, stock_quantity, delivery_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            '''
            
            count = 0
            for medicine in sample_medicines:
                cursor.execute(insert_query, medicine)
                count += 1
            
            print(f"✓ Inserted {count} sample medicines")
        else:
            print("⚠ No approved seller found. Run CREATE_TEST_SELLER_PROFILE.sql first!")
        
        # Commit all changes
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
