#!/usr/bin/env python3
"""
Check ColPali processing results
"""

import psycopg2
import json
from datetime import datetime

# Connection parameters
conn_params = {
    'host': '135.181.106.12',
    'port': 5432,
    'database': 'morphik',
    'user': 'morphik',
    'password': 'morphik'
}

def check_colpali_results():
    """Check ColPali processing results."""
    
    print("=" * 60)
    print("🔍 COLPALI PROCESSING CHECK")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Check documents
    print("\n📄 Documents:")
    cur.execute("""
        SELECT external_id, filename, content_type, 
               doc_metadata->'using_colpali' as using_colpali,
               doc_metadata->'chunk_count' as chunk_count
        FROM documents 
        ORDER BY external_id DESC
        LIMIT 5
    """)
    
    docs = cur.fetchall()
    for doc in docs:
        doc_id, filename, content_type, using_colpali, chunk_count = doc
        print(f"\n  Document: {filename}")
        print(f"    ID: {doc_id[:8]}...")
        print(f"    Type: {content_type}")
        print(f"    Using ColPali: {using_colpali}")
        print(f"    Chunks: {chunk_count}")
    
    # Check if chunks table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'chunks'
        )
    """)
    
    if not cur.fetchone()[0]:
        # Try langchain tables
        print("\n🔍 Checking vector store tables...")
        
        cur.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_name LIKE 'langchain_pg_%'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        for table_name, col_count in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"  {table_name}: {count} records ({col_count} columns)")
            
            # Check for embeddings in langchain_pg_embedding
            if 'embedding' in table_name and count > 0:
                cur.execute(f"""
                    SELECT 
                        id,
                        collection_id,
                        custom_id,
                        LEFT(document::text, 100) as doc_preview,
                        cmetadata::text as metadata
                    FROM {table_name}
                    LIMIT 3
                """)
                
                print(f"\n  Sample embeddings from {table_name}:")
                for row in cur.fetchall():
                    id_val, coll_id, custom_id, doc_preview, metadata = row
                    print(f"    → ID: {id_val[:8] if id_val else 'N/A'}...")
                    if metadata:
                        try:
                            meta = json.loads(metadata) if isinstance(metadata, str) else metadata
                            if isinstance(meta, dict):
                                print(f"      Metadata: is_image={meta.get('is_image', False)}, "
                                      f"page={meta.get('page_number', 'N/A')}")
                        except:
                            print(f"      Metadata: {metadata[:50]}...")
                    print(f"      Document: {doc_preview}...")
    
    # Check for ColPali specific settings
    print("\n⚙️  ColPali Configuration:")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'documents' 
        AND column_name LIKE '%colpali%'
        OR column_name LIKE '%metadata%'
        LIMIT 5
    """)
    
    cols = cur.fetchall()
    if cols:
        for col_name, col_type in cols:
            print(f"  {col_name}: {col_type}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    check_colpali_results()