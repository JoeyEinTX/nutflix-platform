import React, { useState, useEffect } from 'react';
import './IRLEDControl.css';

const IRLEDControl = () => {
  const [irStatus, setIrStatus] = useState({
    is_on: false,
    brightness: 0,
    auto_mode: false,
    gpio_pin: 23
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [brightness, setBrightness] = useState(1.0);
  const [autoModeEnabled, setAutoModeEnabled] = useState(false);

  // Fetch IR LED status on component mount
  useEffect(() => {
    fetchIRStatus();
  }, []);

  const fetchIRStatus = async () => {
    try {
      const response = await fetch('/api/ir/status');
      const data = await response.json();
      
      if (data.success) {
        setIrStatus(data.status);
        setBrightness(data.status.brightness);
        setAutoModeEnabled(data.status.auto_mode);
        setError(null);
      } else {
        setError(data.error || 'Failed to fetch IR status');
      }
    } catch (err) {
      setError('Connection error');
      console.error('Error fetching IR status:', err);
    }
  };

  const turnOnIR = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ir/on', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ brightness })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIrStatus(data.status);
        setError(null);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to turn on IR LED');
      console.error('Error turning on IR:', err);
    } finally {
      setLoading(false);
    }
  };

  const turnOffIR = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ir/off', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIrStatus(data.status);
        setError(null);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to turn off IR LED');
      console.error('Error turning off IR:', err);
    } finally {
      setLoading(false);
    }
  };

  const setBrightnessLevel = async (newBrightness) => {
    if (!irStatus.is_on) return; // Only set brightness when LED is on
    
    setLoading(true);
    try {
      const response = await fetch('/api/ir/brightness', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ brightness: newBrightness })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIrStatus(data.status);
        setError(null);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to set brightness');
      console.error('Error setting brightness:', err);
    } finally {
      setLoading(false);
    }
  };

  const pulseIR = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ir/pulse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          duration: 1.0,
          brightness: brightness 
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIrStatus(data.status);
        setError(null);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to pulse IR LED');
      console.error('Error pulsing IR:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleAutoMode = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/ir/auto-mode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          enabled: !autoModeEnabled,
          threshold: 0.3 
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIrStatus(data.status);
        setAutoModeEnabled(data.status.auto_mode);
        setError(null);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to toggle auto mode');
      console.error('Error toggling auto mode:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBrightnessChange = (e) => {
    const newBrightness = parseFloat(e.target.value);
    setBrightness(newBrightness);
    
    // Update brightness in real-time if LED is on
    if (irStatus.is_on) {
      setBrightnessLevel(newBrightness);
    }
  };

  return (
    <div className="ir-led-control">
      <div className="ir-header">
        <h3>🔦 IR LED Night Vision</h3>
        <div className="ir-status">
          <span className={`status-indicator ${irStatus.is_on ? 'on' : 'off'}`}>
            {irStatus.is_on ? '🟢 ON' : '🔴 OFF'}
          </span>
          <span className="gpio-info">GPIO {irStatus.gpio_pin}</span>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
          <button onClick={fetchIRStatus} className="retry-btn">Retry</button>
        </div>
      )}

      <div className="ir-controls">
        <div className="power-controls">
          <button 
            onClick={turnOnIR}
            disabled={loading || irStatus.is_on}
            className="ir-btn ir-btn-on"
          >
            {loading ? '⏳' : '🟢'} Turn On
          </button>
          
          <button 
            onClick={turnOffIR}
            disabled={loading || !irStatus.is_on}
            className="ir-btn ir-btn-off"
          >
            {loading ? '⏳' : '🔴'} Turn Off
          </button>
          
          <button 
            onClick={pulseIR}
            disabled={loading}
            className="ir-btn ir-btn-pulse"
          >
            {loading ? '⏳' : '💫'} Pulse
          </button>
        </div>

        <div className="brightness-control">
          <label htmlFor="brightness-slider">
            💡 Brightness: {Math.round(brightness * 100)}%
          </label>
          <div className="slider-container">
            <input
              id="brightness-slider"
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={brightness}
              onChange={handleBrightnessChange}
              disabled={loading}
              className="brightness-slider"
            />
            <div className="brightness-labels">
              <span>10%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>
        </div>

        <div className="auto-mode-control">
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={autoModeEnabled}
              onChange={toggleAutoMode}
              disabled={loading}
            />
            <span className="slider"></span>
            🌙 Auto Night Mode
          </label>
          <p className="auto-mode-desc">
            Automatically turns on IR LED in low light conditions
          </p>
        </div>
      </div>

      <div className="ir-info">
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Current Status:</span>
            <span className="info-value">
              {irStatus.is_on ? `ON (${Math.round(irStatus.brightness * 100)}%)` : 'OFF'}
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Auto Mode:</span>
            <span className="info-value">
              {irStatus.auto_mode ? '🌙 Enabled' : '⏸️ Disabled'}
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Hardware:</span>
            <span className="info-value">GPIO {irStatus.gpio_pin} (Pin 16)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IRLEDControl;
