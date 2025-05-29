import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import Bloomberg from './pages/Bloomberg';
import { Layout } from './components/Layout';
import apiClient from './api/client';

function App() {
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Check API health on mount
    apiClient.get('/ping')
      .then(() => {
        // API is working, no need to show status
        setError('');
      })
      .catch((err: any) => {
        console.error('API Error:', err);
        setError('API Error: Could not connect');
      });
  }, []);

  return (
    <Router>
      <div className="App">
        {/* API Status Check - only show if there's an error */}
        {error && (
          <div className="bg-red-50 border border-red-200 p-4 mb-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}
        
        <Routes>
          <Route path="/" element={
            <Layout currentPage="bloomberg">
              <Bloomberg />
            </Layout>
          } />
          <Route path="/bloomberg" element={
            <Layout currentPage="bloomberg">
              <Bloomberg />
            </Layout>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
