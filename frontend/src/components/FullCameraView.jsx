import React, { useState, useEffect } from 'react';

function FullCameraView({ camera }) {
  const [streamSrc, setStreamSrc] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchSnapshot = async () => {
      try {
        setIsLoading(true);
        setError(false);
        
        // Use the correct camera name from Flask backend logs
        const cameraName = camera.apiName || camera.name;
        const response = await fetch(`/api/stream/${cameraName}/snapshot`);
        
        if (response.ok) {
          const blob = await response.blob();
          const imageUrl = URL.createObjectURL(blob);
          setStreamSrc(imageUrl);
        } else {
          setError(true);
        }
      } catch (err) {
        console.error(`Error fetching snapshot for ${camera.name}:`, err);
        setError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSnapshot();
    
    // Refresh snapshot every 3 seconds for quasi-live view
    const interval = setInterval(fetchSnapshot, 3000);
    
    return () => {
      clearInterval(interval);
      if (streamSrc) {
        URL.revokeObjectURL(streamSrc);
      }
    };
  }, [camera.apiName, camera.name]);

  return (
    <div>
      <h2 style={{ color: '#76b900', marginBottom: '1rem', textAlign: 'center' }}>
        {camera.name} Camera
      </h2>
      <p style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <strong>Location:</strong> {camera.location} | <strong>Status:</strong> 
        <span style={{ color: camera.status === 'live' ? '#76b900' : '#dc3545', marginLeft: '0.5rem' }}>
          {camera.status.toUpperCase()}
        </span>
      </p>
      
      {/* Live View */}
      <div style={{
        width: '100%',
        height: '400px',
        maxWidth: '800px',
        background: camera.status === 'live' ? 'radial-gradient(circle, rgba(76,175,80,0.15), transparent)' : 'rgba(60,60,60,0.5)',
        borderRadius: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '1.5rem auto',
        position: 'relative',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
        overflow: 'hidden'
      }}>
        {isLoading ? (
          <div style={{ textAlign: 'center', color: '#76b900' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⏳</div>
            <div>Loading camera feed...</div>
          </div>
        ) : error || !streamSrc ? (
          camera.status === 'live' ? (
            <div style={{ textAlign: 'center', color: '#888' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📹</div>
              <div>Camera feed unavailable</div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#888' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
              <div>CAMERA OFFLINE</div>
            </div>
          )
        ) : (
          <img 
            src={streamSrc} 
            alt={`${camera.name} live view`}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              borderRadius: '16px'
            }}
            onError={() => setError(true)}
          />
        )}
        
        {/* LIVE badge */}
        {camera.status === 'live' && !error && !isLoading && (
          <div style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: '#dc3545',
            color: 'white',
            fontSize: '0.9rem',
            padding: '4px 12px',
            borderRadius: '6px',
            fontWeight: 'bold',
            boxShadow: '0 2px 8px rgba(220, 53, 69, 0.8)',
            animation: 'pulse 2s infinite'
          }}>
            ● LIVE
          </div>
        )}
        
        {/* Refresh indicator */}
        {camera.status === 'live' && !error && !isLoading && (
          <div style={{
            position: 'absolute',
            bottom: '16px',
            left: '16px',
            background: 'rgba(118, 185, 0, 0.8)',
            color: 'white',
            fontSize: '0.8rem',
            padding: '4px 8px',
            borderRadius: '4px',
            fontWeight: 'bold'
          }}>
            Refreshing every 3s
          </div>
        )}
      </div>
      
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
      `}</style>
    </div>
  );
}

export default FullCameraView;
