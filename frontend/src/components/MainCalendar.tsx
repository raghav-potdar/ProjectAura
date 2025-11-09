import React, { useEffect, useRef, useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import apiService, { CalendarEvent } from '../services/api.service';

type Props = {
  events?: CalendarEvent[];
  selectedDate?: Date;
};

export default function MainCalendar({ events: propEvents = [], selectedDate }: Props) {
  const [baseEvents, setBaseEvents] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const calendarRef = useRef<FullCalendar | null>(null);

  useEffect(() => {
    const fetchBaseEvents = async () => {
      try {
        const events = await apiService.getBaseEvents();
        setBaseEvents(events);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch base events');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBaseEvents();
  }, []);

  // Combine base events with prop events
  const allEvents = [...baseEvents, ...propEvents];

  useEffect(() => {
    if (selectedDate && calendarRef.current) {
      const api = calendarRef.current.getApi();
      api.gotoDate(selectedDate);
    }
  }, [selectedDate]);

  return (
    <div className="flex-1 bg-white rounded-lg shadow-sm p-6">
      <FullCalendar
        ref={calendarRef}
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        initialDate={selectedDate ?? new Date()}
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'timeGridWeek,timeGridDay',
        }}
        events={allEvents}
        editable={false}
        droppable={false}
        selectable={false}
        selectMirror={true}
        dayMaxEvents={true}
        weekends={false}
        height="auto"
        slotMinTime="08:00:00"
        slotMaxTime="21:00:00"
  allDaySlot={true}
        slotDuration="00:30:00"
        slotLabelInterval="01:00"
        slotLabelFormat={{
          hour: 'numeric',
          minute: '2-digit',
          meridiem: 'short'
        }}
        expandRows={true}
        stickyHeaderDates={true}
        nowIndicator={true}
        eventContent={(eventInfo) => {
          const isAllDay = eventInfo.event.allDay;
          const startLabel = eventInfo.event.start
            ? eventInfo.event.start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
            : null;
          const endLabel = eventInfo.event.end
            ? eventInfo.event.end.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
            : null;
          return (
            <div className="p-1 text-sm">
              <div className="font-semibold">{eventInfo.event.title}</div>
              <div className="text-xs opacity-75">
                {isAllDay ? 'All day' : `${startLabel ?? ''}${endLabel ? ` – ${endLabel}` : ''}`}
              </div>
            </div>
          )
        }}
      />
    </div>
  );
}