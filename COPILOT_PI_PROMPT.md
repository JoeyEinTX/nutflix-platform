# Nutflix Platform - Pi Copilot Setup Prompt

Copy and paste this into Copilot when setting up on your Raspberry Pi:

---

I'm working on the **Nutflix Platform** - a wildlife monitoring system for Raspberry Pi that captures, analyzes, and displays footage of animals like squirrels, birds, and raccoons.

## Project Overview:
- **Purpose**: Wildlife monitoring with AI species classification
- **Hardware**: Raspberry Pi 5 with dual cameras, BME280 sensor, audio recording
- **Tech Stack**: Python Flask backend + React frontend
- **AI**: TensorFlow Lite for species recognition
- **Features**: Motion detection, video recording, live streaming, web dashboard

## Current Architecture:
```
nutflix-platform/
├── frontend/              # React web interface (port 3000 dev, served by Flask in prod)
├── dashboard/             # Flask API backend (port 8000)
│   └── app_with_react.py  # Main server with CORS for React
├── core/                  # Shared modules
│   ├── camera/           # Camera management (picamera2)
│   ├── audio/            # Audio recording
│   ├── ai/               # Species classification
│   ├── motion/           # Motion detection
│   └── storage/          # File management
├── devices/nutpod/       # Pi-specific configuration
└── requirements.txt      # Pi-optimized dependencies
```

## Key Technologies:
- **Flask + Flask-CORS**: Web framework and API
- **React**: Frontend dashboard with routing
- **picamera2**: Pi camera interface
- **OpenCV**: Computer vision and motion detection
- **TensorFlow Lite**: Lightweight AI inference on Pi
- **BME280**: Environmental sensor (temperature, humidity)
- **sounddevice**: Audio recording
- **NumPy/SciPy**: Numerical processing

## Current Status:
✅ Core modules implemented
✅ React frontend integrated with Flask backend
✅ Pi-optimized requirements (tflite-runtime vs tensorflow)
✅ CORS configured for React development
✅ Production deployment scripts ready
✅ Systemd service configuration available

## Immediate Goals:
1. **Deploy to Pi**: Clone repo, install deps, test hardware integration
2. **Camera Setup**: Configure dual camera system with picamera2
3. **AI Integration**: Load species classification models
4. **React Integration**: Migrate existing React GUI components
5. **Hardware Testing**: Verify sensors, audio, motion detection

## Development Workflow:
- **Backend**: `./start_backend.sh` (Flask serves API + React build)
- **Frontend Dev**: `cd frontend && npm start` (React dev server)
- **Production**: Single Flask server serves everything on port 8000

## Pi-Specific Considerations:
- Uses tflite-runtime instead of full TensorFlow (10x faster)
- picamera2 for camera access (not opencv camera)
- I2C enabled for BME280 sensor
- Hardware-accelerated video encoding
- Systemd service for auto-start

## Files to Focus On:
- `dashboard/app_with_react.py` - Main Flask application
- `core/camera/camera_manager.py` - Camera interface
- `frontend/src/` - React components and API integration
- `requirements.txt` - Pi-optimized dependencies
- `PI_DEPLOYMENT.md` - Complete setup guide

Please help me with Pi deployment, hardware integration, performance optimization, and any issues that come up during the setup process. The goal is a production-ready wildlife monitoring system that can run 24/7 on the Pi.

---

This prompt gives Copilot full context about your project structure, current state, and what you're trying to accomplish on the Pi!
