#!/bin/bash
# Nutflix Platform - Complete Setup Script
# This script sets up the entire Nutflix platform on a fresh Raspberry Pi

set -e  # Exit on any error

echo "🐿️ Nutflix Platform - Complete Setup"
echo "======================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "    Some hardware features may not work properly"
    echo ""
fi

# 1. System Dependencies
echo "📦 Step 1: Installing system dependencies..."
if [ -f "./setup_system_deps.sh" ]; then
    ./setup_system_deps.sh
else
    echo "❌ setup_system_deps.sh not found! Please run from project root."
    exit 1
fi

echo ""
echo "🐍 Step 2: Setting up Python environment..."

# 2. Python Environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists"
fi

echo "Activating virtual environment and installing packages..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "⚛️ Step 3: Setting up React frontend..."

# 3. Frontend Setup
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Node.js dependencies already installed"
fi

echo "Building React app..."
npm run build
cd ..

echo ""
echo "🔧 Step 4: Hardware configuration check..."

# 4. Hardware Checks
echo "Checking camera support..."
if command -v libcamera-hello &> /dev/null; then
    echo "✅ Camera support installed"
else
    echo "⚠️  Camera support may need configuration"
fi

echo "Checking I2C support..."
if command -v i2cdetect &> /dev/null; then
    echo "✅ I2C tools installed"
else
    echo "⚠️  I2C tools installation may have failed"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Enable Pi hardware features:"
echo "   sudo raspi-config"
echo "   → Interface Options → Camera → Enable"
echo "   → Interface Options → I2C → Enable"
echo ""
echo "2. Reboot Pi:"
echo "   sudo reboot"
echo ""
echo "3. Start the platform:"
echo "   ./start_backend.sh"
echo ""
echo "4. Access dashboard at:"
echo "   http://$(hostname -I | awk '{print $1}'):8000/app"
echo ""
echo "🔍 Troubleshooting:"
echo "   - Check emoji display: fonts should now work in browser"
echo "   - Camera issues: Run 'libcamera-hello' to test"
echo "   - Sensor issues: Run 'python test_bme280_sensor.py'"
