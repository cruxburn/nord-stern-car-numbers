#!/usr/bin/env python3
"""
Script to clear all car registration data from the database.
This preserves the table structure but removes all data.
"""

import sqlite3
import os


def clear_database():
    """Clear all car registration data from the database."""

    # Check if database file exists
    if not os.path.exists("car_numbers.db"):
        print("❌ Database file 'car_numbers.db' not found!")
        return

    # Connect to SQLite database
    conn = sqlite3.connect("car_numbers.db")
    cursor = conn.cursor()

    try:
        # Get current count
        cursor.execute("SELECT COUNT(*) FROM car_registrations")
        current_count = cursor.fetchone()[0]

        print(f"📊 Current database contains {current_count} registrations")

        if current_count == 0:
            print("✅ Database is already empty!")
            return

        # Clear all data from the table
        cursor.execute("DELETE FROM car_registrations")

        # Reset the auto-increment counter
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="car_registrations"')

        # Commit the changes
        conn.commit()

        # Verify the table is empty
        cursor.execute("SELECT COUNT(*) FROM car_registrations")
        new_count = cursor.fetchone()[0]

        print(
            f"✅ Successfully cleared {current_count} registrations from the database"
        )
        print(f"📊 Database now contains {new_count} registrations")
        print("🔄 Auto-increment counter has been reset")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("🗑️  Nord Stern Car Numbers - Database Clear Tool")
    print("=" * 50)

    # Automatically clear the database without confirmation
    clear_database()
    print("\n🎉 Database cleared successfully!")
    print("📝 You can now import your new CSV file.")
