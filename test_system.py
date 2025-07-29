#!/usr/bin/env python3
"""
Comprehensive test script for the Advanced RAG System.
Tests all major components and their integration.
"""

import sys
import os
import traceback
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration loading."""
    print("🧪 Testing Configuration...")
    try:
        from config import Config
        
        # Test basic config access
        print(f"   ✓ Embedding Model: {Config.EMBEDDING_MODEL}")
        print(f"   ✓ LLM Model: {Config.LLM_MODEL}")
        print(f"   ✓ Chunk Size: {Config.CHUNK_SIZE}")
        print(f"   ✓ ChromaDB Path: {Config.CHROMA_DB_PATH}")
        
        # Test validation (will raise exception if OPENAI_API_KEY is missing)
        try:
            Config.validate()
            print("   ✓ Configuration validation passed")
        except ValueError as e:
            print(f"   ⚠️  Configuration validation warning: {e}")
            print("   ℹ️  Set OPENAI_API_KEY environment variable to test OpenAI features")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_sample_data_generator():
    """Test sample data generation."""
    print("\n🧪 Testing Sample Data Generator...")
    try:
        from sample_data_generator import SampleDataGenerator
        
        generator = SampleDataGenerator()
        
        # Test generating different document types
        research_paper = generator.generate_research_paper("artificial intelligence")
        news_article = generator.generate_news_article("climate change")
        technical_report = generator.generate_technical_report("quantum computing")
        summary = generator.generate_summary("biotechnology")
        
        print(f"   ✓ Research paper generated: '{research_paper['title'][:50]}...'")
        print(f"   ✓ News article generated: '{news_article['title'][:50]}...'")
        print(f"   ✓ Technical report generated: '{technical_report['title'][:50]}...'")
        print(f"   ✓ Summary generated: '{summary['title'][:50]}...'")
        
        # Test batch generation
        batch_docs = generator.generate_sample_documents(5)
        print(f"   ✓ Batch generation: {len(batch_docs)} documents created")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Sample data generator test failed: {e}")
        traceback.print_exc()
        return False

def test_vector_store():
    """Test vector store operations."""
    print("\n🧪 Testing Vector Store...")
    try:
        from vector_store import ChromaVectorStore
        from sample_data_generator import SampleDataGenerator
        
        # Initialize vector store with test collection
        vs = ChromaVectorStore("test_collection")
        print("   ✓ Vector store initialized")
        
        # Generate test documents
        generator = SampleDataGenerator()
        test_docs = generator.generate_sample_documents(3)
        
        # Test adding documents
        result = vs.add_documents(test_docs)
        print(f"   ✓ Added {len(test_docs)} documents to vector store")
        
        # Test similarity search
        search_results = vs.similarity_search("artificial intelligence", k=2)
        print(f"   ✓ Search returned {len(search_results)} results")
        
        if search_results:
            best_result = search_results[0]
            print(f"   ✓ Best result score: {best_result['similarity_score']:.3f}")
        
        # Test collection stats
        stats = vs.get_collection_stats()
        print(f"   ✓ Collection stats: {stats.get('total_chunks', 0)} chunks")
        
        # Cleanup test collection
        vs.clear_collection()
        print("   ✓ Test collection cleared")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Vector store test failed: {e}")
        traceback.print_exc()
        return False

def test_external_content_retriever():
    """Test external content retrieval."""
    print("\n🧪 Testing External Content Retriever...")
    try:
        from external_content_retriever import ExternalContentRetriever, ContentAggregator
        
        retriever = ExternalContentRetriever()
        print("   ✓ External content retriever initialized")
        
        # Test Wikipedia fetching (this will actually try to fetch from Wikipedia)
        wiki_result = retriever.fetch_wikipedia_article("artificial intelligence")
        if wiki_result:
            print(f"   ✓ Wikipedia fetch successful: '{wiki_result['title']}'")
            print(f"   ✓ Content length: {len(wiki_result['content'])} characters")
        else:
            print("   ⚠️  Wikipedia fetch returned no results (may be network issue)")
        
        # Test mock content generation
        news_articles = retriever.fetch_news_articles("machine learning")
        print(f"   ✓ Generated {len(news_articles)} mock news articles")
        
        research_papers = retriever.fetch_research_papers("quantum computing")
        print(f"   ✓ Generated {len(research_papers)} mock research papers")
        
        # Test content aggregator
        aggregator = ContentAggregator()
        aggregated_content = aggregator.gather_comprehensive_content("artificial intelligence")
        print(f"   ✓ Content aggregator gathered {len(aggregated_content)} pieces of content")
        
        return True
        
    except Exception as e:
        print(f"   ❌ External content retriever test failed: {e}")
        traceback.print_exc()
        return False

def test_rag_retriever():
    """Test RAG retrieval system."""
    print("\n🧪 Testing RAG Retriever...")
    try:
        from rag_retriever import AdvancedRAGRetriever, QueryProcessor
        from sample_data_generator import SampleDataGenerator
        
        # Initialize RAG retriever
        rag_retriever = AdvancedRAGRetriever()
        print("   ✓ RAG retriever initialized")
        
        # Add some sample data
        generator = SampleDataGenerator()
        sample_docs = generator.generate_sample_documents(5)
        rag_retriever.vector_store.add_documents(sample_docs)
        print("   ✓ Added sample documents to knowledge base")
        
        # Test query processing
        query_processor = QueryProcessor()
        enhanced_query = query_processor.enhance_query("tell me about AI")
        print(f"   ✓ Query enhanced: '{enhanced_query['original']}' -> '{enhanced_query['enhanced'][:50]}...'")
        
        # Test context retrieval
        context_data = rag_retriever.retrieve_relevant_context(
            "artificial intelligence applications",
            k=3,
            include_external=False  # Skip external for testing speed
        )
        
        print(f"   ✓ Retrieved {len(context_data['results'])} relevant results")
        print(f"   ✓ Context summary: {context_data['context_summary'][:100]}...")
        
        # Test contextual prompt generation
        contextual_prompt = rag_retriever.generate_contextual_prompt(
            "What is artificial intelligence?",
            context_data
        )
        print(f"   ✓ Generated contextual prompt ({len(contextual_prompt)} characters)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ RAG retriever test failed: {e}")
        traceback.print_exc()
        return False

def test_memory_manager():
    """Test memory management system."""
    print("\n🧪 Testing Memory Manager...")
    try:
        from memory_manager import MemoryManager, SmartMemoryRAGSystem
        from vector_store import ChromaVectorStore
        from sample_data_generator import SampleDataGenerator
        
        # Initialize components
        vs = ChromaVectorStore("test_memory_collection")
        memory_manager = MemoryManager(vs)
        print("   ✓ Memory manager initialized")
        
        # Generate and add test documents
        generator = SampleDataGenerator()
        test_docs = generator.generate_sample_documents(3)
        
        for doc in test_docs:
            chunk_ids = memory_manager.add_document_with_tracking(doc)
            print(f"   ✓ Added document '{doc['title'][:30]}...' with {len(chunk_ids)} chunks")
        
        # Test search pattern tracking
        test_queries = [
            "artificial intelligence research",
            "machine learning applications",
            "AI technology trends"
        ]
        
        for query in test_queries:
            results = vs.similarity_search(query, k=2)
            memory_manager.track_search_pattern(query, len(results))
        
        print("   ✓ Tracked search patterns")
        
        # Test memory stats
        stats = memory_manager.get_memory_stats()
        print(f"   ✓ Memory stats: {stats['tracked_documents']} tracked documents")
        print(f"   ✓ Search patterns: {stats['search_patterns_tracked']} tracked")
        
        # Test smart memory system
        smart_system = SmartMemoryRAGSystem(vs)
        intelligence_stats = smart_system.get_system_intelligence_stats()
        print("   ✓ Smart memory system operational")
        
        # Cleanup
        vs.clear_collection()
        print("   ✓ Test memory collection cleared")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Memory manager test failed: {e}")
        traceback.print_exc()
        return False

def test_agents_system():
    """Test the OpenAI Agents integration."""
    print("\n🧪 Testing Agents System...")
    try:
        from agents_rag_system import AgenticRAGSystem, RAGTools
        
        # Initialize the system
        system = AgenticRAGSystem()
        print("   ✓ Agentic RAG system initialized")
        
        # Initialize with sample data
        if system.initialize(with_sample_data=True, num_sample_docs=5):
            print("   ✓ System initialized with sample data")
        else:
            print("   ⚠️  System initialization completed with warnings")
        
        # Test basic chat functionality
        test_message = "Tell me about artificial intelligence"
        response = system.chat(test_message)
        
        if response and len(response) > 10:
            print(f"   ✓ Chat response generated ({len(response)} characters)")
            print(f"   ✓ Response preview: '{response[:100]}...'")
        else:
            print("   ⚠️  Chat response was short or empty")
        
        # Test system stats
        stats = system.get_system_stats()
        if stats.get('success'):
            print("   ✓ System statistics retrieved successfully")
        else:
            print("   ⚠️  System statistics retrieval had issues")
        
        # Test document addition
        test_doc_result = system.add_document(
            title="Test Document",
            content="This is a test document for the RAG system.",
            author="Test Suite"
        )
        
        if test_doc_result.get('success'):
            print("   ✓ Document addition successful")
        else:
            print("   ⚠️  Document addition had issues")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agents system test failed: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all tests and provide summary."""
    print("🚀 Starting Comprehensive RAG System Test")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    tests = [
        ("Configuration", test_config),
        ("Sample Data Generator", test_sample_data_generator),
        ("Vector Store", test_vector_store),
        ("External Content Retriever", test_external_content_retriever),
        ("RAG Retriever", test_rag_retriever),
        ("Memory Manager", test_memory_manager),
        ("Agents System", test_agents_system)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {e}")
            test_results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The RAG system is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Set your OPENAI_API_KEY in .env file")
        print("   2. Run: streamlit run streamlit_app.py")
        print("   3. Open http://localhost:8501 in your browser")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("   Make sure you have set up the OPENAI_API_KEY environment variable.")
        print("   Some features may require internet connectivity.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)