#!/usr/bin/env python3
"""
Test ColPali endpoint on Modal.com
"""

import requests
import json
import base64
from PIL import Image
import io

def create_test_image():
    """Create a simple test image and convert to base64"""
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"

def test_colpali_endpoint():
    """Test the ColPali endpoint with a simple image"""
    
    # Endpoint URL
    url = "https://rugusev--morphik-processor-process-colpali.modal.run"
    
    # Create test image
    test_image = create_test_image()
    
    # Test payload
    payload = {
        "type": "image",
        "data": test_image,
        "document_id": "test_doc_001",
        "chunk_id": "test_chunk_001"
    }
    
    print("🚀 Testing ColPali endpoint...")
    print(f"📍 URL: {url}")
    print(f"📦 Payload size: {len(json.dumps(payload))} bytes")
    
    try:
        # Make POST request
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! Response received:")
            print(f"  - Status: {result.get('status')}")
            print(f"  - Model: {result.get('model')}")
            print(f"  - Embeddings shape: {result.get('shape')}")
            print(f"  - Saved to DB: {result.get('saved_to_db')}")
            
            # Check embeddings
            if 'embeddings' in result:
                embeddings = result['embeddings']
                print(f"  - Embeddings length: {len(embeddings) if isinstance(embeddings, list) else 'N/A'}")
                if isinstance(embeddings, list) and len(embeddings) > 0:
                    print(f"  - First embedding sample: {embeddings[0][:5] if isinstance(embeddings[0], list) else embeddings[:5]}...")
            
            return True
        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n⏱️ Request timed out (30s). The endpoint might be cold starting...")
        print("Try running the test again in a minute.")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_health_endpoint():
    """Quick health check first"""
    url = "https://rugusev--morphik-processor-health.modal.run"
    print("🏥 Checking health endpoint first...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"Response: {response.json()}")
            return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("ColPali Modal.com Endpoint Test")
    print("=" * 60)
    
    # Test health first
    if test_health_endpoint():
        print("\n" + "=" * 60)
        # Test ColPali
        success = test_colpali_endpoint()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 All tests passed successfully!")
        else:
            print("⚠️ Some tests failed. Check the output above.")
    else:
        print("⚠️ Health check failed. The service might be down.")