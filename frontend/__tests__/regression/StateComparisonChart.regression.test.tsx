import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import StateComparisonChart from '../../components/charts/StateComparisonChart';

// Mock fetch API
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock console methods to avoid noise in tests
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

beforeEach(() => {
  console.log = jest.fn();
  console.error = jest.fn();
  mockFetch.mockClear();
});

afterEach(() => {
  console.log = originalConsoleLog;
  console.error = originalConsoleError;
});

describe('StateComparisonChart Regression Tests', () => {
  const mockStateData = {
    data: [
      { state: 'Borno', incidents: 40, fatalities: 350 },
      { state: 'Zamfara', incidents: 126, fatalities: 246 },
      { state: 'Kaduna', incidents: 94, fatalities: 275 },
      { state: 'Plateau', incidents: 197, fatalities: 805 },
      { state: 'Niger', incidents: 99, fatalities: 204 },
      { state: 'Benue', incidents: 88, fatalities: 531 },
      { state: 'Katsina', incidents: 70, fatalities: 185 },
      { state: 'Sokoto', incidents: 79, fatalities: 162 },
    ],
    status: 'ok',
    cached: false
  };

  const mockTrendData = {
    comparison: {
      'Borno': {
        months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        incidents: [5, 8, 6, 7, 9, 5],
        fatalities: [45, 62, 58, 51, 67, 67],
        total: 40,
        avgPerMonth: 6.7
      },
      'Zamfara': {
        months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        incidents: [15, 22, 18, 20, 25, 26],
        fatalities: [35, 42, 38, 41, 45, 45],
        total: 126,
        avgPerMonth: 21.0
      },
      'Kaduna': {
        months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        incidents: [12, 16, 15, 18, 17, 16],
        fatalities: [40, 48, 45, 50, 46, 46],
        total: 94,
        avgPerMonth: 15.7
      },
      'Plateau': {
        months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        incidents: [25, 35, 30, 32, 40, 35],
        fatalities: [120, 150, 135, 140, 160, 160],
        total: 197,
        avgPerMonth: 32.8
      },
      'Niger': {
        months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        incidents: [15, 18, 16, 17, 17, 16],
        fatalities: [30, 35, 32, 34, 34, 39],
        total: 99,
        avgPerMonth: 16.5
      }
    },
    timeRange: '12 months',
    generatedAt: new Date().toISOString()
  };

  test('CRITICAL: should display exactly 5 states in smart selection mode', async () => {
    // Mock API responses
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockStateData)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTrendData)
      });

    render(
      <StateComparisonChart 
        defaultToSmartSelection={true} 
        maxStates={5}
        monthsBack={12}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText('Loading state comparison...')).not.toBeInTheDocument();
    });

    // Critical: Should show exactly 5 state cards
    const stateCards = screen.getAllByTestId(/state-card/i);
    expect(stateCards).toHaveLength(5);

    // Verify the states are the expected ones (3 hot, 1 medium, 1 safe)
    const expectedStates = ['Plateau', 'Borno', 'Benue', 'Kaduna', 'Zamfara']; // Based on fatalities
    expectedStates.forEach(state => {
      expect(screen.getByText(state)).toBeInTheDocument();
    });
  });

  test('CRITICAL: should handle API response structure changes gracefully', async () => {
    // Test different response structures that could occur
    const responseVariations = [
      // Standard structure with data field
      { data: mockStateData.data, status: 'ok' },
      // Direct array (old structure)
      mockStateData.data,
      // Different field name
      { results: mockStateData.data, status: 'ok' },
      // Nested structure
      { response: { data: mockStateData.data }, status: 'ok' }
    ];

    for (const response of responseVariations) {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(response)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockTrendData)
        });

      render(
        <StateComparisonChart 
          defaultToSmartSelection={true} 
          maxStates={5}
          monthsBack={12}
        />
      );

      await waitFor(() => {
        expect(screen.queryByText('Loading state comparison...')).not.toBeInTheDocument();
      });

      // Should not show error state
      expect(screen.queryByText(/No data available/i)).not.toBeInTheDocument();
      
      // Cleanup for next iteration
      render(<div />);
    }
  });

  test('CRITICAL: should fall back to default states when API fails', async () => {
    // Mock API failure
    mockFetch.mockRejectedValue(new Error('Network error'));

    const defaultStates = ['Borno', 'Zamfara', 'Kaduna', 'Plateau', 'Niger'];
    
    render(
      <StateComparisonChart 
        states={defaultStates}
        defaultToSmartSelection={true}
        maxStates={5}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading state comparison...')).not.toBeInTheDocument();
    });

    // Should fall back to default states
    defaultStates.forEach(state => {
      expect(screen.getByText(state)).toBeInTheDocument();
    });
  });

  test('should maintain exactly 5 states even with API errors', async () => {
    // Mock successful state API but failed trend API
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockStateData)
      })
      .mockRejectedValueOnce(new Error('Trend API failed'));

    render(
      <StateComparisonChart 
        defaultToSmartSelection={true} 
        maxStates={5}
        monthsBack={12}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading state comparison...')).not.toBeInTheDocument();
    });

    // Should still show 5 states even if trend data fails
    const stateCards = screen.getAllByTestId(/state-card/i);
    expect(stateCards).toHaveLength(5);
  });

  test('should handle empty API response gracefully', async () => {
    // Mock empty response
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: [], status: 'ok' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTrendData)
      });

    const defaultStates = ['Borno', 'Zamfara', 'Kaduna', 'Plateau', 'Niger'];
    
    render(
      <StateComparisonChart 
        states={defaultStates}
        defaultToSmartSelection={true}
        maxStates={5}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading state comparison...')).not.toBeInTheDocument();
    });

    // Should fall back to default states when API returns empty data
    defaultStates.forEach(state => {
      expect(screen.getByText(state)).toBeInTheDocument();
    });
  });

  test('should respect maxStates parameter', async () => {
    // Mock API responses
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockStateData)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTrendData)
      });

    render(
      <StateComparisonChart 
        defaultToSmartSelection={true} 
        maxStates={3} // Different max states
        monthsBack={12}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading state comparison...')).not.toBeInTheDocument();
    });

    // Should respect maxStates parameter
    const stateCards = screen.getAllByTestId(/state-card/i);
    expect(stateCards).toHaveLength(3);
  });

  test('should handle user state selection correctly', async () => {
    // Mock API responses
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockStateData)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTrendData)
      });

    render(
      <StateComparisonChart 
        defaultToSmartSelection={false} // Don't use smart selection
        states={['Borno', 'Zamfara', 'Kaduna']} // Only 3 states initially
        maxStates={5}
        allowUserSelection={true}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading state comparison...')).not.toBeInTheDocument();
    });

    // Should show initial 3 states
    expect(screen.getByText('Borno')).toBeInTheDocument();
    expect(screen.getByText('Zamfara')).toBeInTheDocument();
    expect(screen.getByText('Kaduna')).toBeInTheDocument();

    // Open controls
    const controlsButton = screen.getByText('Select States & Period');
    fireEvent.click(controlsButton);

    // Add more states
    const plateauButton = screen.getByText('Plateau');
    fireEvent.click(plateauButton);

    const nigerButton = screen.getByText('Niger');
    fireEvent.click(nigerButton);

    // Should now show 5 states
    expect(screen.getByText('Plateau')).toBeInTheDocument();
    expect(screen.getByText('Niger')).toBeInTheDocument();
  });

  test('should not exceed maxStates when user selects states', async () => {
    // Mock API responses
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockStateData)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTrendData)
      });

    render(
      <StateComparisonChart 
        defaultToSmartSelection={false}
        states={['Borno', 'Zamfara']}
        maxStates={3}
        allowUserSelection={true}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading state comparison...')).not.toBeInTheDocument();
    });

    // Open controls
    const controlsButton = screen.getByText('Select States & Period');
    fireEvent.click(controlsButton);

    // Try to add more states than maxStates allows
    const kadunaButton = screen.getByText('Kaduna');
    fireEvent.click(kadunaButton);

    const plateauButton = screen.getByText('Plateau');
    fireEvent.click(plateauButton);

    // Should only have 3 states (maxStates)
    const stateCards = screen.getAllByTestId(/state-card/i);
    expect(stateCards).toHaveLength(3);
  });

  test('should handle API response with missing fields gracefully', async () => {
    // Mock response with missing fields
    const incompleteData = {
      data: [
        { state: 'Borno', incidents: 40 }, // Missing fatalities
        { state: 'Zamfara', fatalities: 246 }, // Missing incidents
        { state: 'Kaduna' }, // Missing both
        { state: 'Plateau', incidents: 197, fatalities: 805 },
        { state: 'Niger', incidents: 99, fatalities: 204 },
      ],
      status: 'ok'
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(incompleteData)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTrendData)
      });

    render(
      <StateComparisonChart 
        defaultToSmartSelection={true} 
        maxStates={5}
        monthsBack={12}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText('Loading state comparison...')).not.toBeInTheDocument();
    });

    // Should handle missing fields gracefully and still show 5 states
    const stateCards = screen.getAllByTestId(/state-card/i);
    expect(stateCards).toHaveLength(5);
  });
});
