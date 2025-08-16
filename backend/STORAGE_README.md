# Persistent Storage Implementation

This document describes the persistent storage implementation for the Google Drive client, designed to work with Vercel's serverless environment.

## Overview

The persistent storage system provides a way to store and retrieve Google Drive authentication tokens across serverless function invocations. It supports multiple storage backends and automatically selects the appropriate one based on the deployment environment.

## Storage Backends

### 1. Environment Variable Storage (Default for Vercel)
- **Use Case**: Production deployments on Vercel
- **Implementation**: Stores tokens as base64-encoded environment variables
- **Pros**: Works in serverless environments, no external dependencies
- **Cons**: Limited by environment variable size limits, not persistent across deployments

### 2. File Storage (Development/Testing)
- **Use Case**: Local development and testing
- **Implementation**: Stores tokens as JSON files in a specified directory
- **Pros**: Simple, works offline, persistent
- **Cons**: Not suitable for serverless environments

## Configuration

The storage backend is automatically selected based on the environment:

```python
# Environment variables for configuration
STORAGE_BACKEND=environment  # 'environment' or 'file'
STORAGE_PREFIX=STORAGE_      # Prefix for environment variable keys
STORAGE_DIR=/tmp            # Directory for file storage (file backend only)
VERCEL=1                    # Automatically set by Vercel
```

### Automatic Backend Selection

- **Vercel Environment**: Always uses environment variable storage
- **Development Environment**: Uses the value of `STORAGE_BACKEND` environment variable
- **Production (non-Vercel)**: Defaults to environment variable storage

## Usage

### Basic Usage

```python
from utils.storage import storage

# Save a token
token_data = {
    "token": "access_token_value",
    "refresh_token": "refresh_token_value",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "scopes": ["https://www.googleapis.com/auth/drive"]
}

success = storage.save_token(token_data, "GOOGLE_TOKEN")

# Load a token
token_data = storage.load_token("GOOGLE_TOKEN")

# Check if token exists
exists = storage.token_exists("GOOGLE_TOKEN")

# Delete a token
success = storage.delete_token("GOOGLE_TOKEN")
```

### Custom Storage Backend

```python
from utils.storage import PersistentStorage, FileStorageBackend

# Create custom file storage
file_storage = PersistentStorage(FileStorageBackend("/custom/path"))

# Use the custom storage
file_storage.save_token(token_data, "CUSTOM_TOKEN")
```

## Integration with Google Drive Client

The Google Drive client automatically uses the persistent storage:

1. **Authentication**: Tokens are saved to persistent storage after successful authentication
2. **Token Refresh**: Refreshed tokens are automatically saved back to storage
3. **Session Persistence**: Tokens are loaded from storage on subsequent requests

## Testing

Run the test suite to verify storage functionality:

```bash
cd backend
python test_storage.py
```

## Environment Variables for Vercel

To use this on Vercel, you'll need to set the following environment variables in your Vercel project settings:

1. `GOOGLE_DRIVE_CREDENTIALS_FILE`: Path to your Google Drive credentials file
2. `GOOGLE_DRIVE_REDIRECT_URI`: Your OAuth redirect URI
3. `STORAGE_PREFIX`: (Optional) Custom prefix for storage keys

## Limitations

### Environment Variable Storage
- **Size Limit**: Environment variables have size limits (typically 4KB-32KB)
- **Persistence**: Not persistent across deployments (tokens are lost when code is redeployed)
- **Security**: Tokens are stored in plain text (base64 encoded)

### Recommendations for Production

For production use with high security requirements, consider:

1. **External Database**: Implement a database storage backend (Redis, PostgreSQL, etc.)
2. **Encryption**: Encrypt tokens before storage
3. **Token Rotation**: Implement automatic token refresh and rotation
4. **Monitoring**: Add logging and monitoring for token operations

## Future Enhancements

Potential improvements for the storage system:

1. **Database Backend**: Support for Redis, PostgreSQL, or MongoDB
2. **Encryption**: Built-in encryption for stored tokens
3. **Token Expiry**: Automatic cleanup of expired tokens
4. **Multiple Users**: Support for storing tokens for multiple users
5. **Backup/Restore**: Backup and restore functionality for tokens
