"""DMARC (Domain-based Message Authentication, Reporting and Conformance) implementation."""
import dns.resolver
import re


class DMARCAnalyzer:
    def __init__(self, domain):
        """
        Initialize DMARC analyzer.
        
        Args:
            domain (str): The domain to analyze DMARC for
        """
        self.domain = domain
        self._dmarc_record = None
    
    @property
    def dmarc_record(self):
        """Get the DMARC record for the domain."""
        if self._dmarc_record is None:
            try:
                # DMARC records are published at _dmarc.domain
                lookup_domain = f"_dmarc.{self.domain}"
                answers = dns.resolver.resolve(lookup_domain, 'TXT')
                for rdata in answers:
                    txt_record = rdata.to_text().strip('"')
                    if txt_record.startswith('v=DMARC1'):
                        self._dmarc_record = txt_record
                        break
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                self._dmarc_record = ""
        return self._dmarc_record
    
    def verify_record_exists(self):
        """Check if a DMARC record exists for the domain."""
        return bool(self.dmarc_record)
    
    def analyze_record(self):
        """
        Analyze the DMARC record for common issues.
        
        Returns:
            dict: Analysis results
        """
        if not self.dmarc_record:
            return {"exists": False, "error": "No DMARC record found"}
        
        results = {
            "exists": True,
            "record": self.dmarc_record,
            "issues": [],
            "parsed": {}
        }
        
        # Parse key-value pairs
        pairs = re.findall(r'([a-z]+)=([^;]+)', self.dmarc_record)
        for key, value in pairs:
            results["parsed"][key] = value
        
        # Check for required tags
        required_tags = ["v", "p"]
        for tag in required_tags:
            if tag not in results["parsed"]:
                results["issues"].append(f"Missing required tag: {tag}")
        
        # Check policy value
        policy = results["parsed"].get("p", "")
        if policy not in ["none", "quarantine", "reject"]:
            results["issues"].append(f"Invalid policy value: {policy}")
        elif policy == "none":
            results["issues"].append("Policy set to 'none', provides no protection")
        
        # Check reporting addresses
        rua = results["parsed"].get("rua", "")
        ruf = results["parsed"].get("ruf", "")
        
        if not rua:
            results["issues"].append("No aggregate reporting address (rua) specified")
        if not ruf:
            results["issues"].append("No forensic reporting address (ruf) specified")
            
        # Check percentage
        pct = results["parsed"].get("pct", "100")
        if pct != "100":
            results["issues"].append(f"Only applying DMARC to {pct}% of emails")
            
        return results
    
    def generate_record(self, policy="none", subdomain_policy=None, 
                      reporting_email=None, percentage=100, 
                      spf_strict=False, dkim_strict=False):
        """
        Generate a DMARC record based on the provided parameters.
        
        Args:
            policy (str): Policy to apply ('none', 'quarantine', 'reject')
            subdomain_policy (str): Policy for subdomains
            reporting_email (str): Email address for reports
            percentage (int): Percentage of messages to apply policy to
            spf_strict (bool): Whether to require SPF alignment
            dkim_strict (bool): Whether to require DKIM alignment
            
        Returns:
            str: Generated DMARC record
        """
        record_parts = ["v=DMARC1"]
        
        # Add policy
        record_parts.append(f"p={policy}")
        
        # Add subdomain policy if different from main policy
        if subdomain_policy is not None and subdomain_policy != policy:
            record_parts.append(f"sp={subdomain_policy}")
        
        # Add alignment settings
        aspf = "s" if spf_strict else "r"
        adkim = "s" if dkim_strict else "r"
        record_parts.append(f"aspf={aspf}")
        record_parts.append(f"adkim={adkim}")
        
        # Add reporting addresses
        if reporting_email:
            record_parts.append(f"rua=mailto:{reporting_email}")
            record_parts.append(f"ruf=mailto:{reporting_email}")
        
        # Add percentage if not 100%
        if percentage != 100:
            record_parts.append(f"pct={percentage}")
        
        return "; ".join(record_parts)