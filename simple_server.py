#!/usr/bin/env python3
"""
Simple test - just start the server
"""
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting simple test...")

try:
    logger.info("Importing Flask...")
    from flask import Flask
    logger.info("Flask imported successfully")
    
    logger.info("Creating Flask app...")
    app = Flask(__name__)
    logger.info("Flask app created")
    
    @app.route('/test')
    def test():
        return {'status': 'ok'}
    
    logger.info("Starting server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    sys.exit(1)
