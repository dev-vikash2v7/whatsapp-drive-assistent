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
  RefreshCw,
  Search,
  BookOpen,
  FolderOpen
} from 'lucide-react';

const Summary = () => {
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [summary, setSummary] = useState('');
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [summaryType, setSummaryType] = useState(''); // 'file' or 'folder'

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await driveAPI.listFiles('/');
      if (response.success) {
        const itemList = parseItemList(response.response);
        setFiles(itemList.filter(item => !item.isFolder));
        setFolders(itemList.filter(item => item.isFolder));
      } else {
        setError(response.error || 'Failed to load items');
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

  const parseItemList = (responseText) => {
    const lines = responseText.split('\n');
    const itemList = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.match(/^\d+\./)) {
        const nameMatch = line.match(/\*\*(.*?)\*\*/);
        if (nameMatch) {
          const itemName = nameMatch[1];
          
          let itemType = 'Unknown';
          let itemSize = 'Unknown';
          let modifiedDate = 'Unknown';
          
          if (i + 1 < lines.length && lines[i + 1].includes('Type:')) {
            itemType = lines[i + 1].split('Type:')[1]?.trim() || 'Unknown';
          }
          if (i + 2 < lines.length && lines[i + 2].includes('Size:')) {
            itemSize = lines[i + 2].split('Size:')[1]?.trim() || 'Unknown';
          }
          if (i + 3 < lines.length && lines[i + 3].includes('Modified:')) {
            modifiedDate = lines[i + 3].split('Modified:')[1]?.trim() || 'Unknown';
          }
          
          itemList.push({
            name: itemName,
            type: itemType,
            size: itemSize,
            modified: modifiedDate,
            isFolder: itemType.includes('folder') || itemType.includes('application/vnd.google-apps.folder')
          });
        }
      }
    }
    
    return itemList;
  };

  const getItemIcon = (itemType, isFolder) => {
    if (isFolder) return <Folder className="w-6 h-6 text-blue-500" />;
    
    if (itemType.includes('document') || itemType.includes('text')) {
      return <FileText className="w-6 h-6 text-green-500" />;
    } else if (itemType.includes('image')) {
      return <Image className="w-6 h-6 text-purple-500" />;
    } else if (itemType.includes('video')) {
      return <Video className="w-6 h-6 text-red-500" />;
    } else if (itemType.includes('audio')) {
      return <Music className="w-6 h-6 text-yellow-500" />;
    } else if (itemType.includes('zip') || itemType.includes('rar')) {
      return <Archive className="w-6 h-6 text-orange-500" />;
    } else {
      return <File className="w-6 h-6 text-gray-500" />;
    }
  };

  const handleItemClick = async (item, type) => {
    setSelectedItem(item);
    setSummaryType(type);
    setSummary('');
    setSummaryLoading(true);
    setError(null);

    try {
      let response;
      const itemPath = `/${item.name}`;

      if (type === 'file') {
        response = await driveAPI.getFileSummary(itemPath);
      } else {
        response = await driveAPI.getFolderSummary(itemPath);
      }

      if (response.success) {
        setSummary(response.response);
      } else {
        setError(response.error || `Failed to get ${type} summary`);
      }
    } catch (err) {
      setError(`Failed to get ${type} summary`);
    } finally {
      setSummaryLoading(false);
    }
  };

  const filteredFiles = files.filter(file =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredFolders = folders.filter(folder =>
    folder.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">Document Summaries</h2>
            <p className="text-sm text-gray-500">Get AI-powered summaries of files and folders</p>
          </div>
          <button
            onClick={loadItems}
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

        <div className="p-6">
          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search files and folders..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Files Section */}
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-green-500" />
                Files
              </h3>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="w-6 h-6 animate-spin text-primary-500" />
                  <span className="ml-2 text-gray-600">Loading files...</span>
                </div>
              ) : filteredFiles.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No files found
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredFiles.map((file, index) => (
                    <div
                      key={index}
                      onClick={() => handleItemClick(file, 'file')}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedItem?.name === file.name && summaryType === 'file'
                          ? 'border-primary-500 bg-primary-50'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        {getItemIcon(file.type, false)}
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-gray-900 truncate">{file.name}</h4>
                          <p className="text-sm text-gray-500">{file.type}</p>
                          <p className="text-sm text-gray-500">{file.size}</p>
                        </div>
                        <BookOpen className="w-5 h-5 text-gray-400" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Folders Section */}
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center">
                <FolderOpen className="w-5 h-5 mr-2 text-blue-500" />
                Folders
              </h3>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="w-6 h-6 animate-spin text-primary-500" />
                  <span className="ml-2 text-gray-600">Loading folders...</span>
                </div>
              ) : filteredFolders.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No folders found
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredFolders.map((folder, index) => (
                    <div
                      key={index}
                      onClick={() => handleItemClick(folder, 'folder')}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedItem?.name === folder.name && summaryType === 'folder'
                          ? 'border-primary-500 bg-primary-50'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        {getItemIcon(folder.type, true)}
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-gray-900 truncate">{folder.name}</h4>
                          <p className="text-sm text-gray-500">{folder.type}</p>
                          <p className="text-sm text-gray-500">{folder.size}</p>
                        </div>
                        <BookOpen className="w-5 h-5 text-gray-400" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Summary Display */}
          {selectedItem && (
            <div className="mt-8">
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-800 mb-4">
                  {summaryType === 'file' ? 'File' : 'Folder'} Summary: {selectedItem.name}
                </h3>
                
                {summaryLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="w-6 h-6 animate-spin text-primary-500" />
                    <span className="ml-2 text-gray-600">Generating summary...</span>
                  </div>
                ) : summary ? (
                  <div className="bg-white rounded-lg p-4 border">
                    <div className="prose max-w-none">
                      {summary.split('\n').map((line, index) => (
                        <p key={index} className="mb-2 text-gray-700">
                          {line}
                        </p>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    Click on a {summaryType} to generate its summary
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Summary;
