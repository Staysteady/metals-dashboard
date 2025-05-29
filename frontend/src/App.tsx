import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import Home from './pages/Home';
import Bloomberg from './pages/Bloomberg';
import Portfolio from './pages/Portfolio';
import { Layout } from './components/Layout';
import { api } from './api/client';

// Placeholder component for missing pages
const PlaceholderPage: React.FC<{ title: string }> = ({ title }) => (
  <div className="container mx-auto p-4">
    <div className="text-center py-16">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
      <p className="text-gray-600">This page is under development.</p>
    </div>
  </div>
);

function App() {
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Check API health on mount
    api.ping()
      .then(() => {
        // API is working, no need to show status
        setError('');
      })
      .catch(err => {
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
            <Layout currentPage="dashboard">
              <Home />
            </Layout>
          } />
          <Route path="/bloomberg" element={
            <Layout currentPage="bloomberg">
              <Bloomberg />
            </Layout>
          } />
          <Route path="/tickers" element={
            <Layout currentPage="tickers">
              <Portfolio />
            </Layout>
          } />
          <Route path="/charts" element={
            <Layout currentPage="charts">
              <PlaceholderPage title="Charts" />
            </Layout>
          } />
          <Route path="/settlement" element={
            <Layout currentPage="settlement">
              <PlaceholderPage title="Settlement" />
            </Layout>
          } />
          <Route path="/alerts" element={
            <Layout currentPage="alerts">
              <PlaceholderPage title="Alerts" />
            </Layout>
          } />
          <Route path="/settings" element={
            <Layout currentPage="settings">
              <PlaceholderPage title="Settings" />
            </Layout>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
