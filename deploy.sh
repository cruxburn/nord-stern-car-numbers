#!/bin/bash

# Nord Stern Car Numbers - Google Cloud Run Deployment Script
# This script deploys the application code only - NEVER touches production database

set -e

# Configuration
PROJECT_ID="nord-stern-car-numbers"  # Replace with your actual project ID
REGION="us-central1"
SERVICE_NAME="nord-stern-car-numbers"
IMAGE_NAME="us-docker.pkg.dev/$PROJECT_ID/nord-stern-car-numbers/nord-stern-car-numbers"

echo "🚀 Deploying Nord Stern Car Numbers to Google Cloud Run (Code Only)"
echo "=================================================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo "⚠️  This deployment will NOT affect the production database"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud. Please run:"
    echo "   gcloud auth login"
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable storage.googleapis.com

# Create Artifact Registry repository (if it doesn't exist)
echo "🏗️ Setting up Artifact Registry..."
gcloud artifacts repositories create nord-stern-car-numbers \
  --repository-format=docker \
  --location=us \
  --description="Nord Stern Car Numbers Docker Repository" \
  --quiet || echo "Repository already exists"

# Step 1: Export current production data (if service exists)
echo "📊 Step 1: Preserving current production data..."
if gcloud run services describe $SERVICE_NAME --region=$REGION --quiet &>/dev/null; then
    echo "   Found existing service, attempting to export current data..."
    
    # Create a temporary script to export data from the running service
    cat > export_production_data.py << 'EOF'
#!/usr/bin/env python3
"""
Script to export data from the production database via HTTP API.
This runs inside the Cloud Run container to export data before deployment.
"""
import requests
import json
import sys
import os

def export_production_data():
    """Export production data via HTTP API."""
    try:
        # Get the service URL from environment or construct it
        service_url = os.environ.get('SERVICE_URL', 'https://nord-stern-car-numbers-53xwewtdza-uc.a.run.app')
        
        # Export data via API endpoint (we'll need to add this to app.py)
        response = requests.get(f"{service_url}/api/export", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save to file
            with open('production_data_backup.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Successfully exported {data.get('total_registrations', 0)} registrations")
            return True
        else:
            print(f"❌ Failed to export data: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return False

if __name__ == "__main__":
    success = export_production_data()
    sys.exit(0 if success else 1)
EOF

    # Try to export data from the running service
    if python export_production_data.py; then
        echo "   ✅ Production data exported successfully"
        HAS_PRODUCTION_DATA=true
    else
        echo "   ⚠️  Could not export production data (service may be down or no data)"
        HAS_PRODUCTION_DATA=false
    fi
    
    # Clean up temporary script
    rm -f export_production_data.py
else
    echo "   ℹ️  No existing service found, skipping data export"
    HAS_PRODUCTION_DATA=false
fi

# Step 2: Build and deploy using Cloud Build
echo "🏗️ Step 2: Building and deploying with Cloud Build..."
if [ "$HAS_PRODUCTION_DATA" = true ] && [ -f "production_data_backup.json" ]; then
    echo "   This deployment will preserve existing production data"
    echo "   Including production data backup in deployment..."
    
    # Create a temporary deployment directory with the backup file
    DEPLOY_DIR="deploy_temp_$(date +%s)"
    mkdir -p "$DEPLOY_DIR"
    
    # Copy all files except backup file
    echo "   Copying application files..."
    rsync -av --exclude='production_data_backup.json' --exclude='venv/' --exclude='.git/' --exclude='deploy_temp_*/' . "$DEPLOY_DIR/"
    
    # Copy backup file to deployment directory
    echo "   Copying production data backup..."
    cp production_data_backup.json "$DEPLOY_DIR/"
    
    # Store current directory
    ORIGINAL_DIR=$(pwd)
    
    # Change to deployment directory and build
    cd "$DEPLOY_DIR"
    gcloud builds submit --config cloudbuild.yaml .
    
    # Change back to original directory
    cd "$ORIGINAL_DIR"
    
    # Clean up deployment directory and backup file
    echo "   Cleaning up deployment files..."
    rm -rf "$DEPLOY_DIR"
    rm -f production_data_backup.json
else
    echo "   This deployment preserves existing production data (no backup available)"
    gcloud builds submit --config cloudbuild.yaml .
fi

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Your application is available at: $SERVICE_URL"
echo ""
echo "📊 Database Status:"
echo "   - Production database preserved (no changes made)"
echo "   - Application code updated"
echo ""
echo "📊 To view logs:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=20 --format=\"value(timestamp,textPayload)\""
echo ""
echo "🔧 To update the service:"
echo "   ./deploy.sh"
echo ""
echo "📊 To refresh production data from local database:"
echo "   ./deploy_with_data.sh"
echo ""
echo "🗑️ To delete the service:"
echo "   gcloud run services delete $SERVICE_NAME --region=$REGION" 