#!/bin/bash

# Python Learning Platform Startup Script
echo "Starting Python Learning Platform..."

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Base directory: $BASE_DIR"

# Function to check and kill processes using specific ports
kill_port_processes() {
    local port=$1
    local process_type=$2
    local process_ids=()
    
    echo "Checking for existing $process_type processes on port $port..."
    
    # Find processes using the specified port
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        process_ids=($(lsof -ti :$port))
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        process_ids=($(fuser $port/tcp 2>/dev/null))
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        process_ids=($(netstat -ano | grep ":$port" | awk '{print $5}'))
    fi
    
    # Kill the processes if any were found
    if [ ${#process_ids[@]} -gt 0 ]; then
        echo "Found ${#process_ids[@]} process(es) using port $port. Terminating..."
        for pid in "${process_ids[@]}"; do
            echo "Killing process $pid"
            kill -9 $pid 2>/dev/null
        done
        # Wait a moment to ensure ports are released
        sleep 2
        echo "Port $port is now free"
    else
        echo "No processes found using port $port"
    fi
}

# Function to open a browser
open_browser() {
    sleep 5  # Wait for servers to initialize
    echo "Opening web browser..."
    
    # Determine the correct command based on the OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "http://localhost:3001"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open > /dev/null; then
            xdg-open "http://localhost:3001"
        elif command -v gnome-open > /dev/null; then
            gnome-open "http://localhost:3001"
        fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        start "http://localhost:3001"
    fi
}

# Create a monitor endpoint for browser connection
create_monitor_endpoint() {
    local monitor_dir="$BASE_DIR/backend/monitor"
    mkdir -p "$monitor_dir"
    
    # Create a simple monitor endpoint that will track browser connections
    cat > "$monitor_dir/__init__.py" << 'EOF'

EOF
    
    cat > "$monitor_dir/monitor.py" << 'EOF'
import time
import threading
import os
import signal
from datetime import datetime

# Global state
last_heartbeat = time.time()
monitor_active = True
inactivity_timeout = 300  # 5 minutes

def register_heartbeat():
    """Register a heartbeat from the client"""
    global last_heartbeat
    last_heartbeat = time.time()
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

def shutdown_server():
    """Shutdown the server after a confirmation delay"""
    print("Shutdown requested. Terminating in 5 seconds...")
    time.sleep(5)
    # Kill the parent process (the shell script)
    os.kill(os.getppid(), signal.SIGTERM)
    return {"status": "shutting_down"}

def start_monitor():
    """Start the inactivity monitor thread"""
    def check_activity():
        global monitor_active, last_heartbeat
        while monitor_active:
            current_time = time.time()
            if (current_time - last_heartbeat) > inactivity_timeout:
                print(f"No activity detected for {inactivity_timeout} seconds. Shutting down...")
                shutdown_server()
                break
            time.sleep(60)  # Check every minute
    
    monitor_thread = threading.Thread(target=check_activity)
    monitor_thread.daemon = True
    monitor_thread.start()
    return monitor_thread

# Initialize the monitor when imported
monitor_thread = start_monitor()
EOF

    # Add routes to the FastAPI app in main.py
    local main_file="$BASE_DIR/backend/main.py"
    
    # Create a backup
    cp "$main_file" "${main_file}.bak"
    
    # Check if monitor imports and routes already exist
    if ! grep -q "from monitor import monitor" "$main_file"; then
        # Add the imports first (after other imports)
        awk '
        /from fastapi import/ { print; print "from monitor import monitor"; next }
        { print }
        ' "${main_file}.bak" > "$main_file"
        
        # Add the monitor routes (after existing routes)
        cat >> "$main_file" << 'EOF'

# Monitor endpoints for browser connection tracking
@app.get("/api/monitor/heartbeat")
def heartbeat():
    """Register a heartbeat from the client to track browser connection"""
    return monitor.register_heartbeat()

@app.get("/api/monitor/shutdown")
def shutdown():
    """Shutdown the server (triggered when browser closed)"""
    return monitor.shutdown_server()
EOF
    fi
}

# Create a client-side heartbeat script
create_heartbeat_script() {
    local script_dir="$BASE_DIR/frontend/public"
    mkdir -p "$script_dir"
    
    cat > "$script_dir/heartbeat.js" << 'EOF'
// Server heartbeat and connection monitor
(function() {
    // Configuration
    const HEARTBEAT_INTERVAL = 30000; // 30 seconds
    const API_URL = 'http://localhost:8003/api';
    
    // Send heartbeat to server
    function sendHeartbeat() {
        fetch(`${API_URL}/monitor/heartbeat`, { 
            method: 'GET',
            headers: { 'Cache-Control': 'no-cache' }
        }).catch(err => {
            console.log('Heartbeat error:', err);
        });
    }
    
    // Send shutdown signal to server
    function sendShutdown() {
        fetch(`${API_URL}/monitor/shutdown`, { 
            method: 'GET',
            headers: { 'Cache-Control': 'no-cache' }
        }).catch(err => {
            console.log('Shutdown request error:', err);
        });
    }
    
    // Setup periodic heartbeat
    const heartbeatInterval = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);
    
    // Initial heartbeat
    sendHeartbeat();
    
    // Setup window close handler
    window.addEventListener('beforeunload', function() {
        clearInterval(heartbeatInterval);
        sendShutdown();
    });
})();
EOF

    # Add script to the app layout
    local layout_file="$BASE_DIR/frontend/app/layout.tsx"
    
    # Create a backup
    cp "$layout_file" "${layout_file}.bak"
    
    # Check if the script tag already exists
    if ! grep -q "heartbeat.js" "$layout_file"; then
        # Add the script tag before the closing head tag
        awk '
        /<\/head>/ { print "        <script src=\"/heartbeat.js\"></script>"; print; next }
        { print }
        ' "${layout_file}.bak" > "$layout_file"
    fi
}

# First, kill any existing processes using our ports
kill_port_processes 8003 "backend"
kill_port_processes 3001 "frontend"

# Set up monitor endpoint and heartbeat script
create_monitor_endpoint
create_heartbeat_script

# Start the backend server in the background
echo "Starting backend server..."
cd "$BASE_DIR/backend"
python run.py &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Wait a moment for the backend to initialize
sleep 2

# Start the frontend development server in the background
echo "Starting frontend server..."
cd "$BASE_DIR/frontend"

# Clean any cached files that might be causing issues
echo "Cleaning previous build artifacts..."
rm -rf .next .cache node_modules/.cache
echo "Clean completed."

# Check if node_modules directory exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take a minute)..."
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install frontend dependencies"
        echo "Shutting down backend server..."
        kill $BACKEND_PID
        exit 1
    fi
else
    # Even if node_modules exists, ensure packages are up-to-date
    echo "Updating frontend dependencies..."
    npm install
    
    # Fix vulnerabilities
    echo "Addressing package vulnerabilities..."
    npm audit fix
    if [ $? -ne 0 ]; then
        echo "WARNING: Not all vulnerabilities could be fixed automatically."
        echo "Consider running 'npm audit fix --force' manually in the frontend directory."
    fi
fi

# Start the frontend server
echo "Starting Next.js development server..."
# Use port 3001 to avoid potential conflicts with port 3000
NODE_ENV=development npx next dev -p 3001 &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

# Open browser in the background
open_browser &
BROWSER_PID=$!

# Function to handle script termination
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BROWSER_PID 2>/dev/null || true  # Kill browser opener if still running
    exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

echo "Python Learning Platform is running!"
echo "- Frontend: http://localhost:3001"
echo "- Backend API: http://localhost:8003/api"
echo "- Automatic shutdown: The server will stop when browser is closed or after 5 minutes of inactivity"
echo "Press Ctrl+C to stop all servers."

# Keep the script running
wait 