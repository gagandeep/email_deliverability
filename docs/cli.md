# Command Line Interface

The Email Deliverability library includes a full-featured command line interface (CLI) that provides access to all main functionality directly from your terminal.

## Installation

When you install the library, the command line tool is automatically installed:

```bash
pip install email_deliverability
```

After installation, you can run the CLI using the `email-deliverability` command:

```bash
email-deliverability --help
```

## Available Commands

### Check Authentication

Check domain authentication setup including SPF, DKIM, and DMARC:

```bash
email-deliverability auth --domain example.com
```

Options:
- `--format` or `-f`: Output format (`text` or `json`, default: text)
- `--output` or `-o`: Output file (default: stdout)

### Check Reputation

Check IP or domain reputation against blacklists:

```bash
email-deliverability reputation --ip 192.0.2.1
email-deliverability reputation --domain example.com
```

Options:
- `--format` or `-f`: Output format (`text` or `json`, default: text)
- `--output` or `-o`: Output file (default: stdout)

### Validate Emails

Validate email addresses for format, domain, and more:

```bash
email-deliverability validate --email user@example.com
email-deliverability validate --file emails.txt
```

Options:
- `--check-mx` or `-m`: Check MX records (slower but more accurate)
- `--format`: Output format (`text`, `json`, or `csv`, default: text)
- `--output` or `-o`: Output file (default: stdout)

### Manage Resources

Update or list resources used by the library:

```bash
email-deliverability resources update
email-deliverability resources list
email-deliverability resources debug --resource dnsbl_list
```

Update options:
- `--resource` or `-r`: Specific resource to update (default: all)
- `--force`: Force update even if resource is current

List options:
- `--format` or `-f`: Output format (`text` or `json`, default: text)

Debug options:
- `--resource` or `-r`: Resource to debug (required)

### Generate IP Warming Plan

Create an IP warming schedule for a new sending IP:

```bash
email-deliverability warm-ip --ip 192.0.2.1 --days 30 --target 100000
```

Options:
- `--days` or `-d`: Number of days for warming (default: 30)
- `--target` or `-t`: Target daily email volume (required)
- `--format`: Output format (`text`, `json`, or `csv`, default: text)
- `--output` or `-o`: Output file (default: stdout)

### Comprehensive Check

Run a comprehensive deliverability check:

```bash
email-deliverability check --domain example.com --ip 192.0.2.1
```

Options:
- `--format` or `-f`: Output format (`text` or `json`, default: text)
- `--output` or `-o`: Output file (default: stdout)

### Version Information

Display version information:

```bash
email-deliverability version
```

## Output Formats

The CLI supports multiple output formats:

- **text**: Human-readable formatted text (default)
- **json**: JSON format for programmatic processing
- **csv**: CSV format for commands that return tabular data

## Examples

### Save IP reputation check as JSON

```bash
email-deliverability reputation --ip 192.0.2.1 --format json --output reputation.json
```

### Validate emails from a file and output as CSV

```bash
email-deliverability validate --file subscribers.txt --format csv --output validation_results.csv
```

### Update all resources

```bash
email-deliverability resources update --force
```

### Generate a warming plan as CSV

```bash
email-deliverability warm-ip --ip 192.0.2.1 --days 45 --target 500000 --format csv --output warming_plan.csv
```

## Automation Tips

The CLI can be easily integrated into automated scripts, cron jobs, or CI/CD pipelines:

```bash
#!/bin/bash

# Daily email deliverability check
email-deliverability check --domain example.com --ip 192.0.2.1 --format json --output /var/log/deliverability/$(date +%F).json

# Update resources once a week
if [ $(date +%u) -eq 1 ]; then
  email-deliverability resources update --force
fi
```