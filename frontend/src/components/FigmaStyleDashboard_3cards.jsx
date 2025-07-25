import React, { useState, useEffect } from 'react';

function FigmaStyleDashboard({ systemHealth }) {
  // Camera modal state
  const [selectedSighting, setSelectedSighting] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState(null); // 'header' | 'camera' | 'sighting'
  const [modalData, setModalData] = useState(null);

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

  const handleBoxClick = (boxId) => {
    setModalType('header');
    setModalData(squirrelBoxes.find(box => box.id === boxId));
    setModalOpen(true);
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
            <div style={{ display: 'flex', flexDirection: 'row', gap: '2rem', minWidth: '400px' }}>
              {/* Sidebar: Sensor Data */}
              <div style={{ minWidth: '140px', background: 'rgba(46,204,113,0.05)', borderRadius: '10px', padding: '1rem 0.75rem', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-start', boxShadow: '0 2px 8px rgba(76,175,80,0.05)', marginRight: '1rem' }}>
                {/* Health Indicator */}
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.7rem' }}>
                  <span style={{
                    display: 'inline-block',
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    background: (modalData.batteryLevel > 50 && modalData.storage > 30) ? '#76b900' : (modalData.batteryLevel > 20 ? '#f39c12' : '#dc3545'),
                    marginRight: '0.4rem',
                    border: '2px solid #223a2c'
                  }}></span>
                  <span style={{ fontWeight: 700, color: '#e0e0e0', fontSize: '1rem' }}>{modalData.name}</span>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#8fbc8f', marginBottom: '0.5rem' }}>📍 {modalData.location}</div>
                <div style={{ fontSize: '0.85rem', color: '#f39c12', marginBottom: '0.3rem' }}>🌡️ {Number(modalData.temperature).toFixed(1)}°C</div>
                <div style={{ fontSize: '0.85rem', color: '#3498db', marginBottom: '0.3rem' }}>💧 {Number(modalData.humidity).toFixed(1)}%</div>
                <div style={{ fontSize: '0.85rem', color: '#76b900', marginBottom: '0.3rem' }}>🔋 {modalData.batteryLevel}%</div>
                <div style={{ fontSize: '0.85rem', color: '#e67e22', marginBottom: '0.3rem' }}>💾 {modalData.storage}%</div>
                {/* Progress Bars */}
                <div style={{ width: '100%', marginTop: '0.5rem' }}>
                  <div style={{ fontSize: '0.7rem', color: '#8fbc8f' }}>Battery</div>
                  <div style={{ background: '#223a2c', borderRadius: '4px', height: '6px', width: '100%' }}>
                    <div style={{ background: '#76b900', height: '6px', borderRadius: '4px', width: `${modalData.batteryLevel}%` }}></div>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#8fbc8f', marginTop: '0.3rem' }}>Storage</div>
                  <div style={{ background: '#223a2c', borderRadius: '4px', height: '6px', width: '100%' }}>
                    <div style={{ background: '#e67e22', height: '6px', borderRadius: '4px', width: `${modalData.storage}%` }}></div>
                  </div>
                </div>
              </div>
              {/* Main Info */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-start' }}>
                {/* Last Sighting */}
                <div style={{ marginBottom: '0.7rem', textAlign: 'left' }}>
                  <span style={{ color: '#8fbc8f', fontSize: '0.95rem' }}>Last Sighting:</span>
                  <span style={{ color: '#e0e0e0', fontWeight: 700, fontSize: '1.05rem', marginLeft: '0.5rem' }}>{modalData.recentSightings[0]?.species || 'N/A'}</span>
                  <span style={{ fontSize: '1.2rem', marginLeft: '0.5rem' }}>{modalData.recentSightings[0]?.image || ''}</span>
                  <span style={{ color: '#8fbc8f', fontSize: '0.9rem', marginLeft: '0.5rem' }}>{modalData.recentSightings[0]?.time || ''}</span>
                </div>
                {/* Camera Feed Thumbnails */}
                <div style={{ display: 'flex', gap: '1.2rem', justifyContent: 'flex-start', alignItems: 'center', marginBottom: '0.7rem' }}>
                  {modalData.cameras.map((cam, idx) => (
                    <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer' }}>
                      <div style={{
                        width: '48px',
                        height: '32px',
                        background: cam.status === 'live' ? 'radial-gradient(circle, rgba(76,175,80,0.15), transparent)' : 'rgba(60,60,60,0.5)',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginBottom: '0.2rem',
                        border: `2px solid ${cam.status === 'live' ? '#76b900' : '#888'}`
                      }}>
                        <span style={{ fontSize: '1.5rem', color: cam.status === 'live' ? '#76b900' : '#888' }}>📹</span>
                      </div>
                      <span style={{ fontSize: '0.7rem', color: '#e0e0e0' }}>{cam.name}</span>
                    </div>
                  ))}
                </div>
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
                      <div style={{ fontSize: '2rem' }}>{s.image}</div>
                      <div style={{ color: '#e0e0e0', fontWeight: 700, fontSize: '0.95rem' }}>{s.species}</div>
                      <div style={{ color: '#8fbc8f', fontSize: '0.8rem' }}>{s.time}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          {modalType === 'sighting' && modalData && (
            <div>
              <h2 style={{ color: '#76b900', marginBottom: '1rem' }}>Sighting: {modalData.species}</h2>
              <div style={{ fontSize: '3rem', margin: '1rem 0' }}>{modalData.image}</div>
              <p><strong>Time:</strong> {modalData.time}</p>
              <p><strong>Species:</strong> {modalData.species}</p>
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
          {squirrelBoxes.length} devices active
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
                      setModalType('camera');
                      setModalData({ ...camera, name: box.name, location: camera.location });
                      setModalOpen(true);
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
                    
                    {/* Camera Feed Placeholder */}
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
                      borderBottom: sightingIndex < 2 ? '1px solid rgba(76, 175, 80, 0.1)' : 'none',
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
    </div>
  );
}
import Modal from './Modal';

export default FigmaStyleDashboard;
