import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const Settings = () => {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const data = await apiService.getSettings();
        setSettings(data || {});
      } catch (err) {
        console.error('Settings error:', err);
        setSettings({
          recording_enabled: true,
          motion_sensitivity: 50,
          ai_detection: true,
          notification_email: '',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      await apiService.updateSettings(settings);
      setMessage('Settings saved successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('Failed to save settings.');
      console.error('Save settings error:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  if (loading) return <div>Loading settings...</div>;

  return (
    <div className="settings-page">
      <h1>⚙️ Settings</h1>
      
      {message && (
        <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      <div className="settings-form">
        <div className="setting-group">
          <label>
            <input
              type="checkbox"
              checked={settings.recording_enabled || false}
              onChange={(e) => handleChange('recording_enabled', e.target.checked)}
            />
            Enable Recording
          </label>
        </div>

        <div className="setting-group">
          <label>
            Motion Sensitivity: {settings.motion_sensitivity || 50}
            <input
              type="range"
              min="0"
              max="100"
              value={settings.motion_sensitivity || 50}
              onChange={(e) => handleChange('motion_sensitivity', parseInt(e.target.value))}
            />
          </label>
        </div>

        <div className="setting-group">
          <label>
            <input
              type="checkbox"
              checked={settings.ai_detection || false}
              onChange={(e) => handleChange('ai_detection', e.target.checked)}
            />
            Enable AI Detection
          </label>
        </div>

        <div className="setting-group">
          <label>
            Notification Email:
            <input
              type="email"
              value={settings.notification_email || ''}
              onChange={(e) => handleChange('notification_email', e.target.value)}
              placeholder="your@email.com"
            />
          </label>
        </div>

        <button 
          onClick={handleSave} 
          disabled={saving}
          className="save-button"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
};

export default Settings;
