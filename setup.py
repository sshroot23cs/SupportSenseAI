"""
Setup script to initialize the SquareTrade Chat Agent
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_directories():
    """Create necessary directories"""
    dirs = [
        "data",
        "logs"
    ]
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        logger.info(f"✓ Created directory: {dir_name}")


def create_env_file():
    """Create .env file with default configuration"""
    env_content = """# SquareTrade Chat Agent Configuration

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Logging
LOG_LEVEL=INFO

# RAG Settings
CHUNK_SIZE=500
TOP_K_RESULTS=3

# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        logger.info("✓ Created .env file")
    else:
        logger.info("✓ .env file already exists")


def check_ollama_installation():
    """Check if Ollama is installed and running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            logger.info("✓ Ollama server is running")
            models = response.json().get('models', [])
            if models:
                logger.info(f"  Available models: {len(models)}")
                for model in models:
                    logger.info(f"    - {model.get('name')}")
            else:
                logger.warning("  ⚠ No models found. Pull a model first: ollama pull mistral")
            return True
        else:
            logger.error("✗ Ollama server returned error")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("✗ Cannot connect to Ollama server at localhost:11434")
        logger.error("  Make sure Ollama is installed and running")
        return False
    except Exception as e:
        logger.error(f"✗ Error checking Ollama: {e}")
        return False


def validate_installation():
    """Validate that all components can be imported"""
    try:
        logger.info("\nValidating imports...")
        
        import flask
        logger.info("✓ Flask")
        
        import flask_cors
        logger.info("✓ Flask-CORS")
        
        import requests
        logger.info("✓ Requests")
        
        # Import our modules
        from config import OLLAMA_BASE_URL, OLLAMA_MODEL
        logger.info("✓ Config module")
        
        from data_loader import KnowledgeBase
        logger.info("✓ Data Loader")
        
        from llm_client import OllamaClient
        logger.info("✓ LLM Client")
        
        from rag_engine import RAGEngine
        logger.info("✓ RAG Engine")
        
        from escalation_handler import EscalationHandler
        logger.info("✓ Escalation Handler")
        
        from chat_agent import SquareTradeAgent
        logger.info("✓ Chat Agent")
        
        logger.info("\n✓ All imports successful!")
        return True
    
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        logger.error("  Run: pip install -r requirements.txt")
        return False


def main():
    """Run setup"""
    logger.info("=" * 50)
    logger.info("SquareTrade Chat Agent - Setup Script")
    logger.info("=" * 50)
    
    # Create directories
    logger.info("\n1. Creating directories...")
    create_directories()
    
    # Create env file
    logger.info("\n2. Setting up configuration...")
    create_env_file()
    
    # Check Ollama
    logger.info("\n3. Checking Ollama installation...")
    ollama_available = check_ollama_installation()
    
    # Validate imports
    logger.info("\n4. Validating Python dependencies...")
    imports_valid = validate_installation()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("Setup Summary:")
    logger.info("=" * 50)
    logger.info(f"Directories: ✓")
    logger.info(f"Configuration: ✓")
    logger.info(f"Ollama Server: {'✓' if ollama_available else '✗ Not running'}")
    logger.info(f"Python Dependencies: {'✓' if imports_valid else '✗ Missing packages'}")
    
    if not ollama_available:
        logger.warning("\n⚠ Ollama is not running.")
        logger.warning("  To start Ollama:")
        logger.warning("    On macOS: brew services start ollama")
        logger.warning("    On Windows: ollama serve")
        logger.warning("    On Linux: systemctl start ollama")
        logger.warning("\n  Or install from: https://ollama.ai")
    
    if not imports_valid:
        logger.error("\n✗ Please install dependencies: pip install -r requirements.txt")
        return 1
    
    logger.info("\n" + "=" * 50)
    logger.info("Setup complete! You can now run:")
    logger.info("  python web_widget.py")
    logger.info("=" * 50)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
