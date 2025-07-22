# 🐿️ Nutflix Platform

**Nutflix** is a modular, scalable wildlife monitoring system for Raspberry Pi, designed to capture, analyze, and share footage of animals like squirrels, birds, raccoons, and more.

This repository contains the **shared core codebase** that powers all Nutflix-based devices:

- **NutPod** – the modular electronics brain (Pi 5 with dual cameras, SSD, sensors)
- **ScoutPod** – portable, battery-powered field unit
- **GroundPod** – low-level/ground view with thermal vision
- Future Pods – modular support built in

---

## 📁 Project Structure

```bash
nutflix-platform/
├── core/                # Shared code: cameras, audio, AI, motion, config
├── devices/             # Per-device entrypoints
│   ├── nutpod/
│   ├── scoutpod/
│   └── groundpod/
├── dashboard/           # Local dashboard (Flask or FastAPI)
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
pip install -r requirements.txt
```

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
| Dashboard UI     | 🚧 Planning    |
| Cloud sharing    | ❌ Later phase |

---

## 💬 Maintainer Notes

This repo is the **canonical base** for all Nutflix hardware/software platforms.

Use this repo to:

- Add or improve shared modules
- Scaffold new devices
- Keep all device behavior consistent
