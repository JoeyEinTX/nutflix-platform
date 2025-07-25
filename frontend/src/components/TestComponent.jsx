import React from 'react';

function TestComponent() {
  return (
    <div style={{ padding: '20px', background: '#f0f0f0', color: '#333' }}>
      <h1>🚀 Test Component Working!</h1>
      <p>If you can see this, React is rendering properly.</p>
      <p>Current time: {new Date().toLocaleTimeString()}</p>
    </div>
  );
}

export default TestComponent;
