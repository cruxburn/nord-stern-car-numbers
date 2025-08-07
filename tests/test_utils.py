import unittest
import tempfile
import os
import sqlite3
from datetime import datetime
from app import (
    init_db,
    calculate_expiration_date,
    update_usage_for_registration,
    remove_usage_for_registration,
)


class UtilsTestCase(unittest.TestCase):
    """Test cases for utility functions"""

    def setUp(self):
        """Set up test database before each test"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        init_db(self.db_path)

    def tearDown(self):
        """Clean up after each test"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_calculate_expiration_date_basic(self):
        """Test basic expiration date calculation"""
        # Test with usage
        expiration_date, is_active = calculate_expiration_date("2022-01-15", 2025)
        self.assertEqual(expiration_date, "2028-01-01")
        self.assertTrue(is_active)

        # Test without usage
        expiration_date, is_active = calculate_expiration_date("2022-01-15", None)
        self.assertEqual(expiration_date, "2025-01-01")
        self.assertTrue(is_active)

    def test_calculate_expiration_date_edge_cases(self):
        """Test expiration date calculation edge cases"""
        # Test with very old reservation
        expiration_date, is_active = calculate_expiration_date("1959-03-28", None)
        self.assertEqual(expiration_date, "1962-01-01")
        self.assertFalse(is_active)

        # Test with future reservation
        future_year = datetime.now().year + 5
        expiration_date, is_active = calculate_expiration_date(
            f"{future_year}-01-01", None
        )
        expected_expiration = f"{future_year + 3}-01-01"
        self.assertEqual(expiration_date, expected_expiration)
        self.assertTrue(is_active)

        # Test with current year usage
        current_year = datetime.now().year
        expiration_date, is_active = calculate_expiration_date(
            "2022-01-15", current_year
        )
        expected_expiration = f"{current_year + 3}-01-01"
        self.assertEqual(expiration_date, expected_expiration)
        self.assertTrue(is_active)

    def test_calculate_expiration_date_invalid_inputs(self):
        """Test expiration date calculation with invalid inputs"""
        # Test with invalid date format
        expiration_date, is_active = calculate_expiration_date("invalid-date", None)
        self.assertIsNone(expiration_date)
        self.assertFalse(is_active)

        # Test with None date
        expiration_date, is_active = calculate_expiration_date(None, None)
        self.assertIsNone(expiration_date)
        self.assertFalse(is_active)

        # Test with empty string
        expiration_date, is_active = calculate_expiration_date("", None)
        self.assertIsNone(expiration_date)
        self.assertFalse(is_active)

    def test_calculate_expiration_date_different_formats(self):
        """Test expiration date calculation with different date formats"""
        # Test with different valid date formats
        test_cases = [
            (
                "2022-01-15",
                2025,
                "2028-01-01",
            ),  # 2025 usage extends 2025 expiration to 2028
            (
                "2023-06-30",
                2024,
                "2029-01-01",
            ),  # 2024 usage extends 2026 expiration to 2029
            (
                "2021-12-31",
                2026,
                "2030-01-01",
            ),  # 2026 usage extends 2024 expiration to 2030
        ]

        for reserved_date, usage_year, expected_expiration in test_cases:
            expiration_date, is_active = calculate_expiration_date(
                reserved_date, usage_year
            )
            self.assertEqual(expiration_date, expected_expiration)
            self.assertTrue(is_active)

    def test_update_usage_for_registration_basic(self):
        """Test basic usage update functionality"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        # Insert test registration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "John",
                "Doe",
                "101",
                101,
                "BMW",
                "M3",
                2020,
                "Black",
                "2022-01-15",
                "Test",
            ),
        )
        conn.commit()
        conn.close()

        # Update usage
        success = update_usage_for_registration(1, 2025)
        self.assertTrue(success)

        # Verify the update
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count, expiration_date, is_active_in_period FROM car_registrations WHERE id = ?",
            (1,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], 2025)  # last_usage_year
        self.assertEqual(result[1], 1)  # usage_count
        self.assertEqual(result[2], "2028-01-01")  # expiration_date
        self.assertTrue(result[3])  # is_active_in_period

    def test_update_usage_for_registration_multiple_updates(self):
        """Test multiple usage updates"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        # Insert test registration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "John",
                "Doe",
                "101",
                101,
                "BMW",
                "M3",
                2020,
                "Black",
                "2022-01-15",
                "Test",
            ),
        )
        conn.commit()
        conn.close()

        # Update usage multiple times
        update_usage_for_registration(1, 2024)
        update_usage_for_registration(1, 2025)
        update_usage_for_registration(1, 2026)

        # Verify final state
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count, expiration_date FROM car_registrations WHERE id = ?",
            (1,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], 2026)  # last_usage_year (should be the latest)
        self.assertEqual(result[1], 3)  # usage_count (should be incremented)
        self.assertEqual(
            result[2], "2031-01-01"
        )  # expiration_date (based on latest usage)

    def test_update_usage_for_registration_nonexistent(self):
        """Test updating usage for non-existent registration"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        success = update_usage_for_registration(999, 2025)
        self.assertFalse(success)

    def test_update_usage_for_registration_default_year(self):
        """Test updating usage with default year (current year)"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        # Insert test registration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "John",
                "Doe",
                "101",
                101,
                "BMW",
                "M3",
                2020,
                "Black",
                "2022-01-15",
                "Test",
            ),
        )
        conn.commit()
        conn.close()

        # Update usage with default year
        current_year = datetime.now().year
        success = update_usage_for_registration(1)  # No year specified
        self.assertTrue(success)

        # Verify the update
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year FROM car_registrations WHERE id = ?", (1,)
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], current_year)

    def test_remove_usage_for_registration_basic(self):
        """Test basic usage removal functionality"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        # Insert test registration with usage
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes, last_usage_year, usage_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "John",
                "Doe",
                "101",
                101,
                "BMW",
                "M3",
                2020,
                "Black",
                "2022-01-15",
                "Test",
                2025,
                1,
            ),
        )
        conn.commit()
        conn.close()

        # Remove usage
        success = remove_usage_for_registration(1)
        self.assertTrue(success)

        # Verify the removal
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count, expiration_date, is_active_in_period FROM car_registrations WHERE id = ?",
            (1,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertIsNone(result[0])  # last_usage_year should be None
        self.assertEqual(result[1], 0)  # usage_count should be 0
        self.assertEqual(
            result[2], "2025-01-01"
        )  # expiration_date (based on reserved date)
        self.assertTrue(result[3])  # is_active_in_period

    def test_remove_usage_for_registration_nonexistent(self):
        """Test removing usage for non-existent registration"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        success = remove_usage_for_registration(999)
        self.assertFalse(success)

    def test_remove_usage_for_registration_no_usage(self):
        """Test removing usage when no usage exists"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        # Insert test registration without usage
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "John",
                "Doe",
                "101",
                101,
                "BMW",
                "M3",
                2020,
                "Black",
                "2022-01-15",
                "Test",
            ),
        )
        conn.commit()
        conn.close()

        # Remove usage (should still work)
        success = remove_usage_for_registration(1)
        self.assertTrue(success)

        # Verify state remains the same
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count FROM car_registrations WHERE id = ?",
            (1,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertIsNone(result[0])  # last_usage_year should still be None
        self.assertEqual(result[1], 0)  # usage_count should still be 0

    def test_usage_lifecycle(self):
        """Test complete usage lifecycle: add, update, remove"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        # Insert test registration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "John",
                "Doe",
                "101",
                101,
                "BMW",
                "M3",
                2020,
                "Black",
                "2022-01-15",
                "Test",
            ),
        )
        conn.commit()
        conn.close()

        # Step 1: Add usage
        success = update_usage_for_registration(1, 2024)
        self.assertTrue(success)

        # Verify usage added
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count FROM car_registrations WHERE id = ?",
            (1,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], 2024)
        self.assertEqual(result[1], 1)

        # Step 2: Update usage
        success = update_usage_for_registration(1, 2025)
        self.assertTrue(success)

        # Verify usage updated
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count FROM car_registrations WHERE id = ?",
            (1,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], 2025)
        self.assertEqual(result[1], 2)

        # Step 3: Remove usage
        success = remove_usage_for_registration(1)
        self.assertTrue(success)

        # Verify usage removed
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count FROM car_registrations WHERE id = ?",
            (1,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertIsNone(result[0])
        self.assertEqual(result[1], 0)

    def test_expiration_date_recalculation(self):
        """Test that expiration dates are recalculated correctly"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        # Insert test registration
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "John",
                "Doe",
                "101",
                101,
                "BMW",
                "M3",
                2020,
                "Black",
                "2022-01-15",
                "Test",
            ),
        )
        conn.commit()
        conn.close()

        # Check initial expiration date (no usage) - should be None since not calculated during direct DB insertion
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT expiration_date FROM car_registrations WHERE id = ?", (1,)
        )
        result = cursor.fetchone()
        conn.close()

        self.assertIsNone(
            result[0]
        )  # Not automatically calculated during direct DB insertion

        # Add usage and check expiration date
        update_usage_for_registration(1, 2025)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT expiration_date FROM car_registrations WHERE id = ?", (1,)
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], "2028-01-01")  # 3 years from usage date

        # Remove usage and check expiration date
        remove_usage_for_registration(1)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT expiration_date FROM car_registrations WHERE id = ?", (1,)
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], "2025-01-01")  # Back to 3 years from reserved date

    def test_is_active_in_period_calculation(self):
        """Test that is_active_in_period is calculated correctly"""
        # Set up the database path for the function
        import app

        app.app.config["DATABASE"] = self.db_path

        # Test with current year reservation (should be active)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        current_year = datetime.now().year
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "John",
                "Doe",
                "101",
                101,
                "BMW",
                "M3",
                2020,
                "Black",
                f"{current_year}-01-15",
                "Test",
            ),
        )
        conn.commit()
        conn.close()

        # Should be active (default value)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_active_in_period FROM car_registrations WHERE id = ?", (1,)
        )
        result = cursor.fetchone()
        conn.close()

        self.assertTrue(result[0])  # Default value is True

        # Test with old reservation (should be expired after usage update)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        old_year = current_year - 10
        cursor.execute(
            """
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "Jane",
                "Smith",
                "102",
                102,
                "Porsche",
                "911",
                2020,
                "Red",
                f"{old_year}-01-15",
                "Test",
            ),
        )
        conn.commit()
        conn.close()

        # Update usage to trigger expiration calculation - use a year that will make it expired
        update_usage_for_registration(
            2, old_year + 2
        )  # Usage 2 years after reservation

        # Should be expired (3 years from usage = old_year + 5, which is less than current_year)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_active_in_period FROM car_registrations WHERE id = ?", (2,)
        )
        result = cursor.fetchone()
        conn.close()

        self.assertFalse(result[0])  # Should be expired


if __name__ == "__main__":
    unittest.main()
