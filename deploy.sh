#!/bin/bash

# CampusGenie Deployment Script
# Supports both Vercel and Render deployment

set -e

echo "🚀 CampusGenie Deployment Script"
echo "================================="

# Check if platform is specified
PLATFORM=${1:-"vercel"}
if [ "$#" -gt 0 ]; then
    PLATFORM=$1
fi

echo "📍 Platform: $PLATFORM"

case $PLATFORM in
    "vercel")
        echo "📋 Deploying to Vercel..."
        
        # Check if Vercel CLI is installed
        if ! command -v vercel &> /dev/null; then
            echo "❌ Vercel CLI not found. Installing..."
            npm install -g vercel
        fi
        
        # Check if logged in
        if ! vercel whoami &> /dev/null; then
            echo "🔐 Please login to Vercel first:"
            vercel login
        fi
        
        # Deploy
        echo "📦 Building and deploying..."
        vercel --prod
        
        echo "✅ Vercel deployment complete!"
        echo "🌐 Your app should be available at: https://campusgenie.vercel.app"
        ;;
    
    "render")
        echo "🎯 Deploying to Render..."
        
        # Check if Render CLI is installed
        if ! command -v render &> /dev/null; then
            echo "❌ Render CLI not found. Please install from https://render.com/docs/cli"
            exit 1
        fi
        
        # Deploy
        echo "📦 Triggering deployment..."
        # Note: Render auto-deploys from GitHub pushes
        git push origin main
        
        echo "✅ Render deployment triggered!"
        echo "🌐 Check your Render dashboard for deployment status"
        echo "🌐 Your app will be available at: https://campusgenie.onrender.com"
        ;;
    
    *)
        echo "❌ Unsupported platform: $PLATFORM"
        echo "📍 Supported platforms: vercel, render"
        echo "💡 Usage: ./deploy.sh [vercel|render]"
        exit 1
        ;;
esac

echo ""
echo "📚 Deployment Notes:"
echo "• Make sure all environment variables are set in the platform dashboard"
echo "• First deployment may take longer due to cold starts"
echo "• Monitor logs for any issues"
echo "• Test all endpoints after deployment"
