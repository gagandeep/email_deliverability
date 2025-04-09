API Reference
============

This page provides detailed API documentation for the Email Deliverability Library.

DeliverabilityManager
----------------------

.. autoclass:: email_deliverability.facade.DeliverabilityManager
   :members:
   :undoc-members:
   :show-inheritance:

Authentication
---------------

SPF
^^^

.. autoclass:: email_deliverability.authentication.spf.SPFValidator
   :members:
   :undoc-members:
   :show-inheritance:

DKIM
^^^^

.. autoclass:: email_deliverability.authentication.dkim.DKIMManager
   :members:
   :undoc-members:
   :show-inheritance:

DMARC
^^^^^

.. autoclass:: email_deliverability.authentication.dmarc.DMARCAnalyzer
   :members:
   :undoc-members:
   :show-inheritance:

Reputation
---------

.. autoclass:: email_deliverability.reputation.monitor.ReputationMonitor
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: email_deliverability.reputation.analyze.ReputationAnalyzer
   :members:
   :undoc-members:
   :show-inheritance:

List Hygiene
-------------

.. autoclass:: email_deliverability.list_hygiene.validator.EmailValidator
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: email_deliverability.list_hygiene.cleaner.ListCleaner
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: email_deliverability.list_hygiene.bounce_handler.BounceHandler
   :members:
   :undoc-members:
   :show-inheritance:

IP Warming
---------

.. autoclass:: email_deliverability.ip_warming.scheduler.IPWarmingScheduler
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: email_deliverability.ip_warming.monitor.WarmingMonitor
   :members:
   :undoc-members:
   :show-inheritance:

Resource Management
-------------------

.. autoclass:: email_deliverability.resource_manager.ResourceManager
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: email_deliverability.resource_manager.update_deliverability_resources

.. autofunction:: email_deliverability.resource_manager.start_resource_updater