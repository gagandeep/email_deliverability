.. _list_hygiene:

=============
List Hygiene
=============

Maintaining a clean email list is essential for good deliverability. The Email Deliverability library provides tools for validating, cleaning, and analyzing your email lists.

Email Validation
-----------------

Validate individual email addresses and entire lists:

.. code-block:: python

    from email_deliverability import DeliverabilityManager

    manager = DeliverabilityManager()
    
    # Validate a single email
    result = manager.email_validator.validate_email("user@example.com")
    
    if result["is_valid"]:
        print(f"Email {result['email']} is valid")
    else:
        print(f"Email {result['email']} is invalid")
        print("Issues:")
        for issue in result["issues"]:
            print(f"- {issue}")
    
    # Validate a list of emails
    emails = [
        "valid@example.com",
        "invalid@nonexistent.domain",
        "bad-format@",
        "user@disposable.com"
    ]
    
    validation = manager.validate_email_list(emails)
    
    # Summary of validation results
    analysis = validation["analysis"]
    print(f"Total emails: {analysis['total_emails']}")
    print(f"Valid emails: {analysis['valid_emails']}")
    print(f"Invalid emails: {analysis['invalid_emails']}")
    print(f"Disposable emails: {analysis['disposable_emails']}")
    print(f"Quality score: {analysis['quality_score']}")
    print(f"Quality level: {analysis['quality_level']}")

List Cleaning
--------------

Clean your email lists to remove invalid and risky addresses:

.. code-block:: python

    from email_deliverability.list_hygiene.cleaner import ListCleaner

    cleaner = ListCleaner()
    
    # Clean a list of emails
    emails = [
        "valid@example.com",
        "duplicate@example.com",
        "duplicate@example.com",
        "invalid@nonexistent.domain",
        "user@disposable.com"
    ]
    
    # Remove invalid emails
    cleaned = cleaner.clean_list(emails, strict_mode=True)
    
    print(f"Original list size: {cleaned['input_count']}")
    print(f"Clean list size: {len(cleaned['valid_emails'])}")
    print(f"Removed {len(cleaned['invalid_emails'])} invalid emails")
    print(f"Removed {len(cleaned['disposable_emails'])} disposable emails")
    
    # Deduplicate the list
    deduped = cleaner.deduplicate_list(emails)
    
    print(f"Original list size: {deduped['input_count']}")
    print(f"Deduplicated list size: {deduped['output_count']}")
    print(f"Removed {deduped['duplicates_removed']} duplicates")

Finding Typos in Domains
----------------------------

Identify potential typos in email domains:

.. code-block:: python

    # Find potential typos in domains
    emails = [
        "user@gmali.com",
        "john@yaho.com",
        "test@examples.com",
        "user@hotmial.com"
    ]
    
    typos = cleaner.find_typos(emails)
    
    print(f"Found {len(typos)} potential typos:")
    for typo in typos:
        print(f"- {typo['email']} might be {typo['suggested_email']}")

Bounce Handling
----------------

Process and analyze email bounce data to improve list quality:

.. code-block:: python

    from email_deliverability.list_hygiene.bounce_handler import BounceHandler
    
    handler = BounceHandler()
    
    # Parse bounce logs (CSV format example)
    bounce_csv = """email,reason,type,timestamp
    user1@example.com,recipient rejected,hard,2023-01-01T10:00:00
    user2@example.com,mailbox full,soft,2023-01-01T11:15:00
    user3@example.com,blocked as spam,spam_block,2023-01-01T12:30:00
    """
    
    bounces = handler.parse_bounce_logs(bounce_csv, format_type="csv")
    
    # Extract email addresses to remove from list
    hard_bounces = handler.extract_emails_from_bounces(bounces, bounce_types=["hard"])
    print(f"Emails to remove from list: {hard_bounces}")
    
    # Analyze bounce patterns
    analysis = handler.analyze_bounce_patterns(bounces)
    print(f"Total bounces: {analysis['total_bounces']}")
    
    # Extract problematic domains
    problem_domains = handler.extract_domains_from_bounces(bounces, min_occurrences=1)
    print("Problematic domains:")
    for domain, stats in problem_domains.items():
        print(f"- {domain}: {stats['total']} bounces ({stats['hard']} hard, {stats['soft']} soft)")