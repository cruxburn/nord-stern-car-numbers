#!/usr/bin/env python3
"""
Tests for export and import functionality in Nord Stern Car Numbers
"""

import unittest
import sqlite3
import os
import tempfile
import sys
import json

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import init_db

class ExportImportTestCase(unittest.TestCase):
    """Test cases for export and import functionality"""
    
    def setUp(self):
        """Set up test database"""
        # Create a temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_conn = sqlite3.connect(self.db_path)
        self.cursor = self.db_conn.cursor()
        
        # Initialize the database
        init_db(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        self.db_conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_export_database_structure(self):
        """Test that export includes all required fields"""
        # Insert test data
        test_data = [
            ("John", "Doe", "1", 1, "BMW", "M3", 2020, "Black", "2020-01-15", "Test note", 2024, 3, 1),
            ("Jane", "Smith", "001", 1, "Porsche", "911", 2021, "Red", "2021-02-20", "Another note", 2023, 2, 0),
        ]
        
        for (first_name, last_name, car_number, sort_order, car_make, car_model, 
             car_year, car_color, reserved_date, notes, last_usage_year, usage_count, is_active_in_period) in test_data:
            self.cursor.execute('''
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, 
                 reserved_date, notes, last_usage_year, usage_count, is_active_in_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, 
                  reserved_date, notes, last_usage_year, usage_count, is_active_in_period))
        
        self.db_conn.commit()
        
        # Test export query structure
        self.cursor.execute('''
            SELECT id, first_name, last_name, car_number, sort_order, car_make, car_model, 
                   car_year, car_color, reserved_date, reserved_for_year, status, notes, 
                   last_usage_year, expiration_date, usage_count, is_active_in_period, 
                   created_at, updated_at
            FROM car_registrations
            ORDER BY sort_order, car_number
        ''')
        
        results = self.cursor.fetchall()
        self.assertEqual(len(results), 2)
        
        # Check that all required fields are present
        required_fields = ['id', 'first_name', 'last_name', 'car_number', 'sort_order', 
                          'car_make', 'car_model', 'car_year', 'car_color', 'reserved_date', 
                          'reserved_for_year', 'status', 'notes', 'last_usage_year', 
                          'expiration_date', 'usage_count', 'is_active_in_period', 
                          'created_at', 'updated_at']
        
        # Verify column count matches expected fields
        self.assertEqual(len(results[0]), len(required_fields))
    
    def test_export_data_integrity(self):
        """Test that exported data maintains integrity"""
        # Insert test data
        test_data = [
            ("John", "Doe", "1", 1, "BMW", "M3", 2020, "Black", "2020-01-15", "Test note", 2024, 3, 1),
            ("Jane", "Smith", "001", 1, "Porsche", "911", 2021, "Red", "2021-02-20", "Another note", 2023, 2, 0),
        ]
        
        for (first_name, last_name, car_number, sort_order, car_make, car_model, 
             car_year, car_color, reserved_date, notes, last_usage_year, usage_count, is_active_in_period) in test_data:
            self.cursor.execute('''
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, 
                 reserved_date, notes, last_usage_year, usage_count, is_active_in_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, 
                  reserved_date, notes, last_usage_year, usage_count, is_active_in_period))
        
        self.db_conn.commit()
        
        # Export data
        self.cursor.execute('''
            SELECT id, first_name, last_name, car_number, sort_order, car_make, car_model, 
                   car_year, car_color, reserved_date, reserved_for_year, status, notes, 
                   last_usage_year, expiration_date, usage_count, is_active_in_period, 
                   created_at, updated_at
            FROM car_registrations
            ORDER BY sort_order, car_number
        ''')
        
        results = self.cursor.fetchall()
        
        # Verify data integrity (results are sorted by sort_order, car_number)
        # First result should be "001" (Jane), second should be "1" (John)
        self.assertEqual(results[0][1], test_data[1][0])  # first_name (Jane)
        self.assertEqual(results[0][2], test_data[1][1])  # last_name (Smith)
        self.assertEqual(results[0][3], test_data[1][2])  # car_number (001)
        self.assertEqual(results[0][4], test_data[1][3])  # sort_order (1)
        
        self.assertEqual(results[1][1], test_data[0][0])  # first_name (John)
        self.assertEqual(results[1][2], test_data[0][1])  # last_name (Doe)
        self.assertEqual(results[1][3], test_data[0][2])  # car_number (1)
        self.assertEqual(results[1][4], test_data[0][3])  # sort_order (1)
    
    def test_import_data_structure(self):
        """Test that import can handle the exported data structure"""
        # Create test export data
        export_data = [
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
                "reserved_for_year": 2025,
                "status": "Active",
                "notes": "Test note",
                "last_usage_year": 2024,
                "expiration_date": "2029-01-15",
                "usage_count": 3,
                "is_active_in_period": 1,
                "created_at": "2025-01-15 10:30:00",
                "updated_at": "2025-01-15 10:30:00"
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
                "reserved_for_year": 2025,
                "status": "Active",
                "notes": "Another note",
                "last_usage_year": 2023,
                "expiration_date": "2028-02-20",
                "usage_count": 2,
                "is_active_in_period": 0,
                "created_at": "2025-01-15 11:15:00",
                "updated_at": "2025-01-15 11:15:00"
            }
        ]
        
        # Test that the data structure is valid for import
        for record in export_data:
            # Check required fields
            required_fields = ['first_name', 'last_name', 'car_number', 'sort_order']
            for field in required_fields:
                self.assertIn(field, record)
                self.assertIsNotNone(record[field])
            
            # Check data types
            self.assertIsInstance(record['first_name'], str)
            self.assertIsInstance(record['last_name'], str)
            self.assertIsInstance(record['car_number'], str)
            self.assertIsInstance(record['sort_order'], int)
    
    def test_export_json_format(self):
        """Test that export data can be converted to JSON format"""
        # Insert test data
        test_data = [
            ("John", "Doe", "1", 1, "BMW", "M3", 2020, "Black", "2020-01-15", "Test note", 2024, 3, 1),
        ]
        
        for (first_name, last_name, car_number, sort_order, car_make, car_model, 
             car_year, car_color, reserved_date, notes, last_usage_year, usage_count, is_active_in_period) in test_data:
            self.cursor.execute('''
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, 
                 reserved_date, notes, last_usage_year, usage_count, is_active_in_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, 
                  reserved_date, notes, last_usage_year, usage_count, is_active_in_period))
        
        self.db_conn.commit()
        
        # Export data
        self.cursor.execute('''
            SELECT id, first_name, last_name, car_number, sort_order, car_make, car_model, 
                   car_year, car_color, reserved_date, reserved_for_year, status, notes, 
                   last_usage_year, expiration_date, usage_count, is_active_in_period, 
                   created_at, updated_at
            FROM car_registrations
            ORDER BY sort_order, car_number
        ''')
        
        results = self.cursor.fetchall()
        
        # Convert to JSON format
        columns = ['id', 'first_name', 'last_name', 'car_number', 'sort_order', 'car_make', 'car_model', 
                   'car_year', 'car_color', 'reserved_date', 'reserved_for_year', 'status', 'notes', 
                   'last_usage_year', 'expiration_date', 'usage_count', 'is_active_in_period', 
                   'created_at', 'updated_at']
        
        json_data = []
        for row in results:
            record = dict(zip(columns, row))
            json_data.append(record)
        
        # Test JSON serialization
        try:
            json_string = json.dumps(json_data, indent=2)
            self.assertIsInstance(json_string, str)
            
            # Test JSON deserialization
            parsed_data = json.loads(json_string)
            self.assertEqual(len(parsed_data), 1)
            self.assertEqual(parsed_data[0]['first_name'], "John")
            self.assertEqual(parsed_data[0]['car_number'], "1")
            self.assertEqual(parsed_data[0]['sort_order'], 1)
        except Exception as e:
            self.fail(f"JSON serialization/deserialization failed: {e}")

if __name__ == '__main__':
    unittest.main() 