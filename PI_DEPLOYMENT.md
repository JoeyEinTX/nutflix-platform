# 🐿️ Nutflix Platform - Raspberry Pi Deployment Guide

## Quick Start for Pi Deployment

### 1. Clone to Raspberry Pi
```bash
git clone https://github.com/JoeyEinTX/nutflix-platform.git
cd nutflix-platform
```

### 2. Install System Dependencies
```bash
# Install all required system packages (including emoji fonts!)
./setup_system_deps.sh
```

### 3. Setup Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Setup React Frontend
```bash
# Frontend packages (Node.js already installed by setup script)
cd frontend
npm install
npm run build
cd ..
```

### 5. Configure for Pi Hardware
```bash
# Enable camera
sudo raspi-config
# -> Interface Options -> Camera -> Enable

# Enable I2C for sensors
sudo raspi-config  
# -> Interface Options -> I2C -> Enable

# Reboot
sudo reboot
```

### 6. Start the Platform
```bash
# Start backend (serves React app too)
./start_backend.sh

# Access at: http://[pi-ip]:8000/app
```

## Production Setup

### Auto-start on Boot
```bash
# Create systemd service
sudo nano /etc/systemd/system/nutflix.service
```

Add:
```ini
[Unit]
Description=Nutflix Wildlife Platform
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/nutflix-platform
Environment=PATH=/home/pi/nutflix-platform/.venv/bin
ExecStart=/home/pi/nutflix-platform/.venv/bin/python dashboard/app_with_react.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable nutflix
sudo systemctl start nutflix
```

### Access Points
- **Web Interface**: http://[pi-ip]:8000/app
- **API**: http://[pi-ip]:8000/api/*
- **Health Check**: http://[pi-ip]:8000/health

## Hardware Configuration

### Camera Setup
- Connect camera module to Pi camera port
- Enable camera in raspi-config
- Test: `libcamera-hello`

### Sensor Setup (BME280)
- Connect via I2C (GPIO pins 3/5)
- Enable I2C in raspi-config
- Test: `i2cdetect -y 1`

### Audio Setup
- USB microphone or Pi audio hat
- Test: `arecord -l`

## File Structure for Pi
```
nutflix-platform/
├── frontend/build/          # React production build
├── dashboard/app_with_react.py  # Main server
├── core/                    # AI, camera, audio modules
├── devices/nutpod/         # Pi-specific config
└── requirements.txt        # Pi-optimized deps
```

## Performance Notes
- **tflite-runtime** instead of tensorflow (10x faster on Pi)
- **Lightweight OpenCV** for better performance
- **React build** served by Flask (single port)
- **Systemd service** for reliability

Ready for Pi deployment! 🚀
