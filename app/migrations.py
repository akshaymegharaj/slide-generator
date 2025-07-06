"""
Database migration script
"""
import asyncio
import os
from app.database import create_db_and_tables, engine
from app.models.database import SQLModel

async def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    
    # Create database tables
    await create_db_and_tables()
    
    print("Database migrations completed successfully!")

async def reset_database():
    """Reset database (drop all tables and recreate)"""
    print("Resetting database...")
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    # Recreate tables
    await create_db_and_tables()
    
    print("Database reset completed successfully!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        asyncio.run(reset_database())
    else:
        asyncio.run(run_migrations()) 