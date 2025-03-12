#!/bin/bash

# Check if backend directory exists
if [ ! -d "backend" ]; then
  echo "Error: 'backend' directory not found. Checking if we need to be in a parent directory..."
  # Try a different directory structure
  if [ -d "../backend" ]; then
    cd ..
    echo "Changed to parent directory."
  else
    echo "Error: Could not find backend directory."
    exit 1
  fi
fi

# Check if virtual environment exists, create if not
if [ ! -d "backend/venv" ]; then
  echo "Creating Python virtual environment..."
  cd backend
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  cd ..
else
  echo "Using existing virtual environment."
fi

# Kill any processes already using our ports
echo "Checking for processes using ports 8000 and 3000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start the backend server in the background
echo "Starting FastAPI backend server..."
cd backend
source venv/bin/activate
python run_backend.py &
BACKEND_PID=$!
cd ..

# Start the frontend server in the background
echo "Starting Next.js frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Function to handle termination signals
function cleanup {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit
}

# Trap termination signals
trap cleanup SIGINT SIGTERM

echo ""
echo "====================================================="
echo "Python Learning Platform running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Press Ctrl+C to stop both servers"
echo "====================================================="
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 