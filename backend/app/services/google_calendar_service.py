"""
Google Calendar API Service
Handles calendar creation, configuration, and management
"""
import os
import json
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

class GoogleCalendarService:
    def __init__(self):
        self.calendar_id: Optional[str] = None
        self.service = None
        self.credentials = None
        
    def initialize_service(self):
        """Initialize Google Calendar API service with credentials"""
        try:
            # Option 1: Use service account JSON file
            credentials_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
            if credentials_path and os.path.exists(credentials_path):
                self.credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            # Option 2: Use service account JSON from environment variable
            elif os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'):
                credentials_info = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'))
                self.credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            else:
                print("Warning: No Google Calendar credentials found. Calendar features will be disabled.")
                return False
            
            self.service = build('calendar', 'v3', credentials=self.credentials)
            return True
        except Exception as e:
            print(f"Error initializing Google Calendar service: {e}")
            return False
    
    def create_public_calendar(self, summary: str = "Aura Event Schedule", 
                               description: str = "All events and schedules managed by Aura",
                               timezone: str = "America/New_York") -> Optional[str]:
        """
        Create a new calendar and make it public
        Returns the calendar ID if successful, None otherwise
        """
        if not self.service:
            print("Google Calendar service not initialized")
            return None
        
        try:
            # Step 1: Create the calendar
            calendar = {
                'summary': summary,
                'description': description,
                'timeZone': timezone
            }
            
            created_calendar = self.service.calendars().insert(body=calendar).execute()
            self.calendar_id = created_calendar['id']
            print(f"Created calendar with ID: {self.calendar_id}")
            
            # Step 2: Make it public (reader access for everyone)
            rule = {
                'scope': {
                    'type': 'default'
                },
                'role': 'reader'
            }
            
            self.service.acl().insert(
                calendarId=self.calendar_id,
                body=rule
            ).execute()
            print(f"Calendar is now public")
            
            return self.calendar_id
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
        except Exception as e:
            print(f"Unexpected error creating calendar: {e}")
            return None
    
    def get_embed_url(self) -> Optional[str]:
        """Get the embeddable iframe URL for the calendar"""
        if not self.calendar_id:
            return None
        
        # URL encode the calendar ID (replace @ with %40)
        encoded_id = self.calendar_id.replace('@', '%40')
        return f"https://calendar.google.com/calendar/embed?src={encoded_id}"
    
    def add_event(self, event_data: dict) -> Optional[dict]:
        """Add an event to the calendar"""
        if not self.service or not self.calendar_id:
            print("Cannot add event: service or calendar_id not initialized")
            return None
        
        try:
            print(f"Adding event to calendar: {self.calendar_id}")
            print(f"Event data: {event_data}")
            
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_data
            ).execute()
            
            print(f"Successfully created event: {event.get('id')}")
            return event
        except HttpError as error:
            print(f"An error occurred adding event: {error}")
            print(f"Calendar ID being used: {self.calendar_id}")
            return None
        except Exception as e:
            print(f"Unexpected error adding event: {e}")
            return None
    
    def list_calendars(self):
        """List all calendars (for debugging)"""
        if not self.service:
            return []
        
        try:
            calendar_list = self.service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as error:
            print(f"An error occurred listing calendars: {error}")
            return []
    
    def delete_calendar(self, calendar_id: str = None):
        """Delete a calendar"""
        if not self.service:
            return False
        
        cal_id = calendar_id or self.calendar_id
        if not cal_id:
            return False
        
        try:
            self.service.calendars().delete(calendarId=cal_id).execute()
            print(f"Deleted calendar: {cal_id}")
            return True
        except HttpError as error:
            print(f"An error occurred deleting calendar: {error}")
            return False


# Global instance
google_calendar_service = GoogleCalendarService()
