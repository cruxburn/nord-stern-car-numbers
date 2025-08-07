#!/bin/bash

# Nord Stern Car Numbers - First Deployment with Data Script
# This script exports local data and deploys to Google Cloud Run

set -e

# Configuration
PROJECT_ID="your-google-cloud-project-id"  # Replace with your actual project ID
REGION="us-central1"
SERVICE_NAME="nord-stern-car-numbers"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Nord Stern Car Numbers - First Deployment with Data"
echo "======================================================"

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

# Step 1: Export local database
echo "📊 Step 1: Exporting local database..."
if [ ! -f "export_database.py" ]; then
    echo "❌ export_database.py not found!"
    exit 1
fi

python export_database.py

if [ ! -f "database_export.json" ]; then
    echo "❌ Database export failed!"
    exit 1
fi

echo "✅ Database exported successfully"

# Step 2: Enable required APIs
echo "🔧 Step 2: Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Step 3: Build and deploy using Cloud Build
echo "🏗️ Step 3: Building and deploying with Cloud Build..."
echo "   This will include the database export file in the deployment..."

gcloud builds submit --config cloudbuild.yaml .

# Step 4: Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "✅ First deployment completed successfully!"
echo "🌐 Your application is available at: $SERVICE_URL"
echo ""
echo "📊 Database Status:"
echo "   - Local data exported: 318 registrations"
echo "   - Production database initialized with your data"
echo "   - Application ready for use"
echo ""
echo "📋 Next Steps:"
echo "   1. Visit the application URL to verify your data"
echo "   2. Test the search and management features"
echo "   3. Remove export files for future deployments:"
echo "      rm database_export.json database_export.csv database_import.sql"
echo ""
echo "📊 To view logs:"
echo "   gcloud logs tail --service=$SERVICE_NAME --region=$REGION"
echo ""
echo "🔧 To update the service (after removing export files):"
echo "   ./deploy.sh"
echo ""
echo "🗑️ To delete the service:"
echo "   gcloud run services delete $SERVICE_NAME --region=$REGION" 