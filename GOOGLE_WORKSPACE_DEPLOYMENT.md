# 🚀 Nord Stern Car Numbers - Google Workspace Deployment Guide

This comprehensive guide will help you deploy the Nord Stern Car Numbers application in your Google Workspace environment using Google Cloud Platform.

## 📋 Prerequisites

### Required Accounts & Tools
1. **Google Workspace Account** - Active Google Workspace subscription
2. **Google Cloud Project** - A Google Cloud project with billing enabled
3. **Google Cloud SDK** - gcloud CLI tool installed
4. **Git** - For version control
5. **Docker** - For containerization (optional, Cloud Build handles this)

### Google Cloud APIs Required
- Cloud Build API
- Cloud Run API
- Artifact Registry API (replaces Container Registry)
- Cloud Logging API
- Storage API

## 🎯 Deployment Options

### Option 1: Google Cloud Run (Recommended) ⭐

**Best for:** Production use, cost-effective, automatic scaling, serverless

#### Step 1: Initial Setup

1. **Create Google Cloud Project:**
   ```bash
   # Create new project (if needed)
   gcloud projects create nord-stern-car-numbers --name="Nord Stern Car Numbers"
   
   # Or use existing project
   gcloud config set project YOUR_EXISTING_PROJECT_ID
   ```

2. **Enable Billing:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/billing)
   - Link your project to a billing account

3. **Install Google Cloud SDK:**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

#### Step 2: Authentication & Configuration

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable storage.googleapis.com
```

#### Step 3: Setup Artifact Registry

```bash
# Create Artifact Registry repository (replaces Container Registry)
gcloud artifacts repositories create nord-stern-car-numbers \
  --repository-format=docker \
  --location=us \
  --description="Nord Stern Car Numbers Docker Repository"
```

#### Step 4: Configure IAM Permissions

```bash
# Get your compute service account
COMPUTE_SA=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")-compute@developer.gserviceaccount.com

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$COMPUTE_SA" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$COMPUTE_SA" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:$COMPUTE_SA" \
  --role="roles/iam.serviceAccountUser"
```

#### Step 5: Deploy Application

1. **Update deployment script:**
   ```bash
   # Edit deploy.sh and replace YOUR_PROJECT_ID
   sed -i '' 's/your-google-cloud-project-id/YOUR_ACTUAL_PROJECT_ID/g' deploy.sh
   ```

2. **Make script executable:**
   ```bash
   chmod +x deploy.sh
   ```

3. **Deploy:**
   ```bash
   ./deploy.sh
   ```

4. **Your app will be available at:**
   ```
   https://nord-stern-car-numbers-xxxxx-uc.a.run.app
   ```

#### Step 6: Configure Access (Important!)

After deployment, you may need to configure access permissions:

```bash
# Allow unauthenticated access (if needed)
gcloud run services update nord-stern-car-numbers \
  --region=us-central1 \
  --no-invoker-iam-check

# Or restrict to specific users/domains
gcloud run services add-iam-policy-binding nord-stern-car-numbers \
  --region=us-central1 \
  --member="domain:nordstern.org" \
  --role="roles/run.invoker"
```

### Option 2: Google App Engine

**Best for:** Traditional web app hosting, managed platform

```bash
# Deploy to App Engine
gcloud app deploy app.yaml
```

### Option 3: Google Compute Engine

**Best for:** Full control, custom server setup

1. Create VM instance
2. Install dependencies
3. Upload application
4. Configure nginx
5. Set up SSL

## 🔐 Security Configuration

### Environment Variables

Set secure environment variables in Cloud Run:

```bash
# Set secret key
gcloud run services update nord-stern-car-numbers \
  --region=us-central1 \
  --set-env-vars SECRET_KEY="your-super-secure-secret-key-here"

# Set additional environment variables
gcloud run services update nord-stern-car-numbers \
  --region=us-central1 \
  --set-env-vars FLASK_ENV=production
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

3. **SSL certificate** will be automatically provisioned

## 📊 Monitoring & Logging

### View Application Logs

```bash
# Real-time logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nord-stern-car-numbers" --limit=20 --format="value(timestamp,textPayload)"

# Historical logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nord-stern-car-numbers"

# Export logs
gcloud logging read "resource.type=cloud_run_revision" --limit=1000 --format="table(timestamp,textPayload)" > app-logs.txt
```

### Set up Monitoring Alerts

1. Go to [Google Cloud Console > Monitoring](https://console.cloud.google.com/monitoring)
2. Create alerts for:
   - High error rates (>5%)
   - Response time spikes (>2 seconds)
   - Memory usage (>80%)
   - CPU usage (>70%)

### Performance Monitoring

```bash
# View service metrics
gcloud run services describe nord-stern-car-numbers --region=us-central1

# Monitor resource usage
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"
```

## 🔄 Continuous Deployment

### GitHub Actions Setup

1. **Create GitHub repository secrets:**
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `GCP_SA_KEY`: Service account JSON key

2. **Service Account Setup:**
   ```bash
   # Create service account
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions Service Account"

   # Grant necessary roles
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"

   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.admin"

   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/cloudbuild.builds.builder"

   # Create and download key
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

3. **Add key to GitHub secrets** as `GCP_SA_KEY`

### Manual Deployment Commands

```bash
# Build and deploy manually
gcloud builds submit --config cloudbuild.yaml .

# Update service configuration
gcloud run services update nord-stern-car-numbers \
  --region=us-central1 \
  --memory=1Gi \
  --cpu=2 \
  --max-instances=20

# Rollback to previous version
gcloud run revisions list --service=nord-stern-car-numbers --region=us-central1
gcloud run services update-traffic nord-stern-car-numbers \
  --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```

## 💰 Cost Optimization

### Cloud Run Pricing (Typical Usage)

- **Free tier:** 2 million requests/month
- **Paid tier:** ~$0.40 per million requests
- **Memory:** ~$0.00002400 per GB-second
- **CPU:** ~$0.00002400 per vCPU-second

### Cost Estimation Examples

**Small Organization (50 users/month):**
- Requests: ~5,000/month
- Cost: ~$0.00/month (free tier)

**Medium Organization (500 users/month):**
- Requests: ~50,000/month
- Cost: ~$0.02/month

**Large Organization (5,000 users/month):**
- Requests: ~500,000/month
- Cost: ~$0.20/month

### Cost Optimization Tips

1. **Use appropriate memory/CPU:**
   ```bash
   gcloud run services update nord-stern-car-numbers \
     --region=us-central1 \
     --memory=512Mi \
     --cpu=1
   ```

2. **Set max instances:**
   ```bash
   gcloud run services update nord-stern-car-numbers \
     --region=us-central1 \
     --max-instances=10
   ```

3. **Enable concurrency:**
   ```bash
   gcloud run services update nord-stern-car-numbers \
     --region=us-central1 \
     --concurrency=80
   ```

## 🗄️ Database Considerations

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
     --region=us-central1 \
     --storage-type=SSD \
     --storage-size=10GB
   ```

2. **Create database:**
   ```bash
   gcloud sql databases create car_numbers --instance=nord-stern-db
   ```

3. **Create user:**
   ```bash
   gcloud sql users create car_numbers_user \
     --instance=nord-stern-db \
     --password="secure-password-here"
   ```

4. **Get connection info:**
   ```bash
   gcloud sql instances describe nord-stern-db
   ```

## 🚀 Quick Start Commands

```bash
# 1. Clone repository
git clone <your-repo-url>
cd NordSternCarNumbers

# 2. Setup Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com

# 3. Create Artifact Registry repository
gcloud artifacts repositories create nord-stern-car-numbers \
  --repository-format=docker \
  --location=us \
  --description="Nord Stern Car Numbers Docker Repository"

# 4. Update deployment script
sed -i '' 's/your-google-cloud-project-id/YOUR_ACTUAL_PROJECT_ID/g' deploy.sh

# 5. Deploy
./deploy.sh

# 6. Configure access
gcloud run services update nord-stern-car-numbers \
  --region=us-central1 \
  --no-invoker-iam-check

# 7. Access your application
# URL will be displayed after deployment
```

## 🔧 Troubleshooting

### Common Issues

1. **"Permission denied" errors:**
   ```bash
   # Ensure proper IAM roles for compute service account
   COMPUTE_SA=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")-compute@developer.gserviceaccount.com
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:$COMPUTE_SA" \
     --role="roles/storage.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:$COMPUTE_SA" \
     --role="roles/run.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:$COMPUTE_SA" \
     --role="roles/iam.serviceAccountUser"
   ```

2. **"Repository not found" errors:**
   ```bash
   # Create Artifact Registry repository
   gcloud artifacts repositories create nord-stern-car-numbers \
     --repository-format=docker \
     --location=us \
     --description="Nord Stern Car Numbers Docker Repository"
   ```

3. **Build failures:**
   ```bash
   # Check build logs
   gcloud builds log BUILD_ID
   
   # Test locally
   docker build -t test-image .
   ```

4. **Service not accessible:**
   ```bash
   # Check service status
   gcloud run services describe nord-stern-car-numbers --region=us-central1
   
   # Check logs
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nord-stern-car-numbers" --limit=20 --format="value(timestamp,textPayload)"
   
   # Configure access
   gcloud run services update nord-stern-car-numbers \
     --region=us-central1 \
     --no-invoker-iam-check
   ```

### Performance Issues

1. **Slow response times:**
   - Increase memory allocation
   - Optimize database queries
   - Enable caching

2. **High costs:**
   - Reduce max instances
   - Optimize resource allocation
   - Monitor usage patterns

## 📞 Support & Maintenance

### Regular Maintenance Tasks

1. **Update dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Backup database:**
   ```bash
   # If using Cloud SQL
   gcloud sql export sql nord-stern-db gs://your-bucket/backup.sql \
     --database=car_numbers
   ```

3. **Monitor costs:**
   - Check Google Cloud Console billing
   - Set up budget alerts
   - Review usage reports

### Getting Help

1. **Google Cloud Support:**
   - [Cloud Run Documentation](https://cloud.google.com/run/docs)
   - [Cloud Build Documentation](https://cloud.google.com/build/docs)
   - [Google Cloud Support](https://cloud.google.com/support)

2. **Application Issues:**
   - Check application logs
   - Review error messages
   - Test locally first

## 🔄 Updates and Maintenance

### Application Updates

```bash
# 1. Make your changes
git add .
git commit -m "Update application"
git push

# 2. Automatic deployment (if using GitHub Actions)
# Or manual deployment:
./deploy.sh
```

### Infrastructure Updates

```bash
# Update service configuration
gcloud run services update nord-stern-car-numbers \
  --region=us-central1 \
  --memory=1Gi \
  --cpu=2

# Update environment variables
gcloud run services update nord-stern-car-numbers \
  --region=us-central1 \
  --set-env-vars NEW_VAR=value
```

---

## 🎉 Success!

**Your Nord Stern Car Numbers application is now ready for production use in Google Workspace!**

### Next Steps:
1. ✅ Test all functionality
2. ✅ Set up monitoring alerts
3. ✅ Configure custom domain (optional)
4. ✅ Train users on the system
5. ✅ Set up regular backups
6. ✅ Monitor costs and performance

### Useful Commands:
```bash
# View service URL
gcloud run services describe nord-stern-car-numbers --region=us-central1 --format="value(status.url)"

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nord-stern-car-numbers" --limit=20 --format="value(timestamp,textPayload)"

# Update service
./deploy.sh

# Delete service (if needed)
gcloud run services delete nord-stern-car-numbers --region=us-central1
``` 