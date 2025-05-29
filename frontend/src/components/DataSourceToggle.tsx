import React, { useState, useEffect } from 'react';
import { Radio, AlertCircle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';

interface BloombergStatus {
  bloomberg_available: boolean;
  is_connected: boolean;
  status: string;
  message: string;
}

interface BloombergStatusProps {
  onDataSourceChange?: () => void;
}

const BloombergStatus: React.FC<BloombergStatusProps> = ({ onDataSourceChange }) => {
  const [status, setStatus] = useState<BloombergStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [reconnecting, setReconnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      setError(null);
      const response = await fetch('http://127.0.0.1:8000/settings/data-source-status');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const statusData = await response.json();
      setStatus(statusData);
    } catch (err) {
      console.error('Error fetching Bloomberg status:', err);
      setError('Failed to fetch Bloomberg status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    
    // Refresh status every 10 seconds to keep it in sync
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleReconnect = async () => {
    if (!status?.bloomberg_available) return;

    setReconnecting(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/settings/reconnect-bloomberg', {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      // Refresh status after reconnect attempt
      await fetchStatus();
      
      if (onDataSourceChange) {
        onDataSourceChange();
      }
    } catch (err: unknown) {
      console.error('Error reconnecting to Bloomberg:', err);
      setError('Failed to reconnect to Bloomberg');
    } finally {
      setReconnecting(false);
    }
  };

  const getStatusIcon = () => {
    if (!status) return <Radio className="h-4 w-4" />;
    
    if (status.is_connected) {
      return <CheckCircle className="h-4 w-4 text-green-600" />;
    } else if (status.bloomberg_available) {
      return <AlertCircle className="h-4 w-4 text-yellow-600" />;
    } else {
      return <XCircle className="h-4 w-4 text-red-600" />;
    }
  };

  const getStatusColor = () => {
    if (!status) return 'border-gray-200 bg-gray-50';
    
    if (status.is_connected) {
      return 'border-green-200 bg-green-50';
    } else if (status.bloomberg_available) {
      return 'border-yellow-200 bg-yellow-50';
    } else {
      return 'border-red-200 bg-red-50';
    }
  };

  const getStatusText = () => {
    if (!status) return 'Unknown';
    
    if (status.is_connected) {
      return 'Connected';
    } else if (status.bloomberg_available) {
      return 'Disconnected';
    } else {
      return 'Not Available';
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-20 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  return (
    <div className={`rounded-lg border p-4 ${getStatusColor()}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <h3 className="font-medium">Bloomberg Terminal</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{getStatusText()}</span>
          {status?.bloomberg_available && !status.is_connected && (
            <button
              onClick={handleReconnect}
              disabled={reconnecting}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 rounded border border-blue-300 disabled:opacity-50"
            >
              <RefreshCw className={`h-3 w-3 ${reconnecting ? 'animate-spin' : ''}`} />
              Reconnect
            </button>
          )}
        </div>
      </div>
      
      <div className="text-sm">
        <p className="text-gray-700 mb-2">{status?.message}</p>
        
        {error && (
          <div className="mb-2 p-2 bg-red-100 border border-red-300 rounded text-red-800 text-xs">
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {reconnecting && (
          <p className="text-blue-600 text-xs">Attempting to reconnect...</p>
        )}
        
        {status && !status.bloomberg_available && (
          <div className="mt-2 p-2 bg-orange-100 border border-orange-300 rounded text-orange-800 text-xs">
            <strong>Setup Required:</strong> Install Bloomberg API package:
            <code className="block mt-1 p-1 bg-orange-200 rounded">pip install blpapi</code>
            Then ensure Bloomberg Terminal is running and logged in.
          </div>
        )}
        
        {status && status.bloomberg_available && !status.is_connected && (
          <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-yellow-800 text-xs">
            <strong>Connection Required:</strong> Bloomberg API is installed but Terminal is not connected.
            <br />Please ensure Bloomberg Terminal is running and logged in, then click Reconnect.
          </div>
        )}
        
        {status && status.is_connected && (
          <div className="mt-2 p-2 bg-green-100 border border-green-300 rounded text-green-800 text-xs">
            <strong>Status:</strong> Connected to Bloomberg Terminal - Live market data available.
          </div>
        )}
      </div>
    </div>
  );
};

export default BloombergStatus; 