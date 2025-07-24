import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const Research = () => {
  const [sightings, setSightings] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResearchData = async () => {
      try {
        setLoading(true);
        
        // Try to fetch sightings and trends
        const [sightingsData, trendsData] = await Promise.allSettled([
          apiService.getSightings(),
          apiService.getTrends()
        ]);

        if (sightingsData.status === 'fulfilled') {
          setSightings(sightingsData.value.sightings || sightingsData.value || []);
        }

        if (trendsData.status === 'fulfilled') {
          setTrends(trendsData.value.trends || trendsData.value || []);
        }

      } catch (err) {
        console.error('Research data error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchResearchData();
  }, []);

  if (loading) return <div>Loading research data...</div>;

  return (
    <div className="research-page">
      <h1>🔬 Wildlife Research</h1>
      
      <div className="research-section">
        <h2>Recent Sightings</h2>
        {sightings.length === 0 ? (
          <p>No sightings recorded yet.</p>
        ) : (
          <div className="sightings-list">
            {sightings.slice(0, 5).map((sighting, index) => (
              <div key={index} className="sighting-item">
                <strong>{sighting.species || 'Unknown Species'}</strong>
                <span>{sighting.timestamp ? new Date(sighting.timestamp).toLocaleString() : 'Unknown time'}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="research-section">
        <h2>Activity Trends</h2>
        {trends.length === 0 ? (
          <p>No trend data available yet.</p>
        ) : (
          <div className="trends-list">
            {trends.map((trend, index) => (
              <div key={index} className="trend-item">
                <span>{trend.period || 'Unknown period'}</span>
                <span>{trend.count || 0} sightings</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Research;
