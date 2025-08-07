#!/usr/bin/env python3
"""
Cleanup script to remove the old last_usage_date column since we now use last_usage_year.
This script will:
1. Check the current database structure
2. Remove the last_usage_date column if it exists
3. Verify the cleanup was successful
"""

import sqlite3
import os


def cleanup_usage_columns():
    """Clean up the database by removing old usage date column"""

    db_path = "car_numbers.db"

    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False

    print("🧹 Nord Stern Car Numbers - Database Cleanup")
    print("=" * 50)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check current table structure
        print("📋 Checking current database structure...")
        cursor.execute("PRAGMA table_info(car_registrations)")
        columns = cursor.fetchall()

        print("\nCurrent columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

        # Check if last_usage_date column exists
        has_old_column = any(col[1] == "last_usage_date" for col in columns)
        has_new_column = any(col[1] == "last_usage_year" for col in columns)

        print(f"\n📊 Column Status:")
        print(f"  last_usage_date exists: {has_old_column}")
        print(f"  last_usage_year exists: {has_new_column}")

        if not has_old_column:
            print("\n✅ No cleanup needed - last_usage_date column doesn't exist")
            return True

        if not has_new_column:
            print("\n❌ Error: last_usage_year column doesn't exist!")
            print(
                "Please run the migration script first: python3 migrate_usage_to_year.py"
            )
            return False

        # Show sample data before cleanup
        print("\n📋 Sample data before cleanup:")
        cursor.execute(
            """
            SELECT id, first_name, last_name, car_number, last_usage_date, last_usage_year, usage_count 
            FROM car_registrations 
            WHERE last_usage_date IS NOT NULL 
            LIMIT 5
        """
        )
        sample_data = cursor.fetchall()

        for row in sample_data:
            print(
                f"  ID {row[0]}: {row[1]} {row[2]} (#{row[3]}) - Old: {row[4]}, New: {row[5]}, Count: {row[6]}"
            )

        # Remove the old column
        print(f"\n🗑️  Removing last_usage_date column...")

        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        # First, get all data
        cursor.execute("SELECT * FROM car_registrations")
        all_data = cursor.fetchall()

        # Create new table without last_usage_date
        cursor.execute(
            """
            CREATE TABLE car_registrations_new (
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
                last_usage_year INTEGER,
                expiration_date DATE,
                usage_count INTEGER DEFAULT 0,
                is_active_in_period BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Insert all data (excluding the last_usage_date column)
        for row in all_data:
            # Remove the last_usage_date column (index 12) from the row
            new_row = row[:12] + row[13:]  # Skip index 12 (last_usage_date)
            cursor.execute(
                """
                INSERT INTO car_registrations_new (
                    id, first_name, last_name, car_number, car_make, car_model, car_year, 
                    car_color, reserved_date, reserved_for_year, status, notes, 
                    last_usage_year, expiration_date, usage_count, is_active_in_period, 
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                new_row,
            )

        # Drop old table and rename new table
        cursor.execute("DROP TABLE car_registrations")
        cursor.execute("ALTER TABLE car_registrations_new RENAME TO car_registrations")

        conn.commit()
        print("✅ Cleanup completed successfully!")

        # Verify the cleanup
        print("\n📋 Verifying cleanup...")
        cursor.execute("PRAGMA table_info(car_registrations)")
        columns_after = cursor.fetchall()

        print("\nColumns after cleanup:")
        for col in columns_after:
            print(f"  {col[1]} ({col[2]})")

        has_old_column_after = any(col[1] == "last_usage_date" for col in columns_after)
        has_new_column_after = any(col[1] == "last_usage_year" for col in columns_after)

        print(f"\n📊 Final Status:")
        print(f"  last_usage_date exists: {has_old_column_after}")
        print(f"  last_usage_year exists: {has_new_column_after}")

        if not has_old_column_after and has_new_column_after:
            print(
                "\n🎉 Cleanup successful! Database now uses year-based usage tracking only."
            )
            return True
        else:
            print("\n❌ Cleanup failed!")
            return False

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    success = cleanup_usage_columns()
    if success:
        print("\n🎉 Database cleanup completed!")
        print("📝 The system now uses only year-based usage tracking.")
    else:
        print("\n❌ Database cleanup failed. Please check the error messages above.")
