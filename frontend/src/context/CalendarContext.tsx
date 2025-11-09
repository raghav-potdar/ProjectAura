import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import type { CalendarEvent } from '../services/api.service';

type CalendarContextValue = {
  events: CalendarEvent[];
  addEvents: (incoming: CalendarEvent[]) => void;
  replaceEvents: (next: CalendarEvent[]) => void;
  clearEvents: () => void;
};

const CalendarContext = createContext<CalendarContextValue | undefined>(undefined);

export function CalendarProvider({ children }: { children: React.ReactNode }) {
  const [events, setEvents] = useState<CalendarEvent[]>([]);

  const addEvents = useCallback((incoming: CalendarEvent[]) => {
    if (!incoming.length) return;
    setEvents((previous) => {
      const map = new Map<string, CalendarEvent>();
      const enrich = (event: CalendarEvent, index: number) => {
        if (event.id) return event;
        const safeId = `${event.title ?? 'event'}-${event.start ?? event.end ?? index}-${index}`;
        return { ...event, id: safeId };
      };
      [...previous, ...incoming.map(enrich)].forEach((event, index) => {
        const key = event.id ?? `${event.title}-${event.start ?? ''}-${event.end ?? ''}-${index}`;
        if (!map.has(key)) {
          map.set(key, event);
        }
      });
      return Array.from(map.values());
    });
  }, []);

  const replaceEvents = useCallback((next: CalendarEvent[]) => {
    setEvents(
      next.map((event, index) => {
        if (event.id) return event;
        const safeId = `${event.title ?? 'event'}-${event.start ?? event.end ?? index}-${index}`;
        return { ...event, id: safeId };
      })
    );
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  const value = useMemo(
    () => ({ events, addEvents, replaceEvents, clearEvents }),
    [events, addEvents, replaceEvents, clearEvents]
  );

  return <CalendarContext.Provider value={value}>{children}</CalendarContext.Provider>;
}

export function useCalendar() {
  const context = useContext(CalendarContext);
  if (!context) {
    throw new Error('useCalendar must be used inside a CalendarProvider');
  }
  return context;
}
