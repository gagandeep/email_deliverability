#!/usr/bin/env python3

"""Fix script for IP reputation providers resource."""
import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def fix_reputation_providers():
    """Fix the IP reputation providers resource."""
    # Define the fallback data
    fallback_data = {
        "providers": [
            {"name": "Spamhaus", "url": "https://www.spamhaus.org/"},
            {"name": "SpamCop", "url": "https://www.spamcop.net/"},
            {"name": "Barracuda", "url": "https://www.barracuda.com/"},
            {"name": "SORBS", "url": "http://www.sorbs.net/"},
            {"name": "URIBL", "url": "https://uribl.com/"},
            {"name": "SURBL", "url": "https://www.surbl.org/"},
            {"name": "SpamRats", "url": "https://www.spamrats.com/"},
            {"name": "MailSpike", "url": "https://mailspike.org/"},
            {"name": "Invaluement", "url": "https://www.invaluement.com/"},
            {"name": "Passive Spam Block List", "url": "https://psbl.org/"},
            {"name": "Composite Blocking List", "url": "https://www.abuseat.org/"},
            {"name": "Proofpoint IP Reputation", "url": "https://www.proofpoint.com/"},
            {"name": "Cloudmark", "url": "https://www.cloudmark.com/"},
            {"name": "TrustedSource", "url": "https://www.trustedsource.org/"}
        ]
    }
    
    # Get cache directory path
    cache_dir = os.path.join(os.path.expanduser("~"), ".email_deliverability")
    resource_path = os.path.join(cache_dir, "ip_reputation_providers.json")
    
    # Check if the resource file exists
    if os.path.exists(resource_path):
        try:
            # Read the current file
            with open(resource_path, 'r') as f:
                current_data = json.load(f)
            
            # Check if empty providers
            if isinstance(current_data, dict) and "providers" in current_data and len(current_data["providers"]) == 0:
                logger.info("Found empty providers list, replacing with fallback data")
                
                # Write the fallback data
                with open(resource_path, 'w') as f:
                    json.dump(fallback_data, f, indent=2)
                
                logger.info(f"Fixed IP reputation providers resource with {len(fallback_data['providers'])} providers")
                return True
            else:
                logger.info("Resource file exists and appears to be valid, no action needed")
                return False
                
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error processing resource file: {str(e)}")
            
            # Write the fallback data if there was an error
            with open(resource_path, 'w') as f:
                json.dump(fallback_data, f, indent=2)
            
            logger.info(f"Created new IP reputation providers resource with {len(fallback_data['providers'])} providers")
            return True
    else:
        # File doesn't exist, create it
        os.makedirs(cache_dir, exist_ok=True)
        
        with open(resource_path, 'w') as f:
            json.dump(fallback_data, f, indent=2)
        
        logger.info(f"Created new IP reputation providers resource with {len(fallback_data['providers'])} providers")
        return True

if __name__ == "__main__":
    fixed = fix_reputation_providers()
    print(f"Resource fixed: {fixed}")
