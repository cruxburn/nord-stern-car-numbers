# 🚀 Nord Stern Car Numbers - Google Workspace Deployment Guide

This guide will help you deploy the Nord Stern Car Numbers application in your Google Workspace environment.

## 📋 Prerequisites

1. **Google Cloud Project** - You need a Google Cloud project
2. **Google Cloud SDK** - Install the gcloud CLI tool
3. **Docker** - For building container images
4. **Git** - For version control

## 🎯 Deployment Options

### Option 1: Google Cloud Run (Recommended)

**Best for:** Production use, cost-effective, automatic scaling

#### Step 1: Setup Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your **Project ID** (you'll need this)

#### Step 2: Install Google Cloud SDK

```bash
# macOS (using Homebrew)
brew install google-cloud-sdk

# Or download from Google's website
# https://cloud.google.com/sdk/docs/install
```

#### Step 3: Authenticate and Configure

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

#### Step 4: Deploy the Application

1. **Update the deployment script:**
   ```bash
   # Edit deploy.sh and replace YOUR_PROJECT_ID with your actual project ID
   nano deploy.sh
   ```

2. **Run the deployment:**
   ```bash
   # First deployment with data
   ./deploy_with_data.sh
   
   # Subsequent deployments
   ./deploy.sh
   ```

3. **Your app will be available at:**
   ```
   https://nord-stern-car-numbers-xxxxx-uc.a.run.app
   ```

### Deployment Scripts

**`deploy_with_data.sh`** - First deployment with local data:
- Exports local database to JSON/CSV/SQL formats
- Creates temporary deployment directory with export files
- Deploys to Cloud Run with data pre-loaded
- Automatically cleans up temporary files
- Perfect for initial production deployment

**`deploy.sh`** - Subsequent deployments:
- Standard deployment without data export
- Updates application code only
- Preserves existing production data
- Safe for regular updates

**`setup-deployment.sh`** - Initial GCP setup:
- Creates required GCP resources
- Sets up IAM permissions
- Configures Artifact Registry
- One-time setup script

### Option 2: Google App Engine

**Best for:** Traditional web app hosting, managed platform

#### Step 1: Create app.yaml

```yaml
runtime: python311
entrypoint: python app.py

env_variables:
  SECRET_KEY: "your-secure-secret-key-here"

automatic_scaling:
  target_cpu_utilization: 0.6
  min_instances: 1
  max_instances: 10

resources:
  cpu: 1
  memory_gb: 0.5
  disk_size_gb: 10
```

#### Step 2: Deploy to App Engine

```bash
gcloud app deploy
```

### Option 3: Google Compute Engine

**Best for:** Full control, custom server setup

1. Create a VM instance
2. Install Python, Flask, and dependencies
3. Upload your application files
4. Configure nginx as reverse proxy
5. Set up SSL certificates

## 🔐 Security Configuration

### Environment Variables

Set these in Google Cloud Run:

```bash
# Set secret key
gcloud run services update nord-stern-car-numbers \
  --region=us-central1 \
  --set-env-vars SECRET_KEY="your-super-secure-secret-key-here"
```

### Custom Domain Setup

1. **Map custom domain:**
   ```bash
   gcloud run domain-mappings create \
     --service=nord-stern-car-numbers \
     --domain=car-numbers.yourdomain.com \
     --region=us-central1
   ```

2. **Update DNS records** in Google Domains or your DNS provider

## 📊 Monitoring and Logging

### View Logs

```bash
# Real-time logs
gcloud logs tail --service=nord-stern-car-numbers --region=us-central1

# Historical logs
gcloud logging read "resource.type=cloud_run_revision"
```

### Set up Monitoring

1. Go to Google Cloud Console > Monitoring
2. Create alerts for:
   - High error rates
   - Response time spikes
   - Resource usage

## 🔄 Continuous Deployment

### GitHub Actions Integration

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Google Cloud SDK
      uses: google-github-actions/setup-gcloud@v0
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    
    - name: Deploy to Cloud Run
      run: |
        gcloud builds submit --config cloudbuild.yaml .
```

## 💰 Cost Optimization

### Cloud Run Pricing (Typical Usage)

- **Free tier:** 2 million requests/month
- **Paid tier:** ~$0.40 per million requests
- **Memory:** ~$0.00002400 per GB-second
- **CPU:** ~$0.00002400 per vCPU-second

### Cost Estimation for 100 users/month:
- **Requests:** ~10,000/month
- **Cost:** ~$0.01/month (mostly free tier)

## 🔧 Database Considerations

### Current Setup (SQLite)
- ✅ Simple, no additional setup
- ❌ Data lost when container restarts
- ❌ No concurrent access

### Recommended: Cloud SQL (PostgreSQL)

1. **Create Cloud SQL instance:**
   ```bash
   gcloud sql instances create nord-stern-db \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

2. **Create database:**
   ```bash
   gcloud sql databases create car_numbers --instance=nord-stern-db
   ```

3. **Update application** to use PostgreSQL instead of SQLite

## 🚀 Quick Start Commands

```bash
# 1. Clone and setup
git clone <your-repo>
cd NordSternCarNumbers

# 2. Update project ID
sed -i '' 's/your-google-cloud-project-id/YOUR_ACTUAL_PROJECT_ID/g' deploy.sh

# 3. Deploy
./deploy.sh

# 4. Access your app
# The URL will be displayed after deployment
```

## 📞 Support

For deployment issues:
1. Check Google Cloud Console logs
2. Verify API permissions
3. Ensure billing is enabled
4. Contact Google Cloud support if needed

## 🔄 Updates and Maintenance

### Update Application

```bash
# Make your changes
git add .
git commit -m "Update application"
git push

# Redeploy
./deploy.sh
```

### Backup Database

```bash
# Export data (if using Cloud SQL)
gcloud sql export sql nord-stern-db gs://your-bucket/backup.sql \
  --database=car_numbers
```

---

**🎉 Your Nord Stern Car Numbers application is now ready for production use in Google Workspace!** 