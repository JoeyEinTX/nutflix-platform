#!/bin/bash
echo "🚀 Starting Nutflix Backend (Flask API)..."
echo "Backend will run on: http://localhost:8000"
echo "Press Ctrl+C to stop"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 dashboard/app_with_react.py
