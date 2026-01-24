import React, { useState } from 'react';
import { X, Calendar, MapPin, Filter, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { useMapFilters, type DatePreset } from '../../hooks/useMapFilters';

const NIGERIAN_STATES = [
  'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue',
  'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'Gombe',
  'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara',
  'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau',
  'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara', 'FCT',
];

const EVENT_TYPES = [
  'Armed Conflict',
  'Communal Clash',
  'Banditry',
  'Kidnapping',
  'Cult Clash',
  'Herder-Farmer',
  'Terrorism',
  'Political Violence',
  'Other',
];

const DATE_PRESETS: { label: string; value: DatePreset }[] = [
  { label: 'Last 7 Days', value: 'last7days' },
  { label: 'Last 30 Days', value: 'last30days' },
  { label: 'Last Quarter', value: 'lastQuarter' },
  { label: 'Last Year', value: 'lastYear' },
  { label: '2024', value: '2024' },
  { label: '2023', value: '2023' },
  { label: 'All Time', value: 'allTime' },
];

interface MapFiltersProps {
  onClose?: () => void;
  className?: string;
}

/**
 * Sidebar component for map filtering controls
 */
export const MapFilters: React.FC<MapFiltersProps> = ({ onClose, className = '' }) => {
  const {
    filters,
    setDatePreset,
    toggleEventType,
    toggleState,
    setFatalityRange,
    toggleQuickFilter,
    clearFilters,
    activeFilterCount,
  } = useMapFilters();

  const [customDateRange, setCustomDateRange] = useState({
    start: filters.dateRange?.start ? format(filters.dateRange.start, 'yyyy-MM-dd') : '',
    end: filters.dateRange?.end ? format(filters.dateRange.end, 'yyyy-MM-dd') : '',
  });

  const [fatalityRange, setLocalFatalityRange] = useState({
    min: filters.minFatalities?.toString() || '',
    max: filters.maxFatalities?.toString() || '',
  });

  const applyFatalityRange = () => {
    const min = fatalityRange.min ? parseInt(fatalityRange.min) : undefined;
    const max = fatalityRange.max ? parseInt(fatalityRange.max) : undefined;
    setFatalityRange(min, max);
  };

  return (
    <div className={`bg-white shadow-xl rounded-lg overflow-hidden flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Filter className="text-white" size={20} />
          <h3 className="text-white font-semibold text-lg">Filters</h3>
          {activeFilterCount > 0 && (
            <span className="bg-white text-blue-700 text-xs font-bold px-2 py-0.5 rounded-full">
              {activeFilterCount}
            </span>
          )}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 transition-colors"
            aria-label="Close filters"
          >
            <X size={20} />
          </button>
        )}
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
        {/* Date Range Filter */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <Calendar size={18} className="text-gray-600" />
            <h4 className="font-semibold text-gray-900">Date Range</h4>
          </div>
          
          {/* Preset Buttons */}
          <div className="grid grid-cols-2 gap-2 mb-3">
            {DATE_PRESETS.map((preset) => (
              <button
                key={preset.value}
                onClick={() => setDatePreset(preset.value)}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-blue-50 hover:border-blue-400 transition-colors"
              >
                {preset.label}
              </button>
            ))}
          </div>

          {/* Custom Date Inputs */}
          <div className="space-y-2">
            <input
              type="date"
              value={customDateRange.start}
              onChange={(e) => setCustomDateRange({ ...customDateRange, start: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Start date"
            />
            <input
              type="date"
              value={customDateRange.end}
              onChange={(e) => setCustomDateRange({ ...customDateRange, end: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="End date"
            />
          </div>
        </div>

        {/* Event Types */}
        <div>
          <h4 className="font-semibold text-gray-900 mb-3">Event Types</h4>
          <div className="space-y-2">
            {EVENT_TYPES.map((eventType) => (
              <label key={eventType} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.eventTypes?.includes(eventType) || false}
                  onChange={() => toggleEventType(eventType)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{eventType}</span>
              </label>
            ))}
          </div>
        </div>

        {/* States */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <MapPin size={18} className="text-gray-600" />
            <h4 className="font-semibold text-gray-900">States</h4>
          </div>
          <div className="max-h-48 overflow-y-auto space-y-2 border border-gray-200 rounded p-2">
            {NIGERIAN_STATES.map((state) => (
              <label key={state} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.states?.includes(state) || false}
                  onChange={() => toggleState(state)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{state}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Fatality Range */}
        <div>
          <h4 className="font-semibold text-gray-900 mb-3">Fatality Range</h4>
          <div className="flex space-x-2 items-center">
            <input
              type="number"
              min="0"
              placeholder="Min"
              value={fatalityRange.min}
              onChange={(e) => setLocalFatalityRange({ ...fatalityRange, min: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <span className="text-gray-500">to</span>
            <input
              type="number"
              min="0"
              placeholder="Max"
              value={fatalityRange.max}
              onChange={(e) => setLocalFatalityRange({ ...fatalityRange, max: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={applyFatalityRange}
              className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
            >
              Apply
            </button>
          </div>
        </div>

        {/* Quick Filters */}
        <div>
          <h4 className="font-semibold text-gray-900 mb-3">Quick Filters</h4>
          <div className="space-y-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.showHighFatality || false}
                onChange={() => toggleQuickFilter('showHighFatality')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">High Fatality (10+)</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.showMassDisplacement || false}
                onChange={() => toggleQuickFilter('showMassDisplacement')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Mass Displacement (100+)</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.showRecent || false}
                onChange={() => toggleQuickFilter('showRecent')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Recent (Last 30 Days)</span>
            </label>
          </div>
        </div>
      </div>

      {/* Footer with Clear Filters Button */}
      <div className="border-t px-4 py-3 bg-gray-50">
        <button
          onClick={clearFilters}
          disabled={activeFilterCount === 0}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          <Trash2 size={16} />
          <span>Clear All Filters</span>
        </button>
      </div>
    </div>
  );
};
