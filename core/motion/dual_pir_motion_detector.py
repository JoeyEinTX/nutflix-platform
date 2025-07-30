"""
Dual PIR Motion Detector - Hardware-based motion detection for NutFlix
Supports separate PIR sensors for CritterCam and NestCam
"""

import time
import threading
from datetime import datetime
from typing import Callable, Optional, Dict

# Try to import GPIO, fallback for development
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    print("⚠️  RPi.GPIO not available - PIR detector in simulation mode")
    GPIO_AVAILABLE = False

class DualPIRMotionDetector:
    """Dual PIR sensor-based motion detection for both cameras"""
    
    def __init__(self, motion_callback: Optional[Callable] = None):
        """
        Initialize dual PIR motion detectors
        
        Args:
            motion_callback: Function to call when motion is detected
                            Receives (camera_name, motion_event) parameters
        """
        self.motion_callback = motion_callback
        self.running = False
        self.detection_threads = {}
        
        # PIR sensor configuration (optimized for AM312 sensors)
        self.sensors = {
            'CritterCam': {
                'gpio_pin': 18,
                'last_detection': 0,
                'cooldown': 3.0,  # AM312 has ~2s output pulse, reduced cooldown
                'last_state': False  # Track state changes for edge detection
            },
            'NestCam': {
                'gpio_pin': 12,  # Changed from 24 to 12 (Pin 32) - avoiding all conflicts
                'last_detection': 0,
                'cooldown': 3.0,
                'last_state': False
            }
        }
        
        if GPIO_AVAILABLE:
            self._setup_gpio()
        else:
            print("[DualPIRMotionDetector] Running in simulation mode")
    
    def _setup_gpio(self):
        """Setup GPIO pins for both PIR sensors"""
        try:
            GPIO.setmode(GPIO.BCM)
            
            for camera_name, config in self.sensors.items():
                GPIO.setup(config['gpio_pin'], GPIO.IN)
                print(f"[DualPIRMotionDetector] ✓ {camera_name} PIR sensor on GPIO {config['gpio_pin']}")
                
        except Exception as e:
            print(f"[DualPIRMotionDetector] ❌ GPIO setup failed: {e}")
    
    def start_detection(self):
        """Start monitoring both PIR sensors"""
        if self.running:
            print("[DualPIRMotionDetector] Already running")
            return
            
        self.running = True
        
        # Start detection thread for each camera
        for camera_name in self.sensors.keys():
            thread = threading.Thread(
                target=self._monitor_pir_sensor, 
                args=(camera_name,), 
                daemon=True
            )
            thread.start()
            self.detection_threads[camera_name] = thread
            
        print("[DualPIRMotionDetector] 🚨 Motion detection started for both cameras")
    
    def stop_detection(self):
        """Stop monitoring PIR sensors"""
        self.running = False
        
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            
        print("[DualPIRMotionDetector] Motion detection stopped")
    
    def _monitor_pir_sensor(self, camera_name: str):
        """Monitor a specific PIR sensor with edge detection for AM312"""
        sensor_config = self.sensors[camera_name]
        gpio_pin = sensor_config['gpio_pin']
        
        print(f"[DualPIRMotionDetector] Monitoring {camera_name} on GPIO {gpio_pin} (AM312 sensor)")
        
        # Debug counter for periodic state reporting
        debug_counter = 0
        
        while self.running:
            try:
                if GPIO_AVAILABLE:
                    current_state = GPIO.input(gpio_pin)
                else:
                    # Simulation mode - random motion every 30-60 seconds
                    import random
                    current_state = random.random() < 0.001  # Very low probability per loop
                
                # Debug: Report current state every 10 seconds
                debug_counter += 1
                if debug_counter % 100 == 0:  # Every ~10 seconds (100 * 0.1s sleep)
                    state_name = "HIGH" if current_state else "LOW"
                    print(f"[DualPIRMotionDetector] 🔍 {camera_name} state: {state_name} (last_state: {sensor_config['last_state']})")
                
                # Edge detection: trigger on LOW to HIGH transition (motion start)
                # TEMP: Also trigger HIGH to LOW for testing stuck sensor
                motion_detected = False
                
                if current_state and not sensor_config['last_state']:
                    # Normal LOW→HIGH transition (motion detected)
                    motion_detected = True
                    motion_type = "motion_start"
                elif not current_state and sensor_config['last_state']:
                    # HIGH→LOW transition (motion ended) - temporary for debugging
                    motion_detected = True
                    motion_type = "motion_end"
                
                if motion_detected:
                    current_time = time.time()
                    
                    # Check cooldown period
                    if current_time - sensor_config['last_detection'] > sensor_config['cooldown']:
                        sensor_config['last_detection'] = current_time
                        
                        timestamp = datetime.now()
                        print(f"[DualPIRMotionDetector] 🚨 {motion_type.upper()} on {camera_name} at {timestamp.strftime('%H:%M:%S')} (AM312)")
                        
                        # Create motion event
                        motion_event = {
                            'timestamp': timestamp.isoformat(),
                            'camera_name': camera_name,
                            'sensor_type': 'AM312_PIR',
                            'detection_method': 'hardware_motion_sensor',
                            'trigger_type': 'pir_motion',
                            'gpio_pin': gpio_pin,
                            'motion_type': motion_type
                        }
                        
                        # Trigger callback
                        if self.motion_callback:
                            try:
                                self.motion_callback(camera_name, motion_event)
                            except Exception as e:
                                print(f"[DualPIRMotionDetector] ❌ Callback error for {camera_name}: {e}")
                
                # Update last state for edge detection
                sensor_config['last_state'] = current_state
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[DualPIRMotionDetector] ❌ Error monitoring {camera_name}: {e}")
                time.sleep(1)
    
    def test_sensors(self, duration: int = 30):
        """Test both PIR sensors for specified duration"""
        print(f"[DualPIRMotionDetector] 🧪 Testing both sensors for {duration} seconds...")
        print("Wave your hand in front of each sensor...")
        
        if not GPIO_AVAILABLE:
            print("⚠️  GPIO not available - cannot test actual sensors")
            return
        
        start_time = time.time()
        last_print_time = 0
        
        while time.time() - start_time < duration:
            current_time = time.time()
            
            # Check each sensor
            for camera_name, config in self.sensors.items():
                if GPIO.input(config['gpio_pin']):
                    elapsed = current_time - start_time
                    print(f"[DualPIRMotionDetector] ✅ {camera_name} motion detected! ({elapsed:.1f}s)")
                    time.sleep(0.5)  # Prevent spam
            
            # Print status every 10 seconds
            if current_time - last_print_time > 10:
                elapsed = current_time - start_time
                print(f"[DualPIRMotionDetector] Testing... {elapsed:.0f}s elapsed")
                last_print_time = current_time
            
            time.sleep(0.1)
        
        print("[DualPIRMotionDetector] 🏁 Test complete")
    
    def get_sensor_status(self) -> Dict:
        """Get current status of both sensors"""
        status = {
            'running': self.running,
            'sensors': {}
        }
        
        for camera_name, config in self.sensors.items():
            current_state = False
            if GPIO_AVAILABLE:
                try:
                    current_state = GPIO.input(config['gpio_pin'])
                except:
                    pass
                    
            status['sensors'][camera_name] = {
                'gpio_pin': config['gpio_pin'],
                'current_state': current_state,
                'last_detection': config['last_detection'],
                'cooldown': config['cooldown']
            }
        
        return status

# Test function
def test_callback(camera_name, event):
    print(f"🎯 Motion callback: {camera_name} -> {event}")

if __name__ == "__main__":
    # Test the dual PIR sensors
    detector = DualPIRMotionDetector(callback=test_callback)
    
    try:
        print("Starting detection test...")
        detector.start_detection()
        detector.test_sensors(30)
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        
    finally:
        detector.stop_detection()
        print("✅ Test cleanup complete")
