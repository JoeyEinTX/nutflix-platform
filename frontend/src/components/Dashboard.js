import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [streamStatus, setStreamStatus] = useState(null);
  const [recentClips, setRecentClips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch system status
        const status = await apiService.getStatus();
        setSystemStatus(status);

        // Try to fetch stream status if available
        if (status.modules.stream) {
          try {
            const streamStat = await apiService.getStreamStatus();
            setStreamStatus(streamStat);
          } catch (streamError) {
            console.warn('Stream status unavailable:', streamError);
          }
        }

        // Try to fetch recent clips if available
        if (status.modules.clips) {
          try {
            const clips = await apiService.getClips({ limit: 5 });
            setRecentClips(clips.clips || clips || []);
          } catch (clipsError) {
            console.warn('Recent clips unavailable:', clipsError);
          }
        }

      } catch (err) {
        setError('Failed to load dashboard data');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>Dashboard Error</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          Reload Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h1>🐿️ Nutflix Dashboard</h1>
      
      <div className="dashboard-grid">
        {/* System Status Card */}
        <div className="dashboard-card">
          <h2>System Status</h2>
          <div className="status-info">
            <div className={`status-indicator ${systemStatus?.status || 'unknown'}`}>
              {systemStatus?.status || 'Unknown'}
            </div>
            <p>Version: {systemStatus?.version || 'N/A'}</p>
          </div>
          
          <div className="modules-status">
            <h3>Available Modules</h3>
            {systemStatus?.modules && Object.entries(systemStatus.modules).map(([module, available]) => (
              <div key={module} className={`module-status ${available ? 'available' : 'unavailable'}`}>
                <span className="module-name">{module}</span>
                <span className={`module-indicator ${available ? 'on' : 'off'}`}>
                  {available ? '✓' : '✗'}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Stream Status Card */}
        <div className="dashboard-card">
          <h2>Live Stream</h2>
          {streamStatus ? (
            <div className="stream-info">
              <div className={`stream-status ${streamStatus.active ? 'active' : 'inactive'}`}>
                {streamStatus.active ? '🔴 Live' : '⭕ Offline'}
              </div>
              {streamStatus.active && (
                <div className="stream-details">
                  <p>Viewers: {streamStatus.viewers || 0}</p>
                  <p>Duration: {streamStatus.duration || '00:00'}</p>
                </div>
              )}
            </div>
          ) : (
            <p>Stream module not available</p>
          )}
        </div>

        {/* Recent Clips Card */}
        <div className="dashboard-card recent-clips">
          <h2>Recent Clips</h2>
          {recentClips.length > 0 ? (
            <div className="clips-list">
              {recentClips.slice(0, 3).map((clip, index) => (
                <div key={clip.id || index} className="clip-item">
                  <div className="clip-info">
                    <span className="clip-name">{clip.filename || `Clip ${index + 1}`}</span>
                    <span className="clip-date">
                      {clip.timestamp ? new Date(clip.timestamp).toLocaleDateString() : 'Unknown date'}
                    </span>
                  </div>
                  {clip.species && (
                    <span className="clip-species">{clip.species}</span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p>No recent clips available</p>
          )}
        </div>

        {/* Quick Actions Card */}
        <div className="dashboard-card">
          <h2>Quick Actions</h2>
          <div className="quick-actions">
            <button className="action-btn primary">
              📹 Start Recording
            </button>
            <button className="action-btn secondary">
              📊 View Analytics
            </button>
            <button className="action-btn secondary">
              ⚙️ Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
