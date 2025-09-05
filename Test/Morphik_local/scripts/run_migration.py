#!/usr/bin/env python3
"""
Script to execute the app_metadata table migration.
Run this to create the table needed for multi-tenant support.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path to import from core
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from core.config import get_settings

async def run_migration():
    """Execute the migration SQL file to create app_metadata table."""
    
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.POSTGRES_URI,
        echo=True
    )
    
    # Read migration SQL
    migration_path = Path(__file__).parent.parent / "migrations" / "create_app_metadata_table.sql"
    with open(migration_path, "r") as f:
        migration_sql = f.read()
    
    # Execute migration
    async with engine.begin() as conn:
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        for statement in statements:
            if statement and not statement.startswith('--'):
                print(f"Executing: {statement[:50]}...")
                await conn.exec_driver_sql(statement + ';')
    
    await engine.dispose()
    print("\n✅ Migration completed successfully!")
    print("The app_metadata table has been created.")

if __name__ == "__main__":
    asyncio.run(run_migration())