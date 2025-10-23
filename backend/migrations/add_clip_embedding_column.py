"""
Database Migration: Add CLIP Embedding Column
Add clip_embedding column to document_chunks table for storing visual embeddings
"""

import sys
import os
from pathlib import Path
import asyncio
from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
env_path = backend_dir / '.env'
load_dotenv(env_path)
print(f"📝 Loaded environment from: {env_path}")
print(f"📝 DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")

from sqlalchemy import text
from app.database.postgres import engine


async def upgrade():
    """Add clip_embedding column to document_chunks table"""
    async with engine.begin() as conn:
        # Add clip_embedding column (JSON type to store array of floats)
        await conn.execute(text("""
            ALTER TABLE document_chunks 
            ADD COLUMN IF NOT EXISTS clip_embedding JSON
        """))
        print("✅ Added clip_embedding column to document_chunks table")


async def downgrade():
    """Remove clip_embedding column from document_chunks table"""
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE document_chunks 
            DROP COLUMN IF EXISTS clip_embedding
        """))
        print("✅ Removed clip_embedding column from document_chunks table")


async def main():
    """Run the migration"""
    print("Running migration: Add CLIP embedding column...")
    await upgrade()
    print("Migration completed successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
