import { useState } from 'react';

function RecordingsList() {
  const [recordings] = useState([
    {
      id: 1,
      title: "Nutkin's Morning Feast",
      duration: "2:34",
      timestamp: "2025-01-15 08:23",
      camera: "inside",
      squirrels: ["Nutkin"],
      aiScore: 95,
      thumbnail: "🐿️",
      highlights: ["Acrobatic feeding", "Nut burying behavior"]
    },
    {
      id: 2,
      title: "Territorial Dispute",
      duration: "4:12",
      timestamp: "2025-01-15 10:45",
      camera: "outside",
      squirrels: ["Nutkin", "Chippy"],
      aiScore: 89,
      thumbnail: "⚔️",
      highlights: ["Chase sequence", "Tail flicking"]
    },
    {
      id: 3,
      title: "Mystery Squirrel Visit",
      duration: "1:45",
      timestamp: "2025-01-15 14:32",
      camera: "outside",
      squirrels: ["Unknown"],
      aiScore: 76,
      thumbnail: "❓",
      highlights: ["New visitor", "Cautious approach"]
    },
    {
      id: 4,
      title: "Evening Snack Run",
      duration: "3:28",
      timestamp: "2025-01-15 17:18",
      camera: "inside",
      squirrels: ["Hazel"],
      aiScore: 92,
      thumbnail: "🌙",
      highlights: ["Night vision capture", "Quick feeding"]
    },
    {
      id: 5,
      title: "The Great Nut Heist",
      duration: "5:02",
      timestamp: "2025-01-15 12:15",
      camera: "split",
      squirrels: ["Nutkin", "Pepper"],
      aiScore: 98,
      thumbnail: "💎",
      highlights: ["Coordinated effort", "Tool use observed"]
    }
  ]);

  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');

  const filteredRecordings = recordings
    .filter(recording => {
      if (filter === 'all') return true;
      if (filter === 'today') return recording.timestamp.includes('2025-01-15');
      if (filter === 'highlights') return recording.aiScore >= 90;
      return recording.camera === filter;
    })
    .sort((a, b) => {
      if (sortBy === 'newest') return new Date(b.timestamp) - new Date(a.timestamp);
      if (sortBy === 'duration') return parseInt(b.duration) - parseInt(a.duration);
      if (sortBy === 'score') return b.aiScore - a.aiScore;
      return 0;
    });

  return (
    <div className="recordings">
      <div className="card">
        <h2>🎥 Recorded Squirrel Activity</h2>
        
        <div className="recording-controls">
          <div className="filters">
            <label>Filter:</label>
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="all">All Recordings</option>
              <option value="today">Today</option>
              <option value="highlights">Highlights (90%+)</option>
              <option value="outside">Outside Camera</option>
              <option value="inside">Inside Camera</option>
            </select>
          </div>
          
          <div className="sorting">
            <label>Sort by:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="newest">Newest First</option>
              <option value="duration">Longest First</option>
              <option value="score">Highest AI Score</option>
            </select>
          </div>

          <div className="actions">
            <button className="action-btn">📤 Upload Selected</button>
            <button className="action-btn">🎬 Create Highlight Reel</button>
          </div>
        </div>
      </div>

      <div className="recordings-grid">
        {filteredRecordings.map(recording => (
          <div key={recording.id} className="recording-item">
            <div className="recording-thumbnail">
              <div className="thumbnail-emoji">{recording.thumbnail}</div>
              <div className="duration-badge">{recording.duration}</div>
              <div className="ai-score">{recording.aiScore}%</div>
            </div>
            
            <div className="recording-info">
              <h4>{recording.title}</h4>
              <p className="timestamp">📅 {recording.timestamp}</p>
              <p className="camera">📹 {recording.camera.charAt(0).toUpperCase() + recording.camera.slice(1)} camera</p>
              <p className="squirrels">🐿️ {recording.squirrels.join(', ')}</p>
              
              <div className="highlights">
                <strong>Highlights:</strong>
                <ul>
                  {recording.highlights.map((highlight, index) => (
                    <li key={index}>{highlight}</li>
                  ))}
                </ul>
              </div>

              <div className="recording-actions">
                <button className="play-btn">▶️ Play</button>
                <button className="share-btn">📤 Share</button>
                <button className="download-btn">💾 Download</button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        .recording-controls {
          display: flex;
          gap: 2rem;
          margin-bottom: 2rem;
          flex-wrap: wrap;
          align-items: center;
        }

        .filters, .sorting {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .filters label, .sorting label {
          font-weight: bold;
          color: #666;
        }

        .filters select, .sorting select {
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 6px;
          background: white;
        }

        .actions {
          display: flex;
          gap: 0.5rem;
        }

        .action-btn {
          padding: 0.5rem 1rem;
          border: 1px solid #4ecdc4;
          background: white;
          color: #4ecdc4;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .action-btn:hover {
          background: #4ecdc4;
          color: white;
        }

        .recording-item {
          position: relative;
        }

        .recording-thumbnail {
          position: relative;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          height: 180px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 12px 12px 0 0;
        }

        .thumbnail-emoji {
          font-size: 4rem;
          filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3));
        }

        .duration-badge {
          position: absolute;
          bottom: 10px;
          right: 10px;
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: bold;
        }

        .ai-score {
          position: absolute;
          top: 10px;
          right: 10px;
          background: rgba(76, 175, 80, 0.9);
          color: white;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: bold;
        }

        .recording-info {
          padding: 1rem;
        }

        .recording-info h4 {
          margin-bottom: 0.75rem;
          color: #333;
          font-size: 1.1rem;
        }

        .recording-info p {
          margin-bottom: 0.5rem;
          color: #666;
          font-size: 0.9rem;
        }

        .highlights {
          margin: 1rem 0;
          padding: 0.75rem;
          background: rgba(78, 205, 196, 0.05);
          border-radius: 6px;
          border-left: 3px solid #4ecdc4;
        }

        .highlights ul {
          margin: 0.5rem 0 0 1rem;
          padding: 0;
        }

        .highlights li {
          margin-bottom: 0.25rem;
          color: #555;
        }

        .recording-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
        }

        .play-btn, .share-btn, .download-btn {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid #ddd;
          background: white;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.3s ease;
          font-size: 0.9rem;
        }

        .play-btn:hover {
          background: #4caf50;
          color: white;
          border-color: #4caf50;
        }

        .share-btn:hover {
          background: #2196f3;
          color: white;
          border-color: #2196f3;
        }

        .download-btn:hover {
          background: #ff9800;
          color: white;
          border-color: #ff9800;
        }
      `}</style>
    </div>
  );
}

export default RecordingsList;
