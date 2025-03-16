#!/bin/bash

# Function to check if port is in use and kill the process
kill_process_on_port() {
    PORT=$1
    # Find PID of process using the port
    PID=$(lsof -ti:$PORT)
    if [ ! -z "$PID" ]; then
        echo "Port $PORT is already in use. Stopping existing process..."
        kill -9 $PID
        sleep 1
    fi
}

# Kill any processes already using our ports
kill_process_on_port 3000  # Frontend port

# Check if frontend exists and start it
if [ -d "frontend" ]; then
    echo "Starting Next.js frontend..."
    cd frontend
    
    # Check if node_modules exists, if not run npm install
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    # Start the frontend
    npm run dev &
    FRONTEND_PID=$!
    
    echo ""
    echo "====================================================="
    echo "Python Learning Platform frontend running!"
    echo "Frontend: http://localhost:3000 (opening in browser)"
    echo "Press Ctrl+C to stop the server"
    echo "====================================================="
    echo ""
    
    # Open browser after a short delay to ensure frontend is ready
    sleep 3
    open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null || start http://localhost:3000 2>/dev/null || echo "Could not open browser automatically"
    
    # Function to handle termination signals
    function cleanup {
        echo "Stopping frontend server..."
        kill $FRONTEND_PID 2>/dev/null
        exit
    }
    
    # Trap termination signals
    trap cleanup SIGINT SIGTERM
    
    # Wait for the frontend process
    wait $FRONTEND_PID
else
    echo "Frontend directory not found at $(pwd)/frontend"
    echo "Please make sure you're running this script from the project root directory."
    exit 1
fi 