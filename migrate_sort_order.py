#!/usr/bin/env python3
"""
Migration script to add sort_order column to existing car_registrations table
This script will:
1. Add the sort_order column if it doesn't exist
2. Populate sort_order with the numeric value of car_number
3. Update the database schema
"""

import sqlite3
import os

def migrate_sort_order():
    """Add sort_order column and populate it with numeric car number values"""
    
    db_path = 'car_numbers.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting sort_order migration...")
        
        # Check if sort_order column already exists
        cursor.execute("PRAGMA table_info(car_registrations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'sort_order' not in columns:
            print("📝 Adding sort_order column...")
            cursor.execute('ALTER TABLE car_registrations ADD COLUMN sort_order INTEGER')
            print("✅ sort_order column added")
        else:
            print("ℹ️  sort_order column already exists")
        
        # Get all registrations to update sort_order
        cursor.execute('SELECT id, car_number FROM car_registrations')
        registrations = cursor.fetchall()
        
        print(f"📊 Found {len(registrations)} registrations to update")
        
        updated_count = 0
        for reg_id, car_number in registrations:
            try:
                # Convert car_number to integer for sorting
                # This handles cases like "001" -> 1, "099" -> 99, etc.
                sort_order = int(car_number)
                
                cursor.execute('''
                    UPDATE car_registrations 
                    SET sort_order = ? 
                    WHERE id = ?
                ''', (sort_order, reg_id))
                
                updated_count += 1
                print(f"  ✅ Updated registration {reg_id}: {car_number} -> sort_order {sort_order}")
                
            except ValueError as e:
                print(f"  ⚠️  Warning: Could not convert car_number '{car_number}' to integer for registration {reg_id}")
                # Set to 0 for invalid numbers
                cursor.execute('''
                    UPDATE car_registrations 
                    SET sort_order = 0 
                    WHERE id = ?
                ''', (reg_id,))
        
        conn.commit()
        print(f"✅ Successfully updated {updated_count} registrations")
        
        # Verify the migration
        print("\n🔍 Verifying migration...")
        cursor.execute('''
            SELECT car_number, sort_order 
            FROM car_registrations 
            ORDER BY sort_order, car_number 
            LIMIT 10
        ''')
        
        results = cursor.fetchall()
        print("📋 Sample sorted results:")
        for car_number, sort_order in results:
            print(f"  {car_number} (sort_order: {sort_order})")
        
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_sort_order() 