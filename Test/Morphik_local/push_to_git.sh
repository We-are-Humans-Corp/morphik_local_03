#!/bin/bash

# Git Push Script for Morphik Local

echo "🚀 Starting Git push to Morphik_local repository..."

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
fi

# Add remote if not exists
if ! git remote | grep -q "origin"; then
    echo "🔗 Adding remote repository..."
    git remote add origin https://github.com/We-are-Humans-Corp/Morphik_local.git
else
    echo "🔄 Updating remote URL..."
    git remote set-url origin https://github.com/We-are-Humans-Corp/Morphik_local.git
fi

# Add all files
echo "📝 Adding all files..."
git add .

# Commit
echo "💾 Creating commit..."
git commit -m "feat: Complete Morphik self-hosted setup with authentication

- Add user authentication system (register/login)
- Fix Claude model integration
- Add model name mapping for LiteLLM
- Update UI components
- Add comprehensive documentation
- Configure Docker setup

Co-authored-by: Claude <assistant@anthropic.com>"

# Push to main branch
echo "📤 Pushing to GitHub..."
git push -u origin main --force

echo "✅ Done! Check your repository at: https://github.com/We-are-Humans-Corp/Morphik_local"