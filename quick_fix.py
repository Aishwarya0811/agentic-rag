#!/usr/bin/env python3
"""
Quick fix script to address the sample generation issue.
This temporarily disables external content fetching for more reliable operation.
"""

import sys
from pathlib import Path

def patch_external_content_retriever():
    """Patch the external content retriever to handle errors gracefully."""
    
    try:
        # Backup the original file
        original_file = Path("external_content_retriever.py")
        backup_file = Path("external_content_retriever.py.backup")
        
        if not backup_file.exists():
            print("📄 Creating backup of external_content_retriever.py...")
            backup_file.write_text(original_file.read_text())
        
        # Read the current content
        content = original_file.read_text()
        
        # Add better error handling to the gather_comprehensive_content method
        old_method = """def gather_comprehensive_content(self, topic: str) -> List[Dict[str, Any]]:
        \"\"\"Gather content from multiple sources for a given topic.\"\"\"
        all_content = []
        
        print(f"Gathering content for topic: {topic}")
        
        # Fetch Wikipedia content
        wiki_content = self.retriever.search_and_fetch_content(topic, num_results=2)
        all_content.extend(wiki_content)
        
        # Fetch mock news articles
        news_content = self.retriever.fetch_news_articles(topic)
        all_content.extend(news_content)
        
        # Fetch mock research papers
        research_content = self.retriever.fetch_research_papers(topic)
        all_content.extend(research_content)
        
        print(f"Gathered {len(all_content)} pieces of content")
        return all_content"""
        
        new_method = """def gather_comprehensive_content(self, topic: str) -> List[Dict[str, Any]]:
        \"\"\"Gather content from multiple sources for a given topic.\"\"\"
        all_content = []
        
        print(f"Gathering content for topic: {topic}")
        
        try:
            # Fetch Wikipedia content (with timeout and error handling)
            print("Fetching Wikipedia content...")
            wiki_content = self.retriever.search_and_fetch_content(topic, num_results=2)
            all_content.extend(wiki_content)
            print(f"Added {len(wiki_content)} Wikipedia articles")
        except Exception as e:
            print(f"Warning: Wikipedia fetch failed: {e}")
        
        try:
            # Fetch mock news articles
            print("Generating mock news articles...")
            news_content = self.retriever.fetch_news_articles(topic)
            all_content.extend(news_content)
            print(f"Added {len(news_content)} news articles")
        except Exception as e:
            print(f"Warning: News article generation failed: {e}")
        
        try:
            # Fetch mock research papers
            print("Generating mock research papers...")
            research_content = self.retriever.fetch_research_papers(topic)
            all_content.extend(research_content)
            print(f"Added {len(research_content)} research papers")
        except Exception as e:
            print(f"Warning: Research paper generation failed: {e}")
        
        print(f"Gathered {len(all_content)} pieces of content total")
        return all_content"""
        
        if old_method in content:
            print("🔧 Patching external content retriever...")
            content = content.replace(old_method, new_method)
            original_file.write_text(content)
            print("✅ Patch applied successfully")
            return True
        else:
            print("⚠️  Method not found or already patched")
            return False
            
    except Exception as e:
        print(f"❌ Patch failed: {e}")
        return False

def patch_rag_retriever():
    """Patch the RAG retriever to be more resilient."""
    
    try:
        # Read the RAG retriever file
        rag_file = Path("rag_retriever.py")
        content = rag_file.read_text()
        
        # Add timeout to external content fetching
        old_fetch = """def _fetch_external_content(self, query: str) -> List[Dict[str, Any]]:
        \"\"\"Fetch external content and add to vector store.\"\"\"
        try:
            # Extract key terms from query for better search
            key_terms = self._extract_key_terms(query)
            
            # Gather external content
            external_content = self.content_aggregator.gather_comprehensive_content(key_terms)"""
        
        new_fetch = """def _fetch_external_content(self, query: str) -> List[Dict[str, Any]]:
        \"\"\"Fetch external content and add to vector store.\"\"\"
        try:
            # Extract key terms from query for better search
            key_terms = self._extract_key_terms(query)
            
            # Add timeout for external content gathering
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("External content fetch timed out")
            
            # Set 10 second timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)
            
            try:
                # Gather external content
                external_content = self.content_aggregator.gather_comprehensive_content(key_terms)
            finally:
                signal.alarm(0)  # Cancel the alarm"""
        
        if old_fetch in content:
            print("🔧 Patching RAG retriever for better timeout handling...")
            content = content.replace(old_fetch, new_fetch)
            rag_file.write_text(content)
            print("✅ RAG retriever patched successfully")
            return True
        else:
            print("⚠️  RAG retriever method not found or already patched")
            return False
            
    except Exception as e:
        print(f"❌ RAG retriever patch failed: {e}")
        return False

def restore_backups():
    """Restore original files from backups."""
    try:
        backup_file = Path("external_content_retriever.py.backup")
        original_file = Path("external_content_retriever.py")
        
        if backup_file.exists():
            print("📄 Restoring external_content_retriever.py from backup...")
            original_file.write_text(backup_file.read_text())
            print("✅ Backup restored")
            return True
        else:
            print("⚠️  No backup found")
            return False
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

def main():
    """Main function to apply patches."""
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        print("🔄 Restoring original files...")
        restore_backups()
        return
    
    print("🔧 Advanced RAG System - Quick Fix")
    print("=" * 50)
    print("This will patch the external content retriever to handle errors more gracefully.")
    print("The original file will be backed up before patching.")
    print()
    
    # Apply patches
    patch1_success = patch_external_content_retriever()
    
    if patch1_success:
        print("\n✅ Patches applied successfully!")
        print("🚀 The system should now be more resilient to external content issues.")
        print("\n💡 To restore original files, run: python quick_fix.py restore")
    else:
        print("\n⚠️  Some patches could not be applied.")
        print("The system may already be patched or the files have changed.")

if __name__ == "__main__":
    main()