#!/usr/bin/env python3

"""Fix script for DNSBL list resource."""
import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def fix_dnsbl_list():
    """Fix the DNSBL list resource."""
    # Define the fallback data - the complete list of DNSBLs
    fallback_data = [
        # Spamhaus blocklists
        "zen.spamhaus.org",
        "sbl.spamhaus.org",
        "xbl.spamhaus.org",
        "pbl.spamhaus.org",
        "sbl-xbl.spamhaus.org",
        "dbl.spamhaus.org",
        
        # SpamCop
        "bl.spamcop.net",
        
        # Barracuda
        "b.barracudacentral.org",
        
        # SORBS
        "dnsbl.sorbs.net",
        "spam.dnsbl.sorbs.net",
        "web.dnsbl.sorbs.net",
        "zombie.dnsbl.sorbs.net",
        "dul.dnsbl.sorbs.net",
        "smtp.dnsbl.sorbs.net",
        "new.spam.dnsbl.sorbs.net",
        
        # URIBL
        "multi.uribl.com",
        "black.uribl.com",
        "red.uribl.com",
        "uribl.spameatingmonkey.net",
        
        # Other popular DNSBLs
        "dnsbl-1.uceprotect.net",
        "dnsbl-2.uceprotect.net",
        "dnsbl-3.uceprotect.net",
        "dnsbl.dronebl.org",
        "cbl.abuseat.org",
        "bl.deadbeef.com",
        "bl.emailbasura.org",
        "bl.spamcannibal.org",
        "blackholes.mail-abuse.org",
        "bogons.cymru.com",
        "combined.abuse.ch",
        "db.wpbl.info",
        "rbl.interserver.net",
        "relays.mail-abuse.org",
        "truncate.gbudb.net",
        "psbl.surriel.com",
        "mailspike.net"
    ]
    
    # Get cache directory path
    cache_dir = os.path.join(os.path.expanduser("~"), ".email_deliverability")
    resource_path = os.path.join(cache_dir, "dnsbl_list.json")
    
    # Check if the resource file exists
    if os.path.exists(resource_path):
        try:
            # Read the current file
            with open(resource_path, 'r') as f:
                current_data = json.load(f)
            
            # Check if incomplete list
            if isinstance(current_data, list) and len(current_data) < len(fallback_data):
                logger.info(f"Found incomplete DNSBL list ({len(current_data)} vs {len(fallback_data)} items), replacing with fallback data")
                
                # Write the fallback data
                with open(resource_path, 'w') as f:
                    json.dump(fallback_data, f, indent=2)
                
                logger.info(f"Fixed DNSBL list resource with {len(fallback_data)} DNSBLs")
                return True
            else:
                logger.info("Resource file exists and appears to be valid, no action needed")
                return False
                
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error processing resource file: {str(e)}")
            
            # Write the fallback data if there was an error
            with open(resource_path, 'w') as f:
                json.dump(fallback_data, f, indent=2)
            
            logger.info(f"Created new DNSBL list resource with {len(fallback_data)} DNSBLs")
            return True
    else:
        # File doesn't exist, create it
        os.makedirs(cache_dir, exist_ok=True)
        
        with open(resource_path, 'w') as f:
            json.dump(fallback_data, f, indent=2)
        
        logger.info(f"Created new DNSBL list resource with {len(fallback_data)} DNSBLs")
        return True

if __name__ == "__main__":
    fixed = fix_dnsbl_list()
    print(f"Resource fixed: {fixed}")