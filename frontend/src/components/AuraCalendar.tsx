import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';

export default function AuraCalendar() {
  // Hard-code a couple of demo events so you see something
  const demoEvents = [
    {
      title: 'Sleep',
      start: '2025-11-08T00:00:00',
      end: '2025-11-08T08:00:00',
      display: 'background',
      color: '#e5e5e5',
    },
    {
      title: 'CS 101',
      daysOfWeek: [1, 3], // Mon, Wed
      startTime: '10:00',
      endTime: '11:30',
      color: '#3b82f6',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay',
        }}
        events={demoEvents}
        height="auto"
        slotMinTime="06:00:00"
        slotMaxTime="23:00:00"
      />
    </div>
  );
}