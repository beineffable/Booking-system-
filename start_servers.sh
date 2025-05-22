#!/bin/bash

# Start backend server
echo "Starting backend server..."
cd /home/ubuntu/fitness_platform/backend/fitness_backend
source venv/bin/activate
export FLASK_APP=src/main.py
export FLASK_ENV=development
export STRIPE_SECRET_KEY=sk_test_51OxCvDBXqHVfcDsdfghjklzxcvbnmqwertyuiop1234567890
export STRIPE_PUBLISHABLE_KEY=pk_test_51OxCvDBXqHVfcDsdfghjklzxcvbnmqwertyuiop1234567890
python -m flask run --host=0.0.0.0 --port=5000 &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"

# Wait for backend to initialize
sleep 3

# Start frontend development server
echo "Starting frontend development server..."
cd /home/ubuntu/fitness_platform/frontend/fitness_frontend
npm start &
FRONTEND_PID=$!
echo "Frontend development server started with PID: $FRONTEND_PID"

echo "Both servers are now running. Press Ctrl+C to stop both servers."

# Function to handle script termination
function cleanup {
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  echo "Servers stopped."
  exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

# Keep the script running
wait
