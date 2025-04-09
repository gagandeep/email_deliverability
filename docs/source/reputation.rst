.. _reputation:

====================
Reputation Monitoring
====================

Email sender reputation monitoring is crucial for maintaining high deliverability rates. This module provides tools to check and monitor your sending reputation.

IP Blacklist Checking
----------------------

Check if your sending IP is listed on common blacklists:

.. code-block:: python

    from email_deliverability import DeliverabilityManager

    manager = DeliverabilityManager(ip="192.0.2.10")
    
    # Check IP reputation
    results = manager.check_ip_reputation()
    
    if results["status"] == "clean":
        print(f"IP {results['ip']} is clean on {len(results['clean_on'])} checked blacklists")
    else:
        print(f"IP {results['ip']} is blacklisted on {len(results['blacklisted_on'])} blacklists:")
        for blacklist in results["blacklisted_on"]:
            print(f"- {blacklist}")

Feedback Loop Monitoring
---------------------------

Analyze feedback loop complaint data:

.. code-block:: python

    # Sample CSV data from feedback loop
    feedback_csv = """email,reason,campaign_id,timestamp
    user1@example.com,spam content,campaign1,2023-01-01T10:00:00
    user2@example.com,unwanted,campaign1,2023-01-01T10:15:00
    user3@example.com,spam content,campaign2,2023-01-01T12:30:00"""
    
    # Analyze complaint data
    results = manager.reputation.monitor_feedback_loops(feedback_csv)
    
    print(f"Total complaints: {results['total_complaints']}")
    print("Common reasons:")
    for reason, count in results["common_reasons"].items():
        print(f"- {reason}: {count}")
    
    print("\nAffected campaigns:")
    for campaign, count in results["affected_campaigns"].items():
        print(f"- {campaign}: {count} complaints")

Bounce Analysis
---------------

Analyze email bounces to identify reputation issues:

.. code-block:: python

    # Sample bounce data
    bounce_data = [
        {"email": "user1@example.com", "type": "hard", "reason": "recipient rejected"},
        {"email": "user2@example.com", "type": "soft", "reason": "mailbox full"},
        {"email": "user3@example.com", "type": "spam_block", "reason": "blocked as spam"}
    ]
    
    # Analyze bounce logs
    results = manager.reputation.analyze_bounce_logs(bounce_data)
    
    print(f"Total bounces: {results['total_bounces']}")
    print(f"Hard bounces: {results['hard_bounces']}")
    print(f"Soft bounces: {results['soft_bounces']}")
    print(f"Spam blocks: {results['spam_blocks']}")
    
    print("\nRecommendations:")
    for recommendation in results["recommendations"]:
        print(f"- {recommendation}")

Domain Reputation Checking
-----------------------------

Check the sender reputation of your domain:

.. code-block:: python

    # Check domain reputation
    results = manager.reputation.check_domain_reputation()
    
    print(f"Domain: {results['domain']}")
    print(f"Reputation score: {results['reputation_score']}/100")
    print(f"Spam rate: {results['spam_rate']}%")
    
    print("\nAuthentication pass rates:")
    for auth_type, rate in results['authentication'].items():
        print(f"- {auth_type}: {rate}%")
    
    print("\nIssues:")
    for issue in results["issues"]:
        print(f"- {issue}")

Advanced Analysis with Reputation Analyzer
------------------------------------------------

For more advanced reputation analysis:

.. code-block:: python

    from email_deliverability.reputation.analyze import ReputationAnalyzer
    
    analyzer = ReputationAnalyzer()
    
    # Analyze bounce trends
    bounce_history = [
        ("2023-01-01", 2.5),
        ("2023-01-02", 2.2),
        ("2023-01-03", 1.8),
        ("2023-01-04", 1.5),
        ("2023-01-05", 1.2)
    ]
    
    trend = analyzer.analyze_bounce_trend(bounce_history)
    
    print(f"Bounce trend: {trend['trend']}")
    print(f"Current bounce rate: {trend['current_rate']}%")
    print(f"Change in last period: {trend['change_percent']}%")