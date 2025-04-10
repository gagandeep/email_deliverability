"""
Email Deliverability Management Library

A comprehensive library for managing email deliverability, including:
- Email authentication (SPF, DKIM, DMARC)
- Sender reputation monitoring
- Email list hygiene
- IP warming

Provides both individual tools and a unified facade interface.
"""

__version__ = '0.1.3'

# Import functions directly to avoid circular imports
from .resource_manager import update_deliverability_resources, start_resource_updater

# Import main facade class after resource functions
from .facade import DeliverabilityManager

# Define public API
__all__ = [
    'DeliverabilityManager',
    'update_deliverability_resources',
    'start_resource_updater',
]