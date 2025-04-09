import unittest
from unittest.mock import patch, MagicMock
import dns.resolver
from email_deliverability.list_hygiene.validator import EmailValidator
from email_deliverability.resource_manager import ResourceManager


class TestEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = EmailValidator()
        
        # Mock the resource manager's load_resource method
        self.original_load_resource = ResourceManager.load_resource
        ResourceManager.load_resource = MagicMock(return_value=[
            "disposable.com", "mailinator.com", "tempmail.com"
        ])
    
    def tearDown(self):
        # Restore original method
        ResourceManager.load_resource = self.original_load_resource
    
    def test_is_valid_format_valid(self):
        # Test valid email format
        self.assertTrue(self.validator.is_valid_format("user@example.com"))
        self.assertTrue(self.validator.is_valid_format("user.name+tag@example.co.uk"))
    
    def test_is_valid_format_invalid(self):
        # Test invalid email formats
        self.assertFalse(self.validator.is_valid_format("user@"))
        self.assertFalse(self.validator.is_valid_format("@example.com"))
        self.assertFalse(self.validator.is_valid_format("user.example.com"))
        self.assertFalse(self.validator.is_valid_format("user@example"))
    
    def test_is_disposable(self):
        # Test disposable email detection
        self.assertTrue(self.validator.is_disposable("user@disposable.com"))
        self.assertTrue(self.validator.is_disposable("user@mailinator.com"))
        self.assertFalse(self.validator.is_disposable("user@example.com"))
    
    @patch("dns.resolver.resolve")
    def test_has_valid_mx_valid(self, mock_resolve):
        # Mock valid MX record
        mock_resolve.return_value = [MagicMock()]
        
        # Test valid MX
        self.assertTrue(self.validator.has_valid_mx("user@example.com"))
    
    @patch("dns.resolver.resolve")
    def test_has_valid_mx_invalid(self, mock_resolve):
        # Mock no MX record
        mock_resolve.side_effect = dns.resolver.NoAnswer()
        
        # Test invalid MX
        self.assertFalse(self.validator.has_valid_mx("user@nonexistent.example"))
    
    @patch("dns.resolver.resolve")
    def test_validate_email_valid(self, mock_resolve):
        # Mock valid MX record
        mock_resolve.return_value = [MagicMock()]
        
        # Test valid email validation
        result = self.validator.validate_email("user@example.com")
        self.assertTrue(result["is_valid"])
        self.assertTrue(result["format_valid"])
        self.assertTrue(result["has_mx"])
        self.assertFalse(result["is_disposable"])
        self.assertEqual(0, len(result["issues"]))
    
    def test_validate_email_invalid_format(self):
        # Test invalid format
        result = self.validator.validate_email("invalid-email")
        self.assertFalse(result["is_valid"])
        self.assertFalse(result["format_valid"])
        self.assertEqual(1, len(result["issues"]))
        self.assertIn("Invalid email format", result["issues"])
    
    @patch("dns.resolver.resolve")
    def test_validate_email_disposable(self, mock_resolve):
        # Mock valid MX record
        mock_resolve.return_value = [MagicMock()]
        
        # Test disposable email
        result = self.validator.validate_email("user@disposable.com")
        self.assertTrue(result["is_valid"])  # Still valid, but disposable
        self.assertTrue(result["is_disposable"])
        self.assertEqual(1, len(result["issues"]))
        self.assertIn("Disposable email address", result["issues"])
    
    @patch("dns.resolver.resolve")
    def test_validate_email_no_mx(self, mock_resolve):
        # Mock no MX record
        mock_resolve.side_effect = dns.resolver.NoAnswer()
        
        # Test email with no MX
        result = self.validator.validate_email("user@nonexistent.example")
        self.assertFalse(result["is_valid"])
        self.assertTrue(result["format_valid"])
        self.assertFalse(result["has_mx"])
        self.assertEqual(1, len(result["issues"]))
        self.assertIn("no valid MX records", result["issues"][0])
    
    @patch("email_deliverability.list_hygiene.validator.EmailValidator.validate_email")
    def test_batch_validate(self, mock_validate):
        # Mock the validate_email method
        mock_validate.side_effect = [
            {"email": "user1@example.com", "is_valid": True},
            {"email": "user2@example.com", "is_valid": True},
            {"email": "invalid@nonexistent.example", "is_valid": False}
        ]
        
        # Test batch validation
        emails = ["user1@example.com", "user2@example.com", "invalid@nonexistent.example"]
        results = self.validator.batch_validate(emails, max_workers=1)
        
        # Verify results
        self.assertEqual(3, len(results))
        self.assertTrue(results[0]["is_valid"])
        self.assertTrue(results[1]["is_valid"])
        self.assertFalse(results[2]["is_valid"])
    
    def test_analyze_list_quality(self):
        # Create sample validation results
        validation_results = [
            {"email": "user1@example.com", "is_valid": True, "is_disposable": False, "format_valid": True, "has_mx": True},
            {"email": "user2@example.com", "is_valid": True, "is_disposable": False, "format_valid": True, "has_mx": True},
            {"email": "user3@disposable.com", "is_valid": True, "is_disposable": True, "format_valid": True, "has_mx": True},
            {"email": "invalid@nonexistent", "is_valid": False, "is_disposable": False, "format_valid": True, "has_mx": False},
            {"email": "notanemail", "is_valid": False, "is_disposable": False, "format_valid": False, "has_mx": False}
        ]
        
        # Analyze list quality
        analysis = self.validator.analyze_list_quality(validation_results)
        
        # Verify analysis
        self.assertEqual(5, analysis["total_emails"])
        self.assertEqual(3, analysis["valid_emails"])
        self.assertEqual(2, analysis["invalid_emails"])
        self.assertEqual(1, analysis["disposable_emails"])
        self.assertEqual(60.0, analysis["quality_score"])
        self.assertEqual("poor", analysis["quality_level"])
        self.assertIsInstance(analysis["recommendations"], list)


if __name__ == '__main__':
    unittest.main()