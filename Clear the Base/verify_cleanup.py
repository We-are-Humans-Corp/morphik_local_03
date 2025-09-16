#!/usr/bin/env python3
"""
Verify that database is clean
"""

import psycopg2

def verify_cleanup():
    """Check if database is clean"""
    
    print("🔍 Verifying database cleanup...")
    print("=" * 60)
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host='135.181.106.12',
            port=5432,
            database='morphik',
            user='morphik',
            password='morphik'
        )
        cur = conn.cursor()
        
        # Check multi_vector_embeddings
        cur.execute("SELECT COUNT(*) FROM multi_vector_embeddings")
        embeddings_count = cur.fetchone()[0]
        
        # Check documents
        cur.execute("SELECT COUNT(*) FROM documents")
        docs_count = cur.fetchone()[0]
        
        print("📊 Database status:")
        print(f"   - multi_vector_embeddings: {embeddings_count} records")
        print(f"   - documents: {docs_count} records")
        
        if embeddings_count == 0 and docs_count == 0:
            print("\n✅ Database is CLEAN! All documents and embeddings removed.")
        else:
            print(f"\n⚠️  Database still contains data!")
            
            if embeddings_count > 0:
                # Show sample embeddings
                cur.execute("""
                    SELECT document_id, chunk_number 
                    FROM multi_vector_embeddings 
                    LIMIT 5
                """)
                samples = cur.fetchall()
                print(f"\n   Sample embeddings:")
                for doc_id, chunk_num in samples:
                    print(f"     - {doc_id}, chunk {chunk_num}")
            
            if docs_count > 0:
                # Show sample documents
                cur.execute("""
                    SELECT external_id, title 
                    FROM documents 
                    LIMIT 5
                """)
                samples = cur.fetchall()
                print(f"\n   Sample documents:")
                for ext_id, title in samples:
                    print(f"     - {ext_id}: {title}")
        
        # Close connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_cleanup()