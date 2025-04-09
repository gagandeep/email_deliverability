Quick Start Guide
===============

This guide will help you get started with the Email Deliverability Library quickly.

Basic Setup
----------

First, import the main class:

.. code-block:: python

   from email_deliverability import DeliverabilityManager

Initialize the manager with your domain and sending IP:

.. code-block:: python

   manager = DeliverabilityManager(
       domain="yourdomain.com", 
       ip="192.0.2.10",
       auto_update_resources=True  # Automatically update resources daily
   )

Authentication Analysis
---------------------

Check your domain's authentication setup:

.. code-block:: python

   # Analyze SPF, DKIM, and DMARC setup
   auth_results = manager.analyze_domain_setup()
   
   # Print the overall score
   print(f"Authentication Score: {auth_results['overall_score']}/100")
   
   # Check what issues were found
   for mechanism, data in auth_results.items():
       if mechanism in ['spf', 'dkim', 'dmarc'] and data.get('issues'):
           print(f"{mechanism.upper()} issues:")
           for issue in data['issues']:
               print(f"  - {issue}")
   
   # Get recommendations
   print("\nRecommendations:")
   for rec in auth_results['recommendations']:
       print(f"- {rec}")

Reputation Monitoring
-------------------

Check if your IP is blacklisted:

.. code-block:: python

   ip_results = manager.check_ip_reputation()
   
   if ip_results['status'] == 'clean':
       print("IP is not blacklisted!")
   else:
       print(f"IP is blacklisted on {len(ip_results['blacklisted_on'])} blacklists:")
       for bl in ip_results['blacklisted_on']:
           print(f"- {bl}")

Email List Validation
-------------------

Validate a list of email addresses:

.. code-block:: python

   emails = [
       "user@example.com", 
       "invalid@nonexistent.domain", 
       "test@mailinator.com"
   ]
   
   validation_results = manager.validate_email_list(emails)
   
   # Print quality assessment
   analysis = validation_results['analysis']
   print(f"List Quality: {analysis['quality_level']} ({analysis['quality_score']}%)")
   print(f"Valid emails: {analysis['valid_emails']}/{analysis['total_emails']}")
   print(f"Disposable emails: {analysis['disposable_emails']}")
   
   # Print recommendations for improving list quality
   print("\nRecommendations:")
   for rec in analysis['recommendations']:
       print(f"- {rec}")

IP Warming Plan Creation
----------------------

Create an IP warming plan for a new sending IP:

.. code-block:: python

   warming_plan = manager.create_ip_warming_plan(daily_target=10000, warmup_days=30)
   
   # Print the schedule
   print("IP Warming Schedule:")
   for day in warming_plan['schedule'][:5]:  # Show first 5 days
       print(f"Day {day['day']} ({day['date']}): {day['volume']} emails ({day['percent_of_target']}%)")
   
   # Print recommendations
   print("\nWarming Recommendations:")
   for rec in warming_plan['recommendations'][:3]:  # Show first 3 recommendations
       print(f"- {rec}")

Comprehensive Deliverability Status
---------------------------------

Get a comprehensive deliverability status report:

.. code-block:: python

   status = manager.check_deliverability_status()
   
   print(f"Domain: {status['domain']}")
   print(f"IP: {status['ip']}")
   
   # Print authentication status
   auth = status['authentication']
   print("\nAuthentication:")
   print(f"SPF: {'✓' if auth['spf'] else '✗'}")
   print(f"DKIM: {'✓' if auth['dkim'] else '✗'}")
   print(f"DMARC: {'✓' if auth['dmarc'] else '✗'}")
   print(f"Overall Score: {auth['overall_score']}/100")
   
   # Print reputation status
   rep = status['reputation']
   print("\nReputation:")
   if 'ip_status' in rep:
       print(f"IP Status: {rep['ip_status']}")
   if 'domain_score' in rep:
       print(f"Domain Score: {rep['domain_score']}/100")
   
   # Print recommendations
   print("\nRecommendations:")
   for rec in status['recommendations']:
       print(f"- {rec}")

Resource Management
----------------

The library downloads and caches external resources like blacklists and disposable domain lists. You can manually update these resources:

.. code-block:: python

   from email_deliverability import update_deliverability_resources
   
   # Update all resources
   update_results = update_deliverability_resources()
   print(f"Updated {len(update_results)} resources")

Or start a background scheduler to update resources daily:

.. code-block:: python

   from email_deliverability import start_resource_updater
   
   # Update resources every day at 3 AM
   start_resource_updater("03:00")

Next Steps
---------

Explore the detailed documentation for each component:

- :doc:`authentication` - Details on SPF, DKIM, and DMARC implementation
- :doc:`reputation` - Information on reputation monitoring
- :doc:`list_hygiene` - Email list validation and maintenance
- :doc:`ip_warming` - IP warming strategies
- :doc:`facade` - Using the unified DeliverabilityManager interface