import { useState } from 'react';

function SystemStatus({ systemHealth }) {
  const [diagnostics] = useState({
    cameras: {
      outside: { status: 'Online', fps: 30, resolution: '1920x1080', lastMotion: '2 minutes ago' },
      inside: { status: 'Online', fps: 30, resolution: '1920x1080', lastMotion: '15 minutes ago' }
    },
    storage: {
      total: '1TB',
      used: `${Math.round(systemHealth.storage)}%`,
      available: `${Math.round(1000 - (systemHealth.storage * 10))}GB`,
      recordings: '847 files',
      oldestRecording: '45 days ago'
    },
    network: {
      status: 'Connected',
      signalStrength: '85%',
      uploadSpeed: '25 Mbps',
      downloadSpeed: '100 Mbps',
      lastUpload: '3 minutes ago'
    },
    ai: {
      status: 'Processing',
      queueLength: 12,
      averageProcessingTime: '34 seconds',
      accuracy: '94.2%',
      modelsLoaded: 3
    }
  });

  const [logs] = useState([
    { time: '14:35:23', level: 'INFO', message: 'Motion detected on outside camera - confidence 87%' },
    { time: '14:33:15', level: 'INFO', message: 'AI processing complete for recording_20250115_1432.mp4' },
    { time: '14:32:01', level: 'INFO', message: 'Recording started: outside_camera_motion_trigger' },
    { time: '14:30:45', level: 'WARN', message: 'Storage usage above 75% - cleanup recommended' },
    { time: '14:28:12', level: 'INFO', message: 'Squirrel "Nutkin" identified with 95% confidence' },
    { time: '14:25:33', level: 'INFO', message: 'Environmental sensor data logged - temp: 22.3°C' },
    { time: '14:20:18', level: 'ERROR', message: 'Temporary network interruption - retrying upload' },
    { time: '14:18:45', level: 'INFO', message: 'Daily backup completed successfully' }
  ]);

  const getHealthStatus = (value, thresholds) => {
    if (value >= thresholds.error) return 'error';
    if (value >= thresholds.warning) return 'warning';
    return 'good';
  };

  const getLevelColor = (level) => {
    switch(level) {
      case 'ERROR': return '#f44336';
      case 'WARN': return '#ff9800';
      case 'INFO': return '#4caf50';
      default: return '#666';
    }
  };

  return (
    <div className="system-status">
      <div className="card">
        <h2>⚙️ System Health Overview</h2>
        <div className="health-grid">
          <div className="health-card good">
            <div className="health-icon">📹</div>
            <div className="health-info">
              <h3>Cameras</h3>
              <p>Both cameras online</p>
              <span className="health-status">Excellent</span>
            </div>
          </div>

          <div className={`health-card ${getHealthStatus(systemHealth.storage, { warning: 75, error: 90 })}`}>
            <div className="health-icon">💾</div>
            <div className="health-info">
              <h3>Storage</h3>
              <p>{diagnostics.storage.used} used</p>
              <span className="health-status">
                {systemHealth.storage > 90 ? 'Critical' : 
                 systemHealth.storage > 75 ? 'Warning' : 'Good'}
              </span>
            </div>
          </div>

          <div className="health-card good">
            <div className="health-icon">🌐</div>
            <div className="health-info">
              <h3>Network</h3>
              <p>Connected & uploading</p>
              <span className="health-status">Stable</span>
            </div>
          </div>

          <div className="health-card good">
            <div className="health-icon">🤖</div>
            <div className="health-info">
              <h3>AI Processing</h3>
              <p>{diagnostics.ai.accuracy} accuracy</p>
              <span className="health-status">Active</span>
            </div>
          </div>
        </div>
      </div>

      <div className="details-grid">
        <div className="card">
          <h3>📹 Camera Status</h3>
          <div className="camera-details">
            <div className="camera-item">
              <h4>Outside Camera</h4>
              <div className="camera-stats">
                <span>Status: <strong>{diagnostics.cameras.outside.status}</strong></span>
                <span>Resolution: <strong>{diagnostics.cameras.outside.resolution}</strong></span>
                <span>FPS: <strong>{diagnostics.cameras.outside.fps}</strong></span>
                <span>Last Motion: <strong>{diagnostics.cameras.outside.lastMotion}</strong></span>
              </div>
            </div>
            <div className="camera-item">
              <h4>Inside Camera</h4>
              <div className="camera-stats">
                <span>Status: <strong>{diagnostics.cameras.inside.status}</strong></span>
                <span>Resolution: <strong>{diagnostics.cameras.inside.resolution}</strong></span>
                <span>FPS: <strong>{diagnostics.cameras.inside.fps}</strong></span>
                <span>Last Motion: <strong>{diagnostics.cameras.inside.lastMotion}</strong></span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>💾 Storage Details</h3>
          <div className="storage-details">
            <div className="storage-item">
              <span>Total Capacity:</span>
              <strong>{diagnostics.storage.total}</strong>
            </div>
            <div className="storage-item">
              <span>Used Space:</span>
              <strong>{diagnostics.storage.used}</strong>
            </div>
            <div className="storage-item">
              <span>Available:</span>
              <strong>{diagnostics.storage.available}</strong>
            </div>
            <div className="storage-item">
              <span>Recordings:</span>
              <strong>{diagnostics.storage.recordings}</strong>
            </div>
            <div className="storage-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${systemHealth.storage}%` }}
                ></div>
              </div>
              <span>{systemHealth.storage.toFixed(1)}% used</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>🌐 Network & Connectivity</h3>
          <div className="network-details">
            <div className="network-item">
              <span>Connection Status:</span>
              <strong style={{ color: '#4caf50' }}>{diagnostics.network.status}</strong>
            </div>
            <div className="network-item">
              <span>Signal Strength:</span>
              <strong>{diagnostics.network.signalStrength}</strong>
            </div>
            <div className="network-item">
              <span>Upload Speed:</span>
              <strong>{diagnostics.network.uploadSpeed}</strong>
            </div>
            <div className="network-item">
              <span>Download Speed:</span>
              <strong>{diagnostics.network.downloadSpeed}</strong>
            </div>
            <div className="network-item">
              <span>Last Upload:</span>
              <strong>{diagnostics.network.lastUpload}</strong>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>🤖 AI Processing</h3>
          <div className="ai-details">
            <div className="ai-item">
              <span>Processing Status:</span>
              <strong style={{ color: '#4caf50' }}>{diagnostics.ai.status}</strong>
            </div>
            <div className="ai-item">
              <span>Queue Length:</span>
              <strong>{diagnostics.ai.queueLength} items</strong>
            </div>
            <div className="ai-item">
              <span>Avg Processing Time:</span>
              <strong>{diagnostics.ai.averageProcessingTime}</strong>
            </div>
            <div className="ai-item">
              <span>Recognition Accuracy:</span>
              <strong>{diagnostics.ai.accuracy}</strong>
            </div>
            <div className="ai-item">
              <span>Models Loaded:</span>
              <strong>{diagnostics.ai.modelsLoaded}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>📝 System Logs</h3>
        <div className="logs-container">
          {logs.map((log, index) => (
            <div key={index} className="log-entry">
              <span className="log-time">{log.time}</span>
              <span 
                className="log-level"
                style={{ color: getLevelColor(log.level) }}
              >
                {log.level}
              </span>
              <span className="log-message">{log.message}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>🔧 System Actions</h3>
        <div className="system-actions">
          <button className="action-button primary">🔄 Restart Cameras</button>
          <button className="action-button secondary">🧹 Clean Storage</button>
          <button className="action-button secondary">📊 Generate Report</button>
          <button className="action-button secondary">⚙️ System Settings</button>
          <button className="action-button secondary">🔒 Security Check</button>
          <button className="action-button warning">⏸️ Pause Recording</button>
        </div>
      </div>

      <style jsx>{`
        .health-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .health-card {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1.5rem;
          border-radius: 12px;
          border-left: 4px solid;
          transition: transform 0.3s ease;
        }

        .health-card:hover {
          transform: translateY(-3px);
        }

        .health-card.good {
          background: rgba(76, 175, 80, 0.1);
          border-left-color: #4caf50;
        }

        .health-card.warning {
          background: rgba(255, 193, 7, 0.1);
          border-left-color: #ffc107;
        }

        .health-card.error {
          background: rgba(244, 67, 54, 0.1);
          border-left-color: #f44336;
        }

        .health-icon {
          font-size: 2rem;
          opacity: 0.8;
        }

        .health-info h3 {
          margin: 0 0 0.25rem 0;
          color: #333;
        }

        .health-info p {
          margin: 0 0 0.25rem 0;
          color: #666;
          font-size: 0.9rem;
        }

        .health-status {
          font-size: 0.8rem;
          font-weight: bold;
          text-transform: uppercase;
          opacity: 0.8;
        }

        .details-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .camera-details {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .camera-item {
          padding: 1rem;
          background: rgba(78, 205, 196, 0.05);
          border-radius: 8px;
          border-left: 3px solid #4ecdc4;
        }

        .camera-item h4 {
          margin: 0 0 0.75rem 0;
          color: #333;
        }

        .camera-stats {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .camera-stats span {
          color: #666;
          font-size: 0.9rem;
        }

        .storage-details, .network-details, .ai-details {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .storage-item, .network-item, .ai-item {
          display: flex;
          justify-content: space-between;
          padding: 0.5rem;
          background: rgba(0, 0, 0, 0.02);
          border-radius: 6px;
        }

        .storage-progress {
          margin-top: 1rem;
        }

        .storage-progress span {
          font-size: 0.9rem;
          color: #666;
          margin-top: 0.5rem;
          display: block;
        }

        .logs-container {
          max-height: 300px;
          overflow-y: auto;
          background: #f8f9fa;
          border-radius: 8px;
          padding: 1rem;
        }

        .log-entry {
          display: grid;
          grid-template-columns: auto auto 1fr;
          gap: 1rem;
          padding: 0.5rem;
          border-bottom: 1px solid #eee;
          font-family: monospace;
          font-size: 0.9rem;
        }

        .log-entry:last-child {
          border-bottom: none;
        }

        .log-time {
          color: #666;
          white-space: nowrap;
        }

        .log-level {
          font-weight: bold;
          white-space: nowrap;
        }

        .log-message {
          color: #333;
        }

        .system-actions {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .action-button {
          padding: 1rem;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: bold;
          transition: all 0.3s ease;
          text-align: center;
        }

        .action-button.primary {
          background: linear-gradient(45deg, #4ecdc4, #44a08d);
          color: white;
        }

        .action-button.secondary {
          background: rgba(78, 205, 196, 0.1);
          color: #4ecdc4;
          border: 1px solid rgba(78, 205, 196, 0.3);
        }

        .action-button.warning {
          background: rgba(255, 193, 7, 0.1);
          color: #ff8f00;
          border: 1px solid rgba(255, 193, 7, 0.3);
        }

        .action-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
      `}</style>
    </div>
  );
}

export default SystemStatus;
