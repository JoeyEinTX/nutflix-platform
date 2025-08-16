#!/bin/bash
echo "🧹 Cleaning up React development servers..."

# Kill any existing React/Vite processes
pkill -f "vite"
pkill -f "npm start"
pkill -f "react-scripts"

# Wait a moment for processes to terminate
sleep 2

echo "✅ Frontend processes cleaned up"
echo "🚀 Starting fresh React frontend on port 3000..."

cd frontend
npm start
