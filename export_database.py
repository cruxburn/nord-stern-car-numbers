#!/usr/bin/env python3
"""
Database Export Script for Nord Stern Car Numbers
This script exports the current database data to a format suitable for production deployment.
"""

import sqlite3
import json
import csv
import os
from datetime import datetime


def export_database_to_json():
    """Export database to JSON format"""
    db_path = "car_numbers.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("📊 Exporting database to JSON...")

        # Get all registrations
        cursor.execute(
            """
            SELECT id, first_name, last_name, car_number, sort_order, car_make, car_model, 
                   car_year, car_color, reserved_date, reserved_for_year, status, notes, 
                   last_usage_year, expiration_date, usage_count, is_active_in_period, 
                   created_at, updated_at
            FROM car_registrations
            ORDER BY sort_order, car_number
        """
        )

        registrations = cursor.fetchall()

        # Convert to list of dictionaries
        data = []
        for reg in registrations:
            registration = {
                "id": reg[0],
                "first_name": reg[1],
                "last_name": reg[2],
                "car_number": reg[3],
                "sort_order": reg[4],
                "car_make": reg[5],
                "car_model": reg[6],
                "car_year": reg[7],
                "car_color": reg[8],
                "reserved_date": reg[9],
                "reserved_for_year": reg[10],
                "status": reg[11],
                "notes": reg[12],
                "last_usage_year": reg[13],
                "expiration_date": reg[14],
                "usage_count": reg[15],
                "is_active_in_period": reg[16],
                "created_at": reg[17],
                "updated_at": reg[18],
            }
            data.append(registration)

        # Create export data
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_registrations": len(data),
            "registrations": data,
        }

        # Write to JSON file
        output_file = "database_export.json"
        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2)

        print(f"✅ Successfully exported {len(data)} registrations to {output_file}")

        # Show summary
        print(f"\n📋 Export Summary:")
        print(f"   Total registrations: {len(data)}")
        print(f"   Export file: {output_file}")
        print(f"   Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return True

    except Exception as e:
        print(f"❌ Error during export: {e}")
        return False
    finally:
        conn.close()


def export_database_to_csv():
    """Export database to CSV format (alternative format)"""
    db_path = "car_numbers.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("📊 Exporting database to CSV...")

        # Get all registrations
        cursor.execute(
            """
            SELECT id, first_name, last_name, car_number, sort_order, car_make, car_model, 
                   car_year, car_color, reserved_date, reserved_for_year, status, notes, 
                   last_usage_year, expiration_date, usage_count, is_active_in_period, 
                   created_at, updated_at
            FROM car_registrations
            ORDER BY sort_order, car_number
        """
        )

        registrations = cursor.fetchall()

        # Write to CSV file
        output_file = "database_export.csv"
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(
                [
                    "id",
                    "first_name",
                    "last_name",
                    "car_number",
                    "sort_order",
                    "car_make",
                    "car_model",
                    "car_year",
                    "car_color",
                    "reserved_date",
                    "reserved_for_year",
                    "status",
                    "notes",
                    "last_usage_year",
                    "expiration_date",
                    "usage_count",
                    "is_active_in_period",
                    "created_at",
                    "updated_at",
                ]
            )

            # Write data
            for reg in registrations:
                writer.writerow(reg)

        print(
            f"✅ Successfully exported {len(registrations)} registrations to {output_file}"
        )
        return True

    except Exception as e:
        print(f"❌ Error during export: {e}")
        return False
    finally:
        conn.close()


def create_sql_import_script():
    """Create SQL script for importing data"""
    db_path = "car_numbers.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("📊 Creating SQL import script...")

        # Get all registrations
        cursor.execute(
            """
            SELECT id, first_name, last_name, car_number, sort_order, car_make, car_model, 
                   car_year, car_color, reserved_date, reserved_for_year, status, notes, 
                   last_usage_year, expiration_date, usage_count, is_active_in_period, 
                   created_at, updated_at
            FROM car_registrations
            ORDER BY sort_order, car_number
        """
        )

        registrations = cursor.fetchall()

        # Create SQL script
        output_file = "database_import.sql"
        with open(output_file, "w") as f:
            f.write("-- Nord Stern Car Numbers Database Import Script\n")
            f.write(
                f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"-- Total registrations: {len(registrations)}\n\n")

            f.write("-- Clear existing data (optional)\n")
            f.write("-- DELETE FROM car_registrations;\n\n")

            f.write("-- Insert registrations\n")
            for reg in registrations:
                # Handle NULL values properly
                values = []
                for val in reg:
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, str):
                        values.append(f"'{val.replace("'", "''")}'")
                    elif isinstance(val, bool):
                        values.append("1" if val else "0")
                    else:
                        values.append(str(val))

                f.write(
                    f"INSERT INTO car_registrations VALUES ({', '.join(values)});\n"
                )

        print(f"✅ Successfully created SQL import script: {output_file}")
        return True

    except Exception as e:
        print(f"❌ Error creating SQL script: {e}")
        return False
    finally:
        conn.close()


def main():
    """Main export function"""
    print("🚀 Nord Stern Car Numbers - Database Export Tool")
    print("=" * 50)

    # Export to JSON
    json_success = export_database_to_json()

    # Export to CSV
    csv_success = export_database_to_csv()

    # Create SQL script
    sql_success = create_sql_import_script()

    print("\n" + "=" * 50)
    if json_success and csv_success and sql_success:
        print("✅ All exports completed successfully!")
        print("\n📁 Generated files:")
        print("   - database_export.json (JSON format)")
        print("   - database_export.csv (CSV format)")
        print("   - database_import.sql (SQL script)")
        print("\n💡 For production deployment:")
        print("   1. Use database_import.sql to populate the production database")
        print("   2. Or use the JSON/CSV files with your preferred import method")
    else:
        print("❌ Some exports failed. Check the errors above.")


if __name__ == "__main__":
    main()
