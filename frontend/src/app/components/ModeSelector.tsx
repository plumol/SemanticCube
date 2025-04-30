// frontend/src/app/components/ModeSelector.tsx
'use client';

import React from 'react';

interface ModeSelectorProps {
  mode: 'rollup' | 'filtering';
  onModeChange: (mode: 'rollup' | 'filtering') => void;
}

export default function ModeSelector({ mode, onModeChange }: ModeSelectorProps) {
  return (
    <select
      value={mode}
      onChange={(e) => onModeChange(e.target.value as 'rollup' | 'filtering')}
      className="p-3 border rounded-md text-gray-900 bg-white"
    >
      <option value="rollup">Roll-up Mode</option>
      <option value="filtering">Filtering Mode</option>
    </select>
  );
}