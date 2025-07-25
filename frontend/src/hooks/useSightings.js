import { useState, useEffect } from 'react';

const API_BASE = 'http://10.0.0.79:8000/api';

export function useSightings(limit = 10) {
  const [sightings, setSightings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSightings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/sightings`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Transform data to match expected format
      const transformedSightings = data.slice(0, limit).map((sighting, index) => ({
        id: index + 1,
        species: sighting.species || 'Unknown',
        time: formatTimeAgo(sighting.raw_timestamp || sighting.timestamp),
        image: getSpeciesEmoji(sighting.species),
        behavior: sighting.behavior,
        confidence: sighting.confidence,
        camera: sighting.camera,
        raw_timestamp: sighting.raw_timestamp
      }));
      
      setSightings(transformedSightings);
      setError(null);
    } catch (err) {
      console.error('Error fetching sightings:', err);
      setError(err.message);
      // Fallback to mock data on error
      setSightings(getMockSightings(limit));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSightings();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchSightings, 5000); // Poll every 5 seconds
    
    return () => clearInterval(interval);
  }, [limit]);

  return { sightings, loading, error, refetch: fetchSightings };
}

export function useMotionStatus() {
  const [status, setStatus] = useState({ running: false, recent_sightings_count: 0 });
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/motion/status`);
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (err) {
      console.error('Error fetching motion status:', err);
    } finally {
      setLoading(false);
    }
  };

  const startMotionDetection = async () => {
    try {
      const response = await fetch(`${API_BASE}/motion/start`);
      if (response.ok) {
        await fetchStatus();
        return true;
      }
    } catch (err) {
      console.error('Error starting motion detection:', err);
    }
    return false;
  };

  const stopMotionDetection = async () => {
    try {
      const response = await fetch(`${API_BASE}/motion/stop`);
      if (response.ok) {
        await fetchStatus();
        return true;
      }
    } catch (err) {
      console.error('Error stopping motion detection:', err);
    }
    return false;
  };

  const triggerTestSighting = async () => {
    try {
      const response = await fetch(`${API_BASE}/motion/trigger-test`);
      if (response.ok) {
        const result = await response.json();
        console.log('Test sighting triggered:', result);
        return result;
      }
    } catch (err) {
      console.error('Error triggering test sighting:', err);
    }
    return null;
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return { 
    status, 
    loading, 
    startMotionDetection, 
    stopMotionDetection, 
    triggerTestSighting,
    refetch: fetchStatus 
  };
}

function formatTimeAgo(timestamp) {
  if (!timestamp) return 'Unknown';
  
  try {
    const now = new Date();
    const sightingTime = new Date(timestamp);
    const diffMs = now - sightingTime;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  } catch (e) {
    return timestamp;
  }
}

function getSpeciesEmoji(species) {
  if (!species) return '🔍';
  
  const speciesLower = species.toLowerCase();
  
  if (speciesLower.includes('squirrel')) return '🐿️';
  if (speciesLower.includes('human')) return '👤';
  if (speciesLower.includes('bird') || speciesLower.includes('jay') || speciesLower.includes('cardinal')) return '🐦';
  if (speciesLower.includes('wildlife')) return '🦔';
  if (speciesLower.includes('chipmunk')) return '🐿️';
  if (speciesLower.includes('unknown')) return '❓';
  
  return '🔍'; // Default for motion detection
}

function getMockSightings(limit) {
  const mockData = [
    { id: 1, species: "Eastern Gray Squirrel", time: "2 min ago", image: "🐿️" },
    { id: 2, species: "Red Squirrel", time: "15 min ago", image: "🐿️" },
    { id: 3, species: "Flying Squirrel", time: "1 hour ago", image: "🐿️" },
    { id: 4, species: "Chipmunk", time: "2 hours ago", image: "🐿️" },
    { id: 5, species: "Blue Jay", time: "3 hours ago", image: "🐦" }
  ];
  
  return mockData.slice(0, limit);
}
