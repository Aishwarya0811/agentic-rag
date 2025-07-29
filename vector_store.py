import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import numpy as np
from openai import OpenAI
from config import Config

class ChromaVectorStore:
    """ChromaDB-based vector store for document embeddings and retrieval."""
    
    def __init__(self, collection_name: str = "rag_documents"):
        """Initialize ChromaDB vector store."""
        Config.validate()
        
        # Initialize OpenAI client for embeddings
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(Config.CHROMA_DB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "RAG document embeddings"}
        )
        
        print(f"Initialized ChromaDB collection: {collection_name}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI's embedding model."""
        try:
            response = self.openai_client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=text.replace("\n", " ")
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into overlapping chunks."""
        chunk_size = chunk_size or Config.CHUNK_SIZE
        overlap = overlap or Config.CHUNK_OVERLAP
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence or word boundary
            if end < len(text):
                # Look for sentence boundary
                sentence_end = text.rfind('. ', start, end)
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end != -1 and word_end > start + chunk_size // 2:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + 1, end - overlap)
            
            if start >= len(text):
                break
        
        return chunks
    
    def add_document(self, document: Dict[str, Any]) -> List[str]:
        """Add a document to the vector store with chunking."""
        doc_id = document.get('id', str(uuid.uuid4()))
        content = document.get('content', '')
        
        if not content:
            print(f"Warning: Empty content for document {doc_id}")
            return []
        
        # Chunk the document content
        chunks = self._chunk_text(content)
        chunk_ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            
            # Generate embedding for chunk
            embedding = self._generate_embedding(chunk)
            
            if not embedding:
                print(f"Warning: Failed to generate embedding for chunk {chunk_id}")
                continue
            
            # Prepare metadata
            metadata = {
                "document_id": doc_id,
                "chunk_index": i,
                "title": document.get('title', ''),
                "author": document.get('author', ''),
                "date": document.get('date', ''),
                "topic": document.get('topic', ''),
                "type": document.get('type', ''),
                "chunk_text": chunk[:500]  # First 500 chars for metadata
            }
            
            # Add to collection
            try:
                self.collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[metadata]
                )
            except Exception as e:
                print(f"Error adding chunk {chunk_id}: {e}")
        
        print(f"Added document {doc_id} with {len(chunk_ids)} chunks")
        return chunk_ids
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Add multiple documents to the vector store."""
        result = {}
        
        for doc in documents:
            doc_id = doc.get('id', str(uuid.uuid4()))
            chunk_ids = self.add_document(doc)
            result[doc_id] = chunk_ids
        
        print(f"Successfully added {len(documents)} documents to vector store")
        return result
    
    def similarity_search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Perform similarity search on the vector store."""
        k = k or Config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        if not query_embedding:
            print("Error: Failed to generate query embedding")
            return []
        
        try:
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            
            if results['documents'][0]:  # Check if we have results
                for i in range(len(results['documents'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                    }
                    formatted_results.append(result)
            
            return formatted_results
        
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document by ID."""
        try:
            results = self.collection.get(
                ids=[doc_id],
                include=['documents', 'metadatas']
            )
            
            if results['documents']:
                return {
                    'id': results['ids'][0],
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0]
                }
            
            return None
        
        except Exception as e:
            print(f"Error retrieving document {doc_id}: {e}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and all its chunks from the vector store."""
        try:
            # Find all chunks for this document
            results = self.collection.get(
                where={"document_id": doc_id},
                include=['ids']
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Deleted document {doc_id} and {len(results['ids'])} chunks")
                return True
            else:
                print(f"Document {doc_id} not found")
                return False
        
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
    
    def update_document(self, document: Dict[str, Any]) -> List[str]:
        """Update an existing document by deleting and re-adding it."""
        doc_id = document.get('id')
        
        if not doc_id:
            print("Error: Document ID required for update")
            return []
        
        # Delete existing document
        self.delete_document(doc_id)
        
        # Add updated document
        return self.add_document(document)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            
            # Get sample of metadata to analyze topics/types
            if count > 0:
                sample_results = self.collection.get(
                    limit=min(100, count),
                    include=['metadatas']
                )
                
                topics = set()
                doc_types = set()
                authors = set()
                
                for metadata in sample_results['metadatas']:
                    if metadata.get('topic'):
                        topics.add(metadata['topic'])
                    if metadata.get('type'):
                        doc_types.add(metadata['type'])
                    if metadata.get('author'):
                        authors.add(metadata['author'])
                
                return {
                    'total_chunks': count,
                    'unique_topics': len(topics),
                    'document_types': list(doc_types),
                    'sample_topics': list(topics)[:10],  # First 10 topics
                    'unique_authors': len(authors)
                }
            else:
                return {'total_chunks': 0}
        
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {'error': str(e)}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection.name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection.name,
                metadata={"description": "RAG document embeddings"}
            )
            print("Collection cleared successfully")
            return True
        
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False

if __name__ == "__main__":
    # Test the vector store
    from sample_data_generator import SampleDataGenerator
    
    # Generate sample documents
    generator = SampleDataGenerator()
    docs = generator.generate_sample_documents(3)
    
    # Initialize vector store
    vs = ChromaVectorStore()
    
    # Add documents
    vs.add_documents(docs)
    
    # Perform search
    results = vs.similarity_search("artificial intelligence research")
    
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"Score: {result['similarity_score']:.3f}")
        print(f"Title: {result['metadata']['title']}")
        print("-" * 50)