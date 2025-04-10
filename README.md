# Email Deliverability Management Library

A comprehensive Python library for managing email deliverability, providing tools and guidance for email authentication (SPF, DKIM, DMARC), sender reputation monitoring, email list hygiene, and IP warming.

## Features

- **Email Authentication**
  - SPF record creation, validation, and analysis
  - DKIM key management and signature verification
  - DMARC policy configuration and reporting

- **Reputation Monitoring**
  - IP blacklist checking
  - Feedback loop complaint processing
  - Domain reputation analysis
  - Bounce rate analysis

- **Email List Hygiene**
  - Email format validation
  - MX record checking
  - Disposable email detection
  - List quality scoring and recommendations

- **IP Warming Tools**
  - Customizable warming schedules
  - Volume distribution by hour
  - Multi-IP warming management
  - Best practice recommendations

- **Unified Facade Interface**
  - Comprehensive deliverability checks
  - Simplified access to all tools
  - Actionable recommendations

## Installation

```bash
pip install email_deliverability

```

## Quick Start

```python

from email_deliverability import DeliverabilityManager

# Initialize the manager with your domain and IP
manager = DeliverabilityManager(domain="example.com", ip="8.8.8.8")

# Analyze authentication setup
auth_results = manager.analyze_domain_setup()
print(f"Authentication Score: {auth_results['overall_score']}/100")

# Check IP reputation
ip_results = manager.check_ip_reputation()
if ip_results['status'] == 'clean':
    print("IP is not listed on any blacklists")
else:
    print(f"IP is listed on {len(ip_results['blacklisted_on'])} blacklists")

# Validate email addresses
emails = ["user@example.com", "invalid@nonexistent.domain", "test@mailinator.com"]
validation_results = manager.validate_email_list(emails)
print(f"List Quality: {validation_results['analysis']['quality_level']}")

# Create an IP warming plan
warming_plan = manager.create_ip_warming_plan(daily_target=10000, warmup_days=30)
print(f"Warming schedule created for {warming_plan['warmup_days']} days")

# Get comprehensive deliverability status
status = manager.check_deliverability_status()
for recommendation in status['recommendations']:
    print(f"- {recommendation}")

```

## Command Line Interface

The library comes with a full-featured command line interface:

```bash
# Check domain authentication
email-deliverability auth --domain example.com

# Check IP reputation
email-deliverability reputation --ip 192.0.2.1

# Validate email addresses
email-deliverability validate --email user@example.com
email-deliverability validate --file emails.txt

# Run a comprehensive deliverability check
email-deliverability check --domain example.com --ip 192.0.2.1

# Generate an IP warming plan
email-deliverability warm-ip --ip 192.0.2.1 --days 30 --target 100000

# Update local resource cache
email-deliverability resources update
```

For full CLI documentation:

```bash
email-deliverability --help
```

## Documentation

Full documentation is available at [Read the Docs](https://email-deliverability.readthedocs.io/en/latest/).

## Development

```bash
# Clone the repository
git clone https://github.com/innerkore/email-deliverability.git
cd email-deliverability

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m unittest discover tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
