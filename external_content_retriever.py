import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import re
from urllib.parse import urljoin, urlparse
import time
import random
from datetime import datetime

class ExternalContentRetriever:
    """Tools for fetching and processing external content from web sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def fetch_wikipedia_article(self, title: str) -> Optional[Dict[str, Any]]:
        """Fetch a Wikipedia article by title."""
        try:
            # Use Wikipedia API
            api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + title.replace(" ", "_")
            
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'extract' in data:
                # Get full content using another API endpoint
                content_url = f"https://en.wikipedia.org/w/api.php"
                params = {
                    'action': 'query',
                    'format': 'json',
                    'titles': title,
                    'prop': 'extracts',
                    'exintro': False,
                    'explaintext': True,
                    'exsectionformat': 'plain'
                }
                
                content_response = self.session.get(content_url, params=params, timeout=10)
                content_data = content_response.json()
                
                pages = content_data.get('query', {}).get('pages', {})
                page_id = next(iter(pages.keys()))
                full_content = pages[page_id].get('extract', '')
                
                return {
                    'id': f"wiki_{title.replace(' ', '_').lower()}",
                    'type': 'wikipedia_article',
                    'title': data.get('title', title),
                    'author': 'Wikipedia Contributors',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'topic': self._extract_topic_from_content(full_content),
                    'content': full_content,
                    'source_url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'summary': data.get('extract', '')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching Wikipedia article '{title}': {e}")
            return None
    
    def fetch_web_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch and extract text content from a web page."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside", "header"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else urlparse(url).netloc
            
            # Extract main content
            # Try common content selectors
            content_selectors = [
                'main', 'article', '[role="main"]', '.content', '#content',
                '.post-content', '.entry-content', '.article-content'
            ]
            
            content_element = None
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content_element = element
                    break
            
            # If no specific content area found, use body
            if not content_element:
                content_element = soup.find('body')
            
            if content_element:
                # Extract text content
                text_content = content_element.get_text(separator=' ', strip=True)
                
                # Clean up the text
                text_content = re.sub(r'\s+', ' ', text_content)
                text_content = re.sub(r'\n+', '\n', text_content)
                
                # Extract meta description if available
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ''
                
                return {
                    'id': f"web_{hash(url)}",
                    'type': 'web_page',
                    'title': title_text,
                    'author': urlparse(url).netloc,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'topic': self._extract_topic_from_content(text_content),
                    'content': text_content,
                    'source_url': url,
                    'summary': description
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching web page '{url}': {e}")
            return None
    
    def search_and_fetch_content(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Search for content and fetch multiple sources."""
        results = []
        
        # Try to fetch Wikipedia articles for the query
        wiki_result = self.fetch_wikipedia_article(query)
        if wiki_result:
            results.append(wiki_result)
        
        # Generate some related Wikipedia searches
        related_terms = self._generate_related_terms(query)
        
        for term in related_terms[:num_results-1]:
            time.sleep(1)  # Rate limiting
            wiki_result = self.fetch_wikipedia_article(term)
            if wiki_result:
                results.append(wiki_result)
        
        return results
    
    def fetch_news_articles(self, topic: str) -> List[Dict[str, Any]]:
        """Simulate fetching news articles about a topic."""
        # This is a mock implementation since real news APIs require keys
        # In a real implementation, you would use NewsAPI, Google News API, etc.
        
        mock_articles = []
        
        news_sources = [
            "TechCrunch", "BBC News", "Reuters", "The Guardian", 
            "Scientific American", "Nature News", "Wired"
        ]
        
        for i in range(3):
            article = {
                'id': f"news_{topic.replace(' ', '_')}_{i}",
                'type': 'news_article',
                'title': f"Latest Developments in {topic.title()}: Breaking Analysis",
                'author': f"{random.choice(news_sources)} Reporter",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'topic': topic,
                'content': self._generate_mock_news_content(topic),
                'source_url': f"https://example-news.com/{topic.replace(' ', '-')}-{i}",
                'summary': f"Recent developments and analysis in {topic} sector."
            }
            mock_articles.append(article)
        
        return mock_articles
    
    def fetch_research_papers(self, topic: str) -> List[Dict[str, Any]]:
        """Simulate fetching research papers about a topic."""
        # This would integrate with arXiv API, PubMed, or similar in a real implementation
        
        mock_papers = []
        
        authors = [
            "Dr. Smith et al.", "Prof. Johnson & Team", "Research Consortium",
            "Dr. Zhang et al.", "Academic Research Group"
        ]
        
        for i in range(2):
            paper = {
                'id': f"paper_{topic.replace(' ', '_')}_{i}",
                'type': 'research_paper',
                'title': f"Advances in {topic.title()}: A Comprehensive Study",
                'author': random.choice(authors),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'topic': topic,
                'content': self._generate_mock_research_content(topic),
                'source_url': f"https://arxiv.org/abs/2024.{random.randint(1000, 9999)}",
                'summary': f"Comprehensive research analysis of {topic} methodologies and applications."
            }
            mock_papers.append(paper)
        
        return mock_papers
    
    def _extract_topic_from_content(self, content: str) -> str:
        """Extract the main topic from content using simple heuristics."""
        # Simple topic extraction - in a real system, you might use NLP
        common_topics = [
            'artificial intelligence', 'machine learning', 'climate change',
            'renewable energy', 'space exploration', 'quantum computing',
            'biotechnology', 'cybersecurity', 'blockchain', 'robotics'
        ]
        
        content_lower = content.lower()
        
        for topic in common_topics:
            if topic in content_lower:
                return topic
        
        # Extract potential topics from first paragraph
        first_paragraph = content.split('\n')[0][:500]
        words = re.findall(r'\b[a-z]+\b', first_paragraph.lower())
        
        # Simple frequency-based topic extraction
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        if word_freq:
            most_common = max(word_freq.items(), key=lambda x: x[1])
            return most_common[0]
        
        return 'general'
    
    def _generate_related_terms(self, query: str) -> List[str]:
        """Generate related search terms for a query."""
        base_terms = query.split()
        
        related_terms = []
        
        # Add variations and related concepts
        if 'artificial intelligence' in query.lower() or 'ai' in query.lower():
            related_terms.extend(['machine learning', 'deep learning', 'neural networks'])
        elif 'climate' in query.lower():
            related_terms.extend(['global warming', 'renewable energy', 'sustainability'])
        elif 'space' in query.lower():
            related_terms.extend(['astronomy', 'astrophysics', 'space exploration'])
        elif 'quantum' in query.lower():
            related_terms.extend(['quantum physics', 'quantum mechanics', 'quantum computing'])
        else:
            # Generic related terms
            related_terms = [f"{query} research", f"{query} technology", f"{query} applications"]
        
        return related_terms[:3]
    
    def _generate_mock_news_content(self, topic: str) -> str:
        """Generate mock news content for demonstration."""
        return f"""
        In a significant development for the {topic} industry, leading experts have announced 
        breakthrough findings that could reshape current understanding and applications.
        
        The research, conducted over the past {random.randint(6, 18)} months, reveals new 
        insights into {topic} systems and their potential for widespread adoption across 
        multiple sectors.
        
        "These findings represent a paradigm shift in how we approach {topic} challenges," 
        said lead researcher Dr. Anderson. "The implications extend far beyond current 
        applications and open up entirely new possibilities."
        
        Industry analysts predict that these developments could lead to significant market 
        changes, with projected growth rates of {random.randint(15, 40)}% over the next 
        three years.
        
        The research team plans to publish detailed findings in upcoming peer-reviewed 
        journals and present results at international conferences focused on {topic} innovation.
        
        Regulatory bodies are closely monitoring these developments to ensure appropriate 
        guidelines are established for safe and ethical implementation.
        """
    
    def _generate_mock_research_content(self, topic: str) -> str:
        """Generate mock research content for demonstration."""
        return f"""
        Abstract: This study presents a comprehensive analysis of {topic} methodologies 
        and their practical applications in modern technological frameworks.
        
        Introduction: Recent advances in {topic} have created new opportunities for 
        innovation across multiple disciplines. This research investigates the current 
        state of {topic} technology and identifies key areas for future development.
        
        Methodology: We employed a multi-faceted approach combining theoretical analysis 
        with empirical validation. Our experimental framework included {random.randint(100, 500)} 
        test cases across diverse scenarios.
        
        Results: Our findings demonstrate significant improvements in performance metrics, 
        with efficiency gains of {random.randint(20, 50)}% compared to baseline approaches. 
        Statistical analysis confirms the significance of these improvements (p < 0.001).
        
        Discussion: The implications of these results extend beyond traditional {topic} 
        applications. We observe potential for cross-disciplinary integration and novel 
        application domains.
        
        Conclusion: This research contributes to the advancing field of {topic} by providing 
        evidence-based insights and practical implementation strategies for future development.
        
        Keywords: {topic}, innovation, technology, research, applications
        """

class ContentAggregator:
    """Aggregates content from multiple external sources."""
    
    def __init__(self):
        self.retriever = ExternalContentRetriever()
    
    def gather_comprehensive_content(self, topic: str) -> List[Dict[str, Any]]:
        """Gather content from multiple sources for a given topic."""
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
        return all_content

if __name__ == "__main__":
    # Test the content retriever
    retriever = ExternalContentRetriever()
    
    # Test Wikipedia fetch
    wiki_result = retriever.fetch_wikipedia_article("artificial intelligence")
    if wiki_result:
        print(f"Fetched Wikipedia article: {wiki_result['title']}")
        print(f"Content length: {len(wiki_result['content'])} characters")
    
    # Test content aggregation
    aggregator = ContentAggregator()
    content = aggregator.gather_comprehensive_content("machine learning")
    
    print(f"\nAggregated {len(content)} pieces of content:")
    for item in content:
        print(f"- {item['type']}: {item['title']}")