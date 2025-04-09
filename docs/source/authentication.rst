.. _authentication:

=======================
Email Authentication
=======================

Email authentication is essential for improving deliverability and preventing spoofing.
This library provides tools for managing SPF, DKIM, and DMARC records.

SPF (Sender Policy Framework)
---------------------------------

SPF helps verify that mail sent from a domain comes from servers authorized by that domain's owners.

Analyzing SPF Records
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from email_deliverability import DeliverabilityManager

    manager = DeliverabilityManager(domain="example.com")
    
    # Verify SPF record exists
    if manager.spf.verify_record_exists():
        # Analyze the SPF record
        analysis = manager.spf.analyze_record()
        print(f"SPF Record: {analysis['record']}")
        
        if analysis["issues"]:
            print("Issues found:")
            for issue in analysis["issues"]:
                print(f"- {issue}")
    else:
        print("No SPF record found")

Creating SPF Records
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Generate an SPF record
    spf_record = manager.spf.generate_record(
        authorized_servers=["192.0.2.0/24", "198.51.100.1"],
        include_domains=["_spf.google.com", "sendgrid.net"],
        policy="-all"  # Strict policy
    )
    print(f"Generated SPF record: {spf_record}")

DKIM (DomainKeys Identified Mail)
----------------------------------------

DKIM adds a digital signature to emails, allowing verification that they were sent and authorized by the domain owner.

Managing DKIM Records
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Check if DKIM record exists
    if manager.dkim.verify_record_exists():
        # Analyze the DKIM record
        analysis = manager.dkim.analyze_record()
        print(f"DKIM Record exists: {analysis['record']}")
    else:
        print("No DKIM record found")
        
    # Generate a new DKIM key pair
    private_key, txt_record = manager.dkim.generate_keypair(key_size=2048)
    
    print("Private key (save securely):")
    print(private_key[:100] + "...")
    
    print(f"\nDKIM DNS record to create for selector 'default._domainkey.{manager.domain}':")
    print(txt_record)

DMARC (Domain-based Message Authentication, Reporting and Conformance)
------------------------------------------------------------------------------------

DMARC builds upon SPF and DKIM, providing instructions for handling emails that fail authentication.

Managing DMARC Records
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Check if DMARC record exists
    if manager.dmarc.verify_record_exists():
        # Analyze the DMARC record
        analysis = manager.dmarc.analyze_record()
        print(f"DMARC Record: {analysis['record']}")
        
        if analysis["issues"]:
            print("Issues found:")
            for issue in analysis["issues"]:
                print(f"- {issue}")
    else:
        print("No DMARC record found")
        
    # Generate a DMARC record
    dmarc_record = manager.dmarc.generate_record(
        policy="quarantine",  # Suspicious emails go to spam
        subdomain_policy="reject",  # Stricter policy for subdomains
        reporting_email="dmarc@example.com",
        percentage=100,  # Apply to 100% of emails
        spf_strict=False,  # Relaxed SPF alignment
        dkim_strict=False  # Relaxed DKIM alignment
    )
    
    print(f"Generated DMARC record to add to '_dmarc.{manager.domain}':")
    print(dmarc_record)

Comprehensive Authentication Analysis
-------------------------------------------

The facade provides a comprehensive analysis of all authentication mechanisms:

.. code-block:: python

    # Analyze all authentication methods at once
    results = manager.analyze_domain_setup()
    
    print(f"Overall authentication score: {results['overall_score']}/100")
    
    # Display recommendations
    for recommendation in results["recommendations"]:
        print(f"- {recommendation}")