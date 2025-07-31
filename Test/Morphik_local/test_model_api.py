#!/usr/bin/env python3
"""Test script to check if models are working through the API."""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_chat_completion():
    """Test chat completion with a simple message."""
    print("Testing chat completion API...")
    
    # Test different models
    models_to_test = [
        "ollama_llama",  # Local Ollama model
        "openai_gpt4-1-mini",  # OpenAI model
        "claude_sonnet"  # Claude model
    ]
    
    for model_id in models_to_test:
        print(f"\n--- Testing model: {model_id} ---")
        
        # Prepare the request
        url = f"{BASE_URL}/chat"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Simple test message
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Hello, I am working!' if you can receive this message."
                }
            ],
            "model": model_id,
            "stream": False
        }
        
        try:
            # Send request
            response = requests.post(url, headers=headers, json=data)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success! Response: {result}")
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {str(e)}")

def test_available_models():
    """Test getting available models."""
    print("\n=== Testing available models ===")
    
    try:
        response = requests.get(f"{BASE_URL}/custom")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print(f"Found {len(models)} custom models:")
            for model in models:
                print(f"  - {model['id']}: {model['name']} (provider: {model['provider']})")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {str(e)}")

def test_ollama_directly():
    """Test if Ollama is responding directly."""
    print("\n=== Testing Ollama directly ===")
    
    try:
        # Test Ollama API directly
        response = requests.get("http://localhost:11434/api/tags")
        print(f"Ollama status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Ollama models available: {data}")
        else:
            print(f"Ollama error: {response.text}")
            
    except Exception as e:
        print(f"Ollama not accessible: {str(e)}")

if __name__ == "__main__":
    # Test available models first
    test_available_models()
    
    # Test Ollama directly
    test_ollama_directly()
    
    # Test chat completion
    test_chat_completion()