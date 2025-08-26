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
  Copy,
  Move,
  Trash2,
  RefreshCw,
  Search
} from 'lucide-react';

const FileOperations = ({ whatsappNumber }) => {
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedDestination, setSelectedDestination] = useState('');
  const [operation, setOperation] = useState(''); // 'move', 'copy', 'delete'
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadFiles();
    loadFolders();
  }, []);

  const loadFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await driveAPI.listFiles('/');

      console.log('response' , response)
      if (response.success) {
        const fileList = parseFileList(response.response);
        setFiles(fileList.filter(file => !file.isFolder));
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

  const loadFolders = async () => {
    try {
      const response = await driveAPI.listFiles('/');
      if (response.success) {
        const fileList = parseFileList(response.response);
        setFolders(fileList.filter(file => file.isFolder));
      }
    } catch (err) {
      console.error('Failed to load folders:', err);
    }
  };

  const parseFileList = (responseText) => {
    const lines = responseText.split('\n');
    const fileList = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.match(/^\d+\./)) {
        const nameMatch = line.match(/\*\*(.*?)\*\*/);
        if (nameMatch) {
          const fileName = nameMatch[1];
          
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

  const getFileIcon = (fileType) => {
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

  const handleOperation = async () => {
    if (!selectedFile || !operation) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      let response;
      const filePath = `/${selectedFile.name}`;

      switch (operation) {
        case 'delete':
          response = await driveAPI.deleteFile(filePath);
          break;
        case 'move':
          if (!selectedDestination) {
            setError('Please select a destination folder');
            setLoading(false);
            return;
          }
          response = await driveAPI.moveFile(filePath, selectedDestination);
          break;
        case 'copy':
          if (!selectedDestination) {
            setError('Please select a destination folder');
            setLoading(false);
            return;
          }
          response = await driveAPI.copyFile(filePath, selectedDestination);
          break;
        default:
          setError('Invalid operation');
          setLoading(false);
          return;
      }

      if (response.success) {
        setSuccess(`File ${operation}d successfully!`);
        setSelectedFile(null);
        setSelectedDestination('');
        setOperation('');
        loadFiles();
      } else {
        setError(response.error || `Failed to ${operation} file`);
      }
    } catch (err) {
      setError(`Failed to ${operation} file`);
    } finally {
      setLoading(false);
    }
  };

  const filteredFiles = files.filter(file =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">File Operations</h2>
            <p className="text-sm text-gray-500">Move, copy, or delete files</p>
          </div>
          <button
            onClick={() => {
              loadFiles();
              loadFolders();
            }}
            disabled={loading}
            className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Messages */}
        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-400">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {success && (
          <div className="p-4 bg-green-50 border-l-4 border-green-400">
            <p className="text-green-700">{success}</p>
          </div>
        )}

        <div className="p-6">
          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* File Selection */}
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-800 mb-4">Select File</h3>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-primary-500" />
                <span className="ml-2 text-gray-600">Loading files...</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredFiles.map((file, index) => (
                  <div
                    key={index}
                    onClick={() => setSelectedFile(file)}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedFile?.name === file.name
                        ? 'border-primary-500 bg-primary-50'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      {getFileIcon(file.type)}
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 truncate">{file.name}</h4>
                        <p className="text-sm text-gray-500">{file.type}</p>
                        <p className="text-sm text-gray-500">{file.size}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Operation Selection */}
          {selectedFile && (
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Select Operation</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => setOperation('delete')}
                  className={`p-4 border rounded-lg text-center transition-colors ${
                    operation === 'delete'
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <Trash2 className="w-8 h-8 mx-auto mb-2" />
                  <span className="font-medium">Delete</span>
                </button>
                <button
                  onClick={() => setOperation('move')}
                  className={`p-4 border rounded-lg text-center transition-colors ${
                    operation === 'move'
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <Move className="w-8 h-8 mx-auto mb-2" />
                  <span className="font-medium">Move</span>
                </button>
                <button
                  onClick={() => setOperation('copy')}
                  className={`p-4 border rounded-lg text-center transition-colors ${
                    operation === 'copy'
                      ? 'border-green-500 bg-green-50 text-green-700'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <Copy className="w-8 h-8 mx-auto mb-2" />
                  <span className="font-medium">Copy</span>
                </button>
              </div>
            </div>
          )}

          {/* Destination Selection (for move/copy) */}
          {(operation === 'move' || operation === 'copy') && (
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Select Destination Folder</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                  onClick={() => setSelectedDestination('/')}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedDestination === '/'
                      ? 'border-primary-500 bg-primary-50'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Folder className="w-6 h-6 text-blue-500" />
                    <span className="font-medium">Root Folder</span>
                  </div>
                </div>
                {folders.map((folder, index) => (
                  <div
                    key={index}
                    onClick={() => setSelectedDestination(`/${folder.name}`)}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedDestination === `/${folder.name}`
                        ? 'border-primary-500 bg-primary-50'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Folder className="w-6 h-6 text-blue-500" />
                      <span className="font-medium">{folder.name}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Execute Button */}
          {selectedFile && operation && (
            <div className="flex justify-center">
              <button
                onClick={handleOperation}
                disabled={loading || (operation !== 'delete' && !selectedDestination)}
                className="px-8 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center">
                    <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                    Processing...
                  </div>
                ) : (
                  `${operation.charAt(0).toUpperCase() + operation.slice(1)} File`
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileOperations;
