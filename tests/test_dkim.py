import unittest
from unittest.mock import patch, MagicMock
import dns.resolver
from email_deliverability.authentication.dkim import DKIMManager


class TestDKIMManager(unittest.TestCase):
    def setUp(self):
        self.dkim = DKIMManager("example.com", "selector1")
    
    @patch("dns.resolver.resolve")
    def test_dkim_record_exists(self, mock_resolve):
        # Mock DNS response
        mock_response = MagicMock()
        mock_response.to_text.return_value = '"v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA..."'
        mock_resolve.return_value = [mock_response]
        
        # Test DKIM record retrieval
        self.assertTrue(self.dkim.verify_record_exists())
        self.assertEqual('v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA...', self.dkim.dkim_record)
        
    @patch("dns.resolver.resolve")
    def test_dkim_record_missing(self, mock_resolve):
        # Mock DNS exception
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()
        
        # Test DKIM record missing
        self.assertFalse(self.dkim.verify_record_exists())
        self.assertEqual('', self.dkim.dkim_record)
    
    @patch("dns.resolver.resolve")
    def test_analyze_record_valid(self, mock_resolve):
        # Mock DNS response
        mock_response = MagicMock()
        mock_response.to_text.return_value = '"v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA..."'
        mock_resolve.return_value = [mock_response]
        
        # Test analysis of valid record
        result = self.dkim.analyze_record()
        self.assertTrue(result["exists"])
        self.assertIn("v", result["parsed"])
        self.assertIn("k", result["parsed"])
        self.assertIn("p", result["parsed"])
        self.assertEqual(0, len(result["issues"]))
    
    @patch("dns.resolver.resolve")
    def test_analyze_record_missing_version(self, mock_resolve):
        # Mock DNS response with missing v tag
        mock_response = MagicMock()
        mock_response.to_text.return_value = '"k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA..."'
        mock_resolve.return_value = [mock_response]
        
        # Test analysis of record with missing v tag
        result = self.dkim.analyze_record()
        self.assertTrue(result["exists"])
        self.assertIn("Missing required tag: v", result["issues"])
    
    @patch("dns.resolver.resolve")
    def test_analyze_record_empty_public_key(self, mock_resolve):
        # Mock DNS response with empty public key
        mock_response = MagicMock()
        mock_response.to_text.return_value = '"v=DKIM1; k=rsa; p="'
        mock_resolve.return_value = [mock_response]
        
        # Test analysis of record with empty public key
        result = self.dkim.analyze_record()
        self.assertTrue(result["exists"])
        # Check that "Empty public key" is in the issues list (at any position)
        self.assertIn("Empty public key", " ".join(result["issues"]))
    
    def test_generate_keypair(self):
        # Test key pair generation
        private_pem, txt_record = self.dkim.generate_keypair(key_size=1024)
        
        # Verify the private key format
        self.assertIn('BEGIN RSA PRIVATE KEY', private_pem)
        self.assertIn('END RSA PRIVATE KEY', private_pem)
        
        # Verify the TXT record format
        self.assertIn('v=DKIM1', txt_record)
        self.assertIn('k=rsa', txt_record)
        self.assertIn('p=', txt_record)


if __name__ == '__main__':
    unittest.main()