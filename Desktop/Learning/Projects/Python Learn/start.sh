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
kill_process_on_port 8000  # Backend port
kill_process_on_port 3000  # Frontend port (if exists)

# Start the backend server in the background
echo "Starting FastAPI backend server..."
python run_backend.py &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 2

# Check if frontend exists and start it if possible
if [ -d "python-learning-platform/frontend" ]; then
    echo "Starting Next.js frontend..."
    cd python-learning-platform/frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ../..
    
    echo ""
    echo "====================================================="
    echo "Python Learning Platform running!"
    echo "Frontend: http://localhost:3000 (opening in browser)"
    echo "Backend: http://localhost:8000"
    echo "Press Ctrl+C to stop all servers"
    echo "====================================================="
    echo ""
    
    # Open browser after a short delay to ensure frontend is ready
    sleep 3
    open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null || start http://localhost:3000 2>/dev/null || echo "Could not open browser automatically"
    
    # Function to handle termination signals with frontend
    function cleanup_all {
        echo "Stopping all servers..."
        kill $BACKEND_PID 2>/dev/null
        kill $FRONTEND_PID 2>/dev/null
        exit
    }
    
    # Trap termination signals
    trap cleanup_all SIGINT SIGTERM
    
    # Wait for both processes
    wait $BACKEND_PID $FRONTEND_PID
else
    echo ""
    echo "====================================================="
    echo "Python Learning Platform backend running!"
    echo "Backend: http://localhost:8000 (opening in browser)"
    echo "Frontend not found in expected location."
    echo "Press Ctrl+C to stop the server"
    echo "====================================================="
    echo ""
    
    # Open browser to backend API
    sleep 1
    open http://localhost:8000 2>/dev/null || xdg-open http://localhost:8000 2>/dev/null || start http://localhost:8000 2>/dev/null || echo "Could not open browser automatically"
    
    # Function to handle termination signals
    function cleanup {
        echo "Stopping servers..."
        kill $BACKEND_PID
        exit
    }
    
    # Trap termination signals
    trap cleanup SIGINT SIGTERM
    
    # Wait for the backend process
    wait $BACKEND_PID
fi 