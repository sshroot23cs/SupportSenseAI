#!/usr/bin/env python
"""
Direct API test without requiring a running server
Tests the Flask app directly using test client
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask
from chat_agent import get_agent

# Create test Flask app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        agent = get_agent()
        status = agent.get_agent_status()
        return {"status": "ok", "agent": status}, 200
    except Exception as e:
        return {"error": str(e), "status": "error"}, 500

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    from flask import request
    try:
        data = request.get_json() or {}
        message = data.get('message')
        user_id = data.get('user_id', 'test')
        
        if not message:
            return {"error": "message required"}, 400
        
        agent = get_agent()
        response = agent.process_message(message, user_id)
        return response, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    print("Starting Flask test client...")
    client = app.test_client()
    
    print("\n=== TEST 1: Health Check ===")
    response = client.get('/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    print("\n=== TEST 2: Chat Message ===")
    response = client.post('/chat', json={
        "message": "Hello, can you help me?",
        "user_id": "test_user_1"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    print("\n=== TEST 3: FAQ ===")
    response = client.post('/chat', json={
        "message": "What plans do you have?",
        "user_id": "test_user_2"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    print("\n=== TEST COMPLETE ===")
