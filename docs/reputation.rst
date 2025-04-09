Reputation Monitoring
===================

Monitor and analyze your email sender reputation with our comprehensive tools.

Email sender reputation is a score that Internet Service Providers (ISPs) assign to an organization that sends email. It determines the deliverability of your emails and helps you understand how recipients view your email campaigns.

IP Blacklist Checking
-------------------

Check if your sending IP is on any blacklists:

.. code-block:: python

    from email_deliverability import DeliverabilityManager
    
    # Initialize with your sending IP
    manager = DeliverabilityManager(ip="192.0.2.1")
    
    # Check blacklists
    results = manager.check_ip_reputation()
    
    if results['status'] == 'clean':
        print(f"IP {results['ip']} is not listed on any blacklists")
        print(f"Checked {len(results['clean_on'])} blacklists")
    else:
        print(f"IP {results['ip']} is listed on {len(results['blacklisted_on'])} blacklists:")
        for bl in results['blacklisted_on']:
            print(f"- {bl}")

Feedback Loop Processing
---------------------

Process and analyze feedback loop complaints:

.. code-block:: python

    # Sample feedback loop data (typically from your ESP)
    complaint_data = """email,reason,campaign_id,timestamp
    user1@example.com,spam content,campaign1,2023-01-01T10:00:00
    user2@example.com,unwanted,campaign1,2023-01-01T10:15:00
    user3@example.com,spam content,campaign2,2023-01-01T12:30:00"""
    
    # Analyze complaints
    analysis = manager.reputation.monitor_feedback_loops(complaint_data)
    
    print(f"Total complaints: {analysis['total_complaints']}")
    print("\nCommon reasons:")
    for reason, count in analysis['common_reasons'].items():
        print(f"- {reason}: {count}")
        
    print("\nAffected campaigns:")
    for campaign, count in analysis['affected_campaigns'].items():
        print(f"- {campaign}: {count}")

Bounce Analysis
------------

Analyze email bounces to identify reputation issues:

.. code-block:: python

    # Sample bounce data
    bounce_data = [
        {"email": "nonexistent@example.com", "type": "hard", "reason": "recipient rejected"},
        {"email": "full@example.com", "type": "soft", "reason": "mailbox full"},
        {"email": "temp@example.com", "type": "soft", "reason": "temporary failure"},
        {"email": "spam@example.com", "type": "spam_block", "reason": "blocked as spam"}
    ]
    
    # Analyze bounce patterns
    analysis = manager.reputation.analyze_bounce_logs(bounce_data)
    
    print(f"Total bounces: {analysis['total_bounces']}")
    print(f"Hard bounces: {analysis['hard_bounces']}")
    print(f"Soft bounces: {analysis['soft_bounces']}")
    print(f"Spam blocks: {analysis['spam_blocks']}")
    
    if analysis['recommendations']:
        print("\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"- {rec}")

Domain Reputation Checking
-----------------------

Check your domain's sending reputation:

.. code-block:: python

    # Initialize with your domain
    manager = DeliverabilityManager(domain="example.com")
    
    # Check domain reputation
    reputation = manager.reputation.check_domain_reputation()
    
    print(f"Domain: {reputation['domain']}")
    print(f"Reputation Score: {reputation['reputation_score']}/100")
    print(f"Spam Rate: {reputation['spam_rate']}%")
    
    print("\nAuthentication Pass Rates:")
    auth = reputation['authentication']
    print(f"SPF: {auth['spf_pass_rate']}%")
    print(f"DKIM: {auth['dkim_pass_rate']}%")
    print(f"DMARC: {auth['dmarc_pass_rate']}%")
    
    if reputation['issues']:
        print("\nIssues Detected:")
        for issue in reputation['issues']:
            print(f"- {issue}")

Comprehensive Deliverability Status
--------------------------------

Get a complete overview of your email deliverability status:

.. code-block:: python

    # Initialize with both domain and IP
    manager = DeliverabilityManager(domain="example.com", ip="192.0.2.1")
    
    # Check comprehensive status
    status = manager.check_deliverability_status()
    
    print(f"Domain: {status['domain']}")
    print(f"IP: {status['ip']}")
    
    # Authentication status
    auth = status['authentication']
    print("\nAuthentication:")
    print(f"SPF: {'✓' if auth['spf'] else '✗'}")
    print(f"DKIM: {'✓' if auth['dkim'] else '✗'}")
    print(f"DMARC: {'✓' if auth['dmarc'] else '✗'}")
    print(f"Overall Score: {auth['overall_score']}/100")
    
    # Reputation status
    rep = status['reputation']
    print("\nReputation:")
    if 'ip_status' in rep:
        print(f"IP Status: {rep['ip_status']}")
    if 'domain_score' in rep:
        print(f"Domain Score: {rep['domain_score']}/100")
    
    # Recommendations
    if status['recommendations']:
        print("\nRecommendations:")
        for rec in status['recommendations']:
            print(f"- {rec}")