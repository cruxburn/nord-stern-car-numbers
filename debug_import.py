#!/usr/bin/env python3
"""
Debug script to understand the Excel data structure.
"""

import pandas as pd
import re


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


# Read the Excel file
df = pd.read_excel(
    "/Users/andybarker/Downloads/2025 Car Number Registration 2025-02-04.xlsx"
)
print(f"Successfully read Excel file with {len(df)} rows")

# Process first 20 rows to debug
for index, row in df.iterrows():
    if index >= 20:
        break

    # Skip header rows and empty rows
    if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == "":
        print(f"Row {index}: Empty or NaN")
        continue

    # Skip the header row
    if "Fullname Key" in str(row.iloc[0]):
        print(f"Row {index}: Header row")
        continue

    # Get driver name from first column
    driver_name = row.iloc[0]
    first_name, last_name = clean_name(driver_name)

    print(f"Row {index}:")
    print(f"  Driver name: '{driver_name}'")
    print(f"  Parsed: first='{first_name}', last='{last_name}'")

    if not first_name or not last_name:
        print(f"  -> Skipped: Could not parse name")
        continue

    # Extract car number from the second column (Driver(#) Key)
    driver_key = row.iloc[1]
    car_number = extract_car_number(driver_key)

    print(f"  Driver key: '{driver_key}'")
    print(f"  Car number: {car_number}")

    if car_number is None:
        print(f"  -> Skipped: Could not extract car number")
        continue

    print(f"  -> Would import: {first_name} {last_name} - Car #{car_number}")
    print()
