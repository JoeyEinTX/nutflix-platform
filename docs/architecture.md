# 🧠 Nutflix Platform Architecture

_Last updated: 2025-07-22_

This document outlines the system architecture, repository structure, and implementation status for the Nutflix Platform — a modular wildlife monitoring system built on Raspberry Pi.

---

## 🐿️ Project Purpose

**Nutflix** is a modular, open wildlife monitoring platform combining intelligent edge processing, multi-sensor input, and scalable architecture. This repository (`nutflix-platform`) is the single source of truth for all core functionality across NutPod, ScoutPod, and GroundPod devices.

---

## 📦 Device Family

| Device     | Description                                                         |
|------------|---------------------------------------------------------------------|
| NutPod     | Modular electronics brain (Pi 5, dual cameras, sensors, SSD)       |
| SquirrelBox| Physical wooden enclosure housing NutPod (chew-safe, weatherproof) |
| ScoutPod   | Portable, battery-powered unit for off-grid field use              |
| GroundPod  | Ground-level thermal or wide-angle observation device              |

---

## 🏗️ Repository Layout

```bash
nutflix-platform/
├── core/
│   ├── camera/              # ✅ camera_manager.py (with mock fallback)
│   ├── motion/              # ✅ motion_detector.py
│   ├── recording/           # ✅ recording_engine.py
│   ├── audio/               # 🔜 audio_recorder.py (planned)
│   ├── ai/                  # 🔜 local_ai.py (planned)
│   ├── config/              # ✅ config_manager.py, ✅ settings_manager.py
│   ├── storage/             # 🔜 file_manager.py (planned)
│   └── utils/               # 🔜 helper tools (logging, timestamping, etc.)
├── devices/
│   ├── nutpod/
│   │   ├── config.json      # ✅ sample config with sensitivity, model path, etc.
│   │   └── main.py          # ✅ functional test harness for live integration
│   ├── scoutpod/            # 🧱 placeholder
│   └── groundpod/           # 🧱 placeholder
├── dashboard/               # 🔜 Flask or FastAPI UI with stream/settings endpoints
├── scripts/                 # 🔜 deploy-pi5.sh, .env.pi5 (planned)
├── docs/                    # 📄 This file, wiring diagrams, etc.
└── README.md                # ✅ Overview + setup instructions
```

---

## ✅ Implemented Modules

| Module                  | Purpose                                                                 |
|-------------------------|-------------------------------------------------------------------------|
| `camera_manager.py`     | Dual camera support (CritterCam + NestCam), with mock fallback          |
| `motion_detector.py`    | OpenCV-based motion detection with cooldown and sensitivity             |
| `config_manager.py`     | Loads device-specific config.json files                                 |
| `settings_manager.py`   | Enables runtime reading/writing of config values                        |
| `recording_engine.py`   | Controls recording logic, threaded capture, filenames, and trigger logs |
| `main.py` (NutPod)      | Event loop that pulls camera frames, checks motion, starts/stops recording |

---

## 🔜 Upcoming Modules

| Planned Module           | Description                                                   |
|--------------------------|---------------------------------------------------------------|
| `audio_recorder.py`      | Record audio from I2S MEMS mic (SPH0645LM4H)                 |
| `stream_server.py`       | Serve MJPEG video stream for CritterCam/NestCam              |
| `file_manager.py`        | Clip rotation, cleanup, folder hierarchy, metadata tagging   |
| `local_ai.py`            | Lightweight TensorFlow Lite model for species identification |
| `dashboard.py`           | Local UI + API for settings, stream, stats                   |
| `deploy-pi5.sh`          | Setup script for Raspberry Pi 5 deployment                   |
| `test/`                  | Unit and integration tests                                   |

---

## 📅 System Status

| Component          | Status        |
|--------------------|---------------|
| Camera Input       | ✅ Done        |
| Motion Detection   | ✅ Done        |
| Audio Input        | 🔜 Pending     |
| AI Classification  | 🔜 Planned     |
| Recording Engine   | ✅ Done        |
| Config/Settings    | ✅ Done        |
| Stream Server      | 🔜 Planned     |
| Dashboard UI       | 🔜 Not started |
| Deploy Scripts     | 🔜 Not started |
| Testing Suite      | 🔜 Not started |

---

## 🧠 Architecture Notes

- Device behavior is defined by `config.json` per device
- `settings_manager.py` enables future runtime updates from a UI
- Mock support ensures the project runs in Codespaces and on non-Pi systems
- All modules are cleanly separated and can be reused by future devices

---

## 💬 Maintainer Notes

This document should be updated alongside key code milestones. All new modules should follow the same pattern of:

- Configurable behavior via JSON
- Reusability across NutPod, ScoutPod, GroundPod
- Clean separation of responsibilities

Version: **v1.2**  
Maintainer: JoeyEinTX  
