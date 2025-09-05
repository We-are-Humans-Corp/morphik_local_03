import psycopg2
from pathlib import Path

# Connection parameters
conn_params = {
    'host': '135.181.106.12',
    'port': 5432,
    'database': 'morphik',
    'user': 'morphik',
    'password': 'morphik'
}

try:
    # Connect to the database
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    # Read migration SQL
    migration_path = Path(__file__).parent.parent / "migrations" / "create_app_metadata_table.sql"
    with open(migration_path, "r") as f:
        migration_sql = f.read()
    
    # Execute migration
    cur.execute(migration_sql)
    conn.commit()
    
    # Check if table was created
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'app_metadata'")
    count = cur.fetchone()[0]
    
    if count > 0:
        print("✅ Table 'app_metadata' created successfully!")
        
        # Get column info
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'app_metadata'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        print("\nTable structure:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
    else:
        print("❌ Table creation may have failed")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close()