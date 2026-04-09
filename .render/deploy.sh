#!/bin/bash

# Render Auto-Deploy Script
# This script is triggered automatically when pushed to GitHub

echo "=== CampusGenie Auto-Deploy to Render ==="
echo "Repository: $REPOSITORY_URL"
echo "Branch: $BRANCH"
echo "Commit: $COMMIT_SHA"

# Deploy backend
echo "Deploying backend service..."
render deploy --service campusgenie-backend

# Deploy ChromaDB
echo "Deploying ChromaDB service..."
render deploy --service campusgenie-chroma

# Deploy Ollama
echo "Deploying Ollama service..."
render deploy --service campusgenie-ollama

# Deploy frontend
echo "Deploying frontend service..."
render deploy --service campusgenie-frontend

echo "=== Deployment Complete ==="
echo "Frontend: https://campusgenie-frontend.onrender.com"
echo "Backend: https://campusgenie-backend.onrender.com"
echo "Health: https://campusgenie-backend.onrender.com/api/health"
