import React, { useState, useEffect } from 'react';

function LiveCameraFeed({ camera, size = 'small' }) {
  const [refreshKey, setRefreshKey] = useState(Date.now());
  const [imageError, setImageError] = useState(false);

  // Refresh thumbnail every 3 seconds
  useEffect(() => {
    if (camera.status === 'live' && camera.thumbnailUrl) {
      const refreshTimer = setInterval(() => {
        setRefreshKey(Date.now());
        setImageError(false); // Reset error state
      }, 3000);
      return () => clearInterval(refreshTimer);
    }
  }, [camera.status, camera.thumbnailUrl]);

  const handleImageError = () => {
    console.log(`Failed to load thumbnail for ${camera.name}:`, camera.thumbnailUrl);
    setImageError(true);
  };

  const handleImageLoad = () => {
    setImageError(false);
  };

  if (camera.status !== 'live' || !camera.thumbnailUrl || imageError) {
    // Fallback display
    return (
      <div style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: camera.status === 'live' 
          ? 'radial-gradient(circle, rgba(76, 175, 80, 0.1), transparent)' 
          : 'rgba(60, 60, 60, 0.5)'
      }}>
        <div style={{
          fontSize: size === 'small' ? '1.5rem' : '2.5rem',
          color: camera.status === 'live' ? '#8fbc8f' : '#666',
          opacity: 0.7,
          marginBottom: size === 'small' ? '0' : '0.25rem'
        }}>
          📹
        </div>
        {size !== 'small' && (
          <>
            <div style={{
              fontSize: '0.8rem',
              color: camera.status === 'live' ? '#e0e0e0' : '#888',
              textAlign: 'center',
              fontWeight: 600
            }}>
              {camera.name}
            </div>
            <div style={{ 
              fontSize: '0.7rem', 
              color: '#888',
              textAlign: 'center'
            }}>
              {camera.location}
            </div>
          </>
        )}
      </div>
    );
  }

  return (
    <img 
      key={refreshKey}
      src={`${camera.thumbnailUrl}?t=${refreshKey}`} 
      alt={`${camera.name} live feed`}
      style={{ 
        width: '100%', 
        height: '100%', 
        objectFit: 'cover',
        borderRadius: size === 'small' ? '4px' : '6px'
      }}
      onError={handleImageError}
      onLoad={handleImageLoad}
    />
  );
}

export default LiveCameraFeed;
