"""Handle and analyze email bounces to maintain list hygiene."""
import csv
import io
from datetime import datetime, timedelta
import re


class BounceHandler:
    def __init__(self):
        """Initialize bounce handler."""
        self.bounce_categories = {
            "hard": [
                "550", "5.1.1", "unknown user", "recipient rejected", 
                "does not exist", "no such user", "invalid recipient",
                "recipient address rejected"
            ],
            "soft": [
                "421", "450", "451", "452", "4.2.2", "4.3.1", "4.4.1", "4.4.2",
                "mailbox full", "over quota", "connection refused", "timeout"
            ],
            "spam_block": [
                "550 5.7.1", "554 5.7.1", "blocked", "spam", "bulk", 
                "rejected due to reputation", "policy rejection"
            ]
        }
    
    def categorize_bounce(self, bounce_message):
        """
        Categorize a bounce message based on its content.
        
        Args:
            bounce_message (str): The bounce message text
            
        Returns:
            str: Bounce type (hard, soft, spam_block, or unknown)
        """
        lower_message = bounce_message.lower()
        
        for category, indicators in self.bounce_categories.items():
            for indicator in indicators:
                if indicator.lower() in lower_message:
                    return category
        
        return "unknown"
    
    def parse_bounce_logs(self, logs_data, format_type="csv"):
        """
        Parse bounce logs from various formats.
        
        Args:
            logs_data (str): Log data content
            format_type (str): Format type (csv, json, etc.)
            
        Returns:
            list: Parsed bounce records
        """
        parsed_bounces = []
        
        if format_type == "csv":
            csv_data = io.StringIO(logs_data)
            reader = csv.DictReader(csv_data)
            for row in reader:
                bounce_info = {
                    "email": row.get("email", ""),
                    "timestamp": row.get("timestamp", ""),
                    "reason": row.get("reason", ""),
                    "type": row.get("type", self.categorize_bounce(row.get("reason", "")))
                }
                parsed_bounces.append(bounce_info)
        
        # Could add more formats here (JSON, etc.)
        
        return parsed_bounces
    
    def extract_emails_from_bounces(self, bounces, bounce_types=None):
        """
        Extract email addresses from bounce records.
        
        Args:
            bounces (list): List of bounce records
            bounce_types (list): Types of bounces to include (hard, soft, etc.)
            
        Returns:
            list: List of unique email addresses
        """
        if bounce_types is None:
            bounce_types = ["hard"]
            
        bounced_emails = set()
        
        for bounce in bounces:
            if bounce.get("type") in bounce_types and "email" in bounce:
                bounced_emails.add(bounce["email"])
        
        return list(bounced_emails)
    
    def extract_domains_from_bounces(self, bounces, min_occurrences=3):
        """
        Extract problematic domains from bounce records.
        
        Args:
            bounces (list): List of bounce records
            min_occurrences (int): Minimum occurrences to consider a domain problematic
            
        Returns:
            dict: Domain statistics
        """
        domain_counts = {}
        
        for bounce in bounces:
            email = bounce.get("email", "")
            if '@' in email:
                domain = email.split('@')[-1].lower()
                
                if domain not in domain_counts:
                    domain_counts[domain] = {"total": 0, "hard": 0, "soft": 0, "spam_block": 0}
                    
                domain_counts[domain]["total"] += 1
                bounce_type = bounce.get("type", "unknown")
                if bounce_type in domain_counts[domain]:
                    domain_counts[domain][bounce_type] += 1
        
        # Filter by minimum occurrences
        problematic_domains = {
            domain: stats for domain, stats in domain_counts.items()
            if stats["total"] >= min_occurrences
        }
        
        return problematic_domains
    
    def analyze_bounce_patterns(self, bounces):
        """
        Analyze patterns in bounce data.
        
        Args:
            bounces (list): List of bounce records
            
        Returns:
            dict: Bounce analysis
        """
        if not bounces:
            return {"status": "no_data"}
            
        total_count = len(bounces)
        types = {"hard": 0, "soft": 0, "spam_block": 0, "unknown": 0}
        
        # Group by time periods
        by_hour = [0] * 24
        by_day = [0] * 7
        
        # Extract common reasons
        reasons = {}
        
        for bounce in bounces:
            # Count by type
            bounce_type = bounce.get("type", "unknown")
            if bounce_type in types:
                types[bounce_type] += 1
            else:
                types["unknown"] += 1
                
            # Count by time
            timestamp = bounce.get("timestamp")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    by_hour[dt.hour] += 1
                    by_day[dt.weekday()] += 1
                except (ValueError, TypeError):
                    pass
            
            # Count reasons
            reason = bounce.get("reason", "").lower()
            if reason:
                # Extract key phrases
                for phrase in self._extract_key_phrases(reason):
                    if phrase not in reasons:
                        reasons[phrase] = 0
                    reasons[phrase] += 1
        
        # Calculate percentages
        type_percentages = {
            bounce_type: count / total_count * 100
            for bounce_type, count in types.items()
        }
        
        # Sort reasons by frequency
        top_reasons = sorted(
            reasons.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Find peak hours and days
        peak_hour = by_hour.index(max(by_hour)) if max(by_hour) > 0 else -1
        peak_day = by_day.index(max(by_day)) if max(by_day) > 0 else -1
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        analysis = {
            "total_bounces": total_count,
            "by_type": type_percentages,
            "top_reasons": dict(top_reasons),
            "peak_hour": peak_hour,
            "peak_day": day_names[peak_day] if peak_day >= 0 else None,
        }
        
        # Generate recommendations
        recommendations = []
        
        if type_percentages["hard"] > 5:
            recommendations.append(
                "Hard bounce rate is high (>5%). Clean your list and implement " +
                "real-time email validation."
            )
            
        if type_percentages["spam_block"] > 2:
            recommendations.append(
                "High rate of spam blocks. Review your authentication setup and content."
            )
            
        analysis["recommendations"] = recommendations
        
        return analysis
    
    def _extract_key_phrases(self, text):
        """Extract key phrases from bounce reason text."""
        # Common bounce reason phrases
        phrases = [
            "mailbox full", "user unknown", "does not exist", 
            "rejected", "blocked", "spam content",
            "connection refused", "greylisted", "timeout",
            "quota exceeded", "policy violation"
        ]
        
        found_phrases = []
        for phrase in phrases:
            if phrase in text:
                found_phrases.append(phrase)
                
        # If no known phrases were found, extract the first error code
        if not found_phrases:
            # Try to find error codes like "550 5.1.1"
            error_codes = re.findall(r'\d{3}\s\d\.\d\.\d', text)
            if error_codes:
                found_phrases.append(error_codes[0])
                
        return found_phrases