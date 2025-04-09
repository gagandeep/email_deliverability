"""Utility functions for email deliverability management."""
import os
import json
import requests
import time
from datetime import datetime
import logging
import hashlib
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

logger = logging.getLogger('email_deliverability')


class ResourceManager:
    """Manage external resources like blacklists and IP reputation data."""
    
    def __init__(self, cache_dir=None):
        """
        Initialize the resource manager.
        
        Args:
            cache_dir (str): Directory to store cached resources
        """
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".email_deliverability")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Track the last download time for each resource
        self.last_download_time = {}
        self._last_download_file = os.path.join(self.cache_dir, "last_download.json")
        self._load_download_times()
        
        # Prevent multiple threads from updating resources simultaneously
        self._lock = threading.RLock()
    
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
    
    def download_resource(self, resource_name, url, processor=None, force=False):
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
                # Return cached version if available, otherwise return None
                return self.load_resource(resource_name)
    
    def load_resource(self, resource_name):
        """
        Load a cached resource.
        
        Args:
            resource_name (str): Name of the resource
            
        Returns:
            object: The cached resource data or None if not available
        """
        resource_path = os.path.join(self.cache_dir, f"{resource_name}.json")
        
        if not os.path.exists(resource_path):
            return None
            
        try:
            with open(resource_path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    # Not a JSON file, return as text
                    f.seek(0)
                    return f.read()
        except IOError:
            logger.error(f"Failed to load resource {resource_name}", exc_info=True)
            return None


def update_all_resources():
    """
    Update all external resources used by the library.
    This function should be called periodically (e.g., once a day).
    """
    resource_manager = ResourceManager()
    
    # Define resources to download
    resources = {
        "disposable_domains": {
            "url": "https://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/master/disposable_email_blocklist.conf",
            "processor": lambda data: data.strip().split('\n')
        },
        "dnsbl_list": {
            "url": "https://raw.githubusercontent.com/inSileco/inSilecoRef/master/dnsblList.md",
            "processor": lambda data: [
                line.replace('|', '').strip() 
                for line in data.split('\n') 
                if '|' in line and not line.startswith('|--') and not line.startswith('| DQ') and 'URL' not in line
            ]
        }
    }
    
    results = {}
    
    for name, info in resources.items():
        logger.info(f"Updating resource: {name}")
        data = resource_manager.download_resource(
            name,
            info["url"],
            info.get("processor"),
            force=True
        )
        
        if data:
            results[name] = {
                "status": "updated",
                "timestamp": str(datetime.now()),
                "items": len(data) if isinstance(data, list) else "unknown"
            }
        else:
            results[name] = {
                "status": "failed",
                "timestamp": str(datetime.now())
            }
    
    logger.info(f"Resource update completed: {json.dumps(results)}")
    return results


def get_client_ip():
    """
    Get the client's external IP address.
    
    Returns:
        str: The external IP address
    """
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        logger.error("Failed to get external IP address", exc_info=True)
        return None


def calculate_file_hash(filepath):
    """
    Calculate a hash of a file's contents.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        str: SHA-256 hash of the file
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except IOError:
        logger.error(f"Failed to hash file {filepath}", exc_info=True)
        return None