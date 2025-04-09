#!/usr/bin/env python3

"""Debug script for resource files."""
import os
import json
from email_deliverability.resource_manager import debug_resource

def main():
    """Print debug information for all resources."""
    resources = [
        "disposable_domains",
        "dnsbl_list", 
        "tld_list",
        "ip_reputation_providers"
    ]
    
    print("=== Resource Debug Information ===")
    
    for resource in resources:
        print(f"\n--- {resource} ---")
        info = debug_resource(resource)
        
        for key, value in info.items():
            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                print(f"{key}: {type(value)} with {len(value)} items")
            else:
                print(f"{key}: {value}")
    
    print("\n=== Cache Files ===")
    cache_dir = os.path.join(os.path.expanduser("~"), ".email_deliverability")
    
    for filename in os.listdir(cache_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(cache_dir, filename)
            size = os.path.getsize(filepath)
            print(f"{filename}: {size} bytes")
            
            # Check file contents
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"  List length: {len(data)}")
                    else:
                        print(f"  Type: {type(data)}")
            except json.JSONDecodeError:
                print("  Not valid JSON")
            except Exception as e:
                print(f"  Error reading file: {e}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
