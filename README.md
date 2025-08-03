# 🐿️ Nutflix Platform

**Nutflix** is a modular, scalable wildlife monitoring system for Raspberry Pi, designed to capture, analyze, and share footage of animals like squirrels, birds, raccoons, and more.

This repository contains the **shared core codebase** that powers all Nutflix-based devices:

- **NutPod** – the modular electronics brain (Pi 5 with dual cameras, SSD, sensors)
- **ScoutPod** – portable, battery-powered field unit
- **GroundPod** – low-level/ground view with thermal vision
- Future Pods – modular support built in

---

## � Quick Start (Raspberry Pi)

### One-Command Setup
```bash
# Clone and run complete setup
git clone https://github.com/JoeyEinTX/nutflix-platform.git
cd nutflix-platform
./setup_complete.sh
```

### Manual Setup
```bash
# 1. Install system dependencies (includes emoji fonts!)
./setup_system_deps.sh

# 2. Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Setup frontend
cd frontend && npm install && npm run build && cd ..

# 4. Start the platform
./start_backend.sh
```

### Access Dashboard
- **Web Interface**: `http://[your-pi-ip]:8000/app`
- **Backend API**: `http://[your-pi-ip]:8000/api/`

---

## �📁 Project Structure

```bash
nutflix-platform/
├── core/                # Shared code: cameras, audio, AI, motion, config
├── devices/             # Per-device entrypoints
│   ├── nutpod/
│   ├── scoutpod/
│   └── groundpod/
├── frontend/            # React-based web interface
├── dashboard/           # Flask API backend
├── scripts/             # Installers, CLI tools, utilities
├── docs/                # Tech specs, setup guides, architecture
└── README.md
```

---

## 🧠 Features

- Dual-camera support (CritterCam + NestCam)
- Interior audio recording
- Motion detection
- AI-based species classification
- Local file management
- Optional web dashboard
- Modular device configuration
- Designed for edge or cloud

---

## 🚀 Setup (for development)

```bash
git clone https://github.com/JoeyEinTX/nutflix-platform.git
cd nutflix-platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt  # Development dependencies

# Set up React frontend integration
./setup_react_integration.sh
```

## 🥧 Raspberry Pi Deployment

Ready for Pi deployment! See `PI_DEPLOYMENT.md` for complete setup instructions.

**Quick Pi Setup:**
```bash
git clone https://github.com/JoeyEinTX/nutflix-platform.git
cd nutflix-platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # Full Pi requirements
./setup_react_integration.sh
./start_backend.sh
```

Access at: `http://[pi-ip]:8000/app`

## 🌐 React Frontend

The platform now includes a professional React-based web interface:

```bash
# Start backend API (Terminal 1)
./start_backend.sh

# Start React frontend (Terminal 2)  
./start_frontend.sh
```

- Backend API: http://localhost:8000
- React Frontend: http://localhost:3000

See `INTEGRATION_GUIDE.md` for detailed setup and integration instructions.

---

## 🛠️ Devices

Each device has its own folder under `/devices/`, but all rely on shared modules from `/core/`.

| Device     | Description                                                        |
|------------|--------------------------------------------------------------------|
| NutPod     | Modular electronics brain (Pi 5 with dual cameras, SSD, sensors)   |
| ScoutPod   | Field unit, low-power, battery-based                               |
| GroundPod  | Wide or thermal view, ground angle                                 |

---

## 📅 Status

| Component        | Status        |
|------------------|---------------|
| Core modules     | In progress   |
| NutPod config    | 🚧 Setup       |
| ScoutPod support | ❌ Not started |
| Dashboard UI     | ✅ React Ready    |
| Pi Deployment    | ✅ Ready to Clone |
| Cloud sharing    | ❌ Later phase |

---

## 💬 Maintainer Notes

This repo is the **canonical base** for all Nutflix hardware/software platforms.

Use this repo to:

- Add or improve shared modules
- Scaffold new devices
- Keep all device behavior consistent
