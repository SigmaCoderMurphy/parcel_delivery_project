#!/usr/bin/env python
"""
Test Script: Brevo Email Confirmation Setup
This script tests the Brevo API connection and generates a test email
"""

import os
import sys
import django
from pathlib import Path

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parcel_delivery.settings')
django.setup()

from django.conf import settings
from leads.models import Lead
from leads.brevo_service import send_lead_confirmation_email
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_brevo_connection():
    """Test Brevo API connection and settings"""
    print("\n" + "="*60)
    print("BREVO EMAIL SETUP - VERIFICATION TEST")
    print("="*60 + "\n")
    
    # Check 1: API Key configured
    print("✓ Check 1: Brevo API Key Configuration")
    if settings.BREVO_API_KEY:
        print(f"  ✓ API Key is set: {settings.BREVO_API_KEY[:10]}...{settings.BREVO_API_KEY[-10:]}")
    else:
        print("  ✗ CRITICAL: BREVO_API_KEY not found in .env")
        print("    Add your Brevo API key to .env file:")
        print("    BREVO_API_KEY=your_api_key_from_brevo")
        return False
    
    # Check 2: Sender email configured
    print("\n✓ Check 2: Sender Email Configuration")
    print(f"  ✓ Sender Email: {settings.BREVO_SENDER_EMAIL}")
    print(f"  ✓ Sender Name: {settings.BREVO_SENDER_NAME}")
    
    # Check 3: Site settings available
    print("\n✓ Check 3: Site Configuration")
    print(f"  ✓ Site Name: {settings.SITE_NAME}")
    print(f"  ✓ Site Email: {settings.SITE_EMAIL}")
    print(f"  ✓ Site Phone: {settings.SITE_PHONE}")
    
    # Check 4: Test email dependencies
    print("\n✓ Check 4: Required Dependencies")
    try:
        import httpx
        print(f"  ✓ httpx library installed: {httpx.__version__}")
    except ImportError:
        print("  ✗ httpx not installed. Run: pip install httpx")
        return False
    
    return True

def create_test_lead():
    """Create a test lead in the database"""
    print("\n✓ Check 5: Creating Test Lead")
    
    # Check if test lead exists
    test_lead = Lead.objects.filter(email='test@example.com').first()
    
    if test_lead:
        print(f"  ✓ Test lead already exists (ID: {test_lead.id})")
        print(f"    Email: {test_lead.email}")
        print(f"    Company: {test_lead.company_name}")
        return test_lead
    else:
        # Create new test lead
        test_lead = Lead.objects.create(
            company_name="Test Company Inc",
            contact_name="John Test",
            email="test@example.com",
            phone="416-555-0123",
            business_type="other",
            source="website",
            service_area="Toronto, ON",
            address="123 Test St, Toronto",
            status="new"
        )
        print(f"  ✓ Test lead created (ID: {test_lead.id})")
        print(f"    Company: {test_lead.company_name}")
        print(f"    Email: {test_lead.email}")
        return test_lead

def send_test_email(lead):
    """Send test confirmation email via Brevo"""
    print("\n✓ Check 6: Sending Test Email via Brevo")
    
    result = send_lead_confirmation_email(lead)
    
    if result:
        print(f"  ✓ EMAIL SENT SUCCESSFULLY!")
        print(f"    Recipient: {lead.email}")
        print(f"    To: {lead.contact_name}")
        print(f"    Subject: Thank You for Your Interest - {settings.SITE_NAME}")
        return True
    else:
        print(f"  ✗ Email send failed")
        print(f"    Check logs for detailed error information")
        print(f"    Verify BREVO_API_KEY is correct and active")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("EASTERN LOGISTICS - BREVO EMAIL CONFIRMATION SETUP")
    print("="*60)
    print("\nThis test will verify your Brevo email configuration")
    print("and send a test confirmation email.\n")
    
    # Step 1: Check configuration
    if not test_brevo_connection():
        print("\n" + "!"*60)
        print("SETUP INCOMPLETE - Please configure BREVO_API_KEY first")
        print("!"*60 + "\n")
        sys.exit(1)
    
    # Step 2: Create test lead
    test_lead = create_test_lead()
    
    # Step 3: Send test email
    success = send_test_email(test_lead)
    
    # Final summary
    print("\n" + "="*60)
    if success:
        print("✓ BREVO SETUP COMPLETE AND WORKING!")
        print("="*60)
        print("\nYou're ready to go! When users fill out the contact form,")
        print("they will automatically receive a confirmation email via Brevo.")
        print("\nDaily limit: 300 free emails/day (Brevo free plan)")
        print("\nTo test with a real form submission:")
        print("  1. Start your Django development server")
        print("  2. Go to /contact or fill any lead form on the website")
        print("  3. Check your email for the confirmation message")
    else:
        print("✗ BREVO SETUP INCOMPLETE - Please check errors above")
        print("="*60)
        print("\nNext steps:")
        print("  1. Verify your BREVO_API_KEY in .env is correct")
        print("  2. Go to https://app.brevo.com to check API key")
        print("  3. Ensure sender email matches a verified sender in Brevo")
        sys.exit(1)
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
