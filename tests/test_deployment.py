#!/usr/bin/env python3
"""
Tests for deployment-related functionality in Nord Stern Car Numbers
"""

import unittest
import sqlite3
import os
import tempfile
import sys
import json
import shutil

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from init_production_db import init_production_database


class DeploymentTestCase(unittest.TestCase):
    """Test cases for deployment functionality"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_car_numbers.db")
        
        # Create test data
        self.test_registrations = [
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "car_number": "1",
                "sort_order": 1,
                "car_make": "BMW",
                "car_model": "M3",
                "car_year": 2020,
                "car_color": "Black",
                "reserved_date": "2020-01-15",
                "reserved_for_year": 2020,
                "status": "Active",
                "notes": "Test note",
                "last_usage_year": 2024,
                "expiration_date": "2027-12-31",
                "usage_count": 3,
                "is_active_in_period": 1,
                "created_at": "2020-01-15 10:00:00",
                "updated_at": "2024-01-15 10:00:00"
            },
            {
                "id": 2,
                "first_name": "Jane",
                "last_name": "Smith",
                "car_number": "001",
                "sort_order": 1,
                "car_make": "Porsche",
                "car_model": "911",
                "car_year": 2021,
                "car_color": "Red",
                "reserved_date": "2021-02-20",
                "reserved_for_year": 2021,
                "status": "Active",
                "notes": "Another note",
                "last_usage_year": 2023,
                "expiration_date": "2026-12-31",
                "usage_count": 2,
                "is_active_in_period": 0,
                "created_at": "2021-02-20 10:00:00",
                "updated_at": "2023-02-20 10:00:00"
            }
        ]

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    def test_init_production_database_no_data_file(self):
        """Test that init_production_database preserves existing data when no data file is provided"""
        # First, create a database with some data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create schema
        cursor.execute("""
            CREATE TABLE car_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                car_number TEXT NOT NULL,
                sort_order INTEGER,
                car_make TEXT,
                car_model TEXT,
                car_year INTEGER,
                car_color TEXT,
                reserved_date TEXT,
                reserved_for_year INTEGER,
                status TEXT DEFAULT 'Active',
                notes TEXT,
                last_usage_year INTEGER,
                expiration_date TEXT,
                usage_count INTEGER DEFAULT 0,
                is_active_in_period BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        cursor.execute("""
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("John", "Doe", "1", 1, "BMW", "M3", 2020, "Black", "2020-01-15", "Test"))
        
        conn.commit()
        conn.close()
        
        # Verify data exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM car_registrations")
        initial_count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(initial_count, 1, "Initial data should exist")
        
        # Now run init_production_database with no data file
        success = init_production_database(self.db_path, None)
        
        self.assertTrue(success, "init_production_database should succeed")
        
        # Verify data is still there
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM car_registrations")
        final_count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(final_count, 1, "Existing data should be preserved")
        self.assertEqual(initial_count, final_count, "Data count should not change")

    def test_init_production_database_with_json_data_file(self):
        """Test that init_production_database clears and loads data when JSON file is provided"""
        # Create a database with existing data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create schema
        cursor.execute("""
            CREATE TABLE car_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                car_number TEXT NOT NULL,
                sort_order INTEGER,
                car_make TEXT,
                car_model TEXT,
                car_year INTEGER,
                car_color TEXT,
                reserved_date TEXT,
                reserved_for_year INTEGER,
                status TEXT DEFAULT 'Active',
                notes TEXT,
                last_usage_year INTEGER,
                expiration_date TEXT,
                usage_count INTEGER DEFAULT 0,
                is_active_in_period BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert existing data
        cursor.execute("""
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Old", "Data", "999", 999, "Old", "Car", 2019, "Gray", "2019-01-01", "Old data"))
        
        conn.commit()
        conn.close()
        
        # Create JSON export file
        json_file = os.path.join(self.test_dir, "database_export.json")
        export_data = {"registrations": self.test_registrations}
        
        with open(json_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        # Run init_production_database with JSON file
        success = init_production_database(self.db_path, json_file)
        
        self.assertTrue(success, "init_production_database should succeed")
        
        # Verify data was cleared and replaced
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM car_registrations")
        final_count = cursor.fetchone()[0]
        
        # Check that new data was loaded
        cursor.execute("SELECT first_name, last_name FROM car_registrations ORDER BY id")
        names = cursor.fetchall()
        conn.close()
        
        self.assertEqual(final_count, 2, "Should have 2 registrations from JSON file")
        self.assertEqual(names[0], ("John", "Doe"), "First registration should be John Doe")
        self.assertEqual(names[1], ("Jane", "Smith"), "Second registration should be Jane Smith")

    def test_init_production_database_with_sql_data_file(self):
        """Test that init_production_database clears and loads data when SQL file is provided"""
        # Create a database with existing data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create schema
        cursor.execute("""
            CREATE TABLE car_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                car_number TEXT NOT NULL,
                sort_order INTEGER,
                car_make TEXT,
                car_model TEXT,
                car_year INTEGER,
                car_color TEXT,
                reserved_date TEXT,
                reserved_for_year INTEGER,
                status TEXT DEFAULT 'Active',
                notes TEXT,
                last_usage_year INTEGER,
                expiration_date TEXT,
                usage_count INTEGER DEFAULT 0,
                is_active_in_period BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert existing data
        cursor.execute("""
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Old", "Data", "999", 999, "Old", "Car", 2019, "Gray", "2019-01-01", "Old data"))
        
        conn.commit()
        conn.close()
        
        # Create SQL export file
        sql_file = os.path.join(self.test_dir, "database_import.sql")
        with open(sql_file, 'w') as f:
            f.write("DELETE FROM car_registrations;\n")
            f.write("INSERT INTO car_registrations (id, first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, reserved_for_year, status, notes, last_usage_year, expiration_date, usage_count, is_active_in_period, created_at, updated_at) VALUES (1, 'John', 'Doe', '1', 1, 'BMW', 'M3', 2020, 'Black', '2020-01-15', 2020, 'Active', 'Test note', 2024, '2027-12-31', 3, 1, '2020-01-15 10:00:00', '2024-01-15 10:00:00');\n")
            f.write("INSERT INTO car_registrations (id, first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, reserved_for_year, status, notes, last_usage_year, expiration_date, usage_count, is_active_in_period, created_at, updated_at) VALUES (2, 'Jane', 'Smith', '001', 1, 'Porsche', '911', 2021, 'Red', '2021-02-20', 2021, 'Active', 'Another note', 2023, '2026-12-31', 2, 0, '2021-02-20 10:00:00', '2023-02-20 10:00:00');\n")
        
        # Run init_production_database with SQL file
        success = init_production_database(self.db_path, sql_file)
        
        self.assertTrue(success, "init_production_database should succeed")
        
        # Verify data was cleared and replaced
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM car_registrations")
        final_count = cursor.fetchone()[0]
        
        # Check that new data was loaded
        cursor.execute("SELECT first_name, last_name FROM car_registrations ORDER BY id")
        names = cursor.fetchall()
        conn.close()
        
        self.assertEqual(final_count, 2, "Should have 2 registrations from SQL file")
        self.assertEqual(names[0], ("John", "Doe"), "First registration should be John Doe")
        self.assertEqual(names[1], ("Jane", "Smith"), "Second registration should be Jane Smith")

    def test_init_production_database_creates_indexes(self):
        """Test that init_production_database creates required indexes"""
        # Run init_production_database
        success = init_production_database(self.db_path, None)
        
        self.assertTrue(success, "init_production_database should succeed")
        
        # Check that indexes were created
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        expected_indexes = [
            "idx_car_number",
            "idx_sort_order", 
            "idx_name",
            "idx_status"
        ]
        
        for index in expected_indexes:
            self.assertIn(index, indexes, f"Index {index} should be created")
        
        conn.close()

    def test_init_production_database_invalid_file_format(self):
        """Test that init_production_database handles invalid file formats gracefully"""
        # Create an invalid file
        invalid_file = os.path.join(self.test_dir, "invalid.txt")
        with open(invalid_file, 'w') as f:
            f.write("This is not a valid data file")
        
        # Run init_production_database with invalid file
        success = init_production_database(self.db_path, invalid_file)
        
        self.assertFalse(success, "init_production_database should fail with invalid file format")

    def test_init_production_database_nonexistent_file(self):
        """Test that init_production_database handles nonexistent files gracefully"""
        # Run init_production_database with nonexistent file
        success = init_production_database(self.db_path, "nonexistent.json")
        
        self.assertTrue(success, "init_production_database should succeed and preserve existing data")


if __name__ == "__main__":
    unittest.main() 