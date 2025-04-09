#!/usr/bin/env python3
"""Verify all resources are updating correctly."""

from email_deliverability.resource_manager import update_deliverability_resources

def main():
    """Run a final verification of all resources."""
    print("Updating all resources...")
    results = update_deliverability_resources()
    
    print("\n=== Resource Update Results ===")
    for resource, info in results.items():
        print(f"{resource}: {info['items']} items (Status: {info['status']})")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    main()