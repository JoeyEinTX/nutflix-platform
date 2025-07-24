import React, { useState, useEffect } from 'react';

function FigmaStyleDashboard({ systemHealth }) {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedBox, setSelectedBox] = useState(0);

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
        { name: "NestCam", location: "Interior", status: "live" },
        { name: "OuterCam", location: "Exterior", status: "live" }
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
        { name: "NestCam", location: "Interior", status: "live" },
        { name: "OuterCam", location: "Exterior", status: "live" }
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

  const currentBox = squirrelBoxes[selectedBox];

  const handleBoxClick = (boxId) => {
    console.log(`Opening modal for SquirrelBox: ${boxId}`);
    alert(`Opening detailed view for ${squirrelBoxes.find(box => box.id === boxId)?.name}`);
  };

  return (
    <div style={{ padding: 0, background: 'transparent', color: '#e0e0e0' }}>
      {/* SquirrelBoxes Carousel Section */}
      <div style={{ width: '100%' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '2rem', 
          padding: '0 1rem' 
        }}>
          <h2 style={{ 
            fontSize: '1.8rem', 
            color: '#f0f0f0', 
            margin: 0, 
            fontWeight: 600 
          }}>
            My SquirrelBoxes
          </h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button 
              style={{
                background: 'rgba(30, 45, 55, 0.8)',
                border: '1px solid #76b900',
                color: '#8fbc8f',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                fontSize: '1.2rem',
                transition: 'all 0.3s ease'
              }}
              onClick={() => setSelectedBox(prev => prev > 0 ? prev - 1 : squirrelBoxes.length - 1)}
            >
              ←
            </button>
            <span style={{ color: '#b0b0b0', fontSize: '0.9rem', fontWeight: 500 }}>
              {selectedBox + 1} of {squirrelBoxes.length}
            </span>
            <button 
              style={{
                background: 'rgba(30, 45, 55, 0.8)',
                border: '1px solid #76b900',
                color: '#8fbc8f',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                fontSize: '1.2rem',
                transition: 'all 0.3s ease'
              }}
              onClick={() => setSelectedBox(prev => prev < squirrelBoxes.length - 1 ? prev + 1 : 0)}
            >
              →
            </button>
          </div>
        </div>

        {/* SquirrelBox Card */}
        <div 
          style={{
            background: 'rgba(20, 30, 40, 0.95)',
            borderRadius: '16px',
            padding: '2rem',
            border: '1px solid rgba(76, 175, 80, 0.3)',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            marginBottom: '2rem',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
          }}
          onClick={() => handleBoxClick(currentBox.id)}
        >
          {/* Card Header with Name and Sensor Data */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginBottom: '2rem',
            paddingBottom: '1rem',
            borderBottom: '1px solid rgba(76, 175, 80, 0.2)',
            flexWrap: 'wrap',
            gap: '1rem'
          }}>
            <div>
              <h3 style={{
                fontSize: '1.5rem',
                color: '#f0f0f0',
                margin: '0 0 0.5rem 0',
                fontWeight: 700
              }}>
                {currentBox.name}
              </h3>
              <p style={{
                color: '#8fbc8f',
                margin: 0,
                fontSize: '0.95rem'
              }}>
                📍 {currentBox.location}
              </p>
            </div>
            <div style={{
              display: 'flex',
              gap: '1rem',
              flexWrap: 'wrap'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.75rem',
                background: 'rgba(30, 45, 55, 0.6)',
                borderRadius: '8px',
                border: '1px solid rgba(76, 175, 80, 0.2)',
                fontSize: '0.9rem',
                color: '#e0e0e0'
              }}>
                <span>🌡️</span>
                <span>{Math.round(currentBox.temperature)}°F</span>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.75rem',
                background: 'rgba(30, 45, 55, 0.6)',
                borderRadius: '8px',
                border: '1px solid rgba(76, 175, 80, 0.2)',
                fontSize: '0.9rem',
                color: '#e0e0e0'
              }}>
                <span>💧</span>
                <span>{Math.round(currentBox.humidity)}%</span>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.75rem',
                background: 'rgba(30, 45, 55, 0.6)',
                borderRadius: '8px',
                border: '1px solid rgba(76, 175, 80, 0.2)',
                fontSize: '0.9rem',
                color: '#e0e0e0'
              }}>
                <span>💾</span>
                <span>{Math.round(currentBox.storage)}%</span>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 0.75rem',
                background: 'rgba(30, 45, 55, 0.6)',
                borderRadius: '8px',
                border: '1px solid rgba(76, 175, 80, 0.2)',
                fontSize: '0.9rem',
                color: '#e0e0e0'
              }}>
                <span>🔋</span>
                <span>{currentBox.batteryLevel}%</span>
              </div>
            </div>
          </div>

          {/* Live Camera Feeds */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '1.5rem',
            marginBottom: '2rem'
          }}>
            {currentBox.cameras.map((camera, index) => (
              <div key={index} style={{
                position: 'relative',
                background: 'rgba(15, 25, 35, 0.8)',
                borderRadius: '12px',
                overflow: 'hidden',
                border: '1px solid rgba(76, 175, 80, 0.3)'
              }}>
                <div style={{
                  position: 'absolute',
                  top: '12px',
                  left: '12px',
                  background: camera.status === 'live' ? '#ff4444' : '#666666',
                  color: 'white',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '4px',
                  fontSize: '0.8rem',
                  fontWeight: 'bold',
                  zIndex: 10
                }}>
                  {camera.status === 'live' ? 'LIVE' : 'OFFLINE'}
                </div>
                <div style={{
                  position: 'absolute',
                  top: '12px',
                  right: '12px',
                  background: 'rgba(0, 0, 0, 0.6)',
                  color: 'white',
                  padding: '0.5rem',
                  borderRadius: '4px',
                  fontSize: '1rem',
                  zIndex: 10,
                  cursor: 'pointer'
                }}>
                  ⛶
                </div>
                <div style={{
                  aspectRatio: '16/9',
                  background: '#000',
                  position: 'relative',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'linear-gradient(135deg, rgba(20, 40, 30, 0.9) 0%, rgba(30, 60, 40, 0.9) 100%)',
                    position: 'relative'
                  }}>
                    <div style={{ fontSize: '4rem', zIndex: 2, position: 'relative' }}>🐼</div>
                    <div style={{
                      position: 'absolute',
                      bottom: '-10px',
                      left: '50%',
                      transform: 'translateX(-50%)',
                      fontSize: '2rem',
                      opacity: 0.7,
                      zIndex: 1
                    }}>🌿</div>
                  </div>
                </div>
                <div style={{
                  padding: '0.75rem',
                  background: 'rgba(30, 45, 55, 0.8)'
                }}>
                  <div style={{
                    fontSize: '1rem',
                    fontWeight: 600,
                    color: '#f0f0f0',
                    marginBottom: '0.25rem'
                  }}>
                    {camera.name}
                  </div>
                  <div style={{
                    fontSize: '0.8rem',
                    color: '#8fbc8f'
                  }}>
                    {currentBox.name} - {camera.location}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Recent Sightings */}
          <div style={{ marginBottom: '1.5rem' }}>
            <h4 style={{
              color: '#f0f0f0',
              marginBottom: '1rem',
              fontSize: '1.2rem',
              fontWeight: 600
            }}>
              Recent Sightings
            </h4>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem'
            }}>
              {currentBox.recentSightings.slice(0, 4).map((sighting) => (
                <div key={sighting.id} style={{
                  background: 'rgba(15, 25, 35, 0.8)',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  border: '1px solid rgba(76, 175, 80, 0.2)',
                  transition: 'transform 0.3s ease'
                }}>
                  <div style={{
                    height: '80px',
                    background: 'linear-gradient(135deg, #2d4a2d 0%, #3a5c3a 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <div style={{ fontSize: '2rem' }}>{sighting.image}</div>
                  </div>
                  <div style={{ padding: '0.75rem' }}>
                    <div style={{
                      fontWeight: 600,
                      color: '#f0f0f0',
                      marginBottom: '0.25rem',
                      fontSize: '0.85rem'
                    }}>
                      {sighting.species}
                    </div>
                    <div style={{
                      fontSize: '0.75rem',
                      color: '#b0b0b0'
                    }}>
                      ⏰ {sighting.time}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Click to expand indicator */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '1rem',
            background: 'rgba(76, 175, 80, 0.1)',
            borderRadius: '8px',
            marginTop: '1rem',
            color: '#8fbc8f',
            fontSize: '0.9rem',
            border: '1px solid rgba(76, 175, 80, 0.2)'
          }}>
            <span>Click to view details</span>
            <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>↗</span>
          </div>
        </div>

        {/* Carousel Dots */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '0.5rem',
          marginTop: '1rem'
        }}>
          {squirrelBoxes.map((_, index) => (
            <button
              key={index}
              style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                border: 'none',
                background: index === selectedBox ? '#76b900' : 'rgba(176, 176, 176, 0.4)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                transform: index === selectedBox ? 'scale(1.2)' : 'scale(1)'
              }}
              onClick={() => setSelectedBox(index)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default FigmaStyleDashboard;
