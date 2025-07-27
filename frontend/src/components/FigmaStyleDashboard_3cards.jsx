import React, { useState, useEffect } from 'react';
import { useSightings } from '../hooks/useSightings';
import OnDemandCameraView from './OnDemandCameraView';

function FigmaStyleDashboard({ systemHealth }) {
  // Camera modal state
  const [selectedSighting, setSelectedSighting] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState(null); // 'header' | 'camera' | 'sighting'
  const [modalData, setModalData] = useState(null);
  // On-demand camera view state
  const [showLiveCameraView, setShowLiveCameraView] = useState(false);
  const [liveCameraData, setLiveCameraData] = useState(null);
  // Real system data
  const [realSystemData, setRealSystemData] = useState(null);
  
  // Camera data state for static previews
  const [cameraData, setCameraData] = useState({
    'camera-1': { has_clip: false, last_seen_minutes: null, thumbnail_url: null, loading: true, error: null },
    'camera-2': { has_clip: false, last_seen_minutes: null, thumbnail_url: null, loading: true, error: null },
    'camera-3': { has_clip: false, last_seen_minutes: null, thumbnail_url: null, loading: true, error: null },
    'camera-4': { has_clip: false, last_seen_minutes: null, thumbnail_url: null, loading: true, error: null },
    'camera-5': { has_clip: false, last_seen_minutes: null, thumbnail_url: null, loading: true, error: null },
    'camera-6': { has_clip: false, last_seen_minutes: null, thumbnail_url: null, loading: true, error: null }
  });

  // Fetch camera data from latest clip API
  const fetchCameraData = async () => {
    try {
      const cameras = ['camera-1', 'camera-2', 'camera-3', 'camera-4', 'camera-5', 'camera-6'];
      const timestamp = Date.now(); // Add cache busting
      const promises = cameras.map(async (camera) => {
        try {
          const response = await fetch(`http://10.0.0.79:8000/api/latest_clip/${camera}?t=${timestamp}`);
          const data = await response.json();
          return { camera, data: { ...data, loading: false } };
        } catch (error) {
          console.error(`Error fetching ${camera} data:`, error);
          return { 
            camera, 
            data: { 
              has_clip: false, 
              last_seen_minutes: null, 
              thumbnail_url: null, 
              loading: false,
              error: error.message 
            } 
          };
        }
      });

      const results = await Promise.all(promises);
      const newCameraData = {};
      results.forEach(({ camera, data }) => {
        newCameraData[camera] = data;
      });
      
      setCameraData(newCameraData);
    } catch (error) {
      console.error('Error fetching camera data:', error);
    }
  };

  // Helper function to format camera data for display
  const formatCameraForDisplay = (cameraId, title, colorTheme, cameraNumber) => {
    const data = cameraData[cameraId];
    
    if (data.loading) {
      return {
        name: title,
        location: cameraId.includes('1') || cameraId.includes('3') || cameraId.includes('5') ? 'Interior' : 'Exterior',
        status: 'loading',
        thumbnailUrl: null,
        lastSeen: 'Loading...',
        hasClip: false,
        error: null
      };
    }
    if (data.error) {
      return {
        name: title,
        location: cameraId.includes('1') || cameraId.includes('3') || cameraId.includes('5') ? 'Interior' : 'Exterior',
        status: 'offline',
        thumbnailUrl: null,
        lastSeen: 'Error: ' + data.error,
        hasClip: false,
        error: data.error
      };
    }
    if (!data.has_clip) {
      return {
        name: title,
        location: cameraId.includes('1') || cameraId.includes('3') || cameraId.includes('5') ? 'Interior' : 'Exterior', 
        status: 'offline',
        thumbnailUrl: data.thumbnail_url,
        lastSeen: data.message || 'No sightings yet',
        hasClip: false,
        error: null
      };
    }
    // Format last seen time robustly
    let lastSeenText = '';
    if (typeof data.last_seen_minutes !== 'number' || isNaN(data.last_seen_minutes)) {
      lastSeenText = 'Unknown';
    } else if (data.last_seen_minutes === 0) {
      lastSeenText = 'Just now';
    } else if (data.last_seen_minutes === 1) {
      lastSeenText = '1 minute ago';
    } else if (data.last_seen_minutes < 60) {
      lastSeenText = `${data.last_seen_minutes} minutes ago`;
    } else {
      const hours = Math.floor(data.last_seen_minutes / 60);
      lastSeenText = hours === 1 ? '1 hour ago' : `${hours} hours ago`;
    }
    return {
      name: title,
      location: cameraId.includes('1') || cameraId.includes('3') || cameraId.includes('5') ? 'Interior' : 'Exterior',
      status: 'live',
      thumbnailUrl: data.thumbnail_url,
      lastSeen: lastSeenText,
      hasClip: true,
      triggerType: data.trigger_type,
      timestamp: data.timestamp,
      error: null
    };
  };

  // Use real sightings data - separate hooks for each camera
  const { sightings: critterCamSightings, loading: critterCamLoading, error: critterCamError } = useSightings(3, 'CritterCam');
  const { sightings: nestCamSightings, loading: nestCamLoading, error: nestCamError } = useSightings(3, 'NestCam');
  const { sightings: allSightings, loading: allSightingsLoading, error: allSightingsError, refetch: refetchSightings } = useSightings(4);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch real system data
  useEffect(() => {
    const fetchSystemData = async () => {
      try {
        const response = await fetch(`http://10.0.0.79:8000/api/system-info?t=${Date.now()}`);
        const data = await response.json();
        setRealSystemData(data);
      } catch (error) {
        console.error('Failed to fetch system data:', error);
      }
    };

    fetchSystemData();
    const interval = setInterval(fetchSystemData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Fetch camera data on mount and periodically (every 60 seconds)
  useEffect(() => {
    fetchCameraData();
    const interval = setInterval(fetchCameraData, 60000); // 60 seconds
    return () => clearInterval(interval);
  }, []);

  // Helper function to get camera-specific sightings with camera name
  const getCameraSightings = (cameraName) => {
    const isLoading = critterCamLoading || nestCamLoading;
    
    if (cameraName === 'CritterCam') {
      return isLoading ? [
        { id: 1, species: "Loading...", time: "", image: "⏳", camera: "CritterCam" }
      ] : (critterCamSightings.length > 0 ? critterCamSightings.map(s => ({...s, camera: "CritterCam"})) : [
        { id: 1, species: "No recent sightings", time: "", image: "😴", camera: "CritterCam" }
      ]);
    } else if (cameraName === 'NestCam') {
      return isLoading ? [
        { id: 1, species: "Loading...", time: "", image: "⏳", camera: "NestCam" }
      ] : (nestCamSightings.length > 0 ? nestCamSightings.map(s => ({...s, camera: "NestCam"})) : [
        { id: 1, species: "No recent sightings", time: "", image: "😴", camera: "NestCam" }
      ]);
    }
    
    // For mixed camera setups, use all sightings
    return allSightingsLoading ? [
      { id: 1, species: "Loading...", time: "", image: "⏳" }
    ] : (allSightings.length > 0 ? allSightings : [
      { id: 1, species: "No recent sightings", time: "", image: "😴" }
    ]);
  };

  // Helper function to get combined recent sightings for a SquirrelBox
  const getCombinedSightings = (cameras) => {
    // Use the general all-sightings data which includes both cameras mixed together
    // and is already sorted by most recent first
    return allSightingsLoading ? [
      { id: 1, species: "Loading...", time: "", image: "⏳" }
    ] : (allSightings.length > 0 ? allSightings : [
      { id: 1, species: "No recent sightings", time: "", image: "😴" }
    ]);
  };

  // Mock data for multiple SquirrelBoxes with camera-specific sightings
  const squirrelBoxes = [
    {
      id: 1,
      name: "Hero",
      location: "Backyard Oak Tree",
      temperature: realSystemData?.temperature || systemHealth.temperature,
      humidity: realSystemData?.humidity || systemHealth.humidity,
      storage: realSystemData?.storage || systemHealth.storage,
      batteryLevel: 87,
      cameras: [
        formatCameraForDisplay('camera-1', 'NestCam', 'green', 1),
        formatCameraForDisplay('camera-2', 'CritterCam', 'blue', 2)
      ],
      recentSightings: getCombinedSightings(['NestCam', 'CritterCam'])
    },
    {
      id: 2,
      name: "Garden Guardian",
      location: "Front Yard Maple",
      temperature: (realSystemData?.temperature || 24.3) + 1.2,
      humidity: (realSystemData?.humidity || 72) - 7,
      storage: Math.max(45, (realSystemData?.storage || 62) - 13),
      batteryLevel: 94,
      cameras: [
        formatCameraForDisplay('camera-3', 'NestCam', 'purple', 3),
        formatCameraForDisplay('camera-4', 'CritterCam', 'orange', 4)
      ],
      recentSightings: getCombinedSightings(['NestCam', 'CritterCam'])
    },
    {
      id: 3,
      name: "Forest Watcher",
      location: "Pine Grove",
      temperature: (realSystemData?.temperature || 19.8) - 2.7,
      humidity: (realSystemData?.humidity || 58) - 7,
      storage: Math.min(95, (realSystemData?.storage || 89) + 6),
      batteryLevel: 76,
      cameras: [
        formatCameraForDisplay('camera-5', 'NestCam', 'red', 5),
        formatCameraForDisplay('camera-6', 'CritterCam', 'teal', 6)
      ],
      recentSightings: getCombinedSightings(['NestCam', 'CritterCam'])
    }
  ];

  const handleBoxClick = (boxId) => {
    setModalType('header');
    setModalData(squirrelBoxes.find(box => box.id === boxId));
    setModalOpen(true);
  };

  const handleCameraLiveView = (camera, boxName) => {
    setLiveCameraData({
      ...camera,
      boxName: boxName,
      apiName: camera.name // Ensure we have the correct API name
    });
    setShowLiveCameraView(true);
  };

  return (
    <div style={{ 
      padding: '2rem', 
      background: 'linear-gradient(135deg, #0f1419 0%, #1a2332 100%)', 
      minHeight: '100vh',
      color: '#e0e0e0' 
    }}>
      {/* Modal */}
      {modalOpen && (
        <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
          {modalType === 'header' && modalData && (
            <div style={{ width: '100%', maxWidth: '480px' }}>
              {/* Header with SB name, sensor data, and close button */}
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '1.5rem',
                paddingBottom: '1rem',
                borderBottom: '2px solid rgba(139, 90, 43, 0.6)'
              }}>
                {/* Left: SB Info */}
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{
                      display: 'inline-block',
                      width: '14px',
                      height: '14px',
                      borderRadius: '50%',
                      background: (modalData.batteryLevel > 50 && Math.round(modalData.storage) > 30) ? '#76b900' : (modalData.batteryLevel > 20 ? '#f39c12' : '#dc3545'),
                      marginRight: '0.6rem',
                      border: '2px solid #223a2c'
                    }}></span>
                    <h1 style={{ 
                      fontWeight: 800, 
                      color: '#f5e6d3', 
                      fontSize: '1.6rem',
                      margin: 0,
                      textShadow: '0 2px 8px rgba(0,0,0,0.8), 0 0 12px rgba(245,230,211,0.3)'
                    }}>{modalData.name}</h1>
                  </div>
                  <div style={{ 
                    fontSize: '0.95rem', 
                    color: '#e0d0b8',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                    textShadow: '0 1px 4px rgba(0,0,0,0.7)'
                  }}>
                    <span>📍</span>
                    {modalData.location}
                  </div>
                </div>

                {/* Center: Ultra-Compact Sensor Data */}
                <div style={{ 
                  display: 'flex', 
                  gap: '0.3rem',
                  alignItems: 'center'
                }}>
                  <div style={{ textAlign: 'center', padding: '0.25rem', background: 'rgba(243,156,18,0.4)', borderRadius: '4px', minWidth: '36px', boxShadow: '0 2px 6px rgba(0,0,0,0.3)' }}>
                    <div style={{ fontSize: '0.8rem' }}>🌡️</div>
                    <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#f39c12' }}>
                      {Math.round(Number(modalData.temperature))}°
                    </div>
                  </div>
                  
                  <div style={{ textAlign: 'center', padding: '0.25rem', background: 'rgba(52,152,219,0.4)', borderRadius: '4px', minWidth: '36px', boxShadow: '0 2px 6px rgba(0,0,0,0.3)' }}>
                    <div style={{ fontSize: '0.8rem' }}>💧</div>
                    <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#3498db' }}>
                      {Math.round(Number(modalData.humidity))}%
                    </div>
                  </div>

                  <div style={{ textAlign: 'center', padding: '0.25rem', background: 'rgba(118,185,0,0.4)', borderRadius: '4px', minWidth: '36px', boxShadow: '0 2px 6px rgba(0,0,0,0.3)' }}>
                    <div style={{ fontSize: '0.8rem' }}>🔋</div>
                    <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#76b900' }}>
                      {modalData.batteryLevel}%
                    </div>
                  </div>

                  <div style={{ textAlign: 'center', padding: '0.25rem', background: 'rgba(230,126,34,0.4)', borderRadius: '4px', minWidth: '36px', boxShadow: '0 2px 6px rgba(0,0,0,0.3)' }}>
                    <div style={{ fontSize: '0.8rem' }}>💾</div>
                    <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#e67e22' }}>
                      {Math.round(modalData.storage)}%
                    </div>
                  </div>
                </div>

                {/* Right: Close Button */}
                <button
                  onClick={() => setModalOpen(false)}
                  style={{
                    background: 'rgba(139, 90, 43, 0.5)',
                    color: '#f5e6d3',
                    border: '2px solid rgba(139, 90, 43, 0.7)',
                    borderRadius: '6px',
                    padding: '0.4rem 0.8rem',
                    cursor: 'pointer',
                    fontWeight: '700',
                    fontSize: '1rem',
                    marginLeft: '1rem',
                    boxShadow: '0 3px 8px rgba(0,0,0,0.3)',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = 'rgba(139, 90, 43, 0.7)';
                    e.target.style.color = '#ffffff';
                    e.target.style.transform = 'scale(1.05)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = 'rgba(139, 90, 43, 0.5)';
                    e.target.style.color = '#f5e6d3';
                    e.target.style.transform = 'scale(1)';
                  }}
                >
                  ✕
                </button>
              </div>              {/* Camera Feeds - Side by side layout */}
              <div style={{ 
                display: 'flex', 
                gap: '0.8rem',
                marginBottom: '1.5rem'
              }}>
                {modalData.cameras.map((cam, idx) => (
                  <div key={idx} style={{ 
                    borderRadius: '10px', 
                    border: `2px solid ${cam.status === 'live' ? '#76b900' : '#666'}`,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    flex: '1',
                    minWidth: '180px',
                    overflow: 'hidden'
                  }}>
                    {/* Full-size Camera thumbnail with overlays */}
                    <div style={{
                      width: '100%',
                      height: '150px',
                      background: cam.status === 'live' ? 'radial-gradient(circle, rgba(76,175,80,0.15), transparent)' : 'rgba(60,60,60,0.5)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      overflow: 'hidden',
                      position: 'relative'
                    }}>
                      {cam.status === 'live' && cam.thumbnailUrl ? (
                        <img 
                          src={`${cam.thumbnailUrl}?t=${Date.now()}`}
                          alt={`${cam.name} thumbnail`}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                          }}
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'block';
                          }}
                        />
                      ) : null}
                      <span 
                        style={{ 
                          fontSize: '3rem', 
                          color: cam.status === 'live' ? '#76b900' : '#888',
                          display: (cam.status === 'live' && cam.thumbnailUrl) ? 'none' : 'block'
                        }}
                      >
                        📹
                      </span>
                      
                      {/* Camera name overlay - bottom left */}
                      <div style={{
                        position: 'absolute',
                        bottom: '6px',
                        left: '6px',
                        background: 'rgba(0,0,0,0.7)',
                        color: 'white',
                        fontSize: '0.8rem',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontWeight: 'bold',
                        backdropFilter: 'blur(2px)'
                      }}>{cam.name}</div>
                      
                      {/* Camera Status Indicator */}
                      <div style={{
                        position: 'absolute',
                        top: '6px',
                        right: '6px',
                        background: cam.status === 'recent-activity' ? '#dc3545' : '#6c757d',
                        color: 'white',
                        fontSize: '0.6rem',
                        padding: '3px 6px',
                        borderRadius: '3px',
                        fontWeight: 'bold',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
                        textTransform: 'uppercase'
                      }}>
                        {cam.status === 'recent-activity' ? 'LIVE' : (cam.lastSeen || 'OFFLINE')}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Recent Activity - Compact horizontal list */}
              <div style={{ 
                borderRadius: '10px', 
                padding: '0.8rem'
              }}>
                <h3 style={{ 
                  color: '#87d96e', 
                  fontSize: '1.1rem', 
                  marginBottom: '0.8rem',
                  textAlign: 'center',
                  fontWeight: 800,
                  textShadow: '0 2px 8px rgba(0,0,0,0.8), 0 0 12px rgba(135,217,110,0.3)'
                }}>Recent Activity</h3>
                
                {modalData.recentSightings && modalData.recentSightings.length > 0 ? (
                  <div style={{ display: 'flex', gap: '0.8rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                    {modalData.recentSightings.slice(0, 4).map((sighting, idx) => (
                      <div key={idx} style={{ 
                        textAlign: 'center',
                        padding: '0.6rem',
                        background: 'rgba(118,185,0,0.5)',
                        borderRadius: '6px',
                        border: '1px solid rgba(76,175,80,0.6)',
                        minWidth: '80px',
                        boxShadow: '0 3px 8px rgba(0,0,0,0.3)'
                      }}>
                        {/* Thumbnail image or fallback emoji */}
                        {sighting.thumbnail_url ? (
                          <div style={{
                            width: '60px',
                            height: '45px',
                            borderRadius: '4px',
                            overflow: 'hidden',
                            border: '1px solid rgba(76, 175, 80, 0.3)',
                            margin: '0 auto 0.2rem auto'
                          }}>
                            <img 
                              src={sighting.thumbnail_url}
                              alt={`${sighting.species} sighting`}
                              style={{
                                width: '100%',
                                height: '100%',
                                objectFit: 'cover'
                              }}
                              onError={(e) => {
                                // Fallback to emoji if image fails to load
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'block';
                              }}
                            />
                            <div style={{ 
                              fontSize: '1.5rem', 
                              marginBottom: '0.2rem',
                              display: 'none',
                              paddingTop: '10px'
                            }}>{sighting.image}</div>
                          </div>
                        ) : (
                          <div style={{ fontSize: '1.5rem', marginBottom: '0.2rem' }}>{sighting.image}</div>
                        )}
                        <div style={{ 
                          fontSize: '0.8rem', 
                          fontWeight: 600, 
                          color: '#e0e0e0',
                          marginBottom: '0.1rem'
                        }}>{sighting.species}</div>
                        <div style={{ 
                          fontSize: '0.7rem', 
                          color: '#8fbc8f'
                        }}>{sighting.time}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ 
                    textAlign: 'center',
                    padding: '0.8rem',
                    color: '#8fbc8f',
                    fontSize: '0.9rem'
                  }}>
                    <div style={{ fontSize: '1.5rem', marginBottom: '0.3rem' }}>😴</div>
                    No recent activity
                  </div>
                )}
              </div>
            </div>
          )}
          {modalType === 'camera' && modalData && (
            <div>
              <h2 style={{ color: '#76b900', marginBottom: '1rem' }}>{modalData.name} Camera</h2>
              <p><strong>Location:</strong> {modalData.location}</p>
              <p><strong>Status:</strong> {modalData.status}</p>
              {/* Live View or Sighting Clip */}
              {!selectedSighting ? (
                <div style={{
                  width: '100%',
                  height: '400px',
                  maxWidth: '800px',
                  background: modalData.status === 'live' ? 'radial-gradient(circle, rgba(76,175,80,0.15), transparent)' : 'rgba(60,60,60,0.5)',
                  borderRadius: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '1.5rem auto',
                  position: 'relative',
                  boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
                }}>
                  {modalData.status === 'live' ? (
                    <span style={{ fontSize: '5rem', color: '#76b900', opacity: 0.7 }}>📹</span>
                  ) : (
                    <span style={{ fontSize: '3rem', color: '#888' }}>OFFLINE</span>
                  )}
                  {/* LIVE badge */}
                  {modalData.status === 'live' && (
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
                      boxShadow: '0 2px 8px rgba(76,175,80,0.08)'
                    }}>LIVE</div>
                  )}
                </div>
              ) : (
                <div style={{
                  width: '100%',
                  minHeight: '220px',
                  background: 'rgba(46,204,113,0.08)',
                  borderRadius: '12px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '1rem 0',
                  boxShadow: '0 4px 16px rgba(0,0,0,0.2)'
                }}>
                  <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>{selectedSighting.image}</div>
                  <div style={{ color: '#e0e0e0', fontWeight: 700, fontSize: '1.2rem' }}>{selectedSighting.species}</div>
                  <div style={{ color: '#8fbc8f', fontSize: '1rem', marginBottom: '0.5rem' }}>{selectedSighting.time}</div>
                  <button
                    onClick={() => setSelectedSighting(null)}
                    style={{
                      background: 'rgba(46,204,113,0.15)',
                      color: '#76b900',
                      border: 'none',
                      borderRadius: '6px',
                      padding: '0.5rem 1.2rem',
                      cursor: 'pointer',
                      fontWeight: '700',
                      fontSize: '1rem',
                      marginTop: '1rem',
                      boxShadow: '0 2px 8px rgba(76,175,80,0.08)'
                    }}
                  >
                    ← Back to Live View
                  </button>
                </div>
              )}
              {/* Recent Sightings Carousel */}
              <div style={{ marginTop: '2rem' }}>
                <h3 style={{ color: '#76b900', fontSize: '1.1rem', marginBottom: '0.5rem' }}>Recent Sightings</h3>
                <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                  {(modalData.recentSightings || []).map((s, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'rgba(46,204,113,0.08)',
                        borderRadius: '8px',
                        padding: '0.5rem 1rem',
                        minWidth: '90px',
                        textAlign: 'center',
                        cursor: 'pointer',
                        border: selectedSighting && selectedSighting.id === s.id ? '2px solid #76b900' : '2px solid transparent',
                        boxShadow: selectedSighting && selectedSighting.id === s.id ? '0 2px 8px rgba(76,175,80,0.08)' : 'none'
                      }}
                      onClick={() => setSelectedSighting(s)}
                    >
                      {/* Thumbnail image or fallback emoji */}
                      {s.thumbnail_url ? (
                        <div style={{
                          width: '70px',
                          height: '52px',
                          borderRadius: '4px',
                          overflow: 'hidden',
                          border: '1px solid rgba(76, 175, 80, 0.3)',
                          margin: '0 auto 0.5rem auto'
                        }}>
                          <img 
                            src={s.thumbnail_url}
                            alt={`${s.species} sighting`}
                            style={{
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover'
                            }}
                            onError={(e) => {
                              // Fallback to emoji if image fails to load
                              e.target.style.display = 'none';
                              e.target.nextSibling.style.display = 'block';
                            }}
                          />
                          <div style={{ 
                            fontSize: '2rem',
                            display: 'none',
                            paddingTop: '10px'
                          }}>{s.image}</div>
                        </div>
                      ) : (
                        <div style={{ fontSize: '2rem' }}>{s.image}</div>
                      )}
                      <div style={{ color: '#e0e0e0', fontWeight: 700, fontSize: '0.95rem' }}>{s.species}</div>
                      <div style={{ color: '#8fbc8f', fontSize: '0.8rem' }}>{s.time}</div>
                      {s.camera && (
                        <div style={{ color: '#76b900', fontSize: '0.7rem', marginTop: '0.2rem' }}>📹 {s.camera}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          {modalType === 'sighting' && modalData && (
            <div>
              <h2 style={{ color: '#76b900', marginBottom: '1rem' }}>Sighting: {modalData.species}</h2>
              
              {/* Full-size thumbnail or fallback emoji */}
              {modalData.thumbnail_url ? (
                <div style={{
                  width: '100%',
                  maxWidth: '400px',
                  height: '300px',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  border: '2px solid rgba(76, 175, 80, 0.3)',
                  margin: '1rem auto',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <img 
                    src={modalData.thumbnail_url}
                    alt={`${modalData.species} sighting`}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover'
                    }}
                    onError={(e) => {
                      // Fallback to emoji if image fails to load
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div style={{ 
                    fontSize: '3rem', 
                    display: 'none'
                  }}>{modalData.image}</div>
                </div>
              ) : (
                <div style={{ fontSize: '3rem', margin: '1rem 0', textAlign: 'center' }}>{modalData.image}</div>
              )}
              
              <p><strong>Time:</strong> {modalData.time}</p>
              <p><strong>Species:</strong> {modalData.species}</p>
              {modalData.camera && (
                <p><strong>Camera:</strong> 📹 {modalData.camera}</p>
              )}
              {modalData.behavior && (
                <p><strong>Behavior:</strong> {modalData.behavior}</p>
              )}
              {modalData.confidence && (
                <p><strong>Confidence:</strong> {Math.round(modalData.confidence * 100)}%</p>
              )}
            </div>
          )}
        </Modal>
      )}
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '2rem'
      }}>
        <h2 style={{ 
          fontSize: '1.8rem', 
          color: '#f0f0f0', 
          margin: 0, 
          fontWeight: 600 
        }}>
          My SquirrelBoxes
        </h2>
        <div style={{
          fontSize: '0.9rem',
          color: '#8fbc8f'
        }}>
          {squirrelBoxes.length} devices active • {allSightings.length} recent sightings
        </div>
      </div>

      {/* 3-Card Layout */}
      <div className="dashboard-grid" style={{
        display: 'grid',
        gap: '1.5rem',
        alignItems: 'stretch',
        minHeight: '450px',
        gridTemplateColumns: '1fr',
        maxWidth: '1200px',
        margin: '0 auto',
      }}>
        {squirrelBoxes.map((box, index) => (
          <div 
            key={box.id}
            style={{
              flex: '1',
              background: 'rgba(20, 30, 40, 0.95)',
              borderRadius: '12px',
              padding: '1.5rem',
              border: '1px solid rgba(76, 175, 80, 0.3)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)',
              minWidth: '0',
              display: 'flex',
              flexDirection: 'column'
            }}
            // Card header click
            onClick={(e) => {
              // Only trigger modal if header or card background is clicked
              if (e.target.closest('.card-header')) {
                handleBoxClick(box.id);
              }
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.4)';
              e.currentTarget.style.borderColor = 'rgba(76, 175, 80, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.3)';
              e.currentTarget.style.borderColor = 'rgba(76, 175, 80, 0.3)';
            }}
          >
            {/* Card Header */}
            <div className="card-header" style={{
              marginBottom: '1rem',
              paddingBottom: '0.75rem',
              borderBottom: '1px solid rgba(76, 175, 80, 0.2)',
              cursor: 'pointer'
            }}
              onClick={() => {
                setModalType('header');
                setModalData(box);
                setModalOpen(true);
              }}
            >
              <h3 style={{
                fontSize: '1.25rem',
                color: '#f0f0f0',
                margin: '0 0 0.25rem 0',
                fontWeight: 700
              }}>
                {box.name}
              </h3>
              <p style={{
                color: '#8fbc8f',
                margin: 0,
                fontSize: '0.85rem',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                📍 {box.location}
              </p>
            </div>

            {/* Large Camera Feeds */}
            <div style={{ marginBottom: '1rem', flex: 1 }}>
              <h4 style={{
                fontSize: '0.9rem',
                color: '#8fbc8f',
                margin: '0 0 0.75rem 0',
                fontWeight: 600
              }}>
                📹 Live Cameras
              </h4>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '0.75rem',
                height: '140px'
              }}>
                {box.cameras.map((camera, cameraIndex) => (
                  <div
                    key={cameraIndex}
                    style={{
                      borderRadius: '8px',
                      background: camera.status === 'live' 
                        ? 'linear-gradient(135deg, #1a2a3a, #2a3a4a)' 
                        : 'rgba(40, 40, 40, 0.8)',
                      border: `2px solid ${camera.status === 'live' ? '#76b900' : '#666'}`,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                      position: 'relative',
                      overflow: 'hidden',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                    onClick={() => {
                      handleCameraLiveView(camera, box.name);
                    }}
                    onMouseEnter={(e) => {
                      if (camera.status === 'live') {
                        e.target.style.borderColor = '#8fbc8f';
                        e.target.style.transform = 'scale(1.02)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (camera.status === 'live') {
                        e.target.style.borderColor = '#76b900';
                        e.target.style.transform = 'scale(1)';
                      }
                    }}
                  >
                    {/* Camera Status Indicator */}
                    <div style={{
                      position: 'absolute',
                      top: '6px',
                      right: '6px',
                      background: camera.status === 'live' ? '#dc3545' : '#6c757d',
                      color: 'white',
                      fontSize: '0.7rem',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      fontWeight: 'bold',
                      zIndex: 10,
                      boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
                    }}>
                      {camera.status === 'live' ? 'LIVE' : camera.lastSeen}
                    </div>
                    
                    {/* Camera Feed */}
                    {camera.thumbnailUrl ? (
                      <img 
                        src={camera.thumbnailUrl}
                        alt={`${camera.name} ${camera.status === 'live' ? 'live feed' : 'last captured'}`}
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                          borderRadius: '6px'
                        }}
                        onError={(e) => {
                          // Show fallback if image fails to load
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    
                    {/* Fallback display */}
                    <div style={{
                      width: '100%',
                      height: '100%',
                      display: !camera.thumbnailUrl ? 'flex' : 'none',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                      background: camera.status === 'live' ? 'linear-gradient(135deg, #76b900, #8fbc8f)' : 'linear-gradient(135deg, #6c757d, #adb5bd)',
                      borderRadius: '6px'
                    }}>
                      <div style={{
                        fontSize: '2.5rem',
                        color: camera.status === 'live' ? '#8fbc8f' : '#666',
                        opacity: 0.7,
                        marginBottom: '0.25rem'
                      }}>
                        📹
                      </div>
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
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Sightings */}
            <div style={{ flex: 1 }}>
              <h4 style={{
                fontSize: '0.9rem',
                color: '#8fbc8f',
                margin: '0 0 0.5rem 0',
                fontWeight: 600
              }}>
                🐿️ Recent Sightings
              </h4>
              <div style={{
                maxHeight: '160px',
                overflow: 'hidden'
              }}>
                {box.recentSightings.slice(0, 4).map((sighting, sightingIndex) => (
                  <div
                    key={sighting.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.2rem 0',
                      borderBottom: sightingIndex < 3 ? '1px solid rgba(76, 175, 80, 0.1)' : 'none',
                      cursor: 'pointer'
                    }}
                    onClick={() => {
                      setModalType('sighting');
                      setModalData(sighting);
                      setModalOpen(true);
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                      overflow: 'hidden',
                      minWidth: 0
                    }}>
                      {/* Thumbnail image or fallback emoji */}
                      {sighting.thumbnail_url ? (
                        <div style={{
                          width: '32px',
                          height: '24px',
                          borderRadius: '4px',
                          overflow: 'hidden',
                          border: '1px solid rgba(76, 175, 80, 0.3)',
                          flexShrink: 0
                        }}>
                          <img 
                            src={sighting.thumbnail_url}
                            alt={`${sighting.species} sighting`}
                            style={{
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover'
                            }}
                            onError={(e) => {
                              // Fallback to emoji if image fails to load
                              e.target.style.display = 'none';
                              e.target.nextSibling.style.display = 'inline';
                            }}
                          />
                          <span style={{ 
                            fontSize: '0.8rem', 
                            display: 'none'
                          }}>{sighting.image}</span>
                        </div>
                      ) : (
                        <span style={{ fontSize: '0.8rem' }}>{sighting.image}</span>
                      )}
                      <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0, gap: '0.2rem' }}>
                        <span style={{
                          fontSize: '0.75rem',
                          color: '#e0e0e0',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          lineHeight: '1'
                        }}>
                          {sighting.species}
                        </span>
                        {sighting.camera && (
                          <span style={{
                            fontSize: '0.6rem',
                            color: '#76b900',
                            opacity: 0.8,
                            fontWeight: 500,
                            lineHeight: '1'
                          }}>
                            📹 {sighting.camera}
                          </span>
                        )}
                      </div>
                    </div>
                    <span style={{
                      fontSize: '0.7rem',
                      color: '#888',
                      whiteSpace: 'nowrap',
                      marginLeft: '0.5rem'
                    }}>
                      {sighting.time}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
      {/* Responsive grid CSS */}
      <style>{`
        @media (min-width: 900px) {
          .dashboard-grid {
            grid-template-columns: repeat(3, 1fr) !important;
          }
        }
      `}</style>

      {/* Status Bar */}
      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        background: 'rgba(20, 30, 40, 0.6)',
        borderRadius: '8px',
        border: '1px solid rgba(76, 175, 80, 0.2)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '0.9rem',
        color: '#8fbc8f'
      }}>
        <div>
          System Status: {systemHealth.status === 'online' ? '🟢 Online' : '🔴 Offline'}
        </div>
        <div>
          Last Updated: {currentTime.toLocaleTimeString()}
        </div>
      </div>

      {/* On-Demand Live Camera View */}
      {showLiveCameraView && liveCameraData && (
        <OnDemandCameraView 
          camera={liveCameraData}
          onClose={() => {
            setShowLiveCameraView(false);
            setLiveCameraData(null);
          }}
        />
      )}
    </div>
  );
}

// Defensive: Modal import at top
import Modal from './Modal';

export default FigmaStyleDashboard;
