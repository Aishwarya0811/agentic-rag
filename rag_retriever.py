from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from openai import OpenAI
from vector_store import ChromaVectorStore
from external_content_retriever import ContentAggregator
from config import Config
import re

class AdvancedRAGRetriever:
    """Advanced RAG retrieval system with semantic search and contextual ranking."""
    
    def __init__(self):
        """Initialize the RAG retriever."""
        self.vector_store = ChromaVectorStore()
        self.content_aggregator = ContentAggregator()
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def retrieve_relevant_context(
        self, 
        query: str, 
        k: int = None, 
        include_external: bool = True,
        rerank: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query using advanced RAG techniques.
        
        Args:
            query: The user's query
            k: Number of results to retrieve
            include_external: Whether to fetch external content
            rerank: Whether to rerank results for relevance
        
        Returns:
            Dictionary containing retrieved context and metadata
        """
        k = k or Config.TOP_K_RESULTS
        
        # Step 1: Perform initial similarity search
        initial_results = self.vector_store.similarity_search(query, k=k*2)  # Get more for reranking
        
        # Step 2: Optionally fetch external content
        external_results = []
        if include_external and len(initial_results) < k:
            external_content = self._fetch_external_content(query)
            external_results = self._convert_external_to_results(external_content, query)
        
        # Step 3: Combine and deduplicate results
        all_results = initial_results + external_results
        deduplicated_results = self._deduplicate_results(all_results)
        
        # Step 4: Rerank results if requested
        if rerank and len(deduplicated_results) > k:
            reranked_results = self._rerank_results(query, deduplicated_results)
            final_results = reranked_results[:k]
        else:
            final_results = deduplicated_results[:k]
        
        # Step 5: Generate contextual summary
        context_summary = self._generate_context_summary(query, final_results)
        
        return {
            'query': query,
            'results': final_results,
            'context_summary': context_summary,
            'total_results_found': len(all_results),
            'external_sources_used': len(external_results),
            'retrieval_metadata': {
                'reranked': rerank,
                'external_content_included': include_external,
                'final_result_count': len(final_results)
            }
        }
    
    def _fetch_external_content(self, query: str) -> List[Dict[str, Any]]:
        """Fetch external content and add to vector store."""
        try:
            # Extract key terms from query for better search
            key_terms = self._extract_key_terms(query)
            
            # Gather external content
            external_content = self.content_aggregator.gather_comprehensive_content(key_terms)
            
            # Add to vector store for future use
            if external_content:
                self.vector_store.add_documents(external_content)
                print(f"Added {len(external_content)} external documents to vector store")
            
            return external_content
            
        except Exception as e:
            print(f"Error fetching external content: {e}")
            return []
    
    def _convert_external_to_results(self, external_content: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Convert external content to result format."""
        results = []
        
        for content in external_content:
            # Generate embeddings and calculate similarity
            query_embedding = self.vector_store._generate_embedding(query)
            content_embedding = self.vector_store._generate_embedding(content['content'][:1000])
            
            if query_embedding and content_embedding:
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, content_embedding)
                
                result = {
                    'id': content['id'],
                    'content': content['content'],
                    'metadata': {
                        'title': content['title'],
                        'author': content['author'],
                        'date': content['date'],
                        'topic': content['topic'],
                        'type': content['type'],
                        'source_url': content.get('source_url', ''),
                        'chunk_text': content['content'][:500],
                        'external_source': True
                    },
                    'distance': 1 - similarity,
                    'similarity_score': similarity
                }
                results.append(result)
        
        return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar results."""
        if not results:
            return results
        
        deduplicated = []
        seen_content = set()
        
        for result in results:
            # Create a content hash for deduplication
            content_snippet = result['content'][:200].lower().strip()
            content_hash = hash(content_snippet)
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                deduplicated.append(result)
        
        return deduplicated
    
    def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results using advanced relevance scoring."""
        
        def calculate_advanced_score(result: Dict[str, Any]) -> float:
            base_score = result['similarity_score']
            
            # Boost score based on content type
            type_boost = {
                'research_paper': 1.2,
                'technical_report': 1.1,
                'wikipedia_article': 1.05,
                'news_article': 1.0,
                'summary': 0.95
            }
            
            content_type = result['metadata'].get('type', 'unknown')
            score = base_score * type_boost.get(content_type, 1.0)
            
            # Boost recent content
            date_str = result['metadata'].get('date', '')
            if date_str and '2024' in date_str:
                score *= 1.1
            
            # Boost based on content length (longer content might be more comprehensive)
            content_length = len(result['content'])
            if content_length > 2000:
                score *= 1.05
            elif content_length < 500:
                score *= 0.95
            
            # Boost if query terms appear in title
            title = result['metadata'].get('title', '').lower()
            query_terms = self._extract_key_terms(query).lower().split()
            
            title_matches = sum(1 for term in query_terms if term in title)
            if title_matches > 0:
                score *= (1 + 0.1 * title_matches)
            
            return score
        
        # Calculate advanced scores and sort
        for result in results:
            result['advanced_score'] = calculate_advanced_score(result)
        
        return sorted(results, key=lambda x: x['advanced_score'], reverse=True)
    
    def _generate_context_summary(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Generate a summary of the retrieved context."""
        if not results:
            return "No relevant context found for the query."
        
        # Prepare context information
        topics = set()
        sources = set()
        content_types = set()
        
        for result in results:
            metadata = result['metadata']
            if metadata.get('topic'):
                topics.add(metadata['topic'])
            if metadata.get('author'):
                sources.add(metadata['author'])
            if metadata.get('type'):
                content_types.add(metadata['type'])
        
        # Generate summary
        summary_parts = []
        
        summary_parts.append(f"Found {len(results)} relevant sources for your query about {query}.")
        
        if topics:
            summary_parts.append(f"Related topics include: {', '.join(list(topics)[:3])}.")
        
        if content_types:
            type_counts = {}
            for result in results:
                content_type = result['metadata'].get('type', 'unknown')
                type_counts[content_type] = type_counts.get(content_type, 0) + 1
            
            type_summary = ', '.join([f"{count} {type.replace('_', ' ')}" for type, count in type_counts.items()])
            summary_parts.append(f"Sources include: {type_summary}.")
        
        # Add relevance information
        avg_score = sum(result['similarity_score'] for result in results) / len(results)
        summary_parts.append(f"Average relevance score: {avg_score:.2f}")
        
        return ' '.join(summary_parts)
    
    def _extract_key_terms(self, text: str) -> str:
        """Extract key terms from text for better search."""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'what', 'how', 'when', 'where', 'why'
        }
        
        # Extract words and filter
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return the most important terms
        return ' '.join(key_terms[:5])
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def generate_contextual_prompt(self, query: str, context_data: Dict[str, Any]) -> str:
        """Generate a contextual prompt for the LLM using retrieved information."""
        
        # Extract relevant information from context
        results = context_data.get('results', [])
        context_summary = context_data.get('context_summary', '')
        
        if not results:
            return f"User query: {query}\n\nNo relevant context found. Please provide a general response."
        
        # Build the contextual prompt
        prompt_parts = []
        
        prompt_parts.append("You are an AI assistant with access to relevant information. Use the following context to provide a comprehensive and accurate response.")
        prompt_parts.append(f"\nUser query: {query}")
        prompt_parts.append(f"\nContext summary: {context_summary}")
        prompt_parts.append("\nRelevant information:")
        
        for i, result in enumerate(results[:5], 1):  # Limit to top 5 results
            metadata = result['metadata']
            content_preview = result['content'][:800] + "..." if len(result['content']) > 800 else result['content']
            
            prompt_parts.append(f"\n--- Source {i} ---")
            prompt_parts.append(f"Title: {metadata.get('title', 'Unknown')}")
            prompt_parts.append(f"Type: {metadata.get('type', 'Unknown')}")
            prompt_parts.append(f"Author: {metadata.get('author', 'Unknown')}")
            prompt_parts.append(f"Relevance Score: {result['similarity_score']:.3f}")
            prompt_parts.append(f"Content: {content_preview}")
        
        prompt_parts.append("\nInstructions:")
        prompt_parts.append("1. Use the provided context to answer the user's query comprehensively")
        prompt_parts.append("2. Cite specific sources when referencing information")
        prompt_parts.append("3. If the context doesn't fully address the query, acknowledge this")
        prompt_parts.append("4. Provide a well-structured, informative response")
        
        return '\n'.join(prompt_parts)
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about the retrieval system."""
        vector_stats = self.vector_store.get_collection_stats()
        
        return {
            'vector_store_stats': vector_stats,
            'total_embeddings': vector_stats.get('total_chunks', 0),
            'supported_content_types': ['research_paper', 'news_article', 'technical_report', 'summary', 'wikipedia_article'],
            'external_sources_enabled': True,
            'reranking_enabled': True
        }

class QueryProcessor:
    """Processes and enhances queries for better retrieval."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def enhance_query(self, original_query: str) -> Dict[str, str]:
        """Enhance the original query for better retrieval."""
        try:
            # Use LLM to expand and enhance the query
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a query enhancement specialist. Given a user query, create an enhanced version that includes related terms, synonyms, and specific concepts that would help in document retrieval. Keep it concise but comprehensive."
                    },
                    {
                        "role": "user",
                        "content": f"Original query: {original_query}\n\nProvide an enhanced query for better document retrieval:"
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            enhanced_query = response.choices[0].message.content.strip()
            
            return {
                'original': original_query,
                'enhanced': enhanced_query,
                'key_terms': self._extract_key_terms(enhanced_query)
            }
            
        except Exception as e:
            print(f"Error enhancing query: {e}")
            return {
                'original': original_query,
                'enhanced': original_query,
                'key_terms': original_query
            }
    
    def _extract_key_terms(self, text: str) -> str:
        """Extract key terms from enhanced query."""
        # Similar to the method in AdvancedRAGRetriever
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
        }
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 3]
        
        return ' '.join(key_terms[:8])

if __name__ == "__main__":
    # Test the RAG retriever
    from sample_data_generator import SampleDataGenerator
    
    # Initialize components
    retriever = AdvancedRAGRetriever()
    query_processor = QueryProcessor()
    
    # Generate and add sample data
    generator = SampleDataGenerator()
    sample_docs = generator.generate_sample_documents(10)
    retriever.vector_store.add_documents(sample_docs)
    
    # Test query processing and retrieval
    test_query = "artificial intelligence applications in healthcare"
    
    # Enhance query
    enhanced_query_info = query_processor.enhance_query(test_query)
    print(f"Original query: {enhanced_query_info['original']}")
    print(f"Enhanced query: {enhanced_query_info['enhanced']}")
    
    # Retrieve context
    context_data = retriever.retrieve_relevant_context(
        enhanced_query_info['enhanced'], 
        k=5, 
        include_external=False  # Skip external for testing
    )
    
    print(f"\nRetrieval results:")
    print(f"Context summary: {context_data['context_summary']}")
    print(f"Found {len(context_data['results'])} results")
    
    # Generate contextual prompt
    contextual_prompt = retriever.generate_contextual_prompt(test_query, context_data)
    print(f"\nGenerated contextual prompt length: {len(contextual_prompt)} characters")