/**
 * API Service for Conflict Index
 * Handles all API calls related to conflict index data
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ConflictIndexData {
  rank: number;
  state: string;
  deadliness: number;
  civilianDanger: number;
  geographicDiffusion: number;
  armedGroups: number;
  totalEvents: number;
  fatalities: number;
  compositeScore: number;
  severity: 'extreme' | 'high' | 'turbulent' | 'moderate';
  trend: 'up' | 'down' | 'stable';
}

export interface ConflictIndexResponse {
  states: ConflictIndexData[];
  totalStates: number;
  timeRange: string;
  generatedAt: string;
}

export interface ConflictIndexSummary {
  totalEvents: number;
  fatalities: number;
  statesAffected: number;
  armedGroups: number;
  timeRange: string;
}

/**
 * Fetch conflict index data for all states
 */
export async function fetchConflictIndex(
  timeRange: '6months' | '12months' | '24months' | 'all' = '12months'
): Promise<ConflictIndexResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/conflict-index?time_range=${timeRange}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching conflict index:', error);
    throw error;
  }
}

/**
 * Fetch conflict index summary statistics
 */
export async function fetchConflictIndexSummary(): Promise<ConflictIndexSummary> {
  try {
    const response = await fetch(`${API_URL}/api/v1/conflict-index/summary`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching conflict index summary:', error);
    throw error;
  }
}

/**
 * Export conflict index data as CSV
 */
export function exportConflictIndexToCSV(data: ConflictIndexData[]): void {
  const headers = [
    'Rank',
    'State',
    'Deadliness',
    'Civilian Danger',
    'Geographic Diffusion',
    'Armed Groups',
    'Total Events',
    'Fatalities',
    'Composite Score',
    'Severity',
    'Trend'
  ];

  const rows = data.map(d => [
    d.rank,
    d.state,
    d.deadliness,
    d.civilianDanger,
    d.geographicDiffusion,
    d.armedGroups,
    d.totalEvents,
    d.fatalities,
    d.compositeScore,
    d.severity,
    d.trend
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `nigeria-conflict-index-${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
  window.URL.revokeObjectURL(url);
}
