#!/bin/bash

# Nutflix Platform - React Integration Setup Script
# This script helps you set up the React frontend integration

set -e

echo "🐿️ Nutflix Platform - React Integration Setup"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "dashboard" ]; then
    echo "❌ Error: Please run this script from the nutflix-platform root directory"
    exit 1
fi

echo "📂 Setting up frontend directory..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js $(node --version) detected"
echo "✅ npm $(npm --version) detected"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend

if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in frontend directory"
    exit 1
fi

npm install

echo "✅ Frontend dependencies installed"

# Check if Python backend dependencies are installed
cd ..
echo "🐍 Checking Python backend dependencies..."

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

# Check if flask-cors is available
python3 -c "import flask_cors" 2>/dev/null || {
    echo "⚠️  flask-cors not found. Installing backend dependencies..."
    pip install -r requirements.txt
}

echo "✅ Backend dependencies ready"

# Create startup scripts
echo "📝 Creating startup scripts..."

# Backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Nutflix Backend (Flask API)..."
echo "Backend will run on: http://localhost:8000"
echo "Press Ctrl+C to stop"
python3 dashboard/app_with_react.py
EOF

# Frontend startup script  
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Nutflix Frontend (React)..."
echo "Frontend will run on: http://localhost:3000"
echo "Press Ctrl+C to stop"
cd frontend
npm start
EOF

# Make scripts executable
chmod +x start_backend.sh start_frontend.sh

echo "✅ Startup scripts created"

# Show next steps
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Start the backend:  ./start_backend.sh"
echo "2. In another terminal, start the frontend: ./start_frontend.sh"
echo "3. Open your browser to: http://localhost:3000"
echo ""
echo "📖 For detailed integration instructions, see: INTEGRATION_GUIDE.md"
echo ""
echo "🔧 To integrate your existing React code:"
echo "   - Copy your components to: frontend/src/components/"
echo "   - Update API calls to use: services/api.js"
echo "   - Test with the running backend"
echo ""
echo "Happy coding! 🐿️"
