"""
IR LED Control Routes for NutFlix Platform
Provides REST API endpoints for controlling the IR LED for night vision
"""

import os
import sys
from flask import Blueprint, request, jsonify
import json

# Add the parent directory to Python path so we can import 'core'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from core.infrared.ir_transmitter import IRTransmitter
except ImportError as e:
    print(f"⚠️ Could not import IRTransmitter: {e}")
    IRTransmitter = None

# Create blueprint
ir_bp = Blueprint('ir_control', __name__)

# Global IR transmitter instance
ir_transmitter = None

def init_ir_transmitter():
    """Initialize the IR transmitter instance"""
    global ir_transmitter
    if IRTransmitter and not ir_transmitter:
        try:
            ir_transmitter = IRTransmitter(gpio_pin=23)  # GPIO 23 (Pin 16)
            print("💡 IR transmitter initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize IR transmitter: {e}")
            ir_transmitter = None
    return ir_transmitter

@ir_bp.route('/api/ir/status', methods=['GET'])
def get_ir_status():
    """Get current IR LED status"""
    transmitter = init_ir_transmitter()
    
    if not transmitter:
        return jsonify({
            'success': False,
            'error': 'IR transmitter not available',
            'status': {
                'is_on': False,
                'brightness': 0,
                'auto_mode': False
            }
        }), 500
    
    return jsonify({
        'success': True,
        'status': {
            'is_on': transmitter.is_on,
            'brightness': transmitter.brightness,
            'auto_mode': transmitter.auto_mode,
            'gpio_pin': transmitter.gpio_pin
        }
    })

@ir_bp.route('/api/ir/on', methods=['POST'])
def turn_ir_on():
    """Turn on IR LED with optional brightness"""
    transmitter = init_ir_transmitter()
    
    if not transmitter:
        return jsonify({
            'success': False,
            'error': 'IR transmitter not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        brightness = float(data.get('brightness', 1.0))
        
        # Clamp brightness to valid range
        brightness = max(0.0, min(1.0, brightness))
        
        transmitter.turn_on(brightness)
        
        return jsonify({
            'success': True,
            'message': f'IR LED turned on at {brightness*100:.0f}% brightness',
            'status': {
                'is_on': transmitter.is_on,
                'brightness': transmitter.brightness
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ir_bp.route('/api/ir/off', methods=['POST'])
def turn_ir_off():
    """Turn off IR LED"""
    transmitter = init_ir_transmitter()
    
    if not transmitter:
        return jsonify({
            'success': False,
            'error': 'IR transmitter not available'
        }), 500
    
    try:
        transmitter.turn_off()
        
        return jsonify({
            'success': True,
            'message': 'IR LED turned off',
            'status': {
                'is_on': transmitter.is_on,
                'brightness': transmitter.brightness
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ir_bp.route('/api/ir/brightness', methods=['POST'])
def set_ir_brightness():
    """Set IR LED brightness"""
    transmitter = init_ir_transmitter()
    
    if not transmitter:
        return jsonify({
            'success': False,
            'error': 'IR transmitter not available'
        }), 500
    
    try:
        data = request.get_json()
        if not data or 'brightness' not in data:
            return jsonify({
                'success': False,
                'error': 'brightness parameter required'
            }), 400
        
        brightness = float(data['brightness'])
        brightness = max(0.0, min(1.0, brightness))
        
        transmitter.set_brightness(brightness)
        
        return jsonify({
            'success': True,
            'message': f'IR LED brightness set to {brightness*100:.0f}%',
            'status': {
                'is_on': transmitter.is_on,
                'brightness': transmitter.brightness
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ir_bp.route('/api/ir/pulse', methods=['POST'])
def pulse_ir():
    """Pulse IR LED for a specified duration"""
    transmitter = init_ir_transmitter()
    
    if not transmitter:
        return jsonify({
            'success': False,
            'error': 'IR transmitter not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        duration = float(data.get('duration', 0.5))
        brightness = float(data.get('brightness', 1.0))
        
        # Clamp values
        duration = max(0.1, min(5.0, duration))
        brightness = max(0.0, min(1.0, brightness))
        
        transmitter.pulse(duration, brightness)
        
        return jsonify({
            'success': True,
            'message': f'IR LED pulsed for {duration}s at {brightness*100:.0f}% brightness',
            'status': {
                'is_on': transmitter.is_on,
                'brightness': transmitter.brightness
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ir_bp.route('/api/ir/auto-mode', methods=['POST'])
def toggle_auto_mode():
    """Toggle automatic night mode for IR LED"""
    transmitter = init_ir_transmitter()
    
    if not transmitter:
        return jsonify({
            'success': False,
            'error': 'IR transmitter not available'
        }), 500
    
    try:
        data = request.get_json() or {}
        enable = data.get('enabled', not transmitter.auto_mode)
        
        if enable:
            threshold = float(data.get('threshold', 0.3))
            transmitter.start_auto_night_mode(threshold)
            message = f'Auto night mode enabled (threshold: {threshold})'
        else:
            transmitter.stop_auto_night_mode()
            message = 'Auto night mode disabled'
        
        return jsonify({
            'success': True,
            'message': message,
            'status': {
                'is_on': transmitter.is_on,
                'brightness': transmitter.brightness,
                'auto_mode': transmitter.auto_mode
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
