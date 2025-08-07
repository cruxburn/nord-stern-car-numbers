# First Deployment Guide - Nord Stern Car Numbers

This guide walks you through the first deployment of the Nord Stern Car Numbers application with your current local data.

## 🎯 Overview

For the first deployment, you'll want to populate the production database with the same data you're using locally. After the initial deployment, the production database will be independent of your local database.

## 📋 Prerequisites

1. **Local database is ready** - Your local `car_numbers.db` should contain all the data you want in production
2. **Google Cloud Project set up** - Follow the setup in `GOOGLE_WORKSPACE_DEPLOYMENT.md`
3. **Docker installed** (if using local Docker builds)

## 🚀 Step-by-Step Deployment Process

### Step 1: Export Your Local Database

First, export your current local database data:

```bash
# Make sure you're in the project directory
cd /path/to/NordSternCarNumbers

# Activate virtual environment
source venv/bin/activate

# Export the database
python export_database.py
```

This will create three files:
- `database_export.json` - JSON format (recommended)
- `database_export.csv` - CSV format
- `database_import.sql` - SQL script format

### Step 2: Choose Your Deployment Method

#### Option A: Google Cloud Build (Recommended)

1. **Copy the export file to your project directory:**
   ```bash
   # Copy the JSON export (recommended)
   cp database_export.json ./
   ```

2. **Deploy using Cloud Build:**
   ```bash
   # Update the PROJECT_ID in deploy.sh first
   ./deploy.sh
   ```

#### Option B: Local Docker Build

1. **Copy the export file:**
   ```bash
   cp database_export.json ./
   ```

2. **Build and deploy:**
   ```bash
   # Build the Docker image
   docker build -t nord-stern-car-numbers .
   
   # Deploy to Cloud Run
   gcloud run deploy nord-stern-car-numbers \
     --image nord-stern-car-numbers \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Step 3: Verify the Deployment

1. **Check the deployment logs:**
   ```bash
   gcloud logs tail --service=nord-stern-car-numbers --region=us-central1
   ```

2. **Access your application:**
   - The URL will be shown in the deployment output
   - Navigate to the search page and verify your data is there

## 🔄 Subsequent Deployments

After the first deployment, you can remove the export files and deploy normally:

```bash
# Remove export files (they're no longer needed)
rm database_export.json database_export.csv database_import.sql

# Deploy normally
./deploy.sh
```

## 📊 Database Management

### Production Database Location

The production database will be stored in the Cloud Run container's filesystem. This means:
- ✅ **Data persists** between container restarts
- ⚠️ **Data is lost** if the container is completely replaced
- ⚠️ **No automatic backups** (consider using Cloud SQL for production)

### Backup Strategy (Recommended for Production)

For a production environment, consider:

1. **Cloud SQL** - Use a managed PostgreSQL/MySQL database
2. **Regular backups** - Export data periodically
3. **Database migrations** - Use proper migration scripts

## 🛠️ Troubleshooting

### Common Issues

1. **Database not populated:**
   - Check that the export file is in the project root
   - Verify the file name matches exactly
   - Check deployment logs for errors

2. **Application won't start:**
   - Check the startup logs
   - Verify database permissions
   - Ensure all required files are present

3. **Data missing:**
   - Verify the export was successful
   - Check that the export file contains data
   - Review the initialization logs

### Debug Commands

```bash
# Check deployment status
gcloud run services describe nord-stern-car-numbers --region=us-central1

# View recent logs
gcloud logs tail --service=nord-stern-car-numbers --region=us-central1

# Check database export
python export_database.py

# Test database initialization locally
python init_production_db.py database_export.json
```

## 📝 Important Notes

1. **One-time process** - This is only needed for the first deployment
2. **Data independence** - After deployment, local and production databases are separate
3. **No automatic sync** - Changes in production won't affect your local database
4. **Backup regularly** - Consider implementing a backup strategy for production data

## 🎉 Success!

Once deployed, your Nord Stern Car Numbers application will be available online with all your current data. The production database will be independent of your local development environment.

For ongoing maintenance, refer to the main `GOOGLE_WORKSPACE_DEPLOYMENT.md` guide. 