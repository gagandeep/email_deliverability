"""SPF (Sender Policy Framework) implementation for email authentication."""
import dns.resolver
import re
import ipaddress


class SPFValidator:
    def __init__(self, domain):
        """
        Initialize SPF validator for a domain.
        
        Args:
            domain (str): The domain to validate SPF records for
        """
        self.domain = domain
        self._spf_record = None
    
    @property
    def spf_record(self):
        """Get the SPF record for the domain."""
        if self._spf_record is None:
            try:
                answers = dns.resolver.resolve(self.domain, 'TXT')
                for rdata in answers:
                    txt_record = rdata.to_text().strip('"')
                    if txt_record.startswith('v=spf1'):
                        self._spf_record = txt_record
                        break
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                self._spf_record = ""
        return self._spf_record
    
    def verify_record_exists(self):
        """Check if an SPF record exists for the domain."""
        return bool(self.spf_record)
    
    def analyze_record(self):
        """
        Analyze the SPF record for common issues.
        
        Returns:
            dict: Analysis results
        """
        if not self.spf_record:
            return {"exists": False, "error": "No SPF record found"}
        
        results = {
            "exists": True,
            "record": self.spf_record,
            "issues": [],
            "mechanisms": [],
        }
        
        # Check for too many DNS lookups
        lookups = 0
        mechanisms = re.findall(r'(?:include|a|mx|ptr|exists):[^\s]+', self.spf_record)
        results["mechanisms"] = mechanisms
        lookups = len(mechanisms)
        
        if lookups > 10:
            results["issues"].append(f"Too many DNS lookups ({lookups}). Limit is 10.")
        
        # Check for ~all or -all
        if " -all" not in self.spf_record and " ~all" not in self.spf_record:
            results["issues"].append("Missing strict policy (-all or ~all)")
        
        return results
    
    def validate_ip(self, ip_address):
        """
        Check if an IP address is authorized to send email for the domain.
        
        Args:
            ip_address (str): IP address to check
            
        Returns:
            bool: True if authorized, False otherwise
        """
        if not self.spf_record:
            return False
            
        ip = ipaddress.ip_address(ip_address)
        
        # Check if IP is directly included
        ip_ranges = re.findall(r'ip4:([^\s]+)', self.spf_record)
        for ip_range in ip_ranges:
            try:
                if '/' in ip_range:  # CIDR notation
                    network = ipaddress.ip_network(ip_range)
                    if ip in network:
                        return True
                else:
                    if ip == ipaddress.ip_address(ip_range):
                        return True
            except ValueError:
                continue
                
        # Note: This is a simplified implementation
        # A full implementation would need to handle includes, a, mx, etc.
        
        return False

    def generate_record(self, authorized_servers=None, include_domains=None, policy="~all"):
        """
        Generate an SPF record for the domain.
        
        Args:
            authorized_servers (list): List of IP addresses/ranges to authorize
            include_domains (list): List of domains to include
            policy (str): Policy qualifier (~all, -all, ?all, +all)
            
        Returns:
            str: Generated SPF record
        """
        if authorized_servers is None:
            authorized_servers = []
        if include_domains is None:
            include_domains = []
            
        record_parts = ["v=spf1"]
        
        # Add authorized servers
        for server in authorized_servers:
            if '/' in server:  # CIDR notation
                record_parts.append(f"ip4:{server}")
            else:
                record_parts.append(f"ip4:{server}")
                
        # Add includes
        for domain in include_domains:
            record_parts.append(f"include:{domain}")
            
        # Add policy
        record_parts.append(policy)
        
        return " ".join(record_parts)