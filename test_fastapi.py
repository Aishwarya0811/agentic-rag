#!/usr/bin/env python3
"""
Test script for FastAPI + Frontend integration.
Tests API endpoints and frontend functionality.
"""

import sys
import asyncio
import time
from pathlib import Path
from typing import Dict, Any

# Test imports
try:
    import requests
    import websockets
    import json
    from fastapi.testclient import TestClient
except ImportError as e:
    print(f"❌ Missing test dependencies: {e}")
    print("💡 Install with: pip install requests websockets httpx")
    sys.exit(1)

def test_file_structure():
    """Test that all required files exist."""
    print("🧪 Testing File Structure...")
    
    required_files = [
        "fastapi_app.py",
        "static/style.css", 
        "static/script.js",
        "agents_rag_system.py",
        "config.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def test_static_files():
    """Test that static files have content."""
    print("🧪 Testing Static Files...")
    
    try:
        # Test CSS file
        css_file = Path("static/style.css")
        if css_file.exists():
            css_content = css_file.read_text()
            if len(css_content) > 1000 and "Advanced RAG System" in css_content:
                print("✅ CSS file has content")
            else:
                print("⚠️  CSS file seems incomplete")
        
        # Test JS file
        js_file = Path("static/script.js")
        if js_file.exists():
            js_content = js_file.read_text()
            if len(js_content) > 1000 and "RAGInterface" in js_content:
                print("✅ JavaScript file has content")
            else:
                print("⚠️  JavaScript file seems incomplete")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing static files: {e}")
        return False

def test_fastapi_import():
    """Test that FastAPI app can be imported."""
    print("🧪 Testing FastAPI Import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        # Import FastAPI app
        from fastapi_app import app
        
        print("✅ FastAPI app imported successfully")
        return True, app
        
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False, None

def test_api_endpoints():
    """Test API endpoints using TestClient."""
    print("🧪 Testing API Endpoints...")
    
    success, app = test_fastapi_import()
    if not success:
        return False
    
    try:
        client = TestClient(app)
        
        # Test health endpoint
        print("   Testing /api/health...")
        response = client.get("/api/health")
        if response.status_code == 200:
            data = response.json()
            if "status" in data and "timestamp" in data:
                print("   ✅ Health endpoint working")
            else:
                print("   ⚠️  Health endpoint response format unexpected")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test main page
        print("   Testing / (main page)...")
        response = client.get("/")
        if response.status_code == 200:
            content = response.text
            if "Advanced RAG System" in content and "DOCTYPE html" in content:
                print("   ✅ Main page serving HTML")
            else:
                print("   ⚠️  Main page content unexpected")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
            return False
        
        # Test stats endpoint (may fail if system not initialized)
        print("   Testing /api/stats...")
        response = client.get("/api/stats")
        if response.status_code in [200, 503]:  # 503 if not initialized
            print("   ✅ Stats endpoint responsive")
        else:
            print(f"   ❌ Stats endpoint failed: {response.status_code}")
        
        print("✅ API endpoints test completed")
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def test_document_api():
    """Test document-related API endpoints."""
    print("🧪 Testing Document API...")
    
    success, app = test_fastapi_import()
    if not success:
        return False
    
    try:
        client = TestClient(app)
        
        # Test document addition (may fail if system not initialized)
        print("   Testing POST /api/documents...")
        test_doc = {
            "title": "Test Document",
            "content": "This is a test document for the RAG system.",
            "author": "Test Suite",
            "doc_type": "test_document"
        }
        
        response = client.post("/api/documents", json=test_doc)
        if response.status_code in [200, 503]:  # 503 if system not initialized
            print("   ✅ Document API endpoint responsive")
        else:
            print(f"   ⚠️  Document API returned: {response.status_code}")
        
        # Test sample generation
        print("   Testing POST /api/generate-sample...")
        sample_request = {
            "topic": "test topic",
            "num_documents": 1
        }
        
        response = client.post("/api/generate-sample", json=sample_request)
        if response.status_code in [200, 503]:
            print("   ✅ Sample generation endpoint responsive")
        else:
            print(f"   ⚠️  Sample generation returned: {response.status_code}")
        
        print("✅ Document API test completed")
        return True
        
    except Exception as e:
        print(f"❌ Document API test failed: {e}")
        return False

def test_chat_api():
    """Test chat API endpoint."""
    print("🧪 Testing Chat API...")
    
    success, app = test_fastapi_import()
    if not success:
        return False
    
    try:
        client = TestClient(app)
        
        # Test chat endpoint
        print("   Testing POST /api/chat...")
        chat_message = {
            "message": "Hello, this is a test message",
            "session_id": "test_session"
        }
        
        response = client.post("/api/chat", json=chat_message)
        if response.status_code in [200, 503]:  # 503 if system not initialized
            print("   ✅ Chat API endpoint responsive")
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "session_id" in data:
                    print("   ✅ Chat response format correct")
                else:
                    print("   ⚠️  Chat response format unexpected")
        else:
            print(f"   ❌ Chat API failed: {response.status_code}")
            return False
        
        print("✅ Chat API test completed")
        return True
        
    except Exception as e:
        print(f"❌ Chat API test failed: {e}")
        return False

def test_frontend_integration():
    """Test that frontend files integrate correctly."""
    print("🧪 Testing Frontend Integration...")
    
    try:
        # Test that main HTML includes CSS and JS
        success, app = test_fastapi_import()
        if not success:
            return False
        
        client = TestClient(app)
        response = client.get("/")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for CSS link
            if "/static/style.css" in html_content:
                print("   ✅ CSS file linked in HTML")
            else:
                print("   ❌ CSS file not linked in HTML")
                return False
            
            # Check for JS script
            if "/static/script.js" in html_content:
                print("   ✅ JavaScript file linked in HTML")
            else:
                print("   ❌ JavaScript file not linked in HTML")
                return False
            
            # Check for key HTML elements
            required_elements = [
                "chat-form", "chat-input", "chat-messages",
                "upload-form", "sample-form", "system-status"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in html_content:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"   ⚠️  Missing HTML elements: {', '.join(missing_elements)}")
            else:
                print("   ✅ All key HTML elements present")
            
            print("✅ Frontend integration test completed")
            return True
        else:
            print(f"   ❌ Could not fetch main page: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Frontend integration test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all FastAPI + Frontend tests."""
    print("🚀 Starting FastAPI + Frontend Integration Tests")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Static Files", test_static_files),
        ("FastAPI Import", lambda: test_fastapi_import()[0]),
        ("API Endpoints", test_api_endpoints),
        ("Document API", test_document_api),
        ("Chat API", test_chat_api),
        ("Frontend Integration", test_frontend_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI + Frontend integration is working.")
        print("\n🚀 Next steps:")
        print("   1. Run: python launch.py start")
        print("   2. Open: http://localhost:8000")
        print("   3. Test the web interface manually")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("   Common issues:")
        print("   - Missing dependencies (check requirements.txt)")
        print("   - Missing OpenAI API key (check .env file)")
        print("   - File permissions or path issues")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)