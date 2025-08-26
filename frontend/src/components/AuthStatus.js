import React, { useState, useEffect } from 'react';
import { driveAPI } from '../services/api';
import { 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  Cloud, 
  AlertCircle,
  ExternalLink,
  Phone
} from 'lucide-react';
import { useGoogleLogin } from '@react-oauth/google';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const AuthStatus = ({ onAuthChange, whatsappNumber, onWhatsAppNumberChange }) => {
  const [authStatus, setAuthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [error, setError] = useState(null);
  const [whatsappNumberError, setWhatsappNumberError] = useState('');
 
 

  useEffect(() => {
    if (whatsappNumber.trim()) {
      checkAuthStatus();
    }
  }, [whatsappNumber]);

  const validateWhatsAppNumber = (number) => {
    // Basic WhatsApp number validation
    const cleaned = number.replace(/\D/g, '');
    if (cleaned.length < 10 || cleaned.length > 15) {
      return 'Please enter a valid WhatsApp number (10-15 digits)';
    }
    return '';
  };

  const handleWhatsAppNumberChange = (e) => {
    const number = e.target.value;
    onWhatsAppNumberChange(number);
    setWhatsappNumberError(validateWhatsAppNumber(number));
  };

  const login = useGoogleLogin({
    flow: "auth-code", // 👈 IMPORTANT for backend exchange
    scope: "https://www.googleapis.com/auth/drive.file",
    onSuccess: async (response) => {
      console.log("Auth Code Response:", response);
      
      if (!whatsappNumber.trim()) {
        setError('Please enter your WhatsApp number');
        return;
      }
      
      const validationError = validateWhatsAppNumber(whatsappNumber);
      if (validationError) {
        setError(validationError);
        return;
      }
      
      // response.code contains the authorization code
      const res = await fetch(API_BASE_URL + "/api/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          code: response.code,
          whatsapp_number: whatsappNumber.trim()
        }),
      });
      // console.log(await res.json());

      const data = await res.json();

      if (data.success) {
        setAuthStatus({
          authenticated: true,
          message: 'Successfully connected to Google Drive'
        });
        if (onAuthChange) {
          onAuthChange(true);
        }
        
      } else {
        setError(data.error || data.message || 'Failed to connect to Google Drive');
      }

    },
    onError: (error) => console.error("Login Failed:", error),
  });


  const checkAuthStatus = async () => {
    if (!whatsappNumber.trim()) {
      setError('Please enter your WhatsApp number to check authentication status');
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const response = await driveAPI.checkAuthStatus(whatsappNumber.trim());
      setAuthStatus(response);
      if (onAuthChange) {
        onAuthChange(response.authenticated);
      }
    } catch (err) {
      setError('Failed to check authentication status');
      setAuthStatus({ authenticated: false, message: 'Failed to check status' });
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    if (!whatsappNumber.trim()) {
      setError('Please enter your WhatsApp number');
      return;
    }
    
    const validationError = validateWhatsAppNumber(whatsappNumber);
    if (validationError) {
      setError(validationError);
      return;
    }
    
    setConnecting(true);
    setError(null);
    try {
      login();
      
    } catch (err) {
      if (err.response?.data?.error_type === 'connection') {
        setError('Connection error. Please check your internet connection and try again.');
      } else {
        setError('Failed to connect to Google Drive. Please check your credentials and internet connection.');
      }
    } finally {
      setConnecting(false);
    }
  };

  const handleTestConnection = async () => {
    setTestingConnection(true);
    setError(null);
    try {
      const response = await driveAPI.testConnection();
      if (response.success) {
        alert('Internet connection is working! The issue might be with Google Drive API access.');
      } else {
        alert(`Connection test failed: ${response.message}`);
      }
    } catch (err) {
      alert('Failed to test connection. Please check if the backend server is running.');
    } finally {
      setTestingConnection(false);
    }
  };

  const getStatusIcon = () => {
    if (loading) {
      return <RefreshCw className="w-5 h-5 animate-spin text-gray-500" />;
    }
    if (authStatus?.authenticated) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    }
    return <XCircle className="w-5 h-5 text-red-500" />;
  };

  const getStatusText = () => {
    if (loading) return 'Checking connection...';
    if (authStatus?.authenticated) return 'Connected to Google Drive';
    return 'Not connected to Google Drive';
  };

  const getStatusColor = () => {
    if (loading) return 'text-gray-500';
    if (authStatus?.authenticated) return 'text-green-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center">
          <Cloud className="w-5 h-5 mr-2 text-blue-500" />
          Google Drive Connection
        </h2>
        <button
          onClick={checkAuthStatus}
          disabled={loading || !whatsappNumber.trim()}
          className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* WhatsApp Number Input */}
      <div className="mb-4">
        <label htmlFor="whatsapp-number" className="block text-sm font-medium text-gray-700 mb-2">
          <Phone className="w-4 h-4 inline mr-1" />
          WhatsApp Number
        </label>
        <input
          type="tel"
          id="whatsapp-number"
          value={whatsappNumber}
          onChange={handleWhatsAppNumberChange}
          placeholder="+1234567890"
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            whatsappNumberError ? 'border-red-300' : 'border-gray-300'
          }`}
        />
        {whatsappNumberError && (
          <p className="text-sm text-red-600 mt-1">{whatsappNumberError}</p>
        )}
        <p className="text-xs text-gray-500 mt-1">
          Enter your WhatsApp number to connect your Google Drive account
        </p>
      </div>

      {/* Status Display */}
      <div className="flex items-center space-x-3 mb-4">
        {getStatusIcon()}
        <span className={`font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </div>

      {/* Status Message */}
      {authStatus?.message && (
        <p className="text-sm text-gray-600 mb-4">
          {authStatus.message}
        </p>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

             {/* Action Buttons */}
       <div className="space-y-3">
         {!authStatus?.authenticated && !loading && (
           <>
             <button
               onClick={handleConnect}
               disabled={connecting || !whatsappNumber.trim() || whatsappNumberError}
               className="w-full flex items-center justify-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"

             >
               {connecting ? (
                 <>
                   <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                   Connecting...
                 </>
               ) : (
                 <>
                   <Cloud className="w-4 h-4 mr-2" />
                   Connect to Google Drive
                 </>
               )}
             </button>
             
             
           </>
         )}

    

        {/* Connected Status */}
        {authStatus?.authenticated && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-green-800 font-medium">
                Successfully connected to Google Drive
              </span>
            </div>
            <p className="text-sm text-green-700 mt-1">
              You can now browse and manage your Google Drive files.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuthStatus;
