#!/usr/bin/env python3
"""
ColPali Integration Example for Local Morphik Setup

This example demonstrates how to use ColPali with Morphik when ColPali
is hosted on Modal as a separate API service.

Prerequisites:
1. Morphik API running locally (port 8000)
2. ColPali service running on Modal
3. PostgreSQL with pgvector extension
"""

import os
import requests
import json
from pathlib import Path

# Configuration
MORPHIK_API_URL = "http://localhost:8000"
PDF_FILE = "examples/assets/colpali_example.pdf"

def upload_document():
    """Upload a PDF document for ColPali processing."""
    
    print("📄 Uploading PDF document for ColPali processing...")
    
    # Check if file exists
    if not Path(PDF_FILE).exists():
        print(f"❌ File not found: {PDF_FILE}")
        return None
    
    # Upload file
    with open(PDF_FILE, 'rb') as f:
        files = {'file': (Path(PDF_FILE).name, f, 'application/pdf')}
        
        # ColPali will be used automatically based on server configuration
        response = requests.post(
            f"{MORPHIK_API_URL}/api/files/upload",
            files=files,
            headers={"X-Entity-ID": "test-user"}  # Dev mode header
        )
    
    if response.status_code == 200:
        result = response.json()
        doc_id = result['document_id']
        print(f"✅ Document uploaded successfully! ID: {doc_id}")
        return doc_id
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

def search_documents(query, k=3):
    """Search documents using ColPali visual embeddings."""
    
    print(f"\n🔍 Searching for: '{query}'")
    
    response = requests.post(
        f"{MORPHIK_API_URL}/api/chunks/retrieve",
        json={
            "text": query,
            "k": k,
            "use_colpali": True  # Force ColPali for visual search
        },
        headers={"X-Entity-ID": "test-user"}
    )
    
    if response.status_code == 200:
        chunks = response.json()
        print(f"✅ Found {len(chunks)} relevant chunks\n")
        return chunks
    else:
        print(f"❌ Search failed: {response.text}")
        return []

def query_with_context(query, k=3):
    """Query using RAG with ColPali-retrieved context."""
    
    print(f"\n💬 Querying with context: '{query}'")
    
    response = requests.post(
        f"{MORPHIK_API_URL}/api/query",
        json={
            "text": query,
            "k": k,
            "model": "ollama_llama",  # Use configured model
            "use_colpali": True
        },
        headers={"X-Entity-ID": "test-user"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Answer: {result['completion']}\n")
        return result
    else:
        print(f"❌ Query failed: {response.text}")
        return None

def check_document_status(doc_id):
    """Check processing status of uploaded document."""
    
    response = requests.get(
        f"{MORPHIK_API_URL}/api/documents/{doc_id}",
        headers={"X-Entity-ID": "test-user"}
    )
    
    if response.status_code == 200:
        doc = response.json()
        return doc['status']
    return None

def main():
    """Run ColPali example workflow."""
    
    print("=" * 60)
    print("🚀 ColPali Integration Example")
    print("=" * 60)
    
    # Step 1: Upload document
    doc_id = upload_document()
    if not doc_id:
        return
    
    # Step 2: Wait for processing
    import time
    print("\n⏳ Waiting for document processing...")
    max_attempts = 30
    for i in range(max_attempts):
        status = check_document_status(doc_id)
        if status == "completed":
            print("✅ Document processed successfully!")
            break
        elif status == "failed":
            print("❌ Document processing failed")
            return
        else:
            print(f"   Status: {status} (attempt {i+1}/{max_attempts})")
            time.sleep(2)
    
    # Step 3: Search using ColPali
    test_queries = [
        "At what frequency do we achieve the highest Image Rejection Ratio?",
        "What is the LNA gain?",
        "Show me circuit diagrams"
    ]
    
    for query in test_queries:
        chunks = search_documents(query, k=3)
        
        if chunks:
            print("Retrieved chunks:")
            for i, chunk in enumerate(chunks, 1):
                content = chunk.get('content', '')
                # For image chunks, content will be base64 encoded
                if content.startswith('data:image'):
                    print(f"  {i}. [IMAGE - Page {chunk.get('metadata', {}).get('page_number', 'unknown')}]")
                else:
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"  {i}. {preview}")
                print(f"     Score: {chunk.get('score', 0):.4f}")
    
    # Step 4: Query with RAG
    print("\n" + "=" * 60)
    print("📚 RAG Query with ColPali Context")
    print("=" * 60)
    
    result = query_with_context(
        "Based on the document, at what frequency do we achieve the highest Image Rejection Ratio? Provide specific details.",
        k=5
    )
    
    if result:
        print(f"\n📝 Sources used: {len(result.get('chunks', []))} chunks")
        print(f"🤖 Model: {result.get('model', 'unknown')}")
    
    print("\n✨ Example completed successfully!")

if __name__ == "__main__":
    main()