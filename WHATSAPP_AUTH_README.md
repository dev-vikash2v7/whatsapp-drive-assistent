# WhatsApp Number-Based Authentication System

This document describes the implementation of WhatsApp number-based authentication for the WhatsApp Drive Assistant project.

## Overview

The system now supports multiple users by using their WhatsApp numbers as unique identifiers for Google Drive authentication tokens. Each user's tokens are stored separately and retrieved based on their WhatsApp number.

## Key Features

- **Multi-user Support**: Multiple users can connect their Google Drive accounts using their WhatsApp numbers
- **Token Isolation**: Each user's Google Drive tokens are stored separately and securely
- **WhatsApp Integration**: Seamless integration with WhatsApp webhook for command processing
- **Frontend Validation**: WhatsApp number validation in the frontend interface

## Implementation Details

### Backend Changes

#### 1. Storage System (`backend/utils/storage.py`)

- Modified storage backends to use WhatsApp numbers as keys instead of fixed keys
- Added sanitization for WhatsApp numbers to handle special characters in environment variables and filenames
- Updated all storage methods to accept WhatsApp number parameters

**Key Methods:**
```python
def save_token(self, token_data: Dict[str, Any], whatsapp_number: str) -> bool
def load_token(self, whatsapp_number: str) -> Optional[Dict[str, Any]]
def delete_token(self, whatsapp_number: str) -> bool
def token_exists(self, whatsapp_number: str) -> bool
```

#### 2. Google Drive Client (`backend/utils/google_drive_client.py`)

- Updated authentication methods to accept WhatsApp numbers
- Modified token management to use WhatsApp number-based storage
- Added current WhatsApp number tracking for session management

**Key Methods:**
```python
def _authenticate(self, code: str, whatsapp_number: str)
def is_authenticated(self, whatsapp_number: str = None)
def signIn(self, code: str, whatsapp_number: str)
```

#### 3. API Server (`backend/api_server.py`)

- Updated `/api/auth` endpoint to accept WhatsApp numbers
- Modified `/api/auth/status` endpoint to check authentication for specific WhatsApp numbers
- Updated webhook processing to set WhatsApp number context for command execution

**API Endpoints:**
```python
POST /api/auth
{
    "code": "authorization_code",
    "whatsapp_number": "+1234567890"
}

GET /api/auth/status?whatsapp_number=+1234567890
```

### Frontend Changes

#### 1. AuthStatus Component (`frontend/src/components/AuthStatus.js`)

- Added WhatsApp number input field with validation
- Updated authentication flow to include WhatsApp number
- Added real-time validation and error handling

**Features:**
- WhatsApp number validation (10-15 digits)
- Real-time error feedback
- Integration with Google OAuth flow

#### 2. App Component (`frontend/src/App.js`)

- Added global WhatsApp number state management
- Updated routing to pass WhatsApp number to child components
- Enhanced user experience with WhatsApp number context

#### 3. API Service (`frontend/src/services/api.js`)

- Updated `checkAuthStatus` to accept WhatsApp number parameter
- Modified API calls to include WhatsApp number context

## Usage Flow

### 1. User Authentication

1. User enters their WhatsApp number in the frontend
2. User clicks "Connect to Google Drive"
3. Google OAuth flow is initiated
4. Authorization code is sent to backend with WhatsApp number
5. Backend stores tokens using WhatsApp number as key
6. User is authenticated and can access their Google Drive

### 2. WhatsApp Command Processing

1. User sends command via WhatsApp
2. Webhook receives message with `from_number` (WhatsApp number)
3. Backend sets WhatsApp number context for command execution
4. Command is processed using user's specific Google Drive tokens
5. Response is sent back to user via WhatsApp

### 3. Token Management

- Tokens are automatically refreshed when expired
- Each user's tokens are stored separately
- Tokens can be deleted individually per user

## Security Considerations

1. **Token Isolation**: Each user's tokens are completely isolated
2. **Input Validation**: WhatsApp numbers are validated on both frontend and backend
3. **Sanitization**: Special characters in WhatsApp numbers are handled safely
4. **Environment Variables**: Tokens are stored securely in environment variables or files

## Testing

Run the test script to verify the implementation:

```bash
cd backend
python test_whatsapp_auth.py
```

The test script will:
- Test storage functionality with various WhatsApp number formats
- Test API endpoints (requires server to be running)
- Verify token isolation between different users

## Configuration

### Environment Variables

The system uses the following environment variables:

- `GOOGLE_DRIVE_CREDENTIALS_FILE`: Path to Google OAuth credentials
- `STORAGE_BACKEND`: Storage backend type ('file' or 'env')
- `STORAGE_PREFIX`: Prefix for environment variable storage

### Storage Backends

1. **Environment Storage** (Default): Stores tokens in environment variables
2. **File Storage**: Stores tokens as JSON files in specified directory

## Error Handling

- Invalid WhatsApp numbers are rejected with appropriate error messages
- Missing WhatsApp numbers return 400 Bad Request
- Authentication failures are logged and reported to user
- Token refresh failures are handled gracefully

## Future Enhancements

1. **User Management**: Add user registration and profile management
2. **Token Expiry Notifications**: Notify users when tokens are about to expire
3. **Multi-device Support**: Allow users to connect multiple devices
4. **Admin Panel**: Add administrative interface for user management
5. **Analytics**: Track usage patterns per user

## Troubleshooting

### Common Issues

1. **Invalid WhatsApp Number**: Ensure the number is in international format
2. **Token Not Found**: Verify the WhatsApp number matches the one used during authentication
3. **Authentication Failed**: Check Google OAuth credentials and scopes
4. **Storage Issues**: Verify storage backend configuration

### Debug Mode

Enable debug logging by setting the log level:

```python
logging.basicConfig(level=logging.DEBUG)
```

This will provide detailed information about token storage and retrieval operations.
