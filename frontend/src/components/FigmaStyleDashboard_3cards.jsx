import React, { useState, useEffect } from 'react';

function FigmaStyleDashboard({ systemHealth }) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Mock data for multiple SquirrelBoxes
  const squirrelBoxes = [
    {
      id: 1,
      name: "Hero",
      location: "Backyard Oak Tree",
      temperature: systemHealth.temperature,
      humidity: systemHealth.humidity,
      storage: systemHealth.storage,
      batteryLevel: 87,
      cameras: [
        { name: "CritterCam", location: "Wildlife Area", status: "live" },
        { name: "NestCam", location: "Nesting Box", status: "live" }
      ],
      recentSightings: [
        { id: 1, species: "Eastern Gray Squirrel", time: "2 min ago", image: "🐿️" },
        { id: 2, species: "Red Squirrel", time: "15 min ago", image: "🐿️" },
        { id: 3, species: "Flying Squirrel", time: "1 hour ago", image: "🐿️" },
        { id: 4, species: "Chipmunk", time: "2 hours ago", image: "🐿️" }
      ]
    },
    {
      id: 2,
      name: "Garden Guardian",
      location: "Front Yard Maple",
      temperature: 24.3,
      humidity: 72,
      storage: 62,
      batteryLevel: 94,
      cameras: [
        { name: "CritterCam", location: "Wildlife Area", status: "offline" },
        { name: "NestCam", location: "Nesting Box", status: "offline" }
      ],
      recentSightings: [
        { id: 1, species: "Gray Squirrel", time: "5 min ago", image: "🐿️" },
        { id: 2, species: "Blue Jay", time: "20 min ago", image: "🐦" },
        { id: 3, species: "Cardinal", time: "45 min ago", image: "🐦" }
      ]
    },
    {
      id: 3,
      name: "Forest Watcher",
      location: "Pine Grove",
      temperature: 19.8,
      humidity: 58,
      storage: 89,
      batteryLevel: 76,
      cameras: [
        { name: "NestCam", location: "Interior", status: "offline" },
        { name: "OuterCam", location: "Exterior", status: "live" }
      ],
      recentSightings: [
        { id: 1, species: "Red Squirrel", time: "1 min ago", image: "🐿️" },
        { id: 2, species: "Flying Squirrel", time: "3 hours ago", image: "🐿️" }
      ]
    }
  ];

  const handleBoxClick = (boxId) => {
    console.log(`Opening modal for SquirrelBox: ${boxId}`);
    alert(`Opening detailed view for ${squirrelBoxes.find(box => box.id === boxId)?.name}`);
  };

  return (
    <div style={{ 
      padding: '2rem', 
      background: 'linear-gradient(135deg, #0f1419 0%, #1a2332 100%)', 
      minHeight: '100vh',
      color: '#e0e0e0' 
    }}>
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
          {squirrelBoxes.length} devices active
        </div>
      </div>

      {/* 3-Card Layout */}
      <div style={{
        display: 'flex',
        gap: '1.5rem',
        alignItems: 'stretch',
        minHeight: '450px'
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
            onClick={() => handleBoxClick(box.id)}
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
            <div style={{
              marginBottom: '1rem',
              paddingBottom: '0.75rem',
              borderBottom: '1px solid rgba(76, 175, 80, 0.2)'
            }}>
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
                    {camera.status === 'live' && (
                      <div style={{
                        position: 'absolute',
                        top: '6px',
                        right: '6px',
                        background: '#dc3545',
                        color: 'white',
                        fontSize: '0.7rem',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontWeight: 'bold',
                        zIndex: 10,
                        boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
                      }}>
                        LIVE
                      </div>
                    )}
                    
                    {/* Camera Feed with Real Thumbnails */}
                    <div style={{
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      alignItems: 'center',
                      background: camera.status === 'live' 
                        ? 'rgba(20, 30, 40, 0.9)' 
                        : 'rgba(60, 60, 60, 0.5)',
                      position: 'relative',
                      overflow: 'hidden'
                    }}>
                      
                      {/* Live Camera Thumbnail */}
                      {camera.status === 'live' ? (
                        <img 
                          src={`/api/stream/${camera.name}/thumbnail?t=${Math.floor(Date.now() / 5000)}`}
                          alt={`${camera.name} live feed`}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            opacity: 0.9
                          }}
                          onError={(e) => {
                            // Fallback to recent activity thumbnail if live feed fails
                            e.target.src = camera.name === 'CritterCam' ? '/api/clips/clip_001/thumbnail' : '/api/clips/clip_002/thumbnail';
                          }}
                        />
                      ) : (
                        /* Recent Activity Thumbnail for Offline Cameras */
                        <div style={{
                          width: '100%',
                          height: '100%',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'center',
                          alignItems: 'center',
                          position: 'relative'
                        }}>
                          <img 
                            src={camera.name === 'CritterCam' ? '/api/clips/clip_001/thumbnail' : '/api/clips/clip_002/thumbnail'}
                            alt="Last activity snapshot"
                            style={{
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover',
                              opacity: 0.6,
                              filter: 'grayscale(30%)'
                            }}
                            onError={(e) => {
                              // If thumbnail fails, show placeholder
                              e.target.style.display = 'none';
                              e.target.nextSibling.style.display = 'flex';
                            }}
                          />
                          {/* Fallback placeholder if image fails */}
                          <div style={{
                            position: 'absolute',
                            width: '100%',
                            height: '100%',
                            display: 'none',
                            flexDirection: 'column',
                            justifyContent: 'center',
                            alignItems: 'center'
                          }}>
                            <div style={{
                              fontSize: '2.5rem',
                              color: '#666',
                              opacity: 0.7,
                              marginBottom: '0.25rem'
                            }}>
                              📹
                            </div>
                            <div style={{
                              fontSize: '0.8rem',
                              color: '#888',
                              textAlign: 'center',
                              fontWeight: 600
                            }}>
                              {camera.name}
                            </div>
                          </div>
                          
                          {/* "Last Activity" overlay */}
                          <div style={{
                            position: 'absolute',
                            bottom: '8px',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            fontSize: '0.6rem',
                            color: 'rgba(255, 255, 255, 0.9)',
                            background: 'rgba(0, 0, 0, 0.7)',
                            padding: '2px 6px',
                            borderRadius: '3px',
                            textAlign: 'center',
                            fontWeight: 'bold'
                          }}>
                            Last Activity<br/>
                            {camera.name === 'CritterCam' ? '2:30 PM' : '12:15 PM'}
                          </div>
                        </div>
                      )}
                      
                      {/* Live overlay indicators */}
                      {camera.status === 'live' && (
                        <div style={{
                          position: 'absolute',
                          bottom: '4px',
                          left: '4px',
                          fontSize: '0.6rem',
                          color: 'rgba(255, 255, 255, 0.9)',
                          background: 'rgba(0, 0, 0, 0.7)',
                          padding: '1px 4px',
                          borderRadius: '2px',
                          fontFamily: 'monospace',
                          fontWeight: 'bold'
                        }}>
                          LIVE {new Date().toLocaleTimeString().slice(0, 8)}
                        </div>
                      )}
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
                maxHeight: '100px',
                overflow: 'hidden'
              }}>
                {box.recentSightings.slice(0, 3).map((sighting, sightingIndex) => (
                  <div
                    key={sighting.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.25rem 0',
                      borderBottom: sightingIndex < 2 ? '1px solid rgba(76, 175, 80, 0.1)' : 'none'
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      overflow: 'hidden',
                      minWidth: 0
                    }}>
                      <span style={{ fontSize: '0.8rem' }}>{sighting.image}</span>
                      <span style={{
                        fontSize: '0.75rem',
                        color: '#e0e0e0',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {sighting.species}
                      </span>
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
    </div>
  );
}

export default FigmaStyleDashboard;
