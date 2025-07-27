"""
PIR Motion Detector - Hardware-based motion detection for NutFlix
Replaces camera-based motion detection to avoid hardware conflicts
"""

import RPi.GPIO as GPIO
import time
import threading
from datetime import datetime
from typing import Callable, Optional

class PIRMotionDetector:
    """PIR sensor-based motion detection"""
    
    def __init__(self, pir_pin: int = 18, callback: Optional[Callable] = None):
        self.pir_pin = pir_pin
        self.callback = callback
        self.running = False
        self.last_detection_time = 0
        self.detection_cooldown = 5.0  # Seconds between detections
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pir_pin, GPIO.IN)
        
        print(f"[PIRMotionDetector] Initialized on GPIO {self.pir_pin}")
    
    def start_detection(self):
        """Start monitoring PIR sensor"""
        self.running = True
        detection_thread = threading.Thread(target=self._monitor_pir, daemon=True)
        detection_thread.start()
        print("[PIRMotionDetector] Motion detection started")
    
    def stop_detection(self):
        """Stop monitoring PIR sensor"""
        self.running = False
        GPIO.cleanup()
        print("[PIRMotionDetector] Motion detection stopped")
    
    def _monitor_pir(self):
        """Monitor PIR sensor in background thread"""
        while self.running:
            try:
                # Read PIR sensor state
                if GPIO.input(self.pir_pin):
                    current_time = time.time()
                    
                    # Check cooldown to prevent spam
                    if current_time - self.last_detection_time > self.detection_cooldown:
                        self.last_detection_time = current_time
                        
                        print(f"[PIRMotionDetector] 🚨 Motion detected at {datetime.now().strftime('%H:%M:%S')}")
                        
                        # Trigger callback if provided
                        if self.callback:
                            motion_event = {
                                'timestamp': datetime.now().isoformat(),
                                'sensor_type': 'PIR',
                                'detection_method': 'hardware',
                                'camera': 'PIR_Triggered'  # Will be overridden by recording logic
                            }
                            self.callback(motion_event)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[PIRMotionDetector] Error: {e}")
                time.sleep(1)
    
    def test_sensor(self, duration: int = 30):
        """Test PIR sensor for specified duration"""
        print(f"[PIRMotionDetector] Testing sensor for {duration} seconds...")
        print("Wave your hand in front of the sensor...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            if GPIO.input(self.pir_pin):
                print(f"[PIRMotionDetector] ✅ Motion detected! ({time.time() - start_time:.1f}s)")
                time.sleep(1)  # Prevent spam
            time.sleep(0.1)
        
        print("[PIRMotionDetector] Test complete")

if __name__ == "__main__":
    # Test the PIR sensor
    def test_callback(event):
        print(f"Callback triggered: {event}")
    
    detector = PIRMotionDetector(callback=test_callback)
    try:
        detector.test_sensor(30)
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        detector.stop_detection()
