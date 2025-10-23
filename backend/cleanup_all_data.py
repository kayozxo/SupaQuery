#!/usr/bin/env python3
"""
Complete data cleanup script
Removes all data from:
- PostgreSQL (documents, chunks, chat history)
- Memgraph (knowledge graph)
- FAISS (already cleaned but will verify)
- Physical files
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.database.postgres import db_service
from app.services.memgraph_service import get_memgraph_service
from app.services.graph_rag_v2 import GraphRAGService


async def cleanup_all_data():
    """Clean all data from all systems"""
    print("\n" + "="*60)
    print("🧹 COMPLETE DATA CLEANUP")
    print("="*60)
    print("\n⚠️  WARNING: This will delete ALL data from:")
    print("   - PostgreSQL (documents, chunks, chat sessions)")
    print("   - Memgraph (knowledge graph)")
    print("   - FAISS (semantic index)")
    print("   - Physical files in uploads/")
    print("\nThis action CANNOT be undone!")
    
    response = input("\nType 'DELETE ALL' to confirm: ")
    if response != "DELETE ALL":
        print("❌ Cleanup cancelled")
        return
    
    print("\n" + "="*60)
    print("Starting cleanup process...")
    print("="*60)
    
    # Initialize services
    print("\n1️⃣ Initializing services...")
    await db_service.init_db()
    memgraph = get_memgraph_service()
    graph_rag = GraphRAGService()
    print("   ✓ Services initialized")
    
    # Step 1: Clean PostgreSQL
    print("\n2️⃣ Cleaning PostgreSQL database...")
    try:
        from sqlalchemy import text
        async with db_service.SessionLocal() as session:
            # Delete in order to respect foreign key constraints
            await session.execute(text("DELETE FROM chat_messages"))
            await session.execute(text("DELETE FROM chat_sessions"))
            await session.execute(text("DELETE FROM document_chunks"))
            await session.execute(text("DELETE FROM document_shares"))
            await session.execute(text("DELETE FROM documents"))
            await session.commit()
        print("   ✓ Deleted all documents, chunks, and chat history from PostgreSQL")
    except Exception as e:
        print(f"   ⚠️  PostgreSQL cleanup warning: {e}")
    
    # Step 2: Clean Memgraph
    print("\n3️⃣ Cleaning Memgraph knowledge graph...")
    try:
        success = memgraph.clear_all()
        if success:
            print("   ✓ Deleted all nodes and relationships from Memgraph")
        else:
            print("   ⚠️  Memgraph cleanup had issues")
    except Exception as e:
        print(f"   ⚠️  Memgraph cleanup warning: {e}")
    
    # Step 3: Clean FAISS
    print("\n4️⃣ Cleaning FAISS semantic index...")
    try:
        graph_rag.hybrid_rag.faiss.clear_index()
        print("   ✓ Cleared FAISS index and saved")
    except Exception as e:
        print(f"   ⚠️  FAISS cleanup warning: {e}")
    
    # Step 4: Clean physical files
    print("\n5️⃣ Cleaning physical files...")
    upload_dir = Path("uploads")
    if upload_dir.exists():
        deleted_count = 0
        for file_path in upload_dir.glob("*"):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"   ⚠️  Could not delete {file_path.name}: {e}")
        print(f"   ✓ Deleted {deleted_count} physical files")
    else:
        print("   ⚠️  Upload directory does not exist")
    
    # Step 5: Verify cleanup
    print("\n6️⃣ Verifying cleanup...")
    try:
        # Check PostgreSQL
        docs = await db_service.list_documents(limit=1)
        pg_clean = len(docs) == 0
        
        # Check Memgraph
        mg_stats = memgraph.get_stats()
        mg_clean = mg_stats['documents'] == 0
        
        # Check FAISS
        faiss_count = len(graph_rag.hybrid_rag.faiss.chunk_metadata)
        faiss_clean = faiss_count == 0
        
        # Check files
        remaining_files = len(list(upload_dir.glob("*"))) if upload_dir.exists() else 0
        files_clean = remaining_files == 0
        
        print(f"   PostgreSQL: {'✓ Clean' if pg_clean else '✗ Has data'} ({len(docs)} docs)")
        print(f"   Memgraph: {'✓ Clean' if mg_clean else '✗ Has data'} ({mg_stats['documents']} docs)")
        print(f"   FAISS: {'✓ Clean' if faiss_clean else '✗ Has data'} ({faiss_count} chunks)")
        print(f"   Files: {'✓ Clean' if files_clean else '✗ Has files'} ({remaining_files} files)")
        
        if all([pg_clean, mg_clean, faiss_clean, files_clean]):
            print("\n✅ ALL SYSTEMS CLEANED SUCCESSFULLY!")
        else:
            print("\n⚠️  Some systems still have data. You may need to run this again.")
    
    except Exception as e:
        print(f"   ⚠️  Verification error: {e}")
    
    # Close connections
    await db_service.close()
    
    print("\n" + "="*60)
    print("Cleanup complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(cleanup_all_data())
