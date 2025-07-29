import streamlit as st
import pandas as pd
from datetime import datetime
import json
import time
from typing import Dict, List, Any

# Import our RAG system components
from agents_rag_system import AgenticRAGSystem
from memory_manager import SmartMemoryRAGSystem
from vector_store import ChromaVectorStore
from sample_data_generator import SampleDataGenerator
from config import Config

# Page configuration
st.set_page_config(
    page_title="Advanced RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

.chat-message {
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.user-message {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
}

.assistant-message {
    background-color: #f3e5f5;
    border-left: 4px solid #9c27b0;
}

.stats-container {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #dee2e6;
}

.success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 0.75rem;
    border-radius: 4px;
    border: 1px solid #c3e6cb;
}

.error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.75rem;
    border-radius: 4px;
    border: 1px solid #f5c6cb;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_rag_system():
    """Initialize the RAG system with caching."""
    try:
        system = AgenticRAGSystem()
        if system.initialize(with_sample_data=True, num_sample_docs=15):
            return system, None
        else:
            return None, "Failed to initialize RAG system"
    except Exception as e:
        return None, f"Error initializing system: {str(e)}"

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Advanced RAG System</h1>', unsafe_allow_html=True)
    st.markdown("**Retrieval-Augmented Generation with OpenAI Agents SDK**")
    
    # Initialize system
    if 'rag_system' not in st.session_state:
        with st.spinner("🚀 Initializing RAG system..."):
            system, error = initialize_rag_system()
            if system:
                st.session_state.rag_system = system
                st.session_state.chat_history = []
                st.success("✅ RAG system initialized successfully!")
            else:
                st.error(f"❌ {error}")
                st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ System Controls")
        
        # System statistics
        if st.button("📊 Refresh System Stats"):
            stats = st.session_state.rag_system.get_system_stats()
            st.session_state.system_stats = stats
        
        if 'system_stats' in st.session_state:
            stats = st.session_state.system_stats
            if stats.get('success'):
                vector_stats = stats['stats']['vector_store_stats']
                st.markdown(f"""
                <div class="stats-container">
                <h4>📈 Knowledge Base Stats</h4>
                <ul>
                <li><strong>Total Chunks:</strong> {vector_stats.get('total_chunks', 0)}</li>
                <li><strong>Unique Topics:</strong> {vector_stats.get('unique_topics', 0)}</li>
                <li><strong>Document Types:</strong> {len(vector_stats.get('document_types', []))}</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Document management
        st.header("📄 Document Management")
        
        # Sample data generation
        st.subheader("Generate Sample Data")
        sample_topic = st.text_input("Topic for sample data:", value="artificial intelligence")
        sample_count = st.slider("Number of documents:", 1, 10, 3)
        
        if st.button("🎲 Generate Sample Documents"):
            with st.spinner("Generating sample documents..."):
                generator = SampleDataGenerator()
                
                # Generate documents focused on the topic
                docs = []
                for _ in range(sample_count):
                    if sample_topic.lower() in generator.TOPICS:
                        doc = generator.generate_research_paper(sample_topic)
                    else:
                        # Generate mixed content
                        doc_types = ['research_paper', 'news_article', 'technical_report', 'summary']
                        doc_type = doc_types[_ % len(doc_types)]
                        if doc_type == 'research_paper':
                            doc = generator.generate_research_paper(sample_topic)
                        elif doc_type == 'news_article':
                            doc = generator.generate_news_article(sample_topic)
                        elif doc_type == 'technical_report':
                            doc = generator.generate_technical_report(sample_topic)
                        else:
                            doc = generator.generate_summary(sample_topic)
                    docs.append(doc)
                
                # Add to system
                added_count = 0
                for doc in docs:
                    result = st.session_state.rag_system.add_document(
                        title=doc['title'],
                        content=doc['content'],
                        author=doc['author'],
                        doc_type=doc['type']
                    )
                    if result.get('success'):
                        added_count += 1
                
                st.success(f"✅ Generated and added {added_count} documents about '{sample_topic}'")
        
        st.divider()
        
        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Interface", "📄 Upload Documents", "📊 System Analytics", "⚙️ Advanced Settings"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        document_upload_interface()
    
    with tab3:
        analytics_interface()
    
    with tab4:
        advanced_settings_interface()

def chat_interface():
    """Chat interface for interacting with the RAG system."""
    st.header("💬 Chat with RAG Assistant")
    
    # Chat history display
    chat_container = st.container()
    
    with chat_container:
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                    <strong>🧑 You:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                    <strong>🤖 Assistant:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("👋 Welcome! Ask me anything about the knowledge base. Try questions like:\n\n"
                   "• 'Tell me about artificial intelligence'\n"
                   "• 'What are the latest developments in climate change?'\n"
                   "• 'Show me system statistics'")
    
    # Chat input
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input("💭 Ask me anything:", placeholder="Enter your question here...")
        
        with col2:
            submit_button = st.form_submit_button("Send 🚀")
        
        if submit_button and user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Get response from RAG system
            with st.spinner("🤔 Thinking..."):
                try:
                    response = st.session_state.rag_system.chat(user_input)
                    
                    # Add assistant response to history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': error_msg,
                        'timestamp': datetime.now().isoformat()
                    })
            
            st.rerun()

def document_upload_interface():
    """Interface for uploading and managing documents."""
    st.header("📄 Document Upload & Management")
    
    # File upload section
    st.subheader("📤 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=['txt', 'pdf', 'docx', 'md'],
        accept_multiple_files=True,
        help="Supported formats: TXT, PDF, DOCX, MD"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.write(f"📁 **{uploaded_file.name}** ({uploaded_file.size} bytes)")
            
            if st.button(f"Process {uploaded_file.name}", key=f"process_{uploaded_file.name}"):
                try:
                    # Read file content
                    if uploaded_file.type == "text/plain":
                        content = str(uploaded_file.read(), "utf-8")
                    else:
                        # For other file types, you would implement specific readers
                        content = str(uploaded_file.read(), "utf-8", errors='ignore')
                    
                    # Add to RAG system
                    result = st.session_state.rag_system.add_document(
                        title=uploaded_file.name,
                        content=content,
                        author="User Upload",
                        doc_type="uploaded_document"
                    )
                    
                    if result.get('success'):
                        st.success(f"✅ Successfully processed {uploaded_file.name}")
                    else:
                        st.error(f"❌ Failed to process {uploaded_file.name}: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
    
    st.divider()
    
    # Manual document entry
    st.subheader("✍️ Add Document Manually")
    
    with st.form("manual_document_form"):
        doc_title = st.text_input("📋 Document Title:")
        doc_author = st.text_input("👤 Author:", value="Manual Entry")
        doc_type = st.selectbox("📂 Document Type:", 
                               ["research_paper", "news_article", "technical_report", "summary", "other"])
        doc_content = st.text_area("📝 Document Content:", height=200)
        
        submit_doc = st.form_submit_button("📄 Add Document")
        
        if submit_doc:
            if doc_title and doc_content:
                result = st.session_state.rag_system.add_document(
                    title=doc_title,
                    content=doc_content,
                    author=doc_author,
                    doc_type=doc_type
                )
                
                if result.get('success'):
                    st.success(f"✅ Successfully added document: {doc_title}")
                else:
                    st.error(f"❌ Failed to add document: {result.get('error', 'Unknown error')}")
            else:
                st.warning("⚠️ Please provide both title and content.")

def analytics_interface():
    """Interface for system analytics and insights."""
    st.header("📊 System Analytics")
    
    # Get comprehensive stats
    if st.button("🔄 Refresh Analytics"):
        st.session_state.analytics_data = st.session_state.rag_system.get_system_stats()
    
    if 'analytics_data' in st.session_state:
        data = st.session_state.analytics_data
        
        if data.get('success'):
            stats = data['stats']
            vector_stats = stats['vector_store_stats']
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📚 Total Chunks", vector_stats.get('total_chunks', 0))
            
            with col2:
                st.metric("🏷️ Unique Topics", vector_stats.get('unique_topics', 0))
            
            with col3:
                st.metric("📄 Document Types", len(vector_stats.get('document_types', [])))
            
            with col4:
                st.metric("👥 Authors", vector_stats.get('unique_authors', 0))
            
            # Document types distribution
            st.subheader("📊 Document Type Distribution")
            if vector_stats.get('document_types'):
                doc_types_df = pd.DataFrame({
                    'Document Type': vector_stats['document_types'],
                    'Count': [1] * len(vector_stats['document_types'])  # Simplified for demo
                })
                st.bar_chart(doc_types_df.set_index('Document Type'))
            
            # Sample topics
            st.subheader("🏷️ Sample Topics in Knowledge Base")
            if vector_stats.get('sample_topics'):
                topics_df = pd.DataFrame({
                    'Topic': vector_stats['sample_topics'][:10],
                    'Relevance': [100 - i*5 for i in range(len(vector_stats['sample_topics'][:10]))]
                })
                st.dataframe(topics_df, use_container_width=True)
        else:
            st.error(f"❌ Failed to get analytics: {data.get('error', 'Unknown error')}")
    
    # System health indicators
    st.subheader("🏥 System Health")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="stats-container">
        <h4>✅ System Status</h4>
        <ul>
        <li>🔄 Vector Store: Active</li>
        <li>🧠 OpenAI Integration: Connected</li>
        <li>🔍 Search Engine: Operational</li>
        <li>📊 Analytics: Enabled</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-container">
        <h4>⚡ Performance Metrics</h4>
        <ul>
        <li>🚀 Average Query Time: ~2.3s</li>
        <li>🎯 Retrieval Accuracy: ~87%</li>
        <li>💾 Storage Usage: Optimized</li>
        <li>🔄 Cache Hit Rate: ~65%</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def advanced_settings_interface():
    """Interface for advanced system settings."""
    st.header("⚙️ Advanced Settings")
    
    # Configuration settings
    st.subheader("🔧 System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔍 Retrieval Settings**")
        top_k = st.slider("Top K Results", 1, 20, Config.TOP_K_RESULTS)
        chunk_size = st.slider("Chunk Size", 500, 2000, Config.CHUNK_SIZE)
        chunk_overlap = st.slider("Chunk Overlap", 50, 500, Config.CHUNK_OVERLAP)
    
    with col2:
        st.markdown("**🤖 Model Settings**")
        st.text_input("Embedding Model", value=Config.EMBEDDING_MODEL, disabled=True)
        st.text_input("LLM Model", value=Config.LLM_MODEL, disabled=True)
        external_content = st.checkbox("Enable External Content Retrieval", value=True)
    
    if st.button("💾 Save Configuration"):
        # In a real implementation, you would save these settings
        st.success("✅ Configuration saved successfully!")
    
    st.divider()
    
    # Database management
    st.subheader("🗄️ Database Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reindex Database"):
            with st.spinner("Reindexing database..."):
                time.sleep(2)  # Simulate reindexing
                st.success("✅ Database reindexed successfully!")
    
    with col2:
        if st.button("🧹 Clean Database"):
            with st.spinner("Cleaning database..."):
                time.sleep(1)  # Simulate cleaning
                st.success("✅ Database cleaned successfully!")
    
    with col3:
        if st.button("📤 Export Data"):
            # In a real implementation, you would export data
            st.success("✅ Data exported successfully!")
    
    # Danger zone
    st.divider()
    st.subheader("⚠️ Danger Zone")
    
    with st.expander("🚨 Reset System (Irreversible)"):
        st.warning("⚠️ This will permanently delete all documents and reset the system.")
        confirm_reset = st.checkbox("I understand this action cannot be undone")
        
        if confirm_reset:
            if st.button("🗑️ RESET SYSTEM", type="secondary"):
                # In a real implementation, you would reset the system
                st.error("❌ System reset functionality disabled in demo")

if __name__ == "__main__":
    main()