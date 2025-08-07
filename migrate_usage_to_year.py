#!/usr/bin/env python3
"""
Migration script to change usage tracking from dates to years only.
This script will:
1. Add a new column 'last_usage_year' (INTEGER)
2. Convert existing 'last_usage_date' values to years
3. Update the expiration calculation logic
"""

import sqlite3
from datetime import datetime
import os


def migrate_usage_to_year():
    """Migrate the database to use year-based usage tracking"""

    db_path = "car_numbers.db"

    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False

    print("🔄 Nord Stern Car Numbers - Usage Migration to Year-Based System")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if migration has already been done
        cursor.execute("PRAGMA table_info(car_registrations)")
        columns = [column[1] for column in cursor.fetchall()]

        if "last_usage_year" in columns:
            print("✅ Migration already completed - last_usage_year column exists")
            return True

        print("📋 Starting migration...")

        # Add new column for year-based usage
        print("➕ Adding last_usage_year column...")
        cursor.execute(
            """
            ALTER TABLE car_registrations 
            ADD COLUMN last_usage_year INTEGER
        """
        )

        # Convert existing date-based usage to year-based
        print("🔄 Converting existing usage dates to years...")
        cursor.execute(
            """
            UPDATE car_registrations 
            SET last_usage_year = CAST(strftime('%Y', last_usage_date) AS INTEGER)
            WHERE last_usage_date IS NOT NULL
        """
        )

        # Update expiration dates based on new year-based system
        print("📅 Recalculating expiration dates...")
        cursor.execute(
            "SELECT id, reserved_date, last_usage_year FROM car_registrations"
        )
        registrations = cursor.fetchall()

        updated_count = 0
        for reg_id, reserved_date, last_usage_year in registrations:
            if reserved_date:
                try:
                    reserved_dt = datetime.strptime(reserved_date, "%Y-%m-%d")
                    reserved_year = reserved_dt.year

                    if last_usage_year:
                        # If there's usage, expiration is 3 years from usage year
                        expiration_year = last_usage_year + 3
                    else:
                        # If no usage, expiration is 3 years from reserved year
                        expiration_year = reserved_year + 3

                    expiration_date = f"{expiration_year}-01-01"

                    # Check if still active (current year <= expiration year)
                    current_year = datetime.now().year
                    is_active = current_year <= expiration_year

                    cursor.execute(
                        """
                        UPDATE car_registrations 
                        SET expiration_date = ?, is_active_in_period = ?
                        WHERE id = ?
                    """,
                        (expiration_date, is_active, reg_id),
                    )

                    updated_count += 1

                except ValueError as e:
                    print(f"⚠️  Error processing registration {reg_id}: {e}")

        print(f"✅ Updated {updated_count} expiration dates")

        # Commit all changes
        conn.commit()
        print("💾 Migration completed successfully!")

        # Show summary
        cursor.execute(
            "SELECT COUNT(*) FROM car_registrations WHERE last_usage_year IS NOT NULL"
        )
        with_usage = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM car_registrations")
        total = cursor.fetchone()[0]

        print(f"\n📊 Migration Summary:")
        print(f"   Total registrations: {total}")
        print(f"   With usage recorded: {with_usage}")
        print(f"   Without usage: {total - with_usage}")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    success = migrate_usage_to_year()
    if success:
        print(
            "\n🎉 Migration completed! The system now uses year-based usage tracking."
        )
        print("📝 You can now:")
        print("   • Record usage by year only")
        print("   • Remove usage entirely")
        print("   • See simplified usage display")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
