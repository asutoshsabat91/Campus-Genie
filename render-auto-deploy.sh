#!/bin/bash

# CampusGenie Auto-Deploy Script for Render
# Automatically deploys all services to Render

set -e

echo "=== CampusGenie Auto-Deploy to Render ==="
echo "========================================"

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "Installing Render CLI..."
    npm install -g @render/cli
fi

# Check if logged in to Render
if ! render whoami &> /dev/null; then
    echo "Please login to Render first:"
    echo "1. Go to https://render.com"
    echo "2. Click 'Account' -> 'API Keys'"
    echo "3. Create API key"
    echo "4. Run: render login"
    exit 1
fi

echo "Deploying CampusGenie to Render..."

# Deploy backend service
echo "Deploying backend service..."
render deploy --service campusgenie-backend --config backend/Dockerfile

# Deploy ChromaDB service
echo "Deploying ChromaDB service..."
render deploy --service campusgenie-chroma --config backend/Dockerfile

# Deploy Ollama service
echo "Deploying Ollama service..."
render deploy --service campusgenie-ollama --config backend/Dockerfile

# Deploy frontend service
echo "Deploying frontend service..."
render deploy --service campusgenie-frontend --config frontend/Dockerfile

echo "=== Deployment Complete ==="
echo "========================"
echo "Frontend: https://campusgenie-frontend.onrender.com"
echo "Backend API: https://campusgenie-backend.onrender.com"
echo "Health Check: https://campusgenie-backend.onrender.com/api/health"
echo ""
echo "Your CampusGenie is now live! Test it at the frontend URL above."
