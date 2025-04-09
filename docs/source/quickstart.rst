.. _quickstart:

===========
Quick Start
===========

This guide will help you get started with the Email Deliverability library.

Basic Usage
-------------

Initialize the manager with your domain and IP:

.. code-block:: python

    from email_deliverability import DeliverabilityManager

    # Initialize the manager
    manager = DeliverabilityManager(
        domain="example.com",
        ip="192.0.2.10",
        auto_update_resources=True
    )

Analysis of Domain Configuration
----------------------------------------

Check your domain's authentication setup:

.. code-block:: python

    # Analyze authentication setup
    auth_results = manager.analyze_domain_setup()
    print(f"Authentication Score: {auth_results['overall_score']}/100")

    # Follow the recommendations
    for recommendation in auth_results['recommendations']:
        print(f"- {recommendation}")

Reputation Monitoring
--------------------------

Check if your IP is listed on blacklists:

.. code-block:: python

    # Check IP reputation
    ip_results = manager.check_ip_reputation()
    print(f"IP Status: {ip_results['status']}")

    if ip_results["status"] != "clean":
        print("IP is blacklisted on:")
        for blacklist in ip_results["blacklisted_on"]:
            print(f"- {blacklist}")

Email List Validation
--------------------------

Validate a list of email addresses:

.. code-block:: python

    # Validate email addresses
    emails = ["user@example.com", "invalid@nonexistent.domain", "test@mailinator.com"]
    validation_results = manager.validate_email_list(emails)
    print(f"List Quality: {validation_results['analysis']['quality_level']}")
    print(f"Valid emails: {validation_results['analysis']['valid_emails']}/{validation_results['analysis']['total_emails']}")

IP Warming
---------

Create an IP warming plan:

.. code-block:: python

    # Create an IP warming plan
    warming_plan = manager.create_ip_warming_plan(daily_target=10000, warmup_days=30)
    print(f"Warming schedule created for {warming_plan['warmup_days']} days")

    # View the schedule
    for day in warming_plan["schedule"][:5]:  # First 5 days
        print(f"Day {day['day']}: Send {day['volume']} emails ({day['percent_of_target']}% of target)")

Resource Management
---------------------

Update external resources manually:

.. code-block:: python

    # Update resources
    update_results = manager.update_resources()
    print(f"Updated resources: {', '.join(update_results.keys())}")

Comprehensive Status Check
------------------------------

Perform a comprehensive deliverability check:

.. code-block:: python

    # Get comprehensive deliverability status
    status = manager.check_deliverability_status()
    
    print(f"Authentication score: {status['authentication'].get('overall_score', 0)}")
    print(f"IP status: {status['reputation'].get('ip_status', 'unknown')}")
    
    for recommendation in status["recommendations"]:
        print(f"- {recommendation}")