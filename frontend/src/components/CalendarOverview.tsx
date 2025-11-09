import React, { useEffect, useMemo, useState } from 'react';

type CalendarOverviewProps = {
  selectedDate: Date;
  onSelectDate: (date: Date) => void;
};

export default function CalendarOverview({ selectedDate, onSelectDate }: CalendarOverviewProps) {
  const [visibleMonth, setVisibleMonth] = useState(() => new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1));

  useEffect(() => {
    setVisibleMonth(new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1));
  }, [selectedDate]);

  const { daysInMonth, blanks } = useMemo(() => {
    const firstDay = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth(), 1).getDay();
    const totalDays = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() + 1, 0).getDate();
    return {
      daysInMonth: Array.from({ length: totalDays }, (_, i) => i + 1),
      blanks: Array.from({ length: firstDay }, (_, i) => i),
    };
  }, [visibleMonth]);

  const monthLabel = visibleMonth.toLocaleString('default', { month: 'long', year: 'numeric' });
  const today = useMemo(() => new Date(), []);

  const isSameDay = (dateA: Date, dateB: Date) =>
    dateA.getFullYear() === dateB.getFullYear() &&
    dateA.getMonth() === dateB.getMonth() &&
    dateA.getDate() === dateB.getDate();

  const handleSelect = (day: number) => {
    const nextDate = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth(), day);
    onSelectDate(nextDate);
  };

  const handlePrevMonth = () => {
    setVisibleMonth(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setVisibleMonth(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">{monthLabel}</h2>
        <div className="flex space-x-2">
          <button className="p-1 hover:bg-gray-100 rounded" onClick={handlePrevMonth} aria-label="Previous month">
            <i className="fas fa-chevron-left text-gray-600" />
          </button>
          <button className="p-1 hover:bg-gray-100 rounded" onClick={handleNextMonth} aria-label="Next month">
            <i className="fas fa-chevron-right text-gray-600" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1 text-center mb-2">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="text-xs text-gray-500 font-medium uppercase tracking-wide">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {blanks.map(i => (
          <div key={`blank-${i}`} className="aspect-square" />
        ))}
        {daysInMonth.map(day => {
          const dayDate = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth(), day);
          const selected = isSameDay(dayDate, selectedDate);
          const isToday = isSameDay(dayDate, today);
          return (
            <button
              key={day}
              type="button"
              onClick={() => handleSelect(day)}
              className={`aspect-square flex items-center justify-center text-sm rounded-full transition
                ${selected ? 'bg-blue-600 text-white shadow-sm' : isToday ? 'border border-blue-200 text-blue-600' : 'hover:bg-gray-100 text-gray-700'}`}
            >
              {day}
            </button>
          );
        })}
      </div>
    </div>
  );
}