#!/usr/bin/env python
"""
Simple test server to verify API functionality
Minimal Flask server to test endpoints without loading the full agent on startup
"""

from flask import Flask, jsonify, request, render_template_string
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

app = Flask(__name__)

# Track messages
messages = []
escalations = []

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "flask": "running",
            "api": "ready"
        }
    }), 200

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint - simplified for testing"""
    try:
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id', 'test-session')
        
        if not message:
            return jsonify({"error": "message required"}), 400
        
        # Store message
        messages.append({
            "user": message,
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Simple response logic
        response_text = f"Echo: {message}"
        if any(word in message.lower() for word in ['help', 'support', 'issue']):
            response_text = "I can help with that. Let me escalate this to support."
            escalations.append({
                "id": f"ESC-{len(escalations)+1}",
                "user_id": user_id,
                "issue": message,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return jsonify({
            "session_id": session_id,
            "response": response_text,
            "confidence": 0.85,
            "escalated": len(escalations) > 0,
            "escalation_id": escalations[-1]["id"] if escalations else None
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/faq', methods=['GET'])
def faq():
    """FAQ endpoint"""
    category = request.args.get('category')
    faq_data = {
        "faqs": [
            {"id": "1", "question": "What is SquareTrade?", "answer": "SquareTrade is a protection plan provider.", "category": "general"},
            {"id": "2", "question": "How to file a claim?", "answer": "Visit claims.squaretrade.com", "category": "claims"},
            {"id": "3", "question": "What's covered?", "answer": "Accidental damage, mechanical failure, etc.", "category": "coverage"}
        ]
    }
    if category:
        faq_data["faqs"] = [f for f in faq_data["faqs"] if f.get("category") == category]
    return jsonify(faq_data), 200

@app.route('/escalations', methods=['GET'])
def get_escalations():
    """Get escalations"""
    return jsonify({
        "count": len(escalations),
        "escalations": escalations
    }), 200

@app.route('/widget', methods=['GET'])
def widget():
    """Widget HTML"""
    return render_template_string("""
    <html>
    <head><title>Test Widget</title></head>
    <body>
        <h1>Chat Widget Test</h1>
        <p>This is a test widget endpoint</p>
    </body>
    </html>
    """)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "name": "SquareTrade Chat API",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "chat": "POST /chat",
            "faq": "GET /faq",
            "escalations": "GET /escalations",
            "widget": "GET /widget"
        }
    }), 200

if __name__ == '__main__':
    print("Starting test server on http://127.0.0.1:5000")
    sys.stdout.flush()
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
