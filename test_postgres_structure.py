#!/usr/bin/env python3
"""
Test PostgreSQL structure compatibility
"""

import psycopg2
import json

def test_structure():
    conn = psycopg2.connect(
        host="135.181.106.12",
        port=5432,
        database="morphik",
        user="morphik",
        password="morphik"
    )
    cur = conn.cursor()
    
    print("🔍 Checking PostgreSQL structure...")
    
    # Test INSERT with new structure
    test_data = {
        "document_id": "test_doc_001",
        "chunk_number": 0,
        "content": "data:image/png;base64,test",
        "chunk_metadata": json.dumps({
            "model": "colpali-v1.2",
            "shape": [1, 768],
            "is_image": True,
            "timestamp": "2025-09-11T10:00:00"
        }),
        "embeddings": json.dumps([[0.1, 0.2, 0.3]])
    }
    
    try:
        # Try to insert test data
        cur.execute("""
            INSERT INTO multi_vector_embeddings 
            (document_id, chunk_number, content, chunk_metadata, embeddings)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (document_id, chunk_number) 
            DO UPDATE SET 
                content = EXCLUDED.content,
                chunk_metadata = EXCLUDED.chunk_metadata,
                embeddings = EXCLUDED.embeddings
        """, (
            test_data["document_id"],
            test_data["chunk_number"],
            test_data["content"],
            test_data["chunk_metadata"],
            test_data["embeddings"]
        ))
        
        print("✅ INSERT test successful!")
        
        # Rollback test data
        conn.rollback()
        print("🔄 Test data rolled back")
        
    except Exception as e:
        print(f"❌ INSERT test failed: {e}")
        conn.rollback()
    
    cur.close()
    conn.close()
    print("\n✅ Structure test complete!")

if __name__ == "__main__":
    test_structure()