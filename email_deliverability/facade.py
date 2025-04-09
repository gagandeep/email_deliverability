"""Facade for unified access to all deliverability tools."""
from .authentication.spf import SPFValidator
from .authentication.dkim import DKIMManager
from .authentication.dmarc import DMARCAnalyzer
from .reputation.monitor import ReputationMonitor
from .list_hygiene.validator import EmailValidator
from .ip_warming.scheduler import IPWarmingScheduler
from .resource_manager import ResourceManager, start_resource_updater
from datetime import datetime


class DeliverabilityManager:
    """
    Unified interface for email deliverability tools.
    """
    
    def __init__(self, domain=None, ip=None, api_key=None, auto_update_resources=True):
        """
        Initialize the deliverability manager.
        
        Args:
            domain (str): Email domain
            ip (str): Sending IP address
            api_key (str): API key for external services
            auto_update_resources (bool): Whether to automatically update resources daily
        """
        self.domain = domain
        self.ip = ip
        self.api_key = api_key
        
        # Initialize resource manager
        self.resource_manager = ResourceManager()
        
        # Start resource updater if requested
        if auto_update_resources:
            start_resource_updater("03:00")  # Update resources at 3 AM daily
        
        # Initialize components lazily when needed
        self._spf_validator = None
        self._dkim_manager = None
        self._dmarc_analyzer = None
        self._reputation_monitor = None
        self._email_validator = None
        self._ip_warming_scheduler = None
    
    @property
    def spf(self):
        """Get the SPF validator."""
        if not self._spf_validator and self.domain:
            self._spf_validator = SPFValidator(self.domain)
        return self._spf_validator
    
    @property
    def dkim(self):
        """Get the DKIM manager."""
        if not self._dkim_manager and self.domain:
            self._dkim_manager = DKIMManager(self.domain)
        return self._dkim_manager
    
    @property
    def dmarc(self):
        """Get the DMARC analyzer."""
        if not self._dmarc_analyzer and self.domain:
            self._dmarc_analyzer = DMARCAnalyzer(self.domain)
        return self._dmarc_analyzer
    
    @property
    def reputation(self):
        """Get the reputation monitor."""
        if not self._reputation_monitor:
            self._reputation_monitor = ReputationMonitor(
                domain=self.domain,
                sending_ip=self.ip,
                api_key=self.api_key
            )
        return self._reputation_monitor
    
    @property
    def email_validator(self):
        """Get the email validator."""
        if not self._email_validator:
            self._email_validator = EmailValidator()
        return self._email_validator
    
    @property
    def ip_warming(self):
        """Get the IP warming scheduler."""
        if not self._ip_warming_scheduler:
            self._ip_warming_scheduler = IPWarmingScheduler()
        return self._ip_warming_scheduler
    
    def update_resources(self):
        """
        Manually trigger an update of all resources.
        
        Returns:
            dict: Results of the resource update operation
        """
        return self.resource_manager.update_all_resources()
    
    def analyze_domain_setup(self):
        """
        Analyze the domain's authentication setup.
        
        Returns:
            dict: Analysis results
        """
        if not self.domain:
            return {"error": "Domain not specified"}
        
        results = {
            "domain": self.domain,
            "spf": {},
            "dkim": {},
            "dmarc": {},
            "overall_score": 0,
            "recommendations": []
        }
        
        # Check SPF
        spf_exists = self.spf.verify_record_exists()
        if spf_exists:
            results["spf"] = self.spf.analyze_record()
        else:
            results["spf"] = {"exists": False, "issues": ["No SPF record found"]}
            results["recommendations"].append("Set up an SPF record to authorize your sending servers")
        
        # Check DKIM
        dkim_exists = self.dkim.verify_record_exists()
        if dkim_exists:
            results["dkim"] = self.dkim.analyze_record()
        else:
            results["dkim"] = {"exists": False, "issues": ["No DKIM record found"]}
            results["recommendations"].append("Set up DKIM to digitally sign your emails")
        
        # Check DMARC
        dmarc_exists = self.dmarc.verify_record_exists()
        if dmarc_exists:
            results["dmarc"] = self.dmarc.analyze_record()
        else:
            results["dmarc"] = {"exists": False, "issues": ["No DMARC record found"]}
            results["recommendations"].append("Set up a DMARC policy to protect your domain")
        
        # Calculate overall score
        score = 0
        if spf_exists:
            score += 30 - min(len(results["spf"].get("issues", [])) * 5, 20)
        if dkim_exists:
            score += 30 - min(len(results["dkim"].get("issues", [])) * 5, 20)
        if dmarc_exists:
            score += 40 - min(len(results["dmarc"].get("issues", [])) * 5, 30)
        
        results["overall_score"] = max(0, score)
        
        return results
    
    def check_ip_reputation(self):
        """
        Check IP reputation on blacklists.
        
        Returns:
            dict: IP reputation data
        """
        if not self.ip:
            return {"error": "IP not specified"}
        
        return self.reputation.check_ip_blacklists()
    
    def validate_email_list(self, email_list):
        """
        Validate a list of email addresses.
        
        Args:
            email_list (list): List of email addresses
            
        Returns:
            dict: Validation results and analysis
        """
        validation_results = self.email_validator.batch_validate(email_list)
        analysis = self.email_validator.analyze_list_quality(validation_results)
        
        return {
            "results": validation_results,
            "analysis": analysis
        }
    
    def create_ip_warming_plan(self, daily_target, warmup_days=30):
        """
        Create an IP warming plan.
        
        Args:
            daily_target (int): Target daily volume
            warmup_days (int): Number of days for warmup
            
        Returns:
            dict: IP warming plan
        """
        self._ip_warming_scheduler = IPWarmingScheduler(
            daily_target=daily_target,
            warmup_days=warmup_days
        )
        
        schedule = self._ip_warming_scheduler.generate_schedule()
        recommendations = self._ip_warming_scheduler.get_recommendations()
        
        return {
            "schedule": schedule,
            "recommendations": recommendations,
            "daily_target": daily_target,
            "warmup_days": warmup_days
        }
    
    def check_deliverability_status(self):
        """
        Perform a comprehensive deliverability check.
        
        Returns:
            dict: Deliverability status summary
        """
        results = {
            "timestamp": str(datetime.now()),
            "domain": self.domain,
            "ip": self.ip,
            "authentication": {
                "spf": False,
                "dkim": False, 
                "dmarc": False,
                "overall_score": 0
            },
            "reputation": {},
            "recommendations": []
        }
        
        # Authentication setup
        if self.domain:
            try:
                auth_results = self.analyze_domain_setup()
                
                # Extract authentication data safely using the get method with defaults
                auth_data = results["authentication"]
                auth_data["spf"] = auth_results.get("spf", {}).get("exists", False)
                auth_data["dkim"] = auth_results.get("dkim", {}).get("exists", False)
                auth_data["dmarc"] = auth_results.get("dmarc", {}).get("exists", False)
                auth_data["overall_score"] = auth_results.get("overall_score", 0)
                
                # Add recommendations
                results["recommendations"].extend(auth_results.get("recommendations", []))
            except Exception as e:
                results["authentication"]["error"] = str(e)
        
        # IP reputation
        if self.ip:
            try:
                ip_results = self.check_ip_reputation()
                if "status" in ip_results:
                    results["reputation"]["ip_status"] = ip_results["status"]
                    if ip_results["status"] != "clean":
                        results["recommendations"].append(
                            "Your IP is listed on blacklists. Consider using a new IP or " +
                            "contact the blacklist operators for delisting."
                        )
            except Exception as e:
                results["reputation"]["ip_error"] = str(e)
        
        # Domain reputation
        if self.domain:
            try:
                domain_rep = self.reputation.check_domain_reputation()
                results["reputation"]["domain_score"] = domain_rep.get("reputation_score", 0)
                results["recommendations"].extend(domain_rep.get("issues", []))
            except Exception as e:
                results["reputation"]["domain_error"] = str(e)
        
        return results
