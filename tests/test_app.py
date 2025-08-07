import unittest
import tempfile
import os
import sqlite3
from datetime import datetime
from app import (
    app,
    init_db,
    calculate_expiration_date,
    update_usage_for_registration,
    remove_usage_for_registration,
)


class NordSternCarNumbersTestCase(unittest.TestCase):
    """Test cases for Nord Stern Car Numbers application"""

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
            # Insert some test data
            self._insert_test_data()

    def tearDown(self):
        """Clean up after each test"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _insert_test_data(self):
        """Insert test data into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Test data with different car number formats and usage information
        test_data = [
            # (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, reserved_for_year, status, notes, last_usage_year, expiration_date, usage_count, is_active_in_period)
            (
                "John",
                "Doe",
                "4",
                4,
                "BMW",
                "M3",
                2020,
                "Black",
                "2022-01-15",
                2025,
                "Active",
                "Test registration 1",
                2025,
                "2028-01-01",
                1,
                True,
            ),
            (
                "Jane",
                "Smith",
                "04",
                4,
                "Porsche",
                "911",
                2021,
                "Red",
                "2023-01-16",
                2025,
                "Active",
                "Test registration 2",
                None,
                "2026-01-01",
                0,
                True,
            ),
            (
                "Bob",
                "Johnson",
                "004",
                4,
                "Audi",
                "RS4",
                2019,
                "Silver",
                "2020-01-10",
                2025,
                "Retired",
                "Test registration 3",
                2024,
                "2027-01-01",
                1,
                True,
            ),
            (
                "Alice",
                "Brown",
                "104",
                104,
                "BMW",
                "M2",
                2022,
                "Blue",
                "2021-01-17",
                2025,
                "Active",
                "Test registration 4",
                None,
                "2024-01-01",
                0,
                False,
            ),
            (
                "Charlie",
                "Wilson",
                "105",
                105,
                "Porsche",
                "Cayman",
                2020,
                "White",
                "2024-01-18",
                2025,
                "Active",
                "Test registration 5",
                2025,
                "2028-01-01",
                2,
                True,
            ),
            (
                "Sarah",
                "Johnson",
                "106",
                106,
                "Audi",
                "TT RS",
                2021,
                "Gray",
                "2022-01-19",
                2025,
                "Active",
                "Test registration 6",
                None,
                "2025-01-01",
                0,
                True,
            ),
            (
                "Michael",
                "Chen",
                "107",
                107,
                "BMW",
                "M4",
                2023,
                "Green",
                "2023-01-20",
                2025,
                "Active",
                "Test registration 7",
                2025,
                "2028-01-01",
                1,
                True,
            ),
            (
                "Lisa",
                "Martinez",
                "108",
                108,
                "Porsche",
                "Boxster",
                2018,
                "Yellow",
                "2020-01-21",
                2025,
                "Active",
                "Test registration 8",
                None,
                "2023-01-01",
                0,
                False,
            ),
            (
                "David",
                "Thompson",
                "109",
                109,
                "Audi",
                "S4",
                2020,
                "White",
                "2021-01-22",
                2025,
                "Active",
                "Test registration 9",
                2024,
                "2027-01-01",
                1,
                True,
            ),
            (
                "Emma",
                "Davis",
                "110",
                110,
                "BMW",
                "M5",
                2021,
                "Blue",
                "2022-01-23",
                2025,
                "Active",
                "Test registration 10",
                None,
                "2025-01-01",
                0,
                True,
            ),
            (
                "Leading",
                "Zero",
                "022",
                22,
                "Porsche",
                "GT4",
                2022,
                "Red",
                "2022-12-21",
                2025,
                "Active",
                "Test with leading zero",
                2025,
                "2028-01-01",
                1,
                True,
            ),
        ]

        for data in test_data:
            cursor.execute(
                """
                INSERT INTO car_registrations 
                (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, reserved_for_year, status, notes, last_usage_year, expiration_date, usage_count, is_active_in_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                data,
            )

        conn.commit()
        conn.close()

    def test_home_page(self):
        """Test that home page loads successfully"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nord Stern Car Numbers", response.data)
        self.assertIn(b"Drivers Education Car Number Management", response.data)

    def test_search_page_empty(self):
        """Test search page with no query"""
        response = self.client.get("/search")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Search & Manage Car Numbers", response.data)

    def test_search_by_name(self):
        """Test search by driver name"""
        response = self.client.get("/search?q=John")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"John Doe", response.data)
        self.assertNotIn(b"Jane Smith", response.data)

    def test_search_by_car_number(self):
        """Test search by car number"""
        response = self.client.get("/search?number=4")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"John Doe", response.data)
        self.assertIn(b"4", response.data)

    def test_search_show_all(self):
        """Test search with show_all parameter"""
        response = self.client.get("/search?q=&show_all=1")
        self.assertEqual(response.status_code, 200)
        # Should show all registrations
        self.assertIn(b"John Doe", response.data)
        self.assertIn(b"Jane Smith", response.data)
        self.assertIn(b"Bob Johnson", response.data)

    def test_add_registration_page(self):
        """Test add registration page loads"""
        response = self.client.get("/add")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add New Car Number Registration", response.data)

    def test_add_registration_success(self):
        """Test successful registration addition"""
        data = {
            "first_name": "Test",
            "last_name": "User",
            "car_number": "999",
            "car_make": "BMW",
            "car_model": "M3",
            "car_year": "2023",
            "car_color": "Black",
            "reserved_date": "2023-01-01",
            "notes": "Test registration",
        }

        response = self.client.post("/add", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration added successfully", response.data)

        # Verify the registration was added with correct usage fields
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count, expiration_date, is_active_in_period FROM car_registrations WHERE car_number = ?",
            ("999",),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertIsNone(result[0])  # last_usage_year should be None
        self.assertEqual(result[1], 0)  # usage_count should be 0
        self.assertIsNotNone(result[2])  # expiration_date should be set
        self.assertTrue(result[3])  # is_active_in_period should be True

    def test_add_registration_duplicate_number(self):
        """Test adding registration with duplicate car number"""
        data = {
            "first_name": "Test",
            "last_name": "User",
            "car_number": "4",  # Already exists
            "car_make": "BMW",
            "car_model": "M3",
            "car_year": "2023",
            "car_color": "Black",
            "reserved_date": "2023-01-01",
            "notes": "Test registration",
        }

        response = self.client.post("/add", data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Car number 004 is already taken", response.data)

    def test_add_registration_missing_required_fields(self):
        """Test adding registration with missing required fields"""
        data = {
            "first_name": "",  # Missing
            "last_name": "User",
            "car_number": "999",
            "car_make": "BMW",
            "car_model": "M3",
            "car_year": "2023",
            "car_color": "Black",
            "reserved_date": "2023-01-01",
            "notes": "Test registration",
        }

        response = self.client.post("/add", data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"First name, last name, and car number are required", response.data
        )

    def test_edit_registration_page(self):
        """Test edit registration page loads"""
        response = self.client.get("/edit/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Edit Car Number Registration", response.data)

    def test_edit_registration_success(self):
        """Test successful registration editing"""
        data = {
            "first_name": "John",
            "last_name": "Doe Updated",
            "car_number": "101",
            "car_make": "BMW Updated",
            "car_model": "M3",
            "car_year": "2020",
            "car_color": "Black",
            "reserved_date": "2022-01-15",
            "status": "Active",
            "notes": "Updated test registration",
        }

        response = self.client.post("/edit/1", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration updated successfully", response.data)

    def test_edit_registration_not_found(self):
        """Test editing non-existent registration"""
        response = self.client.get("/edit/999")
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_delete_registration(self):
        """Test registration deletion"""
        response = self.client.post("/delete/1", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"deleted successfully", response.data)

    def test_api_check_number_available(self):
        """Test API check for available car number"""
        response = self.client.get("/api/check_number/999")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["available"])

    def test_api_check_number_taken(self):
        """Test API check for taken car number"""
        response = self.client.get("/api/check_number/4")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["available"])
        self.assertIn("John Doe", data["driver"])

    def test_stats_page(self):
        """Test statistics page loads"""
        response = self.client.get("/stats")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Statistics", response.data)

    def test_car_number_leading_zeros(self):
        """Test car number formatting with leading zeros"""
        data = {
            "first_name": "Test",
            "last_name": "User",
            "car_number": "1",  # Should be formatted to '001'
            "car_make": "BMW",
            "car_model": "M3",
            "car_year": "2023",
            "car_color": "Black",
            "reserved_date": "2023-01-01",
            "notes": "Test registration",
        }

        response = self.client.post("/add", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration added successfully", response.data)

        # Verify the car number was formatted correctly
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT car_number FROM car_registrations WHERE first_name = ? AND last_name = ?",
            ("Test", "User"),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], "001")

    def test_search_with_leading_zeros(self):
        """Test search with leading zeros in car number"""
        # Search for '1' should find '001'
        response = self.client.get("/search?number=1")
        self.assertEqual(response.status_code, 200)
        # Should find the registration with car number '001'

    def test_flexible_car_number_search(self):
        """Test the new flexible car number search functionality"""
        # Test searching for "4" - should find all variations
        response = self.client.get("/search?number=4")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"John Doe", response.data)  # "4"
        self.assertIn(b"Jane Smith", response.data)  # "04"
        self.assertIn(b"Bob Johnson", response.data)  # "004"

    def test_flexible_car_number_search_with_leading_zero(self):
        """Test searching with leading zero format"""
        # Test searching for "04" - should find all variations
        response = self.client.get("/search?number=04")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"John Doe", response.data)  # "4"
        self.assertIn(b"Jane Smith", response.data)  # "04"
        self.assertIn(b"Bob Johnson", response.data)  # "004"

    def test_flexible_car_number_search_with_two_leading_zeros(self):
        """Test searching with two leading zeros format"""
        # Test searching for "004" - should find all variations
        response = self.client.get("/search?number=004")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"John Doe", response.data)  # "4"
        self.assertIn(b"Jane Smith", response.data)  # "04"
        self.assertIn(b"Bob Johnson", response.data)  # "004"

    def test_flexible_car_number_search_invalid_number(self):
        """Test searching with invalid number format"""
        # Test searching for "abc" - should handle gracefully
        response = self.client.get("/search?number=abc")
        self.assertEqual(response.status_code, 200)
        # Should not find any results since it's not a valid number
        self.assertNotIn(b"John Doe", response.data)
        self.assertNotIn(b"Jane Smith", response.data)
        self.assertNotIn(b"Bob Johnson", response.data)

    def test_invalid_car_number(self):
        """Test invalid car number input"""
        data = {
            "first_name": "Test",
            "last_name": "User",
            "car_number": "abc",  # Invalid
            "car_make": "BMW",
            "car_model": "M3",
            "car_year": "2023",
            "car_color": "Black",
            "reserved_date": "2023-01-01",
            "notes": "Test registration",
        }

        response = self.client.post("/add", data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Car number and year must be valid numbers", response.data)

    def test_invalid_year(self):
        """Test invalid year input"""
        data = {
            "first_name": "Test",
            "last_name": "User",
            "car_number": "999",
            "car_make": "BMW",
            "car_model": "M3",
            "car_year": "abc",  # Invalid
            "car_color": "Black",
            "reserved_date": "2023-01-01",
            "notes": "Test registration",
        }

        response = self.client.post("/add", data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Car number and year must be valid numbers", response.data)

    def test_negative_car_number(self):
        """Test negative car number (should be accepted and formatted)"""
        data = {
            "first_name": "Test",
            "last_name": "User",
            "car_number": "-1",  # Negative number
            "car_make": "BMW",
            "car_model": "M3",
            "car_year": "2023",
            "car_color": "Black",
            "reserved_date": "2023-01-01",
            "notes": "Test registration",
        }

        response = self.client.post("/add", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration added successfully", response.data)

    def test_record_usage_api(self):
        """Test recording usage via API"""
        response = self.client.post(
            "/api/record_usage/2", data={"usage_year": "2025"}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Usage recorded successfully for 2025", response.data)

        # Verify usage was recorded correctly
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count FROM car_registrations WHERE id = ?",
            (2,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], 2025)  # last_usage_year
        self.assertEqual(result[1], 1)  # usage_count

    def test_record_usage_api_default_year(self):
        """Test recording usage with default year (current year)"""
        current_year = datetime.now().year
        response = self.client.post(
            "/api/record_usage/2", data={}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f"Usage recorded successfully for {current_year}".encode(), response.data
        )

    def test_remove_usage_api(self):
        """Test removing usage via API"""
        # First record some usage
        self.client.post("/api/record_usage/2", data={"usage_year": "2025"})

        # Then remove it
        response = self.client.post("/api/remove_usage/2", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Usage removed successfully", response.data)

        # Verify usage was removed
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count FROM car_registrations WHERE id = ?",
            (2,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertIsNone(result[0])  # last_usage_year should be None
        self.assertEqual(result[1], 0)  # usage_count should be 0

    def test_record_usage_nonexistent_registration(self):
        """Test recording usage for non-existent registration"""
        response = self.client.post(
            "/api/record_usage/999", data={"usage_year": "2025"}, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Failed to record usage", response.data)

    def test_remove_usage_nonexistent_registration(self):
        """Test removing usage for non-existent registration"""
        response = self.client.post("/api/remove_usage/999", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Failed to remove usage", response.data)

    def test_calculate_expiration_date_with_usage(self):
        """Test expiration date calculation with usage"""
        expiration_date, is_active = calculate_expiration_date("2022-01-15", 2025)
        self.assertEqual(expiration_date, "2028-01-01")
        self.assertTrue(is_active)

    def test_calculate_expiration_date_without_usage(self):
        """Test expiration date calculation without usage"""
        expiration_date, is_active = calculate_expiration_date("2022-01-15", None)
        self.assertEqual(expiration_date, "2025-01-01")
        self.assertTrue(is_active)

    def test_calculate_expiration_date_expired(self):
        """Test expiration date calculation for expired registration"""
        expiration_date, is_active = calculate_expiration_date("2020-01-15", None)
        self.assertEqual(expiration_date, "2023-01-01")
        self.assertFalse(is_active)  # Should be expired

    def test_update_usage_for_registration(self):
        """Test updating usage for registration"""
        success = update_usage_for_registration(2, 2025)
        self.assertTrue(success)

        # Verify the update
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count FROM car_registrations WHERE id = ?",
            (2,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertEqual(result[0], 2025)
        self.assertEqual(result[1], 1)

    def test_remove_usage_for_registration(self):
        """Test removing usage for registration"""
        # First add some usage
        update_usage_for_registration(2, 2025)

        # Then remove it
        success = remove_usage_for_registration(2)
        self.assertTrue(success)

        # Verify the removal
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_usage_year, usage_count FROM car_registrations WHERE id = ?",
            (2,),
        )
        result = cursor.fetchone()
        conn.close()

        self.assertIsNone(result[0])
        self.assertEqual(result[1], 0)

    def test_database_structure(self):
        """Test that database has correct structure after cleanup"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check that last_usage_date column doesn't exist
        cursor.execute("PRAGMA table_info(car_registrations)")
        columns = [col[1] for col in cursor.fetchall()]

        self.assertNotIn("last_usage_date", columns)
        self.assertIn("last_usage_year", columns)
        self.assertIn("expiration_date", columns)
        self.assertIn("usage_count", columns)
        self.assertIn("is_active_in_period", columns)
        self.assertIn("sort_order", columns)

        conn.close()

    def test_search_results_usage_display(self):
        """Test that search results show usage information correctly"""
        response = self.client.get("/search?q=&show_all=1")
        self.assertEqual(response.status_code, 200)

        # Should show usage information for registrations with usage
        self.assertIn(b"Last: 2025", response.data)
        self.assertIn(b"Count: 1", response.data)
        self.assertIn(b"No usage", response.data)

    def test_search_results_expiration_display(self):
        """Test that search results show expiration dates correctly"""
        response = self.client.get("/search?q=&show_all=1")
        self.assertEqual(response.status_code, 200)

        # Should show expiration dates in YYYY format (as displayed in UI)
        self.assertIn(b"2028", response.data)  # YYYY format
        self.assertIn(b"2026", response.data)  # YYYY format

    def test_search_results_status_display(self):
        """Test that search results show status correctly"""
        response = self.client.get("/search?q=&show_all=1")
        self.assertEqual(response.status_code, 200)

        # Should show different status badges
        self.assertIn(b"Active", response.data)
        self.assertIn(b"Retired", response.data)


if __name__ == "__main__":
    unittest.main()
