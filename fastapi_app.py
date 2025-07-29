#!/usr/bin/env python3
"""
FastAPI backend for the Advanced RAG System.
Serves the RAG system as REST API endpoints and hosts the frontend.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our RAG system components
from agents_rag_system import AgenticRAGSystem
from memory_manager import SmartMemoryRAGSystem
from vector_store import ChromaVectorStore
from sample_data_generator import SampleDataGenerator
from config import Config

# Pydantic models for API requests/responses
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    sources: Optional[List[Dict[str, Any]]] = None

class DocumentUpload(BaseModel):
    title: str
    content: str
    author: str = "API User"
    doc_type: str = "uploaded_document"

class SearchQuery(BaseModel):
    query: str
    k: int = 5
    include_external: bool = True

class SystemStats(BaseModel):
    status: str
    stats: Dict[str, Any]
    timestamp: str

class GenerateSampleRequest(BaseModel):
    topic: str
    num_documents: int = 3

# Initialize FastAPI app
app = FastAPI(
    title="Advanced RAG System API",
    description="A comprehensive Retrieval-Augmented Generation system with OpenAI Agents SDK",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
rag_system: Optional[AgenticRAGSystem] = None
active_connections: List[WebSocket] = []
chat_sessions: Dict[str, List[Dict[str, Any]]] = {}

# Create static and templates directories
static_dir = Path("static")
templates_dir = Path("templates")
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup."""
    global rag_system
    
    try:
        print("🚀 Initializing RAG System...")
        rag_system = AgenticRAGSystem()
        
        if rag_system.initialize(with_sample_data=True, num_sample_docs=15):
            print("✅ RAG System initialized successfully")
            
            # Test stats functionality immediately
            try:
                test_stats = rag_system.get_system_stats()
                if test_stats and test_stats.get("success"):
                    print("✅ Stats system working correctly")
                else:
                    print("⚠️  Stats system may have issues")
                    print(f"   Stats result: {test_stats}")
            except Exception as stats_error:
                print(f"⚠️  Stats system error: {stats_error}")
        else:
            print("⚠️  RAG System initialized with warnings")
    
    except Exception as e:
        print(f"❌ Failed to initialize RAG System: {e}")
        import traceback
        traceback.print_exc()
        # Don't exit, allow manual initialization via API

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Shutting down RAG System...")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Frontend Routes
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon."""
    return {"message": "🤖"}

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Advanced RAG System</title>
        <link rel="stylesheet" href="/static/style.css">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div id="app">
            <!-- Header -->
            <header class="header">
                <div class="container">
                    <h1><i class="fas fa-robot"></i> Advanced RAG System</h1>
                    <p>Retrieval-Augmented Generation with OpenAI Agents SDK</p>
                </div>
            </header>

            <!-- Main Content -->
            <main class="main-content">
                <div class="container">
                    <!-- Sidebar -->
                    <aside class="sidebar">
                        <div class="sidebar-section">
                            <h3><i class="fas fa-chart-bar"></i> System Status</h3>
                            <div id="system-status" class="status-card">
                                <div class="loading">Loading...</div>
                            </div>
                        </div>

                        <div class="sidebar-section">
                            <h3><i class="fas fa-upload"></i> Upload Document</h3>
                            <form id="upload-form" class="upload-form">
                                <input type="text" id="doc-title" placeholder="Document Title" required>
                                <input type="text" id="doc-author" placeholder="Author" value="Web User">
                                <select id="doc-type">
                                    <option value="uploaded_document">Upload</option>
                                    <option value="research_paper">Research Paper</option>
                                    <option value="technical_report">Technical Report</option>
                                    <option value="news_article">News Article</option>
                                    <option value="summary">Summary</option>
                                </select>
                                <textarea id="doc-content" placeholder="Document content..." rows="4" required></textarea>
                                <button type="submit"><i class="fas fa-plus"></i> Add Document</button>
                            </form>
                        </div>

                        <div class="sidebar-section">
                            <h3><i class="fas fa-magic"></i> Generate Sample Data</h3>
                            <form id="sample-form" class="sample-form">
                                <input type="text" id="sample-topic" placeholder="Topic" value="artificial intelligence">
                                <input type="number" id="sample-count" min="1" max="10" value="3">
                                <button type="submit"><i class="fas fa-wand-magic-sparkles"></i> Generate</button>
                            </form>
                        </div>
                    </aside>

                    <!-- Chat Interface -->
                    <section class="chat-section">
                        <div class="chat-header">
                            <h2><i class="fas fa-comments"></i> Chat with RAG Assistant</h2>
                            <button id="clear-chat" class="btn-secondary"><i class="fas fa-trash"></i> Clear</button>
                        </div>
                        
                        <div id="chat-messages" class="chat-messages">
                            <div class="welcome-message">
                                <div class="message assistant-message">
                                    <div class="message-content">
                                        <strong>🤖 RAG Assistant:</strong>
                                        <p>Welcome! I'm your advanced RAG assistant. I can help you:</p>
                                        <ul>
                                            <li>Search and retrieve information from the knowledge base</li>
                                            <li>Answer questions using retrieved context</li>
                                            <li>Provide system statistics and insights</li>
                                            <li>Help manage documents and content</li>
                                        </ul>
                                        <p>Try asking: "Tell me about artificial intelligence" or "Show me system stats"</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <form id="chat-form" class="chat-input-form">
                            <div class="chat-input-group">
                                <input type="text" id="chat-input" placeholder="Ask me anything..." required>
                                <button type="submit" id="send-button">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                        </form>
                    </section>
                </div>
            </main>

            <!-- Footer -->
            <footer class="footer">
                <div class="container">
                    <p>&copy; 2025 Advanced RAG System - Built with FastAPI, OpenAI Agents SDK, and ChromaDB</p>
                </div>
            </footer>
        </div>

        <!-- Loading Overlay -->
        <div id="loading-overlay" class="loading-overlay hidden">
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Processing...</p>
            </div>
        </div>

        <!-- Notification Toast -->
        <div id="toast" class="toast hidden">
            <div class="toast-content">
                <span id="toast-message"></span>
                <button id="toast-close">&times;</button>
            </div>
        </div>

        <script src="/static/script.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "rag_system_initialized": rag_system is not None
    }

@app.get("/api/stats")
async def get_system_stats():
    """Get comprehensive system statistics."""
    try:
        if not rag_system:
            return {
                "status": "error",
                "stats": {
                    "vector_store_stats": {
                        "total_chunks": 0,
                        "unique_topics": 0,
                        "document_types": [],
                        "unique_authors": 0
                    },
                    "external_sources_enabled": False,
                    "reranking_enabled": False
                },
                "timestamp": datetime.now().isoformat(),
                "message": "RAG system not initialized"
            }
        
        # Get stats from the RAG system
        print("Fetching system stats...")
        stats = rag_system.get_system_stats()
        print(f"Raw stats received: {stats}")
        
        # Ensure we have the expected structure
        if stats and stats.get("success"):
            vector_stats = stats.get("stats", {}).get("vector_store_stats", {})
            
            return {
                "status": "success",
                "stats": {
                    "vector_store_stats": {
                        "total_chunks": vector_stats.get("total_chunks", 0),
                        "unique_topics": vector_stats.get("unique_topics", 0),
                        "document_types": vector_stats.get("document_types", []),
                        "unique_authors": vector_stats.get("unique_authors", 0),
                        "sample_topics": vector_stats.get("sample_topics", [])[:10]
                    },
                    "external_sources_enabled": stats.get("stats", {}).get("external_sources_enabled", True),
                    "reranking_enabled": stats.get("stats", {}).get("reranking_enabled", True)
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Fallback with default values
            return {
                "status": "partial",
                "stats": {
                    "vector_store_stats": {
                        "total_chunks": 0,
                        "unique_topics": 0,
                        "document_types": [],
                        "unique_authors": 0
                    },
                    "external_sources_enabled": True,
                    "reranking_enabled": True
                },
                "timestamp": datetime.now().isoformat(),
                "message": "Could not retrieve complete stats"
            }
        
    except Exception as e:
        print(f"Error getting system stats: {e}")
        import traceback
        traceback.print_exc()
        
        # Return error response but don't raise HTTP exception
        return {
            "status": "error",
            "stats": {
                "vector_store_stats": {
                    "total_chunks": 0,
                    "unique_topics": 0,
                    "document_types": [],
                    "unique_authors": 0
                },
                "external_sources_enabled": False,
                "reranking_enabled": False
            },
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_rag(chat_message: ChatMessage):
    """Chat with the RAG system."""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or f"session_{datetime.now().timestamp()}"
        
        # Get response from RAG system
        response = rag_system.chat(chat_message.message)
        
        # Store in chat history
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        chat_sessions[session_id].extend([
            {
                "role": "user",
                "content": chat_message.message,
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().isoformat()
            }
        ])
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            sources=[]  # Could be enhanced to include source documents
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/api/documents")
async def add_document(document: DocumentUpload):
    """Add a new document to the knowledge base."""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        result = rag_system.add_document(
            title=document.title,
            content=document.content,
            author=document.author,
            doc_type=document.doc_type
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"Document '{document.title}' added successfully",
                "chunks_created": result.get("chunks_created", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to add document"))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")

@app.post("/api/documents/upload")
async def upload_file(file: UploadFile = File(...), author: str = Form("File Upload"), doc_type: str = Form("uploaded_document")):
    """Upload a file and add it to the knowledge base."""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Read file content
        content = await file.read()
        
        # Decode content based on file type
        if file.content_type and "text" in file.content_type:
            content_str = content.decode("utf-8")
        else:
            # For non-text files, attempt UTF-8 decoding with error handling
            content_str = content.decode("utf-8", errors="ignore")
        
        # Add to RAG system
        result = rag_system.add_document(
            title=file.filename or "Uploaded File",
            content=content_str,
            author=author,
            doc_type=doc_type
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"File '{file.filename}' uploaded and added successfully",
                "chunks_created": result.get("chunks_created", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to process file"))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@app.post("/api/search")
async def search_knowledge_base(search_query: SearchQuery):
    """Search the knowledge base."""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Use the RAG retriever directly for search
        context_data = rag_system.rag_agent.rag_tools.rag_retriever.retrieve_relevant_context(
            query=search_query.query,
            k=search_query.k,
            include_external=search_query.include_external
        )
        
        return {
            "success": True,
            "query": search_query.query,
            "results": context_data.get("results", []),
            "context_summary": context_data.get("context_summary", ""),
            "total_found": context_data.get("total_results_found", 0),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/generate-sample")
async def generate_sample_data(request: GenerateSampleRequest):
    """Generate sample documents for a topic."""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        print(f"Generating {request.num_documents} sample documents for topic: {request.topic}")
        
        # Generate sample documents
        generator = SampleDataGenerator()
        documents = []
        
        for i in range(request.num_documents):
            try:
                # Generate different types of documents
                doc_types = ['research_paper', 'news_article', 'technical_report', 'summary']
                doc_type = doc_types[i % len(doc_types)]
                
                print(f"Generating {doc_type} {i+1}/{request.num_documents}")
                
                if doc_type == 'research_paper':
                    doc = generator.generate_research_paper(request.topic)
                elif doc_type == 'news_article':
                    doc = generator.generate_news_article(request.topic)
                elif doc_type == 'technical_report':
                    doc = generator.generate_technical_report(request.topic)
                else:
                    doc = generator.generate_summary(request.topic)
                
                print(f"Generated document: {doc['title'][:50]}...")
                
                # Add to RAG system (bypass any external content fetching)
                try:
                    result = rag_system.add_document(
                        title=doc['title'],
                        content=doc['content'],
                        author=doc['author'],
                        doc_type=doc['type']
                    )
                except Exception as add_error:
                    print(f"Error adding document to RAG system: {add_error}")
                    result = {"success": False, "error": str(add_error)}
                
                if result.get("success"):
                    documents.append({
                        "title": doc['title'],
                        "type": doc['type'],
                        "chunks_created": result.get("chunks_created", 0)
                    })
                    print(f"Successfully added document with {result.get('chunks_created', 0)} chunks")
                else:
                    print(f"Failed to add document: {result.get('error', 'Unknown error')}")
                    
            except Exception as doc_error:
                print(f"Error generating document {i+1}: {doc_error}")
                # Continue with other documents
                continue
        
        print(f"Sample generation completed. Successfully created {len(documents)} documents")
        
        return {
            "success": True,
            "message": f"Generated {len(documents)} sample documents about '{request.topic}'",
            "documents": documents,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"Sample generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate sample data: {str(e)}")

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    if session_id not in chat_sessions:
        return {"session_id": session_id, "messages": []}
    
    return {
        "session_id": session_id,
        "messages": chat_sessions[session_id],
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/api/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session."""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    
    return {
        "success": True,
        "message": f"Chat history cleared for session {session_id}",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/initialize")
async def initialize_rag_system():
    """Initialize or reinitialize the RAG system."""
    global rag_system
    
    try:
        print("🔄 Reinitializing RAG System...")
        rag_system = AgenticRAGSystem()
        
        if rag_system.initialize(with_sample_data=True, num_sample_docs=15):
            return {
                "success": True,
                "message": "RAG System initialized successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "message": "RAG System initialized with warnings",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize RAG system: {str(e)}")

# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            session_id = message_data.get("session_id", f"ws_session_{datetime.now().timestamp()}")
            
            if not rag_system:
                await manager.send_personal_message(
                    json.dumps({
                        "error": "RAG system not initialized",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
                continue
            
            try:
                # Get response from RAG system
                response = rag_system.chat(user_message)
                
                # Send response back to client
                await manager.send_personal_message(
                    json.dumps({
                        "response": response,
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "user_message": user_message
                    }),
                    websocket
                )
                
            except Exception as e:
                await manager.send_personal_message(
                    json.dumps({
                        "error": f"Chat failed: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    # Create static and templates directories if they don't exist
    static_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)
    
    # Run the FastAPI server
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )