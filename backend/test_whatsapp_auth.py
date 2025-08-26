#!/usr/bin/env python3
"""
Test script for WhatsApp number-based authentication
"""

import requests
import json
import os
from utils.storage import storage

def test_storage_with_whatsapp_number():
    """Test storage functionality with WhatsApp numbers"""
    print("Testing storage with WhatsApp numbers...")
    
    # Test data
    test_token = {
        "token": "test_token_123",
        "refresh_token": "refresh_token_456",
        "expires_in": 3600
    }
    
    whatsapp_numbers = [
        "+1234567890",
        "+44-20-7946-0958",
        "+1 555 123 4567",
        "1234567890"
    ]
    
    for number in whatsapp_numbers:
        print(f"\nTesting with WhatsApp number: {number}")
        
        # Test save
        success = storage.save_token(test_token, number)
        print(f"  Save success: {success}")
        
        # Test exists
        exists = storage.token_exists(number)
        print(f"  Token exists: {exists}")
        
        # Test load
        loaded_token = storage.load_token(number)
        print(f"  Load success: {loaded_token is not None}")
        if loaded_token:
            print(f"  Loaded token matches: {loaded_token == test_token}")
        
        # Test delete
        delete_success = storage.delete_token(number)
        print(f"  Delete success: {delete_success}")
        
        # Verify deletion
        exists_after_delete = storage.token_exists(number)
        print(f"  Token exists after delete: {exists_after_delete}")

def test_api_endpoints():
    """Test API endpoints with WhatsApp numbers"""
    print("\n\nTesting API endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Test auth status endpoint
    test_number = "+1234567890"
    print(f"\nTesting auth status with WhatsApp number: {test_number}")
    
    try:
        response = requests.get(f"{base_url}/api/auth/status", params={"whatsapp_number": test_number})
        print(f"  Status code: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test auth endpoint (without actual code)
    print(f"\nTesting auth endpoint with WhatsApp number: {test_number}")
    
    try:
        response = requests.post(f"{base_url}/api/auth", json={
            "code": "test_code_123",
            "whatsapp_number": test_number
        })
        print(f"  Status code: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    print("WhatsApp Number-Based Authentication Test")
    print("=" * 50)
    
    # Test storage functionality
    test_storage_with_whatsapp_number()
    
    # Test API endpoints (requires server to be running)
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("Test completed!")
