import React, { useState } from 'react';

// This component recreates your Flask dashboard using your exact CSS patterns
function FlaskStyleDashboard({ systemHealth }) {
  const [showModal, setShowModal] = useState(false);
  const [selectedSetting, setSelectedSetting] = useState('motion_sensitivity');
  const [settingValue, setSettingValue] = useState(75);

  // Data in the format your Flask dashboard expects
  const environmentData = {
    temperature: systemHealth.temperature,
    humidity: systemHealth.humidity,
    pressure: 1013.25 // Adding pressure like your Flask dashboard
  };

  const cameraStatus = {
    outside: systemHealth.cameras.outside ? 'online' : 'offline',
    inside: systemHealth.cameras.inside ? 'online' : 'offline'
  };

  const recentActivity = [
    { time: '14:32:01', event: 'Motion detected - Outside camera', level: 'INFO' },
    { time: '14:31:45', event: 'Recording started - motion_trigger.mp4', level: 'INFO' },
    { time: '14:30:12', event: 'Squirrel identified with 95% confidence', level: 'INFO' },
    { time: '14:28:33', event: 'Environment data logged', level: 'INFO' },
  ];

  return (
    <div className="flask-dashboard">
      {/* Status Cards Section (matching your Flask widgets) */}
      <div className="status-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="status-card">
          <h3>Storage Used</h3>
          <div className="value">{Math.round(systemHealth.storage)}</div>
          <div className="unit">% of 1TB</div>
        </div>
        
        <div className="status-card">
          <h3>Recordings Today</h3>
          <div className="value">23</div>
          <div className="unit">clips</div>
        </div>
        
        <div className="status-card">
          <h3>Squirrel Visits</h3>
          <div className="value">47</div>
          <div className="unit">detected</div>
        </div>
        
        <div className="status-card">
          <h3>System Uptime</h3>
          <div className="value">12</div>
          <div className="unit">days</div>
        </div>
      </div>

      {/* Camera Status Cards (matching your Flask camera cards) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className={`camera-card ${cameraStatus.outside === 'offline' ? 'offline' : ''}`}>
          <h3>📹 Outside Camera</h3>
          <div className={`status ${cameraStatus.outside}`}>
            {cameraStatus.outside}
          </div>
          <p>Resolution: 1920x1080 @ 30fps</p>
          <p>Last Motion: 2 minutes ago</p>
          <div className={`motion-badge ${cameraStatus.outside === 'online' ? 'active' : 'inactive'}`}>
            Motion Detection Active
          </div>
        </div>
        
        <div className={`camera-card ${cameraStatus.inside === 'offline' ? 'offline' : ''}`}>
          <h3>📹 Inside Camera</h3>
          <div className={`status ${cameraStatus.inside}`}>
            {cameraStatus.inside}
          </div>
          <p>Resolution: 1920x1080 @ 30fps</p>
          <p>Last Motion: 15 minutes ago</p>
          <div className={`motion-badge ${cameraStatus.inside === 'online' ? 'active' : 'inactive'}`}>
            Motion Detection Active
          </div>
        </div>
      </div>

      {/* Environment Info (matching your Flask env display) */}
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.5rem' }}>
        <h3 style={{ color: 'white', margin: '0 0 1rem 0' }}>🌡️ Environmental Conditions</h3>
        <div className="env-info">
          <div className="env-item">
            <h4>Temperature</h4>
            <div className="env-value">{environmentData.temperature.toFixed(1)}°C</div>
          </div>
          <div className="env-item">
            <h4>Humidity</h4>
            <div className="env-value">{environmentData.humidity.toFixed(1)}%</div>
          </div>
          <div className="env-item">
            <h4>Pressure</h4>
            <div className="env-value">{environmentData.pressure} hPa</div>
          </div>
        </div>
      </div>

      {/* Activity Section (matching your Flask activity log) */}
      <div className="activity-section">
        <h3>📋 Recent Activity</h3>
        {recentActivity.map((activity, index) => (
          <div key={index} className="activity-item">
            <span className="activity-time">{activity.time}</span>
            <span className="activity-event">{activity.event}</span>
            <span style={{ 
              color: activity.level === 'INFO' ? '#4caf50' : '#ff9800',
              fontWeight: 'bold',
              fontSize: '0.8rem'
            }}>
              {activity.level}
            </span>
          </div>
        ))}
      </div>

      {/* Settings Section (matching your Flask forms) */}
      <div className="form-section">
        <h3>⚙️ Quick Settings</h3>
        <div className="form-group">
          <label htmlFor="motion-sensitivity">Motion Sensitivity</label>
          <input 
            type="range" 
            id="motion-sensitivity"
            min="0" 
            max="100" 
            value={settingValue}
            onChange={(e) => setSettingValue(e.target.value)}
          />
          <span className="range-value">{settingValue}%</span>
        </div>
        
        <div className="form-group">
          <label htmlFor="recording-quality">Recording Quality</label>
          <select id="recording-quality">
            <option value="high">High (1080p)</option>
            <option value="medium">Medium (720p)</option>
            <option value="low">Low (480p)</option>
          </select>
        </div>
        
        <button 
          className="submit-btn"
          onClick={() => setShowModal(true)}
        >
          Advanced Settings
        </button>
      </div>

      {/* Modal (matching your Flask modal system) */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Advanced Camera Settings</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                ×
              </button>
            </div>
            
            <div className="form-section" style={{ margin: 0, padding: 0, background: 'none' }}>
              <div className="form-group">
                <label>Night Vision Mode</label>
                <select>
                  <option value="auto">Auto</option>
                  <option value="on">Always On</option>
                  <option value="off">Off</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Recording Duration (seconds)</label>
                <input type="number" defaultValue="30" min="5" max="300" />
              </div>
              
              <div className="form-group">
                <label>
                  <input type="checkbox" defaultChecked /> 
                  Enable audio recording
                </label>
              </div>
              
              <button className="submit-btn">Save Settings</button>
            </div>
          </div>
        </div>
      )}

      {/* Data Table (matching your Flask motion events table) */}
      <div style={{ marginTop: '1.5rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>📊 Recent Motion Events</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Camera</th>
              <th>Duration</th>
              <th>Confidence</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>14:32:01</td>
              <td>Outside</td>
              <td>2:34</td>
              <td>95%</td>
              <td><button style={{ padding: '0.25rem 0.5rem', border: '1px solid #76b900', background: 'rgba(30, 45, 55, 0.8)', color: '#8fbc8f', borderRadius: '4px', cursor: 'pointer' }}>View</button></td>
            </tr>
            <tr>
              <td>14:28:15</td>
              <td>Inside</td>
              <td>1:45</td>
              <td>87%</td>
              <td><button style={{ padding: '0.25rem 0.5rem', border: '1px solid #76b900', background: 'rgba(30, 45, 55, 0.8)', color: '#8fbc8f', borderRadius: '4px', cursor: 'pointer' }}>View</button></td>
            </tr>
            <tr>
              <td>14:25:42</td>
              <td>Outside</td>
              <td>3:12</td>
              <td>92%</td>
              <td><button style={{ padding: '0.25rem 0.5rem', border: '1px solid #76b900', background: 'rgba(30, 45, 55, 0.8)', color: '#8fbc8f', borderRadius: '4px', cursor: 'pointer' }}>View</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default FlaskStyleDashboard;
