IP Warming Tools
=============

The Email Deliverability Library provides comprehensive tools for IP warming - the process of gradually increasing email volume from a new IP address to establish a positive sender reputation.

Creating IP Warming Plans
-----------------------------

Create a customized IP warming schedule based on your target daily volume:

.. code-block:: python

    from email_deliverability import DeliverabilityManager
    
    # Initialize deliverability manager
    manager = DeliverabilityManager()
    
    # Create a warming plan for 50,000 emails per day over 30 days
    warming_plan = manager.create_ip_warming_plan(
        daily_target=50000,
        warmup_days=30
    )
    
    # Print the schedule
    print("IP Warming Schedule:")
    print("-" * 50)
    print(f"{'Day':<5}{'Date':<12}{'Volume':<10}{'% of Target':<15}")
    print("-" * 50)
    
    for day in warming_plan['schedule']:
        print(f"{day['day']:<5}{day['date']:<12}{day['volume']:<10}{day['percent_of_target']:<15}%")
    
    # Print recommendations
    print("\nBest Practices:")
    for i, rec in enumerate(warming_plan['recommendations'], 1):
        print(f"{i}. {rec}")

You can adjust the `warmup_days` parameter to make the warming process faster or slower depending on your needs.

Hourly Distribution
-------------------

For optimal deliverability, distribute your daily email volume throughout the day:

.. code-block:: python

    from email_deliverability.ip_warming.scheduler import IPWarmingScheduler
    
    # Create a scheduler
    scheduler = IPWarmingScheduler()
    
    # Get hourly distribution for a specific day's volume
    day_10_volume = warming_plan['schedule'][9]['volume']  # Day 10 volume
    hourly_volumes = scheduler.distribute_volume_by_hour(day_10_volume)
    
    # Print hourly sending schedule
    print(f"Hourly sending schedule for day 10 (total: {day_10_volume} emails):")
    print("-" * 50)
    print(f"{'Hour':<5}{'Emails':<10}{'% of Daily':<15}")
    print("-" * 50)
    
    for hour, volume in hourly_volumes.items():
        percentage = (volume / day_10_volume) * 100
        time_slot = f"{hour:02d}:00"
        print(f"{time_slot:<5}{volume:<10}{percentage:.1f}%")

Warming Multiple IPs
--------------------

If you need to warm up multiple IPs simultaneously:

.. code-block:: python

    # Create a multi-IP warming plan
    ip_count = 3
    total_daily_target = 150000  # Total volume across all IPs
    
    multi_ip_plan = scheduler.warm_multiple_ips(
        ip_count=ip_count,
        daily_target=total_daily_target
    )
    
    # Print summary of multi-IP warming
    print(f"Warming {ip_count} IPs to handle {total_daily_target} emails daily")
    print("-" * 60)
    
    for ip, schedule in multi_ip_plan.items():
        ip_target = schedule[-1]['volume']  # Final day volume = target
        print(f"{ip}: Target volume of {ip_target} emails per day")
        print(f"  Day 1: {schedule[0]['volume']} emails")
        print(f"  Day 15: {schedule[14]['volume']} emails")
        print(f"  Final day: {ip_target} emails")

Monitoring IP Warming
---------------------

Track and analyze your IP warming progress:

.. code-block:: python

    from email_deliverability.ip_warming.monitor import WarmingMonitor
    
    # Initialize a warming monitor
    monitor = WarmingMonitor(target_volume=50000)
    
    # Load your warming plan
    monitor.load_plan(warming_plan)
    
    # Sample sending data (date, volume sent)
    sent_volumes = [
        ("2025-04-01", 100),
        ("2025-04-02", 250),
        ("2025-04-03", 500),
        ("2025-04-04", 750),
        ("2025-04-05", 1200),
        # ... more days ...
    ]
    
    # Track progress against plan
    progress = monitor.track_progress(sent_volumes)
    
    print(f"Warming Progress: {progress['overall_adherence']}% adherence to plan")
    print(f"Status: {progress['status']}")
    
    # Sample performance metrics
    performance_data = {
        "bounce_rate": 1.2,
        "complaint_rate": 0.05,
        "open_rate": 22.5,
        "click_rate": 3.8,
        "delivery_rate": 98.8
    }
    
    # Monitor key performance metrics
    metrics = monitor.monitor_key_metrics(performance_data)
    
    print(f"\nWarming Health: {metrics['health']}")
    
    if metrics['issues']:
        print("\nIssues:")
        for issue in metrics['issues']:
            print(f"- {issue['message']}")
    
    print("\nRecommendations:")
    for rec in metrics['recommendations']:
        print(f"- {rec}")
    
    # Check blacklists during warming
    blacklist_check = monitor.check_blacklist_during_warming()
    if blacklist_check['warming_impact'] != 'none':
        print(f"\n⚠️ Blacklist Impact: {blacklist_check['warming_impact']}")
        print("Recommendations:")
        for rec in blacklist_check['recommendations']:
            print(f"- {rec}")