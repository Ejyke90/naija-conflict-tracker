/**
 * Color schemes and utilities for conflict map visualization
 */

export const EVENT_COLORS: Record<string, string> = {
  'Armed Conflict': '#DC2626', // Red
  'Communal Clash': '#EA580C', // Orange
  'Banditry': '#CA8A04', // Amber
  'Kidnapping': '#7C3AED', // Purple
  'Cult Clash': '#DB2777', // Pink
  'Other': '#6B7280', // Gray
  'Herder-Farmer': '#F97316', // Deep Orange
  'Terrorism': '#991B1B', // Dark Red
  'Mob Action': '#92400E', // Brown
  'Political Violence': '#6D28D9', // Deep Purple
};

export const getEventColor = (eventType: string): string => {
  return EVENT_COLORS[eventType] || EVENT_COLORS['Other'];
};

export const getMarkerSize = (fatalities: number): number => {
  if (fatalities === 0) return 8;
  if (fatalities < 5) return 12;
  if (fatalities < 10) return 16;
  if (fatalities < 20) return 20;
  return 24;
};

export const getRiskColor = (riskLevel: string): string => {
  const riskColors: Record<string, string> = {
    'low': '#10B981', // Green
    'medium': '#F59E0B', // Amber
    'high': '#EF4444', // Red
    'critical': '#7C2D12', // Dark Red
  };
  return riskColors[riskLevel.toLowerCase()] || riskColors['medium'];
};

export const getFatalityCategory = (fatalities: number): string => {
  if (fatalities === 0) return 'No fatalities';
  if (fatalities < 5) return '1-4 fatalities';
  if (fatalities < 10) return '5-9 fatalities';
  if (fatalities < 20) return '10-19 fatalities';
  return '20+ fatalities';
};

export const LEGEND_ITEMS = [
  { label: 'Armed Conflict', color: EVENT_COLORS['Armed Conflict'] },
  { label: 'Communal Clash', color: EVENT_COLORS['Communal Clash'] },
  { label: 'Banditry', color: EVENT_COLORS['Banditry'] },
  { label: 'Kidnapping', color: EVENT_COLORS['Kidnapping'] },
  { label: 'Cult Clash', color: EVENT_COLORS['Cult Clash'] },
  { label: 'Other', color: EVENT_COLORS['Other'] },
];

export const SIZE_LEGEND = [
  { size: 8, label: 'No fatalities' },
  { size: 12, label: '1-4 fatalities' },
  { size: 16, label: '5-9 fatalities' },
  { size: 20, label: '10-19 fatalities' },
  { size: 24, label: '20+ fatalities' },
];
