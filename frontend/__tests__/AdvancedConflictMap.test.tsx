/**
 * Test file for AdvancedConflictMap Heatmap functionality
 * Run with: npm test frontend/__tests__/AdvancedConflictMap.test.tsx
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdvancedConflictMap from '@/components/mapping/AdvancedConflictMap';

// Mock Leaflet
jest.mock('leaflet', () => ({
  Icon: {
    Default: {
      prototype: {},
      mergeOptions: jest.fn(),
    },
  },
  heatLayer: jest.fn(() => ({
    addTo: jest.fn(),
    removeFrom: jest.fn(),
  })),
}));

// Mock react-leaflet
jest.mock('react-leaflet', () => ({
  MapContainer: ({ children, ...props }: any) => (
    <div data-testid="map-container" {...props}>
      {children}
    </div>
  ),
  TileLayer: () => <div data-testid="tile-layer" />,
  Marker: ({ children }: any) => (
    <div data-testid="marker">{children}</div>
  ),
  Popup: ({ children }: any) => <div data-testid="popup">{children}</div>,
}));

// Mock fetch
global.fetch = jest.fn();

describe('AdvancedConflictMap - Heatmap Functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset fetch mock
    (global.fetch as jest.Mock).mockReset();
  });

  describe('Component Rendering', () => {
    it('should render the map component', () => {
      render(<AdvancedConflictMap />);
      expect(screen.getByTestId('map-container')).toBeInTheDocument();
    });

    it('should render heatmap button', () => {
      render(<AdvancedConflictMap />);
      expect(screen.getByText(/🔥 Heatmap/i)).toBeInTheDocument();
    });

    it('should render export button', () => {
      render(<AdvancedConflictMap />);
      expect(screen.getByText(/⬇ Export/i)).toBeInTheDocument();
    });

    it('should render spatial analysis button', () => {
      render(<AdvancedConflictMap />);
      expect(screen.getByText(/Spatial Analysis/i)).toBeInTheDocument();
    });
  });

  describe('Heatmap Loading', () => {
    it('should load heatmap data on button click', async () => {
      const mockData = {
        points: [
          [9.0765, 8.6753, 5.0],
          [9.0820, 8.6800, 7.5],
        ],
        bounds: { north: 13.8, south: 2.7, east: 14.68, west: 2.67 },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      render(<AdvancedConflictMap />);

      const heatmapButton = screen.getByText(/🔥 Heatmap/i);
      fireEvent.click(heatmapButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/conflicts/heatmap/data?days_back=30'
        );
      });
    });

    it('should show loading spinner while fetching', async () => {
      (global.fetch as jest.Mock).mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                ok: true,
                json: async () => ({ points: [], bounds: {} }),
              });
            }, 100);
          })
      );

      render(<AdvancedConflictMap />);

      const heatmapButton = screen.getByText(/🔥 Heatmap/i);
      fireEvent.click(heatmapButton);

      await waitFor(() => {
        expect(screen.getByText(/Loading heatmap/i)).toBeInTheDocument();
      });
    });

    it('should display error message on API failure', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      render(<AdvancedConflictMap />);

      const heatmapButton = screen.getByText(/🔥 Heatmap/i);
      fireEvent.click(heatmapButton);

      await waitFor(() => {
        expect(
          screen.getByText(/Failed to load heatmap data/)
        ).toBeInTheDocument();
      });
    });

    it('should show legend when heatmap is active', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          points: [[9.0820, 8.6753, 5.0]],
          bounds: {},
        }),
      });

      render(<AdvancedConflictMap />);

      const heatmapButton = screen.getByText(/🔥 Heatmap/i);
      fireEvent.click(heatmapButton);

      await waitFor(() => {
        expect(screen.getByText(/Heatmap Legend/i)).toBeInTheDocument();
        expect(screen.getByText(/Low Intensity/i)).toBeInTheDocument();
        expect(screen.getByText(/High Intensity/i)).toBeInTheDocument();
      });
    });
  });

  describe('Heatmap Toggle', () => {
    it('should toggle heatmap on/off', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({
          points: [[9.0820, 8.6753, 5.0]],
          bounds: {},
        }),
      });

      const { rerender } = render(<AdvancedConflictMap />);

      const heatmapButton = screen.getByText(/🔥 Heatmap/i);

      // Turn on
      fireEvent.click(heatmapButton);
      await waitFor(() => {
        expect(screen.getByText(/Heatmap layer active/i)).toBeInTheDocument();
      });

      // Turn off
      fireEvent.click(heatmapButton);
      await waitFor(() => {
        expect(
          screen.queryByText(/Heatmap layer active/i)
        ).not.toBeInTheDocument();
      });
    });

    it('should disable button while loading', async () => {
      (global.fetch as jest.Mock).mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                ok: true,
                json: async () => ({ points: [], bounds: {} }),
              });
            }, 100);
          })
      );

      render(<AdvancedConflictMap />);

      const heatmapButton = screen.getByText(/🔥 Heatmap/i) as HTMLButtonElement;
      fireEvent.click(heatmapButton);

      expect(heatmapButton).toBeDisabled();
    });
  });

  describe('Export Functionality', () => {
    it('should export data as GeoJSON', async () => {
      const mockData = {
        points: [
          [9.0765, 8.6753, 5.0],
          [9.0820, 8.6800, 7.5],
        ],
        bounds: {},
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      // Mock URL.createObjectURL and document.createElement
      const mockCreateElement = document.createElement;
      const mockClick = jest.fn();
      document.createElement = jest.fn((tag) => {
        if (tag === 'a') {
          const el = mockCreateElement.call(document, tag);
          el.click = mockClick;
          return el;
        }
        return mockCreateElement.call(document, tag);
      });

      render(<AdvancedConflictMap />);

      const exportButton = screen.getByText(/⬇ Export/i);
      fireEvent.click(exportButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/v1/conflicts/heatmap/data?days_back=30'
        );
      });
    });

    it('should handle export errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Export failed')
      );

      // Mock alert
      const mockAlert = jest.spyOn(window, 'alert').mockImplementation();

      render(<AdvancedConflictMap />);

      const exportButton = screen.getByText(/⬇ Export/i);
      fireEvent.click(exportButton);

      await waitFor(() => {
        expect(mockAlert).toHaveBeenCalledWith(
          'Failed to export heatmap data'
        );
      });

      mockAlert.mockRestore();
    });
  });

  describe('Data Format', () => {
    it('should handle empty data correctly', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ points: [], bounds: {} }),
      });

      render(<AdvancedConflictMap />);

      const heatmapButton = screen.getByText(/🔥 Heatmap/i);
      fireEvent.click(heatmapButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    });

    it('should handle malformed API response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),  // Missing 'points' key
      });

      render(<AdvancedConflictMap />);

      const heatmapButton = screen.getByText(/🔥 Heatmap/i);
      fireEvent.click(heatmapButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    });
  });
});
