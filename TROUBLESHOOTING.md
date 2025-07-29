# Troubleshooting Guide - Advanced RAG System

## Common Issues and Solutions

### 🔧 Sample Generation Returns 500 Error

**Symptoms:**
- Sample generation button shows error
- Console shows "500 Internal Server Error" for `/api/generate-sample`
- May see "Gathering content for..." message cut off

**Causes:**
- Network issues when fetching external content (Wikipedia API)
- Timeout during external content retrieval
- Missing dependencies or initialization issues

**Solutions:**

1. **Disable External Content (Quick Fix):**
   ```bash
   # Add to your .env file:
   ENABLE_EXTERNAL_CONTENT=false
   ```
   Then restart the server.

2. **Apply Quick Fix Patch:**
   ```bash
   python quick_fix.py
   ```
   This patches the external content retriever for better error handling.

3. **Check Network Connection:**
   - Ensure internet connection is stable
   - Check if Wikipedia API is accessible
   - Try accessing https://en.wikipedia.org/api/rest_v1/page/summary/artificial_intelligence

4. **Restart the Server:**
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart:
   python fastapi_app.py
   ```

### 🚫 Favicon 404 Error

**Symptoms:**
- Browser console shows 404 error for `/favicon.ico`

**Solution:**
This is cosmetic and doesn't affect functionality. The favicon endpoint now returns a simple response.

### 🔌 WebSocket Connection Issues

**Symptoms:**
- Chat messages don't send in real-time
- "Connection failed" messages in browser console

**Solutions:**

1. **Check Browser WebSocket Support:**
   - Modern browsers support WebSockets
   - Check browser developer tools Network tab

2. **Firewall/Proxy Issues:**
   - Ensure port 8000 is accessible
   - Check corporate firewall settings

3. **Fallback to REST API:**
   - The system automatically falls back to REST API if WebSocket fails
   - Chat will still work, just not real-time

### 🔑 API Key Issues

**Symptoms:**
- "RAG system not initialized" errors
- OpenAI API errors in console

**Solutions:**

1. **Check .env File:**
   ```bash
   # Make sure .env exists and contains:
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Validate API Key:**
   ```bash
   python -c "
   from dotenv import load_dotenv
   import os
   load_dotenv()
   print('API Key found:', bool(os.getenv('OPENAI_API_KEY')))
   "
   ```

3. **Re-initialize System:**
   - Use the `/api/initialize` endpoint
   - Or restart the server

### 💾 ChromaDB Permission Issues

**Symptoms:**
- Permission denied errors when creating `chroma_db` directory
- Database initialization failures

**Solutions:**

1. **Check Directory Permissions:**
   ```bash
   # On Windows:
   # Make sure the directory is writable
   
   # On Linux/Mac:
   chmod 755 ./chroma_db
   ```

2. **Clear Database:**
   ```bash
   # Remove the database directory if corrupted:
   rm -rf chroma_db
   # Then restart the server
   ```

### 🐌 Slow Performance

**Symptoms:**
- Chat responses take very long
- Document upload is slow

**Solutions:**

1. **Reduce Vector Search Results:**
   ```bash
   # In .env file:
   TOP_K_RESULTS=3
   ```

2. **Disable External Content:**
   ```bash
   # In .env file:
   ENABLE_EXTERNAL_CONTENT=false
   ```

3. **Check System Resources:**
   - Ensure adequate RAM (4GB+ recommended)
   - Check CPU usage during operations

### 📱 Frontend Not Loading

**Symptoms:**
- Blank page at http://localhost:8000
- Static files not loading

**Solutions:**

1. **Check Static Files:**
   ```bash
   # Ensure these files exist:
   ls static/style.css
   ls static/script.js
   ```

2. **Clear Browser Cache:**
   - Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
   - Clear browser cache and cookies

3. **Check Console for Errors:**
   - Open browser developer tools (F12)
   - Look for JavaScript or CSS loading errors

### 🔄 Server Won't Start

**Symptoms:**
- Port 8000 already in use
- Import errors on startup

**Solutions:**

1. **Port Already in Use:**
   ```bash
   # Kill existing process:
   # On Windows:
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # On Linux/Mac:
   lsof -ti:8000 | xargs kill
   ```

2. **Missing Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Use Different Port:**
   ```bash
   # Modify fastapi_app.py, change the port in uvicorn.run()
   uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8001)
   ```

## 🔍 Debugging Steps

### 1. Check System Health
```bash
curl http://localhost:8000/api/health
```

### 2. View System Statistics
```bash
curl http://localhost:8000/api/stats
```

### 3. Test Chat API
```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello test"}'
```

### 4. Check Server Logs
- Look at the terminal where you started the server
- Check for error messages and stack traces

### 5. Browser Developer Tools
- Open with F12
- Check Console tab for JavaScript errors
- Check Network tab for failed requests

## 🛠️ Advanced Troubleshooting

### Enable Debug Mode
Add to your .env file:
```bash
DEBUG=true
LOG_LEVEL=debug
```

### Test Individual Components
```bash
# Test vector store
python vector_store.py

# Test sample data generator
python sample_data_generator.py

# Test RAG retriever
python rag_retriever.py

# Test agents system
python agents_rag_system.py
```

### Reset Everything
```bash
# Remove database
rm -rf chroma_db

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Restart server
python fastapi_app.py
```

## 🆘 Getting Help

If you're still experiencing issues:

1. **Check the GitHub Issues:** Look for similar problems
2. **Create a Bug Report:** Include:
   - Your operating system
   - Python version
   - Complete error messages
   - Steps to reproduce the issue
   - Browser and version (for frontend issues)

3. **Enable Verbose Logging:** Add detailed logs to help diagnose the issue

4. **Use the Test Suite:**
   ```bash
   python test_system.py
   python test_fastapi.py
   ```

## 💡 Performance Tips

1. **Use SSD Storage:** For better ChromaDB performance
2. **Increase RAM:** More RAM helps with vector operations
3. **Disable External Content:** For faster, more reliable operation
4. **Reduce Document Size:** Large documents take longer to process
5. **Use Smaller Embedding Models:** If performance is critical

## 🔒 Security Notes

1. **API Key Security:** Never commit .env files to version control
2. **Network Security:** In production, use HTTPS and proper authentication
3. **File Uploads:** Validate and sanitize uploaded content
4. **CORS Settings:** Restrict origins in production environments