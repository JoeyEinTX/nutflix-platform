import './App.css';
import './flask-styles.css'; // Your Flask dashboard styles
import { useState, useEffect } from 'react';
// Option to import your existing components instead:
// import Dashboard from './your-components/YourDashboard';
// import LiveStream from './your-components/YourLiveStream';

import FigmaStyleDashboard from './components/FigmaStyleDashboard_3cards'; // Your beautiful Figma design with 3-card layout
import ResearchDashboard from './components/ResearchDashboard'; // Research analytics integration
import LiveStream from './components/LiveStream';
import RecordingsList from './components/RecordingsList';
import SystemStatus from './components/SystemStatus';
import SquirrelProfiles from './components/SquirrelProfiles';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showDropdown, setShowDropdown] = useState(false);
  const [systemHealth, setSystemHealth] = useState({
    status: 'online',
    cameras: { outside: true, inside: true },
    storage: 75,
    temperature: 22.5,
    humidity: 65
  });

  // Simulate real-time updates (in production, this would come from WebSocket)
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemHealth(prev => ({
        ...prev,
        temperature: 20 + Math.random() * 10,
        humidity: 60 + Math.random() * 20,
        storage: 70 + Math.random() * 20
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const renderContent = () => {
    switch(activeTab) {
      case 'dashboard':
        return <FigmaStyleDashboard systemHealth={systemHealth} />;
      case 'squirrels':
        return <SquirrelProfiles />;
      case 'research':
        return <ResearchDashboard systemHealth={systemHealth} />;
      case 'system':
        return <SystemStatus systemHealth={systemHealth} />;
      default:
        return <FigmaStyleDashboard systemHealth={systemHealth} />;
    }
  };

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'research', label: 'Research', icon: '🔬' },
    { id: 'squirrels', label: 'Squirrel Profiles', icon: '🐿️' },
    { id: 'system', label: 'System Status', icon: '⚙️' }
  ];

  const currentItem = navigationItems.find(item => item.id === activeTab) || navigationItems[0];

  return (
    <div className="App">
        <header style={{
          background: 'linear-gradient(135deg, #2c3e50 0%, #34495e 100%)',
          padding: '1rem 0',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          position: 'relative'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '0 2rem'
          }}>
            <div 
              onClick={() => setActiveTab('dashboard')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                cursor: 'pointer',
                transition: 'opacity 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.opacity = '0.8';
              }}
              onMouseLeave={(e) => {
                e.target.style.opacity = '1';
              }}
            >
              <div style={{
                width: '40px',
                height: '40px',
                background: 'linear-gradient(45deg, #f39c12, #e67e22)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.5rem'
              }}>
                🌰
              </div>
              <h1 style={{
                color: 'white',
                margin: 0,
                fontSize: '1.8rem',
                fontWeight: '700',
                letterSpacing: '-0.5px'
              }}>
                NutFlix
              </h1>
            </div>
            
            {/* Dropdown Navigation */}
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                style={{
                  background: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '8px',
                  padding: '0.75rem',
                  color: 'white',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1rem',
                  transition: 'all 0.2s ease',
                  width: '48px',
                  height: '48px'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(255,255,255,0.15)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'rgba(255,255,255,0.1)';
                }}
              >
                <svg 
                  width="20" 
                  height="20" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2"
                  style={{
                    transition: 'transform 0.2s ease',
                    transform: showDropdown ? 'rotate(90deg)' : 'rotate(0deg)'
                  }}
                >
                  <line x1="3" y1="6" x2="21" y2="6"></line>
                  <line x1="3" y1="12" x2="21" y2="12"></line>
                  <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
              </button>
              
              {showDropdown && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  right: '0',
                  marginTop: '0.5rem',
                  background: 'linear-gradient(135deg, rgba(20, 30, 40, 0.98) 0%, rgba(46, 60, 70, 0.98) 100%)',
                  backdropFilter: 'blur(12px)',
                  borderRadius: '12px',
                  boxShadow: '0 12px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(76, 175, 80, 0.3)',
                  overflow: 'hidden',
                  zIndex: 1000,
                  minWidth: '220px',
                  border: '1px solid rgba(76, 175, 80, 0.2)'
                }}>
                  {navigationItems.map((item, index) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        setActiveTab(item.id);
                        setShowDropdown(false);
                      }}
                      style={{
                        width: '100%',
                        padding: '1rem 1.25rem',
                        border: 'none',
                        background: activeTab === item.id 
                          ? 'linear-gradient(90deg, rgba(76, 175, 80, 0.2) 0%, rgba(118, 185, 0, 0.15) 100%)' 
                          : 'transparent',
                        color: activeTab === item.id ? '#76b900' : '#e0e0e0',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.875rem',
                        fontSize: '0.95rem',
                        fontWeight: activeTab === item.id ? '600' : '500',
                        transition: 'all 0.2s ease',
                        borderBottom: index < navigationItems.length - 1 ? '1px solid rgba(255,255,255,0.08)' : 'none',
                        position: 'relative',
                        overflow: 'hidden'
                      }}
                      onMouseEnter={(e) => {
                        if (activeTab !== item.id) {
                          e.target.style.background = 'rgba(76, 175, 80, 0.1)';
                          e.target.style.color = '#8fbc8f';
                          e.target.style.transform = 'translateX(4px)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (activeTab !== item.id) {
                          e.target.style.background = 'transparent';
                          e.target.style.color = '#e0e0e0';
                          e.target.style.transform = 'translateX(0px)';
                        }
                      }}
                    >
                      <span style={{ 
                        fontSize: '1.3rem',
                        filter: activeTab === item.id ? 'drop-shadow(0 0 4px rgba(118, 185, 0, 0.3))' : 'none',
                        transition: 'filter 0.2s ease'
                      }}>{item.icon}</span>
                      <span style={{
                        textShadow: activeTab === item.id ? '0 0 8px rgba(118, 185, 0, 0.2)' : 'none'
                      }}>{item.label}</span>
                      {activeTab === item.id && (
                        <div style={{
                          position: 'absolute',
                          left: '0',
                          top: '0',
                          bottom: '0',
                          width: '3px',
                          background: 'linear-gradient(180deg, #76b900 0%, #5a7c0a 100%)',
                          boxShadow: '0 0 8px rgba(118, 185, 0, 0.4)'
                        }}></div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </header>

      <main className="main-content">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
