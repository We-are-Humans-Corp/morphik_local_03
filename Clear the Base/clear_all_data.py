#!/usr/bin/env python3
"""
Clear all documents and embeddings from PostgreSQL
"""

import psycopg2
from psycopg2 import sql

def clear_all_data():
    """Clear all document-related data from PostgreSQL"""
    
    print("🗑️  Starting database cleanup...")
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
        
        # Count records before deletion
        tables_to_clear = [
            'multi_vector_embeddings',
            'documents',
            'document_chunks',
            'graph_data',
            'chats',
            'chat_messages'
        ]
        
        print("📊 Current data in tables:")
        for table in tables_to_clear:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                if count > 0:
                    print(f"   - {table}: {count} records")
            except psycopg2.errors.UndefinedTable:
                print(f"   - {table}: table doesn't exist")
                conn.rollback()
            except Exception as e:
                print(f"   - {table}: error checking ({e})")
                conn.rollback()
        
        print("\n🧹 Clearing tables...")
        
        # Clear multi_vector_embeddings
        try:
            cur.execute("DELETE FROM multi_vector_embeddings")
            deleted = cur.rowcount
            conn.commit()
            print(f"   ✅ Deleted {deleted} records from multi_vector_embeddings")
        except Exception as e:
            print(f"   ❌ Error clearing multi_vector_embeddings: {e}")
            conn.rollback()
        
        # Clear documents
        try:
            cur.execute("DELETE FROM documents")
            deleted = cur.rowcount
            conn.commit()
            print(f"   ✅ Deleted {deleted} records from documents")
        except Exception as e:
            print(f"   ❌ Error clearing documents: {e}")
            conn.rollback()
        
        # Clear document_chunks
        try:
            cur.execute("DELETE FROM document_chunks")
            deleted = cur.rowcount
            conn.commit()
            print(f"   ✅ Deleted {deleted} records from document_chunks")
        except Exception as e:
            print(f"   ⚠️  Table document_chunks might not exist or is empty")
            conn.rollback()
        
        # Clear graph_data
        try:
            cur.execute("DELETE FROM graph_data")
            deleted = cur.rowcount
            conn.commit()
            print(f"   ✅ Deleted {deleted} records from graph_data")
        except Exception as e:
            print(f"   ⚠️  Table graph_data might not exist or is empty")
            conn.rollback()
        
        # Clear chats (optional)
        print("\n💬 Chat data (keeping for history):")
        try:
            cur.execute("SELECT COUNT(*) FROM chats")
            chat_count = cur.fetchone()[0]
            print(f"   - chats: {chat_count} records (not deleted)")
            
            cur.execute("SELECT COUNT(*) FROM chat_messages")
            msg_count = cur.fetchone()[0]
            print(f"   - chat_messages: {msg_count} records (not deleted)")
        except:
            pass
        
        print("\n✅ Cleanup complete!")
        print("=" * 60)
        
        # Verify cleanup
        print("\n📋 Final verification:")
        cur.execute("SELECT COUNT(*) FROM multi_vector_embeddings")
        count = cur.fetchone()[0]
        print(f"   - multi_vector_embeddings: {count} records")
        
        cur.execute("SELECT COUNT(*) FROM documents")
        count = cur.fetchone()[0]
        print(f"   - documents: {count} records")
        
        # Close connection
        cur.close()
        conn.close()
        
        print("\n✅ Database is clean and ready for new documents!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Confirmation prompt
    print("⚠️  WARNING: This will delete ALL documents and embeddings!")
    print("   (Chat history will be preserved)")
    response = input("\n   Continue? (yes/no): ")
    
    if response.lower() == 'yes':
        clear_all_data()
    else:
        print("❌ Cancelled. No data was deleted.")