#!/usr/bin/env python3
"""
Production Database Initialization Script for Nord Stern Car Numbers
This script initializes the production database with exported data.
"""

import sqlite3
import json
import os
import sys
from datetime import datetime


def init_production_database(db_path, data_file=None):
    """Initialize production database with schema and optionally data"""

    print(f"🚀 Initializing production database: {db_path}")

    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create the database schema
        print("📋 Creating database schema...")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS car_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                car_number TEXT NOT NULL,
                sort_order INTEGER,
                car_make TEXT,
                car_model TEXT,
                car_year INTEGER,
                car_color TEXT,
                reserved_date TEXT,
                reserved_for_year INTEGER,
                status TEXT DEFAULT 'Active',
                notes TEXT,
                last_usage_year INTEGER,
                expiration_date TEXT,
                usage_count INTEGER DEFAULT 0,
                is_active_in_period BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes for better performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_car_number ON car_registrations(car_number)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sort_order ON car_registrations(sort_order)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_name ON car_registrations(first_name, last_name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_status ON car_registrations(status)"
        )

        conn.commit()
        print("✅ Database schema created successfully")

        # Import data if provided
        if data_file and os.path.exists(data_file):
            print(f"📊 IMPORTING DATA: Found data file {data_file}")
            print("   ⚠️  This will CLEAR existing production data and load new data")

            # Clear existing data first (only when importing new data)
            cursor.execute("DELETE FROM car_registrations")
            print("   ✅ Cleared existing production data")

            if data_file.endswith(".json"):
                success = import_from_json(cursor, data_file)
            elif data_file.endswith(".sql"):
                success = import_from_sql(cursor, data_file)
            else:
                print(f"❌ Unsupported file format: {data_file}")
                success = False

            if success:
                conn.commit()
                print("✅ Data imported successfully")
            else:
                print("❌ Data import failed")
                return False
        else:
            print("📊 NO DATA IMPORT: No data file provided")
            print("   ✅ Preserving existing production data (no changes made)")

        # Show database summary
        cursor.execute("SELECT COUNT(*) FROM car_registrations")
        count = cursor.fetchone()[0]
        print(f"\n📋 Database Summary:")
        print(f"   Total registrations: {count}")
        print(f"   Database file: {db_path}")
        print(f"   Initialized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return True

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def import_from_json(cursor, json_file):
    """Import data from JSON file"""
    try:
        with open(json_file, "r") as f:
            data = json.load(f)

        registrations = data.get("registrations", [])

        for reg in registrations:
            cursor.execute(
                """
                INSERT INTO car_registrations 
                (id, first_name, last_name, car_number, sort_order, car_make, car_model, 
                 car_year, car_color, reserved_date, reserved_for_year, status, notes, 
                 last_usage_year, expiration_date, usage_count, is_active_in_period, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    reg["id"],
                    reg["first_name"],
                    reg["last_name"],
                    reg["car_number"],
                    reg["sort_order"],
                    reg["car_make"],
                    reg["car_model"],
                    reg["car_year"],
                    reg["car_color"],
                    reg["reserved_date"],
                    reg["reserved_for_year"],
                    reg["status"],
                    reg["notes"],
                    reg["last_usage_year"],
                    reg["expiration_date"],
                    reg["usage_count"],
                    reg["is_active_in_period"],
                    reg["created_at"],
                    reg["updated_at"],
                ),
            )

        print(f"   Imported {len(registrations)} registrations from JSON")
        return True

    except Exception as e:
        print(f"❌ Error importing from JSON: {e}")
        return False


def import_from_sql(cursor, sql_file):
    """Import data from SQL file"""
    try:
        with open(sql_file, "r") as f:
            sql_content = f.read()

        # Split into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

        imported_count = 0
        for statement in statements:
            if statement.startswith("INSERT INTO"):
                cursor.execute(statement)
                imported_count += 1

        print(f"   Imported {imported_count} registrations from SQL")
        return True

    except Exception as e:
        print(f"❌ Error importing from SQL: {e}")
        return False


def main():
    """Main function"""
    print("🚀 Nord Stern Car Numbers - Production Database Initialization")
    print("=" * 60)

    # Get database path from environment or use default
    db_path = os.environ.get("DATABASE_PATH", "car_numbers.db")

    # Check for data file argument
    data_file = None
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        if not os.path.exists(data_file):
            print(f"❌ Data file not found: {data_file}")
            sys.exit(1)

    # Initialize database
    success = init_production_database(db_path, data_file)

    if success:
        print("\n✅ Production database initialized successfully!")
        print(f"📁 Database location: {db_path}")
        if data_file:
            print(f"📊 Data imported from: {data_file}")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
