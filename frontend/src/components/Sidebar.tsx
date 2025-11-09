import React, { ReactNode } from 'react';
import CalendarOverview from './CalendarOverview';

interface SidebarProps {
  children?: ReactNode;
  selectedDate: Date;
  onSelectDate: (date: Date) => void;
}

export default function Sidebar({ children, selectedDate, onSelectDate }: SidebarProps) {
  return (
    <aside className="w-80 space-y-6">
      {/* Auth Section */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <h3 className="text-lg font-semibold mb-3">Account</h3>
        <p className="text-sm text-gray-600 mb-4">Register or login to save and sync your schedules.</p>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            Register
          </button>
          <button className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
            Login
          </button>
        </div>
      </div>

      {/* File Upload Section */}
      {children}

      <CalendarOverview selectedDate={selectedDate} onSelectDate={onSelectDate} />
    </aside>
  );
}