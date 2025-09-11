#!/usr/bin/env python3
"""
Check if ColPali embeddings were saved to PostgreSQL on Hetzner
"""

import psycopg2
import json
from datetime import datetime

# PostgreSQL connection settings from .env.production
POSTGRES_CONFIG = {
    "host": "135.181.106.12",
    "port": 5432,
    "database": "morphik",
    "user": "morphik",
    "password": "morphik"
}

def check_embeddings():
    """Check multi_vector_embeddings table for ColPali entries"""
    
    try:
        print("🔌 Connecting to PostgreSQL on Hetzner...")
        print(f"   Host: {POSTGRES_CONFIG['host']}")
        print(f"   Database: {POSTGRES_CONFIG['database']}")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cur = conn.cursor()
        
        print("\n✅ Connected successfully!")
        
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'multi_vector_embeddings'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("❌ Table 'multi_vector_embeddings' does not exist!")
            return
        
        print("✅ Table 'multi_vector_embeddings' exists")
        
        # First, check table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'multi_vector_embeddings'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        print("\n📋 Table structure:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        # Count total embeddings
        cur.execute("SELECT COUNT(*) FROM multi_vector_embeddings;")
        total_count = cur.fetchone()[0]
        print(f"\n📊 Total embeddings in database: {total_count}")
        
        # Skip model-based queries if column doesn't exist
        has_model_column = any(col[0] == 'model' for col in columns)
        
        if has_model_column:
            # Count ColPali embeddings
            cur.execute("""
                SELECT COUNT(*) FROM multi_vector_embeddings 
                WHERE model LIKE '%colpali%' OR model LIKE '%pali%';
            """)
        colpali_count = cur.fetchone()[0]
        print(f"🎯 ColPali embeddings: {colpali_count}")
        
        # Get latest entries
        print("\n📋 Latest 5 embeddings:")
        cur.execute("""
            SELECT 
                document_id,
                chunk_id,
                model,
                LENGTH(embedding) as embedding_size,
                created_at
            FROM multi_vector_embeddings 
            ORDER BY created_at DESC 
            LIMIT 5;
        """)
        
        results = cur.fetchall()
        if results:
            for row in results:
                doc_id, chunk_id, model, emb_size, created = row
                print(f"  - Doc: {doc_id[:20]}... | Chunk: {chunk_id[:20]}...")
                print(f"    Model: {model} | Size: {emb_size} bytes")
                print(f"    Created: {created}")
                print()
        else:
            print("  No embeddings found")
        
        # Check specifically for today's ColPali embeddings
        cur.execute("""
            SELECT 
                document_id,
                chunk_id,
                model,
                LENGTH(embedding) as embedding_size,
                created_at
            FROM multi_vector_embeddings 
            WHERE (model LIKE '%colpali%' OR model LIKE '%pali%')
                AND created_at >= CURRENT_DATE
            ORDER BY created_at DESC 
            LIMIT 5;
        """)
        
        today_results = cur.fetchall()
        if today_results:
            print(f"\n🆕 Today's ColPali embeddings ({len(today_results)} found):")
            for row in today_results:
                doc_id, chunk_id, model, emb_size, created = row
                print(f"  - Doc: {doc_id[:30]}...")
                print(f"    Model: {model} | Size: {emb_size} bytes")
                print(f"    Created: {created}")
        else:
            print("\n⚠️ No ColPali embeddings found from today")
        
        # Get unique models used
        cur.execute("SELECT DISTINCT model FROM multi_vector_embeddings;")
        models = cur.fetchall()
        print(f"\n🤖 Models in use:")
        for model in models:
            print(f"  - {model[0]}")
        
        cur.close()
        conn.close()
        
        print("\n✅ Check complete!")
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Could not connect to PostgreSQL: {e}")
        print("Make sure the Hetzner server is accessible and PostgreSQL is running")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL ColPali Embeddings Check")
    print("=" * 60)
    check_embeddings()