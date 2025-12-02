#!/usr/bin/env python
from flask import Flask
app = Flask(__name__)

@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/')
def index():
    return {"message": "Server is running"}, 200

if __name__ == '__main__':
    print("Server starting...")
    app.run(host='127.0.0.1', port=5000, debug=False)
