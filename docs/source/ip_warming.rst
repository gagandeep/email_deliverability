.. _ip_warming:

==========
IP Warming
==========

IP warming is the practice of gradually increasing email sending volume to establish a positive reputation. The Email Deliverability library provides tools for planning and monitoring IP warming processes.

Creating IP Warming Plans
-----------------------------

Generate a comprehensive IP warming schedule:

.. code-block:: python

    from email_deliverability import DeliverabilityManager

    # Create a manager
    manager = DeliverabilityManager()
    
    # Create an IP warming plan
    plan = manager.create_ip_warming_plan(
        daily_target=50000,  # Target daily volume
        warmup_days=30       # Warmup period in days
    )
    
    print(f"Warming schedule for {plan['warmup_days']} days to reach {plan['daily_target']} emails/day:")
    
    # Display the first week of the schedule
    print("\nFirst week:")
    for day in plan["schedule"][:7]:
        print(f"Day {day['day']} ({day['date']}): {day['volume']} emails ({day['percent_of_target']}% of target)")
    
    # Display the last week of the schedule
    print("\nLast week:")
    for day in plan["schedule"][-7:]:
        print(f"Day {day['day']} ({day['date']}): {day['volume']} emails ({day['percent_of_target']}% of target)")
    
    print("\nBest practices and recommendations:")
    for tip in plan["recommendations"]:
        print(f"- {tip}")

Hourly Distribution
-------------------

Distribute daily volumes across hours for optimal sending:

.. code-block:: python

    from email_deliverability.ip_warming.scheduler import IPWarmingScheduler
    
    # Create a scheduler
    scheduler = IPWarmingScheduler()
    
    # Distribute daily volume by hour
    daily_volume = 10000
    hourly_volumes = scheduler.distribute_volume_by_hour(daily_volume)
    
    print(f"Distribution of {daily_volume} emails throughout the day:")
    for hour, volume in sorted(hourly_volumes.items()):
        print(f"{hour:02d}:00 - {hour+1:02d}:00: {volume} emails ({volume/daily_volume*100:.1f}%)")

Warming Multiple IPs
--------------------

Create warming schedules for multiple IPs:

.. code-block:: python

    # Create warming plans for multiple IPs
    ip_count = 3
    total_daily_target = 150000
    
    multi_ip_plan = scheduler.warm_multiple_ips(ip_count, total_daily_target)
    
    for ip_name, schedule in multi_ip_plan.items():
        print(f"\n{ip_name} warming schedule:")
        print(f"Day 1: {schedule[0]['volume']} emails")
        print(f"Final day: {schedule[-1]['volume']} emails")

Monitoring IP Warming
---------------------

Monitor the progress and performance of your IP warming:

.. code-block:: python

    from email_deliverability.ip_warming.monitor import WarmingMonitor
    
    # Create a monitor
    monitor = WarmingMonitor(target_volume=50000)
    
    # Load an existing warming plan
    monitor.load_plan(plan)
    
    # Mock sending data (date, volume)
    sent_volumes = [
        ("2023-01-01", 100),
        ("2023-01-02", 250),
        ("2023-01-03", 500),
        ("2023-01-04", 1000),
        ("2023-01-05", 1500)
    ]
    
    # Track progress against plan
    progress = monitor.track_progress(sent_volumes)
    
    print(f"Days since start: {progress['days_since_start']}")
    print(f"Overall adherence to plan: {progress['overall_adherence']}%")
    print(f"Status: {progress['status']}")
    
    # Sample performance metrics
    performance_data = {
        "bounce_rate": 1.2,
        "complaint_rate": 0.05,
        "open_rate": 20.5,
        "click_rate": 3.2,
        "delivery_rate": 98.8
    }
    
    # Analyze performance during warming
    analysis = monitor.monitor_key_metrics(performance_data)
    
    print(f"Warming health: {analysis['health']}")
    
    if analysis['issues']:
        print("Issues:")
        for issue in analysis['issues']:
            print(f"- {issue['message']}")
    
    print("Recommendations:")
    for rec in analysis['recommendations']:
        print