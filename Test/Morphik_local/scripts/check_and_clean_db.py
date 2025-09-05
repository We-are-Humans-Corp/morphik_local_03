#!/usr/bin/env python3
"""
Check and optionally clean database
"""

import psycopg2
from datetime import datetime
import sys

# Connection parameters
conn_params = {
    'host': '135.181.106.12',
    'port': 5432,
    'database': 'morphik',
    'user': 'morphik',
    'password': 'morphik'
}

def check_database_status():
    """Check all relevant tables for data."""
    
    print("=" * 60)
    print("🔍 DATABASE STATUS CHECK")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True  # Important for avoiding transaction issues
    cur = conn.cursor()
    
    # Get actual column names for documents table
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'documents' 
        ORDER BY ordinal_position
        LIMIT 5
    """)
    doc_columns = [col[0] for col in cur.fetchall()]
    print(f"\nDocument table columns: {', '.join(doc_columns)}\n")
    
    # Tables to check
    tables_to_check = [
        'documents',
        'chunks', 
        'app_metadata',
        'chats',
        'chat_messages'
    ]
    
    print("📊 Table Status:\n")
    
    data_found = False
    for table_name in tables_to_check:
        try:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            exists = cur.fetchone()[0]
            
            if not exists:
                print(f"  ❌ {table_name:20} - Table does not exist")
                continue
            
            # Count records
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            
            if count > 0:
                data_found = True
                print(f"  ⚠️  {table_name:20} - {count} records")
                
                # Show sample for documents
                if table_name == 'documents' and doc_columns:
                    cols_to_select = doc_columns[:4]  # First 4 columns
                    cur.execute(f"SELECT {', '.join(cols_to_select)} FROM {table_name} LIMIT 2")
                    rows = cur.fetchall()
                    for row in rows:
                        preview = str(row)[:80] + "..." if len(str(row)) > 80 else str(row)
                        print(f"      → {preview}")
            else:
                print(f"  ✅ {table_name:20} - EMPTY")
                
        except Exception as e:
            print(f"  ❌ {table_name:20} - Error: {str(e)[:50]}")
    
    # Check vector tables
    print("\n🔍 Vector Store Status:\n")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name LIKE 'langchain_pg_%'
        ORDER BY table_name
    """)
    vector_tables = cur.fetchall()
    
    for (table_name,) in vector_tables:
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        if count > 0:
            data_found = True
            print(f"  ⚠️  {table_name:30} - {count} vectors")
        else:
            print(f"  ✅ {table_name:30} - EMPTY")
    
    cur.close()
    conn.close()
    
    return data_found

def clean_database():
    """Clean all data from database."""
    
    print("\n🧹 CLEANING DATABASE...\n")
    
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Tables to clean (in order to respect foreign keys)
    tables_to_clean = [
        'chat_messages',
        'chats',
        'chunks',
        'documents',
        # Keep app_metadata as it contains configuration
    ]
    
    for table_name in tables_to_clean:
        try:
            cur.execute(f"TRUNCATE TABLE {table_name} CASCADE")
            print(f"  ✅ Cleaned: {table_name}")
        except Exception as e:
            if "does not exist" not in str(e):
                print(f"  ⚠️  Could not clean {table_name}: {str(e)[:50]}")
    
    # Clean vector tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name LIKE 'langchain_pg_%'
    """)
    vector_tables = cur.fetchall()
    
    for (table_name,) in vector_tables:
        try:
            cur.execute(f"TRUNCATE TABLE {table_name} CASCADE")
            print(f"  ✅ Cleaned vector table: {table_name}")
        except Exception as e:
            print(f"  ⚠️  Could not clean {table_name}: {str(e)[:30]}")
    
    cur.close()
    conn.close()
    
    print("\n✅ Database cleaned!")

def main():
    data_found = check_database_status()
    
    if data_found:
        print("\n" + "=" * 60)
        print("⚠️  DATA FOUND IN DATABASE")
        print("=" * 60)
        
        response = input("\nDo you want to clean the database? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            clean_database()
            print("\n" + "=" * 60)
            print("✅ DATABASE IS NOW CLEAN - Ready for new test!")
            print("=" * 60)
        else:
            print("\n❌ Database not cleaned. Exiting...")
    else:
        print("\n" + "=" * 60)
        print("✅ DATABASE IS ALREADY CLEAN - Ready for new test!")
        print("=" * 60)

if __name__ == "__main__":
    main()