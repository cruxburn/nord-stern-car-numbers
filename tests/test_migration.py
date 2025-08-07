#!/usr/bin/env python3
"""
Tests for migration scripts in Nord Stern Car Numbers
"""

import unittest
import sqlite3
import os
import tempfile
import sys

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import init_db


class MigrationTestCase(unittest.TestCase):
    """Test cases for migration functionality"""

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

    def test_migrate_sort_order_column_addition(self):
        """Test that sort_order column is added correctly"""
        # Check if sort_order column exists
        self.cursor.execute("PRAGMA table_info(car_registrations)")
        columns = [column[1] for column in self.cursor.fetchall()]

        # sort_order should be in the columns list
        self.assertIn("sort_order", columns)

        # Get column details
        self.cursor.execute("PRAGMA table_info(car_registrations)")
        column_info = self.cursor.fetchall()

        sort_order_column = None
        for column in column_info:
            if column[1] == "sort_order":
                sort_order_column = column
                break

        self.assertIsNotNone(sort_order_column)
        self.assertEqual(sort_order_column[2], "INTEGER")  # Data type

    def test_migrate_sort_order_population(self):
        """Test that sort_order is populated correctly for existing data"""
        # Insert test data without sort_order (simulating old data)
        test_data = [
            ("John", "Doe", "1"),
            ("Jane", "Smith", "001"),
            ("Bob", "Johnson", "14"),
            ("Alice", "Brown", "014"),
            ("Charlie", "Wilson", "99"),
        ]

        for first_name, last_name, car_number in test_data:
            self.cursor.execute(
                """
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, car_make, car_model, car_year, car_color, reserved_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    first_name,
                    last_name,
                    car_number,
                    "Test",
                    "Model",
                    2020,
                    "Red",
                    None,
                    "Test note",
                ),
            )

        self.db_conn.commit()

        # Now simulate the migration by updating sort_order
        self.cursor.execute("SELECT id, car_number FROM car_registrations")
        registrations = self.cursor.fetchall()

        for reg_id, car_number in registrations:
            try:
                sort_order = int(car_number)
            except ValueError:
                sort_order = 0

            self.cursor.execute(
                """
                UPDATE car_registrations 
                SET sort_order = ? 
                WHERE id = ?
            """,
                (sort_order, reg_id),
            )

        self.db_conn.commit()

        # Verify the migration
        self.cursor.execute(
            "SELECT car_number, sort_order FROM car_registrations ORDER BY id"
        )
        results = self.cursor.fetchall()

        expected_sort_orders = [1, 1, 14, 14, 99]  # Corresponding to test_data

        for i, (car_number, sort_order) in enumerate(results):
            self.assertEqual(
                sort_order,
                expected_sort_orders[i],
                f"sort_order mismatch for car_number '{car_number}': expected {expected_sort_orders[i]}, got {sort_order}",
            )

    def test_migrate_sort_order_invalid_numbers(self):
        """Test that invalid car numbers get sort_order 0"""
        # Insert test data with invalid car numbers
        test_data = [
            ("John", "Doe", "1"),
            ("Jane", "Smith", "invalid"),
            ("Bob", "Johnson", "14"),
            ("Alice", "Brown", "not-a-number"),
        ]

        for first_name, last_name, car_number in test_data:
            self.cursor.execute(
                """
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, car_make, car_model, car_year, car_color, reserved_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    first_name,
                    last_name,
                    car_number,
                    "Test",
                    "Model",
                    2020,
                    "Red",
                    None,
                    "Test note",
                ),
            )

        self.db_conn.commit()

        # Simulate migration
        self.cursor.execute("SELECT id, car_number FROM car_registrations")
        registrations = self.cursor.fetchall()

        for reg_id, car_number in registrations:
            try:
                sort_order = int(car_number)
            except ValueError:
                sort_order = 0

            self.cursor.execute(
                """
                UPDATE car_registrations 
                SET sort_order = ? 
                WHERE id = ?
            """,
                (sort_order, reg_id),
            )

        self.db_conn.commit()

        # Verify the migration
        self.cursor.execute(
            "SELECT car_number, sort_order FROM car_registrations ORDER BY id"
        )
        results = self.cursor.fetchall()

        expected_sort_orders = [
            1,
            0,
            14,
            0,
        ]  # Valid numbers get their value, invalid get 0

        for i, (car_number, sort_order) in enumerate(results):
            self.assertEqual(
                sort_order,
                expected_sort_orders[i],
                f"sort_order mismatch for car_number '{car_number}': expected {expected_sort_orders[i]}, got {sort_order}",
            )

    def test_migrate_sort_order_verification(self):
        """Test that migrated data can be sorted correctly"""
        # Insert test data and migrate
        test_data = [
            ("Charlie", "Wilson", "99"),
            ("John", "Doe", "1"),
            ("Alice", "Brown", "014"),
            ("Bob", "Johnson", "14"),
            ("Jane", "Smith", "001"),
        ]

        for first_name, last_name, car_number in test_data:
            self.cursor.execute(
                """
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, car_make, car_model, car_year, car_color, reserved_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    first_name,
                    last_name,
                    car_number,
                    "Test",
                    "Model",
                    2020,
                    "Red",
                    None,
                    "Test note",
                ),
            )

        self.db_conn.commit()

        # Migrate
        self.cursor.execute("SELECT id, car_number FROM car_registrations")
        registrations = self.cursor.fetchall()

        for reg_id, car_number in registrations:
            try:
                sort_order = int(car_number)
            except ValueError:
                sort_order = 0

            self.cursor.execute(
                """
                UPDATE car_registrations 
                SET sort_order = ? 
                WHERE id = ?
            """,
                (sort_order, reg_id),
            )

        self.db_conn.commit()

        # Verify sorting works correctly
        self.cursor.execute(
            """
            SELECT car_number, sort_order 
            FROM car_registrations 
            ORDER BY sort_order, car_number 
            LIMIT 10
        """
        )

        results = self.cursor.fetchall()

        # Expected order: 001, 1, 014, 14, 99 (alphabetical within same sort_order)
        expected_order = ["001", "1", "014", "14", "99"]

        for i, (car_number, sort_order) in enumerate(results):
            self.assertEqual(
                car_number,
                expected_order[i],
                f"Sorting order mismatch at position {i}: expected {expected_order[i]}, got {car_number}",
            )


if __name__ == "__main__":
    unittest.main()
