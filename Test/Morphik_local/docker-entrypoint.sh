#!/bin/bash
set -e

# Copy default config if none exists
if [ ! -f /app/morphik.toml ]; then
    cp /app/morphik.toml.default /app/morphik.toml
fi

# Function to check PostgreSQL
check_postgres() {
    if [ -n "$POSTGRES_URI" ]; then
        echo "PostgreSQL URI found, checking connection..."
        
        # Simply use Python to check connection since it's more reliable
        python -c "
import asyncio
import asyncpg
import os
import sys
import time

async def check_connection():
    uri = os.environ.get('POSTGRES_URI', '')
    if not uri:
        print('No POSTGRES_URI found')
        return False
    
    # Convert SQLAlchemy URI to asyncpg format
    # postgresql+asyncpg://user:pass@host:port/db -> postgresql://user:pass@host:port/db
    asyncpg_uri = uri.replace('postgresql+asyncpg://', 'postgresql://')
    
    max_retries = 30
    for i in range(max_retries):
        try:
            print(f'Attempting to connect to PostgreSQL... (Attempt {i+1}/{max_retries})')
            conn = await asyncpg.connect(asyncpg_uri, timeout=5)
            await conn.fetchval('SELECT 1')
            await conn.close()
            print('PostgreSQL connection verified!')
            return True
        except Exception as e:
            if i == max_retries - 1:
                print(f'Could not connect to PostgreSQL after {max_retries} attempts: {e}')
                return False
            print(f'Connection failed: {e}')
            time.sleep(2)
    
    return False

if not asyncio.run(check_connection()):
    print('Error: Could not establish PostgreSQL connection')
    sys.exit(1)
"
        
        if [ $? -ne 0 ]; then
            echo "Error: PostgreSQL connection check failed"
            exit 1
        fi
    else
        echo "No POSTGRES_URI configured, skipping PostgreSQL check"
    fi
}

# Check PostgreSQL
check_postgres

# Check if command arguments were passed ($# is the number of arguments)
if [ $# -gt 0 ]; then
    # If arguments exist, execute them (e.g., execute "arq core.workers...")
    exec "$@"
else
    # Otherwise, execute the default command (uv run uvicorn core.api:app)
    exec uv run uvicorn core.api:app --host $HOST --port $PORT --loop asyncio --http auto --ws auto --lifespan auto
fi