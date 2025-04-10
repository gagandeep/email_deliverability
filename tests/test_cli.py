"""Tests for the command line interface."""
import unittest
from unittest.mock import patch, MagicMock
import json
import sys
from io import StringIO

from email_deliverability.cli import EmailDeliverabilityCommandLine


class TestCLI(unittest.TestCase):
    """Test cases for the command line interface."""
    
    def test_version_command(self):
        """Test the version command."""
        cli = EmailDeliverabilityCommandLine()
        
        # Capture stdout
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            cli.run(['version'])
            output = out.getvalue().strip()
            
            # Check that version info is displayed
            self.assertIn('Email Deliverability CLI', output)
            self.assertIn('UTC', output)
            
        finally:
            sys.stdout = saved_stdout
    
    @patch('email_deliverability.cli.DeliverabilityManager')
    def test_auth_command(self, mock_manager_class):
        """Test the auth command."""
        # Setup mock
        mock_manager = MagicMock()
        mock_manager.analyze_domain_setup.return_value = {
            'overall_score': 85,
            'spf': {'status': 'pass'},
            'dkim': {'status': 'pass'},
            'dmarc': {'status': 'pass'}
        }
        mock_manager_class.return_value = mock_manager
        
        cli = EmailDeliverabilityCommandLine()
        
        # Capture stdout
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            cli.run(['auth', '--domain', 'example.com'])
            output = out.getvalue().strip()
            
            # Check that results are displayed
            self.assertIn('Score: 85/100', output)
            self.assertIn('Spf status: pass', output)
            
            # Check that the manager was called correctly
            mock_manager_class.assert_called_once_with(domain='example.com')
            mock_manager.analyze_domain_setup.assert_called_once()
            
        finally:
            sys.stdout = saved_stdout
    
    @patch('email_deliverability.cli.DeliverabilityManager')
    def test_reputation_command(self, mock_manager_class):
        """Test the reputation command."""
        # Setup mock
        mock_manager = MagicMock()
        mock_manager.check_ip_reputation.return_value = {
            'status': 'clean',
            'blacklisted_on': []
        }
        mock_manager_class.return_value = mock_manager
        
        cli = EmailDeliverabilityCommandLine()
        
        # Test with IP parameter
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            cli.run(['reputation', '--ip', '192.0.2.1'])
            output = out.getvalue().strip()
            
            # Check that results are displayed
            self.assertIn('Status: clean', output)
            
            # Check that the manager was called correctly
            mock_manager_class.assert_called_with(domain=None, ip='192.0.2.1')
            mock_manager.check_ip_reputation.assert_called_once()
            
        finally:
            sys.stdout = saved_stdout


if __name__ == '__main__':
    unittest.main()