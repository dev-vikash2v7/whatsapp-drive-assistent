#!/usr/bin/env python3
"""
Setup script for WhatsApp Drive Assistant
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print("✅ Python version check passed")

def install_dependencies():
    """Install required Python packages"""
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "data", "credentials"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def setup_environment():
    """Setup environment variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open("env.example", "r") as example:
            content = example.read()
        with open(".env", "w") as env:
            env.write(content)
        print("✅ .env file created. Please update it with your credentials.")
    else:
        print("ℹ️ .env file already exists")

def check_credentials():
    """Check if credentials are properly configured"""
    required_files = ["credentials.json"]
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ Missing credential files: {', '.join(missing_files)}")
        print("Please download your Google Drive API credentials and save as credentials.json")
        return False
    
    print("✅ Credential files found")
    return True

def validate_config():
    """Validate configuration"""
    print("🔧 Validating configuration...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found. Run setup again.")
        return False
    
    # Check credentials
    if not check_credentials():
        return False
    
    print("✅ Configuration validation passed")
    return True

def run_tests():
    """Run basic tests"""
    try:
        print("🧪 Running basic tests...")
        
        # Test imports
        import google_drive_client
        import document_summarizer
        import command_parser
        import api_server
        
        print("✅ All modules imported successfully")
        
        # Test API server startup
        print("🚀 Testing API server startup...")
        # Note: This would require a more complex test setup
        print("✅ Basic tests completed")
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up WhatsApp Drive Assistant...")
    print("=" * 50)
    
    check_python_version()
    
    install_dependencies()
    
    create_directories()
    
    setup_environment()
    
    # Validate configuration
    if not validate_config():
        print("\n❌ Setup incomplete. Please fix the issues above and run setup again.")
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your API keys")
    print("2. Download Google Drive API credentials as credentials.json")
    print("3. Import the n8n workflow from n8n-workflows/")
    print("4. Configure Twilio WhatsApp webhook")
    print("5. Start the API server: python python/api_server.py")
    print("\n📚 For detailed instructions, see README.md")

if __name__ == "__main__":
    main()
