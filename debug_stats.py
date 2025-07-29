#!/usr/bin/env python3
"""
Debug script to test the stats functionality directly.
"""

import sys
from pathlib import Path

def test_rag_system_stats():
    """Test the RAG system stats directly."""
    print("🧪 Testing RAG System Stats...")
    
    try:
        # Import the RAG system
        from agents_rag_system import AgenticRAGSystem
        
        print("   ✅ Successfully imported AgenticRAGSystem")
        
        # Initialize the system
        print("   🚀 Initializing RAG system...")
        system = AgenticRAGSystem()
        
        if system.initialize(with_sample_data=True, num_sample_docs=3):
            print("   ✅ RAG system initialized successfully")
        else:
            print("   ⚠️  RAG system initialized with warnings")
        
        # Test get_system_stats method
        print("   📊 Testing get_system_stats()...")
        stats = system.get_system_stats()
        
        print(f"   📋 Raw stats result: {stats}")
        
        if stats:
            if stats.get("success"):
                print("   ✅ Stats retrieval successful")
                vector_stats = stats.get("stats", {}).get("vector_store_stats", {})
                print(f"   📈 Total chunks: {vector_stats.get('total_chunks', 0)}")
                print(f"   🏷️  Unique topics: {vector_stats.get('unique_topics', 0)}")
                print(f"   📄 Document types: {vector_stats.get('document_types', [])}")
            else:
                print("   ❌ Stats retrieval failed")
                print(f"   🔍 Error details: {stats}")
        else:
            print("   ❌ No stats returned")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing RAG system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_store_directly():
    """Test the vector store stats directly."""
    print("\n🧪 Testing Vector Store Stats Directly...")
    
    try:
        from vector_store import ChromaVectorStore
        
        print("   ✅ Successfully imported ChromaVectorStore")
        
        # Initialize vector store
        vs = ChromaVectorStore()
        print("   ✅ Vector store initialized")
        
        # Test get_collection_stats
        stats = vs.get_collection_stats()
        print(f"   📋 Collection stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing vector store: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastapi_stats_endpoint():
    """Test the FastAPI stats endpoint."""
    print("\n🧪 Testing FastAPI Stats Endpoint...")
    
    try:
        import requests
        
        # Test the endpoint
        print("   🌐 Making request to http://localhost:8000/api/stats...")
        response = requests.get("http://localhost:8000/api/stats", timeout=10)
        
        print(f"   📊 Response status: {response.status_code}")
        print(f"   📋 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response data: {data}")
            return True
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   📄 Response text: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection failed - is the FastAPI server running?")
        return False
    except Exception as e:
        print(f"   ❌ Error testing endpoint: {e}")
        return False

def run_diagnostic():
    """Run complete diagnostic."""
    print("🔍 Advanced RAG System - Stats Diagnostic")
    print("=" * 50)
    
    results = {}
    
    # Test 1: RAG System Stats
    results['rag_system'] = test_rag_system_stats()
    
    # Test 2: Vector Store Stats
    results['vector_store'] = test_vector_store_directly()
    
    # Test 3: FastAPI Endpoint
    results['fastapi_endpoint'] = test_fastapi_stats_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! The stats system should be working.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        
        print("\n💡 Troubleshooting tips:")
        if not results['rag_system']:
            print("   - Check if OPENAI_API_KEY is set in .env")
            print("   - Ensure all dependencies are installed")
        
        if not results['vector_store']:
            print("   - Check ChromaDB installation")
            print("   - Verify write permissions for chroma_db directory")
        
        if not results['fastapi_endpoint']:
            print("   - Make sure FastAPI server is running on port 8000")
            print("   - Check server logs for errors")
    
    return all_passed

if __name__ == "__main__":
    success = run_diagnostic()
    sys.exit(0 if success else 1)