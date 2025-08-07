#!/bin/bash

# Nord Stern Car Numbers - Google Cloud Run Deployment Script
# This script deploys the application to Google Cloud Run

set -e

# Configuration
PROJECT_ID="nord-stern-car-numbers"  # Replace with your actual project ID
REGION="us-central1"
SERVICE_NAME="nord-stern-car-numbers"
IMAGE_NAME="us-docker.pkg.dev/$PROJECT_ID/nord-stern-car-numbers/nord-stern-car-numbers"

echo "🚀 Deploying Nord Stern Car Numbers to Google Cloud Run..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"

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

# Build and deploy using Cloud Build
echo "🏗️ Building and deploying with Cloud Build..."
gcloud builds submit --config cloudbuild.yaml .

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Your application is available at: $SERVICE_URL"
echo ""
echo "📊 To view logs:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=20 --format=\"value(timestamp,textPayload)\""
echo ""
echo "🔧 To update the service:"
echo "   ./deploy.sh"
echo ""
echo "🗑️ To delete the service:"
echo "   gcloud run services delete $SERVICE_NAME --region=$REGION" 