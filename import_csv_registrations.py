#!/usr/bin/env python3
"""
CSV Import Script for Nord Stern Car Numbers
Handles initial registration import with 3-year rolling period system
"""

import csv
import sqlite3
import os
from datetime import datetime, timedelta
import sys

# Add the current directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import calculate_expiration_date, init_db


def import_csv_registrations(csv_file_path):
    """
    Import registrations from CSV file with rolling period support

    Args:
        csv_file_path (str): Path to the CSV file
    """

    # Initialize database
    init_db()

    # Connect to database
    conn = sqlite3.connect("car_numbers.db")
    cursor = conn.cursor()

    # Statistics tracking
    stats = {
        "total_rows": 0,
        "imported": 0,
        "skipped_no_name": 0,
        "skipped_duplicate": 0,
        "errors": 0,
    }

    print("🚀 Starting CSV import for Nord Stern Car Numbers")
    print("=" * 60)

    try:
        with open(csv_file_path, "r", encoding="utf-8") as csvfile:
            # Try to detect the delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)

            # Check if it's comma or tab separated
            if "\t" in sample:
                delimiter = "\t"
                print("📋 Detected tab-separated CSV format")
            else:
                delimiter = ","
                print("📋 Detected comma-separated CSV format")

            reader = csv.DictReader(csvfile, delimiter=delimiter)

            # Print column headers for verification
            print(f"📊 CSV Columns: {', '.join(reader.fieldnames)}")
            print()

            for row_num, row in enumerate(
                reader, start=2
            ):  # Start at 2 since row 1 is header
                stats["total_rows"] += 1

                try:
                    # Extract data from CSV row
                    first_name = row.get("First Name", "").strip()
                    last_name = row.get("Last Name", "").strip()
                    car_number = row.get("Car Number", "").strip()
                    car_make = row.get(
                        " Make", ""
                    ).strip()  # Note: there's a leading space in the column name
                    car_model = row.get("Model", "").strip()
                    car_year = row.get("Car Year", "").strip()
                    car_color = row.get("Color", "").strip()
                    reserved_date = row.get("Reserved Date", "").strip()
                    notes = ""  # No notes column in this CSV
                    last_used = row.get("Last Used", "").strip()

                    # Skip rows without first or last name
                    if not first_name or not last_name:
                        print(
                            f"⚠️  Row {row_num}: Skipping - missing first or last name"
                        )
                        stats["skipped_no_name"] += 1
                        continue

                    # Validate car number
                    if not car_number:
                        print(f"⚠️  Row {row_num}: Skipping - missing car number")
                        stats["skipped_no_name"] += 1
                        continue

                    # Validate car number (preserve exact format from CSV)
                    try:
                        # Keep the exact format from CSV, just validate it's a valid number
                        int(
                            car_number
                        )  # This validates it's a number but doesn't change the format
                        car_number = car_number.strip()  # Just remove any whitespace
                    except ValueError:
                        print(
                            f"⚠️  Row {row_num}: Skipping - invalid car number: {car_number}"
                        )
                        stats["errors"] += 1
                        continue

                    # Note: Allowing duplicates - user will manually manage them in the app
                    # Check if car number already exists (for informational purposes only)
                    cursor.execute(
                        "SELECT id FROM car_registrations WHERE car_number = ?",
                        (car_number,),
                    )
                    existing = cursor.fetchone()
                    if existing:
                        print(
                            f"⚠️  Row {row_num}: Duplicate car number {car_number} - importing anyway"
                        )
                        # Don't increment skipped_duplicate since we're allowing them

                    # Process reserved date and handle "Retired" status
                    status = "Active"  # Default status
                    if reserved_date:
                        if reserved_date.lower() == "retired":
                            status = "Retired"
                            reserved_date = None
                        else:
                            try:
                                # Try different date formats
                                date_formats = [
                                    "%m/%d/%y",
                                    "%m/%d/%Y",
                                    "%Y-%m-%d",
                                    "%m-%d-%Y",
                                    "%Y/%m/%d",
                                ]
                                parsed_date = None

                                for fmt in date_formats:
                                    try:
                                        parsed_date = datetime.strptime(
                                            reserved_date, fmt
                                        )
                                        break
                                    except ValueError:
                                        continue

                                if parsed_date:
                                    reserved_date = parsed_date.strftime("%Y-%m-%d")
                                else:
                                    print(
                                        f"⚠️  Row {row_num}: Invalid reserved date format: {reserved_date}"
                                    )
                                    reserved_date = None
                            except Exception as e:
                                print(
                                    f"⚠️  Row {row_num}: Error parsing reserved date: {e}"
                                )
                                reserved_date = None
                    else:
                        # If no reserved date, use default date 03/28/1959
                        reserved_date = "1959-03-28"
                        print(
                            f"📅 Row {row_num}: No reserved date found, using default: 03/28/1959"
                        )

                    # Process car year
                    car_year_int = None
                    if car_year:
                        try:
                            car_year_int = int(car_year)
                        except ValueError:
                            print(f"⚠️  Row {row_num}: Invalid car year: {car_year}")

                    # Calculate initial expiration date
                    expiration_date = None
                    is_active_in_period = True
                    last_usage_date = None
                    usage_count = 0

                    if reserved_date:
                        expiration_date, is_active_in_period = (
                            calculate_expiration_date(reserved_date)
                        )

                    # Process "Last Used" column for 2025 usage
                    last_usage_year = None
                    usage_count = 0

                    if last_used and last_used.lower() in ["x", "yes", "true", "1"]:
                        # Set usage year to 2025
                        last_usage_year = 2025
                        usage_count = 1

                        # Recalculate expiration date based on usage
                        if reserved_date:
                            expiration_date, is_active_in_period = (
                                calculate_expiration_date(
                                    reserved_date, last_usage_year
                                )
                            )

                        print(
                            f"✅ Row {row_num}: {first_name} {last_name} (#{car_number}) - 2025 usage recorded"
                        )
                    else:
                        print(
                            f"✅ Row {row_num}: {first_name} {last_name} (#{car_number}) - no 2025 usage"
                        )

                    # Calculate sort_order from car_number
                    try:
                        sort_order = int(car_number)
                    except ValueError:
                        sort_order = 0

                    # Insert the registration
                    cursor.execute(
                        """
                        INSERT INTO car_registrations 
                        (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, 
                         car_color, reserved_date, notes, status, last_usage_year, expiration_date, 
                         usage_count, is_active_in_period)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            first_name,
                            last_name,
                            car_number,
                            sort_order,
                            car_make,
                            car_model,
                            car_year_int,
                            car_color,
                            reserved_date,
                            notes,
                            status,
                            last_usage_year,
                            expiration_date,
                            usage_count,
                            is_active_in_period,
                        ),
                    )

                    stats["imported"] += 1

                except Exception as e:
                    print(f"❌ Row {row_num}: Error processing row - {str(e)}")
                    stats["errors"] += 1
                    continue

        # Commit all changes
        conn.commit()

        # Print final statistics
        print("\n" + "=" * 60)
        print("📊 Import Statistics")
        print("=" * 60)
        print(f"Total rows processed: {stats['total_rows']}")
        print(f"Successfully imported: {stats['imported']}")
        print(f"Skipped (no name): {stats['skipped_no_name']}")
        print(f"Skipped (duplicate): {stats['skipped_duplicate']}")
        print(f"Errors: {stats['errors']}")

        # Show some sample imported data
        print("\n📋 Sample Imported Registrations:")
        print("-" * 60)
        cursor.execute(
            """
            SELECT first_name, last_name, car_number, reserved_date, expiration_date, 
                   last_usage_year, usage_count, is_active_in_period
            FROM car_registrations 
            ORDER BY car_number 
            LIMIT 10
        """
        )

        sample_data = cursor.fetchall()
        for reg in sample_data:
            (
                first_name,
                last_name,
                car_number,
                reserved_date,
                expiration_date,
                last_usage_year,
                usage_count,
                is_active,
            ) = reg
            status = "Active" if is_active else "Inactive"
            usage_info = f"Used {usage_count}x" if usage_count > 0 else "No usage"
            print(f"#{car_number}: {first_name} {last_name} - {status} - {usage_info}")
            if reserved_date:
                print(f"  Reserved: {reserved_date} → Expires: {expiration_date}")
            if last_usage_year:
                print(f"  Last used: {last_usage_year}")

        print("\n✅ CSV import completed successfully!")

    except FileNotFoundError:
        print(f"❌ Error: CSV file '{csv_file_path}' not found!")
        return False
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return False
    finally:
        conn.close()

    return True


def main():
    """Main function to run the import"""

    if len(sys.argv) != 2:
        print("Usage: python3 import_csv_registrations.py <csv_file_path>")
        print("Example: python3 import_csv_registrations.py registrations.csv")
        return

    csv_file_path = sys.argv[1]

    if not os.path.exists(csv_file_path):
        print(f"❌ Error: File '{csv_file_path}' does not exist!")
        return

    print(f"📁 Importing from: {csv_file_path}")
    print()

    success = import_csv_registrations(csv_file_path)

    if success:
        print(
            "\n🎉 Import completed! You can now view the registrations in the web interface."
        )
        print("🌐 Visit: http://localhost:5001")
    else:
        print("\n❌ Import failed! Please check the error messages above.")


if __name__ == "__main__":
    main()
