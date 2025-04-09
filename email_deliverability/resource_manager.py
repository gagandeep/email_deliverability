"""Resource management for email deliverability data."""
import os
import json
import requests
import time
import logging
from datetime import datetime
import threading

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("email_deliverability.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('email_deliverability.resources')


class ResourceManager:
    """Manage external resources like blacklists and IP reputation data."""
    
    _instance = None  # Singleton instance
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, cache_dir=None):
        """
        Initialize the resource manager.
        
        Args:
            cache_dir (str): Directory to store cached resources
        """
        # Only initialize once (singleton pattern)
        if ResourceManager._initialized:
            return
            
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".email_deliverability")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Track the last download time for each resource
        self.last_download_time = {}
        self._last_download_file = os.path.join(self.cache_dir, "last_download.json")
        self._load_download_times()
        
        # Prevent multiple threads from updating resources simultaneously
        self._lock = threading.RLock()
        
        # Flag to track whether the update scheduler is running
        self._scheduler_running = False
        self._scheduler_thread = None
        
        # List of registered resources
        self.resources = {
            "disposable_domains": {
                "url": "https://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/master/disposable_email_blocklist.conf",
                "processor": lambda data: data.strip().split('\n')
            },
            "dnsbl_list": {
                # Instead of relying on external sources that might disappear, use a comprehensive built-in list
                "fallback": [
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
            },
            "tld_list": {
                "url": "https://data.iana.org/TLD/tlds-alpha-by-domain.txt",
                "processor": lambda data: [line.strip().lower() for line in data.split('\n') 
                                         if line.strip() and not line.startswith('#')]
            },
            "ip_reputation_providers": {
                # Use built-in list of reputation providers instead of relying on external sources
                "fallback": {
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
            }
        }
        
        ResourceManager._initialized = True
    
    def _load_download_times(self):
        """Load last download times from file."""
        try:
            if os.path.exists(self._last_download_file):
                with open(self._last_download_file, 'r') as f:
                    self.last_download_time = json.load(f)
        except (json.JSONDecodeError, IOError):
            self.last_download_time = {}
    
    def _save_download_times(self):
        """Save last download times to file."""
        try:
            with open(self._last_download_file, 'w') as f:
                json.dump(self.last_download_time, f)
        except IOError:
            logger.error("Failed to save resource download times", exc_info=True)
    
    def needs_update(self, resource_name, max_age_hours=24):
        """
        Check if a resource needs updating.
        
        Args:
            resource_name (str): Name of the resource
            max_age_hours (int): Maximum age in hours before update needed
            
        Returns:
            bool: True if the resource needs updating
        """
        if resource_name not in self.last_download_time:
            return True
            
        last_time = self.last_download_time[resource_name]
        current_time = int(time.time())
        age_in_seconds = current_time - last_time
        
        return age_in_seconds > (max_age_hours * 3600)
    
    def download_resource(self, resource_name, url=None, processor=None, force=False):
        """
        Download and cache an external resource.
        
        Args:
            resource_name (str): Name of the resource
            url (str): URL to download the resource from
            processor (callable): Function to process the downloaded data
            force (bool): Force download even if not needed
            
        Returns:
            object: The downloaded resource data
        """
        # Use registered resource info if not provided
        resource_info = {}
        if resource_name in self.resources:
            resource_info = self.resources[resource_name]
            if not url:
                url = resource_info.get("url")
            if not processor:
                processor = resource_info.get("processor")
            
        # For resources without URLs (like dnsbl_list), use fallback directly
        if not url:
            logger.info(f"No URL provided for resource: {resource_name}, using fallback")
            return self._use_fallback_or_cached(resource_name, resource_info)
            
        with self._lock:
            if not force and not self.needs_update(resource_name):
                return self.load_resource(resource_name)
            
            logger.info(f"Downloading resource: {resource_name}")
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.text
                
                # Process the data if a processor function is provided
                if processor and callable(processor):
                    data = processor(data)
                
                # Save the processed data
                resource_path = os.path.join(self.cache_dir, f"{resource_name}.json")
                with open(resource_path, 'w') as f:
                    if isinstance(data, (dict, list)):
                        json.dump(data, f)
                    else:
                        f.write(str(data))
                
                # Update the last download time
                self.last_download_time[resource_name] = int(time.time())
                self._save_download_times()
                
                return data
                
            except Exception as e:
                logger.error(f"Failed to download resource {resource_name}: {str(e)}", exc_info=True)
                # Return cached version or fallback data
                return self._use_fallback_or_cached(resource_name, resource_info)
    
    def _use_fallback_or_cached(self, resource_name, resource_info):
        """Use fallback data or cached data for a resource."""
        # Try cached version first
        cached_data = self._load_cached_resource(resource_name)
        
        # Special checks for cached data validity
        if cached_data is not None:
            if resource_name == "ip_reputation_providers":
                if isinstance(cached_data, dict) and "providers" in cached_data and len(cached_data["providers"]) == 0:
                    logger.info(f"Cached {resource_name} has empty providers list, using fallback instead")
                    cached_data = None  # Force using fallback instead
            elif resource_name == "dnsbl_list":
                # Ensure DNSBL list has all our blacklists
                if isinstance(cached_data, list) and len(cached_data) < len(resource_info.get("fallback", [])):
                    logger.info(f"Cached {resource_name} is missing items, using fallback instead")
                    cached_data = None  # Force using fallback
        
        if cached_data is not None:
            logger.info(f"Using cached data for {resource_name}")
            return cached_data
            
        # Use fallback data if available
        if resource_info and "fallback" in resource_info:
            fallback_data = resource_info["fallback"]
            logger.info(f"Using fallback data for {resource_name}: {type(fallback_data)}")
            
            # Save fallback data to cache
            resource_path = os.path.join(self.cache_dir, f"{resource_name}.json")
            try:
                with open(resource_path, 'w') as f:
                    if isinstance(fallback_data, (dict, list)):
                        json.dump(fallback_data, f, indent=2)  # Use pretty-printing for better debugging
                        logger.info(f"Saved fallback data to {resource_path}")
                    else:
                        f.write(str(fallback_data))
                
                # Update the last download time to prevent immediate re-download attempts
                self.last_download_time[resource_name] = int(time.time())
                self._save_download_times()
                
                return fallback_data
            except IOError as e:
                logger.error(f"Failed to save fallback data for {resource_name}: {str(e)}")
                return fallback_data
                    
        return None
    
    def _load_cached_resource(self, resource_name):
        """Load a resource from cache."""
        resource_path = os.path.join(self.cache_dir, f"{resource_name}.json")
        
        if not os.path.exists(resource_path):
            return None
            
        try:
            with open(resource_path, 'r') as f:
                try:
                    data = json.load(f)
                    logger.debug(f"Loaded JSON data for {resource_name}: {type(data)}")
                    return data
                except json.JSONDecodeError:
                    # Not a JSON file, return as text
                    f.seek(0)
                    data = f.read()
                    logger.debug(f"Loaded text data for {resource_name}")
                    return data
        except IOError:
            logger.error(f"Failed to load resource {resource_name} from cache", exc_info=True)
            return None
    
    def load_resource(self, resource_name):
        """
        Load a cached resource.
        
        Args:
            resource_name (str): Name of the resource
            
        Returns:
            object: The cached resource data or None if not available
        """
        # Try to load from cache
        cached_data = self._load_cached_resource(resource_name)
        if cached_data is not None:
            return cached_data
            
        # If not in cache, try to download if resource is registered
        if resource_name in self.resources:
            return self.download_resource(resource_name)
            
        # If all else fails, return fallback data if available
        if resource_name in self.resources and "fallback" in self.resources[resource_name]:
            return self.resources[resource_name]["fallback"]
            
        return None
    
    def update_all_resources(self):
        """Update all registered resources."""
        results = {}
        
        for name, info in self.resources.items():
            logger.info(f"Updating resource: {name}")
            data = self.download_resource(name, force=True)
            
            # Debug log to see what we're working with
            logger.info(f"Downloaded data type for {name}: {type(data)}")
            if isinstance(data, dict):
                logger.info(f"Dictionary keys: {list(data.keys())}")
            
            item_count = 0
            
            if data:
                # Calculate item count based on resource type and data structure
                if name == "dnsbl_list":
                    if isinstance(data, list):
                        item_count = len(data)
                    else:
                        # If it's not a list, log and use fallback length
                        logger.warning(f"Expected list for dnsbl_list but got {type(data)}")
                        item_count = len(info.get("fallback", []))
                
                elif name == "ip_reputation_providers":
                    # This is a special case with nested structure
                    if isinstance(data, dict) and "providers" in data:
                        logger.info(f"Found providers key with {len(data['providers'])} items")
                        item_count = len(data["providers"])
                    else:
                        # If structure doesn't match what we expect, log details
                        logger.warning(f"Expected dict with 'providers' key for {name}, got: {data}")
                        # Try to use fallback length
                        try:
                            item_count = len(info.get("fallback", {}).get("providers", []))
                            logger.info(f"Using fallback length: {item_count}")
                        except (TypeError, AttributeError) as e:
                            logger.error(f"Error getting fallback length: {e}")
                            item_count = 0
                
                else:
                    # Standard resources
                    if isinstance(data, list):
                        item_count = len(data)
                    elif isinstance(data, dict):
                        item_count = len(data)
                    else:
                        try:
                            item_count = len(data)
                        except:
                            item_count = 0
                            logger.warning(f"Could not determine item count for {name}")
                
                # Log the final count for debugging
                logger.info(f"Final item count for {name}: {item_count}")
                
                # Use UTC time for timestamps
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                
                results[name] = {
                    "status": "updated",
                    "timestamp": timestamp,
                    "items": item_count
                }
            else:
                results[name] = {
                    "status": "failed",
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                }
        
        logger.info(f"Resource update completed: {json.dumps(results)}")
        return results
    
    def start_scheduler(self, update_time="00:00"):
        """
        Start a background scheduler to update resources daily.
        
        Args:
            update_time (str): Time to update resources daily (HH:MM format)
        """
        if self._scheduler_running:
            logger.warning("Resource update scheduler is already running")
            return False
            
        def _run_scheduler():
            # Import here to avoid circular imports
            import schedule
            
            schedule.every().day.at(update_time).do(self.update_all_resources)
            
            while self._scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        self._scheduler_running = True
        self._scheduler_thread = threading.Thread(target=_run_scheduler, daemon=True)
        self._scheduler_thread.start()
        
        logger.info(f"Resource update scheduler started, updates at {update_time} daily")
        return True
    
    def stop_scheduler(self):
        """Stop the background resource update scheduler."""
        if not self._scheduler_running:
            logger.warning("Resource update scheduler is not running")
            return False
            
        self._scheduler_running = False
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=2)
            
        logger.info("Resource update scheduler stopped")
        return True


# Create a function to update resources on demand
def update_deliverability_resources():
    """
    Update all email deliverability resources.
    This function can be called directly or scheduled to run periodically.
    
    Returns:
        dict: Status of each resource update
    """
    manager = ResourceManager()
    return manager.update_all_resources()


# Create a function to start the background scheduler
def start_resource_updater(update_time="03:00"):
    """
    Start the background resource updater to refresh data daily.
    
    Args:
        update_time (str): Time to update resources daily (HH:MM format)
        
    Returns:
        bool: True if scheduler started successfully
    """
    manager = ResourceManager()
    return manager.start_scheduler(update_time)


# Add a debugging function to examine resource data
def debug_resource(resource_name):
    """
    Debug a specific resource by examining its data structure.
    
    Args:
        resource_name (str): Name of the resource to debug
        
    Returns:
        dict: Debug information for the resource
    """
    manager = ResourceManager()
    data = manager.load_resource(resource_name)
    
    result = {
        "resource_name": resource_name,
        "type": str(type(data))
    }
    
    if data is None:
        result["status"] = "not_found"
        return result
    
    result["status"] = "found"
    
    if isinstance(data, dict):
        result["keys"] = list(data.keys())
        result["sample"] = {k: data[k] for k in list(data.keys())[:2]} if data else {}
        
        # Special handling for nested structures
        if "providers" in data and isinstance(data["providers"], list):
            result["providers_count"] = len(data["providers"])
            result["provider_sample"] = data["providers"][0] if data["providers"] else None
    elif isinstance(data, list):
        result["length"] = len(data)
        result["sample"] = data[:2] if data else []
    else:
        try:
            result["length"] = len(data)
            result["preview"] = str(data)[:100]
        except:
            result["note"] = "Could not determine length or preview"
    
    return result