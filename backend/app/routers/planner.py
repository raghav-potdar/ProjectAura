from typing import List, Optional
from datetime import datetime
import pytz

import fitz  # PyMuPDF
from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from ..services import planner_service

router = APIRouter(prefix="/api/v1/planner", tags=["planner"])


class FixedEvent(BaseModel):
    date: str
    day: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    summary: str
    type: Optional[str] = None


class AnalyzeGoalsRequest(BaseModel):
    description: str


class AnalyzeGoalsResponse(BaseModel):
    analysis: str


class AnalyzeFeedbackRequest(BaseModel):
    feedback: str


class AnalyzeFeedbackResponse(BaseModel):
    constraints: str


class ScheduleItem(BaseModel):
    Day: Optional[str] = None
    Date: str
    Start_Time: Optional[str] = None
    End_Time: Optional[str] = None
    Task: str
    Category: Optional[str] = None


class GenerateScheduleRequest(BaseModel):
    fixed_schedule: List[FixedEvent]
    goals: str
    feedback_constraints: Optional[str] = None
    previous_schedule: Optional[List[ScheduleItem]] = None


class GenerateScheduleResponse(BaseModel):
    schedule: List[ScheduleItem]
    reasoning: Optional[str] = None


class CreateIcsRequest(BaseModel):
    schedule: List[ScheduleItem]
    fixed_schedule: List[FixedEvent]


class CreateIcsResponse(BaseModel):
    ics: str


class SyncToGoogleCalendarRequest(BaseModel):
    schedule: List[ScheduleItem]
    fixed_schedule: List[FixedEvent]


class SyncToGoogleCalendarResponse(BaseModel):
    message: str
    eventsCreated: int


@router.post("/parse-syllabus", response_model=List[FixedEvent])
async def parse_syllabus(file: UploadFile = File(...)) -> List[FixedEvent]:
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")
    try:
        payload = await file.read()
        document = fitz.open(stream=payload, filetype="pdf")
        text = ""
        for page in document:
            text += page.get_text()
        document.close()
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
        events = await planner_service.parse_syllabus(text)
        return [FixedEvent.model_validate(event) for event in events]
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Planner parse_syllabus endpoint error: {exc}")
        raise HTTPException(status_code=500, detail="Failed to parse syllabus.")


@router.post("/analyze-goals", response_model=AnalyzeGoalsResponse)
async def analyze_goals(request: AnalyzeGoalsRequest) -> AnalyzeGoalsResponse:
    analysis = await planner_service.analyze_goals(request.description)
    if not analysis:
        raise HTTPException(status_code=500, detail="Failed to analyze goals.")
    return AnalyzeGoalsResponse(analysis=analysis)


@router.post("/analyze-feedback", response_model=AnalyzeFeedbackResponse)
async def analyze_feedback(request: AnalyzeFeedbackRequest) -> AnalyzeFeedbackResponse:
    constraints = await planner_service.analyze_feedback(request.feedback)
    if not constraints:
        raise HTTPException(status_code=500, detail="Failed to analyze feedback.")
    return AnalyzeFeedbackResponse(constraints=constraints)


@router.post("/generate", response_model=GenerateScheduleResponse)
async def generate_schedule(request: GenerateScheduleRequest) -> GenerateScheduleResponse:
    result = await planner_service.generate_schedule(
        request.goals,
        [event.model_dump() for event in request.fixed_schedule],
        feedback_constraints=request.feedback_constraints,
        previous_schedule=[item.model_dump() for item in request.previous_schedule] if request.previous_schedule else None,
    )
    schedule = [ScheduleItem.model_validate(entry) for entry in result.get("schedule", [])]
    return GenerateScheduleResponse(schedule=schedule, reasoning=result.get("reasoning"))


@router.post("/ics", response_model=CreateIcsResponse)
async def create_ics(request: CreateIcsRequest) -> CreateIcsResponse:
    ics_content = planner_service.create_ics(
        [item.model_dump() for item in request.schedule],
        [event.model_dump() for event in request.fixed_schedule],
    )
    return CreateIcsResponse(ics=ics_content)


@router.post("/sync-to-google-calendar", response_model=SyncToGoogleCalendarResponse)
async def sync_to_google_calendar(request: SyncToGoogleCalendarRequest) -> SyncToGoogleCalendarResponse:
    """
    Sync events to Google Calendar by parsing schedule and fixed schedule,
    then creating events via Google Calendar API
    """
    from ..services.google_calendar_service import google_calendar_service
    
    if not google_calendar_service.calendar_id:
        raise HTTPException(
            status_code=503,
            detail="Google Calendar not initialized. Please configure credentials."
        )
    
    print(f"Syncing to calendar ID: {google_calendar_service.calendar_id}")
    print(f"Schedule items: {len(request.schedule)}, Fixed items: {len(request.fixed_schedule)}")
    
    try:
        events_created = 0
        errors = []
        timezone = pytz.timezone('America/New_York')
        
        # Process scheduled events
        for item in request.schedule:
            if not item.Date or not item.Task:
                print(f"Skipping invalid schedule item: {item}")
                continue
                
            try:
                # Parse date and time
                event_date = item.Date  # Format: YYYY-MM-DD
                start_time = item.Start_Time or "09:00:00"  # Default to 9 AM
                end_time = item.End_Time or "10:00:00"      # Default to 10 AM
                
                # Validate time format
                if len(start_time.split(':')) != 3:
                    start_time = f"{start_time}:00" if ':' in start_time else f"{start_time}:00:00"
                if len(end_time.split(':')) != 3:
                    end_time = f"{end_time}:00" if ':' in end_time else f"{end_time}:00:00"
                
                # Parse datetime strings and add timezone
                start_datetime_str = f"{event_date} {start_time}"
                end_datetime_str = f"{event_date} {end_time}"
                
                print(f"Processing: {item.Task} on {start_datetime_str}")
                
                # Create timezone-aware datetime objects
                start_dt = timezone.localize(datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S"))
                end_dt = timezone.localize(datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S"))
                
                # Convert to RFC3339 format
                start_rfc3339 = start_dt.isoformat()
                end_rfc3339 = end_dt.isoformat()
                
                # Build Google Calendar event
                google_event = {
                    'summary': item.Task,
                    'description': f"Category: {item.Category or 'General'}\nDay: {item.Day or ''}",
                    'start': {
                        'dateTime': start_rfc3339,
                        'timeZone': 'America/New_York'
                    },
                    'end': {
                        'dateTime': end_rfc3339,
                        'timeZone': 'America/New_York'
                    }
                }
                
                result = google_calendar_service.add_event(google_event)
                if result:
                    events_created += 1
                    print(f"  ✓ Created: {item.Task}")
                else:
                    errors.append(f"Failed to create: {item.Task}")
            except Exception as e:
                error_msg = f"Error processing '{item.Task}': {str(e)}"
                print(error_msg)
                errors.append(error_msg)
                continue
        
        # Process fixed schedule events
        for event in request.fixed_schedule:
            if not event.date or not event.summary:
                print(f"Skipping invalid fixed event: {event}")
                continue
                
            try:
                event_date = event.date
                start_time = event.start_time or "09:00:00"
                end_time = event.end_time or "10:00:00"
                
                # Validate time format
                if len(start_time.split(':')) != 3:
                    start_time = f"{start_time}:00" if ':' in start_time else f"{start_time}:00:00"
                if len(end_time.split(':')) != 3:
                    end_time = f"{end_time}:00" if ':' in end_time else f"{end_time}:00:00"
                
                start_datetime_str = f"{event_date} {start_time}"
                end_datetime_str = f"{event_date} {end_time}"
                
                print(f"Processing: {event.summary} on {start_datetime_str}")
                
                start_dt = timezone.localize(datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S"))
                end_dt = timezone.localize(datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S"))
                
                start_rfc3339 = start_dt.isoformat()
                end_rfc3339 = end_dt.isoformat()
                
                google_event = {
                    'summary': event.summary,
                    'description': f"Type: {event.type or 'Fixed Event'}\nDay: {event.day or ''}",
                    'start': {
                        'dateTime': start_rfc3339,
                        'timeZone': 'America/New_York'
                    },
                    'end': {
                        'dateTime': end_rfc3339,
                        'timeZone': 'America/New_York'
                    }
                }
                
                result = google_calendar_service.add_event(google_event)
                if result:
                    events_created += 1
                    print(f"  ✓ Created: {event.summary}")
                else:
                    errors.append(f"Failed to create: {event.summary}")
            except Exception as e:
                error_msg = f"Error processing '{event.summary}': {str(e)}"
                print(error_msg)
                errors.append(error_msg)
                continue
        
        print(f"\nTotal events created: {events_created}")
        if errors:
            print(f"Errors encountered: {len(errors)}")
            for err in errors[:5]:  # Show first 5 errors
                print(f"  - {err}")
        
        return SyncToGoogleCalendarResponse(
            message=f"Successfully synced {events_created} events to Google Calendar" + 
                    (f" ({len(errors)} errors)" if errors else ""),
            eventsCreated=events_created
        )
        
    except Exception as exc:
        print(f"Error syncing to Google Calendar: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync events to Google Calendar: {str(exc)}"
        )
