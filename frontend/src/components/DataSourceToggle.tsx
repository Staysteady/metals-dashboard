import React, { useState, useEffect } from 'react';

interface BloombergStatus {
  bloomberg_available: boolean;
  is_connected: boolean;
  status: string;
  message: string;
}

interface BloombergStatusProps {
  onStatusChange?: () => void;
}

const BloombergStatus: React.FC<BloombergStatusProps> = ({ onStatusChange }) => {
  const [status, setStatus] = useState<BloombergStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/health');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setStatus(data.bloomberg);
      
      if (onStatusChange) {
        onStatusChange();
      }
    } catch (err) {
      console.error('Failed to fetch Bloomberg status:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus({
        bloomberg_available: false,
        is_connected: false,
        status: 'error',
        message: 'Failed to connect to API'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReconnect = async () => {
    await fetchStatus();
  };

  useEffect(() => {
    fetchStatus();
    
    // Poll for status updates every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading && !status) {
    return (
      <div className="flex items-center space-x-2 text-gray-600">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        <span className="text-sm">Checking Bloomberg status...</span>
      </div>
    );
  }

  if (error && !status) {
    return (
      <div className="flex items-center space-x-2 text-red-600">
        <span className="text-sm">⚠️ Connection Error</span>
        <button 
          onClick={handleReconnect}
          className="text-xs bg-red-100 hover:bg-red-200 px-2 py-1 rounded"
        >
          Retry
        </button>
      </div>
    );
  }

  const getStatusIcon = () => {
    if (!status) return '⚠️';
    
    switch (status.status) {
      case 'connected': return '🟢';
      case 'disconnected': return '🔴';
      default: return '🟡';
    }
  };

  const getStatusColor = () => {
    if (!status) return 'text-gray-600';
    
    switch (status.status) {
      case 'connected': return 'text-green-600';
      case 'disconnected': return 'text-red-600';
      default: return 'text-yellow-600';
    }
  };

  const getStatusText = () => {
    if (!status) return 'Unknown';
    
    if (status.is_connected) {
      return 'Bloomberg Connected';
    } else if (status.bloomberg_available) {
      return 'Bloomberg Disconnected';
    } else {
      return 'Bloomberg Unavailable';
    }
  };

  return (
    <div className="flex items-center space-x-3 bg-white border border-gray-200 rounded-lg px-4 py-2 shadow-sm">
      <div className="flex items-center space-x-2">
        <span className="text-lg">{getStatusIcon()}</span>
        <div className="flex flex-col">
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </span>
          {status && (
            <span className="text-xs text-gray-500">
              {status.message}
            </span>
          )}
        </div>
      </div>
      
      {status && !status.is_connected && (
        <button
          onClick={handleReconnect}
          className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-1 rounded-md transition-colors"
          disabled={loading}
        >
          {loading ? 'Checking...' : 'Reconnect'}
        </button>
      )}
    </div>
  );
};

export default BloombergStatus; 