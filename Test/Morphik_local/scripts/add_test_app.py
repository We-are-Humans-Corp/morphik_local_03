import psycopg2
import uuid

# Connection parameters
conn_params = {
    'host': '135.181.106.12',
    'port': 5432,
    'database': 'morphik',
    'user': 'morphik',
    'password': 'morphik'
}

try:
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    # Add test applications
    test_apps = [
        {
            'id': 'app-shared',
            'user_id': 'user-free',
            'app_name': 'Shared App (Free Tier)',
            'neon_project_id': 'neon-shared',
            'connection_uri': 'postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik',
            'extra': '{"tier": "free", "shared": true}'
        },
        {
            'id': 'app-premium-1',
            'user_id': 'user-premium',
            'app_name': 'Premium App 1',
            'neon_project_id': 'neon-premium-1',
            'connection_uri': 'postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik_app1',
            'extra': '{"tier": "premium", "dedicated": true}'
        },
        {
            'id': 'app-enterprise-1',
            'user_id': 'user-enterprise',
            'app_name': 'Enterprise App',
            'neon_project_id': 'neon-enterprise-1',
            'connection_uri': 'postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik_enterprise',
            'extra': '{"tier": "enterprise", "dedicated": true, "sla": "99.99"}'
        }
    ]
    
    for app in test_apps:
        cur.execute("""
            INSERT INTO app_metadata (id, user_id, app_name, neon_project_id, connection_uri, extra, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (id) DO UPDATE 
            SET user_id = EXCLUDED.user_id,
                app_name = EXCLUDED.app_name,
                connection_uri = EXCLUDED.connection_uri,
                extra = EXCLUDED.extra,
                updated_at = CURRENT_TIMESTAMP
        """, (app['id'], app['user_id'], app['app_name'], app['neon_project_id'], 
              app['connection_uri'], app['extra']))
    
    conn.commit()
    
    # Verify data
    cur.execute("SELECT id, app_name, connection_uri FROM app_metadata ORDER BY created_at")
    apps = cur.fetchall()
    
    print("✅ Test applications added successfully!\n")
    print("Current apps in database:")
    for app_id, app_name, conn_uri in apps:
        # Hide password in output
        if '@' in conn_uri:
            parts = conn_uri.split('@')
            safe_uri = parts[0].split('://')[0] + '://***:***@' + parts[1]
        else:
            safe_uri = conn_uri
        print(f"  - {app_id}: {app_name}")
        print(f"    URI: {safe_uri}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close()