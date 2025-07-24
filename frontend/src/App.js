import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import Clips from './components/Clips';
import Settings from './components/Settings';
import Research from './components/Research';
import { apiService } from './services/api';

function App() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const status = await apiService.getStatus();
        setSystemStatus(status);
      } catch (error) {
        console.error('Failed to fetch system status:', error);
        setSystemStatus({ status: 'error', message: 'Backend unavailable' });
      } finally {
        setLoading(false);
      }
    };

    checkSystemStatus();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading Nutflix Platform...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <nav className="navbar">
            <div className="nav-brand">
              <h1>🐿️ Nutflix Platform</h1>
              {systemStatus && (
                <span className={`status-badge ${systemStatus.status}`}>
                  {systemStatus.status}
                </span>
              )}
            </div>
            <ul className="nav-links">
              <li><Link to="/">Dashboard</Link></li>
              <li><Link to="/clips">Clips</Link></li>
              <li><Link to="/research">Research</Link></li>
              <li><Link to="/settings">Settings</Link></li>
            </ul>
          </nav>
        </header>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/clips" element={<Clips />} />
            <Route path="/research" element={<Research />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>

        <footer className="App-footer">
          <p>Nutflix Platform v{process.env.REACT_APP_VERSION || '1.0.0'}</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
