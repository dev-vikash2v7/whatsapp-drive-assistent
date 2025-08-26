import os
import json
import base64
from typing import Optional, Dict, Any
import logging
from .config import Config

logger = logging.getLogger(__name__)

class StorageBackend:
    """Abstract base class for storage backends"""
    
    def save_token(self, token_data: Dict[str, Any], whatsapp_number: str) -> bool:
        raise NotImplementedError
    
    def load_token(self, whatsapp_number: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
    
    def delete_token(self, whatsapp_number: str) -> bool:
        raise NotImplementedError
    
    def token_exists(self, whatsapp_number: str) -> bool:
        raise NotImplementedError

class EnvironmentStorageBackend(StorageBackend):
    """Storage backend using environment variables"""
    
    def __init__(self, prefix: str = "STORAGE_"):
        self.prefix = prefix
    
    def save_token(self, token_data: Dict[str, Any], whatsapp_number: str) -> bool:
        """
        Save token data to persistent storage using environment variables.
        
        Args:
            token_data: Dictionary containing token information
            whatsapp_number: WhatsApp number to use as storage key
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Convert token data to JSON string
            token_json = json.dumps(token_data)
            
            # Encode to base64 to handle special characters in environment variables
            token_encoded = base64.b64encode(token_json.encode('utf-8')).decode('utf-8')
            
            # Store in environment variable with WhatsApp number as key
            # Sanitize WhatsApp number for environment variable (remove special chars)
            sanitized_number = whatsapp_number.replace('+', 'PLUS').replace('-', 'DASH').replace(' ', 'SPACE')
            env_key = f"{self.prefix}TOKEN_{sanitized_number}"
            os.environ[env_key] = token_encoded
            
            logger.info(f"Token saved successfully for WhatsApp number: {whatsapp_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save token for WhatsApp number {whatsapp_number}: {e}")
            return False
    
    def load_token(self, whatsapp_number: str) -> Optional[Dict[str, Any]]:
        """
        Load token data from persistent storage.
        
        Args:
            whatsapp_number: WhatsApp number to use as storage key
            
        Returns:
            Dict containing token data or None if not found/invalid
        """
        try:
            # Sanitize WhatsApp number for environment variable
            sanitized_number = whatsapp_number.replace('+', 'PLUS').replace('-', 'DASH').replace(' ', 'SPACE')
            env_key = f"{self.prefix}TOKEN_{sanitized_number}"
            token_encoded = os.environ.get(env_key)
            
            if not token_encoded:
                logger.info(f"No token found for WhatsApp number: {whatsapp_number}")
                return None
            
            # Decode from base64
            token_json = base64.b64decode(token_encoded.encode('utf-8')).decode('utf-8')
            
            # Parse JSON
            token_data = json.loads(token_json)
            
            logger.info(f"Token loaded successfully for WhatsApp number: {whatsapp_number}")
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to load token for WhatsApp number {whatsapp_number}: {e}")
            return None
    
    def delete_token(self, whatsapp_number: str) -> bool:
        """
        Delete token from persistent storage.
        
        Args:
            whatsapp_number: WhatsApp number to use as storage key
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            # Sanitize WhatsApp number for environment variable
            sanitized_number = whatsapp_number.replace('+', 'PLUS').replace('-', 'DASH').replace(' ', 'SPACE')
            env_key = f"{self.prefix}TOKEN_{sanitized_number}"
            if env_key in os.environ:
                del os.environ[env_key]
                logger.info(f"Token deleted successfully for WhatsApp number: {whatsapp_number}")
                return True
            else:
                logger.info(f"No token found to delete for WhatsApp number: {whatsapp_number}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete token for WhatsApp number {whatsapp_number}: {e}")
            return False
    
    def token_exists(self, whatsapp_number: str) -> bool:
        """
        Check if token exists in persistent storage.
        
        Args:
            whatsapp_number: WhatsApp number to use as storage key
            
        Returns:
            bool: True if token exists, False otherwise
        """
        # Sanitize WhatsApp number for environment variable
        sanitized_number = whatsapp_number.replace('+', 'PLUS').replace('-', 'DASH').replace(' ', 'SPACE')
        env_key = f"{self.prefix}TOKEN_{sanitized_number}"
        return env_key in os.environ and os.environ[env_key] is not None

class FileStorageBackend(StorageBackend):
    """Storage backend using local files (for development/testing)"""
    
    def __init__(self, storage_dir: str = "/tmp"):
        self.storage_dir = storage_dir
    
    def save_token(self, token_data: Dict[str, Any], whatsapp_number: str) -> bool:
        try:
            # Sanitize WhatsApp number for filename
            sanitized_number = whatsapp_number.replace('+', 'PLUS').replace('-', 'DASH').replace(' ', 'SPACE')
            file_path = os.path.join(self.storage_dir, f"token_{sanitized_number}.json")
            with open(file_path, 'w') as f:
                json.dump(token_data, f)
            logger.info(f"Token saved successfully to file for WhatsApp number: {whatsapp_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to save token to file for WhatsApp number {whatsapp_number}: {e}")
            return False
    
    def load_token(self, whatsapp_number: str) -> Optional[Dict[str, Any]]:
        try:
            # Sanitize WhatsApp number for filename
            sanitized_number = whatsapp_number.replace('+', 'PLUS').replace('-', 'DASH').replace(' ', 'SPACE')
            file_path = os.path.join(self.storage_dir, f"token_{sanitized_number}.json")
            if not os.path.exists(file_path):
                logger.info(f"No token file found for WhatsApp number: {whatsapp_number}")
                return None
            
            with open(file_path, 'r') as f:
                token_data = json.load(f)
            logger.info(f"Token loaded successfully from file for WhatsApp number: {whatsapp_number}")
            return token_data
        except Exception as e:
            logger.error(f"Failed to load token from file for WhatsApp number {whatsapp_number}: {e}")
            return None
    
    def delete_token(self, whatsapp_number: str) -> bool:
        try:
            # Sanitize WhatsApp number for filename
            sanitized_number = whatsapp_number.replace('+', 'PLUS').replace('-', 'DASH').replace(' ', 'SPACE')
            file_path = os.path.join(self.storage_dir, f"token_{sanitized_number}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Token deleted successfully from file for WhatsApp number: {whatsapp_number}")
            else:
                logger.info(f"No token file found to delete for WhatsApp number: {whatsapp_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete token file for WhatsApp number {whatsapp_number}: {e}")
            return False
    
    def token_exists(self, whatsapp_number: str) -> bool:
        # Sanitize WhatsApp number for filename
        sanitized_number = whatsapp_number.replace('+', 'PLUS').replace('-', 'DASH').replace(' ', 'SPACE')
        file_path = os.path.join(self.storage_dir, f"token_{sanitized_number}.json")
        return os.path.exists(file_path)

class PersistentStorage:
    """
    Persistent storage utility for Vercel serverless environment.
    Supports multiple storage backends.
    """
    
    def __init__(self, backend: StorageBackend = None):
        # Use environment variables by default for Vercel compatibility
        self.backend = backend or EnvironmentStorageBackend()
    
    def save_token(self, token_data: Dict[str, Any], whatsapp_number: str) -> bool:
        return self.backend.save_token(token_data, whatsapp_number)
    
    def load_token(self, whatsapp_number: str) -> Optional[Dict[str, Any]]:
        return self.backend.load_token(whatsapp_number)
    
    def delete_token(self, whatsapp_number: str) -> bool:
        return self.backend.delete_token(whatsapp_number)
    
    def token_exists(self, whatsapp_number: str) -> bool:
        return self.backend.token_exists(whatsapp_number)

def create_storage_instance() -> PersistentStorage:
    """Create storage instance based on configuration"""
    config = Config.get_storage_config()
    
    if config['backend'] == 'file':
        backend = FileStorageBackend(config['storage_dir'])
    else:
        backend = EnvironmentStorageBackend(config['prefix'])
    
    return PersistentStorage(backend)

# Global storage instance
storage = create_storage_instance()
