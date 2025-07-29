#!/usr/bin/env python3
"""
Demo script for the Advanced RAG System.
Showcases key features and capabilities.
"""

import time
import sys
from typing import Dict, Any

def print_header(title: str, char: str = "="):
    """Print a formatted header."""
    print(f"\n{char * 60}")
    print(f"🎯 {title}")
    print(f"{char * 60}")

def print_step(step: str, description: str = ""):
    """Print a demo step."""
    print(f"\n🔹 {step}")
    if description:
        print(f"   {description}")

def demonstrate_sample_data_generation():
    """Demonstrate sample data generation."""
    print_header("Sample Data Generation")
    
    try:
        from sample_data_generator import SampleDataGenerator
        
        print_step("Initializing Sample Data Generator")
        generator = SampleDataGenerator()
        
        print_step("Generating Various Document Types")
        
        # Generate different types of documents
        research_paper = generator.generate_research_paper("artificial intelligence")
        news_article = generator.generate_news_article("climate change")
        technical_report = generator.generate_technical_report("quantum computing")
        summary = generator.generate_summary("biotechnology")
        
        print(f"✅ Research Paper: '{research_paper['title']}'")
        print(f"   Author: {research_paper['author']}")
        print(f"   Length: {len(research_paper['content'])} characters")
        
        print(f"✅ News Article: '{news_article['title']}'")
        print(f"   Date: {news_article['date']}")
        print(f"   Topic: {news_article['topic']}")
        
        print(f"✅ Technical Report: '{technical_report['title']}'")
        print(f"   Type: {technical_report['type']}")
        
        print(f"✅ Summary: '{summary['title']}'")
        print(f"   Content Preview: {summary['content'][:150]}...")
        
        print_step("Batch Document Generation")
        batch_docs = generator.generate_sample_documents(5)
        
        print(f"Generated {len(batch_docs)} documents:")
        for i, doc in enumerate(batch_docs, 1):
            print(f"   {i}. {doc['type']}: {doc['title'][:40]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demonstrate_vector_store():
    """Demonstrate vector store operations."""
    print_header("Vector Store Operations")
    
    try:
        from vector_store import ChromaVectorStore
        from sample_data_generator import SampleDataGenerator
        
        print_step("Initializing Vector Store", "Using ChromaDB for persistent storage")
        vs = ChromaVectorStore("demo_collection")
        
        print_step("Generating Demo Documents")
        generator = SampleDataGenerator()
        demo_docs = generator.generate_sample_documents(5)
        
        print_step("Adding Documents to Vector Store")
        result = vs.add_documents(demo_docs)
        
        total_chunks = sum(len(chunks) for chunks in result.values())
        print(f"✅ Added {len(demo_docs)} documents with {total_chunks} total chunks")
        
        print_step("Demonstrating Semantic Search")
        
        # Perform various searches
        searches = [
            ("artificial intelligence", "AI-related content"),
            ("climate change research", "Environmental research"),
            ("quantum computing applications", "Quantum tech applications"),
            ("biotechnology innovations", "Biotech developments")
        ]
        
        for query, description in searches:
            print(f"\n🔍 Searching: '{query}' ({description})")
            results = vs.similarity_search(query, k=2)
            
            if results:
                for i, result in enumerate(results, 1):
                    score = result['similarity_score']
                    title = result['metadata'].get('title', 'Unknown')
                    print(f"   {i}. Score: {score:.3f} - {title[:50]}...")
            else:
                print("   No results found")
        
        print_step("Vector Store Statistics")
        stats = vs.get_collection_stats()
        print(f"📊 Total chunks: {stats.get('total_chunks', 0)}")
        print(f"📊 Unique topics: {stats.get('unique_topics', 0)}")
        print(f"📊 Document types: {', '.join(stats.get('document_types', []))}")
        
        # Cleanup
        print_step("Cleaning Up Demo Collection")
        vs.clear_collection()
        print("✅ Demo collection cleared")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_external_content():
    """Demonstrate external content retrieval."""
    print_header("External Content Retrieval")
    
    try:
        from external_content_retriever import ExternalContentRetriever, ContentAggregator
        
        print_step("Initializing External Content Retriever")
        retriever = ExternalContentRetriever()
        
        print_step("Attempting Wikipedia Fetch", "Fetching real content from Wikipedia")
        wiki_result = retriever.fetch_wikipedia_article("machine learning")
        
        if wiki_result:
            print(f"✅ Wikipedia Success: '{wiki_result['title']}'")
            print(f"   Content length: {len(wiki_result['content'])} characters")
            print(f"   Summary: {wiki_result.get('summary', 'N/A')[:100]}...")
        else:
            print("⚠️  Wikipedia fetch failed (network or API issue)")
        
        print_step("Generating Mock Content", "Simulating news articles and research papers")
        
        # Generate mock content
        news_articles = retriever.fetch_news_articles("artificial intelligence")
        research_papers = retriever.fetch_research_papers("quantum computing")
        
        print(f"✅ Generated {len(news_articles)} mock news articles")
        for article in news_articles:
            print(f"   📰 {article['title'][:60]}...")
        
        print(f"✅ Generated {len(research_papers)} mock research papers")
        for paper in research_papers:
            print(f"   📄 {paper['title'][:60]}...")
        
        print_step("Content Aggregation", "Combining multiple sources")
        aggregator = ContentAggregator()
        aggregated = aggregator.gather_comprehensive_content("deep learning")
        
        print(f"✅ Aggregated {len(aggregated)} pieces of content")
        
        # Show content type breakdown
        type_counts = {}
        for content in aggregated:
            content_type = content.get('type', 'unknown')
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        
        print("📊 Content breakdown:")
        for content_type, count in type_counts.items():
            print(f"   {content_type}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_rag_system():
    """Demonstrate the complete RAG system."""
    print_header("Complete RAG System Demo")
    
    try:
        from agents_rag_system import AgenticRAGSystem
        
        print_step("Initializing Advanced RAG System", "Setting up all components")
        system = AgenticRAGSystem()
        
        print_step("Loading with Sample Data")
        if system.initialize(with_sample_data=True, num_sample_docs=8):
            print("✅ System initialized successfully with sample data")
        else:
            print("⚠️  System initialization completed with warnings")
        
        print_step("Interactive Chat Demonstration")
        
        # Demo questions
        demo_questions = [
            "What can you tell me about artificial intelligence?",
            "Show me the current system statistics",
            "Tell me about recent developments in quantum computing",
            "What types of documents are in the knowledge base?"
        ]
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n💬 Demo Question {i}: {question}")
            print("🤔 Processing...")
            
            try:
                response = system.chat(question)
                
                # Display response with nice formatting
                if len(response) > 300:
                    print(f"🤖 Response: {response[:300]}...")
                    print("   [Response truncated for demo]")
                else:
                    print(f"🤖 Response: {response}")
                
                time.sleep(1)  # Brief pause for readability
                
            except Exception as e:
                print(f"❌ Error processing question: {e}")
        
        print_step("System Statistics")
        stats = system.get_system_stats()
        
        if stats.get('success'):
            vector_stats = stats['stats']['vector_store_stats']
            print("📊 Current System State:")
            print(f"   Total chunks: {vector_stats.get('total_chunks', 0)}")
            print(f"   Unique topics: {vector_stats.get('unique_topics', 0)}")
            print(f"   Document types: {len(vector_stats.get('document_types', []))}")
            print(f"   External sources: {'✅ Enabled' if stats['stats'].get('external_sources_enabled') else '❌ Disabled'}")
        
        print_step("Document Addition Demo")
        test_doc_result = system.add_document(
            title="Demo Document: Advanced RAG Systems",
            content="""
            This is a demonstration document for the Advanced RAG System.
            
            The system showcases several key capabilities:
            1. Intelligent document chunking and embedding
            2. Semantic search across multiple content types
            3. External content integration from various sources
            4. Automatic memory management and optimization
            5. Agent-based conversation with contextual responses
            
            The RAG (Retrieval-Augmented Generation) approach combines the power of
            large language models with dynamic information retrieval, enabling
            more accurate and contextually relevant responses.
            """,
            author="Demo System",
            doc_type="demonstration"
        )
        
        if test_doc_result.get('success'):
            print("✅ Successfully added demo document to knowledge base")
            print(f"   Created {test_doc_result.get('chunks_created', 0)} chunks")
        else:
            print(f"⚠️  Demo document addition: {test_doc_result.get('error', 'Unknown issue')}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG system demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_complete_demo():
    """Run the complete demonstration."""
    print("🎬 Advanced RAG System - Complete Demonstration")
    print("=" * 60)
    print("This demo showcases the key features of the Advanced RAG System")
    print("built with OpenAI Agents SDK, ChromaDB, and Streamlit.")
    
    demos = [
        ("Sample Data Generation", demonstrate_sample_data_generation),
        ("Vector Store Operations", demonstrate_vector_store),
        ("External Content Retrieval", demonstrate_external_content),
        ("Complete RAG System", demonstrate_rag_system)
    ]
    
    results = {}
    
    for demo_name, demo_func in demos:
        print(f"\n⏰ Starting: {demo_name}")
        try:
            success = demo_func()
            results[demo_name] = success
            
            if success:
                print(f"✅ {demo_name} completed successfully")
            else:
                print(f"⚠️  {demo_name} completed with issues")
        
        except KeyboardInterrupt:
            print(f"\n⏹️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"❌ {demo_name} failed with error: {e}")
            results[demo_name] = False
        
        # Pause between demos
        if demo_name != demos[-1][0]:  # Not the last demo
            print("\n⏸️  Press Enter to continue to next demo (or Ctrl+C to stop)...")
            try:
                input()
            except KeyboardInterrupt:
                print("\n👋 Demo stopped by user")
                break
    
    # Summary
    print_header("Demo Summary", "=")
    
    successful = sum(1 for result in results.values() if result)
    total = len(results)
    
    for demo_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} {demo_name}")
    
    print(f"\n🎯 Overall: {successful}/{total} demos completed successfully")
    
    if successful == total:
        print("\n🎉 All demonstrations completed successfully!")
        print("🚀 The Advanced RAG System is ready for use.")
        print("\n📖 Next Steps:")
        print("   1. Run 'python launch.py start' to launch the Streamlit UI")
        print("   2. Upload your own documents via the web interface")
        print("   3. Chat with the RAG assistant about your content")
        print("   4. Explore the analytics and advanced settings")
    else:
        print("\n⚠️  Some demonstrations had issues.")
        print("   The system may still be functional for basic operations.")
        print("   Check error messages above for troubleshooting.")
    
    return successful == total

if __name__ == "__main__":
    try:
        success = run_complete_demo()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
        sys.exit(0)