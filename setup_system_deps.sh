#!/bin/bash
# Nutflix Platform - System Dependencies Setup
# Run this script to install all required system packages for Raspberry Pi

set -e  # Exit on any error

echo "🐿️ Setting up Nutflix Platform system dependencies..."

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Essential system packages
echo "🔧 Installing essential packages..."
sudo apt install -y \
    git \
    curl \
    wget \
    htop \
    vim \
    build-essential

# Python development packages
echo "🐍 Installing Python dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

# Camera and multimedia support
echo "📹 Installing camera and multimedia packages..."
sudo apt install -y \
    libcamera-apps \
    libcamera-dev \
    python3-numpy \

# Audio packages
echo "🔊 Installing audio packages..."
sudo apt install -y \
    pulseaudio \
    alsa-utils \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev

# I2C and GPIO support
echo "🔌 Installing hardware interface packages..."
sudo apt install -y \
    i2c-tools \
    python3-smbus \
    python3-gpiozero

# UI and Font support for proper dashboard display
echo "🎨 Installing UI and font packages..."
sudo apt install -y \
    fonts-noto-color-emoji \
    fonts-symbola \
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig

# Node.js for React frontend
echo "⚛️ Installing Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
else
    echo "Node.js already installed: $(node --version)"
fi

# Refresh font cache
echo "🔄 Refreshing font cache..."
sudo fc-cache -fv

echo "✅ System dependencies installation complete!"
echo ""
echo "Next steps:"
echo "1. Run: python3 -m venv .venv"
echo "2. Run: source .venv/bin/activate"
echo "3. Run: pip install -r requirements.txt"
echo "4. Run: cd frontend && npm install && cd .."
echo "5. Configure Pi hardware: sudo raspi-config"
echo "6. Start platform: ./start_backend.sh"
