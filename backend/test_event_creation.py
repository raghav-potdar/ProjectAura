"""
Quick test to check calendar creation and event addition
"""
import os
import sys
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.google_calendar_service import GoogleCalendarService

def test_calendar_event():
    print("=" * 60)
    print("Google Calendar Event Creation Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize service
    print("\n1. Initializing service...")
    service = GoogleCalendarService()
    if not service.initialize_service():
        print("   ✗ Failed to initialize service")
        return False
    print("   ✓ Service initialized")
    
    # Create a test calendar
    print("\n2. Creating test calendar...")
    calendar_id = service.create_public_calendar(
        summary="Aura Test Calendar - Event Test",
        description="Testing event creation"
    )
    
    if not calendar_id:
        print("   ✗ Failed to create calendar")
        return False
    
    print(f"   ✓ Calendar created: {calendar_id}")
    print(f"   Calendar ID format check: {'@group.calendar.google.com' in calendar_id}")
    
    # Create a test event with proper RFC3339 format
    print("\n3. Creating test event...")
    timezone = pytz.timezone('America/New_York')
    
    # Create a simple event for tomorrow at 2 PM
    start_dt = timezone.localize(datetime(2025, 11, 10, 14, 0, 0))
    end_dt = timezone.localize(datetime(2025, 11, 10, 15, 0, 0))
    
    event_data = {
        'summary': 'Test Event',
        'description': 'This is a test event to verify API integration',
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'America/New_York'
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'America/New_York'
        }
    }
    
    print(f"   Event start: {start_dt.isoformat()}")
    print(f"   Event end: {end_dt.isoformat()}")
    
    result = service.add_event(event_data)
    
    if result:
        print(f"   ✓ Event created successfully!")
        print(f"   Event ID: {result.get('id')}")
        print(f"   Event link: {result.get('htmlLink')}")
    else:
        print(f"   ✗ Failed to create event")
        return False
    
    # Clean up
    print("\n4. Cleaning up test calendar...")
    if service.delete_calendar(calendar_id):
        print("   ✓ Test calendar deleted")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    print("\nMake sure you're in the backend directory and have .env configured!")
    input("Press Enter to continue...")
    
    success = test_calendar_event()
    
    if not success:
        print("\n✗ Test failed. Check the errors above.")
        sys.exit(1)
