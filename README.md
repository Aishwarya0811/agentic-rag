# Advanced RAG System with OpenAI Agents SDK

A comprehensive Retrieval-Augmented Generation (RAG) system built with OpenAI's Agents SDK, featuring intelligent document retrieval, semantic search, automatic memory management, and a modern web interface powered by FastAPI.

![1753794145376](image/README/1753794145376.png)

## Features

### Core RAG Capabilities

- **Advanced Document Embedding**: Using OpenAI's `text-embedding-3-small` model
- **Semantic Search**: ChromaDB-powered vector similarity search with advanced ranking
- **Contextual Prompt Generation**: Intelligent context assembly for LLM queries
- **Multi-source Retrieval**: Combines local knowledge base with external content

### OpenAI Agents SDK Integration

- **Agent-based Architecture**: Modular design using OpenAI Agents SDK
- **Tool Integration**: RAG-specific tools for document management and search
- **Conversational Interface**: Natural language interaction with the knowledge base

### Intelligent Memory Management

- **Automatic Updates**: Background content refresh based on usage patterns
- **Search Pattern Learning**: Identifies popular topics for proactive updates
- **Document Change Tracking**: Checksums and versioning for efficient updates
- **Cleanup & Optimization**: Removes outdated content and optimizes storage

### External Content Integration

- **Wikipedia Integration**: Automatic Wikipedia article retrieval
- **Web Scraping**: Abstract web content extraction capabilities
- **Mock API Integration**: Simulated news and research paper fetching
- **Content Aggregation**: Multi-source content compilation

### Web Interface

- **FastAPI Backend**: High-performance REST API with automatic documentation
- **Modern Frontend**: Responsive HTML/CSS/JS interface with real-time features
- **WebSocket Chat**: Real-time conversation with the RAG assistant
- **Document Upload**: Support for multiple file formats via web interface
- **System Analytics**: Live system statistics and health monitoring
- **REST API**: Complete API endpoints for integration with other systems
- **Legacy Streamlit App**: Alternative interface for advanced features

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Aishwarya0811/agentic-rag
   cd agentic-rag
   ```
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables**:
   Create a `.env` file based on `.env.example`:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. **Run the FastAPI application**:

   ```bash
   python fastapi_app.py
   ```
5. **Access the application**:

   - **Web Interface**: `http://localhost:8000`
   - **API Documentation**: `http://localhost:8000/api/docs`
   - **Alternative Streamlit UI**: `streamlit run streamlit_app.py` → `http://localhost:8501`

## System Components

### 1. FastAPI Backend (`fastapi_app.py`)

- **REST API Endpoints**: Complete CRUD operations for documents and chat
- **WebSocket Support**: Real-time bidirectional communication for chat
- **Automatic Documentation**: Interactive API docs at `/api/docs`
- **Static File Serving**: Hosts the modern frontend interface
- **CORS Support**: Cross-origin requests for API integration

### 2. Frontend Interface (`static/`)

- **Modern Design**: Responsive CSS with custom styling and animations
- **Real-time Chat**: WebSocket-powered chat with fallback to REST API
- **Document Management**: Upload and manage documents via web interface
- **System Monitoring**: Live statistics and health monitoring
- **Progressive Enhancement**: Works with and without JavaScript

### 3. Vector Store (`vector_store.py`)

- **ChromaDB Integration**: Persistent vector storage
- **Embedding Generation**: OpenAI embedding model integration
- **Document Chunking**: Intelligent text segmentation with overlap
- **Similarity Search**: Advanced semantic search with scoring

### 2. RAG Retriever (`rag_retriever.py`)

- **Query Enhancement**: LLM-powered query expansion
- **Multi-source Retrieval**: Local + external content aggregation
- **Result Reranking**: Advanced relevance scoring
- **Context Generation**: Intelligent prompt assembly

### 3. Agents System (`agents_rag_system.py`)

- **Agent Architecture**: OpenAI Agents SDK implementation
- **Tool Integration**: RAG-specific tools and functions
- **Conversation Management**: Stateful chat interactions
- **System Orchestration**: Coordinates all components

### 4. Memory Manager (`memory_manager.py`)

- **Pattern Learning**: Identifies popular search topics
- **Automatic Updates**: Background content refresh
- **Change Detection**: Document versioning and checksums
- **Cleanup Operations**: Removes outdated content

### 5. External Content (`external_content_retriever.py`)

- **Wikipedia API**: Automatic article fetching
- **Web Scraping**: Generic web content extraction
- **Content Simulation**: Mock news/research paper generation
- **Multi-source Aggregation**: Combines various content sources

## Usage Examples

### FastAPI Web Interface

1. **Start the server**: `python fastapi_app.py`
2. **Open browser**: Go to `http://localhost:8000`
3. **Chat with the assistant**: Use the web interface to ask questions
4. **Upload documents**: Add your own content via the upload form
5. **Generate sample data**: Create demo content for testing

### REST API Usage

```bash
# Health check
curl http://localhost:8000/api/health

# Chat with the system
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Tell me about artificial intelligence"}'

# Add a document
curl -X POST "http://localhost:8000/api/documents" \
     -H "Content-Type: application/json" \
     -d '{"title": "My Document", "content": "Document content here", "author": "Me"}'

# Search the knowledge base
curl -X POST "http://localhost:8000/api/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "artificial intelligence", "k": 5}'
```

### Python API Usage

```python
# Initialize the system
system = AgenticRAGSystem()
system.initialize()

# Ask questions
response = system.chat("Tell me about artificial intelligence")
print(response)
```

### Direct API Usage

```python
from rag_retriever import AdvancedRAGRetriever

# Initialize retriever
retriever = AdvancedRAGRetriever()

# Search for relevant context
context = retriever.retrieve_relevant_context(
    query="machine learning applications",
    k=5,
    include_external=True
)

# Generate contextual prompt
prompt = retriever.generate_contextual_prompt(
    "Explain machine learning", 
    context
)
```

### Document Management

```python
# Add a document
document = {
    'id': 'doc_001',
    'title': 'AI Research Paper',
    'content': 'Content here...',
    'author': 'Dr. Smith',
    'type': 'research_paper'
}

system.add_document(
    title=document['title'],
    content=document['content'],
    author=document['author'],
    doc_type=document['type']
)
```

## Configuration

Key configuration options in `config.py`:

```python
class Config:
    # OpenAI Settings
    OPENAI_API_KEY = "your-api-key"
    EMBEDDING_MODEL = "text-embedding-3-small"
    LLM_MODEL = "gpt-4o-mini"
  
    # Vector Store Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 5
  
    # Paths
    CHROMA_DB_PATH = "./chroma_db"
```

## Features Overview

### Streamlit Web Interface

- **Chat Tab**: Interactive conversation interface
- **Upload Tab**: Document upload and management
- **Analytics Tab**: System statistics and metrics
- **Settings Tab**: Advanced configuration options

### Advanced RAG Features

- **Query Enhancement**: Automatic query expansion for better retrieval
- **Multi-modal Retrieval**: Combines vector similarity with keyword matching
- **Context Ranking**: Intelligent relevance scoring and reranking
- **External Content**: Dynamic external source integration

### Memory Management

- **Usage Learning**: Identifies frequently searched topics
- **Proactive Updates**: Refreshes popular content automatically
- **Storage Optimization**: Removes duplicates and outdated content
- **Background Processing**: Non-blocking update operations

## Testing

Run the system tests:

```bash
# Test individual components
python vector_store.py
python rag_retriever.py
python agents_rag_system.py
python memory_manager.py
```

### Sample Queries to Test

- "What are the latest developments in artificial intelligence?"
- "Explain quantum computing applications"
- "Tell me about climate change research"
- "Show me system statistics"

## Advanced Features

### Automatic Memory Updates

The system includes intelligent memory management that:

- Tracks search patterns to identify popular topics
- Automatically refreshes content for frequently queried subjects
- Removes outdated documents based on age and relevance
- Optimizes vector store performance through cleanup operations

### External Content Integration

Demonstrates how to integrate external sources:

- Wikipedia API integration for real-time content
- Web scraping capabilities for general content
- Mock API simulations for news and research papers
- Content aggregation from multiple sources

### Agent-based Architecture

Built on OpenAI Agents SDK principles:

- Modular tool design for extensibility
- Conversational memory and context management
- Intelligent routing between different capabilities
- Structured response generation

## Monitoring & Analytics

The system provides comprehensive monitoring:

- **Vector Store Statistics**: Document counts, topics, types
- **Search Analytics**: Popular queries and patterns
- **Performance Metrics**: Response times and accuracy
- **System Health**: Component status and diagnostics

## API Endpoints

The FastAPI backend provides the following REST API endpoints:

### Core Endpoints

- `GET /` - Serve the main web interface
- `GET /api/health` - System health check
- `GET /api/stats` - Get comprehensive system statistics
- `POST /api/initialize` - Initialize or reinitialize the RAG system

### Chat & Search

- `POST /api/chat` - Chat with the RAG assistant
- `POST /api/search` - Search the knowledge base
- `GET /api/chat/history/{session_id}` - Get chat history
- `DELETE /api/chat/history/{session_id}` - Clear chat history

### Document Management

- `POST /api/documents` - Add a new document
- `POST /api/documents/upload` - Upload file and add to knowledge base
- `POST /api/generate-sample` - Generate sample documents

### WebSocket

- `WS /ws/chat` - Real-time chat via WebSocket

### API Documentation

- `GET /api/docs` - Interactive Swagger documentation
- `GET /api/redoc` - ReDoc documentation

### Example API Responses

```json
// GET /api/health
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "rag_system_initialized": true
}

// POST /api/chat
{
  "response": "AI is a broad field of computer science...",
  "session_id": "session_123",
  "timestamp": "2024-01-01T12:00:00Z",
  "sources": []
}

// GET /api/stats
{
  "status": "success",
  "stats": {
    "vector_store_stats": {
      "total_chunks": 150,
      "unique_topics": 12,
      "document_types": ["research_paper", "news_article"]
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Deployment

### Local Development

```bash
# FastAPI server (recommended)
python fastapi_app.py

# Alternative: Streamlit interface
streamlit run streamlit_app.py --server.port 8501
```

### Production Deployment

For production deployment, consider:

#### FastAPI Production Setup

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn fastapi_app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with Uvicorn
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Production Considerations

- **Environment Variables**: Secure API key storage with proper env management
- **Authentication**: Implement user authentication and authorization
- **HTTPS**: Use reverse proxy (nginx) with SSL certificates
- **Monitoring**: Set up logging, metrics, and health checks
- **Scaling**: Use load balancers and multiple instances
- **Database**: Consider persistent vector store solutions for larger datasets
- **Caching**: Implement Redis caching for improved performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
