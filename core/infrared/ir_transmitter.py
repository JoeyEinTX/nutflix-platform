"""
IR Transmitter Integration for Simple GPIO IR LED Module
Handles infrared LED control for night vision illumination using direct GPIO control
"""

import time
import threading
from typing import Optional
import logging

# Try to import GPIO libraries for direct IR LED control
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    print("✅ GPIO libraries available for IR transmitter")
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️ GPIO libraries not available - using mock IR interface")

class IRTransmitter:
    """IR LED transmitter for night vision illumination"""
    
    def __init__(self, gpio_pin: int = 23, pwm_frequency: int = 1000):
        """
        Initialize IR transmitter using simple GPIO IR LED module
        
        Your wiring:
        - GND → Pi Ground (Pin 6 or 9)
        - V+  → Pi 5V (Pin 2 or 4) or 3.3V (Pin 1 or 17) 
        - IN  → Pi GPIO 23 (Physical Pin 16)
        
        Args:
            gpio_pin: GPIO pin number for IR LED control (default 23 = Pin 16)
            pwm_frequency: PWM frequency for brightness control (1kHz)
        """
        self.gpio_pin = gpio_pin
        self.pwm_frequency = pwm_frequency
        self.pwm = None
        self.is_on = False
        self.brightness = 0
        
        # Threading for automatic control
        self.auto_mode = False
        self.auto_thread = None
        self.stop_event = threading.Event()
        
        if GPIO_AVAILABLE:
            self._init_real_hardware()
        else:
            print("💡 IR Transmitter initialized in mock mode")
            
    def _init_real_hardware(self):
        """Initialize real GPIO hardware"""
        try:
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup GPIO pin as output
            GPIO.setup(self.gpio_pin, GPIO.OUT)
            
            # Initialize PWM for brightness control
            self.pwm = GPIO.PWM(self.gpio_pin, self.pwm_frequency)
            self.pwm.start(0)  # Start with 0% duty cycle (off)
            
            print(f"💡 IR Transmitter initialized on GPIO {self.gpio_pin}")
            
        except Exception as e:
            print(f"❌ Failed to initialize IR transmitter: {e}")
            self.pwm = None
            
    def turn_on(self, brightness: float = 1.0):
        """
        Turn on IR LED
        
        Args:
            brightness: LED brightness (0.0 to 1.0)
        """
        brightness = max(0.0, min(1.0, brightness))  # Clamp to valid range
        self.brightness = brightness
        
        if GPIO_AVAILABLE and self.pwm:
            try:
                # Convert brightness to PWM duty cycle (0-100%)
                duty_cycle = brightness * 100
                self.pwm.ChangeDutyCycle(duty_cycle)
                    
                self.is_on = True
                print(f"💡 IR LED ON at {brightness*100:.0f}% brightness")
                
            except Exception as e:
                print(f"❌ Failed to turn on IR LED: {e}")
        else:
            # Mock mode
            self.is_on = True
            print(f"💡 [MOCK] IR LED ON at {brightness*100:.0f}% brightness")
            
    def turn_off(self):
        """Turn off IR LED"""
        if GPIO_AVAILABLE and self.pwm:
            try:
                self.pwm.ChangeDutyCycle(0)  # 0% duty cycle = off
                    
                self.is_on = False
                self.brightness = 0
                print("💡 IR LED OFF")
                
            except Exception as e:
                print(f"❌ Failed to turn off IR LED: {e}")
        else:
            # Mock mode
            self.is_on = False
            self.brightness = 0
            print("💡 [MOCK] IR LED OFF")
            
    def set_brightness(self, brightness: float):
        """
        Set IR LED brightness
        
        Args:
            brightness: LED brightness (0.0 to 1.0)
        """
        if self.is_on:
            self.turn_on(brightness)
        else:
            self.brightness = brightness
            
    def pulse(self, duration: float = 0.5, brightness: float = 1.0):
        """
        Pulse IR LED for a specified duration
        
        Args:
            duration: Pulse duration in seconds
            brightness: Peak brightness during pulse
        """
        original_state = self.is_on
        original_brightness = self.brightness
        
        self.turn_on(brightness)
        time.sleep(duration)
        
        if not original_state:
            self.turn_off()
        else:
            self.turn_on(original_brightness)
            
    def start_auto_night_mode(self, light_threshold: float = 0.3):
        """
        Start automatic night mode - turns on IR when it's dark
        
        Args:
            light_threshold: Ambient light threshold (0.0 = dark, 1.0 = bright)
        """
        if self.auto_mode:
            print("💡 Auto night mode already running")
            return
            
        self.auto_mode = True
        self.stop_event.clear()
        
        def auto_control_loop():
            while not self.stop_event.is_set():
                try:
                    # Get ambient light level (would need light sensor integration)
                    light_level = self._get_ambient_light_level()
                    
                    if light_level < light_threshold and not self.is_on:
                        # It's dark and IR is off - turn on
                        brightness = min(1.0, (light_threshold - light_level) * 2)  # Adaptive brightness
                        self.turn_on(brightness)
                        print(f"🌙 Auto night mode: IR ON (light level: {light_level:.2f})")
                        
                    elif light_level > light_threshold * 1.2 and self.is_on:
                        # It's bright enough and IR is on - turn off (with hysteresis)
                        self.turn_off()
                        print(f"☀️ Auto night mode: IR OFF (light level: {light_level:.2f})")
                        
                    time.sleep(10)  # Check every 10 seconds
                    
                except Exception as e:
                    print(f"❌ Auto night mode error: {e}")
                    time.sleep(30)  # Wait longer on error
                    
        self.auto_thread = threading.Thread(target=auto_control_loop, daemon=True)
        self.auto_thread.start()
        
        print("🌙 Auto night mode started")
        
    def stop_auto_night_mode(self):
        """Stop automatic night mode"""
        if not self.auto_mode:
            return
            
        self.auto_mode = False
        self.stop_event.set()
        
        if self.auto_thread:
            self.auto_thread.join(timeout=2)
            
        print("🌙 Auto night mode stopped")
        
    def _get_ambient_light_level(self) -> float:
        """
        Get ambient light level (0.0 = dark, 1.0 = bright)
        
        This would integrate with a light sensor or estimate from camera
        For now, returns mock data based on time of day
        """
        # Mock implementation based on time of day
        current_hour = time.localtime().tm_hour
        
        if 6 <= current_hour <= 18:  # Daytime
            return 0.8
        elif 19 <= current_hour <= 21 or 5 <= current_hour <= 6:  # Twilight
            return 0.4
        else:  # Nighttime
            return 0.1
            
    def get_status(self) -> dict:
        """Get current IR transmitter status"""
        return {
            'is_on': self.is_on,
            'brightness': self.brightness,
            'auto_mode': self.auto_mode,
            'gpio_pin': self.gpio_pin,
            'hardware_available': GPIO_AVAILABLE and self.pwm is not None
        }
        
    def cleanup(self):
        """Clean up GPIO resources"""
        self.stop_auto_night_mode()
        self.turn_off()
        
        if GPIO_AVAILABLE and self.pwm:
            try:
                self.pwm.stop()
                GPIO.cleanup(self.gpio_pin)
            except:
                pass

# Global IR transmitter instance
ir_transmitter = None

def get_ir_transmitter() -> IRTransmitter:
    """Get global IR transmitter instance"""
    global ir_transmitter
    if ir_transmitter is None:
        ir_transmitter = IRTransmitter()
    return ir_transmitter

# Test function
if __name__ == "__main__":
    print("💡 Testing GPIO IR Transmitter...")
    
    ir = IRTransmitter()
    
    try:
        print("Status:", ir.get_status())
        
        # Test basic on/off
        print("\n🔄 Testing basic on/off...")
        ir.turn_on(0.5)
        time.sleep(2)
        ir.turn_off()
        time.sleep(1)
        
        # Test brightness control
        print("\n🔄 Testing brightness control...")
        for brightness in [0.2, 0.5, 0.8, 1.0]:
            ir.turn_on(brightness)
            print(f"Brightness: {brightness}")
            time.sleep(1)
        ir.turn_off()
        
        # Test pulse
        print("\n🔄 Testing pulse...")
        ir.pulse(duration=1.0, brightness=1.0)
        
        # Test auto mode briefly
        print("\n🔄 Testing auto night mode (5 seconds)...")
        ir.start_auto_night_mode()
        time.sleep(5)
        ir.stop_auto_night_mode()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        ir.cleanup()
        
    print("✅ IR transmitter test complete")
