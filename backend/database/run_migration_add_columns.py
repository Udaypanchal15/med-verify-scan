#!/usr/bin/env python3
"""
Migration runner to add missing columns to sellers table
Run this script to fix the database schema
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from flask import Flask
from database import get_db, execute_query

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to add missing columns"""
    app = Flask(__name__)
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    try:
        with app.app_context():
            print("=" * 60)
            print("MIGRATION: Adding Missing Columns to Sellers Table")
            print("=" * 60)
            
            # Read migration SQL
            migration_file = Path(__file__).parent / 'MIGRATION_ADD_MISSING_COLUMNS.sql'
            if not migration_file.exists():
                print(f"Error: Migration file not found: {migration_file}")
                return False
            
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            print("\n📋 Running migration SQL...")
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
            
            for i, statement in enumerate(statements, 1):
                try:
                    # Skip comments and empty lines
                    if statement.startswith('--') or not statement:
                        continue
                    
                    print(f"\n  [{i}] Executing: {statement[:60]}...")
                    execute_query(statement)
                    
                except Exception as e:
                    # Some errors are expected (like IF NOT EXISTS)
                    if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                        print(f"      ℹ️  Column already exists (expected)")
                    else:
                        print(f"      ❌ Error: {str(e)[:100]}")
            
            print("\n✅ Migration completed successfully!")
            print("\n📊 Verifying columns in sellers table:")
            
            # Verify columns
            verify_query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'sellers'
            ORDER BY ordinal_position;
            """
            
            result = execute_query(verify_query, fetch_all=True)
            if result:
                for row in result:
                    print(f"   - {row[0]}: {row[1]}")
            
            print("\n✨ Database schema is now up to date!")
            return True
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
