"""Monitor and analyze email sender reputation."""
import requests
import time
import socket
import csv
import io
from datetime import datetime, timedelta
from ..resource_manager import ResourceManager


class ReputationMonitor:
    def __init__(self, domain=None, sending_ip=None, api_key=None):
        """
        Initialize reputation monitoring for a domain and/or IP.
        
        Args:
            domain (str): Domain to monitor
            sending_ip (str): IP address to monitor
            api_key (str): API key for external services
        """
        self.domain = domain
        self.sending_ip = sending_ip or self._get_server_ip()
        self.api_key = api_key
        self.resource_manager = ResourceManager()
        
    def _get_server_ip(self):
        """Get the IP address of the server."""
        try:
            return requests.get('https://api.ipify.org', timeout=5).text
        except:
            # Fallback to socket
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
    
    def check_ip_blacklists(self):
        """
        Check if the IP is listed in common blacklists.
        
        Returns:
            dict: Results of blacklist checks
        """
        # Load blacklist domains from resource manager
        blacklists = self.resource_manager.load_resource("dnsbl_list")
        
        # Use a default list if resource isn't available
        if not blacklists:
            blacklists = [
                "zen.spamhaus.org",
                "bl.spamcop.net",
                "dnsbl.sorbs.net",
                "b.barracudacentral.org"
            ]
        else:
            # Limit to 20 most common blacklists to avoid too many DNS lookups
            blacklists = blacklists[:20]
        
        results = {
            "ip": self.sending_ip,
            "blacklisted_on": [],
            "clean_on": [],
            "errors": []
        }
        
        for blacklist in blacklists:
            try:
                # Reverse the IP address
                ip_parts = self.sending_ip.split('.')
                ip_parts.reverse()
                reversed_ip = '.'.join(ip_parts)
                
                # Construct lookup domain
                lookup_domain = f"{reversed_ip}.{blacklist}"
                
                try:
                    socket.gethostbyname(lookup_domain)
                    # If we get here, the IP is blacklisted
                    results["blacklisted_on"].append(blacklist)
                except socket.gaierror:
                    # IP not found in this blacklist
                    results["clean_on"].append(blacklist)
            except Exception as e:
                results["errors"].append(f"{blacklist}: {str(e)}")
        
        results["status"] = "clean" if not results["blacklisted_on"] else "blacklisted"
        return results
    
    def monitor_feedback_loops(self, complaint_data):
        """
        Process and analyze feedback loop complaints.
        
        Args:
            complaint_data (str): CSV data of complaints
            
        Returns:
            dict: Analysis of complaints
        """
        results = {
            "total_complaints": 0,
            "complaint_rate": 0,
            "common_reasons": {},
            "affected_campaigns": {},
            "trend": "stable"
        }
        
        # Parse CSV data
        csv_file = io.StringIO(complaint_data)
        reader = csv.DictReader(csv_file)
        
        complaints = list(reader)
        results["total_complaints"] = len(complaints)
        
        # Calculate rates and analyze
        if complaints:
            # Count by reason
            for complaint in complaints:
                reason = complaint.get("reason", "unknown")
                campaign = complaint.get("campaign_id", "unknown")
                
                if reason not in results["common_reasons"]:
                    results["common_reasons"][reason] = 0
                results["common_reasons"][reason] += 1
                
                if campaign not in results["affected_campaigns"]:
                    results["affected_campaigns"][campaign] = 0
                results["affected_campaigns"][campaign] += 1
        
        return results
    
    def check_domain_reputation(self):
        """
        Check domain reputation using a mock service.
        
        Returns:
            dict: Domain reputation data
        """
        # In a real implementation, this would use actual email reputation APIs
        # like Google Postmaster Tools, Microsoft SNDS, or commercial providers
        
        mock_data = {
            "domain": self.domain,
            "reputation_score": 85,  # 0-100 scale
            "spam_rate": 0.2,        # Percentage
            "authentication": {
                "spf_pass_rate": 98.5,
                "dkim_pass_rate": 95.2,
                "dmarc_pass_rate": 90.1
            },
            "issues": []
        }
        
        # Add mock issues based on scores
        if mock_data["spam_rate"] > 0.1:
            mock_data["issues"].append(
                "Spam complaint rate above recommended threshold of 0.1%"
            )
        
        auth_rates = mock_data["authentication"]
        if auth_rates["spf_pass_rate"] < 95:
            mock_data["issues"].append("SPF authentication rate below 95%")
        if auth_rates["dkim_pass_rate"] < 95:
            mock_data["issues"].append("DKIM authentication rate below 95%")
        if auth_rates["dmarc_pass_rate"] < 90:
            mock_data["issues"].append("DMARC pass rate below 90%")
            
        return mock_data
    
    def analyze_bounce_logs(self, bounce_data):
        """
        Analyze email bounce logs to identify reputation issues.
        
        Args:
            bounce_data (list): List of bounce records
            
        Returns:
            dict: Analysis of bounces
        """
        results = {
            "total_bounces": len(bounce_data),
            "hard_bounces": 0,
            "soft_bounces": 0,
            "spam_blocks": 0,
            "unknown": 0,
            "common_reasons": {},
            "recommendations": []
        }
        
        for bounce in bounce_data:
            bounce_type = bounce.get("type", "unknown")
            reason = bounce.get("reason", "unknown")
            
            # Track bounce types
            if bounce_type == "hard":
                results["hard_bounces"] += 1
            elif bounce_type == "soft":
                results["soft_bounces"] += 1
            elif bounce_type == "spam_block":
                results["spam_blocks"] += 1
            else:
                results["unknown"] += 1
                
            # Track reasons
            if reason not in results["common_reasons"]:
                results["common_reasons"][reason] = 0
            results["common_reasons"][reason] += 1
        
        # Generate recommendations
        hard_bounce_rate = results["hard_bounces"] / results["total_bounces"] if results["total_bounces"] else 0
        if hard_bounce_rate > 0.05:
            results["recommendations"].append(
                "Hard bounce rate is above 5%. Clean your email list to remove invalid addresses."
            )
            
        if results["spam_blocks"] > 0:
            results["recommendations"].append(
                "Some emails were blocked as spam. Review authentication settings and content."
            )
            
        return results