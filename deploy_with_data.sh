#!/bin/bash

# Nord Stern Car Numbers - First Deployment with Data Script
# This script exports local data and deploys to Google Cloud Run

set -e

# Configuration
PROJECT_ID="nord-stern-car-numbers"  # Replace with your actual project ID
REGION="us-central1"
SERVICE_NAME="nord-stern-car-numbers"
IMAGE_NAME="us-docker.pkg.dev/$PROJECT_ID/nord-stern-car-numbers/nord-stern-car-numbers"

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

# Get registration count from JSON file
REGISTRATION_COUNT=$(python -c "import json; data=json.load(open('database_export.json')); print(data.get('total_registrations', 0))")
echo "✅ Database exported successfully ($REGISTRATION_COUNT registrations)"

# Step 2: Create deployment directory with export files
echo "📁 Step 2: Preparing deployment files..."
DEPLOY_DIR="deploy_temp_$(date +%s)"
mkdir -p "$DEPLOY_DIR"

# Copy all files except export files
echo "   Copying application files..."
rsync -av --exclude='database_export.*' --exclude='database_import.sql' --exclude='venv/' --exclude='.git/' --exclude='deploy_temp_*/' . "$DEPLOY_DIR/"

# Copy export files to deployment directory
echo "   Copying export files for deployment..."
cp database_export.json database_export.csv database_import.sql "$DEPLOY_DIR/"

# Temporarily rename .gcloudignore to allow export files in build
echo "   Temporarily allowing export files in Cloud Build..."
if [ -f "$DEPLOY_DIR/.gcloudignore" ]; then
    mv "$DEPLOY_DIR/.gcloudignore" "$DEPLOY_DIR/.gcloudignore.backup"
fi

echo "✅ Deployment files prepared in $DEPLOY_DIR"

# Step 3: Enable required APIs
echo "🔧 Step 3: Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable storage.googleapis.com

# Step 4: Create Artifact Registry repository (if it doesn't exist)
echo "🏗️ Step 4: Setting up Artifact Registry..."
gcloud artifacts repositories create nord-stern-car-numbers \
  --repository-format=docker \
  --location=us \
  --description="Nord Stern Car Numbers Docker Repository" \
  --quiet || echo "Repository already exists"

# Step 5: Configure IAM permissions
echo "🔐 Step 5: Configuring IAM permissions..."
COMPUTE_SA=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")-compute@developer.gserviceaccount.com

echo "   Granting permissions to compute service account: $COMPUTE_SA"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$COMPUTE_SA" \
  --role="roles/storage.admin" \
  --quiet || echo "Storage admin role already granted"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$COMPUTE_SA" \
  --role="roles/run.admin" \
  --quiet || echo "Run admin role already granted"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$COMPUTE_SA" \
  --role="roles/iam.serviceAccountUser" \
  --quiet || echo "Service account user role already granted"

# Step 6: Build and deploy using Cloud Build from deployment directory
echo "🏗️ Step 6: Building and deploying with Cloud Build..."
echo "   This will include the database export files in the deployment..."

# Store current directory
ORIGINAL_DIR=$(pwd)

# Change to deployment directory and build
cd "$DEPLOY_DIR"
gcloud builds submit --config cloudbuild.yaml .

# Change back to original directory
cd "$ORIGINAL_DIR"

# Restore .gcloudignore file if it was backed up
if [ -f "$DEPLOY_DIR/.gcloudignore.backup" ]; then
    echo "   Restoring .gcloudignore file..."
    mv "$DEPLOY_DIR/.gcloudignore.backup" "$DEPLOY_DIR/.gcloudignore"
fi

# Step 7: Configure access permissions
echo "🔐 Step 7: Configuring access permissions..."
gcloud run services update $SERVICE_NAME \
  --region=$REGION \
  --no-invoker-iam-check \
  --quiet

# Step 8: Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

# Step 9: Clean up deployment directory
echo "🧹 Step 9: Cleaning up deployment files..."
rm -rf "$DEPLOY_DIR"

echo ""
echo "✅ First deployment completed successfully!"
echo "🌐 Your application is available at: $SERVICE_URL"
echo ""
echo "📊 Database Status:"
echo "   - Local data exported: $REGISTRATION_COUNT registrations"
echo "   - Production database initialized with your data"
echo "   - Application ready for use"
echo ""
echo "📋 Next Steps:"
echo "   1. Visit the application URL to verify your data"
echo "   2. Test the search and management features"
echo "   3. For future deployments, use: ./deploy.sh"
echo ""
echo "📊 To view logs:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=20 --format=\"value(timestamp,textPayload)\""
echo ""
echo "🔧 To update the service (code only, preserves data):"
echo "   ./deploy.sh"
echo ""
echo "🗑️ To delete the service:"
echo "   gcloud run services delete $SERVICE_NAME --region=$REGION" 