import unittest
import logging
from tx_schools_scraper import validate_school_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestSchoolDataValidation(unittest.TestCase):
    def setUp(self):
        logger.info("\n=== Starting New Test ===")
        # Sample valid school data for testing
        self.valid_school_data = {
            "School Name": "Test Elementary School",
            "Address 1": "123 Test Street",
            "City": "Austin",
            "State": "TX",
            "Zip": "78701",
            "Phone": "512-555-0123",
            "School Website": "https://test.school.edu",
            "District": "Test ISD",
            "Grades Served": "K-5",
            "Principal Name": "John Smith"
        }

    def test_valid_school_data(self):
        """Test that valid school data passes validation"""
        logger.info("Testing valid school data")
        result = validate_school_data(self.valid_school_data)
        logger.info(f"Validation result: {result}")
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["score"], 100)
        self.assertEqual(len(result["issues"]), 0)

    def test_invalid_zip_code(self):
        """Test ZIP code validation"""
        logger.info("Testing invalid ZIP codes")
        test_cases = [
            "1234",      # Too short
            "123456",    # Too long
            "abcde",     # Non-numeric
            "12a45"      # Mixed characters
        ]
        
        for invalid_zip in test_cases:
            with self.subTest(zip=invalid_zip):
                logger.info(f"Testing ZIP code: {invalid_zip}")
                data = self.valid_school_data.copy()
                data["Zip"] = invalid_zip
                result = validate_school_data(data)
                logger.info(f"Validation result: {result}")
                self.assertFalse(result["is_valid"])
                self.assertIn("Invalid ZIP format", result["issues"][0])

    def test_invalid_state(self):
        """Test state validation"""
        logger.info("Testing invalid states")
        test_cases = [
            "XX",    # Non-existent state
            "ABC",   # Too long
            "A",     # Too short
            "12"     # Numbers
        ]
        
        for invalid_state in test_cases:
            with self.subTest(state=invalid_state):
                logger.info(f"Testing state: {invalid_state}")
                data = self.valid_school_data.copy()
                data["State"] = invalid_state
                result = validate_school_data(data)
                logger.info(f"Validation result: {result}")
                self.assertFalse(result["is_valid"])
                self.assertIn("Invalid state abbreviation", result["issues"][0])

    def test_invalid_phone(self):
        """Test phone number validation"""
        logger.info("Testing invalid phone numbers")
        test_cases = [
            "123-456-789",    # Missing digit
            "abcd-efg-hijk",  # Non-numeric
            "12345678901"     # Too long
        ]
        
        for invalid_phone in test_cases:
            with self.subTest(phone=invalid_phone):
                logger.info(f"Testing phone number: {invalid_phone}")
                data = self.valid_school_data.copy()
                data["Phone"] = invalid_phone
                result = validate_school_data(data)
                logger.info(f"Validation result: {result}")
                self.assertFalse(result["is_valid"])
                self.assertIn("Invalid phone number format", result["issues"][0])

    def test_invalid_website(self):
        """Test website URL validation"""
        logger.info("Testing invalid website URLs")
        test_cases = [
            "test.com",           # Missing protocol
            "ftp://test.com",     # Wrong protocol
            "not-a-url"           # Invalid format
        ]
        
        for invalid_url in test_cases:
            with self.subTest(url=invalid_url):
                logger.info(f"Testing website URL: {invalid_url}")
                data = self.valid_school_data.copy()
                data["School Website"] = invalid_url
                result = validate_school_data(data)
                logger.info(f"Validation result: {result}")
                self.assertFalse(result["is_valid"])
                self.assertIn("Invalid website URL format", result["issues"][0])

    def test_invalid_school_name(self):
        """Test school name validation"""
        logger.info("Testing invalid school names")
        test_cases = [
            "AB",           # Too short
            "123",          # No letters
            "Not Found"     # Changed from empty string
        ]
        
        for invalid_name in test_cases:
            with self.subTest(name=invalid_name):
                logger.info(f"Testing school name: {invalid_name}")
                data = self.valid_school_data.copy()
                data["School Name"] = invalid_name
                result = validate_school_data(data)
                logger.info(f"Validation result: {result}")
                self.assertFalse(result["is_valid"])
                if invalid_name == "Not Found":
                    self.assertIn("School Name not available", result["issues"][0])
                else:
                    self.assertIn("Invalid school name format", result["issues"][0])

    def test_invalid_city(self):
        """Test city name validation"""
        logger.info("Testing invalid city names")
        test_cases = [
            "Austin123",    # Contains numbers
            "Austin#",      # Contains special characters
            "123"           # Only numbers
        ]
        
        for invalid_city in test_cases:
            with self.subTest(city=invalid_city):
                logger.info(f"Testing city name: {invalid_city}")
                data = self.valid_school_data.copy()
                data["City"] = invalid_city
                result = validate_school_data(data)
                logger.info(f"Validation result: {result}")
                self.assertFalse(result["is_valid"])
                self.assertIn("City name should only contain letters", result["issues"][0])

    def test_invalid_principal_name(self):
        """Test principal name validation"""
        logger.info("Testing invalid principal names")
        test_cases = [
            "John",         # Missing last name
            "J",           # Too short
            "Not Found"    # Changed from empty string
        ]
        
        for invalid_name in test_cases:
            with self.subTest(name=invalid_name):
                logger.info(f"Testing principal name: {invalid_name}")
                data = self.valid_school_data.copy()
                data["Principal Name"] = invalid_name
                result = validate_school_data(data)
                logger.info(f"Validation result: {result}")
                self.assertFalse(result["is_valid"])
                if invalid_name == "Not Found":
                    self.assertIn("Principal Name not available", result["issues"][0])
                else:
                    self.assertIn("Principal name should include first and last name", result["issues"][0])

if __name__ == '__main__':
    unittest.main(verbosity=2)
