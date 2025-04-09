"""Utilities for email authentication."""
import base64
import hashlib
import re
from urllib.parse import urlparse


def is_valid_domain(domain):
    """
    Check if a domain name is valid.
    
    Args:
        domain (str): Domain name to check
        
    Returns:
        bool: True if domain is valid
    """
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))


def get_domain_from_email(email):
    """
    Extract domain from email address.
    
    Args:
        email (str): Email address
        
    Returns:
        str: Domain name
    """
    if '@' not in email:
        return None
    return email.split('@')[-1].lower()


def calculate_domain_hash(domain, algorithm="sha256"):
    """
    Calculate a hash of a domain name.
    
    Args:
        domain (str): Domain to hash
        algorithm (str): Hash algorithm to use
        
    Returns:
        str: Base64-encoded hash
    """
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
    hasher.update(domain.encode('utf-8'))
    return base64.b64encode(hasher.digest()).decode('utf-8')


def parse_dmarc_uri(uri):
    """
    Parse a DMARC reporting URI (mailto: or https:).
    
    Args:
        uri (str): URI to parse
        
    Returns:
        dict: Parsed URI components
    """
    if not uri:
        return None
        
    if uri.startswith('mailto:'):
        email = uri[7:]  # Remove 'mailto:'
        return {
            'scheme': 'mailto',
            'address': email,
            'params': {}
        }
    else:
        parsed = urlparse(uri)
        return {
            'scheme': parsed.scheme,
            'host': parsed.netloc,
            'path': parsed.path,
            'params': dict(param.split('=') for param in parsed.query.split('&') if '=' in param)
        }


def normalize_domain(domain):
    """
    Normalize a domain name (lowercase, remove trailing dot).
    
    Args:
        domain (str): Domain name to normalize
        
    Returns:
        str: Normalized domain
    """
    if not domain:
        return None
        
    domain = domain.lower().strip()
    if domain.endswith('.'):
        domain = domain[:-1]
    return domain