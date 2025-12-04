"""
Flask web API for SquareTrade chat widget
Provides endpoints for the front-end chat interface
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import logging
import uuid
import os
from datetime import datetime
from chat_agent import get_agent

# Configure Flask to serve static files
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

logger = logging.getLogger(__name__)

# Store session info (in production, use Redis or database)
sessions = {}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    agent = get_agent()
    status = agent.get_agent_status()
    return jsonify(status), 200


@app.route('/test', methods=['GET'])
def test():
    """Test connectivity of all components"""
    agent = get_agent()
    results = agent.test_connectivity()
    return jsonify(results), 200


@app.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    Expects JSON: {
        "message": "user message",
        "user_id": "optional user id",
        "session_id": "optional session id"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "message field is required"}), 400
        
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id') or str(uuid.uuid4())
        
        # Track session
        if session_id not in sessions:
            sessions[session_id] = {
                "created_at": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "messages": []
            }
        
        # Process message
        agent = get_agent()
        response_data = agent.process_message(
            user_message=user_message,
            user_id=user_id,
            session_id=session_id
        )
        
        # Log message in session
        sessions[session_id]["messages"].append({
            "user": user_message,
            "agent": response_data.get('response'),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Return response
        return jsonify({
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            **response_data
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/faq', methods=['GET'])
def faq():
    """
    Get FAQ endpoint
    Query params:
        - category: Filter by category (plans, claims, support)
    """
    try:
        category = request.args.get('category')
        agent = get_agent()
        faq_data = agent.get_faq(category=category)
        return jsonify(faq_data), 200
    
    except Exception as e:
        logger.error(f"Error in /faq endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/escalations', methods=['GET'])
def get_escalations():
    """Get pending escalations (admin endpoint)"""
    try:
        agent = get_agent()
        pending = agent.escalation.get_pending_escalations()
        return jsonify({
            "pending_count": len(pending),
            "escalations": pending
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /escalations endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/escalations/<escalation_id>', methods=['PUT'])
def resolve_escalation(escalation_id):
    """Resolve an escalation ticket"""
    try:
        data = request.get_json() or {}
        resolution = data.get('resolution')
        
        agent = get_agent()
        success = agent.escalation.resolve_escalation(escalation_id, resolution)
        
        if success:
            return jsonify({"message": "Escalation resolved"}), 200
        else:
            return jsonify({"error": "Escalation not found"}), 404
    
    except Exception as e:
        logger.error(f"Error resolving escalation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/sessions', methods=['GET'])
def get_sessions():
    """Get session information (admin endpoint)"""
    return jsonify({
        "active_sessions": len(sessions),
        "sessions": sessions
    }), 200


@app.route('/widget', methods=['GET'])
def widget():
    """Serve the chat widget HTML"""
    widget_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SquareTrade Chat Widget</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('/static/allstate-bg.png') center/cover no-repeat fixed;
                min-height: 100vh;
            }
            
            .chat-widget { position: fixed; bottom: 20px; right: 20px; width: 400px; height: 600px; border-radius: 10px; box-shadow: 0 5px 40px rgba(0,0,0,0.16); display: flex; flex-direction: column; background: white; z-index: 9999; }
            
            .chat-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; font-size: 18px; font-weight: 600; }
            
            .chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
            
            .message { margin-bottom: 10px; }
            .message.user { text-align: right; }
            .message.user .text { background: #667eea; color: white; padding: 10px 15px; border-radius: 15px; display: inline-block; max-width: 80%; word-wrap: break-word; }
            .message.agent .text { background: #e3e6ef; color: #333; padding: 10px 15px; border-radius: 15px; display: inline-block; max-width: 80%; word-wrap: break-word; }
            
            .chat-input-area { padding: 15px; border-top: 1px solid #eee; display: flex; gap: 10px; }
            .chat-input-area input { flex: 1; padding: 10px 15px; border: 1px solid #ddd; border-radius: 20px; font-size: 14px; }
            .chat-input-area button { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 20px; cursor: pointer; font-weight: 600; }
            .chat-input-area button:hover { background: #764ba2; }
            
            .loading { text-align: center; color: #999; font-size: 12px; padding: 5px; }
            .escalation-notice { background: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-size: 13px; color: #856404; }
        </style>
    </head>
    <body>
        <div class="chat-widget">
            <div class="chat-header">SquareTrade Support Assistant</div>
            <div class="chat-messages" id="messages"></div>
            <div class="chat-input-area">
                <input type="text" id="inputField" placeholder="Ask a question..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <script>
            const API_URL = '/chat';
            let sessionId = localStorage.getItem('squaretrade_session_id') || '';
            let userId = localStorage.getItem('squaretrade_user_id') || 'widget_user';
            
            async function sendMessage() {
                const input = document.getElementById('inputField');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Display user message
                displayMessage(message, 'user');
                scrollToBottom();
                input.value = '';
                
                // Show loading indicator
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'loading';
                loadingDiv.textContent = 'Thinking...';
                document.getElementById('messages').appendChild(loadingDiv);
                scrollToBottom();
                
                try {
                    const response = await fetch(API_URL, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            user_id: userId,
                            session_id: sessionId
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Save session info
                    if (data.session_id) {
                        sessionId = data.session_id;
                        localStorage.setItem('squaretrade_session_id', sessionId);
                    }
                    
                    // Remove loading indicator
                    loadingDiv.remove();
                    
                    // Display agent response
                    if (data.escalated) {
                        const notice = document.createElement('div');
                        notice.className = 'escalation-notice';
                        notice.textContent = '⚠️ Escalated to human support. Ticket: ' + data.escalation_id;
                        document.getElementById('messages').appendChild(notice);
                        scrollToBottom();
                    }
                    
                    displayMessage(data.response, 'agent');
                    scrollToBottom();
                    
                    // Show confidence if available
                    if (data.confidence !== undefined) {
                        const confidence = document.createElement('div');
                        confidence.className = 'loading';
                        confidence.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
                        document.getElementById('messages').appendChild(confidence);
                        scrollToBottom();
                    }
                } catch (error) {
                    loadingDiv.remove();
                    displayMessage('Error: ' + error.message, 'agent');
                    scrollToBottom();
                }
            }
            
            function displayMessage(text, sender) {
                const div = document.createElement('div');
                div.className = 'message ' + sender;
                div.innerHTML = '<div class="text">' + escapeHtml(text) + '</div>';
                document.getElementById('messages').appendChild(div);
            }
            
            function scrollToBottom() {
                const messagesDiv = document.getElementById('messages');
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function escapeHtml(text) {
                const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
                return text.replace(/[&<>"']/g, m => map[m]);
            }
            
            // Allow Enter key to send
            document.getElementById('inputField').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
            
            // Welcome message
            window.addEventListener('load', () => {
                displayMessage('Hello! I\\'m the SquareTrade Support Assistant. How can I help you today?', 'agent');
                scrollToBottom();
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(widget_html)


@app.route('/', methods=['GET'])
def index():
    """Root endpoint - redirect to widget"""
    return '''
    <html>
    <body>
        <h1>SquareTrade Chat Agent API</h1>
        <ul>
            <li><a href="/widget">Open Chat Widget</a></li>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/test">Test Components</a></li>
            <li><a href="/faq">Get FAQs</a></li>
            <li><a href="/escalations">View Escalations</a></li>
        </ul>
    </body>
    </html>
    ''', 200


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
