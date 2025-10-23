"""
CLIP Image Embedding Service
Handles visual embeddings for images using OpenCLIP
"""

import torch
import open_clip
from PIL import Image
import numpy as np
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class CLIPService:
    """Service for generating visual embeddings using CLIP"""
    
    def __init__(self, model_name: str = "ViT-B-32", pretrained: str = "laion2b_s34b_b79k"):
        """
        Initialize CLIP model
        
        Args:
            model_name: CLIP model architecture (default: ViT-B-32)
            pretrained: Pretrained weights source (default: laion2b_s34b_b79k - publicly available, no auth required)
        """
        self.model = None
        self.preprocess = None
        self.tokenizer = None
        self.model_name = model_name
        self.pretrained = pretrained
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"CLIP Service initialized (device: {self.device})")
    
    def _load_model(self):
        """Lazy load CLIP model"""
        if self.model is None:
            try:
                logger.info(f"Loading CLIP model: {self.model_name} ({self.pretrained})")
                self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                    self.model_name, 
                    pretrained=self.pretrained,
                    device=self.device
                )
                self.tokenizer = open_clip.get_tokenizer(self.model_name)
                self.model.eval()  # Set to evaluation mode
                logger.info("✅ CLIP model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load CLIP model: {e}")
                raise
        
        return self.model
    
    def encode_image(self, image: Image.Image) -> Optional[np.ndarray]:
        """
        Generate CLIP embedding for an image
        
        Args:
            image: PIL Image object
            
        Returns:
            numpy array of shape (512,) containing the image embedding
        """
        try:
            self._load_model()
            
            # Preprocess image
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Generate embedding
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)  # Normalize
            
            # Convert to numpy
            embedding = image_features.cpu().numpy().flatten()
            
            logger.debug(f"Generated CLIP embedding with shape: {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error encoding image with CLIP: {e}")
            return None
    
    def encode_text(self, text: str) -> Optional[np.ndarray]:
        """
        Generate CLIP text embedding (useful for cross-modal search)
        
        Args:
            text: Text to encode
            
        Returns:
            numpy array of shape (512,) containing the text embedding
        """
        try:
            self._load_model()
            
            # Tokenize text
            text_tokens = self.tokenizer([text]).to(self.device)
            
            # Generate embedding
            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)  # Normalize
            
            # Convert to numpy
            embedding = text_features.cpu().numpy().flatten()
            
            logger.debug(f"Generated CLIP text embedding with shape: {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error encoding text with CLIP: {e}")
            return None
    
    def encode_images_batch(self, images: List[Image.Image]) -> Optional[np.ndarray]:
        """
        Generate CLIP embeddings for multiple images in batch
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            numpy array of shape (N, 512) containing embeddings
        """
        try:
            self._load_model()
            
            # Preprocess images
            image_tensors = torch.stack([
                self.preprocess(img) for img in images
            ]).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensors)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy
            embeddings = image_features.cpu().numpy()
            
            logger.debug(f"Generated {len(embeddings)} CLIP embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error encoding images batch with CLIP: {e}")
            return None
    
    def compute_similarity(self, image: Image.Image, text: str) -> Optional[float]:
        """
        Compute similarity between an image and text (cross-modal)
        
        Args:
            image: PIL Image object
            text: Text query
            
        Returns:
            Similarity score (0-1)
        """
        try:
            image_emb = self.encode_image(image)
            text_emb = self.encode_text(text)
            
            if image_emb is None or text_emb is None:
                return None
            
            # Compute cosine similarity
            similarity = np.dot(image_emb, text_emb)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return None
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of CLIP embeddings"""
        return 512  # ViT-B-32 produces 512-dimensional embeddings


# Singleton instance
_clip_service: Optional[CLIPService] = None


def get_clip_service() -> CLIPService:
    """Get or create singleton CLIP service instance"""
    global _clip_service
    if _clip_service is None:
        _clip_service = CLIPService()
    return _clip_service
