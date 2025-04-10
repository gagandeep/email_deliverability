#!/usr/bin/env python3
"""
Command line interface for Email Deliverability library.

This module provides a CLI for accessing the main functionality of the 
Email Deliverability library, including authentication checks, reputation
monitoring, email validation, and resource management.

Author: innerkore
Date: 2025-04-10
"""

import os
import sys
import argparse
import json
import csv
from datetime import datetime
import logging
from typing import List, Optional, Dict, Any, Union

from email_deliverability import DeliverabilityManager
from email_deliverability.resource_manager import update_deliverability_resources, debug_resource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('email_deliverability.cli')


class EmailDeliverabilityCommandLine:
    """Command line interface for Email Deliverability library."""

    def __init__(self):
        """Initialize the CLI."""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser for the CLI.
        
        Returns:
            argparse.ArgumentParser: The configured argument parser
        """
        parser = argparse.ArgumentParser(
            description='Email Deliverability CLI - Analyze and improve email deliverability',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
Examples:
  Check domain authentication:
    email-deliverability auth --domain example.com
    
  Check IP reputation:
    email-deliverability reputation --ip 192.0.2.1
    
  Validate emails:
    email-deliverability validate --email user@example.com
    email-deliverability validate --file emails.txt

  Update cached resources:
    email-deliverability resources update
    
  Generate IP warming plan:
    email-deliverability warm-ip --ip 192.0.2.1 --days 30 --target 100000
    
Version: 0.1.2
Date: {datetime.utcnow().strftime('%Y-%m-%d')}
"""
        )
        
        # Add subparsers for different commands
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # Authentication command
        auth_parser = subparsers.add_parser('auth', help='Check domain authentication (SPF, DKIM, DMARC)')
        auth_parser.add_argument('--domain', '-d', required=True, help='Domain to check')
        auth_parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                                help='Output format')
        auth_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
        
        # Reputation command
        rep_parser = subparsers.add_parser('reputation', help='Check IP or domain reputation')
        rep_parser.add_argument('--ip', '-i', help='IP address to check')
        rep_parser.add_argument('--domain', '-d', help='Domain to check')
        rep_parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                              help='Output format')
        rep_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
        
        # Email validation command
        val_parser = subparsers.add_parser('validate', help='Validate email addresses')
        email_group = val_parser.add_mutually_exclusive_group(required=True)
        email_group.add_argument('--email', '-e', help='Single email address to validate')
        email_group.add_argument('--file', '-f', help='File with email addresses (one per line)')
        val_parser.add_argument('--check-mx', '-m', action='store_true', 
                               help='Check MX records (slower but more accurate)')
        val_parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text',
                              help='Output format')
        val_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
        
        # Resource management command
        res_parser = subparsers.add_parser('resources', help='Manage deliverability resources')
        res_subparsers = res_parser.add_subparsers(dest='resource_command', help='Resource command')
        
        # Update resources command
        update_parser = res_subparsers.add_parser('update', help='Update resources')
        update_parser.add_argument('--resource', '-r', 
                                 help='Specific resource to update (default: all)')
        update_parser.add_argument('--force', action='store_true',
                                 help='Force update even if resource is current')
        
        # List resources command
        list_parser = res_subparsers.add_parser('list', help='List available resources')
        list_parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                               help='Output format')
        
        # Debug resources command
        debug_parser = res_subparsers.add_parser('debug', help='Debug resource information')
        debug_parser.add_argument('--resource', '-r', required=True,
                                help='Resource to debug')
        
        # IP warming command
        warm_parser = subparsers.add_parser('warm-ip', help='Generate IP warming plan')
        warm_parser.add_argument('--ip', '-i', required=True, help='IP address to warm')
        warm_parser.add_argument('--days', '-d', type=int, default=30, 
                               help='Number of days for warming (default: 30)')
        warm_parser.add_argument('--target', '-t', type=int, required=True,
                               help='Target daily email volume')
        warm_parser.add_argument('--format', '-f', choices=['text', 'json', 'csv'], default='text',
                               help='Output format')
        warm_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
        
        # Comprehensive deliverability check
        check_parser = subparsers.add_parser('check', help='Comprehensive deliverability check')
        check_parser.add_argument('--domain', '-d', required=True, help='Domain to check')
        check_parser.add_argument('--ip', '-i', help='IP address to check')
        check_parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                                help='Output format')
        check_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
        
        # Version command
        subparsers.add_parser('version', help='Show version information')
        
        return parser
    
    def _write_output(self, data: Union[str, dict], format_type: str, output_file: Optional[str]) -> None:
        """Write output data to file or stdout.
        
        Args:
            data: Data to write (string or dict)
            format_type: Format type (text, json, csv)
            output_file: Output file path or None for stdout
        """
        # Convert data to the right format if needed
        if format_type == 'json' and isinstance(data, dict):
            output_data = json.dumps(data, indent=2)
        elif format_type == 'csv' and isinstance(data, dict):
            # This is a simple implementation for CSV
            # More complex data structures would need specialized handling
            if output_file:
                with open(output_file, 'w', newline='') as f:
                    if 'results' in data and isinstance(data['results'], list):
                        if data['results'] and isinstance(data['results'][0], dict):
                            fieldnames = data['results'][0].keys()
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(data['results'])
                    return
            output_data = str(data)  # Fallback if we can't write CSV directly
        else:
            # For text format, convert dict to formatted string
            if isinstance(data, dict):
                output_data = self._format_dict_as_text(data)
            else:
                output_data = str(data)
        
        # Write to file or stdout
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_data)
        else:
            print(output_data)
    
    def _format_dict_as_text(self, data: dict, indent: int = 0) -> str:
        """Format a dictionary as a human-readable text.
        
        Args:
            data: Dictionary to format
            indent: Indentation level
            
        Returns:
            str: Formatted text
        """
        result = []
        prefix = ' ' * indent
        
        for key, value in data.items():
            key_str = key.replace('_', ' ').capitalize()
            
            if isinstance(value, dict):
                result.append(f"{prefix}{key_str}:")
                result.append(self._format_dict_as_text(value, indent + 2))
            elif isinstance(value, list):
                result.append(f"{prefix}{key_str}:")
                for item in value:
                    if isinstance(item, dict):
                        result.append(self._format_dict_as_text(item, indent + 2))
                    else:
                        result.append(f"{prefix}  - {item}")
            else:
                result.append(f"{prefix}{key_str}: {value}")
                
        return '\n'.join(result)
    
    def _check_authentication(self, args) -> None:
        """Check domain authentication and output results.
        
        Args:
            args: Parsed command-line arguments
        """
        manager = DeliverabilityManager(domain=args.domain)
        results = manager.analyze_domain_setup()
        
        # Add a summary for text output
        if args.format == 'text':
            summary = {
                'summary': {
                    'domain': args.domain,
                    'score': f"{results['overall_score']}/100",
                    'spf_status': results['spf']['status'],
                    'dkim_status': results['dkim']['status'],
                    'dmarc_status': results['dmarc']['status'],
                }
            }
            results = {**summary, **results}
        
        self._write_output(results, args.format, args.output)
    
    def _check_reputation(self, args) -> None:
        """Check IP or domain reputation and output results.
        
        Args:
            args: Parsed command-line arguments
        """
        if not args.ip and not args.domain:
            print("Error: Either --ip or --domain must be specified")
            sys.exit(1)
            
        manager = DeliverabilityManager(domain=args.domain, ip=args.ip)
        
        if args.ip:
            results = manager.check_ip_reputation()
            entity_type = 'IP'
            entity_value = args.ip
        else:
            results = manager.check_domain_reputation()
            entity_type = 'Domain'
            entity_value = args.domain
        
        # Add a summary for text output
        if args.format == 'text':
            if results['status'] == 'clean':
                status_text = f"{entity_type} is not listed on any blacklists"
            else:
                status_text = f"{entity_type} is listed on {len(results.get('blacklisted_on', []))} blacklists"
                
            summary = {
                'summary': {
                    f'{entity_type.lower()}': entity_value,
                    'status': results['status'],
                    'details': status_text,
                }
            }
            results = {**summary, **results}
        
        self._write_output(results, args.format, args.output)
    
    def _validate_emails(self, args) -> None:
        """Validate email addresses and output results.
        
        Args:
            args: Parsed command-line arguments
        """
        manager = DeliverabilityManager()
        
        # Get emails from file or command line
        if args.email:
            emails = [args.email]
        else:  # args.file must be set due to required mutually exclusive group
            try:
                with open(args.file, 'r') as f:
                    emails = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error reading email file: {e}")
                sys.exit(1)
        
        # Validate emails
        results = manager.validate_email_list(emails, check_mx=args.check_mx)
        
        # Add a summary for text output
        if args.format == 'text':
            summary = {
                'summary': {
                    'total_emails': results['analysis']['total_emails'],
                    'valid_emails': results['analysis']['valid_emails'],
                    'invalid_emails': results['analysis']['invalid_emails'],
                    'disposable_domains': results['analysis']['disposable_domains'],
                }
            }
            results = {**summary, **results}
        
        self._write_output(results, args.format, args.output)
    
    def _manage_resources(self, args) -> None:
        """Manage deliverability resources.
        
        Args:
            args: Parsed command-line arguments
        """
        if args.resource_command == 'update':
            if args.resource:
                # Update specific resource
                manager = DeliverabilityManager()
                result = manager.resource_manager.download_resource(args.resource, force=args.force)
                print(f"Updated resource {args.resource}: {len(result) if result else 0} items")
            else:
                # Update all resources
                results = update_deliverability_resources()
                for resource, info in results.items():
                    print(f"{resource}: {info['items']} items ({info['status']})")
        
        elif args.resource_command == 'list':
            manager = DeliverabilityManager()
            resources = manager.resource_manager.resources
            
            if args.format == 'json':
                self._write_output(resources, args.format, None)
            else:
                print("Available resources:")
                for name, info in resources.items():
                    has_url = "Yes" if "url" in info else "No"
                    print(f"- {name} (External URL: {has_url})")
        
        elif args.resource_command == 'debug':
            debug_info = debug_resource(args.resource)
            print(f"Debug information for {args.resource}:")
            for key, value in debug_info.items():
                print(f"  {key}: {value}")
    
    def _generate_warming_plan(self, args) -> None:
        """Generate IP warming plan and output results.
        
        Args:
            args: Parsed command-line arguments
        """
        manager = DeliverabilityManager(ip=args.ip)
        plan = manager.generate_ip_warming_plan(
            days=args.days,
            target_volume=args.target
        )
        
        if args.format == 'csv':
            # Special handling for CSV format
            if args.output:
                with open(args.output, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Day', 'Date', 'Volume', 'Percentage'])
                    for day in plan['schedule']:
                        writer.writerow([
                            day['day'],
                            day['date'],
                            day['volume'],
                            f"{day['percentage']}%"
                        ])
                print(f"IP warming plan saved to {args.output}")
            else:
                print("Day,Date,Volume,Percentage")
                for day in plan['schedule']:
                    print(f"{day['day']},{day['date']},{day['volume']},{day['percentage']}%")
        else:
            self._write_output(plan, args.format, args.output)
    
    def _check_deliverability(self, args) -> None:
        """Run a comprehensive deliverability check.
        
        Args:
            args: Parsed command-line arguments
        """
        manager = DeliverabilityManager(domain=args.domain, ip=args.ip)
        results = manager.check_deliverability_status()
        
        # Add a summary section for text format
        if args.format == 'text':
            summary = {
                'summary': {
                    'domain': args.domain,
                    'ip': args.ip or 'Not specified',
                    'authentication_score': f"{results['authentication']['overall_score']}/100",
                    'reputation': results['reputation']['status'],
                    'recommendations': len(results['recommendations'])
                }
            }
            results = {**summary, **results}
        
        self._write_output(results, args.format, args.output)
    
    def _show_version(self) -> None:
        """Show version information."""
        from email_deliverability import __version__
        
        print(f"Email Deliverability CLI v{__version__}")
        print(f"Current time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Author: innerkore")
        print("License: MIT")
        print("Documentation: https://email-deliverability.readthedocs.io/")
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the provided arguments.
        
        Args:
            args: Command-line arguments (uses sys.argv if None)
            
        Returns:
            int: Exit code (0 for success, non-zero for errors)
        """
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            if parsed_args.command == 'auth':
                self._check_authentication(parsed_args)
            elif parsed_args.command == 'reputation':
                self._check_reputation(parsed_args)
            elif parsed_args.command == 'validate':
                self._validate_emails(parsed_args)
            elif parsed_args.command == 'resources':
                self._manage_resources(parsed_args)
            elif parsed_args.command == 'warm-ip':
                self._generate_warming_plan(parsed_args)
            elif parsed_args.command == 'check':
                self._check_deliverability(parsed_args)
            elif parsed_args.command == 'version':
                self._show_version()
            else:
                print(f"Unknown command: {parsed_args.command}")
                self.parser.print_help()
                return 1
            
            return 0
            
        except Exception as e:
            logger.error(f"Error executing command: {e}", exc_info=True)
            print(f"Error: {e}")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = EmailDeliverabilityCommandLine()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()