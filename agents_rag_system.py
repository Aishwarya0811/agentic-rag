from typing import Dict, Any, List, Optional
from agents import Agent
from openai import OpenAI
import json
from rag_retriever import AdvancedRAGRetriever, QueryProcessor
from vector_store import ChromaVectorStore
from sample_data_generator import SampleDataGenerator
from external_content_retriever import ContentAggregator
from config import Config

class RAGTools:
    """RAG-specific tools for OpenAI Agents."""
    
    def __init__(self):
        self.rag_retriever = AdvancedRAGRetriever()
        self.query_processor = QueryProcessor()
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def search_knowledge_base(self, query: str, num_results: int = 5, include_external: bool = True) -> Dict[str, Any]:
        """
        Search the knowledge base for relevant information.
        
        Args:
            query: The search query
            num_results: Number of results to return
            include_external: Whether to include external sources
        
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Enhance the query for better retrieval
            enhanced_query_info = self.query_processor.enhance_query(query)
            
            # Retrieve relevant context
            context_data = self.rag_retriever.retrieve_relevant_context(
                enhanced_query_info['enhanced'],
                k=num_results,
                include_external=include_external,
                rerank=True
            )
            
            return {
                'success': True,
                'original_query': query,
                'enhanced_query': enhanced_query_info['enhanced'],
                'results': context_data['results'],
                'context_summary': context_data['context_summary'],
                'total_found': context_data['total_results_found']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_query': query
            }
    
    def add_document_to_knowledge_base(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new document to the knowledge base.
        
        Args:
            document: Document dictionary with content and metadata
        
        Returns:
            Dictionary with operation result
        """
        try:
            chunk_ids = self.rag_retriever.vector_store.add_document(document)
            
            return {
                'success': True,
                'document_id': document.get('id', 'unknown'),
                'chunks_created': len(chunk_ids),
                'message': f"Successfully added document with {len(chunk_ids)} chunks"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'document_id': document.get('id', 'unknown')
            }
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            stats = self.rag_retriever.get_retrieval_stats()
            return {
                'success': True,
                'stats': stats
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_sample_content(self, topic: str, num_documents: int = 5) -> Dict[str, Any]:
        """Generate sample content for the knowledge base."""
        try:
            generator = SampleDataGenerator()
            documents = []
            
            for _ in range(num_documents):
                # Focus on the requested topic
                sample_docs = generator.generate_sample_documents(1)
                if sample_docs:
                    doc = sample_docs[0]
                    # Override topic if specified
                    if topic:
                        doc['topic'] = topic
                        doc['content'] = doc['content'].replace(doc['topic'], topic)
                    documents.append(doc)
            
            # Add to knowledge base
            self.rag_retriever.vector_store.add_documents(documents)
            
            return {
                'success': True,
                'documents_generated': len(documents),
                'topic': topic,
                'message': f"Generated and added {len(documents)} sample documents about {topic}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'topic': topic
            }

class RAGAgent:
    """Main RAG Agent using OpenAI Agents SDK."""
    
    def __init__(self):
        self.rag_tools = RAGTools()
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Initialize the main RAG agent
        self.agent = Agent(
            name="RAG Research Assistant",
            instructions="""
            You are an advanced RAG (Retrieval-Augmented Generation) research assistant with access to a comprehensive knowledge base.
            
            Your capabilities include:
            1. Searching the knowledge base for relevant information
            2. Adding new documents to the knowledge base
            3. Generating contextual responses based on retrieved information
            4. Providing statistics about the knowledge base
            5. Generating sample content for demonstration
            
            Always:
            - Use the search_knowledge_base tool when users ask questions that could benefit from document retrieval
            - Provide accurate, well-sourced responses based on the retrieved information
            - Cite your sources when referencing specific documents
            - Be transparent about the limitations of your knowledge base
            - Offer to add new information if the current knowledge base is insufficient
            
            When searching:
            - Use comprehensive search queries
            - Consider multiple perspectives on the topic
            - Summarize findings clearly and concisely
            """,
            model=Config.LLM_MODEL
        )
        
        # Add RAG-specific tools to the agent
        self._register_tools()
    
    def _register_tools(self):
        """Register RAG tools with the agent."""
        
        # Tool for searching the knowledge base
        def search_knowledge_base_tool(query: str, num_results: int = 5, include_external: bool = True) -> str:
            """Search the RAG knowledge base for relevant information."""
            result = self.rag_tools.search_knowledge_base(query, num_results, include_external)
            
            if result['success']:
                # Format results for the agent
                response_parts = [
                    f"Search Results for: {result['original_query']}",
                    f"Enhanced Query: {result['enhanced_query']}",
                    f"Context Summary: {result['context_summary']}",
                    f"Total Results Found: {result['total_found']}",
                    "\nRelevant Documents:"
                ]
                
                for i, doc in enumerate(result['results'], 1):
                    metadata = doc['metadata']
                    response_parts.append(f"\n--- Document {i} ---")
                    response_parts.append(f"Title: {metadata.get('title', 'Unknown')}")
                    response_parts.append(f"Type: {metadata.get('type', 'Unknown')}")
                    response_parts.append(f"Author: {metadata.get('author', 'Unknown')}")
                    response_parts.append(f"Relevance Score: {doc['similarity_score']:.3f}")
                    response_parts.append(f"Content Preview: {doc['content'][:300]}...")
                
                return '\n'.join(response_parts)
            else:
                return f"Search failed: {result['error']}"
        
        # Tool for adding documents
        def add_document_tool(title: str, content: str, author: str = "User", doc_type: str = "user_document") -> str:
            """Add a new document to the knowledge base."""
            document = {
                'id': f"user_doc_{hash(title)}",
                'title': title,
                'content': content,
                'author': author,
                'type': doc_type,
                'topic': 'user_provided',
                'date': '2024-01-01'
            }
            
            result = self.rag_tools.add_document_to_knowledge_base(document)
            
            if result['success']:
                return f"Successfully added document '{title}' with {result['chunks_created']} chunks to the knowledge base."
            else:
                return f"Failed to add document: {result['error']}"
        
        # Tool for getting stats
        def get_stats_tool() -> str:
            """Get statistics about the RAG knowledge base."""
            result = self.rag_tools.get_knowledge_base_stats()
            
            if result['success']:
                stats = result['stats']
                vector_stats = stats['vector_store_stats']
                
                return f"""
                Knowledge Base Statistics:
                - Total document chunks: {vector_stats.get('total_chunks', 0)}
                - Unique topics: {vector_stats.get('unique_topics', 0)}
                - Document types: {', '.join(vector_stats.get('document_types', []))}
                - External sources enabled: {stats.get('external_sources_enabled', False)}
                - Reranking enabled: {stats.get('reranking_enabled', False)}
                """
            else:
                return f"Failed to get stats: {result['error']}"
        
        # Tool for generating sample content
        def generate_sample_content_tool(topic: str, num_documents: int = 3) -> str:
            """Generate sample documents about a specific topic."""
            result = self.rag_tools.generate_sample_content(topic, num_documents)
            
            if result['success']:
                return f"Generated {result['documents_generated']} sample documents about '{topic}' and added them to the knowledge base."
            else:
                return f"Failed to generate sample content: {result['error']}"
        
        # Register tools with the agent (this would be done via the SDK's tool registration system)
        # Note: The exact tool registration method depends on the OpenAI Agents SDK implementation
        self.agent.tools = {
            'search_knowledge_base': search_knowledge_base_tool,
            'add_document': add_document_tool,
            'get_knowledge_base_stats': get_stats_tool,
            'generate_sample_content': generate_sample_content_tool
        }
    
    def chat(self, message: str) -> str:
        """Process a chat message through the RAG agent."""
        try:
            # For now, implement a simple dispatch mechanism
            # In the full OpenAI Agents SDK, this would be handled automatically
            
            message_lower = message.lower()
            
            # Check if this is a search query
            if any(keyword in message_lower for keyword in ['what', 'how', 'why', 'explain', 'tell me about', 'find', 'search']):
                # Perform knowledge base search
                search_result = self.rag_tools.search_knowledge_base(message, num_results=5, include_external=True)
                
                if search_result['success'] and search_result['results']:
                    # Generate contextual response
                    contextual_prompt = self.rag_tools.rag_retriever.generate_contextual_prompt(message, search_result)
                    
                    # Use OpenAI to generate final response
                    response = self.openai_client.chat.completions.create(
                        model=Config.LLM_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a helpful research assistant. Use the provided context to give comprehensive, accurate answers."},
                            {"role": "user", "content": contextual_prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    
                    return response.choices[0].message.content
                else:
                    return f"I couldn't find relevant information about '{message}'. Would you like me to search for external content or add new information to the knowledge base?"
            
            # Check if this is a request to add content
            elif 'add' in message_lower and ('document' in message_lower or 'content' in message_lower):
                return "I can help you add a document to the knowledge base. Please provide the title and content you'd like to add."
            
            # Check if this is a request for stats
            elif 'stats' in message_lower or 'statistics' in message_lower or 'status' in message_lower:
                stats_result = self.rag_tools.get_knowledge_base_stats()
                if stats_result['success']:
                    stats = stats_result['stats']
                    vector_stats = stats['vector_store_stats']
                    
                    return f"""
                    Here are the current knowledge base statistics:
                    
                    📊 **Vector Store Stats:**
                    - Total document chunks: {vector_stats.get('total_chunks', 0)}
                    - Unique topics: {vector_stats.get('unique_topics', 0)}
                    - Document types available: {', '.join(vector_stats.get('document_types', []))}
                    
                    🔧 **System Features:**
                    - External sources: {'✅ Enabled' if stats.get('external_sources_enabled') else '❌ Disabled'}
                    - Result reranking: {'✅ Enabled' if stats.get('reranking_enabled') else '❌ Disabled'}
                    
                    The system is ready to help you search and retrieve information!
                    """
                else:
                    return f"Sorry, I couldn't retrieve the statistics: {stats_result['error']}"
            
            # Default response for general conversation
            else:
                response = self.openai_client.chat.completions.create(
                    model=Config.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful RAG research assistant. You have access to a knowledge base and can search for information, add documents, and provide insights."},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                return response.choices[0].message.content
        
        except Exception as e:
            return f"I encountered an error while processing your message: {str(e)}"
    
    def initialize_with_sample_data(self, num_docs: int = 10):
        """Initialize the system with sample data."""
        try:
            generator = SampleDataGenerator()
            sample_docs = generator.generate_sample_documents(num_docs)
            
            # Add sample documents to the knowledge base
            result = self.rag_tools.rag_retriever.vector_store.add_documents(sample_docs)
            
            print(f"Initialized RAG system with {num_docs} sample documents")
            print(f"Created {sum(len(chunks) for chunks in result.values())} total chunks")
            
            return True
            
        except Exception as e:
            print(f"Error initializing sample data: {e}")
            return False

class AgenticRAGSystem:
    """Main system orchestrator for the Agentic RAG system."""
    
    def __init__(self):
        """Initialize the complete RAG system."""
        self.rag_agent = RAGAgent()
        self.initialized = False
        
    def initialize(self, with_sample_data: bool = True, num_sample_docs: int = 15):
        """Initialize the RAG system."""
        try:
            Config.validate()
            
            if with_sample_data:
                success = self.rag_agent.initialize_with_sample_data(num_sample_docs)
                if not success:
                    print("Warning: Failed to initialize with sample data")
            
            self.initialized = True
            print("✅ Agentic RAG System initialized successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize RAG system: {e}")
            return False
    
    def chat(self, message: str) -> str:
        """Main chat interface."""
        if not self.initialized:
            return "System not initialized. Please run initialize() first."
        
        return self.rag_agent.chat(message)
    
    def add_document(self, title: str, content: str, author: str = "User", doc_type: str = "user_document") -> Dict[str, Any]:
        """Add a document to the knowledge base."""
        if not self.initialized:
            return {"success": False, "error": "System not initialized"}
        
        document = {
            'id': f"user_doc_{hash(title)}",
            'title': title,
            'content': content,
            'author': author,
            'type': doc_type,
            'topic': 'user_provided',
            'date': '2024-01-01'
        }
        
        return self.rag_agent.rag_tools.add_document_to_knowledge_base(document)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        if not self.initialized:
            return {"success": False, "error": "System not initialized"}
        
        return self.rag_agent.rag_tools.get_knowledge_base_stats()

if __name__ == "__main__":
    # Test the agentic RAG system
    print("🚀 Initializing Agentic RAG System...")
    
    system = AgenticRAGSystem()
    
    if system.initialize():
        print("\n" + "="*50)
        print("🤖 RAG Agent Ready! Try these example queries:")
        print("- 'Tell me about artificial intelligence'")
        print("- 'What are the latest developments in climate change?'")
        print("- 'Show me system statistics'")
        print("="*50)
        
        # Test queries
        test_queries = [
            "What can you tell me about artificial intelligence?",
            "Show me the system statistics",
            "How does machine learning work?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            response = system.chat(query)
            print(f"🤖 Response: {response[:200]}..." if len(response) > 200 else f"🤖 Response: {response}")
            print("-" * 50)
    
    else:
        print("❌ Failed to initialize the system. Please check your configuration.")