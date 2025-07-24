import React, { useState, useEffect } from 'react';

function ResearchDashboard({ systemHealth }) {
  const [sightingsData, setSightingsData] = useState([]);
  const [trendsData, setTrendsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In production, these would be real API calls to your Flask backend
    // For now, we'll simulate the data structure
    
    // Simulate /research/sightings endpoint
    const mockSightings = [
      {
        species: 'Eastern Gray Squirrel',
        behavior: 'Foraging',
        confidence: 95.2,
        camera: 'NestCam',
        motion_zone: 'Zone A',
        timestamp: '2024-01-23 14:30:15',
        clip_path: '/clips/squirrel_20240123_1430.mp4'
      },
      {
        species: 'Red Squirrel',
        behavior: 'Climbing',
        confidence: 87.8,
        camera: 'OuterCam',
        motion_zone: 'Zone B',
        timestamp: '2024-01-23 14:15:42',
        clip_path: '/clips/red_squirrel_20240123_1415.mp4'
      },
      {
        species: 'Flying Squirrel',
        behavior: 'Gliding',
        confidence: 92.1,
        camera: 'NestCam',
        motion_zone: 'Zone C',
        timestamp: '2024-01-23 13:45:20',
        clip_path: '/clips/flying_squirrel_20240123_1345.mp4'
      },
      {
        species: 'Chipmunk',
        behavior: 'Storing',
        confidence: 89.5,
        camera: 'OuterCam',
        motion_zone: 'Zone A',
        timestamp: '2024-01-23 13:20:08',
        clip_path: '/clips/chipmunk_20240123_1320.mp4'
      }
    ];

    // Simulate /research/trends endpoint
    const mockTrends = {
      labels: ['12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM'],
      datasets: [
        {
          label: 'Temperature (°C)',
          data: [22.1, 22.8, 23.2, 23.1, 22.9, 22.7],
          borderColor: '#ff6b35',
          backgroundColor: 'rgba(255, 107, 53, 0.1)',
          tension: 0.4
        },
        {
          label: 'Humidity (%)',
          data: [65, 68, 71, 69, 67, 66],
          borderColor: '#4ecdc4',
          backgroundColor: 'rgba(78, 205, 196, 0.1)',
          tension: 0.4
        },
        {
          label: 'Pressure (hPa)',
          data: [1013, 1012, 1011, 1012, 1013, 1014],
          borderColor: '#76b900',
          backgroundColor: 'rgba(118, 185, 0, 0.1)',
          tension: 0.4
        }
      ]
    };

    // Simulate API delay
    setTimeout(() => {
      setSightingsData(mockSightings);
      setTrendsData(mockTrends);
      setLoading(false);
    }, 1000);
  }, []);

  // Future: Real API integration
  const fetchRealData = async () => {
    try {
      // Replace with your Flask backend URL
      const sightingsResponse = await fetch('/research/sightings');
      const trendsResponse = await fetch('/research/trends');
      
      const sightings = await sightingsResponse.json();
      const trends = await trendsResponse.json();
      
      setSightingsData(sightings);
      setTrendsData(trends);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching research data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '400px',
        color: '#8fbc8f'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔬</div>
          <div>Loading research data...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ color: '#e0e0e0' }}>
      {/* Research Overview */}
      <div style={{
        background: 'rgba(20, 30, 40, 0.95)',
        borderRadius: '16px',
        padding: '2rem',
        marginBottom: '2rem',
        border: '1px solid rgba(76, 175, 80, 0.3)'
      }}>
        <h2 style={{ color: '#f0f0f0', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          🔬 Wildlife Research Dashboard
        </h2>
        <p style={{ color: '#b0b0b0', marginBottom: '1.5rem' }}>
          Advanced analytics and insights from your SquirrelBox network. Real-time data from Flask backend integration.
        </p>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem'
        }}>
          <div style={{
            background: 'rgba(30, 45, 55, 0.6)',
            padding: '1.5rem',
            borderRadius: '12px',
            border: '1px solid rgba(76, 175, 80, 0.2)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📊</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#76b900' }}>
              {sightingsData.length}
            </div>
            <div style={{ fontSize: '0.9rem', color: '#b0b0b0' }}>Recent Sightings</div>
          </div>
          
          <div style={{
            background: 'rgba(30, 45, 55, 0.6)',
            padding: '1.5rem',
            borderRadius: '12px',
            border: '1px solid rgba(76, 175, 80, 0.2)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🎯</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#76b900' }}>
              {sightingsData.length > 0 ? Math.round(sightingsData.reduce((acc, s) => acc + s.confidence, 0) / sightingsData.length) : 0}%
            </div>
            <div style={{ fontSize: '0.9rem', color: '#b0b0b0' }}>Avg Confidence</div>
          </div>
          
          <div style={{
            background: 'rgba(30, 45, 55, 0.6)',
            padding: '1.5rem',
            borderRadius: '12px',
            border: '1px solid rgba(76, 175, 80, 0.2)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🌡️</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#76b900' }}>
              {trendsData?.datasets[0]?.data?.slice(-1)[0] || 0}°C
            </div>
            <div style={{ fontSize: '0.9rem', color: '#b0b0b0' }}>Current Temp</div>
          </div>
          
          <div style={{
            background: 'rgba(30, 45, 55, 0.6)',
            padding: '1.5rem',
            borderRadius: '12px',
            border: '1px solid rgba(76, 175, 80, 0.2)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🐿️</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#76b900' }}>
              {new Set(sightingsData.map(s => s.species)).size}
            </div>
            <div style={{ fontSize: '0.9rem', color: '#b0b0b0' }}>Species Detected</div>
          </div>
        </div>
      </div>

      {/* Environmental Trends */}
      <div style={{
        background: 'rgba(20, 30, 40, 0.95)',
        borderRadius: '16px',
        padding: '2rem',
        marginBottom: '2rem',
        border: '1px solid rgba(76, 175, 80, 0.3)'
      }}>
        <h3 style={{ color: '#f0f0f0', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          📈 Environmental Trends
        </h3>
        
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '8px',
          padding: '1rem',
          minHeight: '300px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div style={{ textAlign: 'center', color: '#666' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
            <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Chart.js Integration Ready</div>
            <div style={{ fontSize: '0.9rem' }}>
              Connect to <code>/research/trends</code> endpoint for live environmental data
            </div>
          </div>
        </div>
        
        <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#b0b0b0' }}>
          <strong>Available Metrics:</strong> Temperature (°C), Humidity (%), Pressure (hPa)<br/>
          <strong>Data Source:</strong> environment_readings table | <strong>Sample Size:</strong> Latest 200 readings
        </div>
      </div>

      {/* Recent Sightings Table */}
      <div style={{
        background: 'rgba(20, 30, 40, 0.95)',
        borderRadius: '16px',
        padding: '2rem',
        border: '1px solid rgba(76, 175, 80, 0.3)'
      }}>
        <h3 style={{ color: '#f0f0f0', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          🎥 Recent Sightings Analysis
        </h3>
        
        <div style={{ overflowX: 'auto' }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.9rem'
          }}>
            <thead>
              <tr style={{ borderBottom: '2px solid rgba(76, 175, 80, 0.3)' }}>
                <th style={{ padding: '1rem 0.5rem', textAlign: 'left', color: '#8fbc8f' }}>Species</th>
                <th style={{ padding: '1rem 0.5rem', textAlign: 'left', color: '#8fbc8f' }}>Behavior</th>
                <th style={{ padding: '1rem 0.5rem', textAlign: 'center', color: '#8fbc8f' }}>Confidence</th>
                <th style={{ padding: '1rem 0.5rem', textAlign: 'left', color: '#8fbc8f' }}>Camera</th>
                <th style={{ padding: '1rem 0.5rem', textAlign: 'left', color: '#8fbc8f' }}>Zone</th>
                <th style={{ padding: '1rem 0.5rem', textAlign: 'left', color: '#8fbc8f' }}>Timestamp</th>
                <th style={{ padding: '1rem 0.5rem', textAlign: 'center', color: '#8fbc8f' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {sightingsData.map((sighting, index) => (
                <tr key={index} style={{
                  borderBottom: '1px solid rgba(76, 175, 80, 0.1)',
                  '&:hover': { background: 'rgba(30, 45, 55, 0.3)' }
                }}>
                  <td style={{ padding: '1rem 0.5rem', color: '#f0f0f0', fontWeight: '500' }}>
                    {sighting.species}
                  </td>
                  <td style={{ padding: '1rem 0.5rem', color: '#e0e0e0' }}>
                    {sighting.behavior}
                  </td>
                  <td style={{ padding: '1rem 0.5rem', textAlign: 'center' }}>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      background: sighting.confidence > 90 ? 'rgba(76, 175, 80, 0.2)' : 
                                 sighting.confidence > 80 ? 'rgba(255, 193, 7, 0.2)' : 'rgba(244, 67, 54, 0.2)',
                      color: sighting.confidence > 90 ? '#4caf50' : 
                             sighting.confidence > 80 ? '#ffc107' : '#f44336',
                      fontSize: '0.85rem',
                      fontWeight: '500'
                    }}>
                      {sighting.confidence}%
                    </span>
                  </td>
                  <td style={{ padding: '1rem 0.5rem', color: '#e0e0e0' }}>
                    {sighting.camera}
                  </td>
                  <td style={{ padding: '1rem 0.5rem', color: '#e0e0e0' }}>
                    {sighting.motion_zone}
                  </td>
                  <td style={{ padding: '1rem 0.5rem', color: '#b0b0b0', fontSize: '0.85rem' }}>
                    {new Date(sighting.timestamp).toLocaleString()}
                  </td>
                  <td style={{ padding: '1rem 0.5rem', textAlign: 'center' }}>
                    <button style={{
                      background: 'rgba(76, 175, 80, 0.2)',
                      border: '1px solid #76b900',
                      color: '#8fbc8f',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      cursor: 'pointer'
                    }}>
                      View Clip
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#b0b0b0' }}>
          <strong>Data Source:</strong> clip_metadata table | <strong>Total Records:</strong> Showing latest 100 sightings
        </div>
      </div>

      {/* API Integration Notes */}
      <div style={{
        background: 'rgba(30, 45, 55, 0.6)',
        borderRadius: '12px',
        padding: '1.5rem',
        marginTop: '2rem',
        border: '1px solid rgba(76, 175, 80, 0.2)'
      }}>
        <h4 style={{ color: '#8fbc8f', marginBottom: '1rem' }}>🔗 Backend Integration Status</h4>
        <div style={{ fontSize: '0.9rem', color: '#b0b0b0', lineHeight: '1.6' }}>
          <strong>Available Endpoints:</strong><br/>
          • <code>/research/sightings</code> - Animal detection data from clip_metadata table<br/>
          • <code>/research/trends</code> - Environmental sensor readings for Chart.js<br/>
          • <code>/research</code> - Research dashboard overview<br/><br/>
          
          <strong>Next Steps:</strong><br/>
          • Replace mock data with real Flask API calls<br/>
          • Add Chart.js for environmental trend visualization<br/>
          • Implement video clip viewing functionality<br/>
          • Add filtering and search capabilities
        </div>
      </div>
    </div>
  );
}

export default ResearchDashboard;
