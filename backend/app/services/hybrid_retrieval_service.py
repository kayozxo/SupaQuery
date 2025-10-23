"""
Hybrid Image-Text Retrieval Service
Combines FAISS text embeddings with CLIP visual embeddings
"""

import numpy as np
from typing import List, Dict, Any, Optional
import faiss


class HybridRetrievalService:
    """
    Service for hybrid retrieval combining:
    1. Text embeddings (from all-MiniLM-L6-v2) for text-based search
    2. CLIP embeddings for visual search
    3. Score fusion for combined ranking
    """
    
    def __init__(self):
        """Initialize hybrid retrieval indices"""
        # Separate FAISS indices for text and images
        self.text_index = None  # 384-dim (all-MiniLM-L6-v2)
        self.image_index = None  # 512-dim (CLIP ViT-B-32)
        
        # Metadata storage
        self.text_metadata = []
        self.image_metadata = []
        
        print("✅ Hybrid Retrieval Service initialized")
    
    def add_image_embeddings(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Add CLIP image embeddings to the image index
        
        Args:
            embeddings: numpy array of shape (N, 512)
            metadata: list of metadata dicts for each embedding
        """
        if embeddings is None or len(embeddings) == 0:
            return
        
        # Initialize image index if needed
        if self.image_index is None:
            self.image_index = faiss.IndexFlatL2(512)  # CLIP dimension
            print("Created CLIP image index (512-dim)")
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.image_index.add(embeddings.astype('float32'))
        self.image_metadata.extend(metadata)
        
        print(f"Added {len(embeddings)} CLIP embeddings to image index")
    
    def search_images(
        self, 
        query_embedding: np.ndarray, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar images using CLIP embeddings
        
        Args:
            query_embedding: CLIP text embedding (512-dim)
            top_k: number of results to return
            
        Returns:
            List of matching results with scores
        """
        if self.image_index is None or self.image_index.ntotal == 0:
            return []
        
        # Normalize query
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.image_index.search(query_embedding, min(top_k, self.image_index.ntotal))
        
        # Format results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0:  # Valid index
                result = self.image_metadata[idx].copy()
                result['score'] = float(1 / (1 + dist))  # Convert distance to similarity score
                result['search_type'] = 'visual'
                results.append(result)
        
        return results
    
    def hybrid_search(
        self,
        text_query: str,
        text_results: List[Dict[str, Any]],
        visual_query_embedding: Optional[np.ndarray] = None,
        top_k: int = 10,
        text_weight: float = 0.6,
        visual_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining text and visual results
        
        Args:
            text_query: Text query string
            text_results: Results from text-based search
            visual_query_embedding: CLIP text embedding for cross-modal search
            top_k: number of final results
            text_weight: weight for text scores (0-1)
            visual_weight: weight for visual scores (0-1)
            
        Returns:
            Fused and reranked results
        """
        # If no visual search requested, return text results
        if visual_query_embedding is None:
            return text_results[:top_k]
        
        # Get visual results
        visual_results = self.search_images(visual_query_embedding, top_k=top_k * 2)
        
        if not visual_results:
            return text_results[:top_k]
        
        # Normalize weights
        total_weight = text_weight + visual_weight
        text_weight = text_weight / total_weight
        visual_weight = visual_weight / total_weight
        
        # Create score maps
        text_score_map = {
            self._get_result_key(r): r.get('score', 0.5) * text_weight 
            for r in text_results
        }
        visual_score_map = {
            self._get_result_key(r): r.get('score', 0.5) * visual_weight 
            for r in visual_results
        }
        
        # Combine all unique results
        all_keys = set(text_score_map.keys()) | set(visual_score_map.keys())
        
        combined_results = []
        result_map = {self._get_result_key(r): r for r in text_results + visual_results}
        
        for key in all_keys:
            if key in result_map:
                result = result_map[key].copy()
                
                # Fusion score
                text_score = text_score_map.get(key, 0)
                visual_score = visual_score_map.get(key, 0)
                result['fused_score'] = text_score + visual_score
                result['text_score'] = text_score / text_weight if text_weight > 0 else 0
                result['visual_score'] = visual_score / visual_weight if visual_weight > 0 else 0
                
                combined_results.append(result)
        
        # Sort by fused score
        combined_results.sort(key=lambda x: x['fused_score'], reverse=True)
        
        return combined_results[:top_k]
    
    def _get_result_key(self, result: Dict[str, Any]) -> str:
        """Generate unique key for a result"""
        doc_id = result.get('doc_id', result.get('document_id', ''))
        chunk_id = result.get('chunk_id', result.get('id', ''))
        return f"{doc_id}_{chunk_id}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the indices"""
        return {
            "image_embeddings": self.image_index.ntotal if self.image_index else 0,
            "text_embeddings": 0,  # Handled by existing FAISS service
            "total_documents": len(set(
                m.get('doc_id', '') for m in self.image_metadata
            ))
        }


# Singleton instance
_hybrid_service: Optional[HybridRetrievalService] = None


def get_hybrid_retrieval_service() -> HybridRetrievalService:
    """Get or create singleton hybrid retrieval service"""
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridRetrievalService()
    return _hybrid_service
