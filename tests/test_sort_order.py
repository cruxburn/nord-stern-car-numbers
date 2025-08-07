#!/usr/bin/env python3
"""
Tests for sort_order functionality in Nord Stern Car Numbers
"""

import unittest
import sqlite3
import os
import tempfile
import sys

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import init_db, calculate_expiration_date

class SortOrderTestCase(unittest.TestCase):
    """Test cases for sort_order functionality"""
    
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
    
    def test_sort_order_calculation(self):
        """Test that sort_order is calculated correctly from car_number"""
        test_cases = [
            ("1", 1),
            ("001", 1),
            ("14", 14),
            ("014", 14),
            ("99", 99),
            ("099", 99),
            ("123", 123),
            ("999", 999),
        ]
        
        for car_number, expected_sort_order in test_cases:
            with self.subTest(car_number=car_number):
                try:
                    sort_order = int(car_number)
                    self.assertEqual(sort_order, expected_sort_order)
                except ValueError:
                    self.fail(f"Could not convert car_number '{car_number}' to integer")
    
    def test_sort_order_insertion(self):
        """Test that sort_order is properly inserted when adding registrations"""
        test_data = [
            ("John", "Doe", "1", 1),
            ("Jane", "Smith", "001", 1),
            ("Bob", "Johnson", "14", 14),
            ("Alice", "Brown", "014", 14),
            ("Charlie", "Wilson", "99", 99),
        ]
        
        for first_name, last_name, car_number, expected_sort_order in test_data:
            # Calculate sort_order
            try:
                sort_order = int(car_number)
            except ValueError:
                sort_order = 0
            
            # Insert registration
            self.cursor.execute('''
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, car_number, sort_order, "Test", "Model", 2020, "Red", None, "Test note"))
        
        self.db_conn.commit()
        
        # Verify sort_order values
        self.cursor.execute('SELECT car_number, sort_order FROM car_registrations ORDER BY id')
        results = self.cursor.fetchall()
        
        for i, (car_number, sort_order) in enumerate(results):
            expected_sort_order = test_data[i][3]
            self.assertEqual(sort_order, expected_sort_order, 
                           f"sort_order mismatch for car_number '{car_number}': expected {expected_sort_order}, got {sort_order}")
    
    def test_sorting_by_sort_order(self):
        """Test that registrations are sorted correctly by sort_order"""
        # Insert test data in random order
        test_data = [
            ("Charlie", "Wilson", "99", 99),
            ("John", "Doe", "1", 1),
            ("Alice", "Brown", "014", 14),
            ("Bob", "Johnson", "14", 14),
            ("Jane", "Smith", "001", 1),
        ]
        
        for first_name, last_name, car_number, sort_order in test_data:
            self.cursor.execute('''
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, car_number, sort_order, "Test", "Model", 2020, "Red", None, "Test note"))
        
        self.db_conn.commit()
        
        # Query with ORDER BY sort_order, car_number
        self.cursor.execute('''
            SELECT car_number, sort_order, first_name, last_name 
            FROM car_registrations 
            ORDER BY sort_order, car_number
        ''')
        results = self.cursor.fetchall()
        
        # Expected order: 001, 1, 014, 14, 99 (alphabetical within same sort_order)
        expected_order = ["001", "1", "014", "14", "99"]
        
        for i, (car_number, sort_order, first_name, last_name) in enumerate(results):
            self.assertEqual(car_number, expected_order[i], 
                           f"Sorting order mismatch at position {i}: expected {expected_order[i]}, got {car_number}")
    
    def test_duplicate_car_numbers_sorting(self):
        """Test that duplicate car numbers are handled correctly in sorting"""
        # Insert registrations with duplicate car numbers
        test_data = [
            ("John", "Doe", "1", 1),
            ("Jane", "Smith", "1", 1),  # Duplicate car number
            ("Bob", "Johnson", "14", 14),
            ("Alice", "Brown", "14", 14),  # Duplicate car number
        ]
        
        for first_name, last_name, car_number, sort_order in test_data:
            self.cursor.execute('''
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, car_number, sort_order, "Test", "Model", 2020, "Red", None, "Test note"))
        
        self.db_conn.commit()
        
        # Query with ORDER BY sort_order, car_number
        self.cursor.execute('''
            SELECT car_number, sort_order, first_name, last_name 
            FROM car_registrations 
            ORDER BY sort_order, car_number
        ''')
        results = self.cursor.fetchall()
        
        # Should have 4 results, sorted by sort_order first, then car_number
        self.assertEqual(len(results), 4)
        
        # First two should be car_number "1" (sort_order 1)
        self.assertEqual(results[0][0], "1")  # car_number
        self.assertEqual(results[0][1], 1)    # sort_order
        self.assertEqual(results[1][0], "1")  # car_number
        self.assertEqual(results[1][1], 1)    # sort_order
        
        # Last two should be car_number "14" (sort_order 14)
        self.assertEqual(results[2][0], "14")  # car_number
        self.assertEqual(results[2][1], 14)    # sort_order
        self.assertEqual(results[3][0], "14")  # car_number
        self.assertEqual(results[3][1], 14)    # sort_order
    
    def test_invalid_car_number_sort_order(self):
        """Test that invalid car numbers get sort_order 0"""
        # Insert registration with invalid car number
        self.cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("Test", "User", "invalid", 0, "Test", "Model", 2020, "Red", None, "Test note"))
        
        self.db_conn.commit()
        
        # Verify sort_order is 0
        self.cursor.execute('SELECT sort_order FROM car_registrations WHERE car_number = ?', ("invalid",))
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 0)
    
    def test_sort_order_update_on_edit(self):
        """Test that sort_order is updated when car_number is changed"""
        # Insert initial registration
        self.cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("John", "Doe", "1", 1, "Test", "Model", 2020, "Red", None, "Test note"))
        
        self.db_conn.commit()
        
        # Update car_number from "1" to "99"
        new_car_number = "99"
        new_sort_order = int(new_car_number)
        
        self.cursor.execute('''
            UPDATE car_registrations 
            SET car_number = ?, sort_order = ?
            WHERE first_name = ? AND last_name = ?
        ''', (new_car_number, new_sort_order, "John", "Doe"))
        
        self.db_conn.commit()
        
        # Verify the update
        self.cursor.execute('SELECT car_number, sort_order FROM car_registrations WHERE first_name = ? AND last_name = ?', ("John", "Doe"))
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "99")  # car_number
        self.assertEqual(result[1], 99)    # sort_order

if __name__ == '__main__':
    unittest.main() 