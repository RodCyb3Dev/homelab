#!/usr/bin/env python3
"""
Test SMTP credentials for Authelia/ProtonMail
Usage:
    # Test with credentials from server secrets
    python3 scripts/test_smtp.py --server

    # Test with manual credentials
    python3 scripts/test_smtp.py --username no-reply@kodeflash.dev --password YOUR_PASSWORD

    # Test with environment variables
    export AUTHELIA_SMTP_USERNAME="no-reply@kodeflash.dev"
    export AUTHELIA_NOTIFIER_SMTP_PASSWORD="YOUR_PASSWORD"
    python3 scripts/test_smtp.py
"""

import argparse
import smtplib
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass

def test_smtp_connection(username, password, sender_email=None, test_email=None):
    """
    Test SMTP connection and authentication with ProtonMail

    Args:
        username: SMTP username (email address)
        password: SMTP password (app-specific password)
        sender_email: Email address to use as sender (defaults to username)
        test_email: Email address to send test message to (optional)
    """
    smtp_server = "smtp.protonmail.ch"
    smtp_port = 587

    if sender_email is None:
        sender_email = username

    print(f"🔍 Testing SMTP connection to {smtp_server}:{smtp_port}")
    print(f"   Username: {username}")
    print(f"   Sender: {sender_email}")
    print()

    try:
        # Create SMTP connection
        print("📡 Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.set_debuglevel(1)  # Enable debug output

        # Start TLS
        print("🔒 Starting TLS encryption...")
        server.starttls()

        # Authenticate
        print("🔐 Authenticating...")
        server.login(username, password)
        print("✅ Authentication successful!")

        if test_email:
            # Send test email
            print(f"\n📧 Sending test email to {test_email}...")
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = test_email
            msg['Subject'] = "Authelia SMTP Test"

            body = f"""
This is a test email from Authelia SMTP configuration.

SMTP Server: {smtp_server}:{smtp_port}
Username: {username}
Sender: {sender_email}

If you received this email, your SMTP configuration is working correctly!
"""
            msg.attach(MIMEText(body, 'plain'))

            server.send_message(msg)
            print(f"✅ Test email sent successfully to {test_email}!")
        else:
            print("\n💡 Tip: Use --test-email to send a test email")

        server.quit()
        print("\n✅ SMTP test completed successfully!")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ Authentication failed!")
        print(f"   Error: {e}")
        print("\n💡 Common issues:")
        print("   1. App-specific password is incorrect or expired")
        print("   2. Username doesn't match ProtonMail account")
        print("   3. Custom domain email not properly configured in ProtonMail")
        print("   4. Two-factor authentication not properly set up")
        return False

    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP error occurred!")
        print(f"   Error: {e}")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error occurred!")
        print(f"   Error: {type(e).__name__}: {e}")
        return False


def get_credentials_from_server():
    """Get credentials from server secret files"""
    import subprocess

    print("📥 Fetching credentials from server...")

    try:
        # Read username
        result = subprocess.run(
            ["ssh", "-i", os.path.expanduser("~/.ssh/ansible_key"), 
             "rodkode@95.216.176.147", 
             "cat /opt/homelab/config/authelia/secrets/AUTHELIA_SMTP_USERNAME"],
            capture_output=True,
            text=True,
            check=True
        )
        username = result.stdout.strip()

        # Read password
        result = subprocess.run(
            ["ssh", "-i", os.path.expanduser("~/.ssh/ansible_key"), 
             "rodkode@95.216.176.147", 
             "cat /opt/homelab/config/authelia/secrets/AUTHELIA_NOTIFIER_SMTP_PASSWORD"],
            capture_output=True,
            text=True,
            check=True
        )
        password = result.stdout.strip()

        print(f"✅ Credentials fetched from server")
        return username, password

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fetch credentials from server: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ SSH not found. Please install SSH or use --username and --password flags")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Test SMTP credentials for Authelia/ProtonMail",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--server",
        action="store_true",
        help="Fetch credentials from server secret files via SSH"
    )
    parser.add_argument(
        "--username",
        type=str,
        help="SMTP username (email address)",
        default=os.environ.get("AUTHELIA_SMTP_USERNAME")
    )
    parser.add_argument(
        "--password",
        type=str,
        help="SMTP password (app-specific password)",
        default=os.environ.get("AUTHELIA_NOTIFIER_SMTP_PASSWORD")
    )
    parser.add_argument(
        "--sender",
        type=str,
        help="Sender email address (defaults to username)",
        default=None
    )
    parser.add_argument(
        "--test-email",
        type=str,
        help="Email address to send test message to",
        default=None
    )

    args = parser.parse_args()

    # Get credentials
    if args.server:
        username, password = get_credentials_from_server()
    else:
        username = args.username
        password = args.password

        if not username:
            username = input("Enter SMTP username (email): ").strip()

        if not password:
            password = getpass("Enter SMTP password (app-specific): ")

    if not username or not password:
        print("❌ Username and password are required!")
        sys.exit(1)

    # Test SMTP connection
    success = test_smtp_connection(
        username=username,
        password=password,
        sender_email=args.sender,
        test_email=args.test_email
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
