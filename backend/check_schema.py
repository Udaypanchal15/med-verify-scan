import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
db_url = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Check medicines by category
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM medicines
        GROUP BY category
        ORDER BY category;
    ''')
    
    print('=== Medicines by Category ===')
    for category, count in cursor.fetchall():
        print(f'  {category}: {count}')
    
    # Check sample medicines
    cursor.execute('''
        SELECT name, batch_no, category, stock_quantity, delivery_status
        FROM medicines
        WHERE category IN ('Fever', 'Diabetes', 'Heart Disease', 'High Blood Pressure', 'Cough & Cold')
        ORDER BY category, name;
    ''')
    
    print('\n=== Sample Medicines ===')
    medicines = cursor.fetchall()
    for name, batch, cat, stock, status in medicines:
        print(f'  {name:20} | {batch:8} | {cat:20} | Stock: {stock:3} | {status}')
    
    print(f'\nTotal sample medicines: {len(medicines)}')
    
    # Check email column in sellers
    cursor.execute('''
        SELECT column_name
        FROM information_schema.columns 
        WHERE table_name = 'sellers'
        AND column_name = 'email';
    ''')
    
    print('\n=== Sellers email column ===')
    if cursor.fetchone():
        print('  ✓ Email column EXISTS')
    else:
        print('  ✗ Email column MISSING!')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
