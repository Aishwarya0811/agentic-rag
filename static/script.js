// Advanced RAG System - Frontend JavaScript

class RAGInterface {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.ws = null;
        this.isConnected = false;
        this.messageQueue = [];
        
        this.init();
        this.loadSystemStats();
        this.connectWebSocket();
    }

    init() {
        // DOM elements
        this.chatForm = document.getElementById('chat-form');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.uploadForm = document.getElementById('upload-form');
        this.sampleForm = document.getElementById('sample-form');
        this.clearChatBtn = document.getElementById('clear-chat');
        this.systemStatus = document.getElementById('system-status');
        this.toast = document.getElementById('toast');
        this.loadingOverlay = document.getElementById('loading-overlay');

        // Event listeners
        this.setupEventListeners();

        // Initial state
        this.updateSendButton(false);
    }

    setupEventListeners() {
        // Chat form
        this.chatForm.addEventListener('submit', (e) => this.handleChatSubmit(e));
        
        // Upload form
        this.uploadForm.addEventListener('submit', (e) => this.handleUploadSubmit(e));
        
        // Sample form
        this.sampleForm.addEventListener('submit', (e) => this.handleSampleSubmit(e));
        
        // Clear chat
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        
        // Toast close
        document.getElementById('toast-close').addEventListener('click', () => this.hideToast());
        
        // Input focus/blur for better UX
        this.chatInput.addEventListener('focus', () => {
            this.chatInput.parentElement.style.borderColor = 'var(--secondary-color)';
        });
        
        this.chatInput.addEventListener('blur', () => {
            this.chatInput.parentElement.style.borderColor = 'var(--light-gray)';
        });

        // Auto-resize chat input
        this.chatInput.addEventListener('input', () => this.autoResizeInput());
        
        // Enter key handling
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleChatSubmit(e);
            }
        });
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // WebSocket Management
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.processMessageQueue();
            };
            
            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.connectWebSocket(), 3000);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
            };
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.isConnected = false;
        }
    }

    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                this.showToast(data.error, 'error');
                this.updateSendButton(false);
                return;
            }
            
            if (data.response) {
                this.addMessage(data.response, 'assistant');
                this.updateSendButton(false);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    processMessageQueue() {
        while (this.messageQueue.length > 0 && this.isConnected) {
            const message = this.messageQueue.shift();
            this.ws.send(JSON.stringify(message));
        }
    }

    // Chat Management
    async handleChatSubmit(e) {
        e.preventDefault();
        
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        this.updateSendButton(true);

        // Send via WebSocket if connected, otherwise use REST API
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            const wsMessage = {
                message: message,
                session_id: this.sessionId
            };
            
            this.ws.send(JSON.stringify(wsMessage));
        } else {
            // Fallback to REST API
            await this.sendChatMessageRest(message);
        }
    }

    async sendChatMessageRest(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.addMessage(data.response, 'assistant');
            
        } catch (error) {
            console.error('Error sending chat message:', error);
            this.showToast('Failed to send message. Please try again.', 'error');
        } finally {
            this.updateSendButton(false);
        }
    }

    addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const roleLabel = role === 'user' ? '🧑 You:' : '🤖 Assistant:';
        const formattedContent = this.formatMessageContent(content);
        
        messageContent.innerHTML = `<strong>${roleLabel}</strong>${formattedContent}`;
        messageDiv.appendChild(messageContent);
        
        // Remove welcome message if it exists
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage && role === 'user') {
            welcomeMessage.remove();
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessageContent(content) {
        // Convert newlines to <br> and handle basic formatting
        let formatted = content.replace(/\n/g, '<br>');
        
        // Handle bullet points
        formatted = formatted.replace(/^[•·-]\s+(.+)$/gm, '<li>$1</li>');
        if (formatted.includes('<li>')) {
            formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }
        
        // Handle numbered lists
        formatted = formatted.replace(/^(\d+)\.\s+(.+)$/gm, '<li>$2</li>');
        
        // Handle bold text (basic markdown-style)
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        return `<p>${formatted}</p>`;
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    updateSendButton(isLoading) {
        if (isLoading) {
            this.sendButton.disabled = true;
            this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        } else {
            this.sendButton.disabled = false;
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    }

    clearChat() {
        // Remove all messages except welcome message
        const messages = this.chatMessages.querySelectorAll('.message:not(.welcome-message .message)');
        messages.forEach(message => message.remove());
        
        // If no welcome message exists, add it back
        if (!this.chatMessages.querySelector('.welcome-message')) {
            this.addWelcomeMessage();
        }
        
        this.showToast('Chat history cleared', 'info');
    }

    addWelcomeMessage() {
        const welcomeHTML = `
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
        `;
        this.chatMessages.innerHTML = welcomeHTML;
    }

    // Document Upload
    async handleUploadSubmit(e) {
        e.preventDefault();
        
        const title = document.getElementById('doc-title').value.trim();
        const author = document.getElementById('doc-author').value.trim();
        const docType = document.getElementById('doc-type').value;
        const content = document.getElementById('doc-content').value.trim();
        
        if (!title || !content) {
            this.showToast('Please provide both title and content', 'warning');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/documents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    content: content,
                    author: author || 'Web User',
                    doc_type: docType
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(`Document "${title}" added successfully!`, 'success');
                this.uploadForm.reset();
                document.getElementById('doc-author').value = 'Web User'; // Reset to default
                this.loadSystemStats(); // Refresh stats
            } else {
                throw new Error(data.message || 'Failed to add document');
            }
            
        } catch (error) {
            console.error('Error uploading document:', error);
            this.showToast('Failed to add document. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    // Sample Data Generation
    async handleSampleSubmit(e) {
        e.preventDefault();
        
        const topic = document.getElementById('sample-topic').value.trim();
        const count = parseInt(document.getElementById('sample-count').value) || 3;
        
        if (!topic) {
            this.showToast('Please provide a topic', 'warning');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/generate-sample', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic: topic,
                    num_documents: count
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(`Generated ${data.documents.length} sample documents about "${topic}"!`, 'success');
                this.loadSystemStats(); // Refresh stats
            } else {
                throw new Error(data.message || 'Failed to generate sample data');
            }
            
        } catch (error) {
            console.error('Error generating sample data:', error);
            this.showToast('Failed to generate sample data. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    // System Statistics
    async loadSystemStats() {
        try {
            console.log('Loading system stats...');
            const response = await fetch('/api/stats');
            
            console.log('Stats response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Stats data received:', data);
            
            // Handle different response statuses
            if (data.status === 'success' || data.status === 'partial') {
                this.updateSystemStatus(data.stats);
                if (data.message) {
                    console.warn('Stats warning:', data.message);
                }
            } else if (data.status === 'error') {
                console.error('Stats error:', data.error || data.message);
                this.updateSystemStatus(data.stats); // Still show what we can
                this.showToast(data.message || 'System stats partially unavailable', 'warning');
            } else {
                throw new Error('Unexpected response format');
            }
            
        } catch (error) {
            console.error('Error loading system stats:', error);
            
            // Show fallback stats
            this.systemStatus.innerHTML = `
                <div class="text-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    Failed to load stats
                </div>
                <div style="margin-top: 10px; font-size: 0.8em; color: #666;">
                    <button onclick="window.ragInterface.loadSystemStats()" 
                            style="background: none; border: 1px solid #ccc; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                        <i class="fas fa-refresh"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    updateSystemStatus(stats) {
        try {
            console.log('Updating system status with:', stats);
            
            // Safely extract vector stats
            const vectorStats = stats?.vector_store_stats || {};
            
            const statusHTML = `
                <div class="status-item">
                    <span class="status-label">Total Chunks:</span>
                    <span class="status-value">${vectorStats.total_chunks || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Unique Topics:</span>
                    <span class="status-value">${vectorStats.unique_topics || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Document Types:</span>
                    <span class="status-value">${(vectorStats.document_types || []).length}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Authors:</span>
                    <span class="status-value">${vectorStats.unique_authors || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">External Sources:</span>
                    <span class="status-value ${stats?.external_sources_enabled ? 'text-success' : 'text-warning'}">
                        ${stats?.external_sources_enabled ? 'Enabled' : 'Disabled'}
                    </span>
                </div>
                <div class="status-item" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;">
                    <span class="status-label" style="font-size: 0.8em; color: #666;">Last Updated:</span>
                    <span class="status-value" style="font-size: 0.8em; color: #666;">${new Date().toLocaleTimeString()}</span>
                </div>
            `;
            
            this.systemStatus.innerHTML = statusHTML;
            
        } catch (error) {
            console.error('Error updating system status:', error);
            this.systemStatus.innerHTML = `
                <div class="text-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    Error displaying stats
                </div>
            `;
        }
    }

    // UI Utilities
    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }

    showToast(message, type = 'success') {
        const toastMessage = document.getElementById('toast-message');
        toastMessage.textContent = message;
        
        // Reset classes
        this.toast.className = 'toast';
        this.toast.classList.add(type);
        this.toast.classList.remove('hidden');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideToast();
        }, 5000);
    }

    hideToast() {
        this.toast.classList.add('hidden');
    }

    autoResizeInput() {
        // Auto-resize functionality could be added here if needed
        // For now, we keep it simple with a fixed height input
    }

    // Health Check
    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Health check:', data);
            
            if (!data.rag_system_initialized) {
                this.showToast('RAG system is initializing...', 'info');
            }
            
        } catch (error) {
            console.error('Health check failed:', error);
            this.showToast('System health check failed', 'error');
        }
    }
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Advanced RAG System Interface...');
    
    // Create global instance
    window.ragInterface = new RAGInterface();
    
    // Perform initial health check
    window.ragInterface.checkHealth();
    
    console.log('RAG Interface initialized successfully!');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Page became visible, check connection
        if (window.ragInterface && !window.ragInterface.isConnected) {
            window.ragInterface.connectWebSocket();
        }
    }
});

// Handle beforeunload
window.addEventListener('beforeunload', () => {
    if (window.ragInterface && window.ragInterface.ws) {
        window.ragInterface.ws.close();
    }
});