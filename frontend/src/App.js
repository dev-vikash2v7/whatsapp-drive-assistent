import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DriveExplorer from './components/DriveExplorer';
import FileOperations from './components/FileOperations';
import Summary from './components/Summary';
import AuthStatus from './components/AuthStatus';
import CredentialsGuide from './components/CredentialsGuide';
import Navbar from './components/Navbar';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleAuthChange = (authenticated) => {
    setIsAuthenticated(authenticated);
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <AuthStatus onAuthChange={handleAuthChange} />
          </div>
          
          <Routes>
            {isAuthenticated ? (
              <>
                <Route path="/" element={<DriveExplorer />} />
                <Route path="/operations" element={<FileOperations />} />
                <Route path="/summary" element={<Summary />} />
              </>
            ) : (
              <Route path="*" element={
                <div className="text-center py-12">
                  <div className="bg-white rounded-lg shadow-md p-8 max-w-md mx-auto">
                    <h2 className="text-xl font-semibold text-gray-800 mb-4">
                      Connect to Google Drive
                    </h2>
                    <p className="text-gray-600 mb-6">
                      Please connect to Google Drive above to start managing your files.
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
