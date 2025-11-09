from typing import List
from datetime import time
from ..models import CalendarEvent

def get_base_events() -> List[CalendarEvent]:
    """
    Returns an empty list as base events since we're handling everything dynamically
    """
    return []