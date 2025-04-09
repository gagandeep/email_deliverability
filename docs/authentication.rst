Authentication Tools
==================

The Email Deliverability Library provides comprehensive tools for setting up, validating, and analyzing email authentication standards: SPF, DKIM, and DMARC.

SPF (Sender Policy Framework)
----------------------------------

SPF allows email receivers to check that incoming mail from a domain comes from a host authorized by that domain's administrators.

.. code-block:: python

    from email_deliverability import DeliverabilityManager
    
    manager = DeliverabilityManager(domain="example.com")
    
    # Check if SPF record exists
    if manager.spf.verify_record_exists():
        print("SPF record exists")
        
        # Analyze the SPF record
        analysis = manager.spf.analyze_record()
        print(f"SPF Record: {analysis['record']}")
        
        if analysis['issues']:
            print("Issues found:")
            for issue in analysis['issues']:
                print(f"- {issue}")
    else:
        print("No SPF record found")
        
        # Generate a basic SPF record
        record = manager.spf.generate_record(
            authorized_servers=["192.0.2.0/24", "198.51.100.1"],
            include_domains=["_spf.google.com", "mailgun.org"],
            policy="-all"  # Strict policy
        )
        print(f"Suggested SPF record: {record}")

DKIM (DomainKeys Identified Mail)
-----------------------------------------

DKIM provides a way for senders to digitally sign their emails, allowing receivers to verify that the content hasn't been altered in transit.

.. code-block:: python

    # Generate a new DKIM key pair
    private_key, record = manager.dkim.generate_keypair(key_size=2048)
    
    print("Private key (keep this secure!):")
    print(private_key[:100] + "...")  # Show just the beginning
    
    print("\nDNS TXT record to publish:")
    print(record)
    
    # Analyze existing DKIM record
    if manager.dkim.verify_record_exists():
        analysis = manager.dkim.analyze_record()
        if analysis['issues']:
            print("DKIM issues:")
            for issue in analysis['issues']:
                print(f"- {issue}")
    
    # Example of using DKIM to sign an email
    email_content = "Subject: Test\r\nFrom: sender@example.com\r\n\r\nThis is a test email."
    signature = manager.dkim.sign_email(email_content, private_key)
    print(f"DKIM-Signature: {signature}")

DMARC (Domain-based Message Authentication, Reporting and Conformance)
-------------------------------------------------------------------------------------

DMARC allows domain owners to publish policies for how email receivers should handle messages that fail SPF and DKIM checks.

.. code-block:: python

    # Check if DMARC record exists
    if manager.dmarc.verify_record_exists():
        analysis = manager.dmarc.analyze_record()
        
        print(f"DMARC Record: {analysis['record']}")
        print(f"Policy: {analysis['parsed'].get('p', 'none')}")
        
        if analysis['issues']:
            print("DMARC issues:")
            for issue in analysis['issues']:
                print(f"- {issue}")
    else:
        # Generate DMARC record
        record = manager.dmarc.generate_record(
            policy="quarantine",  # Suspicious messages go to spam
            subdomain_policy="reject",  # Strict policy for subdomains
            reporting_email="dmarc@example.com",
            percentage=100,  # Apply to 100% of messages
            spf_strict=False,  # Relaxed SPF alignment
            dkim_strict=False  # Relaxed DKIM alignment
        )
        print(f"Suggested DMARC record: {record}")

Comprehensive Authentication Analysis
--------------------------------------------

Analyze all authentication mechanisms at once:

.. code-block:: python

    # Analyze all authentication methods
    results = manager.analyze_domain_setup()
    
    print(f"Authentication Score: {results['overall_score']}/100")
    
    for auth_type in ['spf', 'dkim', 'dmarc']:
        status = "✓" if results[auth_type]['exists'] else "✗"
        print(f"{auth_type.upper()}: {status}")
    
    if results['recommendations']:
        print("\nRecommendations:")
        for rec in results['recommendations']:
            print(f"- {rec}")