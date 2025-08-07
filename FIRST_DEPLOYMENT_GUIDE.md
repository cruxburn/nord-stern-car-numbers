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

### Step 2: Prepare for Deployment

**No manual configuration required!** The deployment script automatically handles file inclusion/exclusion.

The `deploy_with_data.sh` script will:
- Create a temporary deployment directory
- Copy all application files (excluding export files)
- Copy export files to the deployment directory
- Deploy from the temporary directory
- Clean up automatically

### Step 3: Deploy with Data

Use the automated deployment script:

```bash
# Run the first deployment with data script
./deploy_with_data.sh
```

This script will:
1. Export your local database (if not already done)
2. Enable required Google Cloud APIs
3. Build and deploy using Cloud Build
4. Initialize the production database with your data

### Step 4: Verify the Deployment

1. **Check the deployment logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nord-stern-car-numbers" --limit=20 --format="value(timestamp,textPayload)" | grep -E "(database|export|import|Initializing|registrations)"
   ```

2. **Look for these success messages:**
   - "📊 Initializing database with exported data..."
   - "📊 Importing data from /app/database_export.json..."
   - "Imported 318 registrations from JSON"
   - "Total registrations: 318"
   - "✅ Production database initialized successfully!"

3. **Access your application:**
   - The URL will be shown in the deployment output
   - Navigate to the search page and verify your data is there

### Step 5: Clean Up

After confirming the deployment is successful:

```bash
# Remove export files (optional - they're automatically excluded from git)
rm database_export.json database_export.csv database_import.sql
```

**Note:** The deployment script automatically handles file inclusion/exclusion. No manual editing of `.gitignore` or `.gcloudignore` is required.

## 🔄 Subsequent Deployments

After the first deployment, you can deploy normally with data preservation:

```bash
# Deploy with data preservation (recommended)
./deploy.sh
```

**Data Preservation:** The `deploy.sh` script now includes automatic data preservation:
- Exports current production data before deployment
- Includes backup in the new container
- Automatically restores data on container startup
- Ensures zero data loss during code updates

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
   - **Check deployment logs**: Look for "🚨 DATA IMPORT MODE" vs "✅ CODE-ONLY MODE"
   - **Verify export files**: Ensure `database_export.json` exists before running `deploy_with_data.sh`
   - **Check build context size**: Should be ~1.2MB (not ~395kB) when files are included
   - **Check deployment logs**: Look for "📊 IMPORTING DATA" vs "📊 NO DATA IMPORT"

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
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nord-stern-car-numbers" --limit=20 --format="value(timestamp,textPayload)"

# Check database export
python export_database.py

# Test database initialization locally
python init_production_db.py database_export.json

# Verify files are included in build
gcloud meta list-files-for-upload | grep database
```

## 📝 Important Notes

1. **One-time process** - This is only needed for the first deployment
2. **Data independence** - After deployment, local and production databases are separate
3. **No automatic sync** - Changes in production won't affect your local database
4. **Backup regularly** - Consider implementing a backup strategy for production data
5. **Gitignore management** - Remember to temporarily allow export files for first deployment

## 🎉 Success!

Once deployed, your Nord Stern Car Numbers application will be available online with all your current data. The production database will be independent of your local development environment.

For ongoing maintenance, refer to the main `GOOGLE_WORKSPACE_DEPLOYMENT.md` guide. 