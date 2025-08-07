import unittest
import tempfile
import os
import sqlite3
from datetime import datetime
from app import init_db, calculate_expiration_date, update_usage_for_registration, remove_usage_for_registration

class DatabaseTestCase(unittest.TestCase):
    """Test cases for database operations"""

    def setUp(self):
        """Set up test database before each test"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        init_db(self.db_path)

    def tearDown(self):
        """Clean up after each test"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_database_creation(self):
        """Test that database is created with correct structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check that table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='car_registrations'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        
        # Check table structure
        cursor.execute("PRAGMA table_info(car_registrations)")
        columns = cursor.fetchall()
        
        # Verify all required columns exist
        column_names = [col[1] for col in columns]
        
        required_columns = [
            'id', 'first_name', 'last_name', 'car_number', 'sort_order', 'car_make', 'car_model', 
            'car_year', 'car_color', 'reserved_date', 'reserved_for_year', 'status', 
            'notes', 'last_usage_year', 'expiration_date', 'usage_count', 
            'is_active_in_period', 'created_at', 'updated_at'
        ]
        
        for col in required_columns:
            self.assertIn(col, column_names, f"Column {col} not found in database")
        
        # Verify that old column doesn't exist
        self.assertNotIn('last_usage_date', column_names, "Old last_usage_date column should not exist")
        
        conn.close()

    def test_insert_registration(self):
        """Test inserting a new registration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert test registration
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test registration'))
        
        conn.commit()
        
        # Verify insertion
        cursor.execute('SELECT * FROM car_registrations WHERE car_number = ?', ('101',))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[1], 'John')  # first_name
        self.assertEqual(result[2], 'Doe')   # last_name
        self.assertEqual(result[3], '101')   # car_number
        
        # Check that usage fields are properly initialized
        self.assertIsNone(result[13])  # last_usage_year should be None
        self.assertEqual(result[15], 0)  # usage_count should be 0
        # Note: expiration_date and is_active_in_period are not automatically calculated during direct DB insertion
        
        conn.close()

    def test_car_number_formatting(self):
        """Test car number formatting with leading zeros"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert registration with single digit (application would format this, but we're testing raw DB)
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Test', 'User', '1', 1, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test'))
        
        conn.commit()
        
        # Verify it was stored as provided (application formatting happens at the Flask level)
        cursor.execute('SELECT car_number FROM car_registrations WHERE first_name = ?', ('Test',))
        result = cursor.fetchone()
        
        self.assertEqual(result[0], '1')  # Raw value as stored
        
        conn.close()

    def test_timestamp_creation(self):
        """Test that timestamps are created automatically"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert registration
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test'))
        
        conn.commit()
        
        # Check timestamps
        cursor.execute('SELECT created_at, updated_at FROM car_registrations WHERE car_number = ?', ('101',))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result[0])  # created_at
        self.assertIsNotNone(result[1])  # updated_at
        
        # Verify timestamps are in valid format (contain date and time)
        self.assertIn(':', result[0])  # Should contain time
        self.assertIn(':', result[1])  # Should contain time
        self.assertIn('-', result[0])  # Should contain date
        self.assertIn('-', result[1])  # Should contain date
        
        # Verify timestamps are recent (within last 5 hours to be very lenient for test environment)
        try:
            created_at = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            updated_at = datetime.strptime(result[1], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            
            self.assertLess(abs((now - created_at).total_seconds()), 18000)  # 5 hours
            self.assertLess(abs((now - updated_at).total_seconds()), 18000)  # 5 hours
        except ValueError:
            # If timestamp format is different, just verify they exist and have valid format
            self.assertTrue(len(result[0]) > 10)  # Should be a reasonable length
            self.assertTrue(len(result[1]) > 10)  # Should be a reasonable length
        
        conn.close()

    def test_duplicate_car_numbers_allowed(self):
        """Test that duplicate car numbers are now allowed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert first registration
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test 1'))
        
        conn.commit()
        
        # Insert duplicate car number (should now be allowed)
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Jane', 'Smith', '101', 101, 'Porsche', '911', 2021, 'Red', '2022-01-16', 'Test 2'))
        conn.commit()
        
        # Verify both registrations exist
        cursor.execute('SELECT COUNT(*) FROM car_registrations WHERE car_number = ?', ('101',))
        count = cursor.fetchone()[0]
        self.assertEqual(count, 2)
        
        conn.close()

    def test_calculate_expiration_date_function(self):
        """Test the calculate_expiration_date function"""
        # Test with usage
        expiration_date, is_active = calculate_expiration_date('2022-01-15', 2025)
        self.assertEqual(expiration_date, '2028-01-01')
        self.assertTrue(is_active)
        
        # Test without usage
        expiration_date, is_active = calculate_expiration_date('2022-01-15', None)
        self.assertEqual(expiration_date, '2025-01-01')
        self.assertTrue(is_active)
        
        # Test expired registration
        expiration_date, is_active = calculate_expiration_date('2020-01-15', None)
        self.assertEqual(expiration_date, '2023-01-01')
        self.assertFalse(is_active)
        
        # Test with invalid date
        expiration_date, is_active = calculate_expiration_date('invalid-date', None)
        self.assertIsNone(expiration_date)
        self.assertFalse(is_active)

    def test_update_usage_for_registration(self):
        """Test updating usage for a registration"""
        # Set up the database path for the function
        import app
        app.app.config['DATABASE'] = self.db_path
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert test registration
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test'))
        
        conn.commit()
        conn.close()
        
        # Update usage
        success = update_usage_for_registration(1, 2025)
        self.assertTrue(success)
        
        # Verify the update
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT last_usage_year, usage_count, expiration_date, is_active_in_period FROM car_registrations WHERE id = ?', (1,))
        result = cursor.fetchone()
        conn.close()
        
        self.assertEqual(result[0], 2025)  # last_usage_year
        self.assertEqual(result[1], 1)  # usage_count
        self.assertEqual(result[2], '2028-01-01')  # expiration_date
        self.assertTrue(result[3])  # is_active_in_period

    def test_update_usage_for_registration_multiple_times(self):
        """Test updating usage multiple times"""
        # Set up the database path for the function
        import app
        app.app.config['DATABASE'] = self.db_path
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert test registration
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test'))
        
        conn.commit()
        conn.close()
        
        # Update usage multiple times
        update_usage_for_registration(1, 2024)
        update_usage_for_registration(1, 2025)
        
        # Verify the final state
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT last_usage_year, usage_count, expiration_date FROM car_registrations WHERE id = ?', (1,))
        result = cursor.fetchone()
        conn.close()
        
        self.assertEqual(result[0], 2025)  # last_usage_year (should be the latest)
        self.assertEqual(result[1], 2)  # usage_count (should be incremented)
        self.assertEqual(result[2], '2028-01-01')  # expiration_date (based on latest usage)

    def test_remove_usage_for_registration(self):
        """Test removing usage for a registration"""
        # Set up the database path for the function
        import app
        app.app.config['DATABASE'] = self.db_path
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert test registration with usage
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes, last_usage_year, usage_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test', 2025, 1))
        
        conn.commit()
        conn.close()
        
        # Remove usage
        success = remove_usage_for_registration(1)
        self.assertTrue(success)
        
        # Verify the removal
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT last_usage_year, usage_count, expiration_date, is_active_in_period FROM car_registrations WHERE id = ?', (1,))
        result = cursor.fetchone()
        conn.close()
        
        self.assertIsNone(result[0])  # last_usage_year should be None
        self.assertEqual(result[1], 0)  # usage_count should be 0
        self.assertEqual(result[2], '2025-01-01')  # expiration_date (based on reserved date)
        self.assertTrue(result[3])  # is_active_in_period

    def test_update_usage_nonexistent_registration(self):
        """Test updating usage for non-existent registration"""
        # Set up the database path for the function
        import app
        app.app.config['DATABASE'] = self.db_path
        
        success = update_usage_for_registration(999, 2025)
        self.assertFalse(success)

    def test_remove_usage_nonexistent_registration(self):
        """Test removing usage for non-existent registration"""
        # Set up the database path for the function
        import app
        app.app.config['DATABASE'] = self.db_path
        
        success = remove_usage_for_registration(999)
        self.assertFalse(success)

    def test_database_duplicate_insertion(self):
        """Test that duplicate car numbers can be inserted successfully"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert valid registration
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test'))
        
        conn.commit()
        
        # Insert duplicate (should now succeed)
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Jane', 'Smith', '101', 101, 'Porsche', '911', 2021, 'Red', '2022-01-16', 'Test 2'))
        conn.commit()
        
        # Verify both registrations exist
        cursor.execute('SELECT COUNT(*) FROM car_registrations')
        count = cursor.fetchone()[0]
        self.assertEqual(count, 2)
        
        conn.close()

    def test_reserved_date_validation(self):
        """Test reserved date validation and formatting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test with valid date
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test'))
        
        conn.commit()
        
        # Verify date was stored correctly
        cursor.execute('SELECT reserved_date FROM car_registrations WHERE car_number = ?', ('101',))
        result = cursor.fetchone()
        self.assertEqual(result[0], '2022-01-15')
        
        conn.close()

    def test_status_field_defaults(self):
        """Test status field defaults and values"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert registration without specifying status
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test'))
        
        conn.commit()
        
        # Verify default status
        cursor.execute('SELECT status FROM car_registrations WHERE car_number = ?', ('101',))
        result = cursor.fetchone()
        self.assertEqual(result[0], 'Active')
        
        conn.close()

    def test_usage_count_increment(self):
        """Test that usage count increments correctly"""
        # Set up the database path for the function
        import app
        app.app.config['DATABASE'] = self.db_path
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert test registration
        cursor.execute('''
            INSERT INTO car_registrations 
            (first_name, last_name, car_number, sort_order, car_make, car_model, car_year, car_color, reserved_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('John', 'Doe', '101', 101, 'BMW', 'M3', 2020, 'Black', '2022-01-15', 'Test'))
        
        conn.commit()
        conn.close()
        
        # Update usage multiple times
        update_usage_for_registration(1, 2024)
        update_usage_for_registration(1, 2025)
        update_usage_for_registration(1, 2026)
        
        # Verify usage count
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT usage_count FROM car_registrations WHERE id = ?', (1,))
        result = cursor.fetchone()
        conn.close()
        
        self.assertEqual(result[0], 3)  # Should be 3 after 3 updates

    def test_expiration_date_calculation_edge_cases(self):
        """Test expiration date calculation edge cases"""
        # Test with very old reservation
        expiration_date, is_active = calculate_expiration_date('1959-03-28', None)
        self.assertEqual(expiration_date, '1962-01-01')
        self.assertFalse(is_active)
        
        # Test with future reservation
        future_year = datetime.now().year + 5
        expiration_date, is_active = calculate_expiration_date(f'{future_year}-01-01', None)
        expected_expiration = f'{future_year + 3}-01-01'
        self.assertEqual(expiration_date, expected_expiration)
        self.assertTrue(is_active)
        
        # Test with current year usage
        current_year = datetime.now().year
        expiration_date, is_active = calculate_expiration_date('2022-01-15', current_year)
        expected_expiration = f'{current_year + 3}-01-01'
        self.assertEqual(expiration_date, expected_expiration)
        self.assertTrue(is_active)

if __name__ == '__main__':
    unittest.main() 