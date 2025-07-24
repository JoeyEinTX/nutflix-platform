#!/usr/bin/env python3
"""
Simple camera test using v4l2 to check what cameras are working
"""
import os
import subprocess

def test_v4l2_cameras():
    """Test cameras using v4l2-ctl if available"""
    print("📷 Testing cameras with v4l2...")
    
    # List video devices
    video_devices = []
    for i in range(10):  # Check first 10 video devices
        device = f"/dev/video{i}"
        if os.path.exists(device):
            video_devices.append(device)
    
    print(f"Found {len(video_devices)} video devices:")
    for device in video_devices:
        print(f"  {device}")
    
    # Try to get info about first few devices
    for device in video_devices[:4]:  # Test first 4 devices
        try:
            result = subprocess.run(['v4l2-ctl', '--device', device, '--info'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                print(f"\n✅ {device} info:")
                print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
            else:
                print(f"❌ {device}: Cannot get info")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"⚠️  {device}: v4l2-ctl not available or timeout")
        except Exception as e:
            print(f"❌ {device}: Error - {e}")

if __name__ == "__main__":
    print("🐿️ NutFlix Camera Hardware Test")
    print("=" * 35)
    test_v4l2_cameras()
