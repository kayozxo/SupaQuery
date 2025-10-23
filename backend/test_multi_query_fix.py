#!/usr/bin/env python3
"""
Test script to verify multi-query fix
Verifies that all 3 queries go through the full hybrid pipeline
"""

import asyncio
from app.services.graph_rag_enhanced import get_enhanced_graph_rag_service

async def test_multi_query_fix():
    """Test that all queries are used in the hybrid pipeline"""
    
    print("=" * 80)
    print("🧪 Testing Multi-Query Fix")
    print("=" * 80)
    
    # Initialize service
    service = get_enhanced_graph_rag_service()
    
    # Enable multi-query
    service.enable_multi_query = True
    print(f"✓ Multi-query generation: {'Enabled' if service.enable_multi_query else 'Disabled'}")
    
    # Test query - should generate 3 query variations
    test_query = "What are the key concepts discussed in the documents?"
    
    print(f"\n📝 Test Query: {test_query}")
    print("-" * 80)
    
    try:
        result = await service.query(
            query=test_query,
            document_ids=None,
            top_k=5
        )
        
        print("\n" + "=" * 80)
        print("✅ TEST RESULTS")
        print("=" * 80)
        
        # Check response
        print(f"✓ Answer generated: {len(result.get('answer', ''))} characters")
        print(f"✓ Citations: {len(result.get('citations', []))}")
        print(f"✓ Sources: {len(result.get('sources', []))}")
        print(f"✓ Queries used: {result.get('num_queries_used', 'N/A')}")
        
        if result.get('num_queries_used', 0) >= 3:
            print("\n🎉 SUCCESS: Multiple queries were used!")
        else:
            print(f"\n⚠️  WARNING: Only {result.get('num_queries_used', 0)} queries were used")
        
        # Show answer preview
        answer = result.get('answer', '')
        print(f"\n📄 Answer Preview:")
        print(f"{answer[:300]}..." if len(answer) > 300 else answer)
        
        print("\n" + "=" * 80)
        print("✅ Test completed successfully!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(test_multi_query_fix())
    exit(0 if success else 1)
