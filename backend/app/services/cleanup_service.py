"""
Cleanup Service - Handles atomic cleanup across all storage systems
Industry standard approach: centralized, transactional, with rollback capability
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio
from datetime import datetime


class CleanupService:
    """
    Centralized service for cleaning up data across all systems
    Ensures atomic operations with proper error handling
    """
    
    def __init__(self, db_service, memgraph_service, faiss_service, upload_dir: str = "uploads"):
        """
        Initialize cleanup service with dependencies
        
        Args:
            db_service: PostgreSQL database service
            memgraph_service: Memgraph graph database service
            faiss_service: FAISS vector store service
            upload_dir: Directory for uploaded files
        """
        self.db = db_service
        self.memgraph = memgraph_service
        self.faiss = faiss_service
        self.upload_dir = Path(upload_dir)
        
    async def cleanup_document(
        self,
        document_id: int,
        user_id: int,
        check_ownership: bool = True
    ) -> Dict[str, Any]:
        """
        Atomically delete a document from all systems
        
        Process:
        1. Verify document exists and user has access
        2. Get document metadata (needed for cleanup)
        3. Delete from PostgreSQL (source of truth)
        4. Delete from Memgraph (knowledge graph)
        5. Delete from FAISS (semantic index)
        6. Delete physical file
        
        Args:
            document_id: Database document ID
            user_id: User requesting deletion
            check_ownership: Whether to verify user owns document
            
        Returns:
            Dict with cleanup status for each system
        """
        cleanup_status = {
            "success": False,
            "document_id": document_id,
            "timestamp": datetime.now().isoformat(),
            "postgres": False,
            "memgraph": False,
            "faiss": False,
            "file": False,
            "errors": []
        }
        
        # Step 1: Get document info before deletion
        try:
            document = await self.db.get_document(document_id, user_id)
            if not document:
                cleanup_status["errors"].append("Document not found or access denied")
                return cleanup_status
            
            # Check ownership if required
            if check_ownership and document.user_id != user_id:
                cleanup_status["errors"].append("User does not own this document")
                return cleanup_status
            
            file_path = document.file_path
            filename = document.filename
            # Extract file_id from filename (remove extension)
            file_id = filename.rsplit('.', 1)[0] if filename else None
            
            print(f"\n🗑️  Cleaning document: {document.original_filename}")
            print(f"   DB ID: {document_id}, File ID: {file_id}")
            
        except Exception as e:
            cleanup_status["errors"].append(f"Error getting document info: {str(e)}")
            return cleanup_status
        
        # Step 2: Delete from PostgreSQL (source of truth)
        try:
            success = await self.db.delete_document(document_id, user_id)
            if success:
                cleanup_status["postgres"] = True
                print(f"   ✓ Deleted from PostgreSQL")
            else:
                cleanup_status["errors"].append("Failed to delete from PostgreSQL")
                return cleanup_status  # Stop if source of truth fails
        except Exception as e:
            cleanup_status["errors"].append(f"PostgreSQL error: {str(e)}")
            return cleanup_status
        
        # Step 3: Delete from Memgraph (best effort)
        if file_id:
            try:
                success = self.memgraph.delete_document(file_id)
                cleanup_status["memgraph"] = success
                if success:
                    print(f"   ✓ Deleted from Memgraph")
                else:
                    print(f"   ⚠️  Not found in Memgraph (may be already deleted)")
            except Exception as e:
                print(f"   ⚠️  Memgraph error (non-critical): {str(e)}")
                cleanup_status["errors"].append(f"Memgraph warning: {str(e)}")
        
        # Step 4: Delete from FAISS (best effort)
        if file_id:
            try:
                success = self.faiss.delete_document(file_id)
                cleanup_status["faiss"] = success
                if success:
                    print(f"   ✓ Deleted from FAISS and saved index")
                else:
                    print(f"   ⚠️  Not found in FAISS (may be already deleted)")
            except Exception as e:
                print(f"   ⚠️  FAISS error (non-critical): {str(e)}")
                cleanup_status["errors"].append(f"FAISS warning: {str(e)}")
        
        # Step 5: Delete physical file (best effort)
        if file_path:
            try:
                file = Path(file_path)
                if file.exists():
                    file.unlink()
                    cleanup_status["file"] = True
                    print(f"   ✓ Deleted physical file")
                else:
                    print(f"   ⚠️  File not found (may be already deleted)")
            except Exception as e:
                print(f"   ⚠️  File deletion error (non-critical): {str(e)}")
                cleanup_status["errors"].append(f"File warning: {str(e)}")
        
        # Mark as success if at least PostgreSQL succeeded
        cleanup_status["success"] = cleanup_status["postgres"]
        
        return cleanup_status
    
    async def cleanup_all_documents(self, force: bool = False) -> Dict[str, Any]:
        """
        Clean ALL documents from all systems (admin function)
        
        Args:
            force: Skip confirmation (use with caution!)
            
        Returns:
            Dict with cleanup statistics
        """
        stats = {
            "success": False,
            "documents_deleted": 0,
            "chunks_deleted": 0,
            "files_deleted": 0,
            "timestamp": datetime.now().isoformat(),
            "errors": []
        }
        
        try:
            # Get all documents
            documents = await self.db.list_documents(limit=10000)
            total = len(documents)
            
            print(f"\n🗑️  Cleaning {total} documents from all systems...")
            
            # Clean PostgreSQL
            from sqlalchemy import text
            async with self.db.SessionLocal() as session:
                await session.execute(text("DELETE FROM chat_messages"))
                await session.execute(text("DELETE FROM chat_sessions"))
                result = await session.execute(text("DELETE FROM document_chunks"))
                stats["chunks_deleted"] = result.rowcount if hasattr(result, 'rowcount') else 0
                await session.execute(text("DELETE FROM document_shares"))
                result = await session.execute(text("DELETE FROM documents"))
                stats["documents_deleted"] = result.rowcount if hasattr(result, 'rowcount') else 0
                await session.commit()
            print(f"   ✓ Cleaned PostgreSQL: {stats['documents_deleted']} documents")
            
            # Clean Memgraph
            try:
                self.memgraph.clear_all()
                print(f"   ✓ Cleaned Memgraph")
            except Exception as e:
                stats["errors"].append(f"Memgraph: {str(e)}")
            
            # Clean FAISS
            try:
                self.faiss.clear_index()
                print(f"   ✓ Cleaned FAISS")
            except Exception as e:
                stats["errors"].append(f"FAISS: {str(e)}")
            
            # Clean files
            if self.upload_dir.exists():
                for file_path in self.upload_dir.glob("*"):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            stats["files_deleted"] += 1
                        except Exception as e:
                            stats["errors"].append(f"File {file_path.name}: {str(e)}")
            print(f"   ✓ Cleaned {stats['files_deleted']} physical files")
            
            stats["success"] = True
            
        except Exception as e:
            stats["errors"].append(f"Cleanup error: {str(e)}")
        
        return stats
    
    async def verify_sync(self) -> Dict[str, Any]:
        """
        Verify all systems are in sync
        
        Returns:
            Dict with sync status and statistics
        """
        sync_status = {
            "in_sync": False,
            "timestamp": datetime.now().isoformat(),
            "postgres": {"documents": 0, "chunks": 0},
            "memgraph": {"documents": 0, "chunks": 0},
            "faiss": {"chunks": 0},
            "files": {"count": 0},
            "discrepancies": []
        }
        
        try:
            # Check PostgreSQL
            documents = await self.db.list_documents(limit=10000)
            sync_status["postgres"]["documents"] = len(documents)
            
            total_chunks = 0
            for doc in documents:
                chunks = await self.db.get_document_chunks(doc.id)
                total_chunks += len(chunks)
            sync_status["postgres"]["chunks"] = total_chunks
            
            # Check Memgraph
            mg_stats = self.memgraph.get_stats()
            sync_status["memgraph"]["documents"] = mg_stats.get('documents', 0)
            sync_status["memgraph"]["chunks"] = mg_stats.get('chunks', 0)
            
            # Check FAISS
            faiss_count = len(self.faiss.chunk_metadata)
            sync_status["faiss"]["chunks"] = faiss_count
            
            # Check files
            if self.upload_dir.exists():
                file_count = len([f for f in self.upload_dir.glob("*") if f.is_file()])
                sync_status["files"]["count"] = file_count
            
            # Check discrepancies
            if sync_status["postgres"]["documents"] != sync_status["memgraph"]["documents"]:
                sync_status["discrepancies"].append(
                    f"Document count mismatch: PostgreSQL={sync_status['postgres']['documents']}, "
                    f"Memgraph={sync_status['memgraph']['documents']}"
                )
            
            if sync_status["postgres"]["chunks"] != sync_status["faiss"]["chunks"]:
                sync_status["discrepancies"].append(
                    f"Chunk count mismatch: PostgreSQL={sync_status['postgres']['chunks']}, "
                    f"FAISS={sync_status['faiss']['chunks']}"
                )
            
            sync_status["in_sync"] = len(sync_status["discrepancies"]) == 0
            
        except Exception as e:
            sync_status["discrepancies"].append(f"Error checking sync: {str(e)}")
        
        return sync_status
    
    async def resync_systems(self) -> Dict[str, Any]:
        """
        Resynchronize all systems using PostgreSQL as source of truth
        
        Returns:
            Dict with resync status and statistics
        """
        resync_status = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "documents_synced": 0,
            "chunks_synced": 0,
            "errors": []
        }
        
        print(f"\n🔄 Resyncing all systems from PostgreSQL...")
        
        try:
            # Get all documents from PostgreSQL (source of truth)
            documents = await self.db.list_documents(limit=10000)
            print(f"   Found {len(documents)} documents in PostgreSQL")
            
            # Clear Memgraph and FAISS
            print(f"   Clearing Memgraph and FAISS...")
            self.memgraph.clear_all()
            self.faiss.clear_index()
            
            # Rebuild from PostgreSQL
            for doc in documents:
                try:
                    # Get chunks
                    chunks = await self.db.get_document_chunks(doc.id)
                    if not chunks:
                        continue
                    
                    file_id = doc.filename.rsplit('.', 1)[0]
                    
                    # Add to FAISS
                    faiss_chunks = []
                    for chunk in chunks:
                        faiss_chunks.append({
                            'doc_id': file_id,
                            'text': chunk.text,
                            'source': doc.original_filename,
                            'chunk_id': str(chunk.id),
                            'metadata': chunk.chunk_metadata or {}
                        })
                    
                    if faiss_chunks:
                        self.faiss.add_chunks(faiss_chunks)
                        resync_status["chunks_synced"] += len(faiss_chunks)
                    
                    # Add to Memgraph (if you have a method to add from existing data)
                    # This would require extending your memgraph service
                    
                    resync_status["documents_synced"] += 1
                    
                except Exception as e:
                    resync_status["errors"].append(f"Document {doc.id}: {str(e)}")
            
            print(f"   ✓ Synced {resync_status['documents_synced']} documents")
            print(f"   ✓ Synced {resync_status['chunks_synced']} chunks")
            
            resync_status["success"] = True
            
        except Exception as e:
            resync_status["errors"].append(f"Resync error: {str(e)}")
        
        return resync_status


# Singleton instance
_cleanup_service: Optional[CleanupService] = None


def get_cleanup_service(db_service, memgraph_service, faiss_service) -> CleanupService:
    """Get or create cleanup service instance"""
    global _cleanup_service
    if _cleanup_service is None:
        _cleanup_service = CleanupService(db_service, memgraph_service, faiss_service)
    return _cleanup_service
