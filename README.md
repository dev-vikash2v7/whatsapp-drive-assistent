<div align="center">
  <div>
   <img src="https://img.shields.io/badge/Python-black?style=for-the-badge&logoColor=white&logo=python&color=yellow" alt="python" />
   <img src="https://img.shields.io/badge/Flask-red?style=for-the-badge&logoColor=blue&logo=flask&color=white" alt="flask" />
   <img src="https://img.shields.io/badge/-React.js-black?style=for-the-badge&logoColor=white&logo=react&color=61DAFB" alt="react.js" />
   <img src="https://img.shields.io/badge/SQL-black?style=for-the-badge&logoColor=white&logo=mysql&color=green" alt="sql" />
   <img src="https://img.shields.io/badge/Gemini-blue?style=for-the-badge&logoColor=black&logo=gemini&color=blue" alt="gemini" />
   <img src="https://img.shields.io/badge/Twilio-red?style=for-the-badge&logoColor=red&logo=twilio&color=black" alt="Twilio" />
   <img src="https://img.shields.io/badge/Whatsapp-white?style=for-the-badge&logoColor=green&logo=whatsapp&color=white" alt="whatsapp" />
  </div>
  <h3 align="center">WhatsApp Drive Assistant - Full Stack Application</h3>
</div>



## <a name="introduction">🤖 Introduction</a>

A modern full-stack application that provides a GUI interface for Google Drive operations, built with React.js frontend and Flask backend.

## Features

### 🎯 Core Functionality
- **Drive Explorer**: Browse and navigate through Google Drive files and folders
- **File Operations**: Move, copy, and delete files with intuitive GUI
- **Document Summaries**: AI-powered summaries of files and folders
- **Real-time Updates**: Live file listing and operation status

### 🎨 User Interface
- **Modern Design**: Clean, responsive UI built with Tailwind CSS
- **Intuitive Navigation**: Easy-to-use interface with visual file icons
- **Search Functionality**: Quick search through files and folders
- **Interactive Operations**: Click-based file operations instead of commands

### 🔧 Technical Features
- **RESTful API**: Clean API endpoints for all operations
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error handling and user feedback
- **Loading States**: Visual feedback for all operations

## Project Structure

```
whatsapp ai/
├── api_server.py              # Flask backend server
├── requirements.txt           # Python dependencies
├── frontend/                  # React.js frontend
│   ├── package.json          # Node.js dependencies
│   ├── public/               # Static files
│   ├── src/                  # React source code
│   │   ├── components/       # React components
│   │   ├── services/         # API services
│   │   ├── App.js           # Main app component
│   │   └── index.js         # App entry point
│   └── tailwind.config.js   # Tailwind CSS configuration
├── utils/                    # Backend utilities
│   ├── google_drive_client.py
│   ├── command_parser.py
│   └── document_summarizer.py
└── README.md                # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Drive API credentials

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Google Drive credentials**:
   - Create a Google Cloud Project
   - Enable Google Drive API
   - Download credentials JSON file
   - Place it in the project root as `credentials.json`
   - Set environment variable: `GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json`

   **Detailed Setup Guide**: The frontend includes a step-by-step setup guide at `/guide` route.

3. **Run the backend server**:
   ```bash
   python api_server.py
   ```
   The server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`

## Usage

### Authentication
- **Connect to Google Drive**: Click the "Connect to Google Drive" button in the authentication panel
- **Setup Guide**: Access detailed setup instructions at `/guide` route
- **Status Check**: The app automatically checks authentication status on load
- **Re-authentication**: If tokens expire, the app will prompt for re-authentication

### Drive Explorer
- Navigate through folders by clicking on them
- View file details including type, size, and modification date
- Use the back button to navigate to parent folders
- Refresh to get the latest file list

### File Operations
- Select a file from the list
- Choose an operation (Delete, Move, or Copy)
- For move/copy operations, select a destination folder
- Execute the operation with a single click

### Document Summaries
- Select any file or folder to generate an AI summary
- View detailed summaries with key insights
- Summaries are generated using Google's AI services

## API Endpoints

### Authentication
- `GET /api/auth/status` - Check authentication status
- `POST /api/auth/connect` - Connect to Google Drive

### File Operations
- `GET /api/files` - List files in a folder
- `DELETE /api/files/<path>` - Delete a file
- `POST /api/files/move` - Move a file
- `POST /api/files/copy` - Copy a file

### Summaries
- `GET /api/summary/file/<path>` - Get file summary
- `GET /api/summary/folder/<path>` - Get folder summary

### Legacy WhatsApp API
- `POST /api/execute` - Execute commands (for WhatsApp integration)

## Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
FLASK_ENV=DEV
PORT=5000
```

### Vercel Deployment Environment Variables

For Vercel deployment, set these environment variables in your Vercel project settings:

```env
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_REDIRECT_URI=https://your-app.vercel.app
STORAGE_PREFIX=STORAGE_
VERCEL=1
```

**Note**: The application automatically uses persistent storage for Google Drive tokens on Vercel. See `backend/STORAGE_README.md` for detailed information about the storage system.

## Development

### Backend Development
- The Flask server uses the existing WhatsApp command parser
- New API endpoints follow RESTful conventions
- CORS is enabled for frontend communication

### Frontend Development
- Built with React 18 and modern hooks
- Uses Tailwind CSS for styling
- Lucide React for icons
- Axios for API communication

### Adding New Features
1. Add new API endpoints in `api_server.py`
2. Create corresponding frontend components
3. Update the API service in `frontend/src/services/api.js`
4. Add routing in `frontend/src/App.js`

## Deployment

### Backend Deployment
- Deploy to platforms like Heroku, Railway, or AWS
- Set environment variables for production
- Ensure Google Drive credentials are properly configured

### Frontend Deployment
- Build the production version: `npm run build`
- Deploy to platforms like Vercel, Netlify, or AWS S3
- Update API base URL for production

## Troubleshooting

### Common Issues
1. **Google Drive Authentication**: Ensure credentials file is properly set up
2. **CORS Errors**: Check that flask-cors is installed and configured
3. **File Not Found**: Verify file paths and Google Drive permissions
4. **API Connection**: Ensure backend server is running on correct port
5. **SSL Connection Errors**: Use the SSL diagnostic tool to troubleshoot connection issues

### SSL Troubleshooting
If you encounter SSL errors like "wrong version number":

1. **Run the SSL diagnostic tool**:
   ```bash
   python ssl_test.py
   ```

2. **Use the frontend connection test**:
   - Click "Test Internet Connection" in the authentication panel
   - This will help identify if it's a general connection issue

3. **Common solutions**:
   - Update Python to a newer version
   - Check firewall settings
   - Try a different network connection
   - Update SSL certificates
   - If on corporate network, check proxy settings

### Debug Mode
- Backend: Set `FLASK_ENV=DEV` for debug output
- Frontend: Use browser developer tools for debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.

