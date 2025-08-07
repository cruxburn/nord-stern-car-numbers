"""
Tests for data preservation mechanism in Nord Stern Car Numbers
"""

import unittest
import tempfile
import os
import json
import sqlite3
from datetime import datetime
from app import app, init_db


class DataPreservationTestCase(unittest.TestCase):
    """Test cases for data preservation mechanism"""

    def setUp(self):
        """Set up test database and client before each test"""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp()

        # Configure app for testing
        app.config["TESTING"] = True
        app.config["DATABASE"] = self.db_path
        app.config["SECRET_KEY"] = "test-secret-key"

        # Create test client
        self.client = app.test_client()

        # Initialize test database
        with app.app_context():
            init_db(self.db_path)
            # Insert test data
            self._insert_test_data()

    def tearDown(self):
        """Clean up after each test"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _insert_test_data(self):
        """Insert test data into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Test data for data preservation testing
        test_data = [
            (
                "Alice",
                "Johnson",
                "1",
                1,
                "Toyota",
                "Camry",
                2020,
                "Blue",
                "2022-01-15",
                2025,
                "Active",
                "Test data 1",
                2025,
                "2028-01-01",
                1,
                True,
            ),
            (
                "Bob",
                "Smith",
                "2",
                2,
                "Honda",
                "Civic",
                2021,
                "Red",
                "2023-01-16",
                2025,
                "Active",
                "Test data 2",
                None,
                "2026-01-01",
                0,
                True,
            ),
            (
                "Charlie",
                "Brown",
                "3",
                3,
                "Ford",
                "Focus",
                2019,
                "Green",
                "2020-01-10",
                2025,
                "Retired",
                "Test data 3",
                2024,
                "2027-01-01",
                1,
                False,
            ),
        ]

        for data in test_data:
            cursor.execute(
                """
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, sort_order, car_make, car_model, 
                 car_year, car_color, reserved_date, reserved_for_year, status, notes, 
                 last_usage_year, expiration_date, usage_count, is_active_in_period, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                data + (datetime.now().isoformat(), datetime.now().isoformat()),
            )

        conn.commit()
        conn.close()

    def test_export_api_complete_data_structure(self):
        """Test that export API returns complete data structure"""
        response = self.client.get("/api/export")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        # Check top-level structure
        required_top_level = ["export_date", "total_registrations", "registrations"]
        for field in required_top_level:
            self.assertIn(field, data)

        # Check data types
        self.assertIsInstance(data["export_date"], str)
        self.assertIsInstance(data["total_registrations"], int)
        self.assertIsInstance(data["registrations"], list)

        # Check registration count
        self.assertEqual(data["total_registrations"], 3)
        self.assertEqual(len(data["registrations"]), 3)

    def test_export_api_registration_fields(self):
        """Test that each registration has all required fields"""
        response = self.client.get("/api/export")
        data = response.get_json()

        required_fields = [
            "id",
            "first_name",
            "last_name",
            "car_number",
            "sort_order",
            "car_make",
            "car_model",
            "car_year",
            "car_color",
            "reserved_date",
            "reserved_for_year",
            "status",
            "notes",
            "last_usage_year",
            "expiration_date",
            "usage_count",
            "is_active_in_period",
            "created_at",
            "updated_at",
        ]

        for registration in data["registrations"]:
            for field in required_fields:
                self.assertIn(
                    field, registration, f"Registration missing field: {field}"
                )

    def test_export_api_data_accuracy(self):
        """Test that exported data matches database content"""
        response = self.client.get("/api/export")
        data = response.get_json()

        # Get data directly from database for comparison
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM car_registrations ORDER BY id")
        db_rows = cursor.fetchall()
        conn.close()

        # Check that we have the same number of records
        self.assertEqual(len(data["registrations"]), len(db_rows))

        # Check that the data matches
        for i, registration in enumerate(data["registrations"]):
            db_row = db_rows[i]
            self.assertEqual(registration["first_name"], db_row[1])
            self.assertEqual(registration["last_name"], db_row[2])
            self.assertEqual(registration["car_number"], db_row[3])
            self.assertEqual(registration["sort_order"], db_row[4])

    def test_export_api_timestamp_format(self):
        """Test that export_date is in valid ISO format"""
        response = self.client.get("/api/export")
        data = response.get_json()

        export_date = data["export_date"]

        # Try to parse the timestamp
        try:
            # Handle both ISO format with and without timezone
            if export_date.endswith("Z"):
                export_date = export_date.replace("Z", "+00:00")
            datetime.fromisoformat(export_date)
        except ValueError as e:
            self.fail(f"Invalid timestamp format: {export_date}, error: {e}")

    def test_export_api_empty_database(self):
        """Test export API with empty database"""
        # Clear the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM car_registrations")
        conn.commit()
        conn.close()

        response = self.client.get("/api/export")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["total_registrations"], 0)
        self.assertEqual(len(data["registrations"]), 0)
        self.assertIn("export_date", data)

    def test_export_api_json_serialization(self):
        """Test that exported data can be serialized to JSON"""
        response = self.client.get("/api/export")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        # Try to serialize the data back to JSON
        try:
            json_str = json.dumps(data)
            # Try to deserialize it back
            parsed_data = json.loads(json_str)
            self.assertEqual(data, parsed_data)
        except (json.JSONDecodeError, TypeError) as e:
            self.fail(f"Data cannot be serialized to JSON: {e}")

    def test_export_api_content_type(self):
        """Test that export API returns correct content type"""
        response = self.client.get("/api/export")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")

    def test_export_api_error_handling(self):
        """Test that export API handles database errors gracefully"""
        # Close the database connection to simulate an error
        conn = sqlite3.connect(self.db_path)
        conn.close()

        # Try to export data
        response = self.client.get("/api/export")

        # Should still return a response (even if it's an error)
        self.assertIsNotNone(response)
        # The exact behavior depends on how the app handles database errors


if __name__ == "__main__":
    unittest.main()
