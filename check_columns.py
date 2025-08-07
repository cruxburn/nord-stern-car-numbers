#!/usr/bin/env python3
"""
Check the current database column structure and indices
"""

import sqlite3

def check_columns():
    """Check the current database column structure"""
    
    db_path = 'car_numbers.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get column information
        cursor.execute("PRAGMA table_info(car_registrations)")
        columns = cursor.fetchall()
        
        print("📋 Current Database Column Structure:")
        print("=" * 50)
        
        for i, col in enumerate(columns):
            print(f"Index {i}: {col[1]} ({col[2]})")
        
        # Get a sample record to see the data
        cursor.execute('SELECT * FROM car_registrations LIMIT 1')
        sample = cursor.fetchone()
        
        if sample:
            print(f"\n📊 Sample Record Data:")
            print("=" * 30)
            for i, value in enumerate(sample):
                print(f"Index {i}: {value}")
        
        # Check specific columns we care about
        print(f"\n🎯 Key Column Indices:")
        print("=" * 25)
        
        column_names = [col[1] for col in columns]
        
        key_columns = [
            'id', 'first_name', 'last_name', 'car_number', 
            'car_make', 'car_model', 'car_year', 'car_color',
            'reserved_date', 'reserved_for_year', 'status', 'notes',
            'last_usage_year', 'expiration_date', 'usage_count', 
            'is_active_in_period', 'created_at', 'updated_at'
        ]
        
        for col_name in key_columns:
            if col_name in column_names:
                idx = column_names.index(col_name)
                print(f"{col_name}: index {idx}")
            else:
                print(f"{col_name}: NOT FOUND")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    check_columns() 