import os
import json
import base64
from typing import Optional, Dict, Any
from .config import Config


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
        print("Using EnvironmentStorageBackend with prefix for vercel :", prefix)
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
            env_key = f"{self.prefix}TOKEN_{whatsapp_number}"
            os.environ[env_key] = token_encoded

            print('vercel storage env_key', env_key)
            
            print(f"Token saved successfully for WhatsApp number: {whatsapp_number}")
            return True
            
        except Exception as e:
            print(f"Failed to save token for WhatsApp number {whatsapp_number}: {e}")
            return False
    
    def load_token(self, whatsapp_number: str) -> Optional[Dict[str, Any]]:
        """
        Load token data from persistent storage.
        
        Args:
            whatsapp_number: WhatsApp number to use as storage key
            
        Returns:
            Dict containing token data or None if not found/invalid
        """
        print('vercel load_token whatsapp_number', whatsapp_number)
        try:
            # Sanitize WhatsApp number for environment variable
            whatsapp_number = whatsapp_number.replace('+', 'PLUS').replace('-', 'DASH').replace(' ', 'SPACE')
            env_key = f"{self.prefix}TOKEN_{whatsapp_number}"
            token_encoded = os.environ.get(env_key)
            
            if not token_encoded:
                print(f"No token found for WhatsApp number: {whatsapp_number}")
                return None
            
            # Decode from base64
            token_json = base64.b64decode(token_encoded.encode('utf-8')).decode('utf-8')
            
            # Parse JSON
            token_data = json.loads(token_json)
            
            print(f"Token loaded successfully for WhatsApp number: {whatsapp_number}")
            return token_data
            
        except Exception as e:
            print(f"Failed to load token for WhatsApp number {whatsapp_number}: {e}")
            return None
    
    def delete_token(self, whatsapp_number: str) -> bool:
        """
        Delete token from persistent storage.
        
        Args:
            whatsapp_number: WhatsApp number to use as storage key
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        print('vercel delete whatsapp_number', whatsapp_number)

        try:
            # Sanitize WhatsApp number for environment variable
            env_key = f"{self.prefix}TOKEN_{whatsapp_number}"
            if env_key in os.environ:
                del os.environ[env_key]
                print(f"Token deleted successfully for WhatsApp number: {whatsapp_number}")
                return True
            else:
                print(f"No token found to delete for WhatsApp number: {whatsapp_number}")
                return True
                
        except Exception as e:
            print(f"Failed to delete token for WhatsApp number {whatsapp_number}: {e}")
            return False
    
    def token_exists(self, whatsapp_number: str) -> bool:
        env_key = f"{self.prefix}TOKEN_{whatsapp_number}"
        return env_key in os.environ and os.environ[env_key] is not None




class FileStorageBackend(StorageBackend):
    print("Storage backend using local files (for development/testing)")
    
    def __init__(self, storage_dir: str = "/tmp"):
        self.storage_dir = storage_dir
    
    def save_token(self, token_data: Dict[str, Any], whatsapp_number: str) -> bool:
        try:
            tmp_dir = os.path.join(os.getcwd(), "tmp")   # or use tempfile.gettempdir()
            os.makedirs(tmp_dir, exist_ok=True)          # Create folder if missing

            file_path = os.path.join(tmp_dir, f"token_{whatsapp_number}.json")

            # file_path = os.path.join(self.storage_dir, f"token_{whatsapp_number}.json")

            with open(file_path, 'w') as f:
                json.dump(token_data, f)

            print(f"Token saved successfully to file for WhatsApp number: {whatsapp_number}")
            return True
        except Exception as e:
            print(f"Failed to save token to file for WhatsApp number {whatsapp_number}: {e}")
            return False
    
    def load_token(self, whatsapp_number: str) :
        try:
            file_path =  os.path.join(os.path.join(os.getcwd(), "tmp")  , f"token_{whatsapp_number}.json")

            print('file_path', file_path)

            if not os.path.exists(file_path):
                print(f"No token file found for WhatsApp number: {whatsapp_number}")
                return None
            
            with open(file_path, 'r') as f:
                token_data = json.load(f)

            print(f"Token loaded successfully from file for WhatsApp number: {whatsapp_number}")
            return token_data
        except Exception as e:
            print(f"Failed to load token from file for WhatsApp number {whatsapp_number}: {e}")
            return None
    
    def delete_token(self, whatsapp_number: str) -> bool:
        try:
            file_path =  os.path.join(os.path.join(os.getcwd(), "tmp")  , f"token_{whatsapp_number}.json")

            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Token deleted successfully from file for WhatsApp number: {whatsapp_number}")
            else:
                print(f"No token file found to delete for WhatsApp number: {whatsapp_number}")
            return True
        except Exception as e:
            print(f"Failed to delete token file for WhatsApp number {whatsapp_number}: {e}")
            return False
    
    def token_exists(self, whatsapp_number: str) -> bool:
        file_path =  os.path.join(os.path.join(os.getcwd(), "tmp")  , f"token_{whatsapp_number}.json")

        return os.path.exists(file_path)



class PersistentStorage:
    """
    Persistent storage utility for Vercel serverless environment.
    Supports multiple storage backends.
    """
    
    def __init__(self, backend: StorageBackend = None):
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

    print(f"Creating storage instance with config: {config}")
    
    if config['backend'] == 'file':
        backend = FileStorageBackend(config['storage_dir'])
    else:
        backend = EnvironmentStorageBackend(config['prefix'])
    
    return PersistentStorage(backend)

# Global storage instance
storage = create_storage_instance()
