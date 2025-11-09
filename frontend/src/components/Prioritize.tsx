import React from 'react';

export default function Prioritize() {
  const methods = [
    { id: 'em', name: 'Eisenhower Matrix', icon: 'table' },
    { id: 'ef', name: 'Eat The Frog First', icon: 'frog' },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold mb-4">Prioritize</h2>
      <div className="space-y-2">
        {methods.map((method) => (
          <button
            key={method.id}
            className="flex items-center space-x-3 w-full p-2 text-left hover:bg-gray-50 rounded-lg"
          >
            <i className={`fas fa-${method.icon} text-gray-400`} />
            <span className="text-sm text-gray-700">{method.name}</span>
            <i className="fas fa-chevron-right ml-auto text-gray-300" />
          </button>
        ))}
      </div>
    </div>
  );
}