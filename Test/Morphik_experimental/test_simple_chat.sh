#!/bin/bash
# Simple test for document chat API

echo "=== Testing Morphik Document Chat API ==="
echo

# Use a dummy chat ID for testing
CHAT_ID="test-$(date +%s)"

echo "1. Testing document chat completion with Ollama model:"
echo "Chat ID: $CHAT_ID"
echo

# Simple test with just a message
curl -X POST "http://localhost:8000/document/chat/$CHAT_ID/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you respond with a simple greeting?"
  }' \
  -v 2>&1 | grep -E "(< HTTP|data:|error|Error)" | head -50

echo
echo "2. Testing with a specific document (if exists):"
# First get a document ID if available
DOC_ID=$(curl -s http://localhost:8000/documents | jq -r '.[0].id' 2>/dev/null)

if [ ! -z "$DOC_ID" ] && [ "$DOC_ID" != "null" ]; then
    echo "Using document ID: $DOC_ID"
    curl -X POST "http://localhost:8000/document/chat/$CHAT_ID/complete" \
      -H "Content-Type: application/json" \
      -d "{
        \"message\": \"What is this document about?\",
        \"document_id\": \"$DOC_ID\"
      }" \
      --no-buffer 2>&1 | head -20
else
    echo "No documents found, skipping document-based test"
fi

echo
echo "3. Checking backend logs for model errors:"
docker logs morphik-core-morphik-1 --tail 200 2>&1 | grep -E "(model|Model|claude_opus|litellm|provider)" | tail -30