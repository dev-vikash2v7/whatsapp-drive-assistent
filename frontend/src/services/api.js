import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});




export const driveAPI = {
  // Check authentication status
  checkAuthStatus: async (whatsappNumber) => {
    try {
      const response = await api.get('/api/auth/status', {
        params: { whatsapp_number: whatsappNumber }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

 

  // Test internet connection
  testConnection: async () => {
    try {
      const response = await api.get('/api/test/connection');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // List files in a folder
  listFiles: async (folderPath = '/') => {
    try {
      const response = await api.post('/api/execute', {
        message: `list ${folderPath}`
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete a file
  deleteFile: async (filePath) => {
    try {
      const response = await api.post('/api/execute', {
        message: `delete ${filePath}`
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Move a file
  moveFile: async (sourcePath, destinationPath) => {
    try {
      const response = await api.post('/api/execute', {
        message: `move ${sourcePath} to ${destinationPath}`
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Copy a file
  copyFile: async (sourcePath, destinationPath) => {
    try {
      const response = await api.post('/api/execute', {
        message: `copy ${sourcePath} to ${destinationPath}`
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get folder summary
  getFolderSummary: async (folderPath) => {
    try {
      const response = await api.post('/api/execute', {
        message: `folder summary ${folderPath}`
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get file summary
  getFileSummary: async (filePath) => {
    try {
      const response = await api.post('/api/execute', {
        message: `file summary ${filePath}`
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get help
  getHelp: async () => {
    try {
      const response = await api.post('/api/execute', {
        message: 'help'
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export const whatsappAPI = {
  // Get WhatsApp QR code
  getQRCode: async () => {
    try {
      const response = await api.get('/api/whatsapp/qr');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get WhatsApp join code
  getJoinCode: async () => {
    try {
      const response = await api.get('/api/whatsapp/join-code');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Check WhatsApp connection status
  getStatus: async () => {
    try {
      const response = await api.get('/api/whatsapp/status');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default api;
