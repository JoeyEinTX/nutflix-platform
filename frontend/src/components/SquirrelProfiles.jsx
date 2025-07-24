import { useState } from 'react';

function SquirrelProfiles() {
  const [squirrels] = useState([
    {
      id: 1,
      name: "Nutkin",
      avatar: "🐿️",
      status: "Active",
      firstSeen: "2024-12-15",
      totalVisits: 247,
      favoriteFoods: ["Acorns", "Sunflower seeds"],
      personality: "Bold and acrobatic",
      lastSeen: "Today, 14:32",
      behaviors: ["Tool use", "Territory marking", "Cache hiding"],
      aiConfidence: 98,
      color: "Reddish-brown with white belly",
      size: "Medium",
      distinguishingMarks: "Nick in left ear, bushy tail"
    },
    {
      id: 2,
      name: "Chippy",
      avatar: "🐿️",
      status: "Active",
      firstSeen: "2025-01-03",
      totalVisits: 89,
      favoriteFoods: ["Peanuts", "Corn"],
      personality: "Cautious but curious",
      lastSeen: "Today, 10:45",
      behaviors: ["Quick feeding", "Lookout behavior"],
      aiConfidence: 94,
      color: "Gray with darker stripes",
      size: "Small",
      distinguishingMarks: "Distinctive white chest patch"
    },
    {
      id: 3,
      name: "Hazel",
      avatar: "🐿️",
      status: "Regular",
      firstSeen: "2024-11-28",
      totalVisits: 156,
      favoriteFoods: ["Hazelnuts", "Walnuts"],
      personality: "Methodical and patient",
      lastSeen: "Yesterday, 17:18",
      behaviors: ["Slow feeding", "Grooming", "Social interactions"],
      aiConfidence: 91,
      color: "Light brown with golden highlights",
      size: "Large",
      distinguishingMarks: "Particularly fluffy tail"
    },
    {
      id: 4,
      name: "Pepper",
      avatar: "🐿️",
      status: "Occasional",
      firstSeen: "2025-01-10",
      totalVisits: 23,
      favoriteFoods: ["Mixed seeds", "Berries"],
      personality: "Playful and energetic",
      lastSeen: "Today, 12:15",
      behaviors: ["Acrobatic movements", "Cooperative feeding"],
      aiConfidence: 87,
      color: "Dark gray with black markings",
      size: "Medium",
      distinguishingMarks: "White tip on tail"
    },
    {
      id: 5,
      name: "Unknown Visitor",
      avatar: "❓",
      status: "New",
      firstSeen: "Today",
      totalVisits: 1,
      favoriteFoods: ["Unknown"],
      personality: "Cautious newcomer",
      lastSeen: "Today, 14:32",
      behaviors: ["Exploration", "Testing approach"],
      aiConfidence: 76,
      color: "Brown with lighter markings",
      size: "Unknown",
      distinguishingMarks: "Needs more observation"
    }
  ]);

  const [selectedSquirrel, setSelectedSquirrel] = useState(null);

  const getStatusColor = (status) => {
    switch(status) {
      case 'Active': return '#4caf50';
      case 'Regular': return '#2196f3';
      case 'Occasional': return '#ff9800';
      case 'New': return '#9c27b0';
      default: return '#666';
    }
  };

  return (
    <div className="squirrel-profiles">
      <div className="card">
        <h2>🐿️ Squirrel Community</h2>
        <p>Individual squirrels identified and tracked by AI recognition</p>
      </div>

      <div className="profiles-grid">
        {squirrels.map(squirrel => (
          <div key={squirrel.id} className="squirrel-card">
            <div className="squirrel-avatar">
              {squirrel.avatar}
            </div>
            
            <h3>{squirrel.name}</h3>
            
            <div 
              className="status-badge"
              style={{ backgroundColor: getStatusColor(squirrel.status) }}
            >
              {squirrel.status}
            </div>

            <div className="squirrel-stats">
              <div className="stat">
                <span className="label">Visits:</span>
                <span className="value">{squirrel.totalVisits}</span>
              </div>
              <div className="stat">
                <span className="label">AI Confidence:</span>
                <span className="value">{squirrel.aiConfidence}%</span>
              </div>
              <div className="stat">
                <span className="label">Last Seen:</span>
                <span className="value">{squirrel.lastSeen}</span>
              </div>
            </div>

            <div className="personality">
              <strong>Personality:</strong>
              <p>{squirrel.personality}</p>
            </div>

            <div className="favorite-foods">
              <strong>Favorite Foods:</strong>
              <div className="food-tags">
                {squirrel.favoriteFoods.map((food, index) => (
                  <span key={index} className="food-tag">{food}</span>
                ))}
              </div>
            </div>

            <button 
              className="view-details-btn"
              onClick={() => setSelectedSquirrel(squirrel)}
            >
              📊 View Details
            </button>
          </div>
        ))}
      </div>

      {selectedSquirrel && (
        <div className="modal-overlay" onClick={() => setSelectedSquirrel(null)}>
          <div className="squirrel-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-avatar">{selectedSquirrel.avatar}</div>
              <div>
                <h2>{selectedSquirrel.name}</h2>
                <div 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(selectedSquirrel.status) }}
                >
                  {selectedSquirrel.status}
                </div>
              </div>
              <button 
                className="close-btn"
                onClick={() => setSelectedSquirrel(null)}
              >
                ✕
              </button>
            </div>

            <div className="modal-content">
              <div className="detail-section">
                <h4>📋 Basic Information</h4>
                <div className="detail-grid">
                  <div><strong>First Seen:</strong> {selectedSquirrel.firstSeen}</div>
                  <div><strong>Total Visits:</strong> {selectedSquirrel.totalVisits}</div>
                  <div><strong>AI Confidence:</strong> {selectedSquirrel.aiConfidence}%</div>
                  <div><strong>Size:</strong> {selectedSquirrel.size}</div>
                </div>
              </div>

              <div className="detail-section">
                <h4>🎨 Physical Description</h4>
                <p><strong>Coloring:</strong> {selectedSquirrel.color}</p>
                <p><strong>Distinguishing Marks:</strong> {selectedSquirrel.distinguishingMarks}</p>
              </div>

              <div className="detail-section">
                <h4>🧠 Behavior Profile</h4>
                <p><strong>Personality:</strong> {selectedSquirrel.personality}</p>
                <div className="behaviors">
                  <strong>Observed Behaviors:</strong>
                  <div className="behavior-tags">
                    {selectedSquirrel.behaviors.map((behavior, index) => (
                      <span key={index} className="behavior-tag">{behavior}</span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h4>🥜 Food Preferences</h4>
                <div className="food-tags">
                  {selectedSquirrel.favoriteFoods.map((food, index) => (
                    <span key={index} className="food-tag large">{food}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .profiles-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1.5rem;
          margin-top: 1rem;
        }

        .squirrel-card {
          background: white;
          border-radius: 15px;
          padding: 1.5rem;
          text-align: center;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
          transition: transform 0.3s ease;
          position: relative;
        }

        .squirrel-card:hover {
          transform: translateY(-5px);
        }

        .squirrel-avatar {
          width: 80px;
          height: 80px;
          background: linear-gradient(45deg, #ff9a9e, #fecfef);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2.5rem;
          margin: 0 auto 1rem;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .squirrel-card h3 {
          margin-bottom: 0.5rem;
          color: #333;
        }

        .status-badge {
          display: inline-block;
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: bold;
          margin-bottom: 1rem;
        }

        .squirrel-stats {
          text-align: left;
          margin-bottom: 1rem;
        }

        .stat {
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.5rem;
          padding: 0.5rem;
          background: rgba(78, 205, 196, 0.05);
          border-radius: 6px;
        }

        .stat .label {
          color: #666;
          font-weight: 500;
        }

        .stat .value {
          color: #333;
          font-weight: bold;
        }

        .personality {
          text-align: left;
          margin-bottom: 1rem;
          padding: 0.75rem;
          background: rgba(255, 193, 7, 0.1);
          border-radius: 8px;
          border-left: 3px solid #ffc107;
        }

        .personality p {
          margin: 0.5rem 0 0 0;
          color: #555;
          font-style: italic;
        }

        .favorite-foods {
          text-align: left;
          margin-bottom: 1rem;
        }

        .food-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }

        .food-tag {
          background: rgba(76, 175, 80, 0.1);
          color: #4caf50;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.8rem;
          border: 1px solid rgba(76, 175, 80, 0.3);
        }

        .food-tag.large {
          padding: 0.5rem 1rem;
          font-size: 0.9rem;
        }

        .view-details-btn {
          background: linear-gradient(45deg, #4ecdc4, #44a08d);
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          cursor: pointer;
          font-weight: bold;
          transition: all 0.3s ease;
          width: 100%;
        }

        .view-details-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 1rem;
        }

        .squirrel-modal {
          background: white;
          border-radius: 15px;
          max-width: 600px;
          width: 100%;
          max-height: 80vh;
          overflow-y: auto;
        }

        .modal-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1.5rem;
          border-bottom: 1px solid #eee;
        }

        .modal-avatar {
          width: 60px;
          height: 60px;
          background: linear-gradient(45deg, #ff9a9e, #fecfef);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
        }

        .close-btn {
          margin-left: auto;
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          color: #666;
          padding: 0.5rem;
          border-radius: 50%;
          transition: background 0.3s ease;
        }

        .close-btn:hover {
          background: rgba(0, 0, 0, 0.1);
        }

        .modal-content {
          padding: 1.5rem;
        }

        .detail-section {
          margin-bottom: 2rem;
        }

        .detail-section h4 {
          margin-bottom: 1rem;
          color: #333;
          border-bottom: 2px solid #4ecdc4;
          padding-bottom: 0.5rem;
        }

        .detail-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .detail-grid > div {
          padding: 0.75rem;
          background: rgba(78, 205, 196, 0.05);
          border-radius: 6px;
          border-left: 3px solid #4ecdc4;
        }

        .behaviors {
          margin-top: 0.5rem;
        }

        .behavior-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }

        .behavior-tag {
          background: rgba(156, 39, 176, 0.1);
          color: #9c27b0;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.8rem;
          border: 1px solid rgba(156, 39, 176, 0.3);
        }
      `}</style>
    </div>
  );
}

export default SquirrelProfiles;
