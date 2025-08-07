# NordStern Car Numbers - Drivers Education Management System

A lightweight web application for managing car number registrations for car club Drivers Education sessions. This system replaces the traditional Excel spreadsheet with a modern, searchable web interface.

## Features

- **Search & Browse**: Search registrations by driver name or car number
- **Usage Tracking**: Record and track car usage by year
- **Expiration Management**: Automatic calculation of expiration dates based on 3-year rolling periods
- **Complete Car Details**: Store make, model, year, and color information
- **Status Tracking**: Mark registrations as Active, Retired, or Pending
- **Statistics Dashboard**: View registration statistics and trends
- **Mobile-Friendly**: Responsive design works on all devices
- **Data Validation**: Validates input and handles duplicate car numbers
- **Proper Sorting**: Numeric sorting of car numbers (1, 2, 14, 99, etc.)
- **Performance Optimized**: Database indexes for fast queries

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (lightweight, file-based)
- **Frontend**: Bootstrap 5 + Font Awesome icons
- **JavaScript**: Vanilla JS for interactivity

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone or download the project files**

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

## Usage

### Home Page
- Overview of the system
- Quick access to all features
- Quick search functionality

### Search Page
- Search by driver name (partial matches supported)
- Search by exact car number
- View all registrations
- Edit or delete existing registrations

### Add Registration
- Enter driver information (first name, last name)
- Choose car number (with availability checking)
- Add car details (make, model, year, color)
- Set reservation date and notes
- Real-time validation prevents duplicates

### Edit Registration
- Modify any registration details
- Change car number (with conflict checking)
- Update status (Active/Retired/Pending)
- View creation and modification timestamps

### Statistics Page
- Total, active, and retired registration counts
- Most common car makes
- Registration status distribution
- System information and tips

## Database Schema

The application uses a SQLite database (`car_numbers.db`) with the following structure:

```sql
CREATE TABLE car_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    car_number TEXT NOT NULL,
    sort_order INTEGER,
    car_make TEXT,
    car_model TEXT,
    car_year INTEGER,
    car_color TEXT,
    reserved_date DATE,
    reserved_for_year INTEGER DEFAULT 2025,
    status TEXT DEFAULT 'Active',
    notes TEXT,
    last_usage_year INTEGER,
    expiration_date DATE,
    usage_count INTEGER DEFAULT 0,
    is_active_in_period BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Database indexes for improved performance
CREATE INDEX idx_car_number ON car_registrations(car_number);
CREATE INDEX idx_sort_order ON car_registrations(sort_order);
CREATE INDEX idx_name ON car_registrations(first_name, last_name);
CREATE INDEX idx_status ON car_registrations(status);
```

### Key Features:
- **Car numbers are TEXT** (preserves original format like "001", "14")
- **No UNIQUE constraint** on car_number (allows duplicates)
- **sort_order field** for proper numeric sorting
- **Usage tracking** with last_usage_year, usage_count, and expiration_date
- **Rolling period management** with is_active_in_period
- **Performance indexes** for fast queries

## API Endpoints

- `GET /` - Home page
- `GET /search` - Search registrations
- `GET /add` - Add registration form
- `POST /add` - Create new registration
- `GET /edit/<id>` - Edit registration form
- `POST /edit/<id>` - Update registration
- `POST /delete/<id>` - Delete registration
- `POST /api/record_usage/<id>` - Record usage for a registration
- `POST /api/remove_usage/<id>` - Remove usage for a registration
- `GET /api/check_number/<number>` - Check number availability (JSON)
- `GET /stats` - Statistics page

## Configuration

### Production Deployment

The application supports multiple deployment options:

#### **Option 1: Google Cloud Platform (Recommended)**
- **Cloud Run**: Containerized deployment with automatic scaling
- **Cloud Build**: Automated CI/CD pipeline
- **Artifact Registry**: Container image storage
- **Cloud Logging**: Centralized logging and monitoring

**Quick Start:**
```bash
# First deployment with data
./deploy_with_data.sh

# Subsequent deployments
./deploy.sh
```

**Documentation:**
- `DEPLOYMENT.md` - Complete deployment guide
- `GOOGLE_WORKSPACE_DEPLOYMENT.md` - GCP-specific instructions
- `FIRST_DEPLOYMENT_GUIDE.md` - First-time deployment steps

#### **Option 2: Docker Deployment**
```bash
# Build and run locally
docker build -t nord-stern-car-numbers .
docker run -p 5000:5000 nord-stern-car-numbers

# Or use Docker Compose (if needed)
docker-compose up -d
```

#### **Option 3: Traditional Server**
1. **Change the secret key** in `app.py`:
   ```python
   app.secret_key = 'your-secure-secret-key-here'
   ```

2. **Use a production WSGI server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up a reverse proxy** (nginx/Apache) for SSL termination

4. **Regular database backups**:
   ```bash
   cp car_numbers.db car_numbers_backup_$(date +%Y%m%d).db
   ```

#### **CI/CD Pipeline**
- **GitHub Actions**: Automated testing and deployment
- **Test Workflow**: Runs on every PR and push
- **Deploy Workflow**: Manual deployment to production
- **Code Quality**: Black formatting and Flake8 linting

## Data Migration from Excel

To import data from your existing Excel spreadsheet:

1. **Export Excel data** to CSV format
2. **Use the import script** (create if needed):
   ```python
   import csv
   import sqlite3
   
   conn = sqlite3.connect('car_numbers.db')
   cursor = conn.cursor()
   
   with open('your_data.csv', 'r') as file:
       reader = csv.DictReader(file)
       for row in reader:
           # Calculate sort_order from car_number
           try:
               sort_order = int(row['car_number'])
           except ValueError:
               sort_order = 0
               
           cursor.execute('''
               INSERT INTO car_registrations 
               (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ''', (row['first_name'], row['last_name'], row['car_number'], sort_order,
                 row['car_make'], row['car_model'], row['car_year'], row['car_color']))
   
   conn.commit()
   conn.close()
   ```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py`:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Database locked**: Ensure no other process is accessing the database file

3. **Permission errors**: Check file permissions for the database directory

### Logs

The application runs in debug mode by default. Check the console output for error messages and debugging information.

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions, please contact the development team or create an issue in the project repository.

---

**NordStern Car Club** - Drivers Education Car Number Management System
