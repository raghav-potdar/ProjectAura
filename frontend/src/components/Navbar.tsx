import React from 'react';

interface NavItemProps {
  icon: string;
  label: string;
  active?: boolean;
}

function NavItem({ icon, label, active = false }: NavItemProps) {
  return (
    <button
      className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition ${
        active ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'
      }`}
    >
      <i className={`fas fa-${icon} w-5 h-5`} aria-hidden="true" />
      <span className="font-medium">{label}</span>
    </button>
  );
}

export default function Navbar() {
  return (
    <nav className="bg-white rounded-t-lg shadow-sm px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-2xl font-extrabold tracking-wide bg-gradient-to-r from-blue-600 via-purple-500 to-pink-500 bg-clip-text text-transparent">
          AURA
        </span>
        <i className="fas fa-graduation-cap text-xl text-blue-600" aria-hidden />
      </div>

      <div className="flex items-center space-x-8">
        <NavItem icon="th-large" label="Dashboard" active />
        <NavItem icon="tasks" label="Plan" />
        <NavItem icon="calendar" label="Calendar" />
        <NavItem icon="chart-bar" label="Analytics" />
      </div>

      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-500"></div>
    </nav>
  );
}