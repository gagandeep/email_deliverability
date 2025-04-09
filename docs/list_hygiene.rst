Email List Hygiene
================

Maintain clean, high-quality email lists with our comprehensive email validation and list hygiene tools.

Email List Validation
---------------------

Validate email addresses individually or in batches:

.. code-block:: python

    from email_deliverability import DeliverabilityManager
    
    manager = DeliverabilityManager()
    
    # Validate a single email
    email = "test@example.com"
    result = manager.email_validator.validate_email(email)
    
    if result["is_valid"]:
        print(f"✓ {email} is valid")
    else:
        print(f"✗ {email} is invalid:")
        for issue in result["issues"]:
            print(f"  - {issue}")
    
    # Batch validation
    emails = [
        "valid@example.com",
        "invalid@nonexistent.domain",
        "disposable@mailinator.com",
        "malformed.email",
    ]
    
    results = manager.validate_email_list(emails)
    
    # Print validation results
    print("\nValidation Results:")
    for result in results["results"]:
        status = "✓" if result["is_valid"] else "✗"
        print(f"{status} {result['email']}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"  - {issue}")
    
    # Print quality analysis
    analysis = results["analysis"]
    print(f"\nList Quality: {analysis['quality_level']} ({analysis['quality_score']}%)")
    print(f"Valid emails: {analysis['valid_emails']}/{analysis['total_emails']}")
    print(f"Invalid emails: {analysis['invalid_emails']}")
    print(f"Disposable emails: {analysis['disposable_emails']}")
    
    # Print recommendations
    if analysis["recommendations"]:
        print("\nRecommendations:")
        for rec in analysis["recommendations"]:
            print(f"- {rec}")

List Cleaning
--------------

Remove invalid and problematic emails from your list:

.. code-block:: python

    from email_deliverability.list_hygiene.cleaner import ListCleaner
    
    # Sample list of emails
    email_list = [
        "user1@example.com",
        "user2@example.com",
        "duplicate@example.com",
        "duplicate@example.com",
        "invalid@nonexistent.domain",
        "disposable@mailinator.com",
        "malformed.email"
    ]
    
    # Create a list cleaner
    cleaner = ListCleaner()
    
    # Clean the list (remove invalid emails)
    cleaning_result = cleaner.clean_list(email_list, strict_mode=True)
    
    print(f"Original list size: {cleaning_result['input_count']}")
    print(f"Valid emails: {len(cleaning_result['valid_emails'])}")
    print(f"Invalid emails removed: {len(cleaning_result['invalid_emails'])}")
    print(f"Disposable emails removed: {len(cleaning_result['disposable_emails'])}")
    
    # Deduplicate the list
    dedup_result = cleaner.deduplicate_list(email_list)
    
    print(f"\nDuplicates removed: {dedup_result['duplicates_removed']}")
    print(f"List after deduplication: {dedup_result['output_count']} emails")
    
    # Segment by domain
    segments = cleaner.segment_by_domain(email_list)
    
    print("\nEmails by domain:")
    for domain, emails in segments.items():
        print(f"- {domain}: {len(emails)} emails")

Finding Typos in Domains
----------------------------

Identify and correct common domain typos:

.. code-block:: python

    # Find potential typos in email domains
    emails_with_typos = [
        "user@gmial.com",
        "user@yaho.com",
        "user@hotmial.com",
        "user@example.com"
    ]
    
    potential_typos = cleaner.find_typos(emails_with_typos)
    
    if potential_typos:
        print("\nPotential domain typos found:")
        for item in potential_typos:
            print(f"Original: {item['email']}")
            print(f"Suggested: {item['suggested_email']}")
            print()
    else:
        print("\nNo potential typos found.")

Bounce Handling
----------------

Process and analyze email bounce data:

.. code-block:: python

    from email_deliverability.list_hygiene.bounce_handler import BounceHandler
    
    # Sample bounce data (CSV format)
    bounce_csv = """email,reason,type,timestamp
    user1@example.com,mailbox full,soft,2025-01-01T10:00:00
    user2@example.com,user unknown,hard,2025-01-01T11:30:00
    user3@example.com,blocked as spam,spam_block,2025-01-01T12:15:00
    user4@example.com,connection refused,soft,2025-01-01T14:45:00
    user5@example.com,recipient rejected,hard,2025-01-01T16:20:00
    """
    
    # Create a bounce handler
    handler = BounceHandler()
    
    # Parse bounce logs
    bounces = handler.parse_bounce_logs(bounce_csv, format_type="csv")
    
    # Extract email addresses to remove from list
    bounce_emails = handler.extract_emails_from_bounces(bounces, bounce_types=["hard", "spam_block"])
    
    print(f"Emails to remove: {len(bounce_emails)}")
    for email in bounce_emails:
        print(f"- {email}")
    
    # Analyze bounce patterns
    analysis = handler.analyze_bounce_patterns(bounces)
    
    print(f"\nTotal bounces: {analysis['total_bounces']}")
    for bounce_type, percentage in analysis['by_type'].items():
        print(f"{bounce_type}: {percentage:.1f}%")
    
    if analysis['recommendations']:
        print("\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"- {rec}")