#!/bin/bash

# Setup script for Hybrid Image Processing (Tesseract + CLIP)

echo "🚀 Setting up Hybrid Image Processing..."
echo ""

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Must be run from the backend directory"
    echo "Usage: cd backend && bash setup_hybrid_processing.sh"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "Consider running: source venv/bin/activate"
    echo ""
fi

# Install new dependencies
echo "📦 Installing CLIP dependencies..."
pip install open-clip-torch ftfy regex --quiet
echo "   ✅ open-clip-torch installed"
echo "   ✅ ftfy installed"
echo "   ✅ regex installed"
echo ""

# Download CLIP model
echo "📥 Downloading CLIP model (ViT-B-32)..."
python3 << EOF
import open_clip
try:
    model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
    print("   ✅ CLIP model downloaded successfully")
except Exception as e:
    print(f"   ❌ Error downloading CLIP model: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "❌ Failed to download CLIP model"
    exit 1
fi

echo ""

# Run database migration
echo "🗄️  Running database migration..."
if [ -f "migrations/add_clip_embedding_column.py" ]; then
    python migrations/add_clip_embedding_column.py
    if [ $? -eq 0 ]; then
        echo "   ✅ Database migration completed"
    else
        echo "   ⚠️  Migration failed or already applied"
    fi
else
    echo "   ⚠️  Migration file not found (may already be applied)"
fi

echo ""

# Test CLIP service
echo "🧪 Testing CLIP service..."
python3 << EOF
from app.services.clip_service import get_clip_service
from PIL import Image
import numpy as np

try:
    clip = get_clip_service()
    
    # Test text encoding
    text_emb = clip.encode_text("test query")
    assert text_emb is not None and text_emb.shape == (512,), "Text embedding failed"
    print("   ✅ CLIP text encoding works")
    
    # Test embedding dimension
    dim = clip.get_embedding_dimension()
    assert dim == 512, f"Wrong dimension: {dim}"
    print("   ✅ CLIP embedding dimension correct (512)")
    
    print("   ✅ All tests passed!")
except Exception as e:
    print(f"   ❌ Test failed: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "❌ CLIP service test failed"
    exit 1
fi

echo ""
echo "✅ Hybrid Image Processing setup complete!"
echo ""
echo "📚 Documentation: See HYBRID_IMAGE_PROCESSING.md for details"
echo ""
echo "Next steps:"
echo "  1. Start the backend: python main.py"
echo "  2. Upload an image to test the hybrid approach"
echo "  3. Check logs for: ✅ Generated CLIP embedding"
echo ""
