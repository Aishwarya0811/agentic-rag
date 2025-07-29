import random
from typing import List, Dict
from datetime import datetime, timedelta

class SampleDataGenerator:
    """Generates sample text data for RAG system demonstration."""
    
    TOPICS = [
        "artificial intelligence", "machine learning", "climate change", 
        "renewable energy", "space exploration", "quantum computing",
        "biotechnology", "cybersecurity", "blockchain", "robotics",
        "sustainable development", "ocean conservation", "urban planning",
        "healthcare innovation", "education technology", "clean transportation"
    ]
    
    DOCUMENT_TYPES = ["research_paper", "news_article", "technical_report", "summary"]
    
    def __init__(self):
        self.fake_authors = [
            "Dr. Sarah Chen", "Prof. Michael Rodriguez", "Dr. Emily Thompson",
            "Prof. David Kim", "Dr. Lisa Wang", "Prof. James Wilson",
            "Dr. Maria Garcia", "Prof. Robert Taylor", "Dr. Jennifer Lee",
            "Prof. Christopher Brown"
        ]
    
    def generate_research_paper(self, topic: str) -> Dict[str, str]:
        """Generate a mock research paper."""
        title = f"Advanced {topic.title()} Research: Novel Approaches and Applications"
        author = random.choice(self.fake_authors)
        date = self._random_date()
        
        content = f"""
        Abstract: This paper presents a comprehensive analysis of {topic} methodologies and their practical applications.
        Our research demonstrates significant improvements in {topic} systems through innovative approaches.
        
        Introduction: {topic.title()} has become increasingly important in modern technology solutions.
        This study examines the current state of {topic} research and identifies key areas for improvement.
        
        Methodology: We employed a mixed-methods approach combining quantitative analysis with qualitative evaluation.
        Our experimental setup included {random.randint(50, 500)} test cases across multiple scenarios.
        
        Results: Our findings indicate a {random.randint(15, 45)}% improvement in performance metrics
        compared to baseline approaches. Statistical significance was achieved with p < 0.01.
        
        Discussion: The implications of these results extend beyond traditional {topic} applications.
        We observe potential for integration with emerging technologies and cross-disciplinary collaboration.
        
        Conclusion: This research contributes to the advancing field of {topic} by providing
        evidence-based insights and practical implementation strategies.
        """
        
        return {
            "id": f"paper_{random.randint(1000, 9999)}",
            "type": "research_paper",
            "title": title,
            "author": author,
            "date": date,
            "topic": topic,
            "content": content.strip()
        }
    
    def generate_news_article(self, topic: str) -> Dict[str, str]:
        """Generate a mock news article."""
        headlines = [
            f"Breakthrough in {topic.title()} Promises Revolutionary Changes",
            f"New {topic.title()} Initiative Launches Global Collaboration",
            f"Scientists Achieve Major Milestone in {topic.title()} Research",
            f"Industry Leaders Discuss Future of {topic.title()}"
        ]
        
        title = random.choice(headlines)
        date = self._random_date(days_back=30)
        
        content = f"""
        In a significant development for the {topic} sector, researchers have announced
        groundbreaking progress that could reshape industry standards.
        
        The latest findings suggest that {topic} technologies are advancing more rapidly
        than previously anticipated, with practical applications expected within the next
        {random.randint(2, 8)} years.
        
        Key stakeholders emphasize the importance of sustainable development and ethical
        considerations in {topic} implementation. "This represents a paradigm shift
        in how we approach {topic} challenges," said lead researcher Dr. {random.choice(self.fake_authors.split()[1:])}.
        
        The research team plans to publish detailed findings in upcoming academic journals
        and present results at international conferences focused on {topic} innovation.
        
        Industry experts predict significant economic impact, with market analysts
        projecting growth rates of {random.randint(10, 40)}% annually over the next five years.
        """
        
        return {
            "id": f"article_{random.randint(1000, 9999)}",
            "type": "news_article",
            "title": title,
            "author": "Staff Reporter",
            "date": date,
            "topic": topic,
            "content": content.strip()
        }
    
    def generate_technical_report(self, topic: str) -> Dict[str, str]:
        """Generate a mock technical report."""
        title = f"Technical Analysis of {topic.title()} Systems and Implementation Strategies"
        author = random.choice(self.fake_authors)
        date = self._random_date(days_back=90)
        
        content = f"""
        Executive Summary: This technical report evaluates current {topic} systems
        and provides recommendations for optimization and scalability improvements.
        
        System Architecture: The analyzed {topic} framework consists of multiple
        interconnected components designed for high performance and reliability.
        Key components include data processing modules, analysis engines, and user interfaces.
        
        Performance Metrics: Benchmark testing reveals {random.randint(85, 98)}% system uptime
        with average response times of {random.randint(10, 100)}ms under normal load conditions.
        
        Technical Specifications:
        - Processing capacity: {random.randint(1000, 10000)} operations per second
        - Memory utilization: {random.randint(60, 85)}% average
        - Storage requirements: {random.randint(10, 100)}GB baseline configuration
        
        Implementation Challenges: Primary obstacles include system integration complexity,
        scalability limitations, and resource optimization requirements.
        
        Recommendations: We propose a phased implementation approach with emphasis on
        modular design principles and comprehensive testing protocols.
        
        Future Considerations: Emerging trends in {topic} suggest potential for
        enhanced automation and improved user experience through advanced interfaces.
        """
        
        return {
            "id": f"report_{random.randint(1000, 9999)}",
            "type": "technical_report",
            "title": title,
            "author": author,
            "date": date,
            "topic": topic,
            "content": content.strip()
        }
    
    def generate_summary(self, topic: str) -> Dict[str, str]:
        """Generate a mock summary document."""
        title = f"{topic.title()}: Key Insights and Future Directions"
        date = self._random_date(days_back=60)
        
        content = f"""
        Overview: This summary compiles essential information about {topic}
        developments, current research trends, and practical applications.
        
        Key Points:
        • {topic.title()} technology continues to evolve rapidly with new applications emerging regularly
        • Research indicates strong potential for cross-industry adoption and integration
        • Current challenges focus on scalability, efficiency, and ethical implementation
        • Collaborative efforts between academia and industry are accelerating progress
        
        Recent Developments: Notable advances include improved algorithms,
        enhanced processing capabilities, and expanded application domains.
        
        Market Impact: The {topic} sector shows consistent growth with increasing
        investment from both public and private sectors.
        
        Research Priorities: Future work should emphasize sustainability,
        accessibility, and long-term societal benefits.
        
        Conclusion: {topic.title()} represents a critical area for continued
        innovation and strategic development across multiple industries.
        """
        
        return {
            "id": f"summary_{random.randint(1000, 9999)}",
            "type": "summary",
            "title": title,
            "author": "Research Team",
            "date": date,
            "topic": topic,
            "content": content.strip()
        }
    
    def generate_sample_documents(self, count: int = 20) -> List[Dict[str, str]]:
        """Generate a collection of sample documents."""
        documents = []
        
        for _ in range(count):
            topic = random.choice(self.TOPICS)
            doc_type = random.choice(self.DOCUMENT_TYPES)
            
            if doc_type == "research_paper":
                doc = self.generate_research_paper(topic)
            elif doc_type == "news_article":
                doc = self.generate_news_article(topic)
            elif doc_type == "technical_report":
                doc = self.generate_technical_report(topic)
            else:  # summary
                doc = self.generate_summary(topic)
            
            documents.append(doc)
        
        return documents
    
    def _random_date(self, days_back: int = 365) -> str:
        """Generate a random date within the specified range."""
        start_date = datetime.now() - timedelta(days=days_back)
        random_days = random.randint(0, days_back)
        random_date = start_date + timedelta(days=random_days)
        return random_date.strftime("%Y-%m-%d")

if __name__ == "__main__":
    generator = SampleDataGenerator()
    docs = generator.generate_sample_documents(5)
    
    for doc in docs:
        print(f"Title: {doc['title']}")
        print(f"Type: {doc['type']}")
        print(f"Topic: {doc['topic']}")
        print("=" * 50)