#!/usr/bin/env python3
"""
Script to add sample car registration data for testing the web application.
This version supports car numbers with leading zeros (e.g., 001, 014, 022).
"""

import sqlite3
from datetime import datetime


def add_sample_data():
    """Add sample car registration data to the database."""

    # Connect to SQLite database
    conn = sqlite3.connect("car_numbers.db")
    cursor = conn.cursor()

    # Drop existing table to recreate with new schema
    cursor.execute("DROP TABLE IF EXISTS car_registrations")

    # Initialize database with TEXT car_number field
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS car_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            car_number TEXT UNIQUE NOT NULL,
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

    # Sample data with car numbers including leading zeros
    sample_registrations = [
        (
            "Mike",
            "Mady",
            "000",
            "BMW",
            "M3",
            2020,
            "Alpine White",
            "Active",
            "2025-01-15",
            "First registration of the season",
        ),
        (
            "Scott",
            "Anderst",
            "001",
            "Porsche",
            "911",
            2021,
            "GT Silver",
            "Active",
            "2025-01-16",
            "Returning driver",
        ),
        (
            "Paul",
            "Binek",
            "002",
            "Audi",
            "RS4",
            2019,
            "Nardo Gray",
            "Retired",
            "2025-01-10",
            "Retired from active racing",
        ),
        (
            "Gordon",
            "Doering",
            "003",
            "BMW",
            "M2",
            2022,
            "Black Sapphire",
            "Active",
            "2025-01-17",
            "New driver this season",
        ),
        (
            "Bruce",
            "Boeder",
            "004",
            "Porsche",
            "Cayman",
            2020,
            "Guards Red",
            "Active",
            "2025-01-18",
            "Track day enthusiast",
        ),
        (
            "Dave",
            "Billingsley",
            "005",
            "Audi",
            "TT RS",
            2021,
            "Daytona Gray",
            "Active",
            "2025-01-19",
            "Experienced driver",
        ),
        (
            "Dale",
            "Miron",
            "006",
            "BMW",
            "M4",
            2023,
            "Isle of Man Green",
            "Active",
            "2025-01-20",
            "New car this year",
        ),
        (
            "Dmitri",
            "Shtulman",
            "007",
            "Porsche",
            "Boxster",
            2018,
            "Carrara White",
            "Active",
            "2025-01-21",
            "Weekend warrior",
        ),
        (
            "Paul",
            "Thai",
            "008",
            "Audi",
            "S4",
            2020,
            "Glacier White",
            "Active",
            "2025-01-22",
            "Family car for track days",
        ),
        (
            "Keith",
            "Anderson",
            "009",
            "BMW",
            "M5",
            2021,
            "Tanzanite Blue",
            "Active",
            "2025-01-23",
            "High performance sedan",
        ),
        (
            "Rick",
            "Polk",
            "010",
            "Porsche",
            "Cayenne",
            2019,
            "Moonlight Blue",
            "Active",
            "2025-01-24",
            "SUV for track support",
        ),
        (
            "Greg",
            "Windfeldt",
            "011",
            "Audi",
            "RS6",
            2022,
            "Nogaro Blue",
            "Active",
            "2025-01-25",
            "Wagon enthusiast",
        ),
        (
            "Bill",
            "Wolfson",
            "012",
            "BMW",
            "X3 M",
            2021,
            "Toronto Red",
            "Active",
            "2025-01-26",
            "SUV track day",
        ),
        (
            "Bob",
            "Fleming",
            "013",
            "Porsche",
            "Macan",
            2020,
            "Dolomite Silver",
            "Active",
            "2025-01-27",
            "Daily driver",
        ),
        (
            "Tom",
            "Sabow",
            "014",
            "Audi",
            "RS3",
            2023,
            "Kyalami Green",
            "Active",
            "2025-01-28",
            "Compact performance",
        ),
        (
            "Scott",
            "Perkinson",
            "015",
            "BMW",
            "M8",
            2022,
            "Frozen Black",
            "Active",
            "2025-01-29",
            "Luxury performance",
        ),
        (
            "Richard",
            "Moe",
            "016",
            "Porsche",
            "Panamera",
            2021,
            "Jet Black",
            "Active",
            "2025-01-30",
            "Four-door track car",
        ),
        (
            "Jim",
            "Seubert",
            "017",
            "Audi",
            "RS7",
            2020,
            "Daytona Gray",
            "Active",
            "2025-02-01",
            "Fastback sedan",
        ),
        (
            "Sarah",
            "Johnson",
            "018",
            "BMW",
            "M240i",
            2023,
            "Thundernight",
            "Active",
            "2025-02-02",
            "New driver",
        ),
        (
            "Michael",
            "Chen",
            "019",
            "Porsche",
            "718",
            2022,
            "Racing Yellow",
            "Active",
            "2025-02-03",
            "Mid-engine sports car",
        ),
        (
            "Lisa",
            "Martinez",
            "020",
            "Audi",
            "S3",
            2021,
            "Glacier White",
            "Active",
            "2025-02-04",
            "Compact luxury",
        ),
        (
            "Andy",
            "Barker",
            "022",
            "BMW",
            "M3",
            2023,
            "Frozen Black",
            "Active",
            "2025-02-05",
            "Test registration with leading zero",
        ),
        (
            "John",
            "Smith",
            "100",
            "Porsche",
            "911 GT3",
            2022,
            "Shark Blue",
            "Active",
            "2025-02-06",
            "Three digit number",
        ),
        (
            "Jane",
            "Doe",
            "999",
            "Audi",
            "RS e-tron GT",
            2024,
            "Daytona Gray",
            "Active",
            "2025-02-07",
            "High number test",
        ),
    ]

    # Insert sample data
    for registration in sample_registrations:
        try:
            cursor.execute(
                """
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, car_make, car_model, car_year, car_color, status, reserved_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                registration,
            )
            print(
                f"Added: {registration[0]} {registration[1]} - Car #{registration[2]}"
            )
        except sqlite3.IntegrityError as e:
            print(f"Error adding {registration[0]} {registration[1]}: {e}")
        except Exception as e:
            print(f"Error adding {registration[0]} {registration[1]}: {e}")

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"\nSample data import completed!")
    print(f"Added {len(sample_registrations)} sample registrations")
    print(f"Database file: car_numbers.db")
    print(f"Car numbers now support leading zeros (e.g., 001, 014, 022)")


if __name__ == "__main__":
    add_sample_data()
