#!/usr/bin/env python3
"""
Production-ready startup script for SquareTrade Chat Agent
Manages server process, logging, and graceful shutdown
"""

import os
import sys
import logging
import signal
import time
import subprocess
import psutil
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent
VENV_PATH = PROJECT_ROOT / "venv"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / f"server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
PID_FILE = PROJECT_ROOT / "server.pid"
PORT = 5000
HOST = "0.0.0.0"

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ServerManager:
    """Manages the Flask server process"""
    
    def __init__(self):
        self.process = None
        self.is_running = False
        
    def _check_port_available(self) -> bool:
        """Check if port is available"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                for conn in proc.net_connections(kind='inet'):
                    if conn.laddr.port == PORT:
                        logger.warning(f"Port {PORT} is already in use by PID {proc.pid}")
                        return False
            return True
        except Exception as e:
            logger.warning(f"Could not check port availability: {e}")
            return True
    
    def _cleanup_stale_processes(self):
        """Kill any stale Python processes from previous runs"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'web_widget' in ' '.join(proc.cmdline() or []):
                        if proc.pid != os.getpid():
                            logger.info(f"Cleaning up stale process: PID {proc.pid}")
                            proc.terminate()
                            try:
                                proc.wait(timeout=3)
                            except psutil.TimeoutExpired:
                                proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.warning(f"Could not cleanup stale processes: {e}")
    
    def start(self) -> bool:
        """Start the Flask server"""
        logger.info("=" * 60)
        logger.info("SquareTrade Chat Agent - Server Startup")
        logger.info("=" * 60)
        
        # Cleanup stale processes
        self._cleanup_stale_processes()
        time.sleep(1)
        
        # Check port availability
        if not self._check_port_available():
            logger.error(f"Port {PORT} is already in use. Cannot start server.")
            return False
        
        # Verify venv exists
        if not VENV_PATH.exists():
            logger.error(f"Virtual environment not found at {VENV_PATH}")
            logger.error("Please run: python -m venv venv")
            return False
        
        # Change to project directory
        os.chdir(PROJECT_ROOT)
        logger.info(f"Working directory: {PROJECT_ROOT}")
        
        # Setup environment
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        
        # Build command
        if sys.platform == 'win32':
            python_exe = VENV_PATH / "Scripts" / "python.exe"
        else:
            python_exe = VENV_PATH / "bin" / "python"
        
        if not python_exe.exists():
            logger.error(f"Python executable not found at {python_exe}")
            return False
        
        # Start server
        cmd = [
            str(python_exe),
            "web_widget.py"
        ]
        
        logger.info(f"Starting server: {' '.join(cmd)}")
        logger.info(f"Server will listen on http://{HOST}:{PORT}")
        logger.info(f"Logs: {LOG_FILE}")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                env=env,
                cwd=str(PROJECT_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Save PID
            with open(PID_FILE, 'w') as f:
                f.write(str(self.process.pid))
            
            logger.info(f"Server process started with PID: {self.process.pid}")
            self.is_running = True
            
            # Monitor process
            self._monitor_process()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def _monitor_process(self):
        """Monitor the server process and log output"""
        try:
            for line in self.process.stdout:
                if line.strip():
                    logger.info(f"[SERVER] {line.rstrip()}")
            
            # Process ended
            return_code = self.process.wait()
            logger.warning(f"Server process exited with code: {return_code}")
            self.is_running = False
            
        except Exception as e:
            logger.error(f"Error monitoring process: {e}")
            self.is_running = False
    
    def stop(self, graceful=True):
        """Stop the server gracefully"""
        if not self.process or not self.is_running:
            logger.info("Server is not running")
            return
        
        logger.info("Stopping server...")
        
        try:
            if graceful:
                # Send SIGTERM for graceful shutdown
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                    logger.info("Server stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning("Server did not stop gracefully, forcing...")
                    self.process.kill()
                    self.process.wait()
                    logger.info("Server killed")
            else:
                # Force kill
                self.process.kill()
                self.process.wait()
                logger.info("Server killed")
        
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
        
        finally:
            self.is_running = False
            # Clean up PID file
            if PID_FILE.exists():
                PID_FILE.unlink()
    
    def restart(self):
        """Restart the server"""
        logger.info("Restarting server...")
        self.stop(graceful=True)
        time.sleep(2)
        self.start()


def signal_handler(manager, signum, frame):
    """Handle shutdown signals"""
    logger.info(f"\nReceived signal {signum}")
    manager.stop(graceful=True)
    sys.exit(0)


def main():
    """Main entry point"""
    manager = ServerManager()
    
    # Setup signal handlers
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(manager, s, f))
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(manager, s, f))
    
    # Start server
    if not manager.start():
        sys.exit(1)


if __name__ == '__main__':
    main()
