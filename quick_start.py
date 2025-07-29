#!/usr/bin/env python3
"""
Nutflix Platform - Quick Start Script for Raspberry Pi
This will help you get the system running quickly
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_command(cmd, description="", check=True):
    """Run a command and handle output"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   stderr: {e.stderr.strip()}")
        return False

def check_pi_environment():
    """Check if we're on a Pi and what hardware is available"""
    print("\n🥧 Raspberry Pi Environment Check")
    print("=" * 50)
    
    # Check architecture
    arch = os.uname().machine
    print(f"Architecture: {arch}")
    
    is_pi = arch.startswith('arm') or arch.startswith('aarch64')
    if is_pi:
        print("✅ Running on Raspberry Pi")
    else:
        print("⚠️  Not on Raspberry Pi - some features won't work")
    
    return is_pi

def setup_environment():
    """Set up the Python environment"""
    print("\n🐍 Setting up Python Environment")
    print("=" * 50)
    
    # Create venv if needed
    if not os.path.exists('.venv'):
        run_command("python3 -m venv .venv", "Creating virtual environment")
    
    # Install basic requirements
    run_command("source .venv/bin/activate && pip install --upgrade pip", "Upgrading pip")
    
    # Install packages that should work everywhere
    basic_packages = [
        "flask", "numpy", "python-dotenv", "pyyaml", "aiofiles"
    ]
    
    for package in basic_packages:
        run_command(f"source .venv/bin/activate && pip install {package}", f"Installing {package}", check=False)

def start_dashboard():
    """Start the dashboard in development mode"""
    print("\n🌐 Starting Dashboard")
    print("=" * 50)
    
    print("Starting dashboard on http://localhost:8000")
    print("Press Ctrl+C to stop")
    
    os.environ['PYTHONPATH'] = str(Path.cwd())
    
    try:
        subprocess.run([
            "bash", "-c", 
            "cd /workspaces/nutflix-platform && source .venv/bin/activate && python3 dashboard/app.py"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")

def start_nutpod():
    """Start the main NutPod application"""
    print("\n🐿️ Starting NutPod Application")
    print("=" * 50)
    
    print("Starting NutPod main application...")
    print("Press Ctrl+C to stop")
    
    os.environ['PYTHONPATH'] = str(Path.cwd())
    
    try:
        subprocess.run([
            "bash", "-c",
            "cd /workspaces/nutflix-platform && source .venv/bin/activate && python3 devices/nutpod/main.py"
        ])
    except KeyboardInterrupt:
        print("\n👋 NutPod stopped")

def main():
    """Main quick start function"""
    print("🐿️ Nutflix Platform - Quick Start")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Check environment
    is_pi = check_pi_environment()
    
    # Setup
    setup_environment()
    
    # Show options
    print("\n🎯 What would you like to do?")
    print("1. Run system status test")
    print("2. Start dashboard only")
    print("3. Start NutPod main application")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                if Path("test_status.py").exists():
                    run_command("source .venv/bin/activate && python3 test_status.py", "Running system status test")
                else:
                    print("❌ test_status.py not found")
                break
            elif choice == "2":
                start_dashboard()
                break
            elif choice == "3":
                start_nutpod()
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("Please enter 1, 2, 3, or 4")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
