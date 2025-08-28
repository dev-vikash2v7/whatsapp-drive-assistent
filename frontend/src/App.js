import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DriveExplorer from './components/DriveExplorer';
import FileOperations from './components/FileOperations';
import Summary from './components/Summary';
import AuthStatus from './components/AuthStatus';
import Navbar from './components/Navbar';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [whatsappNumber, setWhatsappNumber] = useState(sessionStorage.getItem('whatsappNumber') || '');

  console.log("WhatsApp Number:", whatsappNumber);

  const handleAuthChange = (authenticated) => {
    setIsAuthenticated(authenticated);
  };

  const handleWhatsAppNumberChange = (number) => {
    setWhatsappNumber(number);
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <AuthStatus 
              onAuthChange={handleAuthChange} 
              whatsappNumber={whatsappNumber}
              onWhatsAppNumberChange={handleWhatsAppNumberChange}
            />
          </div>
          
          <Routes>
            {isAuthenticated ? (
              <>
                <Route path="/" element={<DriveExplorer whatsappNumber={whatsappNumber} />} />
                <Route path="/operations" element={<FileOperations whatsappNumber={whatsappNumber} />} />
                <Route path="/summary" element={<Summary whatsappNumber={whatsappNumber} />} />
              </>
            ) : (
              <Route path="*" element={
                <div className="text-center py-12">
                  <div className="bg-white rounded-lg shadow-md p-8 max-w-md mx-auto">
                    <h2 className="text-xl font-semibold text-gray-800 mb-4">
                      Connect to Google Drive
                    </h2>

                   
                    <p className="text-gray-600 mb-6">
                      Please enter your WhatsApp number and connect to Google Drive above to start managing your files.
                    </p>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h3 className="font-medium text-blue-800 mb-2">What you can do:</h3>
                      <ul className="text-sm text-blue-700 space-y-1">
                        <li>• Browse and navigate through files and folders</li>
                        <li>• Move, copy, and delete files</li>
                        <li>• Generate AI-powered summaries of documents</li>
                        <li>• Search and organize your content</li>
                      </ul>
                    </div>
                  </div>
                </div>
              } />
            )}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
