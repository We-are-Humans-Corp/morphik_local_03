#!/usr/bin/env python3
"""
Check database status - verify if all tables are empty
"""

import psycopg2
from datetime import datetime

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
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # Tables to check
        tables_to_check = [
            ('documents', 'Document records'),
            ('chunks', 'Chunk records (text/images)'),
            ('app_metadata', 'Multi-tenant app configurations'),
            ('chats', 'Chat sessions'),
            ('chat_messages', 'Chat messages')
        ]
        
        print("\n📊 Table Status:\n")
        
        total_records = 0
        for table_name, description in tables_to_check:
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
                total_records += count
                
                status = "✅ EMPTY" if count == 0 else f"⚠️  {count} records"
                print(f"  {status:15} - {table_name:20} ({description})")
                
                # Show sample data if not empty
                if count > 0 and count <= 5:
                    if table_name == 'documents':
                        cur.execute(f"SELECT id, file_name, status, created_at FROM {table_name} LIMIT 3")
                        rows = cur.fetchall()
                        for row in rows:
                            print(f"      → ID: {row[0][:8]}... | {row[1]} | {row[2]} | {row[3]}")
                    elif table_name == 'chunks':
                        cur.execute(f"SELECT id, document_id, chunk_number FROM {table_name} LIMIT 3")
                        rows = cur.fetchall()
                        for row in rows:
                            print(f"      → Chunk: {row[0][:8]}... | Doc: {row[1][:8]}... | #: {row[2]}")
                            
            except Exception as e:
                print(f"  ❌ {table_name:20} - Error: {e}")
        
        # Check vector store (pgvector)
        print("\n🔍 Vector Store Status:\n")
        try:
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name LIKE 'langchain_pg_%'
            """)
            vector_tables = cur.fetchone()[0]
            print(f"  Vector tables found: {vector_tables}")
            
            # Check specific vector tables
            cur.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name LIKE 'langchain_pg_%'
            """)
            for (table_name,) in cur.fetchall():
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cur.fetchone()[0]
                status = "✅ EMPTY" if count == 0 else f"⚠️  {count} vectors"
                print(f"  {status:15} - {table_name}")
                
        except Exception as e:
            print(f"  Vector store check error: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        if total_records == 0:
            print("✅ DATABASE IS CLEAN - Ready for new test!")
        else:
            print(f"⚠️  DATABASE CONTAINS DATA - Total records: {total_records}")
        print("=" * 60)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    return total_records == 0

if __name__ == "__main__":
    check_database_status()