from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import List, Literal, Optional, Dict, Any, Union
import uuid

# --- Agent 1 & 2 Models ---

# This is the "contract" for what Agent 1 (Gemini) MUST return.
class TaskProposal(BaseModel):
    title: str
    duration_minutes: int = Field(..., gt=0) # Must be greater than 0
    deadline: date
    difficulty: Literal['Low', 'Medium', 'High'] # Validates the string

# This is the "clean" task that Agent 2 passes to Agent 3.
class VerifiedTask(BaseModel):
    title: str
    duration_minutes: int
    deadline: date
    difficulty: Literal['Low', 'Medium', 'High']

# --- Calendar Event Models ---

# This is the "union" model that FullCalendar understands.
# It can be a recurring event (with startTime) OR a concrete event (with start/end).
class CalendarEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"event-{uuid.uuid4()}")
    title: str
    
    # --- For concrete, scheduled events ---
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    
    # --- For recurring, base-layer events ---
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    daysOfWeek: Optional[List[int]] = None # [0=Sun, 1=Mon, ...]
    
    # --- Styling ---
    display: Optional[str] = None # e.g., 'background'
    color: str = "#3b82f6"
    extendedProps: Dict[str, Any] = {}