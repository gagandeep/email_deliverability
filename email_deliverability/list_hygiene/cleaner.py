"""Tools for cleaning and maintaining email lists."""
from .validator import EmailValidator
from concurrent.futures import ThreadPoolExecutor


class ListCleaner:
    def __init__(self, verification_timeout=10):
        """
        Initialize list cleaner.
        
        Args:
            verification_timeout (int): Timeout for email verification in seconds
        """
        self.validator = EmailValidator(timeout=verification_timeout)
        
    def clean_list(self, email_list, max_workers=5, strict_mode=False):
        """
        Clean an email list by removing invalid addresses.
        
        Args:
            email_list (list): List of email addresses to clean
            max_workers (int): Maximum number of parallel workers
            strict_mode (bool): If True, removes disposable emails too
            
        Returns:
            dict: Cleaning results
        """
        if not email_list:
            return {
                "input_count": 0,
                "valid_emails": [],
                "invalid_emails": [],
                "disposable_emails": [],
                "summary": "No emails provided"
            }
            
        # Validate all emails
        results = self.validator.batch_validate(email_list, max_workers=max_workers)
        
        valid_emails = []
        invalid_emails = []
        disposable_emails = []
        
        for result in results:
            email = result["email"]
            
            if not result["is_valid"]:
                invalid_emails.append(email)
            elif result["is_disposable"]:
                disposable_emails.append(email)
                # In strict mode, disposable emails are considered invalid
                if not strict_mode:
                    valid_emails.append(email)
            else:
                valid_emails.append(email)
        
        return {
            "input_count": len(email_list),
            "valid_emails": valid_emails,
            "invalid_emails": invalid_emails,
            "disposable_emails": disposable_emails,
            "summary": f"Removed {len(invalid_emails)} invalid emails" + 
                      (f" and {len(disposable_emails)} disposable emails" if strict_mode else "")
        }
    
    def deduplicate_list(self, email_list, case_sensitive=False):
        """
        Remove duplicate emails from a list.
        
        Args:
            email_list (list): List of email addresses
            case_sensitive (bool): Whether to treat case differences as distinct
            
        Returns:
            dict: Deduplication results
        """
        if not email_list:
            return {
                "input_count": 0,
                "output_count": 0,
                "duplicates_removed": 0,
                "deduplicated_list": []
            }
            
        # Track seen emails
        seen_emails = set()
        deduplicated = []
        duplicates = []
        
        for email in email_list:
            check_email = email if case_sensitive else email.lower()
            
            if check_email not in seen_emails:
                seen_emails.add(check_email)
                deduplicated.append(email)
            else:
                duplicates.append(email)
        
        return {
            "input_count": len(email_list),
            "output_count": len(deduplicated),
            "duplicates_removed": len(duplicates),
            "deduplicated_list": deduplicated
        }
    
    def segment_by_domain(self, email_list):
        """
        Segment an email list by domain.
        
        Args:
            email_list (list): List of email addresses
            
        Returns:
            dict: Email addresses grouped by domain
        """
        segments = {}
        
        for email in email_list:
            if '@' in email:
                domain = email.split('@')[-1].lower()
                
                if domain not in segments:
                    segments[domain] = []
                    
                segments[domain].append(email)
        
        return segments
    
    def find_typos(self, email_list, common_domains=None):
        """
        Find potential typos in domain names.
        
        Args:
            email_list (list): List of email addresses
            common_domains (list): List of common domains to check against
            
        Returns:
            dict: Emails with potential domain typos
        """
        if common_domains is None:
            common_domains = [
                "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
                "aol.com", "icloud.com", "protonmail.com", "mail.com"
            ]
            
        potential_typos = []
        
        for email in email_list:
            if '@' not in email:
                continue
                
            domain = email.split('@')[-1].lower()
            
            # Skip exact matches
            if domain in common_domains:
                continue
                
            # Check for close matches (simple Levenshtein distance)
            for common_domain in common_domains:
                if self._calculate_distance(domain, common_domain) <= 2:
                    potential_typos.append({
                        "email": email,
                        "domain": domain,
                        "suggested_domain": common_domain,
                        "suggested_email": email.split('@')[0] + '@' + common_domain
                    })
                    break
        
        return potential_typos
        
    def _calculate_distance(self, s1, s2):
        """Calculate Levenshtein distance between two strings."""
        if len(s1) > len(s2):
            s1, s2 = s2, s1
            
        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
            
        return distances[-1]