#!/bin/bash

# Configuration
WORKSPACE_DIR="$(pwd)"
CREDENTIALS_FILE="$HOME/.gmail-mcp/credentials.json"
PYTHON_VENV="$WORKSPACE_DIR/venv"
GMAIL_MCP_PID=""
PYTHON_BACKEND_PID=""
FRONTEND_PID=""

# Function to check if authentication is needed
check_auth() {
    if [ ! -f "$CREDENTIALS_FILE" ]; then
        echo "First time setup: Running authentication..."
        cd Gmail-MCP-Server && node dist/index.js auth
        if [ $? -ne 0 ]; then
            echo "Authentication failed. Please try again."
            exit 1
        fi
        cd "$WORKSPACE_DIR"
    fi
}

# Function to cleanup processes
cleanup() {
    echo "Shutting down services..."
    
    if [ ! -z "$GMAIL_MCP_PID" ]; then
        echo "Shutting down Gmail MCP Server..."
        kill $GMAIL_MCP_PID 2>/dev/null
    fi
    
    if [ ! -z "$PYTHON_BACKEND_PID" ]; then
        echo "Shutting down Python backend..."
        kill $PYTHON_BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Shutting down Next.js frontend..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Deactivate Python virtual environment if active
    if [ ! -z "$VIRTUAL_ENV" ]; then
        deactivate 2>/dev/null
    fi
    
    # Return to original directory
    cd "$WORKSPACE_DIR"
    
    wait 2>/dev/null
}

# Set up cleanup trap
trap cleanup EXIT

# Check if virtual environment exists
if [ ! -d "$PYTHON_VENV" ]; then
    echo "Error: Python virtual environment not found at $PYTHON_VENV"
    echo "Please create it using: python -m venv venv"
    exit 1
fi

# Check if activate script exists
if [ ! -f "$PYTHON_VENV/bin/activate" ]; then
    echo "Error: Virtual environment activate script not found at $PYTHON_VENV/bin/activate"
    exit 1
fi

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "Error: pnpm is not installed. Please install it using:"
    echo "npm install -g pnpm"
    exit 1
fi

# Main execution
echo "Starting services..."

# Check and perform Gmail MCP auth if needed
check_auth

# Start Gmail MCP Server in background
cd Gmail-MCP-Server && node dist/index.js &
GMAIL_MCP_PID=$!
cd "$WORKSPACE_DIR"

echo "Gmail MCP Server started (PID: $GMAIL_MCP_PID)"

# Start Next.js frontend in background
echo "Starting Next.js frontend..."
cd livekit-frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    pnpm install
fi

pnpm dev &
FRONTEND_PID=$!
cd "$WORKSPACE_DIR"

echo "Next.js frontend started (PID: $FRONTEND_PID)"

# Activate Python virtual environment and start backend
echo "Activating Python virtual environment at $PYTHON_VENV..."
source "$PYTHON_VENV/bin/activate"

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate Python virtual environment"
    exit 1
fi

# Verify Python environment
echo "Using Python: $(which python)"
echo "Virtual env: $VIRTUAL_ENV"

# Check if required Python packages are installed
if ! pip list | grep -q "livekit"; then
    echo "Installing required Python packages..."
    pip install -r requirements.txt
fi

echo "Starting Python backend..."
cd "$WORKSPACE_DIR"
python "$WORKSPACE_DIR/main.py" dev &
PYTHON_BACKEND_PID=$!

echo "Python backend started (PID: $PYTHON_BACKEND_PID)"

# Keep script running and show logs
echo "All services started. Press Ctrl+C to stop."
echo "
Services running:
- Gmail MCP Server (PID: $GMAIL_MCP_PID)
- Next.js Frontend (PID: $FRONTEND_PID) - http://localhost:3000
- Python Backend (PID: $PYTHON_BACKEND_PID)
"
wait