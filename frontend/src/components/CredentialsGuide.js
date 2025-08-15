import React, { useState } from 'react';
import { 
  ChevronDown, 
  ChevronRight, 
  ExternalLink, 
  FileText,
  Settings,
  Download,
  Folder
} from 'lucide-react';

const CredentialsGuide = () => {
  const [expandedSteps, setExpandedSteps] = useState({});

  const toggleStep = (stepNumber) => {
    setExpandedSteps(prev => ({
      ...prev,
      [stepNumber]: !prev[stepNumber]
    }));
  };

  const steps = [
    {
      number: 1,
      title: "Create a Google Cloud Project",
      description: "Set up a new project in Google Cloud Console",
      details: [
        "Go to Google Cloud Console",
        "Click 'Select a project' → 'New Project'",
        "Enter a project name (e.g., 'WhatsApp Drive Assistant')",
        "Click 'Create'"
      ],
      link: "https://console.cloud.google.com/",
      linkText: "Open Google Cloud Console"
    },
    {
      number: 2,
      title: "Enable Google Drive API",
      description: "Enable the Google Drive API for your project",
      details: [
        "In your project, go to 'APIs & Services' → 'Library'",
        "Search for 'Google Drive API'",
        "Click on 'Google Drive API'",
        "Click 'Enable'"
      ],
      link: "https://console.cloud.google.com/apis/library/drive.googleapis.com",
      linkText: "Enable Google Drive API"
    },
    {
      number: 3,
      title: "Create OAuth 2.0 Credentials",
      description: "Create OAuth 2.0 client credentials",
      details: [
        "Go to 'APIs & Services' → 'Credentials'",
        "Click 'Create Credentials' → 'OAuth client ID'",
        "Select 'Desktop application' as application type",
        "Enter a name (e.g., 'Drive Assistant Client')",
        "Click 'Create'"
      ],
      link: "https://console.cloud.google.com/apis/credentials",
      linkText: "Create Credentials"
    },
    {
      number: 4,
      title: "Download Credentials File",
      description: "Download the credentials JSON file",
      details: [
        "After creating credentials, click 'Download JSON'",
        "Save the file as 'credentials.json'",
        "Keep this file secure - it contains sensitive information"
      ]
    },
    {
      number: 5,
      title: "Place Credentials in Project",
      description: "Move the credentials file to the project root",
      details: [
        "Copy 'credentials.json' to the project root directory",
        "The file should be at the same level as 'api_server.py'",
        "Ensure the file is named exactly 'credentials.json'"
      ]
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-6">
        <Settings className="w-6 h-6 text-blue-500 mr-3" />
        <h2 className="text-xl font-semibold text-gray-800">
          Google Drive Setup Guide
        </h2>
      </div>

      <div className="space-y-4">
        {steps.map((step) => (
          <div key={step.number} className="border border-gray-200 rounded-lg">
            <button
              onClick={() => toggleStep(step.number)}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
            >
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  {step.number}
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{step.title}</h3>
                  <p className="text-sm text-gray-600">{step.description}</p>
                </div>
              </div>
              {expandedSteps[step.number] ? (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronRight className="w-5 h-5 text-gray-400" />
              )}
            </button>

            {expandedSteps[step.number] && (
              <div className="px-4 pb-4 border-t border-gray-200">
                <div className="pt-4">
                  <ul className="space-y-2">
                    {step.details.map((detail, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="flex-shrink-0 w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                        <span className="text-sm text-gray-700">{detail}</span>
                      </li>
                    ))}
                  </ul>
                  
                  {step.link && (
                    <a
                      href={step.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center mt-3 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 text-sm"
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      {step.linkText}
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

             <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
         <div className="flex items-start space-x-2">
           <FileText className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
           <div>
             <h3 className="font-medium text-yellow-800 mb-1">Important Notes:</h3>
             <ul className="text-sm text-yellow-700 space-y-1">
               <li>• Keep your credentials.json file secure and never share it</li>
               <li>• The first time you connect, a browser window will open for authentication</li>
               <li>• After authentication, a token.json file will be created automatically</li>
               <li>• You only need to authenticate once per device</li>
             </ul>
           </div>
         </div>
       </div>

       <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
         <div className="flex items-start space-x-2">
           <FileText className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
           <div>
             <h3 className="font-medium text-red-800 mb-1">Troubleshooting SSL Errors:</h3>
             <ul className="text-sm text-red-700 space-y-1">
               <li>• If you get SSL errors, try using the "Test Internet Connection" button first</li>
               <li>• Check if your firewall is blocking the connection</li>
               <li>• Try running the app on a different network</li>
               <li>• Ensure your Python installation has up-to-date SSL certificates</li>
               <li>• If using a corporate network, check proxy settings</li>
             </ul>
           </div>
         </div>
       </div>
    </div>
  );
};

export default CredentialsGuide;
