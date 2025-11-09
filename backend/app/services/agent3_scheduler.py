from typing import List, Dict
from datetime import datetime, timedelta, time, date
import uuid

from ..models import VerifiedTask, CalendarEvent

# Maps to Task 6
# This is Person 4's second and most complex file.
# It handles scheduling logic.

def schedule_tasks(tasks: List[CalendarEvent], base_events: List[CalendarEvent]) -> List[CalendarEvent]:
    """
    For class schedules, we just return the events as they are since they're already properly formatted
    """
    return tasks


def schedule_assignments(assignments: List[dict], class_events: List[CalendarEvent]) -> List[CalendarEvent]:
    """
    Schedule assignment phases into the next week's free slots, taking class_events
    (recurring) into account. Each assignment in 'assignments' should be a dict:
      { 'title': str, 'due_date': 'YYYY-MM-DD' or None, 'phases': [ {title, duration_minutes, intensity} ] }

    Returns a list of concrete CalendarEvent objects with start/end datetimes for the scheduled chunks.
    """
    scheduled_events: List[CalendarEvent] = []

    today = date.today()
    # Scheduling window: start today, cover the next 7 days (immediate visibility in calendar)
    window_start_date = today
    window_start = datetime.combine(window_start_date, time(8, 0))
    window_end = datetime.combine(window_start_date + timedelta(days=6), time(22, 0))

    # Expand class_events (recurring) into busy blocks within the window
    busy_blocks: List[Dict] = []
    cur_day = window_start_date
    while cur_day <= (window_start_date + timedelta(days=6)):
        for ev in class_events:
            if ev.daysOfWeek and cur_day.weekday() in ev.daysOfWeek and ev.startTime and ev.endTime:
                s_dt = datetime.combine(cur_day, ev.startTime)
                e_dt = datetime.combine(cur_day, ev.endTime)
                if e_dt < s_dt:
                    e_dt += timedelta(days=1)
                busy_blocks.append({"start": s_dt, "end": e_dt})
        cur_day += timedelta(days=1)

    # Sort and merge busy blocks
    busy_blocks.sort(key=lambda x: x['start'])
    merged: List[Dict] = []
    for block in busy_blocks:
        if not merged:
            merged.append(block)
        else:
            last = merged[-1]
            if block['start'] <= last['end']:
                # overlap
                last['end'] = max(last['end'], block['end'])
            else:
                merged.append(block)
    busy_blocks = merged

    # Build free slots between window_start and window_end
    free_slots: List[Dict] = []
    cursor = window_start
    for b in busy_blocks:
        if cursor < b['start']:
            free_slots.append({"start": cursor, "end": b['start']})
        cursor = max(cursor, b['end'])
    if cursor < window_end:
        free_slots.append({"start": cursor, "end": window_end})

    # Helper: chunk duration based on intensity
    def chunk_size_for_intensity(intensity: str) -> int:
        if intensity == 'High':
            return 60
        if intensity == 'Medium':
            return 45
        return 30

    # Schedule each assignment in order
    for assignment in assignments:
        title = assignment.get('title', 'Assignment')
        due_date_str = assignment.get('due_date')
        try:
            cutoff_date = None
            if due_date_str:
                cutoff_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() - timedelta(days=1)
        except Exception:
            cutoff_date = None

        # Determine latest datetime allowed for scheduling
        latest_allowed = window_end
        if cutoff_date:
            cutoff_dt = datetime.combine(cutoff_date, time(23, 59))
            if cutoff_dt < latest_allowed:
                latest_allowed = cutoff_dt

        # Iterate phases in order
        for phase in assignment.get('phases', []):
            phase_title = phase.get('title', 'Phase')
            duration = int(phase.get('duration_minutes', 0))
            intensity = phase.get('intensity', 'Medium')
            if duration <= 0:
                continue

            # Break into chunks according to intensity
            chunk_size = chunk_size_for_intensity(intensity)
            remaining = duration
            chunks: List[int] = []
            while remaining > 0:
                this_chunk = min(chunk_size, remaining)
                chunks.append(this_chunk)
                remaining -= this_chunk

            # Schedule each chunk into earliest free slot that fits and ends before latest_allowed
            for minutes in chunks:
                placed = False
                for i, slot in enumerate(free_slots):
                    slot_start = slot['start']
                    slot_end = slot['end']
                    slot_duration_minutes = int((slot_end - slot_start).total_seconds() // 60)
                    if slot_duration_minutes >= minutes and slot_end <= latest_allowed:
                        # schedule at slot_start
                        ev_start = slot_start
                        ev_end = ev_start + timedelta(minutes=minutes)
                        new_event = CalendarEvent(
                            id=f"assign-{uuid.uuid4()}",
                            title=f"{title} - {phase_title}",
                            start=ev_start,
                            end=ev_end,
                            color="#f97316",
                            extendedProps={"assignment": title, "phase": phase_title}
                        )
                        scheduled_events.append(new_event)

                        # update free slot
                        free_slots[i]['start'] = ev_end
                        if (free_slots[i]['end'] - free_slots[i]['start']).total_seconds() < 60:
                            free_slots.pop(i)
                        placed = True
                        break

                if not placed:
                    print(f"Could not place chunk ({minutes}m) for {title} - {phase_title}")
                    # continue to next chunk (it will remain unscheduled)

    return scheduled_events