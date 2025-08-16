#!/usr/bin/env python3
"""
Test script for persistent storage functionality
"""

import os
import sys
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.storage import storage, EnvironmentStorageBackend, FileStorageBackend, PersistentStorage
from utils.config import Config

def test_environment_storage():
    """Test environment variable storage backend"""
    print("Testing Environment Storage Backend...")
    
    # Create test data
    test_token = {
        "token": "test_token_value",
        "refresh_token": "test_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "scopes": ["https://www.googleapis.com/auth/drive"]
    }
    
    # Test save
    success = storage.save_token(test_token, "TEST_TOKEN")
    print(f"Save token: {'SUCCESS' if success else 'FAILED'}")
    
    # Test exists
    exists = storage.token_exists("TEST_TOKEN")
    print(f"Token exists: {'YES' if exists else 'NO'}")
    
    # Test load
    loaded_token = storage.load_token("TEST_TOKEN")
    if loaded_token:
        print(f"Load token: SUCCESS - Token matches: {loaded_token == test_token}")
    else:
        print("Load token: FAILED")
    
    # Test delete
    success = storage.delete_token("TEST_TOKEN")
    print(f"Delete token: {'SUCCESS' if success else 'FAILED'}")
    
    # Verify deletion
    exists = storage.token_exists("TEST_TOKEN")
    print(f"Token exists after deletion: {'YES' if exists else 'NO'}")
    
    print()

def test_file_storage():
    """Test file-based storage backend"""
    print("Testing File Storage Backend...")
    
    # Create file storage backend
    file_storage = PersistentStorage(FileStorageBackend("/tmp"))
    
    # Create test data
    test_token = {
        "token": "test_token_value",
        "refresh_token": "test_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "scopes": ["https://www.googleapis.com/auth/drive"]
    }
    
    # Test save
    success = file_storage.save_token(test_token, "TEST_FILE_TOKEN")
    print(f"Save token: {'SUCCESS' if success else 'FAILED'}")
    
    # Test exists
    exists = file_storage.token_exists("TEST_FILE_TOKEN")
    print(f"Token exists: {'YES' if exists else 'NO'}")
    
    # Test load
    loaded_token = file_storage.load_token("TEST_FILE_TOKEN")
    if loaded_token:
        print(f"Load token: SUCCESS - Token matches: {loaded_token == test_token}")
    else:
        print("Load token: FAILED")
    
    # Test delete
    success = file_storage.delete_token("TEST_FILE_TOKEN")
    print(f"Delete token: {'SUCCESS' if success else 'FAILED'}")
    
    # Verify deletion
    exists = file_storage.token_exists("TEST_FILE_TOKEN")
    print(f"Token exists after deletion: {'YES' if exists else 'NO'}")
    
    print()

def test_configuration():
    """Test configuration settings"""
    print("Testing Configuration...")
    
    print(f"Storage Backend: {Config.get_storage_backend()}")
    print(f"Is Vercel: {Config.IS_VERCEL}")
    print(f"Is Development: {Config.IS_DEVELOPMENT}")
    print(f"Storage Config: {Config.get_storage_config()}")
    print()

if __name__ == "__main__":
    print("Persistent Storage Test Suite")
    print("=" * 40)
    
    test_configuration()
    test_environment_storage()
    test_file_storage()
    
    print("Test suite completed!")
