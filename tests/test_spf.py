import unittest
from unittest.mock import patch, MagicMock
import dns.resolver
from email_deliverability.authentication.spf import SPFValidator


class TestSPFValidator(unittest.TestCase):
    def setUp(self):
        self.validator = SPFValidator("example.com")
    
    @patch("dns.resolver.resolve")
    def test_spf_record_exists(self, mock_resolve):
        # Mock DNS response
        mock_response = MagicMock()
        mock_response.to_text.return_value = '"v=spf1 ip4:192.0.2.0/24 ~all"'
        mock_resolve.return_value = [mock_response]
        
        # Test SPF record retrieval
        self.assertTrue(self.validator.verify_record_exists())
        self.assertEqual('v=spf1 ip4:192.0.2.0/24 ~all', self.validator.spf_record)
        
    @patch("dns.resolver.resolve")
    def test_spf_record_missing(self, mock_resolve):
        # Mock DNS exception
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()
        
        # Test SPF record missing
        self.assertFalse(self.validator.verify_record_exists())
        self.assertEqual('', self.validator.spf_record)
    
    @patch("dns.resolver.resolve")
    def test_analyze_record_valid(self, mock_resolve):
        # Mock DNS response
        mock_response = MagicMock()
        mock_response.to_text.return_value = '"v=spf1 ip4:192.0.2.0/24 -all"'
        mock_resolve.return_value = [mock_response]
        
        # Test analysis of valid record
        result = self.validator.analyze_record()
        self.assertTrue(result["exists"])
        self.assertEqual('v=spf1 ip4:192.0.2.0/24 -all', result["record"])
        self.assertEqual(0, len(result["issues"]))
    
    @patch("dns.resolver.resolve")
    def test_analyze_record_soft_all(self, mock_resolve):
        # Mock DNS response with ~all
        mock_response = MagicMock()
        mock_response.to_text.return_value = '"v=spf1 ip4:192.0.2.0/24 ~all"'
        mock_resolve.return_value = [mock_response]
        
        # Test analysis of record with ~all
        result = self.validator.analyze_record()
        self.assertTrue(result["exists"])
        self.assertEqual('v=spf1 ip4:192.0.2.0/24 ~all', result["record"])
        self.assertEqual(0, len(result["issues"]))
    
    @patch("dns.resolver.resolve")
    def test_analyze_record_missing_policy(self, mock_resolve):
        # Mock DNS response with missing -all or ~all
        mock_response = MagicMock()
        mock_response.to_text.return_value = '"v=spf1 ip4:192.0.2.0/24"'
        mock_resolve.return_value = [mock_response]
        
        # Test analysis of record with missing policy
        result = self.validator.analyze_record()
        self.assertTrue(result["exists"])
        self.assertEqual(1, len(result["issues"]))
        self.assertIn("Missing strict policy", result["issues"][0])
    
    @patch("dns.resolver.resolve")
    def test_analyze_record_too_many_lookups(self, mock_resolve):
        # Mock DNS response with too many includes
        mock_response = MagicMock()
        record = 'v=spf1 ' + ' '.join([f'include:domain{i}.com' for i in range(15)]) + ' -all'
        mock_response.to_text.return_value = f'"{record}"'
        mock_resolve.return_value = [mock_response]
        
        # Test analysis of record with too many lookups
        result = self.validator.analyze_record()
        self.assertTrue(result["exists"])
        self.assertEqual(1, len(result["issues"]))
        self.assertIn("Too many DNS lookups", result["issues"][0])
    
    def test_validate_ip_in_range(self):
        # Mock the spf_record property
        self.validator._spf_record = 'v=spf1 ip4:192.0.2.0/24 -all'
        
        # Test IP in range
        self.assertTrue(self.validator.validate_ip('192.0.2.10'))
    
    def test_validate_ip_not_in_range(self):
        # Mock the spf_record property
        self.validator._spf_record = 'v=spf1 ip4:192.0.2.0/24 -all'
        
        # Test IP not in range
        self.assertFalse(self.validator.validate_ip('192.0.3.10'))
    
    def test_generate_record(self):
        # Test record generation
        record = self.validator.generate_record(
            authorized_servers=['192.0.2.1', '192.0.2.0/24'],
            include_domains=['thirdparty.com', 'mail.example.com'],
            policy='-all'
        )
        
        self.assertIn('v=spf1', record)
        self.assertIn('ip4:192.0.2.1', record)
        self.assertIn('ip4:192.0.2.0/24', record)
        self.assertIn('include:thirdparty.com', record)
        self.assertIn('include:mail.example.com', record)
        self.assertIn('-all', record)


if __name__ == '__main__':
    unittest.main()