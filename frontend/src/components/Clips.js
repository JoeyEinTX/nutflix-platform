import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const Clips = () => {
  const [clips, setClips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchClips = async () => {
      try {
        setLoading(true);
        const data = await apiService.getClips();
        setClips(data.clips || data || []);
      } catch (err) {
        setError('Failed to load clips');
        console.error('Clips error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchClips();
  }, []);

  if (loading) return <div>Loading clips...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="clips-page">
      <h1>📹 Video Clips</h1>
      {clips.length === 0 ? (
        <p>No clips available yet.</p>
      ) : (
        <div className="clips-grid">
          {clips.map((clip, index) => (
            <div key={clip.id || index} className="clip-card">
              <h3>{clip.filename || `Clip ${index + 1}`}</h3>
              <p>Date: {clip.timestamp ? new Date(clip.timestamp).toLocaleString() : 'Unknown'}</p>
              {clip.species && <p>Species: {clip.species}</p>}
              {clip.duration && <p>Duration: {clip.duration}s</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Clips;
