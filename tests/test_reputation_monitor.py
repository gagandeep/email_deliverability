import unittest
from unittest.mock import patch, MagicMock
import socket
from email_deliverability.reputation.monitor import ReputationMonitor


class TestReputationMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = ReputationMonitor(domain="example.com", sending_ip="192.0.2.10")
    
    @patch("socket.gethostbyname")
    def test_check_ip_blacklists_clean(self, mock_gethostbyname):
        # Mock socket.gethostbyname to raise an exception (meaning IP not found in blacklist)
        mock_gethostbyname.side_effect = socket.gaierror()
        
        # Test blacklist check with clean result
        result = self.monitor.check_ip_blacklists()
        
        self.assertEqual("clean", result["status"])
        self.assertEqual(0, len(result["blacklisted_on"]))
        self.assertGreater(len(result["clean_on"]), 0)
    
    @patch("socket.gethostbyname")
    def test_check_ip_blacklists_listed(self, mock_gethostbyname):
        # Mock socket.gethostbyname to return an IP for the first blacklist (meaning listed)
        def side_effect(arg):
            if "zen.spamhaus.org" in arg:
                return "127.0.0.2"
            else:
                raise socket.gaierror()
                
        mock_gethostbyname.side_effect = side_effect
        
        # Test blacklist check with blacklisted result
        result = self.monitor.check_ip_blacklists()
        
        self.assertEqual("blacklisted", result["status"])
        self.assertEqual(1, len(result["blacklisted_on"]))  # Fixed the unclosed bracket
        self.assertIn("zen.spamhaus.org", result["blacklisted_on"])
    
    @patch("requests.get")
    def test_monitor_feedback_loops(self, mock_get):
        # Mock CSV data for complaints
        csv_data = """email,reason,campaign_id,timestamp
user1@example.com,spam content,campaign1,2025-01-01T10:00:00
user2@example.com,unwanted,campaign1,2025-01-01T10:15:00
user3@example.com,spam content,campaign2,2025-01-01T12:30:00"""
        
        # Test feedback loop monitoring
        result = self.monitor.monitor_feedback_loops(csv_data)
        
        # Verify results
        self.assertEqual(3, result["total_complaints"])
        self.assertEqual(2, result["common_reasons"].get("spam content", 0))
        self.assertEqual(2, result["affected_campaigns"].get("campaign1", 0))
    
    def test_check_domain_reputation(self):
        # Test domain reputation check (mock implementation)
        result = self.monitor.check_domain_reputation()
        
        # Verify results contain expected fields
        self.assertEqual("example.com", result["domain"])
        self.assertIn("reputation_score", result)
        self.assertIn("spam_rate", result)
        self.assertIn("authentication", result)
        self.assertIsInstance(result["issues"], list)
    
    @patch("email_deliverability.reputation.monitor.ReputationMonitor.check_ip_blacklists")
    def test_analyze_bounce_logs(self, mock_blacklists):
        # Sample bounce data
        bounce_data = [
            {"email": "user1@example.com", "type": "hard", "reason": "recipient rejected"},
            {"email": "user2@example.com", "type": "soft", "reason": "mailbox full"},
            {"email": "user3@example.com", "type": "spam_block", "reason": "blocked as spam"}
        ]
        
        # Test bounce log analysis
        result = self.monitor.analyze_bounce_logs(bounce_data)
        
        # Verify results
        self.assertEqual(3, result["total_bounces"])
        self.assertEqual(1, result["hard_bounces"])
        self.assertEqual(1, result["soft_bounces"])
        self.assertEqual(1, result["spam_blocks"])
        self.assertTrue(any("spam" in r for r in result["recommendations"]))


if __name__ == '__main__':
    unittest.main()