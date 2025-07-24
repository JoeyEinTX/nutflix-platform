import { useState } from 'react';

function LiveStream() {
  const [selectedCamera, setSelectedCamera] = useState('outside');
  const [isRecording, setIsRecording] = useState(false);

  return (
    <div className="live-stream">
      <div className="card">
        <h2>🔴 Live Stream</h2>
        
        <div className="camera-controls">
          <button 
            className={selectedCamera === 'outside' ? 'active' : ''}
            onClick={() => setSelectedCamera('outside')}
          >
            📹 Outside Camera
          </button>
          <button 
            className={selectedCamera === 'inside' ? 'active' : ''}
            onClick={() => setSelectedCamera('inside')}
          >
            📹 Inside Camera
          </button>
          <button 
            className={selectedCamera === 'split' ? 'active' : ''}
            onClick={() => setSelectedCamera('split')}
          >
            🎭 Split View
          </button>
        </div>

        <div className="video-container">
          {selectedCamera === 'split' ? (
            <div className="split-view">
              <div className="video-player half">
                <div className="placeholder-stream">
                  <div>📹</div>
                  <p>Outside Camera</p>
                  <p>Waiting for motion...</p>
                </div>
              </div>
              <div className="video-player half">
                <div className="placeholder-stream">
                  <div>📹</div>
                  <p>Inside Camera</p>
                  <p>No activity detected</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="video-player">
              <div className="placeholder-stream">
                <div style={{ fontSize: '4rem' }}>📹</div>
                <h3>{selectedCamera === 'outside' ? 'Outside' : 'Inside'} Camera</h3>
                <p>{selectedCamera === 'outside' 
                  ? 'Monitoring approach area...' 
                  : 'Waiting for squirrel entry...'
                }</p>
                <div className="stream-status">
                  <span className="status-dot online"></span>
                  <span>Live</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="stream-controls">
          <button 
            className={`record-btn ${isRecording ? 'recording' : ''}`}
            onClick={() => setIsRecording(!isRecording)}
          >
            {isRecording ? '⏹️ Stop Recording' : '🔴 Start Recording'}
          </button>
          <button className="snapshot-btn">📸 Take Snapshot</button>
          <button className="settings-btn">⚙️ Camera Settings</button>
        </div>
      </div>

      <div className="card">
        <h2>📊 Stream Statistics</h2>
        <div className="stream-stats">
          <div className="stat-item">
            <label>Resolution:</label>
            <span>1920x1080 @ 30fps</span>
          </div>
          <div className="stat-item">
            <label>Bitrate:</label>
            <span>2.5 Mbps</span>
          </div>
          <div className="stat-item">
            <label>Motion Sensitivity:</label>
            <span>Medium (75%)</span>
          </div>
          <div className="stat-item">
            <label>Recording Quality:</label>
            <span>High</span>
          </div>
          <div className="stat-item">
            <label>Audio:</label>
            <span>Interior microphone only</span>
          </div>
          <div className="stat-item">
            <label>Night Vision:</label>
            <span>Auto (NoIR cameras)</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        .camera-controls {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
          flex-wrap: wrap;
        }

        .camera-controls button {
          padding: 0.5rem 1rem;
          border: 1px solid #ddd;
          background: white;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .camera-controls button.active {
          background: #4ecdc4;
          color: white;
          border-color: #4ecdc4;
        }

        .video-container {
          margin-bottom: 1rem;
        }

        .split-view {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .video-player.half {
          aspect-ratio: 16/9;
        }

        .stream-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-top: 1rem;
          color: #4caf50;
          font-weight: bold;
        }

        .stream-controls {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
          justify-content: center;
        }

        .record-btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: bold;
          background: #ff4444;
          color: white;
          transition: all 0.3s ease;
        }

        .record-btn.recording {
          background: #ff8a80;
          animation: pulse-record 1s infinite;
        }

        @keyframes pulse-record {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }

        .snapshot-btn, .settings-btn {
          padding: 0.75rem 1.5rem;
          border: 1px solid #4ecdc4;
          background: white;
          color: #4ecdc4;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .snapshot-btn:hover, .settings-btn:hover {
          background: #4ecdc4;
          color: white;
        }

        .stream-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .stat-item {
          display: flex;
          justify-content: space-between;
          padding: 0.75rem;
          background: rgba(78, 205, 196, 0.05);
          border-radius: 6px;
          border-left: 3px solid #4ecdc4;
        }

        .stat-item label {
          font-weight: bold;
          color: #666;
        }

        .stat-item span {
          color: #333;
        }
      `}</style>
    </div>
  );
}

export default LiveStream;
