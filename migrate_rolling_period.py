#!/usr/bin/env python3
"""
Database Migration Script for 3-Year Rolling Period System
Adds new fields to track usage and expiration dates for car number registrations
"""

import sqlite3
import os
from datetime import datetime, timedelta

def migrate_database():
    """Migrate the database to support 3-year rolling periods"""
    
    db_path = 'car_numbers.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if migration has already been done
        cursor.execute("PRAGMA table_info(car_registrations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            'last_usage_date',
            'expiration_date', 
            'usage_count',
            'is_active_in_period'
        ]
        
        # Check which columns need to be added
        columns_to_add = [col for col in new_columns if col not in columns]
        
        if not columns_to_add:
            print("✅ Database already migrated - all new columns exist")
            return True
        
        print(f"🔄 Adding new columns: {', '.join(columns_to_add)}")
        
        # Add new columns
        for column in columns_to_add:
            if column == 'last_usage_date':
                cursor.execute('ALTER TABLE car_registrations ADD COLUMN last_usage_date DATE')
            elif column == 'expiration_date':
                cursor.execute('ALTER TABLE car_registrations ADD COLUMN expiration_date DATE')
            elif column == 'usage_count':
                cursor.execute('ALTER TABLE car_registrations ADD COLUMN usage_count INTEGER DEFAULT 0')
            elif column == 'is_active_in_period':
                cursor.execute('ALTER TABLE car_registrations ADD COLUMN is_active_in_period BOOLEAN DEFAULT 1')
        
        # Calculate initial expiration dates and usage status for existing records
        print("🔄 Calculating initial expiration dates for existing records...")
        
        cursor.execute('SELECT id, reserved_date, status FROM car_registrations')
        registrations = cursor.fetchall()
        
        for reg_id, reserved_date, status in registrations:
            if reserved_date:
                # Parse the reserved date
                try:
                    reserved_dt = datetime.strptime(reserved_date, '%Y-%m-%d')
                    
                    # Calculate expiration date (3 years from reserved date)
                    expiration_dt = reserved_dt + timedelta(days=3*365)
                    
                    # Check if the registration is still active in the current period
                    current_date = datetime.now()
                    is_active = (current_date <= expiration_dt) and (status == 'Active')
                    
                    # Update the record
                    cursor.execute('''
                        UPDATE car_registrations 
                        SET expiration_date = ?, is_active_in_period = ?
                        WHERE id = ?
                    ''', (expiration_dt.strftime('%Y-%m-%d'), is_active, reg_id))
                    
                except ValueError as e:
                    print(f"⚠️  Warning: Could not parse reserved_date '{reserved_date}' for record {reg_id}: {e}")
                    continue
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Show summary
        cursor.execute('SELECT COUNT(*) FROM car_registrations')
        total_records = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM car_registrations WHERE is_active_in_period = 1')
        active_records = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM car_registrations WHERE expiration_date IS NOT NULL')
        with_expiration = cursor.fetchone()[0]
        
        print(f"\n📊 Migration Summary:")
        print(f"   Total records: {total_records}")
        print(f"   Records with expiration dates: {with_expiration}")
        print(f"   Active in current period: {active_records}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def calculate_expiration_date(reserved_date, last_usage_date=None):
    """
    Calculate expiration date based on 3-year rolling period rules
    
    Args:
        reserved_date (str): Original reservation date (YYYY-MM-DD)
        last_usage_date (str): Last usage date (YYYY-MM-DD) or None
    
    Returns:
        tuple: (expiration_date, is_active_in_period)
    """
    try:
        reserved_dt = datetime.strptime(reserved_date, '%Y-%m-%d')
        current_date = datetime.now()
        
        if last_usage_date:
            # If there's usage, calculate from the last usage date
            last_usage_dt = datetime.strptime(last_usage_date, '%Y-%m-%d')
            expiration_dt = last_usage_dt + timedelta(days=3*365)
        else:
            # If no usage, calculate from the original reserved date
            expiration_dt = reserved_dt + timedelta(days=3*365)
        
        # Check if still active in current period
        is_active = current_date <= expiration_dt
        
        return expiration_dt.strftime('%Y-%m-%d'), is_active
        
    except ValueError as e:
        print(f"⚠️  Error calculating expiration date: {e}")
        return None, False

def update_usage_for_registration(registration_id, usage_date=None):
    """
    Update usage information for a registration
    
    Args:
        registration_id (int): The registration ID
        usage_date (str): Usage date (YYYY-MM-DD) or None for current date
    """
    if usage_date is None:
        usage_date = datetime.now().strftime('%Y-%m-%d')
    
    db_path = 'car_numbers.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get current registration info
        cursor.execute('''
            SELECT reserved_date, last_usage_date, usage_count 
            FROM car_registrations 
            WHERE id = ?
        ''', (registration_id,))
        
        result = cursor.fetchone()
        if not result:
            print(f"❌ Registration {registration_id} not found")
            return False
        
        reserved_date, current_last_usage, current_usage_count = result
        
        # Update usage information
        new_usage_count = current_usage_count + 1
        
        # Calculate new expiration date
        expiration_date, is_active = calculate_expiration_date(reserved_date, usage_date)
        
        # Update the record
        cursor.execute('''
            UPDATE car_registrations 
            SET last_usage_date = ?, usage_count = ?, expiration_date = ?, is_active_in_period = ?
            WHERE id = ?
        ''', (usage_date, new_usage_count, expiration_date, is_active, registration_id))
        
        conn.commit()
        print(f"✅ Updated usage for registration {registration_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating usage: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting database migration for 3-year rolling period system...")
    
    if migrate_database():
        print("\n🎉 Migration completed successfully!")
        print("📝 The database now supports:")
        print("   • 3-year rolling periods from reservation date")
        print("   • Usage tracking and automatic renewal")
        print("   • Expiration date calculations")
        print("   • Active period status tracking")
    else:
        print("\n❌ Migration failed!")
        print("💡 Please check the error messages above and try again.") 