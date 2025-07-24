# 🐿️ Nutflix Platform - Project Structure

**Generated:** July 24, 2025  
**Purpose:** Complete project overview for sharing with ChatGPT or team members

## 📁 Root Directory Structure

```
nutflix-platform/
├── 📄 Configuration & Documentation
│   ├── .gitmodules                      # Git submodule configuration
│   ├── COPILOT_PI_PROMPT.md            # Pi deployment context for Copilot
│   ├── GUI_INTEGRATION_STRATEGY.md      # Strategy for GUI submodule integration
│   ├── INTEGRATION_GUIDE.md             # React + Flask integration guide
│   ├── PI_DEPLOYMENT.md                 # Complete Pi deployment instructions
│   ├── PI_GUI_SUBMODULE_SETUP.md       # Detailed GUI submodule setup for Pi
│   ├── REACT_INTEGRATION_COMPLETE.md    # React integration completion guide
│   ├── README.md                        # Main project documentation
│   ├── requirements-dev.txt             # Development dependencies
│   └── requirements.txt                 # Production/Pi dependencies
│
├── 🔧 Scripts & Tools
│   ├── debug_setup.sh                   # Pi debugging setup script
│   ├── debug_test.py                    # System debug test
│   ├── demo_settings.py                 # Settings system demonstration
│   ├── manage_gui.sh                    # GUI submodule management
│   ├── quick_start.py                   # Quick development startup
│   ├── setup_react_integration.sh      # React integration automation
│   ├── start_backend.sh                 # Backend startup script
│   ├── start_frontend.sh                # Frontend startup script
│   └── test_status.py                   # System status test
│
├── 🧠 Core Modules (Shared across all devices)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── notification_system.py       # System notifications
│   │   ├── recording_engine.py          # Main recording controller
│   │   ├── stream_server.py             # Video streaming server
│   │   ├── upload_manager.py            # File upload management
│   │   │
│   │   ├── ai/                          # AI & Machine Learning
│   │   │   ├── __init__.py
│   │   │   └── local_ai.py              # Local AI inference
│   │   │
│   │   ├── audio/                       # Audio Processing
│   │   │   ├── __init__.py
│   │   │   └── audio_recorder.py        # Audio capture & recording
│   │   │
│   │   ├── camera/                      # Camera Management
│   │   │   ├── __init__.py
│   │   │   └── camera_manager.py        # Multi-camera controller
│   │   │
│   │   ├── config/                      # Legacy Configuration Management
│   │   │   ├── __init__.py
│   │   │   ├── config_manager.py        # Device config loader (legacy)
│   │   │   └── settings_manager.py      # Runtime settings (legacy)
│   │   │
│   │   ├── settings/                    # Modern Settings System
│   │   │   ├── __init__.py
│   │   │   ├── settings_manager.py      # Comprehensive settings manager
│   │   │   ├── default_settings.yaml    # Default configuration schema
│   │   │   └── integration.py           # Legacy compatibility bridge
│   │   │
│   │   ├── motion/                      # Motion Detection
│   │   │   ├── __init__.py
│   │   │   └── motion_detector.py       # OpenCV motion detection
│   │   │
│   │   ├── storage/                     # File Management
│   │   │   ├── __init__.py
│   │   │   └── file_manager.py          # Storage & cleanup
│   │   │
│   │   └── utils/                       # Utilities
│   │       ├── __init__.py
│   │       ├── clip_coordinator.py      # Video clip coordination
│   │       ├── sensor_reader.py         # Environmental sensors
│   │       └── stitch_clips.py          # Video stitching
│   │
├── 🤖 Device Types (Independent edge devices)
│   ├── devices/
│   │   ├── nutpod/                      # Full-featured Pi 5 device
│   │   │   ├── config.json              # NutPod configuration
│   │   │   └── main.py                  # NutPod main application
│   │   │
│   │   ├── scoutpod/                    # Portable battery device
│   │   │   ├── config.json              # ScoutPod configuration
│   │   │   └── main.py                  # ScoutPod main application
│   │   │
│   │   └── groundpod/                   # Ground-level thermal device
│   │       ├── config.json              # GroundPod configuration
│   │       └── main.py                  # GroundPod main application
│   │
├── 🌐 Web Interface (Development environment only)
│   ├── dashboard/                       # Flask Backend API
│   │   ├── app.py                       # Basic Flask app
│   │   ├── app_simple.py                # Simplified version
│   │   ├── app_with_react.py            # React-integrated Flask app
│   │   ├── README.md                    # Dashboard documentation
│   │   │
│   │   ├── routes/                      # API Endpoints
│   │   │   ├── clips.py                 # Video clips API
│   │   │   ├── dashboard.py             # Dashboard API
│   │   │   ├── health.py                # Health check API
│   │   │   ├── research.py              # Research data API
│   │   │   ├── settings.py              # Settings API
│   │   │   └── stream.py                # Streaming API
│   │   │
│   │   ├── services/                    # Business Logic
│   │   │   └── analytics.py             # Analytics service
│   │   │
│   │   ├── static/                      # Static Assets
│   │   │   ├── research.css
│   │   │   └── style.css
│   │   │
│   │   └── templates/                   # HTML Templates
│   │       ├── base.html
│   │       ├── clips.html
│   │       ├── dashboard.html
│   │       ├── settings.html
│   │       └── research/
│   │           ├── index.html
│   │           ├── sightings.html
│   │           └── trends.html
│   │
│   └── frontend/                        # React Frontend
│       ├── package.json                 # React dependencies
│       ├── README.md                    # Frontend documentation
│       │
│       ├── public/                      # Static Files
│       │   └── index.html               # React entry point
│       │
│       └── src/                         # React Source Code
│           ├── App.css                  # Main styles
│           ├── App.js                   # Main React component
│           ├── index.css                # Global styles
│           ├── index.js                 # React entry point
│           │
│           ├── components/              # React Components
│           │   ├── Clips.js             # Video clips component
│           │   ├── Dashboard.js         # Dashboard component
│           │   ├── Research.js          # Research component
│           │   └── Settings.js          # Settings component
│           │
│           └── services/                # API Services
│               └── api.js               # API communication layer
│
├── 📚 Documentation
│   ├── docs/
│   │   └── architecture.md              # System architecture documentation
│   │
│   └── scripts/
│       └── README.md                    # Scripts documentation
│
└── 🔧 Utilities
    ├── utils/
    │   └── env_sensor.py                # Environmental sensor utilities
    │
    └── project_structure.txt            # This file (auto-generated)
```

## 🏗️ Architecture Overview

### **Core Philosophy:**
- **Modular Design**: Shared `core/` modules across all devices
- **Edge Processing**: Each device operates independently
- **Device-Specific**: Different capabilities per device type
- **Development Separation**: GUI/dashboard only on development platform

### **Device Types:**
- **NutPod**: Full-featured (dual cameras, audio, streaming, SSD storage)
- **ScoutPod**: Portable (single camera, battery, no streaming)
- **GroundPod**: Specialized (thermal camera, ground-level, minimal storage)

### **Deployment Strategy:**
- **NutPodHero**: Development platform + reference NutPod
- **Other Pis**: Lightweight device deployments only
- **Independent Updates**: Each device manages itself
- **No Central Hub**: True distributed edge processing

## 🎯 Key Points for ChatGPT Context

1. **This is NOT a centralized system** - each device is autonomous
2. **The GUI/dashboard is for development only** - not deployed to production devices
3. **Core modules are shared** but each device type has different capabilities
4. **Scaling challenge**: Deploy lightweight device code to multiple Pis
5. **Current issue**: Development environment mixed with device runtime

## 📦 What Gets Deployed to Production Devices

**Deployed (lightweight):**
- `core/` modules (camera, motion, audio, etc.)
- `devices/[type]/` specific configuration and main.py
- Minimal runtime dependencies
- Device-specific config.json

**NOT Deployed (development only):**
- `frontend/` React development
- `dashboard/` Flask development environment
- `docs/` documentation
- Development scripts and tools
- GUI submodule

This structure supports true edge computing with autonomous wildlife monitoring devices!
