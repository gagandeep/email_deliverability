import unittest
from unittest.mock import patch, MagicMock
from email_deliverability.facade import DeliverabilityManager


class TestDeliverabilityManager(unittest.TestCase):
    @patch('email_deliverability.facade.start_resource_updater')
    def setUp(self, mock_start_updater):
        self.manager = DeliverabilityManager(
            domain="example.com",
            ip="192.0.2.1",
            auto_update_resources=False  # Changed to False for testing purposes
        )
        # No need to verify resource updater in tests
    
    def test_initialization(self):
        # Test basic initialization
        self.assertEqual("example.com", self.manager.domain)
        self.assertEqual("192.0.2.1", self.manager.ip)
    
    @patch('email_deliverability.authentication.spf.SPFValidator.verify_record_exists')
    @patch('email_deliverability.authentication.dkim.DKIMManager.verify_record_exists')
    @patch('email_deliverability.authentication.dmarc.DMARCAnalyzer.verify_record_exists')
    def test_analyze_domain_setup(self, mock_dmarc_exists, mock_dkim_exists, mock_spf_exists):
        # Mock authentication verification
        mock_spf_exists.return_value = True
        mock_dkim_exists.return_value = False
        mock_dmarc_exists.return_value = True
        
        # Mock analysis methods
        self.manager.spf.analyze_record = MagicMock(return_value={"exists": True, "issues": []})
        self.manager.dmarc.analyze_record = MagicMock(return_value={"exists": True, "issues": ["Policy set to 'none'"]})
        
        # Test domain setup analysis
        result = self.manager.analyze_domain_setup()
        
        # Verify result
        self.assertEqual("example.com", result["domain"])
        self.assertTrue(result["spf"]["exists"])
        self.assertFalse(result["dkim"]["exists"])
        self.assertTrue(result["dmarc"]["exists"])
        self.assertGreater(result["overall_score"], 0)
        self.assertLess(result["overall_score"], 100)  # Should be penalized for missing DKIM
        self.assertIn("Set up DKIM", result["recommendations"][0])
    
    @patch('email_deliverability.reputation.monitor.ReputationMonitor.check_ip_blacklists')
    def test_check_ip_reputation(self, mock_check_blacklists):
        # Mock blacklist check
        mock_check_blacklists.return_value = {
            "ip": "192.0.2.1",
            "status": "clean",
            "blacklisted_on": [],
            "clean_on": ["zen.spamhaus.org", "bl.spamcop.net"]
        }
        
        # Test IP reputation check
        result = self.manager.check_ip_reputation()
        
        # Verify result
        self.assertEqual("clean", result["status"])
        self.assertEqual(0, len(result["blacklisted_on"]))
    
    @patch('email_deliverability.list_hygiene.validator.EmailValidator.batch_validate')
    @patch('email_deliverability.list_hygiene.validator.EmailValidator.analyze_list_quality')
    def test_validate_email_list(self, mock_analyze, mock_validate):
        # Mock validation and analysis
        validation_results = [
            {"email": "user1@example.com", "is_valid": True},
            {"email": "invalid@nonexistent.example", "is_valid": False}
        ]
        mock_validate.return_value = validation_results
        
        analysis_result = {
            "total_emails": 2,
            "valid_emails": 1,
            "quality_score": 50.0,
            "quality_level": "poor"  # Updated to match the fixed implementation
        }
        mock_analyze.return_value = analysis_result
        
        # Test email list validation
        emails = ["user1@example.com", "invalid@nonexistent.example"]
        result = self.manager.validate_email_list(emails)
        
        # Verify result structure
        self.assertIn("results", result)
        self.assertIn("analysis", result)
        self.assertEqual(validation_results, result["results"])
        self.assertEqual(analysis_result, result["analysis"])
    
    def test_create_ip_warming_plan(self):
        # Test IP warming plan creation
        result = self.manager.create_ip_warming_plan(daily_target=10000, warmup_days=15)
        
        # Verify result structure
        self.assertIn("schedule", result)
        self.assertIn("recommendations", result)
        self.assertEqual(10000, result["daily_target"])
        self.assertEqual(15, result["warmup_days"])
        self.assertEqual(15, len(result["schedule"]))
        
        # Verify schedule has increasing volumes
        first_day = result["schedule"][0]["volume"]
        last_day = result["schedule"][-1]["volume"]
        self.assertLess(first_day, last_day)
        self.assertEqual(10000, last_day)  # Last day should reach target
    
    @patch('email_deliverability.facade.DeliverabilityManager.analyze_domain_setup')
    @patch('email_deliverability.facade.DeliverabilityManager.check_ip_reputation')
    @patch('email_deliverability.reputation.monitor.ReputationMonitor.check_domain_reputation')
    def test_check_deliverability_status(self, mock_domain_rep, mock_ip_rep, mock_domain_setup):
        # Mock component methods
        # Fix: Ensure mock_domain_setup returns the full expected structure including authentication keys
        mock_domain_setup.return_value = {
            "domain": "example.com",
            "spf": {"exists": True},  # This needs to be present
            "dkim": {"exists": True}, 
            "dmarc": {"exists": False},
            "overall_score": 60,
            "recommendations": ["Set up a DMARC policy"]
        }
        
        mock_ip_rep.return_value = {
            "status": "clean",
            "blacklisted_on": []
        }
        
        mock_domain_rep.return_value = {
            "reputation_score": 85,
            "issues": ["Spam complaint rate above threshold"]
        }
        
        # Test deliverability status check
        result = self.manager.check_deliverability_status()
        
        # Verify result
        self.assertIn("timestamp", result)
        self.assertEqual("example.com", result["domain"])
        self.assertEqual("192.0.2.1", result["ip"])
        self.assertIn("authentication", result)
        self.assertIn("reputation", result)
        self.assertIn("recommendations", result)
        self.assertEqual(85, result["reputation"]["domain_score"])
        self.assertEqual("clean", result["reputation"]["ip_status"])
        self.assertGreaterEqual(len(result["recommendations"]), 2)  # Should have recommendations from both checks
    
    @patch('email_deliverability.resource_manager.ResourceManager.update_all_resources')
    def test_update_resources(self, mock_update):
        # Mock resource update
        mock_update.return_value = {
            "disposable_domains": {"status": "updated", "items": 1000},
            "dnsbl_list": {"status": "updated", "items": 50}
        }
        
        # Test resource update
        result = self.manager.update_resources()
        
        # Verify result
        self.assertEqual(mock_update.return_value, result)
        mock_update.assert_called_once()


if __name__ == '__main__':
    unittest.main()