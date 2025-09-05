#!/usr/bin/env python3
"""
Quick test for ColPali integration with Morphik SDK
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Morphik SDK
try:
    from morphik import Morphik
    print("✅ Morphik SDK imported successfully")
except ImportError:
    print("❌ Morphik SDK not found. Installing...")
    os.system("pip install morphik")
    from morphik import Morphik

def test_colpali():
    """Test ColPali functionality."""
    
    # Connect to Morphik
    morphik_uri = os.getenv("MORPHIK_URI", "http://localhost:8000")
    print(f"\n🔗 Connecting to Morphik at: {morphik_uri}")
    
    try:
        db = Morphik(
            morphik_uri, 
            timeout=10000,
            is_local=True  # For local development
        )
        print("✅ Connected to Morphik")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Test file path
    pdf_file = "examples/assets/colpali_example.pdf"
    
    if not Path(pdf_file).exists():
        print(f"❌ Test PDF not found: {pdf_file}")
        return
    
    print(f"\n📄 Ingesting PDF with ColPali: {pdf_file}")
    
    try:
        # Ingest with ColPali
        result = db.ingest_file(
            pdf_file, 
            use_colpali=True  # Enable ColPali processing
        )
        print(f"✅ Document ingested successfully")
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        return
    
    # Test retrieval
    test_query = "At what frequency do we achieve the highest Image Rejection Ratio?"
    print(f"\n🔍 Testing retrieval with query: '{test_query}'")
    
    try:
        chunks = db.retrieve_chunks(
            test_query,
            use_colpali=True,
            k=3
        )
        
        print(f"✅ Retrieved {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            # Check if it's an image chunk
            if hasattr(chunk.content, 'show'):  # PIL Image
                print("  Type: IMAGE")
                print(f"  Metadata: {chunk.metadata}")
            else:
                content_preview = str(chunk.content)[:200]
                print(f"  Content: {content_preview}...")
                
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return
    
    # Test query with RAG
    print(f"\n💬 Testing RAG query...")
    
    try:
        response = db.query(
            test_query,
            use_colpali=True,
            k=3
        )
        
        print(f"✅ RAG Response:")
        print(f"  {response.completion}")
        
    except Exception as e:
        print(f"❌ RAG query failed: {e}")
    
    print("\n✨ ColPali test completed!")

if __name__ == "__main__":
    test_colpali()