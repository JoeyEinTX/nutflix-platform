#!/usr/bin/env python3
"""
Safe Flask Test - Start Flask in background and test it
"""

import subprocess
import time
import requests
import signal
import os

def test_flask_safely():
    print("🧪 Starting Flask server in background...")
    
    # Start Flask in background
    flask_process = subprocess.Popen(
        ['python3', 'dashboard/app_with_react.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    print("⏳ Waiting 5 seconds for server to start...")
    time.sleep(5)
    
    # Check if process is still running
    if flask_process.poll() is not None:
        print("❌ Flask process died!")
        stdout, stderr = flask_process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return
    
    print("✅ Flask process is running")
    
    try:
        # Test basic connectivity
        print("🔍 Testing server connectivity...")
        response = requests.get('http://localhost:8000/api/status', timeout=5)
        print(f"✅ Server responds: {response.status_code}")
        
        # Test sightings API
        print("🔍 Testing sightings API...")
        response = requests.get('http://localhost:8000/api/sightings', timeout=5)
        print(f"✅ Sightings API responds: {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    finally:
        print("🛑 Stopping Flask server...")
        flask_process.terminate()
        flask_process.wait()
        print("✅ Flask server stopped")

if __name__ == '__main__':
    test_flask_safely()
