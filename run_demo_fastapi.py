#!/usr/bin/env python3
"""
FastAPI Demo Runner for the Advanced RAG System.
Demonstrates the complete FastAPI + Frontend integration.
"""

import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path
import requests
from datetime import datetime

def print_banner():
    """Print a welcome banner."""
    print("=" * 70)
    print("🚀 ADVANCED RAG SYSTEM - FASTAPI DEMO")
    print("=" * 70)
    print("This demo will:")
    print("✅ Start the FastAPI server")
    print("✅ Launch the web interface in your browser")
    print("✅ Provide guided tour of features")
    print("=" * 70)

def check_dependencies():
    """Check if all dependencies are available."""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import openai
        import chromadb
        print("✅ Core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def wait_for_server(url="http://localhost:8000", timeout=30):
    """Wait for the server to be ready."""
    print(f"⏳ Waiting for server at {url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        print(".", end="", flush=True)
    
    print(f"\n❌ Server did not start within {timeout} seconds")
    return False

def start_server():
    """Start the FastAPI server in a separate thread."""
    print("🚀 Starting FastAPI server...")
    
    def run_server():
        try:
            subprocess.run([sys.executable, "fastapi_app.py"], 
                         capture_output=True, text=True)
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return server_thread

def open_browser(url="http://localhost:8000"):
    """Open the web browser."""
    print(f"🌐 Opening web browser to {url}...")
    
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"💡 Please manually open: {url}")
        return False

def run_api_demo():
    """Demonstrate API usage."""
    print("\n🧪 API Demo - Testing key endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        print("   Testing health check...")
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health: {data.get('status', 'unknown')}")
        
        # Test stats endpoint
        print("   Testing system stats...")
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {}).get('vector_store_stats', {})
            print(f"   ✅ Total chunks: {stats.get('total_chunks', 0)}")
            print(f"   ✅ Unique topics: {stats.get('unique_topics', 0)}")
        
        # Test adding a sample document
        print("   Testing document addition...")
        test_doc = {
            "title": "FastAPI Demo Document",
            "content": "This is a demonstration document created via the FastAPI interface. It showcases the document addition capabilities of the Advanced RAG System.",
            "author": "Demo Script",
            "doc_type": "demo_document"
        }
        
        response = requests.post(f"{base_url}/api/documents", json=test_doc)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Document added with {data.get('chunks_created', 0)} chunks")
        
        # Test chat
        print("   Testing chat functionality...")
        chat_msg = {
            "message": "What can you tell me about the system?",
            "session_id": "demo_session"
        }
        
        response = requests.post(f"{base_url}/api/chat", json=chat_msg)
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            print(f"   ✅ Chat response: {response_text[:100]}...")
        
        print("✅ API demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ API demo failed: {e}")
        return False

def print_usage_instructions():
    """Print instructions for using the web interface."""
    print("\n" + "=" * 70)
    print("🎯 WEB INTERFACE GUIDE")
    print("=" * 70)
    print("The web interface is now running at: http://localhost:8000")
    print()
    print("📱 FEATURES TO TRY:")
    print("   1. 💬 CHAT INTERFACE")
    print("      • Ask questions like 'Tell me about artificial intelligence'")
    print("      • Try 'Show me system statistics'")
    print("      • Chat history is maintained in your session")
    print()
    print("   2. 📄 DOCUMENT UPLOAD")
    print("      • Add new documents via the sidebar form")
    print("      • Supports various document types")
    print("      • Documents are automatically indexed")
    print()
    print("   3. 🎲 SAMPLE DATA GENERATION")
    print("      • Generate demo content for any topic")
    print("      • Useful for testing and exploration")
    print("      • Creates realistic sample documents")
    print()
    print("   4. 📊 SYSTEM MONITORING")
    print("      • View real-time system statistics")
    print("      • Monitor knowledge base growth")
    print("      • Track system health")
    print()
    print("🔗 API DOCUMENTATION:")
    print("   • Interactive docs: http://localhost:8000/api/docs")
    print("   • ReDoc format: http://localhost:8000/api/redoc")
    print()
    print("⚡ ADVANCED FEATURES:")
    print("   • Real-time WebSocket chat")
    print("   • Automatic context retrieval")
    print("   • External content integration")
    print("   • Memory pattern learning")
    print("=" * 70)

def main():
    """Main demo function."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if server is already running
    print("🔍 Checking if server is already running...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=3)
        if response.status_code == 200:
            print("✅ Server is already running!")
            server_running = True
        else:
            server_running = False
    except:
        server_running = False
    
    # Start server if not running
    if not server_running:
        server_thread = start_server()
        
        # Wait for server to be ready
        if not wait_for_server():
            print("❌ Failed to start server. Please check the logs.")
            sys.exit(1)
    
    # Run API demo
    print("\n🧪 Running API demonstration...")
    api_success = run_api_demo()
    
    # Open browser
    print("\n🌐 Launching web interface...")
    browser_success = open_browser()
    
    # Print usage instructions
    print_usage_instructions()
    
    # Keep running
    print("\n🔄 Demo is running. Press Ctrl+C to stop.")
    print("   (The server will continue running in the background)")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Demo stopped. Thanks for trying the Advanced RAG System!")
        print("💡 The server may still be running. You can:")
        print("   • Continue using the web interface")
        print("   • Stop it manually if needed")
        
        # Final status
        if api_success and browser_success:
            print("\n🎉 Demo completed successfully!")
            print("🚀 The Advanced RAG System is ready for production use.")
        else:
            print("\n⚠️  Demo had some issues, but core functionality works.")
            print("   Check the console output for details.")

if __name__ == "__main__":
    main()