import os
from typing import Optional

class Config:
    """Configuration management for the application"""
    
    # Storage configuration
    STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'file')  # 'environment' or 'file'
    STORAGE_PREFIX = os.getenv('STORAGE_PREFIX', 'STORAGE_')
    STORAGE_DIR = os.getenv('STORAGE_DIR', '/tmp')
    
    # Google Drive configuration
    GOOGLE_DRIVE_CREDENTIALS_FILE = os.getenv('GOOGLE_DRIVE_CREDENTIALS_FILE')
    GOOGLE_DRIVE_REDIRECT_URI = os.getenv('GOOGLE_DRIVE_REDIRECT_URI', 'https://whatsapp-drive-assistent.vercel.app')
    
    # Environment detection
    IS_DEVELOPMENT = os.getenv('FLASK_ENV') == 'DEV'

    print(f"Config - :  IS_DEVELOPMENT: {IS_DEVELOPMENT}, STORAGE_BACKEND: {STORAGE_BACKEND}")
    print(f"Config - GOOGLE_DRIVE_CREDENTIALS_FILE: {GOOGLE_DRIVE_CREDENTIALS_FILE}")
    print(f"Config - STORAGE_DIR: {STORAGE_DIR}")
    print(f"Config - STORAGE_PREFIX: {STORAGE_PREFIX}")
    print(f"Config - GOOGLE_DRIVE_REDIRECT_URI: {GOOGLE_DRIVE_REDIRECT_URI}")

    
    @classmethod
    def get_storage_backend(cls) -> str:
        """Get the appropriate storage backend based on environment"""
        if cls.IS_DEVELOPMENT:
            return cls.STORAGE_BACKEND
        else:
            return 'environment'  # Default to environment for production
    
    @classmethod
    def get_storage_config(cls) -> dict:
        """Get storage configuration"""
        return {
            'backend': cls.get_storage_backend(),
            'prefix': cls.STORAGE_PREFIX,
            'storage_dir': cls.STORAGE_DIR
        }
