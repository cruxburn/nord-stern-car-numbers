#!/bin/bash

# Nord Stern Car Numbers - Google Cloud Setup Script
# This script sets up the initial Google Cloud configuration for deployment

set -e

echo "🚀 Nord Stern Car Numbers - Google Cloud Setup"
echo "=============================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK is not installed."
    echo "Please install it first:"
    echo "  macOS: brew install google-cloud-sdk"
    echo "  Or download from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ Google Cloud SDK is installed"

# Get project ID
read -p "Enter your Google Cloud Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID is required"
    exit 1
fi

echo "📋 Setting up project: $PROJECT_ID"

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Please authenticate with Google Cloud..."
    gcloud auth login
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable logging.googleapis.com

# Update deployment script
echo "📝 Updating deployment script..."
sed -i '' "s/your-google-cloud-project-id/$PROJECT_ID/g" deploy.sh

# Make scripts executable
chmod +x deploy.sh

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Ensure billing is enabled for your project"
echo "2. Run: ./deploy.sh"
echo ""
echo "Your application will be deployed to:"
echo "https://nord-stern-car-numbers-xxxxx-uc.a.run.app"
echo ""
echo "📚 For detailed instructions, see: GOOGLE_WORKSPACE_DEPLOYMENT.md" 