import React, { useState, useEffect } from 'react';

function OnDemandCameraView({ camera, onClose }) {
  const [streamMode, setStreamMode] = useState('snapshot'); // 'snapshot' | 'live'
  const [streamSrc, setStreamSrc] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(false);
  const [streamStats, setStreamStats] = useState(null);

  // Snapshot mode (default) - refresh every 3 seconds
  useEffect(() => {
    if (streamMode === 'snapshot') {
      const fetchSnapshot = async () => {
        try {
          setError(false);
          const cameraName = camera.apiName || camera.name;
          const response = await fetch(`/api/stream/${cameraName}/snapshot?t=${Date.now()}`);
          
          if (response.ok) {
            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);
            if (streamSrc) {
              URL.revokeObjectURL(streamSrc);
            }
            setStreamSrc(imageUrl);
          } else {
            setError(true);
          }
        } catch (err) {
          console.error(`Error fetching snapshot for ${camera.name}:`, err);
          setError(true);
        }
      };

      fetchSnapshot();
      const interval = setInterval(fetchSnapshot, 3000);
      
      return () => {
        clearInterval(interval);
        if (streamSrc) {
          URL.revokeObjectURL(streamSrc);
        }
      };
    }
  }, [camera.apiName, camera.name, streamMode, streamSrc]);

  // Live stream mode - MJPEG stream
  useEffect(() => {
    if (streamMode === 'live') {
      const cameraName = camera.apiName || camera.name;
      const streamUrl = `/api/stream/${cameraName}/live`;
      setStreamSrc(streamUrl);
      
      // Fetch stream stats
      fetch('/api/stream/status')
        .then(res => res.json())
        .then(data => {
          if (data.cameras && data.cameras[cameraName]) {
            setStreamStats(data.cameras[cameraName]);
          }
        })
        .catch(err => console.error('Error fetching stream stats:', err));
    }
  }, [camera.apiName, camera.name, streamMode]);

  const startLiveStream = async () => {
    setIsLoading(true);
    try {
      // Request to start live streaming for this camera
      const response = await fetch('/api/stream/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ camera: camera.apiName || camera.name })
      });
      
      if (response.ok) {
        setStreamMode('live');
      } else {
        setError(true);
      }
    } catch (err) {
      console.error('Error starting live stream:', err);
      setError(true);
    } finally {
      setIsLoading(false);
    }
  };

  const stopLiveStream = async () => {
    try {
      await fetch('/api/stream/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ camera: camera.apiName || camera.name })
      });
      setStreamMode('snapshot');
      setStreamStats(null);
    } catch (err) {
      console.error('Error stopping live stream:', err);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      background: 'rgba(0,0,0,0.9)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      {/* Header */}
      <div style={{
        width: '100%',
        maxWidth: '900px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        color: '#fff'
      }}>
        <div>
          <h2 style={{ margin: 0, color: '#76b900' }}>{camera.name}</h2>
          <p style={{ margin: '0.5rem 0 0 0', color: '#8fbc8f' }}>
            📍 {camera.location} • 
            <span style={{ 
              color: streamMode === 'live' ? '#dc3545' : '#f39c12',
              marginLeft: '0.5rem',
              fontWeight: 'bold'
            }}>
              {streamMode === 'live' ? '🔴 LIVE' : '📸 SNAPSHOTS'}
            </span>
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          {/* Stream Mode Toggle */}
          {streamMode === 'snapshot' ? (
            <button
              onClick={startLiveStream}
              disabled={isLoading}
              style={{
                padding: '0.75rem 1.5rem',
                background: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                opacity: isLoading ? 0.6 : 1
              }}
            >
              {isLoading ? '⏳ Starting...' : '🔴 Go Live'}
            </button>
          ) : (
            <button
              onClick={stopLiveStream}
              style={{
                padding: '0.75rem 1.5rem',
                background: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              📸 Switch to Snapshots
            </button>
          )}
          
          {/* Close Button */}
          <button
            onClick={onClose}
            style={{
              padding: '0.75rem 1rem',
              background: 'rgba(139, 90, 43, 0.8)',
              color: '#f5e6d3',
              border: '2px solid rgba(139, 90, 43, 0.7)',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '1.1rem'
            }}
          >
            ✕ Close
          </button>
        </div>
      </div>

      {/* Video Display */}
      <div style={{
        width: '100%',
        maxWidth: '900px',
        height: '500px',
        background: 'rgba(20, 30, 40, 0.95)',
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
        border: `2px solid ${streamMode === 'live' ? '#dc3545' : '#f39c12'}`
      }}>
        {error ? (
          <div style={{ textAlign: 'center', color: '#dc3545' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
            <div>Camera feed unavailable</div>
            <button
              onClick={() => setError(false)}
              style={{
                marginTop: '1rem',
                padding: '0.5rem 1rem',
                background: '#76b900',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Retry
            </button>
          </div>
        ) : streamSrc ? (
          <img 
            src={streamMode === 'live' ? `${streamSrc}?t=${Date.now()}` : streamSrc}
            alt={`${camera.name} ${streamMode} view`}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain'
            }}
            onError={() => setError(true)}
          />
        ) : (
          <div style={{ textAlign: 'center', color: '#8fbc8f' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⏳</div>
            <div>Loading camera feed...</div>
          </div>
        )}

        {/* Stream Stats Overlay */}
        {streamMode === 'live' && streamStats && (
          <div style={{
            position: 'absolute',
            top: '1rem',
            left: '1rem',
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            fontSize: '0.8rem',
            backdropFilter: 'blur(4px)'
          }}>
            <div>Resolution: {streamStats.resolution || '640x480'}</div>
            <div>FPS: {streamStats.fps || 30}</div>
            <div>Quality: High</div>
          </div>
        )}

        {/* Refresh Indicator for Snapshot Mode */}
        {streamMode === 'snapshot' && !error && (
          <div style={{
            position: 'absolute',
            bottom: '1rem',
            right: '1rem',
            background: 'rgba(243, 156, 18, 0.8)',
            color: 'white',
            padding: '0.25rem 0.75rem',
            borderRadius: '4px',
            fontSize: '0.7rem',
            fontWeight: 'bold'
          }}>
            📸 Refreshing every 3s
          </div>
        )}
      </div>

      {/* Instructions */}
      <div style={{
        marginTop: '1rem',
        color: '#8fbc8f',
        fontSize: '0.9rem',
        textAlign: 'center',
        maxWidth: '900px'
      }}>
        {streamMode === 'snapshot' ? (
          <p>💡 <strong>Snapshot Mode:</strong> Low bandwidth, updates every 3 seconds. Click "Go Live" for real-time streaming.</p>
        ) : (
          <p>💡 <strong>Live Mode:</strong> Real-time MJPEG stream. Uses more bandwidth. Click "Switch to Snapshots" to reduce usage.</p>
        )}
      </div>
    </div>
  );
}

export default OnDemandCameraView;
