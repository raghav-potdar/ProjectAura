"""
Quick test script to verify Google Calendar API setup
Run this to check if your credentials are configured correctly
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.google_calendar_service import GoogleCalendarService

def test_calendar_setup():
    print("=" * 60)
    print("Google Calendar API Setup Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check for credentials
    print("\n1. Checking for credentials...")
    has_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    has_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    
    if has_file:
        print(f"   ✓ Found GOOGLE_SERVICE_ACCOUNT_FILE: {has_file}")
        if os.path.exists(has_file):
            print(f"   ✓ File exists")
        else:
            print(f"   ✗ File does not exist!")
            return False
    elif has_json:
        print(f"   ✓ Found GOOGLE_SERVICE_ACCOUNT_JSON (length: {len(has_json)} chars)")
    else:
        print("   ✗ No credentials found!")
        print("\n   Please set either:")
        print("   - GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/credentials.json")
        print("   - GOOGLE_SERVICE_ACCOUNT_JSON={...json content...}")
        return False
    
    # Initialize service
    print("\n2. Initializing Google Calendar service...")
    service = GoogleCalendarService()
    if service.initialize_service():
        print("   ✓ Service initialized successfully")
    else:
        print("   ✗ Failed to initialize service")
        return False
    
    # Test listing calendars
    print("\n3. Testing API access (listing calendars)...")
    try:
        calendars = service.list_calendars()
        print(f"   ✓ API access successful! Found {len(calendars)} calendar(s)")
        if calendars:
            print("\n   Your calendars:")
            for cal in calendars[:5]:  # Show first 5
                print(f"   - {cal.get('summary', 'Unknown')} ({cal.get('id', 'no-id')})")
    except Exception as e:
        print(f"   ✗ API access failed: {e}")
        return False
    
    # Test creating a calendar
    print("\n4. Testing calendar creation...")
    try:
        calendar_id = service.create_public_calendar(
            summary="Aura Test Calendar",
            description="Test calendar - safe to delete"
        )
        if calendar_id:
            print(f"   ✓ Calendar created successfully!")
            print(f"   Calendar ID: {calendar_id}")
            embed_url = service.get_embed_url()
            print(f"   Embed URL: {embed_url}")
            
            # Clean up
            print("\n5. Cleaning up test calendar...")
            if service.delete_calendar(calendar_id):
                print("   ✓ Test calendar deleted")
            
            return True
        else:
            print("   ✗ Failed to create calendar")
            return False
    except Exception as e:
        print(f"   ✗ Calendar creation failed: {e}")
        return False

if __name__ == "__main__":
    print("\nMake sure you're in the backend directory and have .env configured!")
    input("Press Enter to continue...")
    
    success = test_calendar_setup()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed! Your Google Calendar setup is working.")
        print("\nYou can now start the backend with:")
        print("  python -m uvicorn app.main:app --reload")
    else:
        print("✗ Setup incomplete. Please check the errors above.")
        print("\nRefer to GOOGLE_CALENDAR_SETUP.md for detailed instructions.")
    print("=" * 60)
