import { useState, useEffect } from 'react';

function Dashboard({ systemHealth }) {
  const [recentActivity, setRecentActivity] = useState([
    { time: '14:32', event: 'Squirrel detected - Outside camera', confidence: 95 },
    { time: '14:31', event: 'Motion detected - Feeding area', confidence: 87 },
    { time: '14:28', event: 'Squirrel identified: "Nutkin"', confidence: 92 },
    { time: '14:25', event: 'Recording started - Inside camera', confidence: 100 },
  ]);

  const [todayStats, setTodayStats] = useState({
    squirrelVisits: 23,
    recordingTime: 47,
    uniqueSquirrels: 4,
    bestClip: "Nutkin's acrobatic feeding"
  });

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Squirrel Visits Today</h3>
          <div className="value">{todayStats.squirrelVisits}</div>
          <div className="unit">visits</div>
        </div>
        <div className="stat-card">
          <h3>Recording Time</h3>
          <div className="value">{todayStats.recordingTime}</div>
          <div className="unit">minutes</div>
        </div>
        <div className="stat-card">
          <h3>Unique Squirrels</h3>
          <div className="value">{todayStats.uniqueSquirrels}</div>
          <div className="unit">identified</div>
        </div>
        <div className="stat-card">
          <h3>Storage Used</h3>
          <div className="value">{Math.round(systemHealth.storage)}</div>
          <div className="unit">% of 1TB</div>
        </div>
      </div>

      <div className="card">
        <h2>🎯 Quick Actions</h2>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button className="action-btn primary">📹 Start Manual Recording</button>
          <button className="action-btn secondary">🔴 View Live Stream</button>
          <button className="action-btn secondary">⚙️ Adjust Motion Sensitivity</button>
          <button className="action-btn secondary">📤 Upload Recent Clips</button>
        </div>
      </div>

      <div className="card">
        <h2>📈 Recent Activity</h2>
        <div className="activity-feed">
          {recentActivity.map((activity, index) => (
            <div key={index} className="activity-item">
              <span className="activity-time">{activity.time}</span>
              <span className="activity-event">{activity.event}</span>
              <span className="activity-confidence">{activity.confidence}%</span>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2>🌡️ Environmental Conditions</h2>
        <div className="environmental-grid">
          <div className="env-item">
            <h4>Temperature</h4>
            <div className="env-value">{systemHealth.temperature.toFixed(1)}°C</div>
          </div>
          <div className="env-item">
            <h4>Humidity</h4>
            <div className="env-value">{systemHealth.humidity.toFixed(1)}%</div>
          </div>
          <div className="env-item">
            <h4>Light Level</h4>
            <div className="env-value">Bright</div>
          </div>
          <div className="env-item">
            <h4>Wind</h4>
            <div className="env-value">Light Breeze</div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .action-btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.3s ease;
        }

        .action-btn.primary {
          background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
          color: white;
        }

        .action-btn.secondary {
          background: rgba(78, 205, 196, 0.1);
          color: #4ecdc4;
          border: 1px solid rgba(78, 205, 196, 0.3);
        }

        .action-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .activity-feed {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .activity-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 0.75rem;
          background: rgba(78, 205, 196, 0.05);
          border-radius: 8px;
          border-left: 3px solid #4ecdc4;
        }

        .activity-time {
          font-weight: bold;
          color: #4ecdc4;
          min-width: 60px;
        }

        .activity-event {
          flex: 1;
          color: #333;
        }

        .activity-confidence {
          background: rgba(76, 175, 80, 0.1);
          color: #4caf50;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: bold;
        }

        .environmental-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
        }

        .env-item {
          text-align: center;
          padding: 1rem;
          background: rgba(255, 255, 255, 0.5);
          border-radius: 8px;
        }

        .env-item h4 {
          margin-bottom: 0.5rem;
          color: #666;
          font-size: 0.9rem;
        }

        .env-value {
          font-size: 1.5rem;
          font-weight: bold;
          color: #333;
        }
      `}</style>
    </div>
  );
}

export default Dashboard;
