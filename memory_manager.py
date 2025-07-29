import time
import threading
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
from vector_store import ChromaVectorStore
from external_content_retriever import ContentAggregator
from config import Config

class MemoryManager:
    """Manages automatic memory updates and re-indexing for the RAG system."""
    
    def __init__(self, vector_store: ChromaVectorStore):
        self.vector_store = vector_store
        self.content_aggregator = ContentAggregator()
        
        # Memory state tracking
        self.memory_state_file = Config.CHROMA_DB_PATH / "memory_state.json"
        self.document_checksums: Dict[str, str] = {}
        self.last_update_time = datetime.now()
        self.update_frequency_hours = 24  # Update every 24 hours
        
        # Track search patterns for intelligent updates
        self.search_patterns: Dict[str, int] = {}
        self.popular_topics: Set[str] = set()
        
        # Background update thread
        self.update_thread: Optional[threading.Thread] = None
        self.stop_updates = False
        
        # Load existing memory state
        self._load_memory_state()
    
    def _load_memory_state(self):
        """Load memory state from disk."""
        try:
            if self.memory_state_file.exists():
                with open(self.memory_state_file, 'r') as f:
                    state = json.load(f)
                    self.document_checksums = state.get('document_checksums', {})
                    self.search_patterns = state.get('search_patterns', {})
                    self.popular_topics = set(state.get('popular_topics', []))
                    last_update_str = state.get('last_update_time')
                    if last_update_str:
                        self.last_update_time = datetime.fromisoformat(last_update_str)
                print("Loaded memory state from disk")
        except Exception as e:
            print(f"Warning: Could not load memory state: {e}")
    
    def _save_memory_state(self):
        """Save memory state to disk."""
        try:
            state = {
                'document_checksums': self.document_checksums,
                'search_patterns': self.search_patterns,
                'popular_topics': list(self.popular_topics),
                'last_update_time': self.last_update_time.isoformat()
            }
            
            with open(self.memory_state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
        except Exception as e:
            print(f"Warning: Could not save memory state: {e}")
    
    def _calculate_document_checksum(self, document: Dict[str, Any]) -> str:
        """Calculate a checksum for a document to detect changes."""
        content_str = f"{document.get('title', '')}{document.get('content', '')}{document.get('author', '')}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def track_search_pattern(self, query: str, results_found: int):
        """Track search patterns to identify popular topics."""
        # Extract key terms from query
        key_terms = self._extract_key_terms(query)
        
        # Update search patterns
        for term in key_terms.split():
            if len(term) > 3:  # Ignore short terms
                self.search_patterns[term] = self.search_patterns.get(term, 0) + 1
        
        # Identify popular topics (terms searched > 5 times)
        for term, count in self.search_patterns.items():
            if count >= 5:
                self.popular_topics.add(term)
        
        # Save state periodically
        if len(self.search_patterns) % 10 == 0:  # Every 10 searches
            self._save_memory_state()
    
    def _extract_key_terms(self, text: str) -> str:
        """Extract key terms from text."""
        import re
        
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'what', 'how', 'when', 'where', 'why'
        }
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return ' '.join(key_terms[:5])
    
    def add_document_with_tracking(self, document: Dict[str, Any]) -> List[str]:
        """Add a document and track it for future updates."""
        doc_id = document.get('id', '')
        
        if not doc_id:
            print("Warning: Document without ID cannot be tracked")
            return []
        
        # Calculate checksum
        checksum = self._calculate_document_checksum(document)
        
        # Add to vector store
        chunk_ids = self.vector_store.add_document(document)
        
        # Track the document
        if chunk_ids:
            self.document_checksums[doc_id] = checksum
            print(f"Added and tracking document: {doc_id}")
            self._save_memory_state()
        
        return chunk_ids
    
    def update_document_if_changed(self, document: Dict[str, Any]) -> bool:
        """Update a document only if it has changed."""
        doc_id = document.get('id', '')
        
        if not doc_id:
            return False
        
        # Calculate new checksum
        new_checksum = self._calculate_document_checksum(document)
        old_checksum = self.document_checksums.get(doc_id)
        
        # Check if document has changed
        if old_checksum != new_checksum:
            print(f"Document {doc_id} has changed, updating...")
            
            # Update in vector store
            chunk_ids = self.vector_store.update_document(document)
            
            if chunk_ids:
                self.document_checksums[doc_id] = new_checksum
                self._save_memory_state()
                return True
        
        return False
    
    def auto_refresh_popular_content(self):
        """Automatically refresh content for popular search topics."""
        if not self.popular_topics:
            print("No popular topics identified yet")
            return
        
        print(f"Refreshing content for popular topics: {', '.join(list(self.popular_topics)[:5])}")
        
        refreshed_count = 0
        
        for topic in list(self.popular_topics)[:3]:  # Refresh top 3 popular topics
            try:
                # Fetch fresh external content
                fresh_content = self.content_aggregator.gather_comprehensive_content(topic)
                
                if fresh_content:
                    for content in fresh_content:
                        # Check if this is new content
                        content_id = content.get('id', '')
                        if content_id not in self.document_checksums:
                            # Add new content
                            chunk_ids = self.add_document_with_tracking(content)
                            if chunk_ids:
                                refreshed_count += 1
                        else:
                            # Update existing content if changed
                            if self.update_document_if_changed(content):
                                refreshed_count += 1
                
                # Brief pause between topics
                time.sleep(1)
                
            except Exception as e:
                print(f"Error refreshing content for topic '{topic}': {e}")
        
        print(f"Auto-refresh completed: {refreshed_count} documents updated/added")
        self.last_update_time = datetime.now()
        self._save_memory_state()
    
    def cleanup_outdated_content(self, max_age_days: int = 90):
        """Remove outdated content from the vector store."""
        try:
            # Get all documents with metadata
            collection_data = self.vector_store.collection.get(include=['metadatas'])
            
            if not collection_data['metadatas']:
                return
            
            outdated_doc_ids = set()
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            for i, metadata in enumerate(collection_data['metadatas']):
                doc_date_str = metadata.get('date', '')
                if doc_date_str:
                    try:
                        doc_date = datetime.strptime(doc_date_str, '%Y-%m-%d')
                        if doc_date < cutoff_date:
                            doc_id = metadata.get('document_id', '')
                            if doc_id:
                                outdated_doc_ids.add(doc_id)
                    except ValueError:
                        continue  # Skip documents with invalid dates
            
            # Remove outdated documents
            removed_count = 0
            for doc_id in outdated_doc_ids:
                if self.vector_store.delete_document(doc_id):
                    # Remove from tracking
                    self.document_checksums.pop(doc_id, None)
                    removed_count += 1
            
            if removed_count > 0:
                print(f"Cleanup completed: removed {removed_count} outdated documents")
                self._save_memory_state()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def optimize_vector_store(self):
        """Optimize the vector store for better performance."""
        try:
            # Get collection statistics
            stats = self.vector_store.get_collection_stats()
            total_chunks = stats.get('total_chunks', 0)
            
            print(f"Optimizing vector store with {total_chunks} chunks...")
            
            # If we have too many chunks, consider consolidating similar ones
            if total_chunks > 10000:
                self._consolidate_similar_chunks()
            
            # Remove duplicate content
            self._remove_duplicate_chunks()
            
            print("Vector store optimization completed")
            
        except Exception as e:
            print(f"Error during vector store optimization: {e}")
    
    def _consolidate_similar_chunks(self):
        """Consolidate very similar chunks to reduce storage."""
        # This is a placeholder for advanced consolidation logic
        # In a production system, you might:
        # 1. Find chunks with very high similarity (>0.95)
        # 2. Merge their content
        # 3. Replace multiple chunks with a single consolidated chunk
        print("Chunk consolidation not implemented in this demo")
    
    def _remove_duplicate_chunks(self):
        """Remove exact duplicate chunks."""
        try:
            # Get all documents
            collection_data = self.vector_store.collection.get(include=['documents', 'ids'])
            
            if not collection_data['documents']:
                return
            
            content_to_ids = {}
            duplicate_ids = []
            
            # Find duplicates
            for i, content in enumerate(collection_data['documents']):
                content_hash = hashlib.md5(content.encode()).hexdigest()
                chunk_id = collection_data['ids'][i]
                
                if content_hash in content_to_ids:
                    duplicate_ids.append(chunk_id)
                else:
                    content_to_ids[content_hash] = chunk_id
            
            # Remove duplicates
            if duplicate_ids:
                self.vector_store.collection.delete(ids=duplicate_ids)
                print(f"Removed {len(duplicate_ids)} duplicate chunks")
        
        except Exception as e:
            print(f"Error removing duplicate chunks: {e}")
    
    def start_background_updates(self):
        """Start background thread for automatic updates."""
        if self.update_thread and self.update_thread.is_alive():
            print("Background updates already running")
            return
        
        self.stop_updates = False
        self.update_thread = threading.Thread(target=self._background_update_loop, daemon=True)
        self.update_thread.start()
        print("Started background memory updates")
    
    def stop_background_updates(self):
        """Stop background updates."""
        self.stop_updates = True
        if self.update_thread:
            self.update_thread.join(timeout=5)
        print("Stopped background memory updates")
    
    def _background_update_loop(self):
        """Background loop for automatic updates."""
        while not self.stop_updates:
            try:
                # Check if it's time for an update
                hours_since_update = (datetime.now() - self.last_update_time).total_seconds() / 3600
                
                if hours_since_update >= self.update_frequency_hours:
                    print("Performing scheduled memory update...")
                    
                    # Auto-refresh popular content
                    self.auto_refresh_popular_content()
                    
                    # Cleanup outdated content (weekly)
                    if hours_since_update >= 168:  # 7 days
                        self.cleanup_outdated_content()
                    
                    # Optimize vector store (monthly)
                    if hours_since_update >= 720:  # 30 days
                        self.optimize_vector_store()
                
                # Sleep for 1 hour before next check
                time.sleep(3600)
                
            except Exception as e:
                print(f"Error in background update loop: {e}")
                time.sleep(3600)  # Continue after error
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory management statistics."""
        hours_since_update = (datetime.now() - self.last_update_time).total_seconds() / 3600
        
        return {
            'tracked_documents': len(self.document_checksums),
            'search_patterns_tracked': len(self.search_patterns),
            'popular_topics': list(self.popular_topics),
            'hours_since_last_update': round(hours_since_update, 2),
            'next_update_in_hours': max(0, self.update_frequency_hours - hours_since_update),
            'background_updates_active': self.update_thread and self.update_thread.is_alive() and not self.stop_updates,
            'top_search_terms': sorted(self.search_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def force_update(self):
        """Force an immediate memory update."""
        print("Forcing immediate memory update...")
        self.auto_refresh_popular_content()
        self.cleanup_outdated_content()
        print("Forced update completed")

class SmartMemoryRAGSystem:
    """RAG system with intelligent memory management."""
    
    def __init__(self, vector_store: ChromaVectorStore):
        self.vector_store = vector_store
        self.memory_manager = MemoryManager(vector_store)
    
    def search_with_learning(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Search with automatic pattern learning."""
        # Perform the search
        results = self.vector_store.similarity_search(query, k)
        
        # Track the search pattern
        self.memory_manager.track_search_pattern(query, len(results))
        
        return {
            'results': results,
            'query': query,
            'total_found': len(results)
        }
    
    def add_document_smart(self, document: Dict[str, Any]) -> List[str]:
        """Add document with smart tracking."""
        return self.memory_manager.add_document_with_tracking(document)
    
    def start_smart_updates(self):
        """Start intelligent background updates."""
        self.memory_manager.start_background_updates()
    
    def stop_smart_updates(self):
        """Stop intelligent background updates."""
        self.memory_manager.stop_background_updates()
    
    def get_system_intelligence_stats(self) -> Dict[str, Any]:
        """Get comprehensive system intelligence statistics."""
        memory_stats = self.memory_manager.get_memory_stats()
        vector_stats = self.vector_store.get_collection_stats()
        
        return {
            'memory_management': memory_stats,
            'vector_store': vector_stats,
            'system_health': {
                'auto_updates_enabled': memory_stats['background_updates_active'],
                'learning_active': len(memory_stats['search_patterns_tracked']) > 0,
                'popular_topics_identified': len(memory_stats['popular_topics']) > 0
            }
        }

if __name__ == "__main__":
    # Test the memory manager
    from sample_data_generator import SampleDataGenerator
    
    # Initialize components
    vector_store = ChromaVectorStore("test_memory_collection")
    memory_manager = MemoryManager(vector_store)
    
    # Generate test documents
    generator = SampleDataGenerator()
    test_docs = generator.generate_sample_documents(5)
    
    # Add documents with tracking
    for doc in test_docs:
        memory_manager.add_document_with_tracking(doc)
    
    # Simulate some searches
    test_queries = [
        "artificial intelligence research",
        "machine learning applications",
        "AI technology trends",
        "artificial intelligence future"
    ]
    
    for query in test_queries:
        results = vector_store.similarity_search(query, k=3)
        memory_manager.track_search_pattern(query, len(results))
    
    # Get memory stats
    stats = memory_manager.get_memory_stats()
    print("Memory Management Statistics:")
    print(f"- Tracked documents: {stats['tracked_documents']}")
    print(f"- Popular topics: {stats['popular_topics']}")
    print(f"- Top search terms: {stats['top_search_terms'][:3]}")
    
    # Test smart system
    smart_system = SmartMemoryRAGSystem(vector_store)
    system_stats = smart_system.get_system_intelligence_stats()
    print(f"\nSystem Intelligence Status:")
    print(f"- Learning active: {system_stats['system_health']['learning_active']}")
    print(f"- Popular topics identified: {system_stats['system_health']['popular_topics_identified']}")