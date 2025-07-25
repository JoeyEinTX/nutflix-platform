import React, { useState, useEffect } from 'react';

function CameraThumbnail({ camera, onClick }) {
  const [thumbnailSrc, setThumbnailSrc] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchThumbnail = async () => {
      try {
        setIsLoading(true);
        setError(false);
        
        // Use the correct camera name from Flask backend logs
        const cameraName = camera.apiName || camera.name;
        const response = await fetch(`/api/stream/${cameraName}/thumbnail`);
        
        if (response.ok) {
          const blob = await response.blob();
          const imageUrl = URL.createObjectURL(blob);
          setThumbnailSrc(imageUrl);
        } else {
          setError(true);
        }
      } catch (err) {
        console.error(`Error fetching thumbnail for ${camera.name}:`, err);
        setError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchThumbnail();
    
    // Refresh thumbnail every 5 seconds for live feed
    const interval = setInterval(fetchThumbnail, 5000);
    
    return () => {
      clearInterval(interval);
      if (thumbnailSrc) {
        URL.revokeObjectURL(thumbnailSrc);
      }
    };
  }, [camera.apiName, camera.name]);

  const handleClick = () => {
    if (onClick) {
      onClick(camera);
    }
  };

  return (
    <div 
      style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer' }}
      onClick={handleClick}
    >
      <div style={{
        width: '48px',
        height: '32px',
        background: camera.status === 'live' ? 'radial-gradient(circle, rgba(76,175,80,0.15), transparent)' : 'rgba(60,60,60,0.5)',
        borderRadius: '6px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '0.2rem',
        border: `2px solid ${camera.status === 'live' ? '#76b900' : '#888'}`,
        overflow: 'hidden',
        position: 'relative'
      }}>
        {isLoading ? (
          <span style={{ fontSize: '1rem', color: '#76b900' }}>⏳</span>
        ) : error || !thumbnailSrc ? (
          <span style={{ fontSize: '1.5rem', color: camera.status === 'live' ? '#76b900' : '#888' }}>📹</span>
        ) : (
          <img 
            src={thumbnailSrc} 
            alt={`${camera.name} thumbnail`}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              borderRadius: '4px'
            }}
            onError={() => setError(true)}
          />
        )}
        
        {/* Live indicator */}
        {camera.status === 'live' && !error && (
          <div style={{
            position: 'absolute',
            top: '2px',
            right: '2px',
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: '#dc3545',
            boxShadow: '0 0 4px rgba(220, 53, 69, 0.8)'
          }} />
        )}
      </div>
      <span style={{ fontSize: '0.7rem', color: '#e0e0e0' }}>{camera.name}</span>
    </div>
  );
}

export default CameraThumbnail;
