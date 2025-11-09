import React from 'react';
import { Link } from 'react-router-dom';

export default function Categories() {
  const categories = [
    { id: 'pd', name: 'Product Design', count: 5, color: 'blue' },
    { id: 'se', name: 'Software Engineering', count: 3, color: 'purple' },
    { id: 'ur', name: 'User Research', count: 1, color: 'green' },
    { id: 'mk', name: 'Marketing', count: 0, color: 'pink' },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold mb-4">Categories</h2>
      <div className="space-y-2">
        {categories.map((category) => (
          <div
            key={category.id}
            className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg cursor-pointer"
          >
            <div className="flex items-center space-x-3">
              <div className={`w-2 h-2 rounded-full bg-${category.color}-500`} />
              <span className="text-sm text-gray-700">{category.name}</span>
            </div>
            <span className="text-xs text-gray-500">{category.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}