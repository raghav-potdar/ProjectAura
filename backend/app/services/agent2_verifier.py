import json
from pydantic import ValidationError, parse_obj_as
from typing import List
from datetime import datetime, time
from ..models import CalendarEvent
import uuid

def verify_tasks(schedule_string: str) -> List[CalendarEvent]:
    """
    Takes the raw JSON string from Agent 1 and converts it into CalendarEvent objects
    """
    try:
        schedule_data = json.loads(schedule_string)
        events = []
        
        for class_item in schedule_data:
            try:
                # Parse times
                start_time = datetime.strptime(class_item['startTime'], '%H:%M').time()
                end_time = datetime.strptime(class_item['endTime'], '%H:%M').time()
                
                # Create calendar event
                event = CalendarEvent(
                    id=f"class-{uuid.uuid4()}",
                    title=class_item['title'],
                    startTime=start_time,
                    endTime=end_time,
                    daysOfWeek=class_item['daysOfWeek'],
                    color="#2563eb"  # Default blue color for classes
                )
                events.append(event)
            except (KeyError, ValueError) as e:
                print(f"Error processing class item: {e}")
                continue
                
        return events
    except json.JSONDecodeError as e:
        print(f"Error parsing schedule JSON: {e}")
        return []


def verify_assignments(assignments_string: str) -> List[dict]:
    """
    Parse and validate the JSON produced by Agent 1 for assignments.
    Returns a list of assignment dictionaries with keys: title, due_date (str or None), phases (list of dicts)
    Each phase dict must have: title, duration_minutes (int), intensity (Low/Medium/High)
    """
    try:
        data = json.loads(assignments_string)
        valid_assignments = []

        for item in data:
            title = item.get('title') or item.get('name')
            due_date = item.get('due_date') or item.get('deadline') or None
            phases = item.get('phases', [])
            if not title or not isinstance(phases, list):
                print(f"Skipping invalid assignment item: {item}")
                continue

            clean_phases = []
            for ph in phases:
                try:
                    p_title = ph.get('title') or ph.get('name') or 'Phase'
                    duration = int(ph.get('duration_minutes') or ph.get('duration') or 0)
                    intensity = ph.get('intensity', 'Medium')
                    if intensity not in ('Low', 'Medium', 'High'):
                        intensity = 'Medium'
                    if duration <= 0:
                        # Skip zero-length phases
                        continue
                    clean_phases.append({
                        'title': p_title,
                        'duration_minutes': duration,
                        'intensity': intensity
                    })
                except Exception as e:
                    print(f"Error parsing phase: {e}")
                    continue

            if not clean_phases:
                print(f"No valid phases for assignment {title}")
                continue

            valid_assignments.append({
                'title': title,
                'due_date': due_date,
                'phases': clean_phases
            })

        return valid_assignments
    except json.JSONDecodeError as e:
        print(f"Error parsing assignments JSON: {e}")
        return []