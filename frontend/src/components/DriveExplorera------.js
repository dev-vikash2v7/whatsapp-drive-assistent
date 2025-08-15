import React, { useState, useEffect } from 'react';
import { driveAPI } from '../services/api';
import { 
  Folder, 
  File, 
  FileText, 
  Image, 
  Video, 
  Music, 
  Archive,
  ArrowLeft,
  RefreshCw,
  Trash2,
  Copy,
  Move,
  FileSearch
} from 'lucide-react';

const DriveExplorer = () => {
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [showOperations, setShowOperations] = useState(false);

  useEffect(() => {
    loadFiles();
  }, [currentPath]);

  const loadFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await driveAPI.listFiles(currentPath);
      if (response.success) {
        // Parse the response to extract file information
        const fileList = parseFileList(response.response);
        setFiles(fileList);
      } else {
        setError(response.error || 'Failed to load files');
      }
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Authentication required. Please connect to Google Drive first.');
      } else {
        setError('Failed to connect to server');
      }
    } finally {
      setLoading(false);
    }
  };

  const parseFileList = (responseText) => {
    // Parse the WhatsApp-style response to extract file information
    const lines = responseText.split('\n');
    const fileList = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.match(/^\d+\./)) {
        // Extract file name
        const nameMatch = line.match(/\*\*(.*?)\*\*/);
        if (nameMatch) {
          const fileName = nameMatch[1];
          
          // Look for type, size, and modified info in next lines
          let fileType = 'Unknown';
          let fileSize = 'Unknown';
          let modifiedDate = 'Unknown';
          
          if (i + 1 < lines.length && lines[i + 1].includes('Type:')) {
            fileType = lines[i + 1].split('Type:')[1]?.trim() || 'Unknown';
          }
          if (i + 2 < lines.length && lines[i + 2].includes('Size:')) {
            fileSize = lines[i + 2].split('Size:')[1]?.trim() || 'Unknown';
          }
          if (i + 3 < lines.length && lines[i + 3].includes('Modified:')) {
            modifiedDate = lines[i + 3].split('Modified:')[1]?.trim() || 'Unknown';
          }
          
          fileList.push({
            name: fileName,
            type: fileType,
            size: fileSize,
            modified: modifiedDate,
            isFolder: fileType.includes('folder') || fileType.includes('application/vnd.google-apps.folder')
          });
        }
      }
    }
    
    return fileList;
  };

  const getFileIcon = (fileType, isFolder) => {
    if (isFolder) return <Folder className="w-6 h-6 text-blue-500" />;
    
    if (fileType.includes('document') || fileType.includes('text')) {
      return <FileText className="w-6 h-6 text-green-500" />;
    } else if (fileType.includes('image')) {
      return <Image className="w-6 h-6 text-purple-500" />;
    } else if (fileType.includes('video')) {
      return <Video className="w-6 h-6 text-red-500" />;
    } else if (fileType.includes('audio')) {
      return <Music className="w-6 h-6 text-yellow-500" />;
    } else if (fileType.includes('zip') || fileType.includes('rar')) {
      return <Archive className="w-6 h-6 text-orange-500" />;
    } else {
      return <File className="w-6 h-6 text-gray-500" />;
    }
  };

  const handleFileClick = (file) => {
    if (file.isFolder) {
      setCurrentPath(currentPath === '/' ? `/${file.name}` : `${currentPath}/${file.name}`);
    } else {
      setSelectedFile(file);
      setShowOperations(true);
    }
  };

  const handleBackClick = () => {
    if (currentPath === '/') return;
    
    const pathParts = currentPath.split('/').filter(Boolean);
    pathParts.pop();
    const newPath = pathParts.length === 0 ? '/' : `/${pathParts.join('/')}`;
    setCurrentPath(newPath);
  };

  const handleDelete = async () => {
    if (!selectedFile) return;
    
    const filePath = currentPath === '/' ? `/${selectedFile.name}` : `${currentPath}/${selectedFile.name}`;
    
    try {
      const response = await driveAPI.deleteFile(filePath);
      if (response.success) {
        setShowOperations(false);
        setSelectedFile(null);
        loadFiles();
      } else {
        setError(response.error || 'Failed to delete file');
      }
    } catch (err) {
      setError('Failed to delete file');
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-4">
            <button
              onClick={handleBackClick}
              disabled={currentPath === '/'}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h2 className="text-xl font-semibold text-gray-800">Drive Explorer</h2>
              <p className="text-sm text-gray-500">Current path: {currentPath}</p>
            </div>
          </div>
          <button
            onClick={loadFiles}
            disabled={loading}
            className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-400">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* File List */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-primary-500" />
              <span className="ml-2 text-gray-600">Loading files...</span>
            </div>
          ) : files.length === 0 ? (
            <div className="text-center py-12">
              <FileSearch className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No files found in this folder</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {files.map((file, index) => (
                <div
                  key={index}
                  onClick={() => handleFileClick(file)}
                  className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <div className="flex items-start space-x-3">
                    {getFileIcon(file.type, file.isFolder)}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">{file.name}</h3>
                      <p className="text-sm text-gray-500">{file.type}</p>
                      <p className="text-sm text-gray-500">{file.size}</p>
                      <p className="text-sm text-gray-500">{file.modified}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* File Operations Modal */}
      {showOperations && selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">File Operations</h3>
            <p className="text-gray-600 mb-4">Selected: {selectedFile.name}</p>
            
            <div className="space-y-3">
              <button
                onClick={handleDelete}
                className="w-full flex items-center justify-center px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete File
              </button>
              
              <button
                onClick={() => setShowOperations(false)}
                className="w-full px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DriveExplorer;
