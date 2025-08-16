#!/usr/bin/env python3
"""
Migration script to transition from file-based token storage to persistent storage
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.storage import storage, FileStorageBackend, PersistentStorage
from utils.config import Config

def migrate_from_file_to_persistent():
    """Migrate tokens from file storage to persistent storage"""
    print("Migrating tokens from file storage to persistent storage...")
    
    # Old file path
    old_token_file = "/tmp/token.json"
    
    if not os.path.exists(old_token_file):
        print(f"No old token file found at {old_token_file}")
        return False
    
    try:
        # Read the old token file
        with open(old_token_file, 'r') as f:
            token_data = json.load(f)
        
        # Save to persistent storage
        success = storage.save_token(token_data, "GOOGLE_TOKEN")
        
        if success:
            print("Token migrated successfully!")
            
            # Create backup of old file
            backup_file = "/tmp/token.json.backup"
            shutil.copy2(old_token_file, backup_file)
            print(f"Old token file backed up to {backup_file}")
            
            # Optionally remove the old file
            remove_old = input("Remove old token file? (y/n): ").lower().strip()
            if remove_old == 'y':
                os.remove(old_token_file)
                print("Old token file removed.")
            
            return True
        else:
            print("Failed to save token to persistent storage")
            return False
            
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

def migrate_from_persistent_to_file():
    """Migrate tokens from persistent storage to file storage (for development)"""
    print("Migrating tokens from persistent storage to file storage...")
    
    # Load token from persistent storage
    token_data = storage.load_token("GOOGLE_TOKEN")
    
    if not token_data:
        print("No token found in persistent storage")
        return False
    
    try:
        # Create file storage backend
        file_storage = PersistentStorage(FileStorageBackend("/tmp"))
        
        # Save to file storage
        success = file_storage.save_token(token_data, "GOOGLE_TOKEN")
        
        if success:
            print("Token migrated to file storage successfully!")
            return True
        else:
            print("Failed to save token to file storage")
            return False
            
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

def verify_migration():
    """Verify that tokens are accessible in the target storage"""
    print("Verifying migration...")
    
    # Try to load token from persistent storage
    token_data = storage.load_token("GOOGLE_TOKEN")
    
    if token_data:
        print("✅ Token found in persistent storage")
        print(f"   Token type: {type(token_data)}")
        print(f"   Has access token: {'token' in token_data}")
        print(f"   Has refresh token: {'refresh_token' in token_data}")
        return True
    else:
        print("❌ No token found in persistent storage")
        return False

def main():
    """Main migration function"""
    print("Token Storage Migration Tool")
    print("=" * 40)
    
    # Check current configuration
    print(f"Current storage backend: {Config.get_storage_backend()}")
    print(f"Environment: {'Vercel' if Config.IS_VERCEL else 'Development'}")
    print()
    
    # Check if old token file exists
    old_token_file = "/tmp/token.json"
    if os.path.exists(old_token_file):
        print(f"Found old token file: {old_token_file}")
        migrate = input("Migrate to persistent storage? (y/n): ").lower().strip()
        
        if migrate == 'y':
            if migrate_from_file_to_persistent():
                verify_migration()
            else:
                print("Migration failed!")
    else:
        print("No old token file found.")
    
    # Check if token exists in persistent storage
    if storage.token_exists("GOOGLE_TOKEN"):
        print("\nToken found in persistent storage.")
        if Config.IS_DEVELOPMENT:
            migrate_to_file = input("Migrate to file storage for development? (y/n): ").lower().strip()
            if migrate_to_file == 'y':
                migrate_from_persistent_to_file()
    
    print("\nMigration tool completed!")

if __name__ == "__main__":
    main()
