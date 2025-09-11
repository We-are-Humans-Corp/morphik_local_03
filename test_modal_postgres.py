#!/usr/bin/env python3
"""
Test if Modal can connect to PostgreSQL
"""

import requests
import json

def test_postgres_connection():
    """Test PostgreSQL connection through Modal endpoint"""
    
    url = "https://rugusev--morphik-processor-process-colpali.modal.run"
    
    # Special test payload to check DB connection
    payload = {
        "type": "test_connection",
        "data": "test"
    }
    
    print("🔍 Testing PostgreSQL connection from Modal...")
    print(f"📍 Endpoint: {url}")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📡 Response status: {response.status_code}")
        print(f"📄 Response: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                print(f"\n❌ Error from Modal: {result['error']}")
                if "traceback" in result:
                    print("Traceback:")
                    print(result['traceback'][:1000])
        
    except Exception as e:
        print(f"\n❌ Request error: {e}")

if __name__ == "__main__":
    test_postgres_connection()