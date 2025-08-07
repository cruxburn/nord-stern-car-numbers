#!/usr/bin/env python3
"""
Script to import car registration data from Excel file into the SQLite database.
This script processes the Excel file and extracts driver information and car details.
"""

import pandas as pd
import sqlite3
import re
from datetime import datetime


def clean_name(name):
    """Clean and parse driver names from the Excel format."""
    if pd.isna(name) or name == "NaN":
        return None, None

    # Handle cases like "Mady,Mike" or "Mady,Mike(0)"
    name_str = str(name).strip()

    # Remove any trailing numbers in parentheses like "(0)", "(01)", etc.
    name_str = re.sub(r"\(\d+\)$", "", name_str)

    # Split by comma
    if "," in name_str:
        parts = name_str.split(",")
        if len(parts) >= 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            return first_name, last_name

    # If no comma, try to split by space
    parts = name_str.split()
    if len(parts) >= 2:
        first_name = parts[0].strip()
        last_name = parts[1].strip()
        return first_name, last_name

    return None, None


def extract_car_number(name):
    """Extract car number from driver name field."""
    if pd.isna(name) or name == "NaN":
        return None

    name_str = str(name).strip()

    # Look for numbers in parentheses like "(0)", "(01)", "(004)"
    match = re.search(r"\((\d+)\)$", name_str)
    if match:
        return int(match.group(1))

    return None


def import_excel_data():
    """Import data from Excel file into SQLite database."""

    # Read the Excel file
    try:
        df = pd.read_excel(
            "/Users/andybarker/Downloads/2025 Car Number Registration 2025-02-04.xlsx"
        )
        print(f"Successfully read Excel file with {len(df)} rows")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Connect to SQLite database
    conn = sqlite3.connect("car_numbers.db")
    cursor = conn.cursor()

    # Initialize database
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS car_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            car_number INTEGER UNIQUE NOT NULL,
            car_make TEXT,
            car_model TEXT,
            car_year INTEGER,
            car_color TEXT,
            reserved_date DATE,
            reserved_for_year INTEGER DEFAULT 2025,
            status TEXT DEFAULT 'Active',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Clear existing data
    cursor.execute("DELETE FROM car_registrations")

    imported_count = 0
    skipped_count = 0

    # Process each row
    for index, row in df.iterrows():
        # Skip header rows and empty rows
        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
            continue

        # Skip the header row
        if "Fullname Key" in str(row.iloc[0]):
            continue

        # Get driver name from first column
        driver_name = row.iloc[0]
        first_name, last_name = clean_name(driver_name)

        if not first_name or not last_name:
            skipped_count += 1
            continue

        # Extract car number from the second column (Driver(#) Key)
        driver_key = row.iloc[1]
        car_number = extract_car_number(driver_key)
        if car_number is None:
            skipped_count += 1
            continue

        # Check if reserved for 2025 (column 3)
        reserved_2025 = row.iloc[2]
        status = "Active"
        if pd.notna(reserved_2025) and str(reserved_2025).strip().lower() == "retired":
            status = "Retired"

        # Try to get car information from the last columns
        car_make = None
        car_model = None
        car_year = None
        car_color = None

        # Look for car information in the last few columns
        for col_idx in range(len(row) - 10, len(row)):
            if pd.notna(row.iloc[col_idx]):
                cell_value = str(row.iloc[col_idx]).strip()
                if cell_value and cell_value != "nan":
                    # Try to identify car make, model, year, color
                    if not car_make and any(
                        brand in cell_value.lower()
                        for brand in [
                            "bmw",
                            "porsche",
                            "audi",
                            "mercedes",
                            "ferrari",
                            "lamborghini",
                            "toyota",
                            "honda",
                            "ford",
                            "chevrolet",
                        ]
                    ):
                        car_make = cell_value
                    elif not car_model and len(cell_value) <= 10:
                        car_model = cell_value
                    elif (
                        not car_year
                        and cell_value.isdigit()
                        and 1900 <= int(cell_value) <= 2030
                    ):
                        car_year = int(cell_value)
                    elif not car_color and len(cell_value) <= 15:
                        car_color = cell_value

        # Insert into database
        try:
            cursor.execute(
                """
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, car_make, car_model, car_year, car_color, status, reserved_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    first_name,
                    last_name,
                    car_number,
                    car_make,
                    car_model,
                    car_year,
                    car_color,
                    status,
                    datetime.now().date(),
                ),
            )

            imported_count += 1
            print(f"Imported: {first_name} {last_name} - Car #{car_number}")

        except sqlite3.IntegrityError as e:
            print(f"Error importing {first_name} {last_name}: {e}")
            skipped_count += 1
        except Exception as e:
            print(f"Error importing {first_name} {last_name}: {e}")
            skipped_count += 1

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"\nImport completed!")
    print(f"Successfully imported: {imported_count} registrations")
    print(f"Skipped: {skipped_count} entries")
    print(f"Database file: car_numbers.db")


if __name__ == "__main__":
    import_excel_data()
