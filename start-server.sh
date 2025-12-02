#!/bin/bash

# Bash startup script for SquareTrade Chat Agent
# Usage: ./start-server.sh

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/server_$TIMESTAMP.log"
PID_FILE="$PROJECT_ROOT/server.pid"
PORT=5000

# Create log directory
mkdir -p "$LOG_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_server() {
    echo -e "${CYAN}[SERVER]${NC} $1" | tee -a "$LOG_FILE"
}

cleanup_processes() {
    log_info "Cleaning up existing processes..."
    
    # Find and kill existing web_widget processes
    pgrep -f "python.*web_widget" | while read pid; do
        if [ "$pid" != "$$" ]; then
            log_warning "Terminating existing process: PID $pid"
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
    
    sleep 2
}

check_port() {
    if command -v lsof &> /dev/null; then
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_error "Port $PORT is already in use"
            return 1
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tlnp 2>/dev/null | grep ":$PORT " | grep -q LISTEN; then
            log_error "Port $PORT is already in use"
            return 1
        fi
    fi
    return 0
}

verify_environment() {
    # Check venv exists
    if [ ! -d "$VENV_PATH" ]; then
        log_error "Virtual environment not found at $VENV_PATH"
        log_error "Please run: python3 -m venv venv"
        return 1
    fi
    
    # Check Python executable exists
    PYTHON_EXE="$VENV_PATH/bin/python"
    if [ ! -x "$PYTHON_EXE" ]; then
        log_error "Python executable not found at $PYTHON_EXE"
        return 1
    fi
    
    return 0
}

start_server() {
    log_info "============================================================"
    log_info "SquareTrade Chat Agent - Server Startup"
    log_info "============================================================"
    
    # Cleanup existing processes
    cleanup_processes
    
    # Check port availability
    if ! check_port; then
        return 1
    fi
    
    # Verify environment
    if ! verify_environment; then
        return 1
    fi
    
    PYTHON_EXE="$VENV_PATH/bin/python"
    
    log_info "Working directory: $PROJECT_ROOT"
    log_info "Server will listen on http://0.0.0.0:$PORT"
    log_info "Logs: $LOG_FILE"
    log_info "Starting server..."
    
    # Set environment variables
    export PYTHONUNBUFFERED=1
    export PYTHONDONTWRITEBYTECODE=1
    
    cd "$PROJECT_ROOT"
    
    # Start server
    {
        $PYTHON_EXE web_widget.py 2>&1 | while IFS= read -r line; do
            log_server "$line"
        done
    } &
    
    SERVER_PID=$!
    
    # Save PID
    echo $SERVER_PID > "$PID_FILE"
    log_info "Server process started with PID: $SERVER_PID"
    
    # Wait for server process
    wait $SERVER_PID
    
    return 0
}

stop_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        log_info "Stopping server (PID: $PID)..."
        
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
            sleep 1
            
            # Force kill if still running
            if kill -0 "$PID" 2>/dev/null; then
                log_warning "Force killing process..."
                kill -9 "$PID" 2>/dev/null || true
            fi
        fi
        
        rm -f "$PID_FILE"
        log_info "Server stopped"
    fi
}

# Handle signals
trap stop_server SIGTERM SIGINT

# Main execution
log_info "SquareTrade Server Manager Starting..."

if start_server; then
    log_info "Server started successfully"
    exit 0
else
    log_error "Failed to start server"
    exit 1
fi
