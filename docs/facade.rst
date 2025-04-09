Unified Facade Interface
=====================

The Email Deliverability Library provides a unified facade interface, `DeliverabilityManager`, that gives you convenient access to all deliverability tools through a single entry point.

This design pattern simplifies usage and ensures components work together seamlessly.

Initialization
---------------

Initialize the deliverability manager with your domain and IP:

.. code-block:: python

    from email_deliverability import DeliverabilityManager
    
    # Basic initialization
    manager = DeliverabilityManager(
        domain="example.com",
        ip="192.0.2.1"
    )
    
    # With additional options
    manager = DeliverabilityManager(
        domain="example.com",
        ip="192.0.2.1",
        api_key="your_api_key_for_external_services",
        auto_update_resources=True  # Updates resources daily at 3 AM
    )

Available Components
--------------------

The facade provides access to these main components:

.. code-block:: python

    # Access SPF tools
    manager.spf
    
    # Access DKIM tools
    manager.dkim
    
    # Access DMARC tools 
    manager.dmarc
    
    # Access reputation monitoring
    manager.reputation
    
    # Access email validation
    manager.email_validator
    
    # Access IP warming tools
    manager.ip_warming

Integrated Analysis Methods
------------------------------

The facade also provides integrated methods that combine multiple components:

.. code-block:: python

    # Comprehensive authentication analysis
    auth_results = manager.analyze_domain_setup()
    
    # IP reputation check
    ip_results = manager.check_ip_reputation()
    
    # Email list validation
    validation_results = manager.validate_email_list(emails)
    
    # IP warming plan creation
    warming_plan = manager.create_ip_warming_plan(daily_target=10000)
    
    # Complete deliverability health check
    status = manager.check_deliverability_status()
    
    # Manual resource update
    manager.update_resources()

Example: Complete Deliverability Analysis
-----------------------------------------------

This example performs a comprehensive deliverability analysis:

.. code-block:: python

    # Initialize with domain and IP
    manager = DeliverabilityManager(domain="example.com", ip="192.0.2.1")
    
    # Get complete deliverability status
    status = manager.check_deliverability_status()
    
    # Print summary
    print(f"Domain: {status['domain']}")
    print(f"IP: {status['ip']}")
    print(f"Timestamp: {status['timestamp']}")
    
    # Authentication status
    auth = status['authentication']
    print("\nAuthentication Status:")
    print(f"SPF: {'✓' if auth['spf'] else '✗'}")
    print(f"DKIM: {'✓' if auth['dkim'] else '✗'}")
    print(f"DMARC: {'✓' if auth['dmarc'] else '✗'}")
    print(f"Overall Score: {auth['overall_score']}/100")
    
    # Reputation status
    rep = status['reputation']
    print("\nReputation Status:")
    if 'ip_status' in rep:
        print(f"IP Status: {rep['ip_status']}")
    if 'domain_score' in rep:
        print(f"Domain Score: {rep['domain_score']}/100")
    
    # Print recommendations
    if status['recommendations']:
        print("\nRecommendations:")
        for rec in status['recommendations']:
            print(f"- {rec}")