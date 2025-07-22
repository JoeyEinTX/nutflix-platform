#!/bin/bash
# Nutflix Platform - Raspberry Pi Debug Setup Script
# Run this script on your Pi to set up the environment and start debugging

echo "🐿️ Nutflix Platform - Pi Debug Setup"
echo "====================================="

# Check if we're on a Pi
ARCH=$(uname -m)
echo "Architecture: $ARCH"

if [[ "$ARCH" == arm* ]] || [[ "$ARCH" == aarch64 ]]; then
    echo "✅ Running on ARM architecture (likely Raspberry Pi)"
    IS_PI=true
else
    echo "⚠️  Not on ARM architecture - some hardware features won't work"
    IS_PI=false
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p recordings logs config

# Check Python version
echo "🐍 Python version:"
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install basic dependencies first
echo "📦 Installing basic dependencies..."
pip install flask numpy python-dotenv pyyaml aiofiles

# Pi-specific installations
if [ "$IS_PI" = true ]; then
    echo "🥧 Installing Raspberry Pi specific packages..."
    
    # Enable camera if not already enabled
    echo "📷 Checking camera status..."
    if ! grep -q "^camera_auto_detect=1" /boot/config.txt 2>/dev/null; then
        echo "⚠️  Camera may not be enabled. You may need to run 'sudo raspi-config' and enable camera"
    fi
    
    # Install Pi-specific packages
    pip install picamera2 || echo "⚠️  picamera2 install failed - may need system packages"
    
    # Try to install other hardware packages
    pip install adafruit-circuitpython-bme280 adafruit-blinka || echo "⚠️  Adafruit packages failed"
    pip install sounddevice scipy || echo "⚠️  Audio packages failed"
    
    # Check for video devices
    echo "📷 Video devices found:"
    ls -la /dev/video* 2>/dev/null || echo "No video devices found"
    
    # Check for audio devices
    echo "🔊 Audio devices:"
    aplay -l 2>/dev/null || echo "No audio devices found or alsa-utils not installed"
    
    # Check GPIO
    echo "📌 GPIO status:"
    if [ -d "/sys/class/gpio" ]; then
        echo "✅ GPIO interface available"
    else
        echo "❌ GPIO interface not found"
    fi
    
else
    echo "💻 Installing development alternatives..."
    pip install opencv-python  # For non-Pi systems
fi

echo ""
echo "🔍 Hardware Detection Results:"
echo "=============================="

# Test imports
echo "🧪 Testing core module imports..."
python3 << 'EOF'
import sys
import os

# Add current directory to Python path
sys.path.insert(0, '/workspaces/nutflix-platform')

modules_to_test = [
    'core.config.config_manager',
    'core.camera.camera_manager', 
    'core.motion.motion_detector',
    'core.recording.recording_engine',
    'core.stream.stream_server',
    'core.audio.audio_recorder'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module}: {e}")
    except Exception as e:
        print(f"⚠️  {module}: {e}")
EOF

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Fix any import errors shown above"
echo "2. Run: python3 debug_test.py"
echo "3. Run: python3 devices/nutpod/main.py"
echo "4. Access dashboard at: http://localhost:8000"
echo ""
echo "🛠️  Debugging completed!"
