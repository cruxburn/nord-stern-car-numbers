# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Create startup script
RUN echo '#!/bin/bash\n\
if [ -f "/app/database_export.json" ]; then\n\
    echo "🚨 DATA IMPORT MODE: Found database_export.json"\n\
    echo "   This will CLEAR production data and load local data"\n\
    python /app/init_production_db.py /app/database_export.json\n\
elif [ -f "/app/database_import.sql" ]; then\n\
    echo "🚨 DATA IMPORT MODE: Found database_import.sql"\n\
    echo "   This will CLEAR production data and load local data"\n\
    python /app/init_production_db.py /app/database_import.sql\n\
elif [ -f "/app/production_data_backup.json" ]; then\n\
    echo "🔄 DATA RESTORE MODE: Found production_data_backup.json"\n\
    echo "   Restoring production data from backup"\n\
    python /app/init_production_db.py /app/production_data_backup.json\n\
    echo "   Cleaning up backup file"\n\
    rm -f /app/production_data_backup.json\n\
else\n\
    echo "✅ CODE-ONLY MODE: No data files found"\n\
    echo "   Preserving existing production data"\n\
    python /app/init_production_db.py\n\
fi\n\
\n\
echo "🚀 Starting application..."\n\
exec python app.py' > /app/start.sh && chmod +x /app/start.sh

USER appuser

# Expose port
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1

# Run the application
CMD ["/app/start.sh"] 