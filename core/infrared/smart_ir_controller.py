"""
Smart IR LED Integration for Camera System
Provides automatic IR LED control based on camera motion detection and light conditions
"""

import cv2
import numpy as np
from typing import Optional
from datetime import datetime, time
import threading
import logging

# Import the IR transmitter
try:
    from core.infrared.ir_transmitter import IRTransmitter
    IR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ IR transmitter not available: {e}")
    IR_AVAILABLE = False

class SmartIRController:
    """Smart IR LED controller that integrates with camera motion detection"""
    
    def __init__(self):
        self.ir_transmitter = None
        self.current_camera = None
        self.is_active = False
        self._lock = threading.Lock()
        
        # IR LED mapping - only NestCam for now
        self.camera_ir_map = {
            'NestCam': True,   # NestCam has IR LED
            'CritterCam': False  # CritterCam doesn't (decided later)
        }
        
        # Initialize IR transmitter if available
        if IR_AVAILABLE:
            try:
                self.ir_transmitter = IRTransmitter(gpio_pin=23)  # GPIO 23 = Pin 16
                print("🔦 Smart IR controller initialized for NestCam")
            except Exception as e:
                print(f"❌ Failed to initialize IR controller: {e}")
                self.ir_transmitter = None
        else:
            print("🔦 IR controller running in mock mode")
    
    def should_use_ir(self, camera_name: str, frame: Optional[np.ndarray] = None) -> bool:
        """
        Determine if IR LED should be activated for this camera
        
        Args:
            camera_name: Name of the camera ('NestCam' or 'CritterCam')
            frame: Optional current frame for light analysis
            
        Returns:
            bool: True if IR LED should be on
        """
        # Only NestCam has IR LED for now
        if not self.camera_ir_map.get(camera_name, False):
            return False
        
        # Check if it's nighttime based on current time
        now = datetime.now().time()
        is_nighttime = now.hour < 6 or now.hour >= 20  # 8 PM to 6 AM
        
        # If we have a frame, also analyze brightness
        if frame is not None:
            avg_brightness = self._analyze_frame_brightness(frame)
            is_dark = avg_brightness < 80  # Threshold for "dark" conditions
            
            # Use IR if it's either nighttime OR the frame is dark
            return is_nighttime or is_dark
        
        # Fallback to time-based decision
        return is_nighttime
    
    def _analyze_frame_brightness(self, frame: np.ndarray) -> float:
        """
        Analyze frame brightness to determine if IR LED is needed
        
        Args:
            frame: Camera frame (BGR format)
            
        Returns:
            float: Average brightness (0-255)
        """
        try:
            # Convert to grayscale and calculate average brightness
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return float(np.mean(gray))
        except Exception as e:
            print(f"⚠️ Error analyzing frame brightness: {e}")
            return 128  # Default to medium brightness
    
    def on_motion_detected(self, camera_name: str, frame: Optional[np.ndarray] = None):
        """
        Handle motion detection event - potentially turn on IR LED
        
        Args:
            camera_name: Name of the camera that detected motion
            frame: Current camera frame for light analysis
        """
        with self._lock:
            # Check if we should use IR for this camera
            if not self.should_use_ir(camera_name, frame):
                return
            
            # Turn on IR LED if not already on
            if self.ir_transmitter and not self.is_active:
                try:
                    brightness = self._calculate_optimal_brightness(frame)
                    self.ir_transmitter.turn_on(brightness)
                    self.is_active = True
                    self.current_camera = camera_name
                    
                    print(f"🔦 IR LED activated for {camera_name} motion (brightness: {brightness*100:.0f}%)")
                    
                    # Schedule auto-off after 30 seconds
                    threading.Timer(30.0, self._auto_turn_off).start()
                    
                except Exception as e:
                    print(f"❌ Failed to activate IR LED: {e}")
    
    def _calculate_optimal_brightness(self, frame: Optional[np.ndarray]) -> float:
        """
        Calculate optimal IR LED brightness based on conditions
        
        Args:
            frame: Current camera frame for analysis
            
        Returns:
            float: Optimal brightness (0.1 to 1.0)
        """
        if frame is None:
            return 0.8  # Default brightness
        
        try:
            avg_brightness = self._analyze_frame_brightness(frame)
            
            # Darker conditions need brighter IR
            if avg_brightness < 30:      # Very dark
                return 1.0
            elif avg_brightness < 60:    # Dark
                return 0.8  
            elif avg_brightness < 100:   # Dim
                return 0.6
            else:                        # Twilight
                return 0.4
                
        except Exception as e:
            print(f"⚠️ Error calculating IR brightness: {e}")
            return 0.8  # Safe default
    
    def _auto_turn_off(self):
        """Automatically turn off IR LED after timeout"""
        with self._lock:
            if self.ir_transmitter and self.is_active:
                try:
                    self.ir_transmitter.turn_off()
                    self.is_active = False
                    print(f"🔦 IR LED auto-turned off for {self.current_camera}")
                    self.current_camera = None
                except Exception as e:
                    print(f"❌ Failed to auto-turn off IR LED: {e}")
    
    def force_off(self):
        """Manually turn off IR LED"""
        with self._lock:
            if self.ir_transmitter and self.is_active:
                try:
                    self.ir_transmitter.turn_off()
                    self.is_active = False
                    print(f"🔦 IR LED manually turned off")
                    self.current_camera = None
                except Exception as e:
                    print(f"❌ Failed to turn off IR LED: {e}")
    
    def activate_for_camera(self, camera_name: str, frame: Optional[np.ndarray] = None):
        """
        Activate IR LED for a specific camera during recording
        
        Args:
            camera_name: Name of the camera requesting IR
            frame: Optional current frame for brightness analysis
        """
        with self._lock:
            # Check if IR is supported for this camera
            if not self.camera_ir_map.get(camera_name, False):
                print(f"ℹ️ IR LED not supported for {camera_name}")
                return
            
            # Turn on IR LED if not already active
            if self.ir_transmitter and not self.is_active:
                try:
                    brightness = self._calculate_optimal_brightness(frame) if frame is not None else 0.8
                    self.ir_transmitter.turn_on(brightness)
                    self.is_active = True
                    self.current_camera = camera_name
                    print(f"🔦 IR LED activated for {camera_name} recording (brightness: {brightness*100:.0f}%)")
                except Exception as e:
                    print(f"❌ Failed to activate IR LED for {camera_name}: {e}")
            elif self.is_active:
                print(f"ℹ️ IR LED already active for {self.current_camera}")
    
    def deactivate(self):
        """Deactivate IR LED"""
        with self._lock:
            if self.ir_transmitter and self.is_active:
                try:
                    self.ir_transmitter.turn_off()
                    old_camera = self.current_camera
                    self.is_active = False
                    self.current_camera = None
                    print(f"🔦 IR LED deactivated (was active for {old_camera})")
                except Exception as e:
                    print(f"❌ Failed to deactivate IR LED: {e}")
            else:
                print("ℹ️ IR LED was not active")
    
    def get_status(self) -> dict:
        """Get current IR controller status"""
        return {
            'ir_available': self.ir_transmitter is not None,
            'is_active': self.is_active,
            'current_camera': self.current_camera,
            'supported_cameras': [cam for cam, supported in self.camera_ir_map.items() if supported]
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.force_off()
        if self.ir_transmitter:
            self.ir_transmitter.cleanup()

# Global smart IR controller instance
smart_ir_controller = SmartIRController()
